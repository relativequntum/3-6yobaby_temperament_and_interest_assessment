# scoring-config.json 说明（计分契约机读化）

本目录把方法学第 4 章的**计分契约**固化为机读配置 `scoring-config.json`，供阶段四计分 skill 直接消费。本文件逐条解释配置项如何对应方法学 `docs/理论依据与方法学.md` §4 与各既定决策。

- **事实源关系**：题级事实以 `docs/item-bank.json`（题库，`item_bank_version` 1.1.1）为准；某次作答的过程数据以导出 JSON（机读事实源 `schema/export.schema.json`，`schema_version` 1.1）为准。本配置**不复制题干文本**，只携带计分所需的题级元数据（section/subscale/report_subscale/cluster/scale/reverse/age_bands/scored/consistency_pair_id），且这些字段逐题对齐题库、由题库机械生成，不臆造规则。
- **本配置不计分**：题库与问卷前端均不计分；计分在 skill 侧依据导出 JSON + 本配置执行（§4 开头约束）。

## 1. 顶层字段

| 字段 | 含义 | 对应方法学 |
|---|---|---|
| `version` | 本配置版本（1.0.0） | — |
| `source_item_bank_version` | 据以生成的题库版本（1.1.1） | §4.8 元数据支撑 |
| `source_export_schema_version` | 消费的导出契约版本（1.1） | json-schema §0 |
| `non_diagnostic_notice` | 非诊断/非筛查/不出百分位总声明 | §4.2、§6.1 |
| `age_bands` | 3-4/4-5/5-6 月龄区间（复制自题库） | §2.2 |
| `items` | 题号→题级计分元数据 | §4.1、§4.6、§4.8 |
| `clusters` | 5 组同义簇及合并规则 | §4.6 |
| `centering` | 个体内中心化作用域与基线剔除清单 | §4.1.3、§4.8 |
| `aggregation` | 默认粒度与单题/子维度处理 | §4.7、§4.3、§4.8 |
| `descriptive_bands` | 均值→高/中/低 的锚点语义描述 | §4.2 |
| `quality_flags` | 质量旗标来源/状态/规则 | §5.1、§5.2 |
| `red_flags` | 软转介触发规则与非诊断措辞 | §4.5 |

## 2. `items`：题级计分元数据（对应 §4.1 / §4.6 / §4.8）

每题携带：`section`、`subscale`（计分聚合用）、`report_subscale`（报告措辞用）、`cluster`（同义簇归属，无则 null）、`scale`（freq5/like5/single/multi）、`reverse`、`age_bands`、`scored`、`consistency_pair_id`。

- **逐题对齐题库**：题号、`reverse`、`scale`、`age_bands` 与 `item-bank.json` 完全一致（已脚本校验 0 处不符）。
- **反向计分（§4.1.1）**：`reverse:true` 的 14 题（TMP-02/04/05/14/17、SEL-03/06/09、INT-11/13、LRN-02/09/11/13）由 skill 先做 `6 − raw_value` 翻转、同向校验通过后再汇总。配置只标记 `reverse`，翻转动作由 skill 执行。
- **`scored`（§4.5 家庭画像独立 / json-schema §2.4）**：TMP/SEL/DEV/INT/LRN=`true`；FAM 13 题=`false`（写入 responses 但不计入孩子画像，仅供建议）。OPEN 3 道开放题为 `text`，归 `open_ended`、不在本 `items` 内。
- **`consistency_pair_id`（§4.1 同向性 / §5.2）**：cp-1=SEL-08↔09、cp-2=INT-10↔11、cp-3=INT-12↔13、cp-4=LRN-01↔02，供 `inconsistency_flag`。

## 3. `clusters`：同义/近义子维度合并（对应 §4.6，B1）

按题库 `cluster` 字段建 5 组同义簇（与 §4.6 对照表逐题一致）：

| 簇 | report_name | 成员（跨 section） |
|---|---|---|
| `focus_persistence` | 专注-坚持 | TMP-13,14,15 + LRN-01,02,03 + INT-09,10,11 |
| `inhibitory_control` | 抑制控制 | TMP-16,17,18 + SEL-04,05,06 |
| `initiative` | 主动性 | SEL-07,08,09 + INT-12,13 + LRN-06,14 |
| `resilience` | 挫折恢复/情绪调节 | TMP-08,09,10 + SEL-01,02,03 + LRN-12,13 |
| `mastery` | 掌握取向 | INT-14,15 + LRN-10,11 |

`merge_rule` = 「合并为单一指标、只计基线一次」。实现要点（写入 `merge_detail`）：(a) 合并 = 簇内全部本龄段启用题（已翻转、同向校验通过）的统一均值，为单一共享方差指标；(b) 该指标在「个人总均值基线」与「相对位排序」中**只占一席**；(c) 报告对每簇**只写一条**叙述，不得拆成 TMP/LRN/INT 多条独立优势；(d) 子维度若仍展示，必须标注「与他维高相关、已合并计基线，仅供定性参考」。这正是 §4.6 防止「同一份共享方差重复计入、放大权重、误报多个独立优势」的契约。

## 4. `centering`：个体内中心化作用域与基线剔除（对应 §4.1.3 / §4.8，B3/B5）

