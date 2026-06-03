---
name: child-strengths-interest-report
description: 3–6 岁幼儿「发展优势 + 兴趣画像」非诊断测评报告生成。当用户要为某个孩子的问卷导出 JSON 生成画像报告、批量处理 inbox 里的导出、或把测评结果写成给家长看的温暖报告时使用。本 skill 编排「校验→计分→候选筛选→Claude 撰写叙事→渲染→归档」全流程。非诊断、个体内（ipsative）相对比较、不报人群百分位、不下临床结论。
---

# 幼儿发展优势与兴趣画像报告 · 工作流

你（运行此 skill 的 Claude）要把一份问卷导出 JSON 变成一份给家长看的、温暖、循证、**非诊断**的画像报告。
**确定性部分（校验/计分/候选筛选）交给脚本；叙事撰写与活动裁剪由你来做，但必须戴着下面的镣铐跳舞。**

> 一句话定位：脚本算「这个孩子自己内部相对突出/相对还在发展中的是什么、可挂哪些循证活动」；
> 你负责把它写成有温度、因人而异、可溯源、绝不制造焦虑的文字。

---

## 0. 铁律（违反即返工，先背下来）

1. **非诊断**：全程不出现任何诊断/筛查词（自闭、发育迟缓、多动、障碍、落后、达标……），不下临床结论，不制造焦虑。
2. **个体内（ipsative）**：只做「孩子和自己比」的相对比较。**绝不**出现「超过 X% 的孩子」「同龄人平均」等人群百分位/常模表述。
3. **原始水平防护（T-11）**：中心化必然产生相对低项。**原始水平为高（`protected_high=true` 或 `raw_band.level=高`）的项，绝不写成劣势/待发展**，只能写「相对没那么突出但仍很常见」。
4. **goodness-of-fit 视角**：建议是「顺势放大长板/兴趣」+「按孩子气质给低门槛扶持」，不是「补短板纠错」。结合每条活动的 `temperament_fit_notes` 因娃调适。
5. **可溯源**：每条具体建议必须挂一个**真实存在的 activity id**（来自候选 shortlist）。不臆造活动、不臆造 target。
6. **用昵称**：全程用 `meta.nickname` 称呼孩子，口吻温暖、对家长友好、去刻板化（不贴「内向就是缺点」之类标签）。
7. **据实标注置信**：`confidence` 为 `med/low` 时弱化绝对表述、加重免责话术。
8. **红旗软措辞**：`red_flags` 只能用温和、非评判的软转介模板，绝不诊断、绝不下结论。

---

## 环境准备（首次/换机一次性）

脚本依赖纯标准库，**仅两处例外**需预装；本机已装，换机才需重做：

```bash
pip install jsonschema playwright      # jsonschema 供 score.py 校验导出；playwright 供 PDF
playwright install chromium            # 联网一次性缓存 chromium（render.py 设了 PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1，只用缓存、不每次下载）
```

- 无 chromium 时用 `render.py --no-pdf`：仍正常产出 `report.md` 与 `report.html`，只跳过 PDF（退出码 3 表示「仅 PDF 失败、MD/HTML 已落盘」，不丢人读主产物）。
- 脚本里多处简称的资源全路径：活动库在 `skill/activity_bank/activity-bank.json`（select_activities 的 `DEFAULT_BANK` 已默认指向，CLI 无需手填）；profile 完整契约见 `skill/PROFILE_SCHEMA.md`；HTML 外壳模板在 `skill/templates/base.html`。

---

## 1. 取件：从 inbox/ 拿 JSON（支持批量 / 单份）

输入目录 `inbox/`，每份导出按**日期子目录**组织：`inbox/<YYYY-MM-DD>/*.json`（`schema/export.schema.json`，schema_version 1.1）。

- **单份**：用户点名某个文件 → 只处理该文件。
- **批量**：用户说「处理 inbox」/没点名 → 用 Glob `inbox/**/*.json`（**递归**，匹配日期子目录里的文件；扁平 `inbox/*.json` 会漏件）列出全部，**逐份**跑下面 2–6 的完整管线（互不影响；任一份失败不阻断其余，最后汇总成功/失败清单）。

