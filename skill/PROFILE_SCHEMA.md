# profile.json 结构说明（计分引擎输出契约）

`skill/scripts/score.py` 消费一份导出 JSON（`schema/export.schema.json`，`schema_version` 1.1），
经 schema 校验后按 `skill/scoring/scoring-config.json` 与方法学 `docs/理论依据与方法学.md` §4.6-4.8
计分，产出本文件描述的 `profile.json`（`profile_schema` 1.0）。

> 铁律：全程**非诊断、个体内（ipsative）相对比较**；不报人群百分位、不下临床结论。计分**确定性可复现**（无随机；同一输入→同一输出）。**T-11 人为低点防护**：中心化必然产生相对低项，必须并行呈现【原始水平描述带】，**原始为高的项绝不标为劣势/待发展**。

运行：

```bash
python skill/scripts/score.py <export.json> [-o profile.json] [--no-validate]
# 默认自动定位 skill/scoring/scoring-config.json 与 schema/export.schema.json
```

退出码：`0` 成功；`2` 失败（schema 校验失败 / 读取解析失败 / 坏输入，stderr 给 `code`）。

---

## 顶层字段

| 字段 | 类型 | 含义 |
|---|---|---|
| `schema` | object | `{profile_schema:"1.0", doc:"skill/PROFILE_SCHEMA.md"}` |
| `meta` | object | 昵称/child_id/龄段/`effective_age_band`(SA-03：越界回退后实际生效龄段)/月龄/性别/提交时间/题库版本/计分配置版本/非诊断声明 |
| `data_quality` | object | 各质量旗标 + `confidence`(high/med/low) + 说明 + 处置原则 |
| `baseline` | object | freq5 个人总均值基线（中心化基准）与构成单位 |
| `sections[]` | array | TMP/SEL/DEV/INT(B层)/LRN 各一个个体内相对位（默认报告粒度） |
| `clusters[]` | array | 5 组同义簇，各合并为单一指标、只计基线一次 |
| `subscales[]` | array | 子维度定性补充（恒带 caveat、不排序） |
| `interest_map` | object | INT A 层 8 领域 like5 个体内兴趣热度排序（兴趣画像） |
| `interest_quality[]` | array | INT B 层品质信号（并入相应簇的成色读出） |
| `relative_strengths_top[]` | array | 个体内相对突出项（section/cluster），最多 5 |
| `growth_areas_top` | object | 成长方向（**T-11 防护**：原始高项绝不列入） |
| `red_flags[]` | array | 保守软转介（非诊断温和措辞），无则空 |
| `reverse_applied[]` | array | 翻转过的反向题记录（item_id/scale/raw_value/oriented） |
| `notes[]` | array | 报告级声明（非诊断、ipsative、簇合并、越界/低置信提示等） |

---

## meta

```jsonc
{
  "nickname": "豆豆", "child_id": "cid-...", "age_band": "4-5",
  "effective_age_band": "4-5",
  "age_months_at_submit": 54, "sex": "girl",
  "submitted_at": "2026-06-02T17:34:32+08:00",
  "item_bank_version": "1.1.2", "scoring_config_version": "1.0.0",
  "source_export_schema_version": "1.1",
  "non_diagnostic_notice": "本配置仅用于个体内相对优势画像；不做诊断/筛查……"
}
```

## data_quality

- `flags`：`straightlining` / `fast_response` / `high_missing`(+`missing_ratio`) / `inconsistency` / `familiarity_low` / `recent_disruption` / `sdb_halo`(预留) / `resumed_from_draft`。
  来源融合：`meta.quality`（前端 computed）+ skill 侧自算（`longstring_max≥10`→直答；`总活跃/题数<2s`→过快；缺答比例≥20%→高缺答；`consistency_pair_id` cp-1..cp-4 同向化后差值≥3→矛盾；`_identity_extra.daily_contact=lt1`→familiarity_low）。
- `confidence`：硬旗(直答/过快/高缺答/矛盾)≥2 或 硬1+软1 → `low`；硬1 或 软≥1 → `med`；否则 `high`。
- `explanations[]`：人读说明；`handling`：标注优先而非删除（Ward & Meade 2023）。

## baseline

```jsonc
{
  "freq5_person_mean": 3.696,   // 中心化基准：仅由计入画像的 freq5 题构成
  "n_units": [ {"kind":"cluster","id":"resilience"}, {"kind":"subscale","id":["DEV","沟通/语言"]}, ... ],
  "scope": "按量表/按section（freq5 行为题；like5 不并入）"
}
```

**单位口径（§4.6 “只占一席”）**：每个簇合并指标算 1 个单位；每个**非簇、≥2 题**的 freq5 子维度算 1 个单位；基线 = 各单位均值的均值（等权，避免题量大的簇/维度放大权重）。
**剔除**：like5 领域(INT-01..08)、standalone 单题(TMP-03/04/05)、任何“本段启用题数=1 且不归簇”的 freq5 单题、FAM(scored:false)、OPEN。

## sections[]

每条：`id`、`name`、`scale`、`raw_mean`、`raw_band`(=`{level,phrase,scale}`，**原始水平描述带**)、`n_items`、`n_units`(= 该 section 折叠后的单位数：簇折一席 + 非簇 freq5 子维度各一席)、`within_child_relative`(= section 均值 − baseline)、`relative_label`、`protected_high`(原始 band=高)。
按 `within_child_relative` 降序。**DEV** 另含 `domain_order[]`（5 领域在孩子内部排序，每个领域同样带 `raw_band`/相对位/`protected_high`）。

