# 导出 JSON 契约｜问卷【导出JSON】

> 本文件定义问卷在用户提交后**导出的 JSON 结构**（自包含）。它是问卷前端与未来计分 skill 之间的契约：前端按此结构产出，skill 按此结构消费。
> 与 `docs/item-bank.json`（题库事实源）的关系：题库是「问什么」，导出 JSON 是「这一次某个孩子答了什么 + 怎么答的过程元数据」。键名用英文，文本值用简体中文。
> 版本：本导出契约 `schema_version` 当前为 **`1.1`**（详见 §0 变更说明）。注意：导出 JSON 顶层的 `schema_version`（导出契约版本）与题库 `item_bank_version`（本次所用题库版本，当前 `1.1.2`）是两条独立的版本线，互不绑定。
> **机读事实源**：本文档为人读说明；导出结构的**唯一机读事实源**是 [`schema/export.schema.json`](../schema/export.schema.json)（JSON Schema draft 2020-12）。两者如有歧义，以 `schema/export.schema.json` 为准；前端实际导出（`questionnaire/index.html` 的 `buildExport()`）为行为基准，本文与 schema 均按其真实导出描述。

---

## 0. 版本与变更（schema_version 1.1）

`schema_version` 由 `1.0` 升至 **`1.1`**，纳入前端 `buildExport()` 已实际导出、但 1.0 未登记的字段与口径：

- `responses[]` 新增三个题库附加字段：`report_subscale`、`cluster`、`consistency_pair_id`（均复制自题库，无则为 `null`）。
- `meta.quality` 新增 `quality_flag_status` 对象：标注各质量旗标的**计算来源/状态**（含 `reserved` 预留位说明）。
- `_identity_extra`（顶层可选键）由「约定容忍」正式**登记为允许的顶层字段**（见 §1 与 §2.8）。
- `child.child_id` 语义改为「**单次会话随机标识**」：仅标记本份作答，**跨次不可自动关联**（删除「稳定标识 / 纵向追踪」表述，见 §2.2）。
- `child.age_months_at_submit` 明确**月龄取整口径**（completed-month 法，消除 ±1 月歧义，对应 XS-04，见 §2.2）。

> 向后兼容：1.1 仅为 1.0 的**附加**（新增字段 + 语义澄清），未删除/重命名 1.0 已有字段。期望 `1.0` 的老消费方读取 1.1 导出时，未识别的新字段应忽略而非报错。

---

## 1. 顶层结构

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema_version` | string | 是 | 导出契约版本，须等于消费方期望版本（当前 `"1.1"`）。 |
| `instrument` | object | 是 | 工具标识，整体复制自题库 `instrument`，并附本次所用题库版本。 |
| `child` | object | 是 | 孩子身份信息（昵称/出生年月/性别/child_id）。 |
| `age_band` | string | 是 | 本次根据出生年月判定的年龄段：`"3-4"`/`"4-5"`/`"5-6"`，或 `"out_of_range"`。 |
| `consent` | object | 是 | 知情同意记录（含同意时间戳）。 |
| `responses` | array | 是 | 评分题作答数组（TMP/SEL/DEV/INT/LRN/FAM 的每道**已呈现**题一条）。 |
| `open_ended` | array | 是 | 开放题作答数组（OPEN，可为空数组）。 |
| `meta` | object | 是 | 过程元数据：`timing`（计时）与 `quality`（数据质量预留标记）。 |
| `_identity_extra` | object | 否（前端恒导出，schema 允许） | 身份补充字段：填写人与孩子的关系、每日相处时长，供 skill 侧推断 `familiarity_low`。键名以 `_` 前缀标识「非核心、可选」，消费方未识别时应忽略而非报错。**已在 1.1 正式登记为允许的顶层字段**（见 §2.8）。 |

> 说明：FAM 题虽不计入孩子画像，但仍写入 `responses`（用 `scored:false` 标识），便于生成建议与留痕；是否计分由 `scored` 字段与 skill 决定，而非由是否出现在数组里决定。
> 说明：`_identity_extra` 为前端**实际恒导出**的可选顶层键（见 §2.8），已正式登记。机读 schema `schema/export.schema.json` 在顶层显式允许该键，并放开 `^_` 前缀键（`patternProperties` `"^_"`）以容纳未来扩展。计分 skill 若按严格模式校验，应将 `_identity_extra` 列入允许键，或忽略所有 `_` 前缀键，而非报错。

---

## 2. 各对象字段定义

### 2.1 `instrument`
```
{ "name": string, "version": string, "date": "2026-06-02",
  "age_range": "3-6", "language": "zh-CN",
  "item_bank_version": string }   // 本次使用的题库版本，便于回溯