```
inbox/**/*.json   ──→  每份独立跑管线  ──→  reports/{昵称-childid-日期}/  +  processed/{原文件}
```

> 处理顺序对结果无影响（每份独立、确定性）。批量时对每份单独 try：失败的记录文件名 + 错误 code，继续下一份。

---

## 2. 校验 + 计分 → profile.json（确定性，脚本做）

```bash
python skill/scripts/score.py <inbox/某份.json> -o <work/profile.json>
```

- 内部先做 `export.schema.json` 校验，再按 `scoring-config.json` 与方法学 §4.6–4.8 计分。
- **退出码**：`0` 成功；`2` 失败（schema 校验失败 / 解析失败 / 坏输入，stderr 给 `{"code":...}`）。
- 产出 `profile.json`（**完整契约以 `skill/PROFILE_SCHEMA.md` 为准**）：`sections / clusters / subscales /
  interest_map / interest_quality / relative_strengths_top / growth_areas_top / red_flags / data_quality /
  baseline / reverse_applied / notes`。

**计分已替你做完的防护**（你不要重算、只读取）：簇合并只占基线一席、单题不排序、reverse 已翻转、
like5/freq5 分基线、**T-11 把原始高项移出 growth_areas_top.items**、红旗保守触发。

---

## 3. 候选筛选 → candidates.json（确定性，脚本做）

```bash
python skill/scripts/select_activities.py <work/profile.json> -o <work/candidates.json>
```

退出码 `0` 成功 / `2` 坏输入。产出 `candidates.json.advice_lines[]`，每条「建议线」含：

- `line_kind`：`amplify`（顺势放大：相对优势 section/cluster + 强兴趣领域 + 高成色兴趣品质信号）
  或 `nurture`（该补的：个体内相对靠后**且原始非高**的 section/cluster/DEV 领域，低挫败入口）。
- `label` / `rationale`：人读的成线理由（已溯源到 profile 的 ref 与相对位）。
- `protected_high`：True 表示该方向原始为高 → 只能放大、**绝不写成待发展**。
- `shortlist[]`：排好序的候选活动（`id / name / type / matched_targets / evidence_strength /
  temperament_fit_notes / safety_notes`）。已做 target 命中数排序、有据优先、game/exercise/companionship 类型均衡。

> 脚本只**提候选**，不裁剪、不写文采。`warnings[]` 若非空（某线无命中/越库 target），在报告里相应弱化或跳过该线。

---

## 4. 【你来做】撰写各章叙事 + 裁剪活动

读 `profile.json` + `candidates.json` + 方法学，撰写报告。**强约束清单**：

**结构建议**（可微调，但都要在）：
1. 开篇致家长：用昵称、暖场、点明「这是优势与兴趣画像，不是考试、不是诊断」。
2. 气质风格小像（TMP）：用 `raw_band` 锚点语义 + 个体内相对位描述，去刻板化。
3. 相对突出的长板（`relative_strengths_top` / amplify 线）：每个 section/cluster **只写一条**叙述（簇不可拆成多条独立优势）。
4. 兴趣画像（`interest_map` 8 领域热度 + `interest_quality` 成色）：like5 偏好与行为分**分开**讲。
5. 成长方向（**仅** `growth_areas_top.items` + nurture 线）：写成「顺着 goodness-of-fit 可以多给的机会」。
6. 给家长的活动建议：从候选 shortlist **裁剪**，每条挂 activity id；按 `temperament_fit_notes` 因娃调适；三类（游戏/锻炼/陪伴）均衡。
7. 温和收尾 + 非诊断免责声明 + （若有）红旗软提示。

