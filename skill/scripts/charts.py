#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内联 SVG 图表生成 charts.py

从 score.py 产出的 profile.json（profile_schema 1.0，见 skill/PROFILE_SCHEMA.md）
生成【内联 SVG 字符串】。纯 Python 拼字符串，不依赖 matplotlib——因此
**不踩中文字体坑**：SVG <text> 直接写中文，由浏览器/chromium 渲染时用系统字体。

报告渲染层 render.py 通过 render_all(profile) -> {chart_name: svg} 取图：
  1. radar_sections(profile)   —— 各 section 个体内相对位雷达图（默认报告粒度）。
  2. interest_bars(profile)    —— INT A 层 8 领域兴趣热度条形图（原始喜爱度 1-5）。
  3. cluster_bars(profile)     —— 5 组同义簇优势条形图（个体内相对位，发散条）。

另保留若干轻量内联组件（confidence_badge / raw_level_dots / relative_bar_chart /
interest_heatmap / domain_ladder），供 render.py 在正文内联使用；不属三张主图，
但同样自包含、非诊断、T-11 安全。

铁律落地（与计分引擎一致）：
  - 全程**非诊断、个体内（ipsative）相对比较**：雷达/簇图标注「个体内相对·非与他人比较」，
    **绝不画人群百分位、不画跨人对照、不画达标线**。
  - 同时呈现【原始水平描述带】（高/中/低）与【个体内相对位】两套读数，避免 T-11
    人为低点误读：原始为高（protected_high）的项即使相对偏低，配色与图例都不贬为劣势。
  - 配色温暖、对家长友好、去刻板化（不用红=坏的二元色）；viewBox 自适应（移动端可缩放）；
    含图例与「相对/原始」双读数说明。