```

### 2.2 `child`
```
{ "child_id": string,            // 单次会话随机标识（cid- + UUID），仅标记本份作答
  "nickname": string|null,       // 昵称，可为 null（报告则称「孩子」）
  "birth_month": "YYYY-MM",      // 出生年月
  "age_months_at_submit": int,   // 提交时月龄（completed-month 取整，见下）
  "sex": "girl"|"boy"|"prefer_not" }
```
> **`child_id` 语义（已改）**：本字段是**单次会话随机标识**，前端用 `cid-` + `crypto.randomUUID()` 生成（旧环境回退到随机字节拼成的 UUID）。它**仅用于标记这一份作答**，**跨次填写不可自动关联到同一孩子**；不由出生月/昵称/时间派生，避免被反推或被误用作稳定身份。它**不是**稳定标识、**不**支持纵向追踪。若家长想做复测对照，请人工按昵称对应两次结果。
> **`age_months_at_submit` 取整口径（XS-04）**：采用 **completed-month（已满整月）法**，消除 ±1 月歧义。计算等价于：把 `birth_month` 视为「当月 1 日」、把提交日视为提交当月，取两者的**整月差**——
> `age = (submitYear − birthYear) × 12 + (submitMonth − birthMonth)`。
> 即只按「年-月」粒度做差，**不看具体日**，因此同一出生月、同一提交月内的任意日期都得到同一月龄，不会因「日」产生 ±1 个月的抖动。例：`birth_month = 2021-09`、提交于 `2026-06` 任意日 → `(2026−2021)×12 + (6−9) = 57` 个月。`birth_month` 缺失/非法时为 `null`。年龄段（顶层 `age_band`）按此月龄判定（36–47→`3-4`，48–59→`4-5`，60–72→`5-6`，否则 `out_of_range`）。

### 2.3 `consent`
```
{ "agreed": true,                       // 必须为 true 才允许提交
  "consent_version": string,            // 同意书文本版本
  "agreed_at": "2026-06-02T09:30:00+08:00" }  // 同意时间戳（ISO 8601 带时区）
```

### 2.4 `responses[]`（每条一道评分题）
| 字段 | 类型 | 说明 |
|---|---|---|
| `item_id` | string | 题号，如 `"TMP-09"`。 |
| `section` | string | 所属 section：`TMP`/`SEL`/`DEV`/`INT`/`LRN`/`FAM`。 |
| `construct` | string | 顶层构念，复制自题库 `construct`。 |
| `subscale` | string | 子维度，复制自题库 `subscale`。 |
| `report_subscale` | string\|null | 报告呈现用子维度名（复制自题库 `report_subscale`，无则 `null`）。计分聚合用 `subscale`，报告措辞可用此名。 |
| `cluster` | string\|null | 跨 section 的能力簇标签（复制自题库 `cluster`，如 `"resilience"`/`"focus_persistence"`/`"initiative"`/`"inhibitory_control"`/`"mastery"`），用于簇级聚合；无归簇为 `null`。 |
| `consistency_pair_id` | string\|null | 一致性配对题的配对标识（复制自题库 `consistency_pair_id`，如 `"cp-1"`）；同一 id 的正/反向题构成语义配对，供 skill 侧计算 `inconsistency_flag`。无配对为 `null`。 |
| `question_text` | string | 作答时呈现的题干原文（自包含，便于离线复现）。 |
| `scale` | string | `freq5`/`like5`/`single`/`multi`。 |
| `raw_value` | number\|string\|array | 原始作答值：freq5/like5 为 1-5 整数；single 为选项 `v`；multi 为 `v` 的数组。 |
| `value_label` | string\|array | 所选项的中文标签（multi 为标签数组），自包含便于报告。 |
| `age_band` | string | 该题**锚点实际呈现所用的年龄段**（`"3-4"`/`"4-5"`/`"5-6"`），用于锚点复现与跨段分析。注：当顶层 `age_band` 为 `"out_of_range"`（出生月龄 <36 或 >72）时，本字段记录回退后实际呈现锚点的段（<36→`"3-4"`，>72→`"5-6"`），以保证 `anchor_shown` 可据此复现；「本次判定是否越界」以**顶层** `age_band` 为准。 |
| `reverse` | boolean | 是否反向题（复制自题库），供计分方翻转。 |
| `scored` | boolean | 是否计入孩子画像（TMP/SEL/DEV/INT/LRN=true；FAM=false）。 |
| `anchor_shown` | string\|null | 作答时实际呈现给家长的本龄段锚点文本（无则 null），便于审计。 |

### 2.5 `open_ended[]`（每条一道开放题）
```
{ "item_id": "OPEN-01", "construct": string, "question_text": string,
  "text": string }   // 家长输入，可为空字符串