- **作用域 `按量表/按section`（§4.1.3，B3）**：`like5_freq5_separate=true`——`like5`（兴趣领域分）与 `freq5`（行为频率分）各自在「同量表/同 section」内中心化，**禁止把两种语义不同的量表混进同一基线**。个人总均值基线**只由计入画像的 freq5 行为题构成**；INT A 层 like5 领域分只在 INT 内部横向排序、不并入 freq5 基线。
- **`reverse_then_center`**：先翻转、同向校验通过，再参与均分与中心化（§4.1.1→§4.1.3 顺序）。
- **`exclude_from_baseline`（§4.8，B5）**——从个人总均值基线剔除：
  - `int_a_like5_domains`：INT-01..08 八个 like5 活动领域（§4.8 典型例外 + §4.1.3 like5 不入 freq5 基线）。
  - `standalone_single_item_freq5_subscales`：TMP-03（社交接近）、TMP-04（害羞/慢热）、TMP-05（趋避/适应）——三段均为**单题且不归任何簇**的 freq5 子维度，按 §4.8「单题不纳入排序、只作描述、从基线剔除」剔除，避免单题噪声污染中心化基准。
  - `fam_section`、`open_section`：FAM（scored:false）与 OPEN（开放题）不计入孩子画像。
  - `note_in_cluster_singles`：TMP-10/INT-09/INT-14/LRN-06/LRN-12 虽在某些段为单题，但**归属同义簇**，按 §4.6 折叠进对应簇的合并指标（随簇计基线一次），**不**作为 standalone 剔除——这是 §4.8「以『该子维度本段启用题数=1』为判据」与 §4.6 簇合并的交界处理。

## 5. `aggregation`：默认粒度上提到 section（对应 §4.7 / §4.3 / §4.8，B2）

- `default_granularity="section"`（§4.7，B2）：TMP/SEL/INT(B 层)/LRN 各输出**一个**个体内相对位；DEV 按 5 领域在孩子内部排序（§4.3，不判达标/落后、不出百分位、不设切分点）。理由：本工具无本土信效度、子维度可分性证据不足，顶层 section 更稳健。
- `subscale="qualitative_only_with_caveat"`：子维度仅作定性补充，凡展示**强制标注** `subscale_caveat`「题少／子维度间相关高，仅供参考」。
- `single_item="not_ranked"`（§4.8）：单题子维度只作描述性陈述、不纳入个体内排序。
- `int_two_layer`（§4.3）：INT A 层 8 领域横向偏好排序、B 层 4 品质信号判断「成色」，二者不混合求和。

## 6. `descriptive_bands`：锚点语义而非人群百分位（对应 §4.2）

均值→高/中/低 的映射**锚定在量表频率/喜爱档位语义上，不是人群分布**。`freq5`/`like5` 各给 5 档全文字标签与「均值区间→档位 + 频率/喜爱描述短语」。`caution` 重申：阈值仅为人读描述方便，**非人群常模切分**；须配合个体内相对位（相对突出/相对还在发展中）使用，**绝不出现「超过 X% 的孩子」**。这同时满足非诊断定位、规避参照群体效应（Heine 2002）、用途导向效度（《标准》2014）。

## 7. `quality_flags`：标注优先（对应 §5.1 / §5.2）

每个旗标标 `source`/`status`/`rule`，`status` 取值与导出契约 `quality_flag_status` 枚举一致：
- `longstring`、`timing`、`high_missing`：`computed`（计时/作答模式直接推断）。
- `familiarity_low`、`recent_disruption`：`computed_from_contact`（由 `_identity_extra.daily_contact`/关系等身份字段推断；`daily_contact=lt1` 即低熟悉度）。
- `inconsistency`：`computed_in_skill_from_pairs`（用 cp-1..cp-4 翻转后同向比对；覆盖面有限，无专用语义矛盾探针）。
- `sdb_halo`：`reserved`（缺去赞许探针，恒 false、暂不稳健判定；可暂以「全卷高分+维度间方差过低」作低置信弱代理）。

`handling`：依 Ward & Meade 2023「标注优先而非删除」——多旗标→弱化绝对表述、加重免责，对家长温和提示而非指责，不静默删作答。

## 8. `red_flags`：软提示/温和转介（对应 §4.5）

- `philosophy`：非诊断、非筛查、保守（宁可少触发），借鉴 AAP 2020 / CDC LTSAE / ASQ-3 监测区。
- `trigger`：按 **DEV 原始锚点档位**（非个体内相对位）——某发展领域长期停最低档（原始=1「几乎从不」）、且 `familiarity_low=false` 且 `recent_disruption=false` 时，触发一条温和软转介。`soft_referral` 不并入孩子优势分。
- `wording_template` + `red_lines`：固定非评判话术，**绝不**出现诊断词（自闭/发育迟缓/多动）、绝不下结论或制造焦虑、始终以「可以问问专业人士」收尾。
- `open_ended_concern`：OPEN-03 家长自述担忧时温和引导专业评估、不诊断。
- `fam_advisory`：FAM 要求性×回应性养育方式提示、屏幕/睡眠对照 WHO/AAP/AASM 给「绿色/可优化」建议，不并入优势分、不贴「专制/放任」标签（独立于 red_flags 的非诊断建议侧）。

## 9. 一致性保证

`items` 由 `item-bank.json` 机械抽取生成，并经脚本逐题校验：题号集合相等、`reverse`/`scale`/`age_bands`/`subscale`/`report_subscale`/`cluster`/`consistency_pair_id` 0 处不符，`scored` 标记正确（仅 FAM=false），5 组 `clusters` 成员与题库 `cluster` 字段完全一致。题库升版后须重跑生成与校验。
