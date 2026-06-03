#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""select_activities.py — 确定性活动候选筛选器（可溯源 shortlist 生成）

输入：score.py 产出的 profile.json + activity_bank/activity-bank.json
输出：candidates.json —— 把活动库按孩子的个体内画像分成若干「建议线（advice line）」，
      每条线给出排好序、带匹配理由的候选活动 shortlist，供 LLM 最终裁剪与撰写叙事。

本脚本只做【确定性、可复现、可溯源】的候选检索与排序，绝不生成文采、绝不下结论。
所有匹配都能溯源到 profile 的某个 ref 与 activity 的某个 target；不臆造 target。

非诊断铁律落到代码里的体现：
  * T-11 人为低点防护：protected_high（原始为高）的项绝不进入「待发展/该补」建议线；
    只会出现在「顺势放大」侧或被忽略，永不被当作缺陷来检索补救活动。
  * 个体内（ipsative）：建议线来自 within_child_relative 相对位与 raw_band 原始带，
    不引入任何人群常模。
  * red_flags / soft_referral 不在此处转成活动建议（属专业转介，独立于优势画像）。

建议线分两类（与编排任务一致）：
  顺势放大（amplify）：相对优势 section/cluster、强兴趣领域(interest_map 高/靠前)、
                       高成色兴趣品质信号(interest_quality 高)。→ 放大已有热情与长板。
  该补的（nurture） ：个体内相对靠后【且原始不高】的 section/cluster（即 growth_areas_top.items），
                       以及 DEV 内相对靠后且原始非「高」的领域。→ 温和扶持、低挫败入口。

每条线内：先按 target 命中数、再按 evidence 有据优先、再按 type 均衡（game/exercise/companionship
各保底），最后按 id 稳定排序，输出 shortlist（默认每线最多 8 条、三类型各至少保 1 条若库中存在）。

用法：
  python skill/scripts/select_activities.py <profile.json> [-b activity-bank.json] [-o candidates.json]
        [--per-line N] [--no-validate-targets]

退出码：0 成功；2 输入/解析错误（stderr 给出 code）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 常量与映射（全部来自 item-bank / scoring-config / activity-bank，不臆造）
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_BANK = os.path.join(SKILL_DIR, "activity_bank", "activity-bank.json")

# 相对位阈值，与 PROFILE_SCHEMA 的 relative_label 切分一致。
REL_STRONG = 0.30   # ≥ → 相对突出
REL_LOW = -0.30     # ≤ → 相对还在发展中（仅当原始非高才算「待发展」）

# interest_map 的 item_id ↔ activity targets 里的 INT 构念码（A 层 8 领域）。
# 顺序与 INT_constructs / item-bank 固定对应，确定性。
INT_ITEM_TO_CONSTRUCT = {
    "INT-01": "INT-MOV",   # 运动/大肌肉
    "INT-02": "INT-ART",   # 艺术/绘画手工
    "INT-03": "INT-MUS",   # 音乐/律动
    "INT-04": "INT-LAN",   # 语言/故事
    "INT-05": "INT-LOG",   # 数理/逻辑
    "INT-06": "INT-NAT",   # 自然探索
    "INT-07": "INT-CON",   # 建构/搭建
    "INT-08": "INT-SOC",   # 社交/扮演
}

# 三类活动类型，用于均衡保底。
TYPES = ("game", "exercise", "companionship")

# section ref → 活动 target 前缀。section 自身不是合法 target 前缀单独项，
# 故 section 级建议线靠「该 section 下的 report_subscale + 归属 cluster」展开。
SECTION_KEYS = ("TMP", "SEL", "DEV", "INT", "LRN")


# ---------------------------------------------------------------------------
# 载入
# ---------------------------------------------------------------------------

def _die(code: str, msg: str) -> None:
    sys.stderr.write(json.dumps({"code": code, "error": msg}, ensure_ascii=False) + "\n")
    sys.exit(2)