> **SCORE-F1 同口径**：section（及 DEV 领域）的 `raw_mean` 与个人基线**同一聚合口径**——section 内**先把同义簇折叠为一席、再与非簇 freq5 子维度等权**求「单位均值的均值」，使 `within_child_relative` 的零点与基线一致（消除原「题级均值 vs 单位均值之均值」约 0.08 的零点偏差）。

`relative_label` 取值：`相对突出`(rel≥ `strong_at_or_above`) / `中间位置` / `相对还在发展中`(rel≤ `low_at_or_below` 且非原始高) / **`相对没那么突出但仍很常见`**(rel≤ `low_at_or_below` 但原始 band=高，**T-11 防护**)。档位阈值（**CMC-03**）读自 `scoring-config.json` 的 `relative_label_thresholds`（`strong_at_or_above` 默认 0.30、`low_at_or_below` 默认 −0.30；缺省回退 ±0.30）。判档所用 rel 与 `within_child_relative` **同口径**（均为 round 后值，**SCORE-F3**），避免极窄窗口下 label 与 growth 池不一致。

## clusters[]

5 组同义簇（focus_persistence/inhibitory_control/initiative/resilience/mastery），各为单一合并指标：
`cluster`、`report_name`、`raw_mean`(簇内启用题统一均值)、`raw_band`、`n_items`、`members_used[]`、`within_child_relative`、`relative_label`、`protected_high`、`merged_single_metric:true`、`counts_in_baseline_once:true`。
**报告对每簇只写一条叙述，绝不拆成多个独立优势。**

## subscales[]

定性补充，**不进入个体内排序**：`section`、`report_subscale`、`scale`、`raw_mean`、`raw_band`、`n_items`、`in_cluster`、`ranked:false`、`excluded_from_baseline`、`baseline_contribution`、`standalone_single_item`、`caveat:"题少／子维度间相关高，仅供参考"`。

> **SCORE-F6 防误读**：`excluded_from_baseline` 仅指「该子维度是否**作为独立子维度单位**进入 freq5 基线」——对 `in_cluster:true` 的子维度恒为 `false`，但这**不代表**其题被计入基线：簇成员题是**折叠进所属簇、以簇一席**进入基线的。故另给 `baseline_contribution` ∈ {`as_subscale_unit`(以子维度一席计入) / `via_cluster`(折叠进簇一席) / `none_standalone_single`(单题/standalone 剔除) / `none_like5`(like5 不入 freq5 基线)} 显式标明贡献路径。

## interest_map

```jsonc
{
  "person_like5_mean": 4.0,
  "domains": [ {"item_id":"INT-02","domain":"艺术/绘画手工","like5_raw":5,
                "raw_band":{"level":"高",...},"within_int_relative":1.0,
                "label":"最被吸引（一玩就停不下来）","rank":1}, ... ]   // 8 条，rank 1-8
}
```

INT A 层 8 领域（like5）**单独**做个体内兴趣热度排序，**不与行为分混算**；`within_int_relative` 仅在 INT like5 内部中心化。

## interest_quality[]

INT B 层品质信号并入相应簇（focus_persistence/initiative/mastery），给“偏好成色”定性读出（高=已超越一时新鲜、值得继续提供机会）。

## relative_strengths_top[] / growth_areas_top

- `relative_strengths_top[]`：相对突出的 section/cluster（rel≥0，最多 5），各带 `raw_band`、`within_child_relative`、`relative_label`、`protected_high`。
- `growth_areas_top`：
  - `items[]`：个体内相对靠后**且原始 band 非“高”**者（最多 3），每条带 `note:"个体内相对靠后；非劣势、非诊断……"`。
  - `protected_high_relative_low[]`：**原始为高但相对偏低**的项——**T-11 防护**：绝不进 `items`，仅在此列出并标 `"原始水平高（经常/几乎总是），相对没那么突出但仍很常见，不列为待发展"`。
  - `t11_guard`：防护规则声明。

## red_flags[]

保守软转介，**非诊断**。触发条件（同时满足）：某 DEV 发展领域**原始作答长期停最低档(=1「几乎从不」)** 且 `familiarity_low=false` 且 `recent_disruption=false` 且 `confidence≠low`。
每条：`type`(`soft_referral`/`open_ended_gentle_guide`)、`area`、`basis`、`non_diagnostic:true`、`wording`(温和模板，**绝不含诊断词**)、`red_lines_respected`。`soft_referral` **不并入孩子优势分**。

## reverse_applied[] / notes[]

- `reverse_applied[]`：本次翻转的 14 道反向题（`item_id`/`scale`/`raw_value`/`oriented`，`oriented = 6 − raw_value`）。
- `notes[]`：报告级固定声明 + 条件提示（月龄越界回退、低置信弱化措辞）。

---

## 测试

`skill/tests/test_scoring.py`（25 例，纯 `unittest`）覆盖：簇合并只产 1 指标、单题不进基线/不排序、**T-11 全高分防护**、反向翻转、like5/freq5 分基线、缺字段/越界/越龄段稳健、红旗触发与抑制。

```bash
python -m unittest skill.tests.test_scoring -v
```