纯标准库（math + html）。无外部依赖、无随机、确定性。输入缺失时返回温和占位 SVG。
"""

from __future__ import annotations

import math
from html import escape
from typing import Optional, Sequence

# ---------------------------------------------------------------------------
# 温暖配色（family-friendly），统一在此调；去刻板化、避免红=坏的负面联想。
# ---------------------------------------------------------------------------
PALETTE = {
    "bg": "#FFFDF9",          # 暖米白背景
    "ink": "#4A3F35",         # 主文字（暖棕）
    "ink_soft": "#8A7E72",    # 次级文字
    "muted": "#8A7E72",       # 别名
    "track": "#F0E4D4",       # 条形底槽
    "grid": "#EAD9C7",        # 网格/轴线（浅暖棕）
    "axis": "#D8C3A8",        # 轴线略深
    "accent": "#E8915B",      # 主强调（暖橙）
    "accent_soft": "#F6C89A", # 浅橙
    "accent_fill": "#F9D8B6", # 雷达填充
    "above": "#7FB686",       # 相对突出（柔绿，正向不刺眼）
    "near": "#E6B86A",        # 中间位置（暖黄）
    "below": "#C9A9CE",       # 相对还在发展中（柔紫，非红、不贬义）
    "protected": "#9CC4E4",   # 原始为高但相对偏低（T-11 受保护，柔蓝）
    "baseline": "#B89B7A",    # 基线参考线
    "heat0": "#F3ECE1",       # 兴趣热度：最低
    "heat1": "#F6D8B6",
    "heat2": "#F2C089",
    "heat3": "#E8995A",
    "heat4": "#DD7B3F",       # 兴趣热度：最高
    "badge_high": "#7FB686",
    "badge_med": "#D6A85A",
    "badge_low": "#C98A6A",
    "card": "#FFFFFF",
    "card_stroke": "#F0E4D4",
}

# 兴趣 8 领域各给暖色相，便于区分（确定性顺序）
INTEREST_COLORS = [
    "#E8915B", "#E27D9A", "#9C8FD1", "#6FB1C9",
    "#7FB686", "#E6B86A", "#D98C6A", "#B49BD0",
]

# 相对标签 → 颜色键（与计分引擎 _relative_label 取值一致）
_LABEL_COLOR = {
    "相对突出": "above",
    "中间位置": "near",
    "相对还在发展中": "below",
    "相对没那么突出但仍很常见": "protected",
}

FONT = (
    "'PingFang SC','Microsoft YaHei','Hiragino Sans GB',"
    "'Noto Sans CJK SC','Heiti SC',sans-serif"
)


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def _e(text) -> str:
    """转义为 XML 文本安全字符串（中文保留，特殊符号转义）。"""
    return escape("" if text is None else str(text), quote=True)


def _num(value, default=0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _f(num, ndigits=2) -> str:
    """格式化数字为紧凑字符串（去掉多余尾零），坐标用。"""
    if num is None:
        return "0"
    r = round(float(num), ndigits)
    if r == int(r):
        return str(int(r))
    return ("%.*f" % (ndigits, r)).rstrip("0").rstrip(".")


def _clamp(value, lo, hi) -> float:
    return max(lo, min(hi, value))


def _truncate(text, max_chars) -> str:
    """中文标签过长时截断加省略号，避免溢出画布。"""
    s = "" if text is None else str(text)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def _color(key) -> str:
    return PALETTE.get(key, "#999999")


def _band_level(obj) -> str:
    """从 section/cluster/domain 的 raw_band 取 高/中/低；缺失返回空串。"""
    band = (obj or {}).get("raw_band") or {}
    return band.get("level") or ""


def _relative_color(rel, band_level, protected_high):
    """按个体内相对位 + 原始档位 + T-11 保护决定条/点颜色。

    - protected_high 且相对偏低 → 受保护蓝（绝不当劣势）。
    - rel >= 0.30 → 柔绿（相对突出）。
    - rel <= -0.30（且非保护）→ 柔紫（相对还在发展中，非红、不贬义）。
    - 其余 → 暖黄（中间位置）。
    """
    if rel is None:
        return _color("near")
    if protected_high and rel < 0:
        return _color("protected")
    if rel >= 0.30:
        return _color("above")
    if rel <= -0.30:
        return _color("below")
    return _color("near")


def _svg_open(width, height, title):
    """统一的 <svg> 头：viewBox 自适应、width=100% 移动端可缩放、含背景卡片与无障碍标题。"""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 %d %d" width="100%%" '
        'preserveAspectRatio="xMidYMid meet" '
        'font-family="%s" role="img" aria-label="%s">'
        '<title>%s</title>'
        '<rect x="0" y="0" width="%d" height="%d" rx="16" fill="%s" '
        'stroke="%s" stroke-width="1"/>'
        % (width, height, FONT, _e(title), _e(title),
           width, height, PALETTE["bg"], PALETTE["card_stroke"])
    )


def _text(x, y, s, size=13, color=None, anchor="start", weight="normal", opacity=1.0):
    color = color or PALETTE["ink"]
    op = "" if opacity >= 1.0 else ' opacity="%s"' % _f(opacity, 2)
    return (
        '<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s" '
        'font-weight="%s"%s>%s</text>'
        % (_f(x, 1), _f(y, 1), _f(size, 1), color, anchor, weight, op, _e(s))
    )


def _caption(x, y):
    """统一「相对/原始」双读数说明 + 非诊断声明（页脚小字）。"""
    line1 = "图中为「个体内相对位」（与孩子自己的平均比，非与他人比较）。"
    line2 = "另以颜色/标注呈现「原始水平」：原始为高的项即使相对没那么突出，也不视为短板。"
    return (
        _text(x, y, line1, size=11, color=PALETTE["ink_soft"])
        + _text(x, y + 15, line2, size=11, color=PALETTE["ink_soft"])
    )


def _placeholder_box(width, height, message):
    return (
        _svg_open(width, height, message)
        + _text(width / 2, height / 2 + 4, message, size=13,
                color=PALETTE["ink_soft"], anchor="middle")
        + "</svg>"
    )


# ---------------------------------------------------------------------------
# 1) 雷达图：各 section 个体内相对位
# ---------------------------------------------------------------------------
def radar_sections(profile) -> str:
    """各 section（TMP/SEL/DEV/INT/LRN）个体内相对位雷达图。

    半径映射：以 baseline 为中环（相对位 0），向外=相对突出、向内=相对还在发展中。
    相对位区间按 ±REL_SPAN 截断到内外环，确保不出界；中环画基线参考圈。
    每个轴端标注 section 名 + 原始水平档位（高/中/低），双读数并存。
    """
    sections = profile.get("sections") or []
    nickname = (profile.get("meta") or {}).get("nickname") or "孩子"
    order = ["TMP", "SEL", "DEV", "INT", "LRN"]
    by_id = {s.get("id"): s for s in sections}
    axes = [by_id[i] for i in order if i in by_id]
    axes += [s for s in sections if s.get("id") not in order]
    n = len(axes)

    W, H = 760, 560
    cx, cy = 300, 270
    r_out = 185
    r_in = 55
    r_base = (r_out + r_in) / 2.0
    REL_SPAN = 0.8

    parts = [_svg_open(W, H, "%s · 各领域个体内相对位雷达图" % nickname)]
    parts.append(_text(28, 40, "%s · 发展领域雷达" % nickname, size=20,
                       color=PALETTE["ink"], weight="bold"))
    parts.append(_text(28, 62, "个体内相对·非与他人比较", size=12,
                       color=PALETTE["accent"], weight="bold"))

    if n < 3:
        parts.append(_text(cx, cy, "可用领域不足，暂不绘制雷达图", size=14,
                           color=PALETTE["ink_soft"], anchor="middle"))
        parts.append("</svg>")
        return "".join(parts)

    def angle(i):
        return -math.pi / 2 + 2 * math.pi * i / n

    def radius_for(rel):
        if rel is None:
            return r_base
        clamped = _clamp(rel, -REL_SPAN, REL_SPAN)
        return r_base + (clamped / REL_SPAN) * (r_out - r_base)

    def pt(i, radius):
        a = angle(i)
        return cx + radius * math.cos(a), cy + radius * math.sin(a)

    # 同心参考环（内/基线/外）
    for rr, dash, col in (
        (r_out, "4 4", PALETTE["grid"]),
        (r_base, "", PALETTE["baseline"]),
        (r_in, "4 4", PALETTE["grid"]),
    ):
        ring = []
        for i in range(n):
            x, y = pt(i, rr)
            ring.append("%s,%s" % (_f(x, 1), _f(y, 1)))
        dash_attr = ' stroke-dasharray="%s"' % dash if dash else ""
        parts.append(
            '<polygon points="%s" fill="none" stroke="%s" stroke-width="1.2"%s/>'
            % (" ".join(ring), col, dash_attr)
        )
    parts.append(_text(cx, cy - r_base - 6, "基线（孩子自己的平均）", size=10,
                       color=PALETTE["baseline"], anchor="middle"))

    # 轴线 + 端点标签
    for i, s in enumerate(axes):
        x, y = pt(i, r_out)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
            % (_f(cx, 1), _f(cy, 1), _f(x, 1), _f(y, 1), PALETTE["axis"])
        )
        lx, ly = pt(i, r_out + 26)
        a = angle(i)
        anchor = "middle"
        if math.cos(a) > 0.25:
            anchor = "start"
        elif math.cos(a) < -0.25:
            anchor = "end"
        name = _truncate(s.get("name"), 6)
        level = _band_level(s)
        parts.append(_text(lx, ly, name, size=13, color=PALETTE["ink"],
                           anchor=anchor, weight="bold"))
        if level:
            parts.append(_text(lx, ly + 15, "原始：%s" % level, size=10,
                               color=PALETTE["ink_soft"], anchor=anchor))

    # 数据多边形
    poly = []
    for i, s in enumerate(axes):
        x, y = pt(i, radius_for(s.get("within_child_relative")))
        poly.append("%s,%s" % (_f(x, 1), _f(y, 1)))
    parts.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.45" stroke="%s" '
        'stroke-width="2.2" stroke-linejoin="round"/>'
        % (" ".join(poly), PALETTE["accent_fill"], PALETTE["accent"])
    )
    # 数据点（按相对位/保护态着色）
    for i, s in enumerate(axes):
        rel = s.get("within_child_relative")
        x, y = pt(i, radius_for(rel))
        col = _relative_color(rel, _band_level(s), s.get("protected_high"))
        parts.append(
            '<circle cx="%s" cy="%s" r="5" fill="%s" stroke="#FFFFFF" '
            'stroke-width="1.5"/>' % (_f(x, 1), _f(y, 1), col)
        )

    # 图例（右侧）
    lx0 = 560
    ly0 = 120
    parts.append(_text(lx0, ly0 - 16, "颜色＝个体内相对位", size=12,
                       color=PALETTE["ink"], weight="bold"))
    legend = [
        (PALETTE["above"], "相对突出"),
        (PALETTE["near"], "中间位置"),
        (PALETTE["below"], "相对还在发展中"),
        (PALETTE["protected"], "原始高·相对没那么突出"),
    ]
    for j, (col, lab) in enumerate(legend):
        yy = ly0 + j * 26
        parts.append('<circle cx="%s" cy="%s" r="6" fill="%s"/>'
                     % (_f(lx0 + 6, 1), _f(yy, 1), col))
        parts.append(_text(lx0 + 20, yy + 4, lab, size=11, color=PALETTE["ink_soft"]))

    parts.append(_caption(28, H - 34))
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# 2) 兴趣热度条形图：INT A 层 8 领域（原始喜爱度 like5）
# ---------------------------------------------------------------------------
def interest_bars(profile) -> str:
    """8 个兴趣领域的喜爱度条形图（原始 like5：1-5），按热度从高到低。

    条长＝原始喜爱度（兴趣画像更直观），并叠加个体内相对位标注
    （比该孩子兴趣平均更高/更低），双读数并存；画个人兴趣均值参考线。
    """
    im = profile.get("interest_map") or {}
    domains = list(im.get("domains") or [])
    nickname = (profile.get("meta") or {}).get("nickname") or "孩子"
    person_mean = im.get("person_like5_mean")

    if not domains:
        return _placeholder_box(760, 120, "暂无兴趣领域数据")

    domains.sort(key=lambda d: d.get("rank", 999))
    n = len(domains)

    W = 760
    top = 92
    row_h = 46
    H = top + n * row_h + 70
    label_w = 150
    bar_x = 28 + label_w
    bar_max = 470
    val_min, val_max = 1.0, 5.0

    parts = [_svg_open(W, H, "%s · 兴趣热度（8 领域）" % nickname)]
    parts.append(_text(28, 40, "%s · 兴趣热度地图" % nickname, size=20,
                       color=PALETTE["ink"], weight="bold"))
    parts.append(_text(28, 62, "原始喜爱度（1–5）＋个体内相对热度", size=12,
                       color=PALETTE["accent"], weight="bold"))

    # 满分参考刻度
    for tick in (1, 2, 3, 4, 5):
        tx = bar_x + (tick - val_min) / (val_max - val_min) * bar_max
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1" '
            'stroke-dasharray="2 4"/>'
            % (_f(tx, 1), top - 8, _f(tx, 1), top + n * row_h - 10, PALETTE["grid"])
        )
        parts.append(_text(tx, top - 14, str(tick), size=10,
                           color=PALETTE["ink_soft"], anchor="middle"))

    # 个人兴趣均值参考线
    if person_mean is not None:
        mx = bar_x + (person_mean - val_min) / (val_max - val_min) * bar_max
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.6" '
            'stroke-dasharray="5 4"/>'
            % (_f(mx, 1), top - 8, _f(mx, 1), top + n * row_h - 10, PALETTE["baseline"])
        )
        parts.append(_text(mx, top + n * row_h + 4, "兴趣平均 %s" % _f(person_mean, 1),
                           size=10, color=PALETTE["baseline"], anchor="middle"))

    for i, d in enumerate(domains):
        y = top + i * row_h
        cyy = y + row_h / 2 - 4
        val = _num(d.get("like5_raw"), 0)
        rel = d.get("within_int_relative")
        color = INTEREST_COLORS[i % len(INTEREST_COLORS)]
        bar_len = (_clamp(val, val_min, val_max) - val_min) / (val_max - val_min) * bar_max
        name = _truncate(d.get("domain"), 8)
        # 个体内相对热度标（放在领域名右侧/下方，左侧空间充足，绝不溢出右边界）
        rel_txt = ""
        if rel is not None:
            if rel > 0:
                rel_txt = "比兴趣平均更热"
            elif rel < 0:
                rel_txt = "相对没那么热，但仍可喜欢"
            else:
                rel_txt = "约在兴趣平均"
        parts.append(_text(28, cyy, "%d. %s" % (d.get("rank", i + 1), name),
                           size=13, color=PALETTE["ink"], anchor="start", weight="bold"))
        if rel_txt:
            parts.append(_text(28, cyy + 14, _truncate(rel_txt, 13), size=10,
                               color=PALETTE["ink_soft"], anchor="start"))
        # 轨道
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="18" rx="9" fill="%s"/>'
            % (_f(bar_x, 1), _f(cyy - 5, 1), _f(bar_max, 1), PALETTE["track"])
        )
        # 实条
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="18" rx="9" fill="%s"/>'
            % (_f(bar_x, 1), _f(cyy - 5, 1), _f(max(bar_len, 1), 1), color)
        )
        # 分值：条够长时放条内末端（白字右对齐），否则放条尾右侧（深字）
        score_txt = "%s分" % _f(val, 1)
        if bar_len >= 36:
            parts.append(_text(bar_x + bar_len - 8, cyy + 4, score_txt,
                               size=11, color="#FFFFFF", anchor="end", weight="bold"))
        else:
            parts.append(_text(bar_x + bar_len + 6, cyy + 4, score_txt,
                               size=11, color=PALETTE["ink_soft"], anchor="start"))

    parts.append(_caption(28, H - 30))
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# 3) 5 簇优势条形图：个体内相对位（发散条，以基线为 0 轴）
# ---------------------------------------------------------------------------
def cluster_bars(profile) -> str:
    """5 组同义簇优势条形图：以基线（相对位 0）为中轴，向右=相对突出。

    每簇画一条发散条（正向右、负向左），颜色按相对位 + T-11 保护着色；
    条端标注个体内相对位数值 + 原始水平档位（高/中/低），双读数并存。
    """
    clusters = list(profile.get("clusters") or [])
    nickname = (profile.get("meta") or {}).get("nickname") or "孩子"

    if not clusters:
        return _placeholder_box(760, 120, "暂无优势簇数据")

    clusters.sort(key=lambda c: (c.get("within_child_relative") is None,
                                 -_num(c.get("within_child_relative"), 0)))
    n = len(clusters)

    W = 760
    top = 96
    row_h = 52
    H = top + n * row_h + 64
    label_w = 138
    zero_x = 28 + label_w + 150
    half = 175
    REL_SPAN = 0.8

    parts = [_svg_open(W, H, "%s · 五大优势簇（个体内相对位）" % nickname)]
    parts.append(_text(28, 40, "%s · 五大优势簇" % nickname, size=20,
                       color=PALETTE["ink"], weight="bold"))
    parts.append(_text(28, 62, "个体内相对·非与他人比较", size=12,
                       color=PALETTE["accent"], weight="bold"))

    # 0 轴（基线）
    axis_top = top - 10
    axis_bot = top + n * row_h - 8
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"/>'
        % (_f(zero_x, 1), axis_top, _f(zero_x, 1), axis_bot, PALETTE["baseline"])
    )
    parts.append(_text(zero_x, axis_top - 6, "基线", size=11,
                       color=PALETTE["baseline"], anchor="middle", weight="bold"))
    parts.append(_text(zero_x + half, axis_top - 6, "相对突出 →", size=11,
                       color=PALETTE["above"], anchor="end"))
    parts.append(_text(zero_x - half, axis_top - 6, "← 还在发展中", size=11,
                       color=PALETTE["ink_soft"], anchor="start"))

    def relx(rel):
        clamped = _clamp(_num(rel, 0), -REL_SPAN, REL_SPAN)
        return clamped / REL_SPAN * half

    for i, c in enumerate(clusters):
        y = top + i * row_h
        cyy = y + row_h / 2 - 6
        rel = c.get("within_child_relative")
        level = _band_level(c)
        color = _relative_color(rel, level, c.get("protected_high"))
        dx = relx(rel)
        name = _truncate(c.get("report_name") or c.get("cluster"), 9)
        parts.append(_text(28, cyy + 4, name, size=13, color=PALETTE["ink"],
                           anchor="start", weight="bold"))
        # 发散条
        if dx >= 0:
            bx, bw = zero_x, dx
        else:
            bx, bw = zero_x + dx, -dx
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="20" rx="10" fill="%s"/>'
            % (_f(bx, 1), _f(cyy - 6, 1), _f(max(bw, 2), 1), color)
        )
        # 相对位数值 + 原始档位
        end_x = (zero_x + dx + 8) if dx >= 0 else (zero_x + dx - 8)
        end_anchor = "start" if dx >= 0 else "end"
        rel_str = ("%+.2f" % rel) if rel is not None else "—"
        parts.append(_text(end_x, cyy + 5,
                           "%s · 原始%s" % (rel_str, level or "—"),
                           size=11, color=PALETTE["ink_soft"], anchor=end_anchor))
        # 相对标签（小字，第二行）
        rel_label = c.get("relative_label") or ""
        if rel_label:
            parts.append(_text(28, cyy + 20, _truncate(rel_label, 14), size=10,
                               color=PALETTE["ink_soft"], anchor="start"))

    # 图例
    parts.append(_caption(28, H - 30))
    legend = [
        (PALETTE["above"], "相对突出"),
        (PALETTE["near"], "中间位置"),
        (PALETTE["below"], "相对还在发展中"),
        (PALETTE["protected"], "原始高·受保护"),
    ]
    for j, (col, lab) in enumerate(legend):
        xx = 28 + j * 178
        parts.append('<rect x="%s" y="%s" width="12" height="12" rx="3" fill="%s"/>'
                     % (_f(xx, 1), _f(H - 58, 1), col))
        parts.append(_text(xx + 18, H - 48, lab, size=10, color=PALETTE["ink_soft"]))
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# 汇总接口（render.py 调用）
# ---------------------------------------------------------------------------
def render_all(profile) -> dict:
    """供 render.py 调用：返回 {chart_name: svg_string}。

    每张图独立 try：单图失败不拖垮整份报告（返回占位 SVG 并附错误注记）。
    """
    builders = {
        "radar_sections": radar_sections,
        "interest_bars": interest_bars,
        "cluster_bars": cluster_bars,
    }
    out = {}
    for name, fn in builders.items():
        try:
            out[name] = fn(profile)
        except Exception as exc:  # 稳健：图表绝不应让报告整体失败
            out[name] = _placeholder_box(760, 120,
                                         "（此图暂不可用：%s）" % _truncate(str(exc), 40))
    return out


# ---------------------------------------------------------------------------
# 轻量内联组件（供 render.py 正文内联；非三张主图，但同样自包含、T-11 安全）
# ---------------------------------------------------------------------------
def relative_bar_chart(items: Sequence[dict], *, width: int = 640,
                       title: Optional[str] = None,
                       value_key: str = "within_child_relative",
                       label_key: str = "name") -> str:
    """通用个体内相对位双向条形图（零位=个人基线）；可喂 sections / clusters / DEV 领域。

    每个 item 至少含 label_key 与 value_key；可选 relative_label / protected_high /
    raw_band 用于着色与右侧原始水平标注（T-11 防护）。**不画任何人群刻度/百分位。**
    """
    rows = [r for r in (items or []) if isinstance(r, dict)]
    if not rows:
        return _placeholder_box(width, 80, "暂无可展示的相对位数据")

    vals = [_num(r.get(value_key), 0.0) for r in rows]
    span = _clamp(max(0.5, max(abs(v) for v in vals)), 0.5, 4.0)

    pad_left = 132
    pad_right = 110
    row_h = 34
    bar_h = 18
    top = 40 if title else 16
    plot_w = width - pad_left - pad_right
    mid_x = pad_left + plot_w / 2
    height = top + row_h * len(rows) + 22

    parts = [_svg_open(width, height, title or "个体内相对位")]
    if title:
        parts.append(_text(20, 28, title, size=15, color=PALETTE["ink"], weight="bold"))

    y0 = top
    y1 = top + row_h * len(rows)
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5" '
        'stroke-dasharray="3 3"/>'
        % (_f(mid_x, 1), y0, _f(mid_x, 1), y1, PALETTE["baseline"])
    )
    parts.append(_text(mid_x, y1 + 14, "个人基线（自己的平均）", size=10,
                       color=PALETTE["ink_soft"], anchor="middle"))

    for i, r in enumerate(rows):
        cyy = top + i * row_h + row_h / 2
        v = _num(r.get(value_key), 0.0)
        frac = _clamp(v / span, -1.0, 1.0)
        bar_len = abs(frac) * (plot_w / 2)
        # 着色：优先 relative_label，再回退相对位符号；T-11 保护项恒走保护色
        color = _relative_color(v, _band_level(r), r.get("protected_high"))
        key = _LABEL_COLOR.get(r.get("relative_label"))
        if key and not (r.get("protected_high") and v < 0):
            color = _color(key)
        parts.append(_text(pad_left - 10, cyy + 4, _truncate(r.get(label_key), 8),
                           size=12.5, color=PALETTE["ink"], anchor="end"))
        x = mid_x if frac >= 0 else mid_x - bar_len
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="%d" rx="5" fill="%s"/>'
            % (_f(x, 1), _f(cyy - bar_h / 2, 1), _f(max(bar_len, 1.5), 1), bar_h, color)
        )
        level = _band_level(r)
        note = ("原始：%s" % level) if level else ""
        rl = r.get("relative_label")
        if rl and rl != "中间位置":
            note = (note + "｜" if note else "") + rl
        if note:
            parts.append(_text(width - 8, cyy + 4, _truncate(note, 16), size=10.5,
                               color=PALETTE["ink_soft"], anchor="end"))
    parts.append("</svg>")
    return "".join(parts)


def interest_heatmap(domains: Sequence[dict], *, width: int = 640,
                     title: Optional[str] = None) -> str:
    """兴趣 8 领域热度卡片图：按 like5 原始喜爱度着色（个体内偏好），4 列网格。"""
    rows = [d for d in (domains or []) if isinstance(d, dict)]
    if not rows:
        return _placeholder_box(width, 90, "暂无兴趣领域数据")
    rows = sorted(rows, key=lambda d: (_num(d.get("rank"), 99), -_num(d.get("like5_raw"))))

    cols = 4
    rows_n = (len(rows) + cols - 1) // cols
    pad = 8
    top = (40 if title else 16) + 26
    cell_w = (width - pad * (cols + 1)) / cols
    cell_h = 56
    height = top + rows_n * (cell_h + pad) + 10

    parts = [_svg_open(width, height, title or "兴趣热度图")]
    if title:
        parts.append(_text(20, 28, title, size=15, color=PALETTE["ink"], weight="bold"))
    ly = (40 if title else 16)
    parts.append(_text(20, ly + 4, "越被吸引 →", size=10.5, color=PALETTE["ink_soft"]))
    lx = 100
    for k in range(5):
        parts.append('<rect x="%s" y="%s" width="20" height="14" rx="3" fill="%s"/>'
                     % (_f(lx + k * 22, 1), _f(ly - 8, 1), _color("heat%d" % k)))
    parts.append(_text(lx + 5 * 22 + 6, ly + 4, "（个体内相对偏好，非与他人比较）",
                       size=10.5, color=PALETTE["ink_soft"]))

    for idx, d in enumerate(rows):
        c = idx % cols
        rr = idx // cols
        x = pad + c * (cell_w + pad)
        y = top + rr * (cell_h + pad)
        v = int(_clamp(round(_num(d.get("like5_raw"), 3.0)), 1, 5))
        fill = _color("heat%d" % (v - 1))
        txt_fill = "#FFFFFF" if v >= 4 else PALETTE["ink"]
        parts.append('<rect x="%s" y="%s" width="%s" height="%d" rx="9" fill="%s"/>'
                     % (_f(x, 1), _f(y, 1), _f(cell_w, 1), cell_h, fill))
        parts.append(_text(x + 10, y + 22, _truncate(d.get("domain"), 7), size=12.5,
                           color=txt_fill, weight="bold"))
        sub = d.get("label") or ""
        if sub:
            parts.append(_text(x + 10, y + 40, _truncate(sub, 9), size=10,
                               color=txt_fill, opacity=0.92))
        rank = d.get("rank")
        if rank:
            parts.append(_text(x + cell_w - 8, y + 18, "#%d" % int(_num(rank)),
                               size=11, color=txt_fill, anchor="end", weight="bold",
                               opacity=0.85))
    parts.append("</svg>")
    return "".join(parts)


def domain_ladder(domains: Sequence[dict], *, width: int = 640,
                  title: Optional[str] = None) -> str:
    """DEV 5 领域（或任意带相对位的列表）横向阶梯：复用相对位双向条形逻辑。"""
    return relative_bar_chart(domains, width=width, title=title, label_key="domain")


def confidence_badge(confidence: str) -> str:
    """数据置信度小徽标：high/med/low → 文案 + 柔色点。内联 SVG，可嵌入文字行。"""
    mapping = {
        "high": ("badge_high", "数据置信：较高"),
        "med": ("badge_med", "数据置信：中等"),
        "low": ("badge_low", "数据置信：偏低（解读请更谨慎）"),
    }
    key, text = mapping.get((confidence or "").lower(), ("muted", "数据置信：未知"))
    color = _color(key)
    w = 188 if (confidence or "").lower() == "low" else 120
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d 22" height="18" '
        'role="img" aria-label="%s" font-family="%s" '
        'style="vertical-align:middle">'
        '<rect x="0.5" y="0.5" width="%d" height="21" rx="10.5" fill="%s1f" '
        'stroke="%s" stroke-width="1"/>'
        '<circle cx="12" cy="11" r="4.5" fill="%s"/>%s</svg>'
        % (w, _e(text), FONT, w - 1, color, color, color,
           _text(22, 15, text, size=11, color=PALETTE["ink"]))
    )


def raw_level_dots(level: str) -> str:
    """三点小图：低·中·高，点亮当前原始水平档；在相对位旁恒显原始水平（T-11 视觉锚）。"""
    order = ["低", "中", "高"]
    active = level if level in order else None
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 70 16" height="14" '
        'role="img" aria-label="原始水平：%s" style="vertical-align:middle">' % _e(level)
    ]
    for i, lv in enumerate(order):
        on = lv == active
        fill = _color("accent") if on else _color("track")
        r = 5 if on else 3.5
        parts.append(
            '<circle cx="%d" cy="8" r="%s" fill="%s" stroke="%s" stroke-width="0.8"/>'
            % (8 + i * 24, _f(r, 1), fill, PALETTE["grid"])
        )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# CSS（图表容器外观，供 render.py 注入；纯展示、无外链）
# ---------------------------------------------------------------------------
CHART_CSS = """
.ax-chart svg, .ax-chart > svg { display:block; margin:10px 0; max-width:100%; height:auto; }
svg[role="img"] text { font-family: inherit; }
""".strip()


# ---------------------------------------------------------------------------
# CLI 自测：python charts.py <profile.json> [-o outdir]
# ---------------------------------------------------------------------------
def _main(argv=None):
    import argparse
    import json
    import os
    import xml.dom.minidom as minidom

    parser = argparse.ArgumentParser(description="从 profile.json 生成内联 SVG 图表")
    parser.add_argument("profile", help="profile.json 路径")
    parser.add_argument("-o", "--outdir", default=None, help="输出 SVG 目录（缺省仅自测）")
    args = parser.parse_args(argv)

    with open(args.profile, "r", encoding="utf-8") as fh:
        profile = json.load(fh)
    charts = render_all(profile)

    report = []
    for name, svg in charts.items():
        minidom.parseString(svg.encode("utf-8"))  # 良构校验：解析失败会抛异常
        report.append("%s: well-formed, %d bytes" % (name, len(svg.encode("utf-8"))))
        if args.outdir:
            os.makedirs(args.outdir, exist_ok=True)
            with open(os.path.join(args.outdir, name + ".svg"), "w", encoding="utf-8") as fh:
                fh.write(svg)
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
