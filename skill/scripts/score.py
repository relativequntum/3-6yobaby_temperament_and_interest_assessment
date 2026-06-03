#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确定性计分引擎 score.py

输入一份导出 JSON（schema/export.schema.json，schema_version 1.1）→ 校验 → 按
skill/scoring/scoring-config.json + docs/理论依据与方法学.md §4.6-4.8 计分 →
输出结构化 profile.json。

铁律：
  - 全程非诊断、个体内（ipsative）相对比较；不报人群百分位、不下临床结论。
  - 计分确定性、可复现（同一输入→同一输出，无随机）。
  - T-11 人为低点防护：中心化必产生相对低项；必须并行呈现【原始水平描述带】
    （高/中/低，锚定量表频率语义）；原始为高的项绝不标为劣势/待发展，只写
    “相对没那么突出但仍很常见”。

纯标准库 + jsonschema。

用法：
    python score.py <export.json> [-c scoring-config.json] [-s export.schema.json]
                    [-o profile.json]
默认从仓库相对路径自动定位配置/schema；-o 缺省时打印到 stdout。
"""

import argparse
import json
import os
import sys
from collections import defaultdict

try:
    import jsonschema
except ImportError:  # pragma: no cover - 环境保证
    jsonschema = None


# ---------------------------------------------------------------------------
# 路径定位（相对仓库根，确定性）
# ---------------------------------------------------------------------------
_THIS = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS, "..", ".."))
DEFAULT_CONFIG = os.path.join(REPO_ROOT, "skill", "scoring", "scoring-config.json")
DEFAULT_SCHEMA = os.path.join(REPO_ROOT, "schema", "export.schema.json")


# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------
class ScoringError(Exception):
    """计分阶段的稳健失败（带 code 供调用方分流）。"""

    def __init__(self, message, code="scoring_error"):
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def round_half_up(value, ndigits=3):
    """确定性四舍五入（用 Decimal，避免 banker's rounding 造成平台差异）。"""
    if value is None:
        return None
    from decimal import Decimal, ROUND_HALF_UP

    q = Decimal(1).scaleb(-ndigits)
    return float(Decimal(repr(value)).quantize(q, rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------------------
# 描述带（原始水平 → 高/中/低 + 锚点语义短语），T-11 核心：原始为高者受保护
# ---------------------------------------------------------------------------
def _band_table(config, scale):
    return config["descriptive_bands"].get(scale, {}).get("mean_to_band", [])


def raw_band(config, scale, mean):
    """把同向化后的均值映射到锚点语义档位（高/中/低）。

    依据 descriptive_bands.<scale>.mean_to_band 的区间：
      [1.0, 2.5) 低 / [2.5, 3.5) 中 / [3.5, 5.0] 高。
    返回 dict：{level, phrase, scale}；mean 为 None 时返回 None。
    """
    if mean is None or scale not in ("freq5", "like5"):
        return None
    phrase_key = "freq_phrase" if scale == "freq5" else "like_phrase"
    last = None
    for entry in _band_table(config, scale):
        last = entry
        lo, hi, hi_inclusive = _parse_range(entry["range"])
        if mean >= lo and (mean <= hi if hi_inclusive else mean < hi):
            return {"level": entry["level"], "phrase": entry.get(phrase_key, ""), "scale": scale}
    # 边界兜底（理论上不触发，作稳健处理）
    if last is not None:
        return {"level": last["level"], "phrase": last.get(phrase_key, ""), "scale": scale}
    return None


def _parse_range(text):
    """解析 "[1.0, 2.5)" → (1.0, 2.5, False)；"[3.5, 5.0]" → (3.5, 5.0, True)。"""
    text = text.strip()
    hi_inclusive = text.endswith("]")
    inner = text[1:-1]
    lo_s, hi_s = inner.split(",")
    return float(lo_s), float(hi_s), hi_inclusive


def is_high(band):
    return bool(band) and band.get("level") == "高"


# ---------------------------------------------------------------------------
# 主计分类
# ---------------------------------------------------------------------------
class Scorer:
    # 进入 freq5 个人基线的 section（行为频率）。INT 仅 B 层 freq5 行为题计入；
    # INT A 层 like5 领域题单独排序、不入基线（由 exclude 清单 + scale 双重保证）。
    BASELINE_SECTIONS = ("TMP", "SEL", "DEV", "INT", "LRN")

    # 缺答比例阈值（high_missing 兜底自算，当 schema 未给 computed 值时参考）
    HIGH_MISSING_RATIO = 0.20
    # 每题过快下界（秒），方法学常用每题 <2s 为可疑；总活跃时长口径
    FAST_PER_ITEM_SEC = 2.0
    # 一致性配对同向化后差值阈值（>=3 视为严重矛盾，5 点量表跨度过半）
    INCONSISTENCY_DELTA = 3
    # straightlining：连续同档 longstring_max 阈值
    LONGSTRING_THRESHOLD = 10

    def __init__(self, config):
        self.config = config
        self.items_cfg = config["items"]
        self.clusters_cfg = config["clusters"]
        self.exclude = config["centering"]["exclude_from_baseline"]
        self.age_bands = {b["id"]: b for b in config["age_bands"]}
        # 反向题集合（来自配置，逐题对齐题库）
        self.reverse_items = {iid for iid, m in self.items_cfg.items() if m.get("reverse")}
        # standalone 单题剔除集合（freq5 单题且不归簇）
        self.standalone_excluded = set(
            self.exclude.get("standalone_single_item_freq5_subscales", [])
        )
        self.like5_domains = set(self.exclude.get("int_a_like5_domains", []))
        # CMC-03：相对位档位阈值改为读 scoring-config（无则回退默认 ±0.30）。
        rlt = config.get("relative_label_thresholds", {}) or {}
        self.rel_strong = rlt.get("strong_at_or_above", 0.30)
        self.rel_low = rlt.get("low_at_or_below", -0.30)
        # 簇成员 → 簇名 反查
        self.item_to_cluster = {}
        for cname, cinfo in self.clusters_cfg.items():
            for iid in cinfo["members"]:
                self.item_to_cluster[iid] = cname

    # -- 翻转 --------------------------------------------------------------
    @staticmethod
    def flip(scale, raw_value):
        """reverse:true 题按 scale 翻转。freq5/like5 均为 1-5，翻转用 6 - v。"""
        if scale in ("freq5", "like5") and isinstance(raw_value, int):
            return 6 - raw_value
        return raw_value

    def oriented_value(self, item_cfg, raw_value):
        """返回该题同向化后的数值（freq5/like5 才有意义），非数值返回 None。"""
        if not isinstance(raw_value, int):
            return None
        if item_cfg["scale"] not in ("freq5", "like5"):
            return None
        if item_cfg.get("reverse"):
            return self.flip(item_cfg["scale"], raw_value)
        return raw_value

    # -- 主入口 ------------------------------------------------------------
    def score(self, export):
        age_band = export.get("age_band")
        active_band = self._active_band(export)
        meta_out = self._meta(export, active_band)

        # 收集每题同向化值（仅 scored=true 且本龄段启用、数值合法者）
        oriented = {}  # item_id -> oriented numeric value
        reverse_applied = []  # 记录翻转过的题
        responses = export.get("responses", [])
        answered_scored = 0
        total_scored_presented = 0

        for resp in responses:
            iid = resp.get("item_id")
            cfg = self.items_cfg.get(iid)
            if cfg is None:
                continue  # 配置未登记（如未来新题/FAM 外）→ 跳过，稳健
            if not cfg.get("scored"):
                continue  # FAM 等不计入孩子画像
            # 越龄段：该题在判定龄段不启用则不纳入计分（仍稳健，不报错）
            if active_band and active_band not in cfg.get("age_bands", []):
                continue
            total_scored_presented += 1
            raw = resp.get("raw_value")
            ov = self.oriented_value(cfg, raw)
            if ov is None:
                continue  # 未作答/非数值 → 缺答，不纳入均值
            answered_scored += 1
            oriented[iid] = ov
            if cfg.get("reverse"):
                reverse_applied.append(
                    {"item_id": iid, "scale": cfg["scale"], "raw_value": raw, "oriented": ov}
                )

        # ---- 子维度（report_subscale，按 section）聚合 ----
        subscales = self._build_subscales(oriented)
        # ---- 簇合并 ----
        clusters = self._build_clusters(oriented)
        # ---- 个人 freq5 基线（核心）----
        baseline_mean, baseline_units = self._baseline(oriented, clusters)
        # ---- section 相对位 ----
        sections = self._build_sections(oriented, clusters, baseline_mean)
        # ---- 个体内相对分写回 cluster ----
        self._center_clusters(clusters, baseline_mean)
        # ---- 兴趣画像（INT A 层 like5）----
        interest_map = self._interest_map(oriented)
        interest_quality = self._interest_quality(clusters)
        # ---- 优势/成长（带 T-11 防护）----
        strengths, growth = self._strengths_and_growth(sections, clusters, oriented)
        # ---- 数据质量 + confidence ----
        data_quality = self._data_quality(
            export, oriented, total_scored_presented, answered_scored
        )
        # ---- 红旗软转介 ----
        red_flags = self._red_flags(export, responses, active_band, data_quality)

        notes = self._notes(age_band, active_band, data_quality)

        return {
            "schema": {
                "profile_schema": "1.0",
                "doc": "skill/PROFILE_SCHEMA.md",
            },
            "meta": meta_out,
            "data_quality": data_quality,
            "baseline": {
                "freq5_person_mean": round_half_up(baseline_mean) if baseline_mean is not None else None,
                "n_units": baseline_units,
                "scope": "按量表/按section（freq5 行为题；like5 不并入）",
                "note": "个人总均值仅由计入画像的 freq5 题（簇合并后只计一次）构成；"
                "like5 兴趣领域分单独在 INT 内排序、不并入。",
            },
            "sections": sections,
            "clusters": clusters,
            "subscales": subscales,
            "interest_map": interest_map,
            "interest_quality": interest_quality,
            "relative_strengths_top": strengths,
            "growth_areas_top": growth,
            "red_flags": red_flags,
            "reverse_applied": reverse_applied,
            "notes": notes,
        }

    # -- meta --------------------------------------------------------------
    def _meta(self, export, active_band=None):
        child = export.get("child", {}) or {}
        instrument = export.get("instrument", {}) or {}
        timing = (export.get("meta", {}) or {}).get("timing", {}) or {}
        return {
            "nickname": child.get("nickname"),
            "child_id": child.get("child_id"),
            "age_band": export.get("age_band"),
            # SA-03：实际用于题目启用/活动龄段命中的龄段（越界已回退到最近段；
            # 下游 select_activities 用它命中活动库，避免 out_of_range 整盘落空）。
            "effective_age_band": active_band,
            "age_months_at_submit": child.get("age_months_at_submit"),
            "sex": child.get("sex"),
            "submitted_at": timing.get("submitted_at"),
            "item_bank_version": instrument.get("item_bank_version"),
            "scoring_config_version": self.config.get("version"),
            "source_export_schema_version": self.config.get("source_export_schema_version"),
            "non_diagnostic_notice": self.config.get("non_diagnostic_notice"),
        }

    def _active_band(self, export):
        """实际用于“题目启用”判断的龄段。

        age_band=out_of_range 时回退：月龄不足最小段→'3-4'；超过最大段→'5-6'；
        无法判断则用 None（仅按各题自身 age_bands 过滤会全空，故尽量回退）。
        """
        band = export.get("age_band")
        if band in self.age_bands:
            return band
        months = (export.get("child", {}) or {}).get("age_months_at_submit")
        if isinstance(months, int):
            ordered = sorted(self.age_bands.values(), key=lambda b: b["min_months"])
            if months < ordered[0]["min_months"]:
                return ordered[0]["id"]
            if months > ordered[-1]["max_months"]:
                return ordered[-1]["id"]
            for b in ordered:
                if b["min_months"] <= months <= b["max_months"]:
                    return b["id"]
        return None

    # -- 子维度 ------------------------------------------------------------
    def _build_subscales(self, oriented):
        """按 (section, report_subscale) 聚合 → 定性子维度。

        - 全部带 caveat「题少／子维度间相关高，仅供参考」。
        - 单题（本段启用题数=1 且不归簇）标 not_ranked / standalone_excluded。
        - 不参与个体内排序（ranked=False 恒成立：默认粒度 section）。
        """
        groups = defaultdict(list)
        for iid, ov in oriented.items():
            cfg = self.items_cfg[iid]
            key = (cfg["section"], cfg.get("report_subscale") or cfg.get("subscale"))
            groups[key].append((iid, ov))

        out = []
        for (section, name), items in sorted(groups.items()):
            values = [v for _, v in items]
            n = len(values)
            mean = sum(values) / n if n else None
            scale = self.items_cfg[items[0][0]]["scale"]
            in_cluster = any(self.item_to_cluster.get(i) for i, _ in items)
            standalone = all(i in self.standalone_excluded for i, _ in items)
            band = raw_band(self.config, scale, mean)
            # SCORE-F6：本字段=「该子维度是否【作为独立子维度单位】进入 freq5 基线」。
            # 注意它对 in_cluster=True 的子维度恒为 False，并不代表其题被计入基线——
            # 簇成员题是【折叠进所属簇、以簇一席】进入基线的，而非以子维度单位进入。
            # 故另给 baseline_contribution 显式标明贡献路径，避免把「excluded=False」
            # 误读成「以子维度计入基线」。
            excluded_as_subscale_unit = (
                scale == "like5"
                or standalone
                or (n == 1 and not in_cluster)
            )
            if scale == "like5":
                baseline_contribution = "none_like5"           # like5 不入 freq5 基线
            elif in_cluster:
                baseline_contribution = "via_cluster"          # 折叠进簇一席
            elif excluded_as_subscale_unit:
                baseline_contribution = "none_standalone_single"  # 单题/standalone 剔除
            else:
                baseline_contribution = "as_subscale_unit"     # 以子维度一席计入
            out.append(
                {
                    "section": section,
                    "report_subscale": name,
                    "scale": scale,
                    "raw_mean": round_half_up(mean),
                    "raw_band": band,
                    "n_items": n,
                    "in_cluster": in_cluster,
                    "ranked": False,
                    "excluded_from_baseline": excluded_as_subscale_unit,
                    "baseline_contribution": baseline_contribution,
                    "standalone_single_item": standalone,
                    "caveat": self.config["aggregation"]["subscale_caveat"],
                }
            )
        return out

    # -- 簇 ----------------------------------------------------------------
    def _build_clusters(self, oriented):
        """5 组同义簇各合并为单一指标（簇内启用题统一均值）。

        合并 = 簇内全部本龄段启用、已同向化的题的统一均值（单一共享方差指标）。
        进入个人基线与排序时只占一席。
        """
        out = []
        for cname, cinfo in self.clusters_cfg.items():
            vals = []
            members_used = []
            for iid in cinfo["members"]:
                if iid in oriented:
                    vals.append(oriented[iid])
                    members_used.append(iid)
            if not vals:
                continue
            mean = sum(vals) / len(vals)
            # 簇成员均为 freq5（按配置），描述带按 freq5
            band = raw_band(self.config, "freq5", mean)
            out.append(
                {
                    "cluster": cname,
                    "report_name": cinfo["report_name"],
                    "scale": "freq5",
                    "raw_mean": round_half_up(mean),
                    "raw_band": band,
                    "n_items": len(vals),
                    "members_used": members_used,
                    "within_child_relative": None,  # 中心化后回填
                    "relative_label": None,
                    "merged_single_metric": True,
                    "counts_in_baseline_once": True,
                    "_raw_mean_exact": mean,  # 内部用，输出前删除
                }
            )
        return out

    # -- 基线 --------------------------------------------------------------
    def _baseline(self, oriented, clusters):
        """个人 freq5 总均值基线（中心化基准）。

        单位（“一席”）= 计入画像的 freq5 非簇单题维度 + 每个簇合并指标各算一个单位。
        剔除：like5 领域（INT-01..08）、standalone 单题（TMP-03/04/05）、
        FAM（scored:false 本就不在 oriented）、簇成员（折叠进簇单位，不单算）。

        采用“单位均值的均值”：把每个进入基线的单位（簇指标 / 非簇 freq5 单题维度
        的本题值）等权汇入，避免题量大的簇/维度放大权重——契合 §4.6“只占一席”。
        """
        units = []  # 每个单位贡献一个均值
        # 簇单位
        for c in clusters:
            units.append({"kind": "cluster", "id": c["cluster"], "mean": c["_raw_mean_exact"]})
        # 非簇 freq5 题：按 (section, report_subscale) 聚合为子维度单位
        non_cluster = defaultdict(list)
        for iid, ov in oriented.items():
            cfg = self.items_cfg[iid]
            if self.item_to_cluster.get(iid):
                continue  # 已折叠进簇
            if cfg["scale"] != "freq5":
                continue  # like5 不入基线
            if iid in self.standalone_excluded:
                continue  # 单题剔除（TMP-03/04/05）
            key = (cfg["section"], cfg.get("report_subscale") or cfg.get("subscale"))
            non_cluster[key].append(ov)
        for key, vals in non_cluster.items():
            # 单题且不归簇 → 仍可能是“非 standalone 标注”的单题维度；
            # 按 §4.8“本段启用题数=1 且不归簇”从基线剔除以免单题噪声污染。
            if len(vals) == 1:
                continue
            units.append({"kind": "subscale", "id": key, "mean": sum(vals) / len(vals)})

        if not units:
            return None, []
        baseline = sum(u["mean"] for u in units) / len(units)
        unit_summary = [
            {"kind": u["kind"], "id": (u["id"] if isinstance(u["id"], str) else list(u["id"]))}
            for u in units
        ]
        return baseline, unit_summary

    # -- 同口径折叠：簇折叠成一席、与非簇 freq5 子维度等权（与基线一致）------
    def _fold_units_mean(self, item_values):
        """SCORE-F1：把一组 (iid, oriented) 折叠为「单位均值的均值」。

        与 _baseline 同口径：簇成员先按所属簇折叠为一席（簇内题统一均值算一个单位），
        非簇 freq5 题按 (section, report_subscale) 聚合为子维度单位；standalone 单题
        与 like5 不计入。每个单位等权汇入，确保 section/DEV 相对位的零点与基线一致
        （消除原「题级均值 vs 单位均值的均值」不对称导致的 ~0.08 零点偏差）。

        不破坏：簇只占一席（按簇折叠）；standalone 单题不进基线（剔除）；
        like5/freq5 分离（仅 freq5 入）；T-11（仅改聚合口径，不动防护）。
        """
        cluster_vals = defaultdict(list)
        non_cluster = defaultdict(list)
        for iid, ov in item_values:
            cfg = self.items_cfg[iid]
            if cfg["scale"] != "freq5":
                continue  # like5 不入
            if iid in self.standalone_excluded:
                continue  # standalone 单题剔除
            cname = self.item_to_cluster.get(iid)
            if cname:
                cluster_vals[cname].append(ov)  # 折叠进簇一席
            else:
                key = (cfg["section"], cfg.get("report_subscale") or cfg.get("subscale"))
                non_cluster[key].append(ov)
        units = []
        for cname, vals in cluster_vals.items():
            units.append(sum(vals) / len(vals))  # 每簇一席
        for key, vals in non_cluster.items():
            # 与 _baseline 同口径：本段启用题数=1 且不归簇的单题维度不入（§4.8 噪声防护）。
            if len(vals) == 1:
                continue
            units.append(sum(vals) / len(vals))  # 每非簇子维度一席
        if not units:
            return None, 0
        return sum(units) / len(units), len(units)

    # -- section 相对位 ----------------------------------------------------
    def _build_sections(self, oriented, clusters, baseline_mean):
        """TMP/SEL/DEV/INT(B层)/LRN 各一个个体内相对位。

        section 原始均值 = 该 section 内「先折叠簇为一席、再与非簇 freq5 子维度
        等权」的单位均值的均值（与 _baseline 同口径，见 _fold_units_mean）。这样
        section 相对位的零点与个人基线一致，不会因簇题量大而系统性偏低（SCORE-F1）。
        relative = section_mean - baseline_mean。
        DEV 另含 5 领域内部排序（domain_order）。
        """
        section_items = defaultdict(list)
        for iid, ov in oriented.items():
            cfg = self.items_cfg[iid]
            sec = cfg["section"]
            if cfg["scale"] != "freq5":
                continue  # INT A 层 like5 不进 section 行为相对位
            if iid in self.standalone_excluded:
                continue  # 单题剔除维度不污染 section 均值
            section_items[sec].append((iid, ov))

        out = []
        section_names = {
            "TMP": "气质", "SEL": "社会情绪", "DEV": "发展快照",
            "INT": "兴趣品质(B层)", "LRN": "学习品质",
        }
        for sec in ("TMP", "SEL", "DEV", "INT", "LRN"):
            items = section_items.get(sec, [])
            if not items:
                continue
            mean, n_units = self._fold_units_mean(items)
            if mean is None:
                # 全为被剔单题维度等极端：退回题级均值以免整段丢失（仍非诊断、稳健）。
                vals = [ov for _, ov in items]
                mean = sum(vals) / len(vals)
                n_units = 0
            band = raw_band(self.config, "freq5", mean)
            rel = (mean - baseline_mean) if baseline_mean is not None else None
            # SCORE-F3：label 与 pool 同口径——统一用 round 后的相对位判档。
            rel_r = round_half_up(rel) if rel is not None else None
            entry = {
                "id": sec,
                "name": section_names[sec],
                "scale": "freq5",
                "raw_mean": round_half_up(mean),
                "raw_band": band,
                "n_items": len(items),
                "n_units": n_units,
                "within_child_relative": rel_r,
                "relative_label": self._relative_label(rel_r, band),
                "protected_high": is_high(band),
            }
            if sec == "DEV":
                entry["domain_order"] = self._dev_domains(oriented, baseline_mean)
            out.append(entry)
        # section 内排序值（仅用于展示相对突出顺序，不跨人比较）
        out.sort(key=lambda e: (e["within_child_relative"] is None, -(e["within_child_relative"] or 0)))
        return out

    def _dev_domains(self, oriented, baseline_mean):
        """DEV 按 5 领域（report_subscale）在孩子内部排序。"""
        groups = defaultdict(list)
        for iid, ov in oriented.items():
            cfg = self.items_cfg[iid]
            if cfg["section"] != "DEV":
                continue
            groups[cfg.get("report_subscale") or cfg["subscale"]].append(ov)
        domains = []
        for name, vals in groups.items():
            mean = sum(vals) / len(vals)
            band = raw_band(self.config, "freq5", mean)
            rel = (mean - baseline_mean) if baseline_mean is not None else None
            rel_r = round_half_up(rel) if rel is not None else None  # SCORE-F3 同口径
            domains.append(
                {
                    "domain": name,
                    "raw_mean": round_half_up(mean),
                    "raw_band": band,
                    "n_items": len(vals),
                    "within_child_relative": rel_r,
                    "relative_label": self._relative_label(rel_r, band),
                    "protected_high": is_high(band),
                }
            )
        domains.sort(key=lambda d: (d["within_child_relative"] is None, -(d["within_child_relative"] or 0)))
        return domains

    def _center_clusters(self, clusters, baseline_mean):
        for c in clusters:
            mean = c["_raw_mean_exact"]
            rel = (mean - baseline_mean) if baseline_mean is not None else None
            rel_r = round_half_up(rel) if rel is not None else None  # SCORE-F3 同口径
            c["within_child_relative"] = rel_r
            c["relative_label"] = self._relative_label(rel_r, c["raw_band"])
            c["protected_high"] = is_high(c["raw_band"])
            del c["_raw_mean_exact"]

    def _relative_label(self, rel, band):
        """个体内相对位标签。T-11：原始为高（band=高）即便相对低，也用保护性措辞。

        档位阈值（CMC-03）来自 scoring-config.relative_label_thresholds，缺省 ±0.30。
        """
        if rel is None:
            return None
        protected = is_high(band)
        if rel >= self.rel_strong:
            return "相对突出"
        if rel <= self.rel_low:
            if protected:
                # 人为低点防护：原始高但相对偏低 → 不贬为劣势
                return "相对没那么突出但仍很常见"
            return "相对还在发展中"
        return "中间位置"

    # -- 兴趣画像 ----------------------------------------------------------
    def _interest_map(self, oriented):
        """INT A 层 8 领域（like5）个体内热度排序，不与行为分混算。"""
        domain_names = {
            "INT-01": "运动/大肌肉", "INT-02": "艺术/绘画手工", "INT-03": "音乐/律动",
            "INT-04": "语言/故事", "INT-05": "数理/逻辑", "INT-06": "自然探索",
            "INT-07": "建构/搭建", "INT-08": "社交/扮演",
        }
        rows = []
        like_vals = [oriented[i] for i in self.like5_domains if i in oriented]
        person_like_mean = sum(like_vals) / len(like_vals) if like_vals else None
        for iid in sorted(self.like5_domains):
            if iid not in oriented:
                continue
            v = oriented[iid]
            band = raw_band(self.config, "like5", v)
            rel = (v - person_like_mean) if person_like_mean is not None else None
            rows.append(
                {
                    "item_id": iid,
                    "domain": domain_names.get(iid, self.items_cfg.get(iid, {}).get("subscale")),
                    "like5_raw": v,
                    "raw_band": band,
                    "within_int_relative": round_half_up(rel) if rel is not None else None,
                    "label": self._interest_label(v, rel),
                }
            )
        # 按原始喜爱度降序排名（同分按 item_id 稳定）
        rows.sort(key=lambda r: (-r["like5_raw"], r["item_id"]))
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        return {
            "person_like5_mean": round_half_up(person_like_mean) if person_like_mean is not None else None,
            "domains": rows,
        }

    def _interest_label(self, value, rel):
        if value >= 5:
            return "最被吸引（一玩就停不下来）"
        if value >= 4:
            return "明显更被吸引、会主动玩"
        if value <= 2:
            return "相对较少被这类活动吸引"
        return "一般/还行"

    def _interest_quality(self, clusters):
        """INT B 层品质信号：并入相应簇（focus_persistence/initiative/mastery 等）。

        以簇为载体表达“偏好成色”：B 层信号已在簇内合并，这里给定性读出。
        """
        relevant = {"focus_persistence", "initiative", "mastery"}
        out = []
        for c in clusters:
            if c["cluster"] in relevant:
                out.append(
                    {
                        "cluster": c["cluster"],
                        "report_name": c["report_name"],
                        "raw_band": c["raw_band"],
                        "signal": "高=已超越一时新鲜、值得继续提供机会；"
                        "低而某领域 like5 高=目前喜欢但尚未稳定深度投入",
                        "note": "B 层品质信号并入相应簇，仅作偏好成色定性参考",
                    }
                )
        return out

    def _section_cluster_overlap(self, oriented):
        """SCORE-F2：每个 section → 其内出现的簇集合，及该 section 是否「全由簇成员构成」。

        返回 (section_to_clusters, fully_cluster_sections)：
          - section_to_clusters[sec] = {cluster_name, ...}（该 section 含成员的簇）
          - fully_cluster_sections = {sec, ...}（该 section 计入相对位的 freq5 题里
            没有任何非簇子维度单位——典型如 INT(B层)，其 section 信号与重叠簇同源）。
        用于去重：section 与其重叠簇不同时上榜。
        """
        section_to_clusters = defaultdict(set)
        section_has_non_cluster = defaultdict(bool)
        for iid, _ov in oriented.items():
            cfg = self.items_cfg[iid]
            if cfg["scale"] != "freq5":
                continue
            if iid in self.standalone_excluded:
                continue
            sec = cfg["section"]
            cname = self.item_to_cluster.get(iid)
            if cname:
                section_to_clusters[sec].add(cname)
            else:
                section_has_non_cluster[sec] = True
        fully = {
            sec for sec, cls in section_to_clusters.items()
            if cls and not section_has_non_cluster.get(sec)
        }
        return section_to_clusters, fully

    # -- 优势/成长（T-11 防护核心）----------------------------------------
    def _strengths_and_growth(self, sections, clusters, oriented):
        """relative_strengths_top / growth_areas_top。

        T-11 人为低点防护：
          - growth_areas 只收 within_child_relative 偏低 且 原始 band 非“高”者。
          - 原始为“高”的项绝不进入 growth（protected_high=True 直接排除）；
            若它相对偏低，仅在 strengths 侧或单独标“相对没那么突出但仍很常见”。
        以 section 层 + 簇为候选（默认粒度 section；簇为合并单一指标）。

        SCORE-F2 去重：当某 section 的相对位信号「全由簇成员构成」（如 INT B 层
        全为 INT-09..15，分属 3 簇），该 section 与其重叠簇是同一信号，不得同时上榜。
        策略：择一——保留更精细、可溯源的「簇」候选，剔除该冗余 section 候选；并在
        该 section 候选上记 merged_into_clusters 供叙述合并。
        """
        section_to_clusters, fully_cluster_sections = self._section_cluster_overlap(oriented)

        candidates = []
        for s in sections:
            sec = s["id"]
            cand = {
                "ref": sec,
                "kind": "section",
                "name": s["name"],
                "raw_band": s["raw_band"],
                "within_child_relative": s["within_child_relative"],
                "relative_label": s["relative_label"],
                "protected_high": s.get("protected_high", False),
            }
            # 全簇构成的 section（信号与重叠簇同源）→ 标注并从候选剔除，择「簇」上榜。
            if sec in fully_cluster_sections:
                cand["_redundant_with_clusters"] = sorted(section_to_clusters.get(sec, set()))
                continue
            candidates.append(cand)
        for c in clusters:
            candidates.append(
                {
                    "ref": c["cluster"],
                    "kind": "cluster",
                    "name": c["report_name"],
                    "raw_band": c["raw_band"],
                    "within_child_relative": c["within_child_relative"],
                    "relative_label": c["relative_label"],
                    "protected_high": c.get("protected_high", False),
                }
            )
        scored = [c for c in candidates if c["within_child_relative"] is not None]

        strengths = sorted(scored, key=lambda c: -c["within_child_relative"])
        strengths_top = [c for c in strengths if c["within_child_relative"] >= 0][:5]

        # growth：相对偏低 且 非原始高
        growth_pool = [
            c for c in scored
            if c["within_child_relative"] < 0 and not c["protected_high"]
        ]
        growth_pool.sort(key=lambda c: c["within_child_relative"])
        growth_top = growth_pool[:3]

        # 被保护项（原始高但相对偏低）单列说明，绝不入 growth
        protected_low = [
            {
                **{k: c[k] for k in ("ref", "kind", "name", "raw_band", "within_child_relative")},
                "note": "原始水平高（经常/几乎总是），相对没那么突出但仍很常见，不列为待发展",
            }
            for c in scored
            if c["within_child_relative"] < 0 and c["protected_high"]
        ]

        for c in growth_top:
            c["note"] = "个体内相对靠后；非劣势、非诊断，可作陪伴练习方向"

        return (
            strengths_top,
            {
                "items": growth_top,
                "protected_high_relative_low": protected_low,
                "t11_guard": "原始为高的项绝不列入 growth；仅个体内相对偏低、原始非高者才入。",
            },
        )

    # -- 数据质量 + confidence --------------------------------------------
    def _data_quality(self, export, oriented, presented, answered):
        meta = export.get("meta", {}) or {}
        quality = meta.get("quality", {}) or {}
        timing = meta.get("timing", {}) or {}
        identity = export.get("_identity_extra", {}) or {}

        flags = {}
        notes = []

        # straightlining（前端 computed，longstring_max 兜底）
        straight = bool(quality.get("straightlining_flag"))
        ls_max = quality.get("longstring_max")
        if not straight and isinstance(ls_max, int) and ls_max >= self.LONGSTRING_THRESHOLD:
            straight = True
            notes.append("最长连续同档≥10，疑似一条道直答")
        flags["straightlining"] = straight

        # fast_response（前端 computed，按总活跃时长/题数兜底）
        fast = bool(quality.get("fast_response_flag"))
        total_sec = timing.get("total_active_sec")
        if isinstance(total_sec, int) and presented > 0:
            per_item = total_sec / presented
            if per_item < self.FAST_PER_ITEM_SEC:
                fast = True
                notes.append(
                    "平均每题约 %.1f 秒，低于 2 秒可疑下界（阈值需本地校准）" % per_item
                )
        flags["fast_response"] = fast

        # high_missing
        high_missing = bool(quality.get("high_missing_flag"))
        miss_ratio = ((presented - answered) / presented) if presented else 0.0
        if miss_ratio >= self.HIGH_MISSING_RATIO:
            high_missing = True
            notes.append("缺答比例 %.0f%% 偏高" % (miss_ratio * 100))
        flags["high_missing"] = high_missing
        flags["missing_ratio"] = round_half_up(miss_ratio, 3)

        # inconsistency（用 cp 配对在 skill 侧自算）
        inconsistency, inc_detail = self._inconsistency(oriented, quality)
        flags["inconsistency"] = inconsistency
        if inc_detail:
            notes.extend(inc_detail)

        # familiarity_low（由 daily_contact 推断）
        daily = identity.get("daily_contact")
        relationship = identity.get("relationship")
        fam_low = bool(quality.get("familiarity_low")) or daily == "lt1"
        if fam_low:
            extra = "（且为其他照看人）" if relationship == "other_caregiver" else ""
            notes.append("填写人每日相处较少%s，报告强度下调、加重免责" % extra)
        flags["familiarity_low"] = fam_low

        # SCORE-F4：recent_disruption 为 frontend_provided——直接读前端预置布尔，skill 不派生。
        flags["recent_disruption"] = bool(quality.get("recent_disruption"))
        # sdb_halo 预留（恒读前端值，弱代理不在此强判，仅记录）
        flags["sdb_halo"] = bool(quality.get("sdb_halo_flag"))
        flags["resumed_from_draft"] = bool(timing.get("resumed_from_draft"))

        # ---- confidence 综合 ----
        hard = sum(
            1 for k in ("straightlining", "fast_response", "high_missing", "inconsistency")
            if flags[k]
        )
        soft = sum(1 for k in ("familiarity_low", "recent_disruption") if flags[k])
        if hard >= 2 or (hard >= 1 and soft >= 1):
            confidence = "low"
        elif hard == 1 or soft >= 1:
            confidence = "med"
        else:
            confidence = "high"

        return {
            "flags": flags,
            "confidence": confidence,
            "confidence_basis": {
                "hard_flags": hard,
                "soft_flags": soft,
                "rule": "硬旗(直答/过快/高缺答/矛盾)≥2 或 硬1+软1 → low；硬1或软≥1 → med；否则 high",
            },
            "explanations": notes or ["未触发显著质量旗标，数据可信度良好"],
            "handling": "标注优先而非删除（Ward & Meade 2023）：多旗标→弱化绝对表述、加重免责。",
        }

    def _inconsistency(self, oriented, quality):
        """用 cp-1..cp-4 配对：两题各自同向化后差值≥阈值即矛盾。"""
        pairs = (
            self.config["quality_flags"]["inconsistency"].get("pairs", {})
            if "inconsistency" in self.config.get("quality_flags", {})
            else {}
        )
        flagged = False
        detail = []
        for pid, members in pairs.items():
            a, b = members[0], members[1]
            if a in oriented and b in oriented:
                delta = abs(oriented[a] - oriented[b])
                if delta >= self.INCONSISTENCY_DELTA:
                    flagged = True
                    detail.append("配对 %s(%s/%s) 同向化后差值 %d，前后不太一致" % (pid, a, b, delta))
        # 也尊重前端预置（若已置真）
        if quality.get("inconsistency_flag"):
            flagged = True
        return flagged, detail

    # -- 红旗软转介 --------------------------------------------------------
    def _red_flags(self, export, responses, active_band, data_quality):
        """保守软转介：DEV 某领域原始作答长期停最低档(=1)，且数据可信、熟悉度高、近期无变动。"""
        cfg_rf = self.config.get("red_flags", {})
        flags = data_quality["flags"]
        # 守门：familiarity_low / recent_disruption 为真则不触发（避免误判）
        if flags.get("familiarity_low") or flags.get("recent_disruption"):
            return []
        # 数据不可信也不触发（保守）
        if data_quality["confidence"] == "low":
            return []

        # 按 DEV 领域聚合“原始作答（同向，正向题=原值）”，看是否长期=1
        dev_domains = defaultdict(list)
        for resp in responses:
            iid = resp.get("item_id")
            cfg = self.items_cfg.get(iid)
            if not cfg or cfg["section"] != "DEV" or not cfg.get("scored"):
                continue
            if active_band and active_band not in cfg.get("age_bands", []):
                continue
            raw = resp.get("raw_value")
            if not isinstance(raw, int):
                continue
            # DEV 题均为正向；同向值=原值。最低档=1「几乎从不」
            dev_domains[cfg.get("report_subscale") or cfg["subscale"]].append(raw)

        out = []
        template = cfg_rf.get("wording_template", "")
        for domain, vals in dev_domains.items():
            # SCORE-F5：至少 2 题守卫——单题领域不足以触发软转介，避免单题噪声误判。
            if len(vals) >= 2 and all(v == 1 for v in vals):
                out.append(
                    {
                        "type": "soft_referral",
                        "area": domain,
                        "basis": "该发展领域相关行为原始作答长期停在最低档（几乎从不）",
                        "non_diagnostic": True,
                        "wording": template.replace("X", domain) if "X" in template else template,
                        "red_lines_respected": cfg_rf.get("red_lines", []),
                    }
                )

        # OPEN-03 家长自述担忧（轻量启发：不做诊断，仅温和引导）
        for op in export.get("open_ended", []) or []:
            if op.get("item_id") == "OPEN-03" and (op.get("text") or "").strip():
                # 仅当存在明显担忧词时给温和引导，否则不打扰
                text = op["text"]
                if any(w in text for w in ("担心", "头疼", "焦虑", "迟", "不会", "落后", "问题")):
                    out.append(
                        {
                            "type": "open_ended_gentle_guide",
                            "area": "家长自述关切(OPEN-03)",
                            "basis": "家长在开放题表达了带养困扰",
                            "non_diagnostic": True,
                            "wording": "每个孩子节奏不同，这套小测评不能替代专业判断。"
                            "若您持续有担心，和儿保医生或专业老师聊一聊是稳妥的做法。",
                        }
                    )
                break
        return out

    # -- notes -------------------------------------------------------------
    def _notes(self, age_band, active_band, data_quality):
        notes = [
            "本报告为非诊断、个体内（ipsative）相对比较；不报人群百分位、不下临床结论。",
            "原始水平描述带锚定量表频率/喜爱语义；个体内相对位仅在该孩子内部有意义。",
            "同义簇已合并为单一指标、只计基线一次；子维度仅定性补充，标『题少/相关高，仅供参考』。",
        ]
        if age_band == "out_of_range":
            notes.append(
                "月龄越界（out_of_range）：已回退到最接近龄段 %s 的启用题计分，结果仅供参考。"
                % (active_band or "未知")
            )
        if data_quality["confidence"] != "high":
            notes.append("数据可信度为 %s：报告已弱化绝对表述、加重免责。" % data_quality["confidence"])
        return notes


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------
def validate_export(export, schema):
    if jsonschema is None:
        raise ScoringError("jsonschema 未安装，无法校验", code="missing_dependency")
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    errors = sorted(validator.iter_errors(export), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "(root)"
        raise ScoringError(
            "导出 JSON 未通过 schema 校验：%s @ %s（共 %d 处）"
            % (first.message, loc, len(errors)),
            code="schema_invalid",
        )


def score_export(export, config, schema=None):
    """对外主函数：校验（可选）→ 计分 → 返回 profile dict。"""
    if not isinstance(export, dict):
        raise ScoringError("导出内容不是 JSON 对象", code="bad_input")
    if schema is not None:
        validate_export(export, schema)
    return Scorer(config).score(export)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(description="确定性计分引擎：导出 JSON → profile.json")
    parser.add_argument("export", help="导出 JSON 文件路径")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, help="scoring-config.json")
    parser.add_argument("-s", "--schema", default=DEFAULT_SCHEMA, help="export.schema.json")
    parser.add_argument("-o", "--output", default=None, help="输出 profile.json（缺省打印到 stdout）")
    parser.add_argument("--no-validate", action="store_true", help="跳过 schema 校验（不推荐）")
    args = parser.parse_args(argv)

    try:
        export = load_json(args.export)
        config = load_json(args.config)
        schema = None if args.no_validate else load_json(args.schema)
        profile = score_export(export, config, schema)
    except ScoringError as exc:
        sys.stderr.write("[score.py] %s（code=%s）\n" % (exc, exc.code))
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write("[score.py] 读取/解析失败：%s\n" % exc)
        return 2

    text = json.dumps(profile, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        sys.stderr.write("[score.py] 已写入 %s\n" % args.output)
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