```

### 2.6 `meta.timing`
```
{ "started_at": "2026-06-02T09:18:30+08:00",
  "submitted_at": "2026-06-02T09:30:12+08:00",
  "total_active_sec": int,                 // 总活跃作答秒数（排除挂起/切后台）
  "per_section_sec": { "TMP": int, "SEL": int, "DEV": int,
                        "INT": int, "LRN": int, "FAM": int, "OPEN": int },
  "resumed_from_draft": boolean }          // 是否从草稿续填
```

### 2.7 `meta.quality`（预留，前端可仅写部分，skill 侧补全/判定）
```
{ "straightlining_flag": boolean,   // 长串同选（如连续≥10题完全同档）
  "fast_response_flag": boolean,    // 平均每题作答过快（如<2秒/题，需本地校准）
  "high_missing_flag": boolean,     // 缺答比例过高
  "inconsistency_flag": boolean,    // 反向配对/语义矛盾
  "sdb_halo_flag": boolean,         // 社会赞许/光环疑似（全卷高分且去赞许探针冲突）
  "familiarity_low": boolean,       // 由身份字段「相处时长/关系」推断的低熟悉度
  "recent_disruption": boolean,     // 近期特殊情况（生病/换环境/家庭变动）
  "longstring_max": int,            // 最长连续同选串（原始指标）
  "notes": string|null,             // 备注
  "quality_flag_status": {          // 各旗标的计算来源/状态（见下）
    "sdb_halo": "reserved",
    "inconsistency": "computed_in_skill_from_pairs",
    "longstring": "computed",
    "familiarity_low": "computed_from_contact" } }
```
> 预留约定：未判定的布尔位默认 `false`；`meta.quality` 用于 skill 侧**自动降级报告强度、加重免责**，而非删除作答（Ward & Meade 2023：标注优先）。
>
> **`quality_flag_status`（1.1 新增）**：标注各旗标当前由谁、以何方式得出，避免把「尚未计算」误读为「已判定无异常」。取值枚举：
> - `reserved`：本版**预留、恒 `false`、暂不计算**（如 `sdb_halo`：未加陷阱/探针题，故不下判断）。
> - `computed`：**前端本端已计算**（如 `longstring`：由本端按作答直线度算出 `longstring_max` / `straightlining_flag`）。
> - `computed_in_skill_from_pairs`：留待 **skill 侧**用正/反配对题（`consistency_pair_id`）计算（如 `inconsistency`）。
> - `computed_from_contact`：由 `_identity_extra.daily_contact` 推断（如 `familiarity_low`：每日相处 `lt1` 即判低熟悉度）。
>
> 当前前端 `quality_flag_status` 仅写这四个键，其余旗标（`fast_response`/`high_missing`/`recent_disruption`）默认 `false` 且不在 `quality_flag_status` 中列出，由 skill 侧按需补判。`quality_flag_status` 对象本身的取值集合在 `schema/export.schema.json` 中以枚举固定（含 `reserved`）。

### 2.8 `_identity_extra`（可选顶层键）
```
{ "relationship": "mother"|"father"|"grandparent"|"other_caregiver",
  "daily_contact": "lt1"|"1to3"|"3to6"|"gt6" }