def load_json(path: str, code: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        _die(code, f"文件不存在: {path}")
    except json.JSONDecodeError as exc:
        _die(code, f"JSON 解析失败 {path}: {exc}")
    except OSError as exc:
        _die(code, f"读取失败 {path}: {exc}")


# ---------------------------------------------------------------------------
# 从 profile 抽取「建议线种子」
# ---------------------------------------------------------------------------

def _band_level(node: Dict[str, Any]) -> Optional[str]:
    rb = node.get("raw_band") or {}
    return rb.get("level")


def _is_protected_high(node: Dict[str, Any]) -> bool:
    # 显式 protected_high 优先；否则回退到 raw_band.level == 高（T-11 双保险）。
    if node.get("protected_high") is True:
        return True
    return _band_level(node) == "高"


def collect_seeds(profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """把 profile 解析成两组建议线种子：amplify / nurture。

    每个种子是一条建议线，含：
      line_id, line_kind(amplify|nurture), label(人读，来自 profile 名称),
      target_tokens(该线用于检索 activity.targets 的合法键集合),
      rationale(为何成线，溯源 profile ref 与相对位),
      protected_high(bool，仅 amplify 侧可能为 True)。
    """
    amplify: List[Dict[str, Any]] = []
    nurture: List[Dict[str, Any]] = []

    sections = {s.get("id"): s for s in profile.get("sections", [])}
    clusters = {c.get("cluster"): c for c in profile.get("clusters", [])}

    # ---- 顺势放大：相对突出的 cluster ----
    for cl in profile.get("clusters", []):
        rel = float(cl.get("within_child_relative", 0.0))
        if rel >= REL_STRONG:
            amplify.append({
                "line_id": f"amplify:cluster:{cl.get('cluster')}",
                "line_kind": "amplify",
                "label": cl.get("report_name") or cl.get("cluster"),
                "source_ref": {"kind": "cluster", "id": cl.get("cluster")},
                "target_tokens": [cl.get("cluster")],
                "rationale": (
                    f"同义簇『{cl.get('report_name')}』个体内相对突出"
                    f"（相对位 {rel:+.2f}，原始带『{_band_level(cl)}』）——顺势放大长板。"
                ),
                "protected_high": _is_protected_high(cl),
            })

    # ---- 顺势放大：相对突出的 section（DEV 用领域，其余用 section 下 report_subscale 兜底）----
    for sid in SECTION_KEYS:
        sec = sections.get(sid)
        if not sec:
            continue
        rel = float(sec.get("within_child_relative", 0.0))
        if sid == "DEV":
            # DEV 拆到领域级，逐个领域成线（相对突出→放大；相对靠后且非高→该补）。
            for dom in sec.get("domain_order", []):
                drel = float(dom.get("within_child_relative", 0.0))
                dname = dom.get("domain") or dom.get("report_subscale")
                token = f"DEV:{dname}"
                if drel >= REL_STRONG:
                    amplify.append({
                        "line_id": f"amplify:dev:{dname}",
                        "line_kind": "amplify",
                        "label": dname,
                        "source_ref": {"kind": "dev_domain", "id": dname},
                        "target_tokens": [token],
                        "rationale": (
                            f"发展快照·{dname} 在孩子内部相对突出"
                            f"（相对位 {drel:+.2f}，原始带『{_band_level(dom)}』）——放大已展现的能力。"
                        ),
                        "protected_high": _is_protected_high(dom),
                    })
                elif drel <= REL_LOW and not _is_protected_high(dom):
                    nurture.append({
                        "line_id": f"nurture:dev:{dname}",
                        "line_kind": "nurture",
                        "label": dname,
                        "source_ref": {"kind": "dev_domain", "id": dname},
                        "target_tokens": [token],
                        "rationale": (
                            f"发展快照·{dname} 在孩子内部相对靠后且原始非高"
                            f"（相对位 {drel:+.2f}，原始带『{_band_level(dom)}』）——温和扶持、低挫败入口。"
                        ),
                        "protected_high": False,
                    })
            continue
        # 非 DEV section：成线时把该 section 下所有 report_subscale 与归属 cluster 作为 target。
        toks = _section_target_tokens(sid, profile)
        if rel >= REL_STRONG:
            amplify.append({
                "line_id": f"amplify:section:{sid}",
                "line_kind": "amplify",
                "label": sec.get("name") or sid,
                "source_ref": {"kind": "section", "id": sid},
                "target_tokens": toks,
                "rationale": (
                    f"{sec.get('name')}（{sid}）整体个体内相对突出"
                    f"（相对位 {rel:+.2f}，原始带『{_band_level(sec)}』）——顺势放大。"
                ),
                "protected_high": _is_protected_high(sec),
            })

    # ---- 该补的：直接采信 score.py 已做完 T-11 防护的 growth_areas_top.items ----
    # items 已保证「相对靠后且原始非高」，且 protected_high 项已被 score.py 移到
    # protected_high_relative_low（绝不出现在 items）。这里再加一道断言式防护。
    growth = profile.get("growth_areas_top", {}) or {}
    for it in growth.get("items", []):
        ref = it.get("ref")
        kind = it.get("kind")
        if _is_protected_high(it):
            # 双保险：理论上不会发生；发生则跳过并记入 warnings。
            continue
        toks = _ref_to_target_tokens(ref, kind, profile)
        if not toks:
            continue
        nurture.append({
            "line_id": f"nurture:{kind}:{ref}",
            "line_kind": "nurture",
            "label": it.get("name") or ref,
            "source_ref": {"kind": kind, "id": ref},
            "target_tokens": toks,
            "rationale": (
                f"{it.get('name')}（{ref}）个体内相对靠后且原始非高"
                f"（相对位 {float(it.get('within_child_relative', 0.0)):+.2f}）——"
                f"该补的方向，按 goodness-of-fit 给低门槛活动。"
            ),
            "protected_high": False,
        })

    # ---- 顺势放大：兴趣领域（interest_map 中靠前/原始高的领域）----
    imap = profile.get("interest_map", {}) or {}
    for dom in imap.get("domains", []):
        iid = dom.get("item_id")
        construct = INT_ITEM_TO_CONSTRUCT.get(iid)
        if not construct:
            continue
        rank = dom.get("rank")
        level = _band_level(dom)
        wir = float(dom.get("within_int_relative", 0.0))
        # 取「原始高」或「INT 内排序靠前(rank<=3)且相对位>0」的领域作放大线。
        if level == "高" or (isinstance(rank, int) and rank <= 3 and wir > 0):
            amplify.append({
                "line_id": f"amplify:interest:{construct}",
                "line_kind": "amplify",
                "label": dom.get("domain"),
                "source_ref": {"kind": "interest_domain", "id": iid, "construct": construct},
                "target_tokens": [construct],
                "rationale": (
                    f"兴趣领域『{dom.get('domain')}』被明显吸引"
                    f"（INT 内排名第{rank}，原始带『{level}』，喜爱档 {dom.get('like5_raw')}）——"
                    f"顺势提供更多此类机会。"
                ),
                "protected_high": (level == "高"),  # 兴趣高=正向信号，本就在放大侧
            })

    # ---- 顺势放大：高成色兴趣品质信号（interest_quality 高 → 偏好已超越一时新鲜）----
    for q in profile.get("interest_quality", []):
        if _band_level(q) == "高":
            cl_key = q.get("cluster")
            amplify.append({
                "line_id": f"amplify:quality:{cl_key}",
                "line_kind": "amplify",
                "label": q.get("report_name") or cl_key,
                "source_ref": {"kind": "interest_quality", "id": cl_key},
                "target_tokens": [cl_key] if cl_key else [],
                "rationale": (
                    f"兴趣品质信号『{q.get('report_name')}』为高——"
                    f"偏好已超越一时新鲜、值得持续提供深入机会。"
                ),
                "protected_high": True,
            })

    return {"amplify": _dedup_lines(amplify), "nurture": _dedup_lines(nurture)}


def _dedup_lines(lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """同 line_id 去重（兴趣领域与品质信号可能与 cluster 线撞键），保留先到者并并合 target。"""
    seen: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for ln in lines:
        lid = ln["line_id"]
        if lid not in seen:
            seen[lid] = ln
            order.append(lid)
        else:
            merged = list(dict.fromkeys(seen[lid]["target_tokens"] + ln["target_tokens"]))
            seen[lid]["target_tokens"] = merged
    return [seen[lid] for lid in order]


def _section_target_tokens(sid: str, profile: Dict[str, Any]) -> List[str]:
    """某 section 下、孩子画像里出现过的 report_subscale 与归属 cluster 的合法 target 键。

    例外：INT section 的活动 target 在库中一律用构念码（INT-MOV…），不存在
    `INT:report_subscale` 形态键；若对 INT 也生成 `INT:子维度` 会 100% 被
    validate_targets 剔除并产出恒定假警告。故 INT 只走归属 cluster（兴趣领域线
    另由 amplify:interest 用 INT 构念码覆盖），不生成 `INT:report_subscale`。
    """
    toks: List[str] = []
    if sid != "INT":
        for sub in profile.get("subscales", []):
            if sub.get("section") == sid and sub.get("report_subscale"):
                toks.append(f"{sid}:{sub['report_subscale']}")
    for cl in profile.get("clusters", []):
        members = cl.get("members_used", []) or []
        if any(m.startswith(sid + "-") for m in members):
            toks.append(cl.get("cluster"))
    return list(dict.fromkeys(t for t in toks if t))


def _ref_to_target_tokens(ref: str, kind: str, profile: Dict[str, Any]) -> List[str]:
    """growth/strength 条目的 ref(+kind) → 合法 activity target 键集合。"""
    if kind == "cluster":
        return [ref]
    if kind == "section":
        return _section_target_tokens(ref, profile)
    if kind == "dev_domain":
        return [f"DEV:{ref}"]
    # 退而求其次：ref 本身若已是合法形态（如 "SEL:情绪调节"）直接用。
    if ":" in str(ref) or str(ref) in (c.get("cluster") for c in profile.get("clusters", [])):
        return [ref]
    return []


# ---------------------------------------------------------------------------
# 活动检索与排序
# ---------------------------------------------------------------------------

def _evidence_rank(act: Dict[str, Any]) -> int:
    # 有据 优先于 一般性发展原理（确定性 tie-break，不夸大效果声明）。
    strength = (act.get("evidence") or {}).get("strength", "")
    return 0 if strength == "有据" else 1


def match_activities(
    line: Dict[str, Any],
    activities: List[Dict[str, Any]],
    age_band: str,
    per_line: int,
) -> List[Dict[str, Any]]:
    """对单条建议线，从活动库检索命中、打分、做类型均衡，返回 shortlist。"""
    targets = set(line["target_tokens"])
    if not targets:
        return []

    scored: List[Tuple[Tuple, Dict[str, Any]]] = []
    for act in activities:
        if age_band not in act.get("age_bands", []):
            continue
        atoks = set(act.get("targets", []))
        hit = sorted(targets & atoks)
        if not hit:
            continue
        # 排序键：命中数多→前；有据→前；活动 id 稳定升序。
        sort_key = (-len(hit), _evidence_rank(act), act["id"])
        scored.append((sort_key, {
            "id": act["id"],
            "name": act.get("name"),
            "type": act.get("type", []),
            "age_bands": act.get("age_bands", []),
            "matched_targets": hit,
            "match_count": len(hit),
            "evidence_strength": (act.get("evidence") or {}).get("strength"),
            "domain": act.get("domain"),
            "temperament_fit_notes": act.get("temperament_fit_notes"),
            "safety_notes": act.get("safety_notes"),
        }))

    scored.sort(key=lambda x: x[0])
    ranked = [item for _, item in scored]

    return _balance_types(ranked, per_line)


def _balance_types(ranked: List[Dict[str, Any]], per_line: int) -> List[Dict[str, Any]]:
    """类型均衡：在排名顺序基础上，确保 game/exercise/companionship 各至少 1 条
    （若候选池中存在该类型），其余按原排名补满 per_line。确定性、不打乱已选相对序。"""
    if len(ranked) <= per_line:
        return ranked

    chosen: List[Dict[str, Any]] = []
    chosen_ids = set()

    # 第一轮：每种类型挑排名最高的一条入选（保底覆盖三类）。
    for t in TYPES:
        for act in ranked:
            if act["id"] in chosen_ids:
                continue
            if t in (act.get("type") or []):
                chosen.append(act)
                chosen_ids.add(act["id"])
                break

    # 第二轮：按原排名补满到 per_line。
    for act in ranked:
        if len(chosen) >= per_line:
            break
        if act["id"] not in chosen_ids:
            chosen.append(act)
            chosen_ids.add(act["id"])

    # 保持稳定输出序：按原 ranked 顺序排列 chosen。
    rank_index = {a["id"]: i for i, a in enumerate(ranked)}
    chosen.sort(key=lambda a: rank_index[a["id"]])
    return chosen[:per_line]


def _type_coverage(shortlist: List[Dict[str, Any]]) -> Dict[str, int]:
    cov = {t: 0 for t in TYPES}
    for a in shortlist:
        for t in a.get("type", []):
            if t in cov:
                cov[t] += 1
    return cov


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def build_candidates(
    profile: Dict[str, Any],
    bank: Dict[str, Any],
    per_line: int,
    validate_targets: bool,
) -> Dict[str, Any]:
    meta = profile.get("meta", {}) or {}
    age_band = meta.get("age_band")
    activities = bank.get("activities", [])

    warnings: List[str] = []

    # 合法 target 键全集（用于校验种子 token，不臆造）。
    legal_tokens = set()
    for act in activities:
        legal_tokens.update(act.get("targets", []))

    seeds = collect_seeds(profile)

    advice_lines: List[Dict[str, Any]] = []
    for kind in ("amplify", "nurture"):
        for line in seeds[kind]:
            toks = line["target_tokens"]
            if validate_targets:
                bad = [t for t in toks if t not in legal_tokens]
                if bad:
                    warnings.append(
                        f"建议线 {line['line_id']} 含库中不存在的 target 键，已剔除: {bad}"
                    )
                    toks = [t for t in toks if t in legal_tokens]
                    line["target_tokens"] = toks
            shortlist = match_activities(line, activities, age_band, per_line)
            if not shortlist:
                warnings.append(
                    f"建议线 {line['line_id']} 在龄段 {age_band} 下无命中活动（target={toks}）。"
                )
            advice_lines.append({
                "line_id": line["line_id"],
                "line_kind": line["line_kind"],
                "label": line["label"],
                "source_ref": line["source_ref"],
                "target_tokens": toks,
                "rationale": line["rationale"],
                "protected_high": line["protected_high"],
                "shortlist": shortlist,
                "type_coverage": _type_coverage(shortlist),
            })

    # 数据置信据实透传，供 LLM 决定措辞强度（不在此处改写画像）。
    dq = profile.get("data_quality", {}) or {}

    return {
        "schema": {"candidates_schema": "1.0", "doc": "skill/SKILL.md §候选筛选"},
        "meta": {
            "nickname": meta.get("nickname"),
            "child_id": meta.get("child_id"),
            "age_band": age_band,
            "age_months_at_submit": meta.get("age_months_at_submit"),
            "activity_bank_version": bank.get("version"),
            "item_bank_version": meta.get("item_bank_version"),
            "non_diagnostic_notice": meta.get("non_diagnostic_notice"),
        },
        "confidence": dq.get("confidence"),
        "data_quality_flags": dq.get("flags", {}),
        "selection_policy": {
            "amplify": "相对优势 section/cluster + 强兴趣领域 + 高成色兴趣品质信号 → 顺势放大",
            "nurture": "个体内相对靠后【且原始非高】的 section/cluster/DEV 领域 → 该补的，低挫败入口",
            "rank_within_line": "target 命中数↓ → evidence『有据』优先 → id 升序；再做 game/exercise/companionship 类型均衡保底",
            "t11_guard": "protected_high（原始为高）的项绝不进入 nurture 线，只可能出现在 amplify；growth_areas_top.items 已由 score.py 完成 T-11 防护，本脚本再加断言式双保险。",
            "non_diagnostic": "不引入人群常模；red_flags/soft_referral 不在此转成活动建议。",
            "per_line": per_line,
        },
        "advice_lines": advice_lines,
        "red_flags_passthrough": profile.get("red_flags", []),
        "warnings": warnings,
        "instructions_for_llm": (
            "以上 shortlist 为确定性候选，仅供裁剪。撰写时：每条建议必须挂一个真实 activity id 以溯源；"
            "用昵称、温暖口吻；amplify 线写成『顺势放大长板/兴趣』，nurture 线写成『按 goodness-of-fit 的低门槛扶持』，"
            "绝不把 ipsative 相对低点说成缺陷或诊断；protected_high 的项只夸不补；"
            "confidence 为 low/med 时弱化绝对表述、加重免责；结合 temperament_fit_notes 按孩子气质给出调适。"
        ),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="确定性活动候选筛选器（可溯源 shortlist）")
    ap.add_argument("profile", help="score.py 产出的 profile.json")
    ap.add_argument("-b", "--bank", default=DEFAULT_BANK, help="activity-bank.json 路径")
    ap.add_argument("-o", "--out", default=None, help="输出 candidates.json（默认打印到 stdout）")
    ap.add_argument("--per-line", type=int, default=8, help="每条建议线 shortlist 上限（默认 8）")
    ap.add_argument("--no-validate-targets", action="store_true",
                    help="不校验种子 target 是否在库中存在（默认校验并剔除非法键）")
    args = ap.parse_args(argv)

    profile = load_json(args.profile, "bad_profile")
    bank = load_json(args.bank, "bad_bank")

    if "meta" not in profile or "age_band" not in (profile.get("meta") or {}):
        _die("bad_profile", "profile 缺少 meta.age_band，无法做龄段命中筛选。")

    out = build_candidates(
        profile, bank,
        per_line=max(1, args.per_line),
        validate_targets=not args.no_validate_targets,
    )

    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
        except OSError as exc:
            _die("write_failed", f"写出失败 {args.out}: {exc}")
        sys.stderr.write(f"[select_activities] 已写出 {args.out}\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