**撰写禁令（NEVER）**：
- ❌ 不把 ipsative 相对低点说成「缺陷/落后/问题/弱项/差」。相对低 = 「相对还在发展中」，仅此而已。
- ❌ 不给 `protected_high=true` 的项写任何待发展/补救建议；只夸、只放大。
- ❌ 不出现人群百分位、同龄对照、达标线、排名分数。
- ❌ 不出现诊断词、不下临床结论、不制造焦虑。
- ❌ 不臆造活动 id / target / 效果声明；建议必须来自 shortlist，活动的 `evidence_strength` 是「一般性发展原理」时不夸大成「被证实有效」。
- ❌ 不把单题子维度（带 caveat）当成独立优势/劣势排序。
- ❌ 不忽略 `confidence`：med/low 时必须弱化措辞、加重免责。

**必须做（ALWAYS）**：
- ✅ 全程用昵称；口吻温暖、具体、给家长可操作的画面感。
- ✅ 每个簇只写一条叙述；amplify=放大长板/兴趣，nurture=低门槛扶持。
- ✅ 每条活动建议括注 `（id）`，并据 `temperament_fit_notes` 给「针对你家娃可以这样调」。
- ✅ 引用 `raw_band` 的锚点语义（「经常/几乎总是」「一玩就停不下来」）让家长有体感。
- ✅ `red_flags` 非空时，原样使用其 `wording` 软模板，温和收尾。

### 4.1 把叙事 + 活动组装成 RCO（报告内容对象）—— 喂给 render.py 的输入

第 5 步的 `render.py` 不接受你手搓的 HTML，而是吃一个 **RCO（report content object）**，由它一次性产出 MD/HTML/PDF 三件套并保证同源。你要在本步把成果写成一个 `rco.json`：

```jsonc
{
  "profile": { …直接内联 profile.json，或第 5 步用 --profile 单独给… },
  "glance":  { "portrait": "一句话画像", "strengths_top": [...], "three_things": ["本周3件事", ...] },
  "narratives": { "overview":…, "temperament":…, "social_emotional":…, "dev_snapshot":…,
                  "interests":…, "learning":…, "family_env":…, "synthesis":…, "boundary":…, "retest":… },
  "activities": [ … 见下「富化」 … ],
  "soft_hints": []
}
```

**活动富化（关键，shortlist 字段 ≠ RCO.activities 字段）**：`candidates.json` 的 shortlist 每条只有扁平的
`id / name / type / matched_targets / evidence_strength / temperament_fit_notes / safety_notes`，**缺 `steps / why / difficulty_ladder / evidence.basis`**。你要：

1. 从 shortlist 选定的每个 **id** 回 `skill/activity_bank/activity-bank.json` 按 id 捞回完整条目；
2. 取其 `steps`（数组）、`difficulty_ladder`（`{easier,harder}`）、`evidence`（**嵌套对象** `{strength, basis}`，注意 shortlist 给的是扁平字符串 `evidence_strength`、键名也不同）、`safety_notes`；
3. `why` 由你写（顺势放大/低门槛扶持的因娃理由，结合 `temperament_fit_notes`）；
4. 写成 RCO 的一条 activity：`{id, name, type, why, steps, difficulty_ladder, evidence:{strength,basis}, safety_notes}`。

> 现成范本：`questionnaire/sample-rco.json`（含 glance + 10 章 narratives + 内联 profile + 3 条已富化 activities），照它的形状写即可。

---

## 5. 渲染 → MD / HTML / PDF 到 reports/{昵称-childid-日期}/

输出目录：`reports/{nickname}-{child_id短码}-{YYYY-MM-DD}/`（child_id 取后 8 位即可，避免目录名过长）。

**用 render.py 一次产出三件套**（不要手搓 HTML——它会绕过块树同源、T-11 防护框与打印分页）：

```bash
python skill/scripts/render.py <work/rco.json> --profile <work/profile.json> -o <reports/{昵称-childid-日期}/>
# rco.json 已内联 profile 时可省略 --profile；无 chromium 缓存时加 --no-pdf 仍出 MD/HTML
```

render.py 把 RCO 摊平成统一「块树」，MD 与 HTML 从同一棵树序列化（同源同内容），图表走
`skill/scripts/charts.py` 内联 SVG（`relative_bar_chart` / `interest_heatmap` / `confidence_badge` /
`raw_level_dots` / `domain_ladder`），离线自包含、遵守 T-11（protected_high 用保护色不用警示色）、不画人群百分位。

