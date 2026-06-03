#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""报告渲染层 render.py — 三件套产出（report.md / report.html / report.pdf）

输入：一个「报告内容对象」（report content object，下称 RCO），含
  - profile：计分引擎 score.py 的确定性输出（skill/PROFILE_SCHEMA.md）
  - narratives：LLM 已写好的各章叙事文本（循证、可溯、因人而异；本层不生成叙事）
  - activities：已选定并裁剪好的活动列表（游戏/锻炼/家庭陪伴三线，每条带来源 id）
  - glance：一页速览文本（一句话画像 + 相对优势 TOP + 本周三件事）
  - 其它可选：theme/palette、soft_hints、retest、appendix 等

输出（写入指定目录）：
  ① report.md   —— 权威源（authoritative source）。Markdown，叙事与数据同源。
  ② report.html —— 由同一份「文档模型」渲染：响应式·手机优先·内联 CSS 与 SVG
                    图表·自包含离线（base.html 注入）。与 MD 同源同内容。
  ③ report.pdf  —— A4，用已缓存的 Playwright/Chromium **打印 report.html** 得到
                    （PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1）。

铁律（贯穿渲染）：
  - 全程非诊断、个体内（ipsative）相对比较；不报人群百分位、不下临床结论。
  - 渲染层**不写死叙事**（叙事是输入），但提供清晰占位与组织；缺叙事时给出
    中性、合规的兜底占位，绝不编造结论。
  - **T-11 人为低点防护**：原始水平=高的项绝不渲染成劣势/待发展；恒并列原始水平带。
  - 报告口吻温暖、对家长友好、用昵称称呼、去刻板化（措辞由叙事承载，结构在此保障）。

「文档模型」(doc model)：render.py 先把 RCO 摊平成一棵由「块」(blocks) 组成的中间
结构（标题/段落/列表/卡片/图表/防护框/活动三线/表格…），MD 与 HTML 各自从同一棵
块树序列化，从根本上保证两格式「同源同内容」。

用法：
    python render.py <rco.json> -o <out_dir> [--no-pdf] [--profile profile.json]
其中 rco.json 可直接内联 profile，或用 --profile 单独给出；二者取其一。

