# 导出 JSON 契约｜问卷【导出JSON】

> 本文件定义问卷在用户提交后**导出的 JSON 结构**（自包含）。它是问卷前端与未来计分 skill 之间的契约：前端按此结构产出，skill 按此结构消费。
> 与 `docs/item-bank.json`（题库事实源）的关系：题库是「问什么」，导出 JSON 是「这一次某个孩子答了什么 + 怎么答的过程元数据」。键名用英文，文本值用简体中文。
> 版本：与题库 `schema_version` 对齐（当前 `1.0`）。

---

## 1. 顶层结构

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema_version` | string | 是 | 导出契约版本，须等于消费方期望版本（当前 `"1.0"`）。 |
| `instrument` | object | 是 | 工具标识，整体复制自题库 `instrument`，并附本次所用题库版本。 |
| `child` | object | 是 | 孩子身份信息（昵称/出生年月/性别/child_id）。 |
| `age_band` | string | 是 | 本次根据出生年月判定的年龄段：`"3-4"`/`"4-5"`/`"5-6"`，或 `"out_of_range"`。 |
| `consent` | object | 是 | 知情同意记录（含同意时间戳）。 |
| `responses` | array | 是 | 评分题作答数组（TMP/SEL/DEV/INT/LRN/FAM 的每道**已呈现**题一条）。 |
| `open_ended` | array | 是 | 开放题作答数组（OPEN，可为空数组）。 |
| `meta` | object | 是 | 过程元数据：`timing`（计时）与 `quality`（数据质量预留标记）。 |
| `_identity_extra` | object | 否 | 身份补充字段：填写人与孩子的关系、每日相处时长，供 skill 侧推断 `familiarity_low`。键名以 `_` 前缀标识「非核心、可选」，消费方未识别时应忽略而非报错。 |

> 说明：FAM 题虽不计入孩子画像，但仍写入 `responses`（用 `scored:false` 标识），便于生成建议与留痕；是否计分由 `scored` 字段与 skill 决定，而非由是否出现在数组里决定。
> 说明：`_identity_extra` 为前端实际导出的可选顶层键（见 §2.8）。计分 skill 若按 `additionalProperties:false` 严格校验，应将 `_identity_extra` 列入允许键，或忽略所有 `_` 前缀键。

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
{ "child_id": string,            // 本地生成的稳定标识，关联同一孩子多次填写
  "nickname": string|null,       // 昵称，可为 null（报告则称「孩子」）
  "birth_month": "YYYY-MM",      // 出生年月
  "age_months_at_submit": int,   // 提交时月龄（由 birth_month 与 submitted_at 计算）
  "sex": "girl"|"boy"|"prefer_not" }
```

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
  "notes": string|null }            // 备注
```
> 预留约定：未判定的布尔位默认 `false`；`meta.quality` 用于 skill 侧**自动降级报告强度、加重免责**，而非删除作答（Ward & Meade 2023：标注优先）。

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
  "schema_version": "1.0",
  "instrument": {
    "name": "3-6岁幼儿发展优势与兴趣画像测评",
    "version": "1.0.0",
    "date": "2026-06-02",
    "age_range": "3-6",
    "language": "zh-CN",
    "item_bank_version": "1.0.0"
  },
  "child": {
    "child_id": "cid-7f3a9b2e",
    "nickname": "豆豆",
    "birth_month": "2021-09",
    "age_months_at_submit": 56,
    "sex": "girl"
  },
  "age_band": "4-5",
  "consent": {
    "agreed": true,
    "consent_version": "1.0",
    "agreed_at": "2026-06-02T09:18:05+08:00"
  },
  "responses": [
    {
      "item_id": "TMP-13",
      "section": "TMP",
      "construct": "努力控制 Effortful Control",
      "subscale": "注意聚焦/坚持",
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
      "notes": null
    }
  },
  "_identity_extra": {
    "relationship": "mother",
    "daily_contact": "3to6"
  }
}
```

> 示例为节选：完整导出的 `responses` 应包含本龄段呈现的全部评分题（4-5 段 76 评分题 + 13 道 FAM）。`open_ended` 含家长实际填写的开放题（未填可省略或留空 `text`）。