- **退出码**：`0` 三件套全成；`2` 坏输入/RCO 解析失败（不出产物）；`3` 仅 PDF 失败但 MD/HTML 已落盘（无 chromium 时的常见情形，可接受）。
- 某图表数据缺失时 charts.py 返回温和占位 SVG 而非报错，渲染不中断整篇。

---

## 6. 归档：原始 JSON 移到 processed/

报告成功落盘后，把 `inbox/` 里这份原始导出 JSON 移到 `processed/`（保留原文件名，便于回溯）。
批量结束后，给用户一份小结：成功 N 份（各报告目录路径）、失败 M 份（文件名 + 错误 code）。

---

## 错误处理 & 边界情形

| 情形 | 触发 | 处置 |
|---|---|---|
| **校验失败** | `score.py` 退出码 2 | 不生成报告；记下文件名 + stderr 的 `code`；批量时继续下一份；告知用户该份需修复导出。 |
| **PDF 渲染失败** | `render.py` 退出码 3 | MD/HTML 已落盘、仅缺 PDF（多为无 chromium 缓存）；可接受，记一笔「缺 PDF」并提示装 `playwright install chromium` 后补打印。 |
| **越龄段 / 月龄越界** | profile `notes[]` 有月龄越界回退提示 | 照常出报告，但在开篇与免责里点明「孩子月龄接近龄段边界，描述供参考」，弱化绝对表述。 |
| **低置信** | `confidence=low`（或 med） | 全篇弱化绝对措辞、加重免责；`familiarity_low` 时额外说明「填写者与孩子相处时间有限，画像仅供参考」。 |
| **某建议线无候选** | `candidates.warnings[]` 提到该线无命中 | 跳过该线，不硬凑活动；绝不臆造活动填补。 |
| **红旗触发** | `red_flags[]` 非空 | 仅用其 `wording` 软模板温和提示「可以问问儿保医生/专业老师」；不诊断、不并入优势分、不制造焦虑。 |
| **数据质量旗标** | `data_quality.flags` 有 straightlining/fast_response/high_missing/inconsistency | 标注优先而非删除：温和提示「这次作答可能较快/有缺答，结果供参考」，降低强度，不指责家长。 |

---

## 「不要把 ipsative 相对低点说成缺陷」· 明确禁令清单

1. 相对低 ≠ 差。措辞只能是「相对还在发展中」「相对没那么突出」，且要并陈原始水平带。
2. `protected_high=true` → 原始水平高，**任何情况下不进成长方向、不写补救**。
3. growth 方向只取 `growth_areas_top.items`（score.py 已做 T-11 过滤）；`protected_high_relative_low[]` 里的项**只读不写成短板**。
4. 不把「相对低」翻译成家长容易焦虑的词（跟不上、不如别人、有问题）。
5. nurture 建议的语气是「顺着孩子的节奏，多给一点这样的好玩机会」，不是「需要训练/纠正」。
6. 簇（resilience/focus_persistence/…）相对低时，整簇只写一条温和叙述，不拆成多条「弱点」。

---

## 命令速查

```bash
# 环境（首次/换机一次）
pip install jsonschema playwright && playwright install chromium

# 单份全管线
python skill/scripts/score.py inbox/2026-06-03/xxx.json -o work/profile.json          # ① 校验+计分
python skill/scripts/select_activities.py work/profile.json -o work/candidates.json   # ② 候选筛选
#   ③ 由你撰写叙事 + 富化活动 → 组装 work/rco.json（见 §4.1，范本 questionnaire/sample-rco.json）
python skill/scripts/render.py work/rco.json --profile work/profile.json -o reports/{昵称-childid-日期}/  # ④ 渲染三件套（无chromium加 --no-pdf）
#   ⑤ 把原始 JSON 移到 processed/

# 批量：对 inbox/**/*.json（递归）逐份重复 ①②③④⑤

# 自检（开发时）
python -m unittest skill.tests.test_scoring -v
```