```
> 用途：供 skill 侧推断 `meta.quality.familiarity_low`（如 `relationship=other_caregiver` 且 `daily_contact=lt1` 时熟悉度低）。这两项属身份最小必要范围、与 `child` 同源采集，但因含「关系/相处」非核心标识信息，独立放在 `_` 前缀键内，便于消费方选择性忽略。`child` 对象本身**不含**这两项。

---

## 3. 精简示例（4-5 岁、节选）

```json
{
  "schema_version": "1.1",
  "instrument": {
    "name": "3-6岁幼儿发展优势与兴趣画像测评",
    "version": "1.0.0",
    "date": "2026-06-02",
    "age_range": "3-6",
    "language": "zh-CN",
    "item_bank_version": "1.1.2"
  },
  "child": {
    "child_id": "cid-7f3a9b2e-4c10-4d8a-9f21-0b3e5a7c9d10",
    "nickname": "豆豆",
    "birth_month": "2021-09",
    "age_months_at_submit": 57,
    "sex": "girl"
  },
  "age_band": "4-5",
  "consent": {
    "agreed": true,
    "consent_version": "1.1",
    "agreed_at": "2026-06-02T09:18:05+08:00"
  },
  "responses": [
    {
      "item_id": "TMP-13",
      "section": "TMP",
      "construct": "努力控制 Effortful Control",
      "subscale": "注意聚焦/坚持",
      "report_subscale": "注意聚焦/坚持",
      "cluster": "focus_persistence",
      "consistency_pair_id": null,
      "question_text": "做自己感兴趣的事时，孩子能专注比较长的时间。",
      "scale": "freq5",
      "raw_value": 4,
      "value_label": "经常",
      "age_band": "4-5",
      "reverse": false,
      "scored": true,
      "anchor_shown": "能完成一个有步骤的小任务"
    },
    {
      "item_id": "TMP-14",
      "section": "TMP",
      "construct": "努力控制 Effortful Control",
      "subscale": "注意聚焦/坚持",
      "report_subscale": "注意聚焦/坚持",
      "cluster": "focus_persistence",
      "consistency_pair_id": null,
      "question_text": "做一件事时，孩子很容易被周围的事物吸引而分心。",
      "scale": "freq5",
      "raw_value": 2,
      "value_label": "偶尔",
      "age_band": "4-5",
      "reverse": true,
      "scored": true,
      "anchor_shown": null
    },
    {
      "item_id": "INT-04",
      "section": "INT",
      "construct": "活动领域偏好·语言 INT-LAN",
      "subscale": "语言/故事",
      "report_subscale": "语言/故事",
      "cluster": null,
      "consistency_pair_id": null,
      "question_text": "听故事、读绘本、自己翻看图画书时，孩子的喜欢程度是？",
      "scale": "like5",
      "raw_value": 5,
      "value_label": "一玩就停不下来",
      "age_band": "4-5",
      "reverse": false,
      "scored": true,
      "anchor_shown": null
    },
    {
      "item_id": "FAM-08",
      "section": "FAM",
      "construct": "屏幕与媒体 Screen Use",
      "subscale": "屏幕与媒体使用",
      "report_subscale": "屏幕与媒体使用",
      "cluster": null,
      "consistency_pair_id": null,
      "question_text": "孩子平时每天看屏幕（电视/平板/手机）大约多久？",
      "scale": "single",
      "raw_value": "05to1",
      "value_label": "半小时到1小时",
      "age_band": "4-5",
      "reverse": false,
      "scored": false,
      "anchor_shown": null
    },
    {
      "item_id": "FAM-12",
      "section": "FAM",
      "construct": "照看结构 Caregiving Structure",
      "subscale": "照看结构与支持网络",
      "report_subscale": "照看结构与支持网络",
      "cluster": null,
      "consistency_pair_id": null,
      "question_text": "平时孩子主要由谁照看？（可多选）",
      "scale": "multi",
      "raw_value": ["parents", "grandparents"],
      "value_label": ["父母", "祖辈"],
      "age_band": "4-5",
      "reverse": false,
      "scored": false,
      "anchor_shown": null
    }
  ],
  "open_ended": [
    {
      "item_id": "OPEN-02",
      "construct": "兴趣线索 Interest Cue",
      "question_text": "孩子最近为什么着迷？有没有一件事/一样东西他特别上心、反复要玩或要看？",
      "text": "最近迷上恐龙，每天要听恐龙绘本，自己还会编恐龙的故事。"
    }
  ],
  "meta": {
    "timing": {
      "started_at": "2026-06-02T09:18:30+08:00",
      "submitted_at": "2026-06-02T09:30:12+08:00",
      "total_active_sec": 642,
      "per_section_sec": { "TMP": 165, "SEL": 138, "DEV": 96, "INT": 110, "LRN": 88, "FAM": 33, "OPEN": 12 },
      "resumed_from_draft": false
    },
    "quality": {
      "straightlining_flag": false,
      "fast_response_flag": false,
      "high_missing_flag": false,
      "inconsistency_flag": false,
      "sdb_halo_flag": false,
      "familiarity_low": false,
      "recent_disruption": false,
      "longstring_max": 4,
      "notes": null,
      "quality_flag_status": {
        "sdb_halo": "reserved",
        "inconsistency": "computed_in_skill_from_pairs",
        "longstring": "computed",
        "familiarity_low": "computed_from_contact"
      }
    }
  },
  "_identity_extra": {
    "relationship": "mother",
    "daily_contact": "3to6"
  }
}
```

> 示例为节选：完整导出的 `responses` 应包含本龄段呈现的全部评分题（4-5 段 78 评分题 + 13 道 FAM）。`open_ended` 含家长实际填写的开放题（未填可省略或留空 `text`）。