依赖：纯标准库 +（仅 PDF 需要）playwright。MD→HTML 用内置极简转换器，无 markdown 库。
"""

from __future__ import annotations

import argparse
import html as _html
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

_THIS = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS, "..", ".."))
TEMPLATES_DIR = os.path.join(_THIS, "..", "templates")

# 与本脚本同目录的图表接口（自包含 SVG）
try:
    import charts as _charts
except ImportError:  # pragma: no cover - 兼容以包路径导入
    from . import charts as _charts  # type: ignore


# ===========================================================================
# 文档模型：块(block)。每块是 {"t": <type>, ...}，MD 与 HTML 各自序列化。
# 块类型：h(标题) p(段落) raw_md(原样markdown段) ul/ol(列表) chips(标签)
#         chart(内联SVG) card(卡片，含子块) guard/note/soft(防护/提示框)
#         act_lines(活动三线) table(表格) hr(分隔) glance(速览) anchor(锚点)
# ===========================================================================

# ---- 文本工具 -------------------------------------------------------------
def _h(text) -> str:
    """HTML 转义。"""
    return _html.escape("" if text is None else str(text), quote=True)


def _md_inline_escape(text) -> str:
    """MD 文本里转义会破坏结构的字符（保守，仅必要处）。"""
    if text is None:
        return ""
    return str(text).replace("\\", "\\\\").replace("|", "\\|")


def _nickname(profile) -> str:
    nk = (((profile or {}).get("meta") or {}).get("nickname")) or "孩子"
    return str(nk)


def _band_text(band) -> str:
    """raw_band → 「原始水平：高（语义短语）」可读串。"""
    if not isinstance(band, dict):
        return ""
    lvl = band.get("level")
    phrase = band.get("phrase")
    if not lvl:
        return ""
    return f"原始水平：{lvl}" + (f"（{phrase}）" if phrase else "")


# ===========================================================================
# RCO 取值帮助：叙事按 key 取，缺失给合规兜底占位（绝不编造结论）。
# ===========================================================================
class RCO:
    """报告内容对象的轻封装：提供 profile、各章叙事、活动、速览的安全取值。"""

    # 章节叙事 key（与报告结构对应；LLM 产出时按此 key 命名）
    NARRATIVE_KEYS = [
        "overview", "temperament", "social_emotional", "dev_snapshot",
        "interests", "learning", "family_env", "synthesis",
        "boundary", "retest",
    ]

    def __init__(self, rco: Dict[str, Any], profile: Optional[Dict[str, Any]] = None):
        self.rco = rco or {}
        self.profile = profile or self.rco.get("profile") or {}
        self.narr = self.rco.get("narratives") or {}
        self.activities = self.rco.get("activities") or []
        self.glance = self.rco.get("glance") or {}
        self.palette = self.rco.get("palette") or getattr(_charts, "PALETTE", None)

    def narrative(self, key: str, fallback: str = "") -> str:
        """取某章叙事文本；缺失返回兜底（中性、合规，不下结论）。"""
        val = self.narr.get(key)
        if isinstance(val, list):
            val = "\n\n".join(str(v) for v in val if v)
        if val and str(val).strip():
            return str(val).strip()
        return fallback


# ===========================================================================
# 主渲染器：RCO → 块树 → (MD, HTML body)
# ===========================================================================
class ReportBuilder:
    SECTION_TITLES = {
        "overview": "概览",
        "temperament": "气质",
        "social_emotional": "社会情绪与自我调节",
        "dev_snapshot": "发展快照",
        "interests": "兴趣画像",
        "learning": "学习品质",
        "family_env": "家庭与环境如何调节",
        "synthesis": "综合画像",
        "actions": "行动建议",
        "boundary": "边界声明与复测建议",
        "appendix": "附录：方法学与局限",
    }
    ACT_LINE_TITLES = {
        "game": ("游戏", "🎲"),
        "exercise": ("锻炼", "🏃"),
        "companionship": ("家庭陪伴", "🤍"),
    }

    def __init__(self, rco: RCO):
        self.r = rco
        self.p = rco.profile
        self.nick = _nickname(self.p)
        self.blocks: List[Dict[str, Any]] = []
        # 三张主图一次性生成（每图独立 try，单图失败不拖垮整份报告）
        self.main_charts = _charts.render_all(self.p)

    # -- 顶层装配 ----------------------------------------------------------
    def build(self) -> List[Dict[str, Any]]:
        self.blocks = []
        self._cover()
        self._glance()
        self._overview()
        self._temperament()
        self._social_emotional()
        self._dev_snapshot()
        self._interests()
        self._learning()
        self._family_env()
        self._synthesis()
        self._actions()
        self._boundary_and_retest()
        self._appendix()
        return self.blocks

    # -- 小工具：追加块 ----------------------------------------------------
    def _add(self, block):
        self.blocks.append(block)

    def _h(self, level, text, anchor=None):
        self._add({"t": "h", "level": level, "text": text, "anchor": anchor})

    def _p(self, text):
        if text and str(text).strip():
            self._add({"t": "p", "text": str(text).strip()})

    def _narr(self, key, default_hint):
        """渲染一章叙事段落（支持多段）；缺失给中性占位。"""
        text = self.r.narrative(key, fallback="")
        if not text:
            self._add({"t": "p", "text": default_hint, "muted": True})
            return
        self._add({"t": "raw_md", "text": text})

    # -- 封面 --------------------------------------------------------------
    def _cover(self):
        meta = self.p.get("meta", {}) or {}
        dq = self.p.get("data_quality", {}) or {}
        months = meta.get("age_months_at_submit")
        age_txt = f"{months} 月龄" if months else (meta.get("age_band") or "")
        sex_map = {"girl": "女孩", "boy": "男孩"}
        sub = meta.get("submitted_at") or ""
        self._add({
            "t": "cover",
            "kicker": "发展优势 + 兴趣画像 · 非诊断测评",
            "title": f"{self.nick}的成长画像",
            "meta_pairs": [
                ("昵称", self.nick),
                ("月龄", age_txt),
                ("画像类型", sex_map.get(meta.get("sex"), "")),
                ("作答时间", (sub[:10] if sub else "")),
            ],
            "confidence": dq.get("confidence"),
            "confidence_explanations": dq.get("explanations") or [],
        })

    # -- 一页速览 ----------------------------------------------------------
    def _glance(self):
        g = self.r.glance or {}
        portrait = g.get("portrait") or g.get("one_liner") or ""
        if not portrait:
            # 兜底：从 profile 的相对优势 TOP 拼一句中性画像
            tops = [s.get("name") for s in (self.p.get("relative_strengths_top") or [])[:2]]
            tops = [t for t in tops if t]
            if tops:
                portrait = (
                    f"在{self.nick}自己身上，"
                    + "、".join(tops)
                    + "等方面相对更突出；这是 TA 自己内部的相对偏好，不与其他孩子比较。"
                )
            else:
                portrait = f"这是{self.nick}在自己身上各方面的相对画像（非诊断、不与他人比较）。"

        strengths = g.get("strengths_top")
        if not strengths:
            strengths = [
                self._strength_chip_text(s)
                for s in (self.p.get("relative_strengths_top") or [])[:3]
            ]
        three = g.get("three_things") or g.get("week3") or []

        self._add({
            "t": "glance",
            "portrait": portrait,
            "strengths": [s for s in strengths if s],
            "three": [t for t in three if t],
        })

    def _strength_chip_text(self, s):
        name = s.get("name") or s.get("ref")
        band = s.get("raw_band") or {}
        lvl = band.get("level")
        suffix = f"（原始{lvl}）" if lvl else ""
        return f"{name}{suffix}"

    # -- 概览（昵称/月龄/数据置信标）--------------------------------------
    def _overview(self):
        self._h(2, self.SECTION_TITLES["overview"], anchor="overview")
        dq = self.p.get("data_quality", {}) or {}
        conf = dq.get("confidence")
        self._add({"t": "chart", "name": "confidence_badge",
                   "svg": _charts.confidence_badge(conf),
                   "caption": "这枚小标表示本次作答的数据可信程度，越高解读越稳。"})
        self._narr(
            "overview",
            f"这一页是关于{self.nick}的整体说明：报告只在 {self.nick} 自己身上做相对比较，"
            "帮助家长看见 TA 此刻相对更投入、相对还在发展中的方面。",
        )
        # 数据质量解释（若有旗标，温和呈现）
        flags = dq.get("flags", {}) or {}
        triggered = [k for k in ("straightlining", "fast_response", "high_missing",
                                 "inconsistency", "familiarity_low", "recent_disruption")
                     if flags.get(k)]
        if triggered and conf != "high":
            expl = dq.get("explanations") or []
            self._add({"t": "note", "text":
                       "有几道题的填写似乎较快或前后不太一致，报告已据此弱化绝对表述。"
                       + ("相关线索：" + "；".join(expl) if expl else "")
                       + " 若方便，换个安静的时间回看几题再生成，会更贴近 TA 的真实样子。"})

    # -- 气质 --------------------------------------------------------------
    def _temperament(self):
        self._h(2, self.SECTION_TITLES["temperament"], anchor="temperament")
        self._narr(
            "temperament",
            f"气质是{self.nick}与生俱来、相对稳定的行事风格，没有好坏之分。"
            "下面是 TA 在自己身上各气质侧面的相对位（横轴零点是 TA 自己的平均）。",
        )
        tmp = self._find_section("TMP")
        if tmp is not None:
            self._relpos_with_guard([tmp], title="气质（section 层相对位）")
        # 子维度定性补充（恒带 caveat、不排序）
        self._subscale_chips("TMP", "气质各侧面（仅定性参考）")

    # -- 社会情绪与自我调节 ------------------------------------------------
    def _social_emotional(self):
        self._h(2, self.SECTION_TITLES["social_emotional"], anchor="social_emotional")
        self._narr(
            "social_emotional",
            f"这一节关于{self.nick}在情绪调节、与人相处、冲动控制方面的相对表现。",
        )
        rows = [s for s in (self.p.get("sections") or []) if s.get("id") == "SEL"]
        # 同时把相关簇并入呈现（每簇只写一条）
        rel_clusters = self._clusters_by(("resilience", "inhibitory_control", "initiative"))
        if rows or rel_clusters:
            self._relpos_with_guard(rows + rel_clusters,
                                    title="社会情绪 / 自我调节（含相关簇，已合并去冗余）")
        self._subscale_chips("SEL", "社会情绪各侧面（仅定性参考）")

    # -- 发展快照（+软提示如触发）-----------------------------------------
    def _dev_snapshot(self):
        self._h(2, self.SECTION_TITLES["dev_snapshot"], anchor="dev_snapshot")
        self._narr(
            "dev_snapshot",
            f"发展快照按 5 个领域，看{self.nick}在自己身上相对更轻松、相对还在发展中的方面。"
            "这不是发育筛查，更不是达标判定。",
        )
        dev = self._find_section("DEV")
        domains = (dev or {}).get("domain_order") or []
        if domains:
            svg = _charts.domain_ladder(domains, title="发展 5 领域（个体内相对位）")
            self._add({"t": "chart", "name": "dev_ladder", "svg": svg,
                       "caption": "向右=在 TA 自己身上相对更常见；向左=相对还在发展中。"
                                  "右侧标注的是原始水平，原始为「高」者不会被当作短板。"})
            self._raw_band_guard_list(domains, name_key="domain")
        # 软提示（red_flags）——温和、非诊断
        self._soft_hints_block()

    # -- 兴趣画像（热度图）------------------------------------------------
    def _interests(self):
        self._h(2, self.SECTION_TITLES["interests"], anchor="interests")
        self._narr(
            "interests",
            f"兴趣画像看{self.nick}相对最被哪些活动领域吸引。这是 TA 自己内部的偏好排序，"
            "会随成长和接触机会变化，不预设任何性别或天赋标签。",
        )
        imap = self.p.get("interest_map", {}) or {}
        domains = imap.get("domains") or []
        if domains:
            # 热度图（色块）+ 主图条形（原始喜爱度 + 个体内相对热度），双视角同源
            self._add({"t": "chart", "name": "interest_heatmap",
                       "svg": _charts.interest_heatmap(domains, title="兴趣 8 领域热度图"),
                       "caption": "色越深=TA 相对越被吸引。这是横向偏好，不与行为能力分混算。"})
            self._add({"t": "chart", "name": "interest_bars",
                       "svg": self.main_charts.get("interest_bars", ""),
                       "caption": "条长=原始喜爱度（1–5）；虚线是 TA 自己的兴趣平均，"
                                  "用于看相对更热/没那么热的领域。"})
        # 兴趣品质成色（B 层并入簇的定性读出）
        iq = self.p.get("interest_quality") or []
        if iq:
            chips = []
            for q in iq:
                band = q.get("raw_band") or {}
                lvl = band.get("level")
                chips.append({"text": f"{q.get('report_name')}：成色{lvl or '—'}",
                              "kind": "calm"})
            self._add({"t": "chips", "items": chips})
            self._add({"t": "p", "muted": True,
                       "text": "成色高=已超越一时新鲜、值得继续提供机会；"
                               "成色一般而某领域很喜欢=目前喜欢但尚未稳定深度投入。"})

    # -- 学习品质 ----------------------------------------------------------
    def _learning(self):
        self._h(2, self.SECTION_TITLES["learning"], anchor="learning")
        self._narr(
            "learning",
            f"学习品质（approaches to learning）关注{self.nick}「怎么学」——专注、坚持、"
            "好奇、掌握取向等过程性特质，而非学了多少。",
        )
        rows = [s for s in (self.p.get("sections") or []) if s.get("id") == "LRN"]
        clusters = self._clusters_by(("focus_persistence", "mastery"))
        if rows or clusters:
            self._relpos_with_guard(rows + clusters,
                                    title="学习品质（含相关簇，已合并去冗余）")
        self._subscale_chips("LRN", "学习品质各侧面（仅定性参考）")

    # -- 家庭与环境如何调节 ------------------------------------------------
    def _family_env(self):
        self._h(2, self.SECTION_TITLES["family_env"], anchor="family_env")
        self._narr(
            "family_env",
            "这一节谈家庭与环境如何温和地为孩子的特质「搭脚手架」——"
            "不贴养育类型标签，只给可优化的方向。",
        )

    # -- 综合画像（相对优势 / 最需脚手架，带原始水平防护）-----------------
    def _synthesis(self):
        self._h(2, self.SECTION_TITLES["synthesis"], anchor="synthesis")
        self._narr(
            "synthesis",
            f"把上面各节合在一起，看{self.nick}此刻在自己身上的相对优势，"
            "以及相对最需要被多创造机会、多搭脚手架的方面。",
        )
        # 全局视角：各 section 个体内相对位雷达 + 五大优势簇发散条（主图）
        if self.main_charts.get("radar_sections"):
            self._add({"t": "chart", "name": "radar_sections",
                       "svg": self.main_charts["radar_sections"],
                       "caption": "一眼看 TA 在各领域相对自己平均的位置——"
                                  "越往外=相对更突出，越往内=相对还在发展中。"})
        if self.main_charts.get("cluster_bars"):
            self._add({"t": "chart", "name": "cluster_bars",
                       "svg": self.main_charts["cluster_bars"],
                       "caption": "五组跨节合并的能力簇（已去冗余、每簇只一条），"
                                  "以 TA 自己的基线为中轴。"})
        # 相对优势 TOP
        strengths = self.p.get("relative_strengths_top") or []
        if strengths:
            svg = _charts.relative_bar_chart(
                strengths, title="相对优势 TOP（个体内）")
            self._add({"t": "chart", "name": "strengths_top", "svg": svg,
                       "caption": "这些是 TA 在自己身上相对更突出的方面，附原始水平。"})
        # 成长方向（T-11 防护：原始高项绝不入，单列保护说明）
        growth = self.p.get("growth_areas_top", {}) or {}
        items = growth.get("items") or []
        protected = growth.get("protected_high_relative_low") or []
        if items:
            self._add({"t": "h", "level": 3, "text": "相对还可以多创造机会的方面"})
            self._add({"t": "ul", "items": [
                f"{it.get('name')}：{it.get('note') or '个体内相对靠后；非劣势、非诊断，可作陪伴练习方向。'}"
                for it in items]})
        if protected:
            names = "、".join(str(x.get("name")) for x in protected if x.get("name"))
            self._add({"t": "guard", "text":
                       f"温馨防护：{names} 的原始水平其实是「高」（经常/几乎总是），"
                       "只是在 TA 众多强项里相对没那么突出——仍很常见、很好，"
                       "绝不列为待发展。"})
        if not items and not protected:
            self._add({"t": "p", "muted": True,
                       "text": "本次未发现需要特别标注的相对靠后方面。"})

    # -- 行动建议（游戏/锻炼/家庭陪伴三线，每条标来源活动 id）-------------
    def _actions(self):
        self._h(2, self.SECTION_TITLES["actions"], anchor="actions")
        intro = self.r.narrative(
            "actions_intro",
            f"下面是为{self.nick}挑选、按 TA 的画像与气质裁剪过的家庭建议，"
            "分游戏 / 锻炼 / 家庭陪伴三条线。每条都标注了来源活动编号，便于回溯。"
            "这些是顺势养育的机会，不是训练处方、不承诺改变测评分数。")
        self._p(intro)
        grouped = self._group_activities(self.r.activities)
        self._add({"t": "act_lines", "groups": grouped})

    def _group_activities(self, activities):
        """把活动列表按三条 type 线分组；每条保留 id（来源）。"""
        groups = {"game": [], "exercise": [], "companionship": []}
        for a in activities or []:
            if not isinstance(a, dict):
                continue
            types = a.get("type") or a.get("lines") or []
            if isinstance(types, str):
                types = [types]
            placed = False
            for t in types:
                if t in groups:
                    groups[t].append(a)
                    placed = True
            if not placed:
                # 无 type 时归入家庭陪伴底色线
                groups["companionship"].append(a)
        return groups

    # -- 边界声明 + 软提示 + 复测建议 -------------------------------------
    def _boundary_and_retest(self):
        self._h(2, self.SECTION_TITLES["boundary"], anchor="boundary")
        self._narr(
            "boundary",
            "本报告是家庭层面的自我了解工具，不是医学诊断、发育筛查或天赋鉴定，"
            "不与其他孩子比较、不给人群百分位。它反映的是「这位填写人在最近一段时间、"
            "在家庭情境中观察到的孩子」。若您对孩子某方面有持续担心，"
            "和儿保医生或专业老师聊一聊是稳妥的做法。")
        # 软提示再申明（若有 red_flags 已在发展快照呈现，此处给统一边界）
        self._narr(
            "retest",
            "复测建议：孩子在发展、报告会随时间变化，建议每隔几个月再做一次做纵向对照；"
            "也鼓励陪伴时间最多的另一位照看人单独填一次，作为不同情境视角的对照。")
        # profile 级声明
        notes = self.p.get("notes") or []
        if notes:
            self._add({"t": "boundary", "items": notes})

    # -- 附录（方法学与局限）---------------------------------------------
    def _appendix(self):
        self._h(2, self.SECTION_TITLES["appendix"], anchor="appendix")
        appx = self.r.narrative("appendix", "")
        if appx:
            self._add({"t": "raw_md", "text": appx})
        meta = self.p.get("meta", {}) or {}
        baseline = self.p.get("baseline", {}) or {}
        rows = [
            ("方法", "个体内（ipsative）相对比较：以孩子自己的 freq5 总均值为基线做中心化。"),
            ("不做什么", "不诊断、不筛查、不给人群百分位、不下临床结论、不与他人比较。"),
            ("题库版本", meta.get("item_bank_version")),
            ("计分配置版本", meta.get("scoring_config_version")),
            ("个人基线（freq5 均值）", baseline.get("freq5_person_mean")),
            ("同义簇处理", "5 组同义簇合并为单一指标、只计基线一次，报告每簇只写一条。"),
            ("子维度", "题少 / 子维度间相关高，仅供定性参考，不进入排序。"),
        ]
        self._add({"t": "table", "head": ["项目", "说明"],
                   "rows": [[k, v] for k, v in rows if v is not None]})
        self._add({"t": "p", "muted": True,
                   "text": "本工具暂无本土常模与信效度数据，结果仅供家庭参考。"})

    # =======================================================================
    # 复用：相对位 + 防护、子维度 chips、簇取值、软提示、原始水平带
    # =======================================================================
    def _find_section(self, sid):
        for s in self.p.get("sections") or []:
            if s.get("id") == sid:
                return s
        return None

    def _clusters_by(self, names):
        out = []
        for c in self.p.get("clusters") or []:
            if c.get("cluster") in names:
                out.append({
                    "name": c.get("report_name"),
                    "within_child_relative": c.get("within_child_relative"),
                    "relative_label": c.get("relative_label"),
                    "protected_high": c.get("protected_high"),
                    "raw_band": c.get("raw_band"),
                })
        return out

    def _relpos_with_guard(self, rows, title):
        """渲染一组相对位条形图 + 原始水平防护清单。"""
        rows = [r for r in rows if isinstance(r, dict)
                and r.get("within_child_relative") is not None]
        if not rows:
            return
        svg = _charts.relative_bar_chart(rows, title=title)
        self._add({"t": "chart", "name": "relpos", "svg": svg,
                   "caption": "横轴零点是 TA 自己的平均；右侧标注原始水平。"
                              "原始为「高」者即便相对靠后，也不作短板解读。"})
        self._raw_band_guard_list(rows, name_key="name")

    def _raw_band_guard_list(self, rows, name_key):
        """对 protected_high 且相对偏低者，逐条给保护话术（T-11）。"""
        guarded = []
        for r in rows:
            if r.get("protected_high") and (r.get("within_child_relative") or 0) < 0:
                nm = r.get(name_key) or r.get("name") or r.get("domain")
                guarded.append(str(nm))
        if guarded:
            self._add({"t": "guard", "text":
                       "防护说明：" + "、".join(guarded)
                       + " 的原始水平为「高」（经常/几乎总是），"
                       "在 TA 自己众多强项中相对没那么突出，但仍很常见、很好，不是短板。"})

    def _subscale_chips(self, section_id, title):
        subs = [s for s in (self.p.get("subscales") or [])
                if s.get("section") == section_id]
        if not subs:
            return
        self._add({"t": "h", "level": 3, "text": title})
        chips = []
        for s in subs:
            band = s.get("raw_band") or {}
            lvl = band.get("level") or "—"
            kind = "strong" if lvl == "高" else ("calm" if lvl == "中" else "")
            chips.append({"text": f"{s.get('report_subscale')}：{lvl}", "kind": kind})
        self._add({"t": "chips", "items": chips})
        self._add({"t": "p", "muted": True,
                   "text": "以上子维度题少 / 子维度间相关高，仅供定性参考，不参与相对排序。"})

    def _soft_hints_block(self):
        """red_flags 软提示：温和、非诊断；并把 RCO 里额外软提示一并呈现。"""
        flags = self.p.get("red_flags") or []
        extra = self.r.rco.get("soft_hints") or []
        if not flags and not extra:
            return
        lines = []
        for f in flags:
            wording = f.get("wording") or (
                "每个孩子节奏不同，这套小测评不能替代专业判断。"
                f"如果您对孩子在「{f.get('area')}」方面的发展有持续的担心，"
                "和儿保医生或专业老师聊一聊，是个很稳妥的做法。")
            lines.append(wording)
        for e in extra:
            lines.append(str(e))
        self._add({"t": "soft", "title": "温和的小提示", "items": lines})


# ===========================================================================
# 序列化 1：块树 → Markdown（权威源）
# ===========================================================================
class MarkdownWriter:
    def __init__(self, nick):
        self.nick = nick

    def render(self, blocks) -> str:
        out: List[str] = []
        for b in blocks:
            out.append(self._block(b))
        text = "\n\n".join(x for x in out if x is not None and x != "")
        return text.rstrip() + "\n"

    def _block(self, b):
        t = b.get("t")
        m = getattr(self, f"_{t}", None)
        return m(b) if m else ""

    def _cover(self, b):
        lines = [f"# {b['title']}", "", f"_{b['kicker']}_"]
        pairs = [f"**{k}**：{v}" for k, v in b.get("meta_pairs", []) if v]
        if pairs:
            lines += ["", " ｜ ".join(pairs)]
        conf = b.get("confidence")
        if conf:
            conf_txt = {"high": "较高", "med": "中等", "low": "偏低（解读请更谨慎）"}.get(conf, conf)
            lines += ["", f"> 数据置信：{conf_txt}"]
        return "\n".join(lines)

    def _glance(self, b):
        lines = ["## 一页速览", "", f"**一句话画像**：{b['portrait']}"]
        if b.get("strengths"):
            lines += ["", "**相对优势 TOP**：", ""]
            lines += [f"- {s}" for s in b["strengths"]]
        if b.get("three"):
            lines += ["", "**本周可以试试的 3 件事**：", ""]
            lines += [f"{i}. {t}" for i, t in enumerate(b["three"], 1)]
        return "\n".join(lines)

    def _h(self, b):
        return ("#" * int(b.get("level", 2))) + " " + str(b.get("text", ""))

    def _p(self, b):
        prefix = "_" if b.get("muted") else ""
        suffix = "_" if b.get("muted") else ""
        return f"{prefix}{b.get('text','')}{suffix}"

    def _raw_md(self, b):
        return str(b.get("text", "")).strip()

    def _ul(self, b):
        return "\n".join(f"- {it}" for it in b.get("items", []))

    def _ol(self, b):
        return "\n".join(f"{i}. {it}" for i, it in enumerate(b.get("items", []), 1))

    def _chips(self, b):
        return " · ".join(f"`{c.get('text')}`" for c in b.get("items", []))

    def _chart(self, b):
        # MD 是权威文字源：图表以「图注 + 文字说明」表达，不内嵌 SVG（保证纯文本可读）。
        cap = b.get("caption")
        name = {"interest_heatmap": "（兴趣热度图）", "interest_bars": "（兴趣热度条形图）",
                "strengths_top": "（相对优势图）", "relpos": "（个体内相对位图）",
                "dev_ladder": "（发展领域阶梯图）", "radar_sections": "（各领域相对位雷达图）",
                "cluster_bars": "（五大优势簇图）",
                "confidence_badge": "", "dev_band": ""}.get(b.get("name"), "（图）")
        bits = []
        if name:
            bits.append(f"_{name}_")
        if cap:
            bits.append(f"> {cap}")
        return "\n\n".join(bits)

    def _guard(self, b):
        return f"> 🛡️ {b.get('text','')}"

    def _note(self, b):
        return f"> ℹ️ {b.get('text','')}"

    def _soft(self, b):
        lines = [f"> **{b.get('title','温和的小提示')}**", ">"]
        for it in b.get("items", []):
            lines.append(f"> - {it}")
        return "\n".join(lines)

    def _boundary(self, b):
        items = b.get("items") or ([b.get("text")] if b.get("text") else [])
        return "\n".join(f"> {it}" for it in items)

    def _hr(self, b):
        return "---"

    def _table(self, b):
        head = b.get("head", [])
        rows = b.get("rows", [])
        out = ["| " + " | ".join(_md_inline_escape(h) for h in head) + " |"]
        out.append("| " + " | ".join("---" for _ in head) + " |")
        for r in rows:
            out.append("| " + " | ".join(_md_inline_escape(c) for c in r) + " |")
        return "\n".join(out)

    def _act_lines(self, b):
        line_titles = ReportBuilder.ACT_LINE_TITLES
        out = []
        for key in ("game", "exercise", "companionship"):
            acts = b.get("groups", {}).get(key, [])
            title, icon = line_titles[key]
            out.append(f"### {icon} {title}")
            if not acts:
                out.append("_本次暂无此线建议。_")
                continue
            for a in acts:
                out.append(self._act_item_md(a))
        return "\n\n".join(out)

    def _act_item_md(self, a):
        name = a.get("name") or a.get("id")
        aid = a.get("id")
        head = f"**{name}**" + (f"（来源 `{aid}`）" if aid else "")
        lines = [head]
        why = a.get("why") or a.get("reason")
        if why:
            lines.append(f"- 为什么适合 TA：{why}")
        steps = a.get("steps")
        if isinstance(steps, list) and steps:
            lines.append("- 怎么玩：" + "；".join(str(s) for s in steps[:3]))
        elif a.get("how"):
            lines.append(f"- 怎么玩：{a.get('how')}")
        ladder = a.get("difficulty_ladder") or {}
        tip = a.get("ladder_tip") or ladder.get("harder") or ladder.get("easier")
        if tip:
            lines.append(f"- 难度微调：{tip}")
        evi = a.get("evidence") or {}
        if evi.get("strength"):
            lines.append(f"- 证据：{evi.get('strength')}"
                         + (f"——{evi.get('basis')}" if evi.get("basis") else ""))
        safety = a.get("safety_notes") or a.get("safety")
        if safety:
            lines.append(f"- 安全：{safety}")
        return "\n".join(lines)


# ===========================================================================
# 序列化 2：块树 → HTML body（与 MD 同源；图表内嵌 SVG）
# ===========================================================================
class HtmlWriter:
    def __init__(self, nick):
        self.nick = nick

    def render(self, blocks) -> str:
        return "\n".join(self._block(b) for b in blocks)

    def _block(self, b):
        t = b.get("t")
        m = getattr(self, f"_{t}", None)
        return m(b) if m else ""

    def _cover(self, b):
        pairs = "".join(
            f'<span><b>{_h(k)}</b> {_h(v)}</span>'
            for k, v in b.get("meta_pairs", []) if v)
        conf = ""
        if b.get("confidence"):
            conf = ('<div style="margin-top:10px">'
                    + _charts.confidence_badge(b["confidence"]) + "</div>")
        return (
            f'<section class="cover avoid-break">'
            f'<p class="kicker">{_h(b["kicker"])}</p>'
            f'<h1>{_h(b["title"])}</h1>'
            f'<div class="meta-row">{pairs}</div>{conf}</section>')

    def _glance(self, b):
        parts = [f'<section class="glance avoid-break"><h2>一页速览</h2>',
                 f'<p class="portrait">{_h(b["portrait"])}</p>']
        if b.get("strengths"):
            chips = "".join(f'<span class="chip strong">{_h(s)}</span>'
                            for s in b["strengths"])
            parts.append(f'<div style="margin-top:10px"><b>相对优势 TOP</b>'
                         f'<div class="chips">{chips}</div></div>')
        if b.get("three"):
            lis = "".join(f"<li>{_h(t)}</li>" for t in b["three"])
            parts.append(f'<div class="three"><b>本周可以试试的 3 件事</b>'
                         f'<ol>{lis}</ol></div>')
        parts.append("</section>")
        return "".join(parts)

    def _h(self, b):
        lvl = int(b.get("level", 2))
        anchor = f' id="{_h(b["anchor"])}"' if b.get("anchor") else ""
        return f'<h{lvl}{anchor}>{_h(b.get("text",""))}</h{lvl}>'

    def _p(self, b):
        cls = ' class="muted"' if b.get("muted") else ""
        return f'<p{cls}>{_h(b.get("text",""))}</p>'

    def _raw_md(self, b):
        return md_to_html_fragment(str(b.get("text", "")))

    def _ul(self, b):
        return "<ul>" + "".join(f"<li>{_inline_md(it)}</li>"
                                for it in b.get("items", [])) + "</ul>"

    def _ol(self, b):
        return "<ol>" + "".join(f"<li>{_inline_md(it)}</li>"
                                for it in b.get("items", [])) + "</ol>"

    def _chips(self, b):
        out = []
        for c in b.get("items", []):
            kind = c.get("kind")
            cls = "chip" + (f" {kind}" if kind in ("strong", "protect", "calm") else "")
            out.append(f'<span class="{cls}">{_h(c.get("text"))}</span>')
        return f'<div class="chips">{"".join(out)}</div>'

    def _chart(self, b):
        cap = (f'<p class="muted" style="font-size:.86rem;margin-top:4px">'
               f'{_h(b["caption"])}</p>') if b.get("caption") else ""
        return f'<figure style="margin:8px 0">{b.get("svg","")}{cap}</figure>'

    def _guard(self, b):
        return f'<div class="guard">🛡️ {_h(b.get("text",""))}</div>'

    def _note(self, b):
        return f'<div class="note">ℹ️ {_h(b.get("text",""))}</div>'

    def _soft(self, b):
        lis = "".join(f"<li>{_h(it)}</li>" for it in b.get("items", []))
        return (f'<div class="soft-hint"><strong>{_h(b.get("title","温和的小提示"))}'
                f'</strong><ul>{lis}</ul></div>')

    def _boundary(self, b):
        items = b.get("items") or ([b.get("text")] if b.get("text") else [])
        lis = "".join(f"<li>{_h(it)}</li>" for it in items)
        return f'<div class="boundary"><ul>{lis}</ul></div>'

    def _hr(self, b):
        return "<hr>"

    def _table(self, b):
        head = "".join(f"<th>{_h(h)}</th>" for h in b.get("head", []))
        body = "".join(
            "<tr>" + "".join(f"<td>{_h(c)}</td>" for c in r) + "</tr>"
            for r in b.get("rows", []))
        return f'<table class="avoid-break"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

    def _act_lines(self, b):
        out = ['<div class="act-lines">']
        for key in ("game", "exercise", "companionship"):
            title, icon = ReportBuilder.ACT_LINE_TITLES[key]
            acts = b.get("groups", {}).get(key, [])
            inner = "".join(self._act_item_html(a) for a in acts) or \
                '<p class="muted" style="padding:8px 0">本次暂无此线建议。</p>'
            out.append(
                f'<div class="act-line {key} avoid-break">'
                f'<div class="head">{icon} {_h(title)}</div>'
                f'<div class="body">{inner}</div></div>')
        out.append("</div>")
        return "".join(out)

    def _act_item_html(self, a):
        name = a.get("name") or a.get("id")
        aid = a.get("id")
        src = f'<span class="src">来源 {_h(aid)}</span>' if aid else ""
        meta_bits = []
        why = a.get("why") or a.get("reason")
        if why:
            meta_bits.append(f"为什么适合 TA：{_h(why)}")
        steps = a.get("steps")
        if isinstance(steps, list) and steps:
            meta_bits.append("怎么玩：" + _h("；".join(str(s) for s in steps[:3])))
        elif a.get("how"):
            meta_bits.append("怎么玩：" + _h(a.get("how")))
        ladder = a.get("difficulty_ladder") or {}
        tip = a.get("ladder_tip") or ladder.get("harder") or ladder.get("easier")
        if tip:
            meta_bits.append("难度微调：" + _h(tip))
        safety = a.get("safety_notes") or a.get("safety")
        if safety:
            meta_bits.append("安全：" + _h(safety))
        evi = a.get("evidence") or {}
        evi_tag = ""
        if evi.get("strength"):
            cls = "evi" + (" principle" if "原理" in str(evi.get("strength")) else "")
            evi_tag = f'<span class="{cls}">{_h(evi.get("strength"))}</span>'
        meta_html = ("".join(f'<div class="meta">{m}</div>' for m in meta_bits))
        return (f'<div class="act-item"><div class="name">{_h(name)}{evi_tag}{src}</div>'
                f'{meta_html}</div>')


# ===========================================================================
# 极简 Markdown → HTML 片段（无第三方依赖）。仅支持报告会用到的子集：
#   #/##/### 标题、- 与 1. 列表、> 引用、**bold** *italic* `code`、段落、空行。
# 用于 raw_md 块（LLM 叙事可能含基础 markdown）。
# ===========================================================================
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline_md(text) -> str:
    """行内 markdown → HTML（先转义，再放行受控标记）。"""
    s = _h(text)
    # 注意：_h 已转义，这里在转义后的文本上匹配 markdown 记号（记号本身是 ASCII，未被转义）
    s = _INLINE_CODE.sub(r"<code>\1</code>", s)
    s = _BOLD.sub(r"<strong>\1</strong>", s)
    s = _ITALIC.sub(r"<em>\1</em>", s)
    s = _LINK.sub(r'<a href="\2" rel="noopener nofollow">\1</a>', s)
    return s


def md_to_html_fragment(md: str) -> str:
    """块级 markdown → HTML 片段（段落/标题/列表/引用）。"""
    lines = md.replace("\r\n", "\n").split("\n")
    html_parts: List[str] = []
    i = 0
    n = len(lines)
    para: List[str] = []

    def flush_para():
        if para:
            html_parts.append("<p>" + _inline_md(" ".join(para).strip()) + "</p>")
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para()
            i += 1
            continue
        # 标题
        mh = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if mh:
            flush_para()
            lvl = min(len(mh.group(1)) + 1, 6)  # 叙事内标题降一级，避免与章节 h2 冲突
            html_parts.append(f"<h{lvl}>{_inline_md(mh.group(2))}</h{lvl}>")
            i += 1
            continue
        # 引用
        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            html_parts.append('<blockquote class="note">'
                              + _inline_md(" ".join(quote)) + "</blockquote>")
            continue
        # 无序列表
        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            html_parts.append("<ul>" + "".join(f"<li>{_inline_md(it)}</li>"
                                                for it in items) + "</ul>")
            continue
        # 有序列表
        if re.match(r"^\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            html_parts.append("<ol>" + "".join(f"<li>{_inline_md(it)}</li>"
                                                for it in items) + "</ol>")
            continue
        # 普通段落行（累积）
        para.append(stripped)
        i += 1
    flush_para()
    return "\n".join(html_parts)


# ===========================================================================
# HTML 文档组装（注入 base.html 模板）
# ===========================================================================
def load_template() -> str:
    path = os.path.join(TEMPLATES_DIR, "base.html")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def assemble_html(title: str, body: str) -> str:
    tpl = load_template()
    return tpl.replace("{{TITLE}}", _h(title)).replace("{{BODY}}", body)


# ===========================================================================
# PDF：用已缓存的 Playwright/Chromium 打印 report.html
# ===========================================================================
def render_pdf(html_path: str, pdf_path: str) -> None:
    """用 Playwright/Chromium 把本地 HTML 打印为 A4 PDF。

    设 PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1，使用已缓存浏览器；失败抛 RuntimeError。
    """
    os.environ.setdefault("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("未安装 playwright，无法生成 PDF；可加 --no-pdf 跳过。") from exc

    file_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page()
            page.goto(file_url, wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "14mm", "right": "14mm",
                        "bottom": "16mm", "left": "14mm"},
                prefer_css_page_size=True,
            )
        finally:
            browser.close()


# ===========================================================================
# 顶层入口：RCO → 三件套
# ===========================================================================
def render_report(rco_dict: Dict[str, Any], out_dir: str,
                  make_pdf: bool = True,
                  profile: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """渲染三件套，返回 {md, html, pdf?} 路径字典。"""
    os.makedirs(out_dir, exist_ok=True)
    rco = RCO(rco_dict, profile=profile)
    if not rco.profile:
        raise ValueError("RCO 缺少 profile（计分输出）；无法渲染。")

    nick = _nickname(rco.profile)
    blocks = ReportBuilder(rco).build()

    md_text = MarkdownWriter(nick).render(blocks)
    body_html = HtmlWriter(nick).render(blocks)
    title = f"{nick}的成长画像 · 发展优势+兴趣画像（非诊断）"
    full_html = assemble_html(title, body_html)

    md_path = os.path.join(out_dir, "report.md")
    html_path = os.path.join(out_dir, "report.html")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md_text)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(full_html)

    result = {"md": md_path, "html": html_path}
    if make_pdf:
        pdf_path = os.path.join(out_dir, "report.pdf")
        render_pdf(html_path, pdf_path)
        result["pdf"] = pdf_path
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="报告渲染：报告内容对象(RCO) → report.md/html/pdf 三件套")
    parser.add_argument("rco", help="报告内容对象 JSON（可内联 profile）")
    parser.add_argument("-o", "--out-dir", required=True, help="输出目录")
    parser.add_argument("--profile", default=None,
                        help="单独的 profile.json（RCO 未内联时用）")
    parser.add_argument("--no-pdf", action="store_true", help="跳过 PDF 生成")
    args = parser.parse_args(argv)

    try:
        with open(args.rco, "r", encoding="utf-8") as fh:
            rco_dict = json.load(fh)
        profile = None
        if args.profile:
            with open(args.profile, "r", encoding="utf-8") as fh:
                profile = json.load(fh)
        paths = render_report(rco_dict, args.out_dir,
                              make_pdf=not args.no_pdf, profile=profile)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write("[render.py] 失败：%s\n" % exc)
        return 2
    except RuntimeError as exc:
        sys.stderr.write("[render.py] PDF 失败：%s（MD/HTML 已生成）\n" % exc)
        return 3

    sys.stderr.write("[render.py] 已生成：\n")
    for k, v in paths.items():
        sys.stderr.write("  %-4s %s\n" % (k, v))
    print(json.dumps(paths, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
