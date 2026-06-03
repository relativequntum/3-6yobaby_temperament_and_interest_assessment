# 报告渲染层（render.py + templates）说明

> 三件套产出：`report.md`（权威源）/ `report.html`（响应式·手机优先·内联自包含离线）/
> `report.pdf`（A4，用已缓存的 Playwright/Chromium 打印 `report.html`）。
> 渲染层**不写叙事**——叙事是输入；本层只负责结构、占位、图表、口吻护栏与三格式同源。

## 文件

| 文件 | 作用 |
|---|---|
| `skill/scripts/render.py` | 渲染主程序：报告内容对象(RCO) → 块树(doc model) → MD/HTML/PDF |
| `skill/scripts/charts.py` | 自包含内联 SVG 图表（三主图 + 轻量内联组件），非诊断·T-11 安全 |
| `skill/templates/base.html` | HTML 外壳：内联响应式 CSS + 打印样式（`{{TITLE}}` `{{BODY}}` 占位） |

## 运行

```bash
# RCO 内联 profile：
python skill/scripts/render.py <rco.json> -o <out_dir>
# profile 单独给：
python skill/scripts/render.py <rco.json> --profile profile.json -o <out_dir>
# 跳过 PDF（仅 MD/HTML）：
python skill/scripts/render.py <rco.json> -o <out_dir> --no-pdf
```

退出码：`0` 成功；`2` 读取/解析/缺 profile 失败；`3` PDF 失败（MD/HTML 已生成）。
PDF 自动设 `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`，用已缓存 Chromium 打印，A4、含背景、矢量。

## 报告内容对象（RCO）契约

`render_report(rco_dict, out_dir, make_pdf, profile)` 的输入。顶层键：

```jsonc
{
  "profile": { ... },          // 必填：score.py 输出（PROFILE_SCHEMA 1.0）。也可用 --profile 外给
  "narratives": {              // 选填：LLM 写好的各章叙事（缺则用中性合规兜底，绝不编造结论）
    "overview": "...",         // 概览
    "temperament": "...",      // 气质
    "social_emotional": "...", // 社会情绪与自我调节
    "dev_snapshot": "...",     // 发展快照
    "interests": "...",        // 兴趣画像
    "learning": "...",         // 学习品质
    "family_env": "...",       // 家庭与环境如何调节
    "synthesis": "...",        // 综合画像
    "boundary": "...",         // 边界声明
    "retest": "...",           // 复测建议
    "actions_intro": "...",    // 行动建议引言（选填）
    "appendix": "..."          // 附录补充（选填，可含基础 markdown）
    // 值可为字符串或字符串数组（数组按段落拼接）；支持基础 markdown（#/-/1./**/`/>）
  },
  "glance": {                  // 选填：一页速览（缺则从 profile 兜底拼装）
    "portrait": "一句话画像…",
    "strengths_top": ["专注-坚持（原始高）", "..."],   // 相对优势 TOP（字符串数组）
    "three_things": ["本周第1件事", "第2件", "第3件"]    // 本周三件事
  },
  "activities": [              // 选填：已选定并裁剪好的活动（每条带来源 id）
    {
      "id": "ACT-INT-001",                 // 来源活动 id（报告会回溯标注）
      "name": "厨房打击乐·跟拍子",
      "type": ["game"],                    // game/exercise/companionship（决定归入哪条线；缺省归陪伴）
      "why": "为什么适合这个孩子…",          // 也可用 reason
      "steps": ["…","…"],                   // 也可用 how（字符串）
      "difficulty_ladder": {"easier":"…","harder":"…"},  // 或 ladder_tip 直接给一句
      "evidence": {"strength":"有据","basis":"…"},
      "safety_notes": "…"                  // 或 safety
    }
  ],
  "soft_hints": ["温和的小提示…"],   // 选填：额外软提示（与 profile.red_flags 一并呈现）
  "palette": { ... }                // 选填：当前被 charts.py 忽略（图表用模块级 PALETTE）
}
```

> 注：当前 `charts.py` 的图表用模块级 `PALETTE`，不接受 per-call palette；RCO 的
> `palette` 字段保留向后兼容但不生效。如需换肤，改 `charts.py` 的 `PALETTE`。

## 报告结构（MD 与 HTML 同源同内容）

封面 → **一页速览**（一句话画像＋相对优势 TOP＋本周 3 件事）→ 详尽：
概览（昵称/月龄/数据置信标）→ 气质 → 社会情绪与自我调节 → 发展快照（+软提示如触发）
→ 兴趣画像（热度图＋热度条形）→ 学习品质 → 家庭与环境如何调节 → 综合画像
（各领域相对位雷达＋五大优势簇＋相对优势 TOP；成长方向带 T-11 防护）
→ 行动建议（游戏/锻炼/家庭陪伴三线，每条标来源活动 id）→ 边界声明＋软提示＋复测建议
→ 附录（方法学与局限）。

### 同源保证（doc model）
render.py 先把 RCO 摊平成一棵「块树」(blocks)，MD 与 HTML 各自从同一棵块树序列化，
从根本保证两格式同源同内容。MD 是权威文字源：图表以「图注＋文字说明」表达（不内嵌 SVG，
保证纯文本可读）；HTML 内嵌同一批 SVG。已验证：MD 中每个 `##` 章节标题都出现在 HTML。

## 口吻与边界护栏（结构层强制，措辞由叙事承载）

- 全程**非诊断、个体内（ipsative）相对比较**；不报人群百分位、不下临床结论。图表均标
  「个体内相对·非与他人比较」，不画达标线/百分位。
- **T-11 人为低点防护**：`profile.growth_areas_top.items` 已由计分层剔除原始高项；渲染层
  对 `protected_high` 且相对偏低者额外输出保护话术框（柔紫 `.guard`），绝不渲染成短板。
- 子维度恒带「题少／子维度间相关高，仅供参考」，不进入排序。
- 数据 `confidence≠high` 时，概览处温和提示「填写似乎较快/前后不太一致…要不要回看」。
- 软提示（`red_flags`）用温和、非诊断模板，结尾导向「问问专业人士」。
- 用昵称称呼、去刻板化（性别仅措辞、不比较不改分）。

## 离线自包含 & 打印

HTML 全内联（CSS 在 `base.html`、图表为内联 SVG）；已验证产物**零外部 http(s) 资源引用**，
可离线打开。PDF 由 Playwright `page.pdf(format=A4, print_background, prefer_css_page_size)`
打印 `report.html` 得到（`@page{size:A4}` + 打印样式控制分页、避免卡片跨页断裂）。
