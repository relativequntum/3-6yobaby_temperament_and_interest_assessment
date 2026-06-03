# 循证活动库（activity_bank）说明

> 配套「3–6 岁幼儿发展优势与兴趣画像测评」的**循证活动库**。由分析 skill 按孩子的**个体内（ipsative）画像**——哪些构念/能力/兴趣相对突出、哪些相对还在发展中——检索、裁剪后，输出「游戏 / 锻炼 / 家庭陪伴」三条建议线。
>
> 机读主文件：`activity-bank.json`（version 1.1.0，对齐 `item-bank.json` v1.1.2 / `scoring-config.json` v1.0.0）
> 数据来源：`docs/research/activities/A1–A8`（8 份循证简报）

---

## 1. 定位与铁律（务必前置）

- **非诊断、非训练处方、个体内相对比较**。活动是「顺势养育 / 创造练习机会」的家庭建议，不承诺改变测评分数、不做能力达标判定、不出人群百分位、不贴「落后 / 缺陷 / 天赋」标签。对相对待发展的维度一律用「还在发展中 / 可以多创造机会」的措辞。
- **不编造效果声明**。每条活动的 `evidence` 区分两档（见 §5），依据弱者如实标注「一般性发展原理」，不把通行实践包装成研究结论。
- **goodness-of-fit（气质契合）贯穿**。每条含 `temperament_fit_notes`（Thomas-Chess 匹配度 + Rothbart 三因子），对高活跃 / 慢热 / 高负性情绪等给不同调整——配合气质给机会，而非纠正气质。
- **安全优先**。每条含 `safety_notes`；凡涉及小零件、攀高、水边、刀火、屏幕等均给看护要点。红旗 / 软转介逻辑不在本库，由 `scoring-config.json` 的 `red_flags` 处理。

---

## 2. 文件结构（`activity-bank.json`）

```
{
  version, generated_for{ instrument, item_bank_version, date, purpose, sources[], rules[],
                          total_activities, coverage_self_check, note_v110 },
  targets_index{ ... 见 §3 ... },
  activities: [ { id, name, type[], domain, targets[], age_bands[],
                  materials, steps[], difficulty_ladder{easier,harder},
                  temperament_fit_notes, evidence{strength,basis}, safety_notes,
                  source_card | merged_from[] } ]
}
```

活动字段说明：

| 字段 | 含义 |
|---|---|
| `id` | `ACT-<域>-<序>`，域：GM 大运动 / FM 精细动作 / LANG 语言 / COG 认知STEM / SEL 社会情绪 / ATL 学习品质 / INT 兴趣领域 / FAM 家庭陪伴养育 |
| `type` | `game` / `exercise` / `companionship`（可多选，对应三条建议线） |
| `domain` | 活动主域（多用 `SECTION:report_subscale` 或 `INT-构念` 标注） |
| `targets` | **命中键**：与 item-bank 真实构念/能力对齐（见 §3），分析 skill 用画像里的相对突出/待发展键来检索 |
| `age_bands` | `3-4` / `4-5` / `5-6`，仅推 `age_bands` 含该孩子段位的活动 |
| `difficulty_ladder` | `easier` / `harder` 各一句，按掌握动机「中等难度最优」原则裁剪 |
| `temperament_fit_notes` | 按气质画像（高活跃/慢热/高负性情绪等）的 goodness-of-fit 调整 |
| `evidence` | `{strength: "有据"\|"一般性发展原理", basis: ...}` |
| `source_card` / `merged_from` | 溯源到简报卡片；`merged_from` 表示跨简报去重合并（见 §6） |

---

## 3. targets 与 item-bank 构念的对应（`targets_index`）

**targets 只用 item-bank / scoring-config 真实存在的键，不臆造。** 合法键四类：

1. **section id**：`TMP` `SEL` `DEV` `INT` `LRN` `FAM`（粗粒度命中整节）。
2. **cluster key（5 个同义簇）**：`resilience`（挫折恢复/情绪调节）、`focus_persistence`（专注-坚持）、`inhibitory_control`（抑制控制）、`initiative`（主动性）、`mastery`（掌握取向）。这些是 scoring-config 中**跨节合并、只计基线一次**的共享方差指标——活动命中簇键即服务于该簇下的全部成员题。
3. **`SECTION:report_subscale` 形式**：如 `DEV:大运动`、`DEV:精细动作`、`DEV:沟通/语言`、`DEV:问题解决/认知`、`DEV:个人-社会/自理`、`SEL:情绪调节`、`SEL:行为与冲动控制`、`SEL:依恋与关系`、`SEL:共情与亲社会`、`SEL:主动性与自主`、`TMP:活动水平`、`TMP:害羞/慢热`、`TMP:社交接近`、`TMP:趋避/适应`、`TMP:冒险/高强度愉悦`、`TMP:可安抚性`、`TMP:挫折/愤怒反应`、`TMP:恐惧/谨慎`、`TMP:注意聚焦/坚持`、`TMP:抑制控制`、`LRN:专注与坚持`、`LRN:好奇与探索`、`LRN:主动性与自我驱动`、`LRN:创造与灵活`、`LRN:掌握愉悦与挑战取向`、`LRN:面对挫折的恢复`、`FAM:养育方式·要求性`、`FAM:养育方式·回应性`、`FAM:家庭学习环境`、`FAM:屏幕与媒体使用`、`FAM:作息与睡眠`、`FAM:语言环境`、`FAM:照看结构与支持网络`。**冒号右侧字串与 item-bank `report_subscale` 逐字一致。**
4. **INT 构念代码（兴趣画像）**：8 个活动领域 `INT-MOV / INT-ART / INT-MUS / INT-LAN / INT-LOG / INT-NAT / INT-CON / INT-SOC` + 4 个兴趣品质信号 `INT-INT`（沉浸）/ `INT-PER`（持续）/ `INT-SELF`（自主）/ `INT-MAS`（掌握）。INT 一律用构念代码命中，不用 `INT:report_subscale` 形式（与既有 24 条 A1 活动一致）。

> **简报旧键 → item-bank 真实键的换算**见 `targets_index.crosswalk_brief_to_item_bank`。例：简报里的 `DEV-GM` → `DEV:大运动`；`LRN-A` → `LRN:专注与坚持`（cluster `focus_persistence`）；`EF-INH` → `inhibitory_control`；`SEL-A..E` → `SEL` 各 report_subscale。**工作记忆/认知灵活（EF-WM/EF-SHIFT）不单列诊断键，归入 `DEV:问题解决/认知` 与 `LRN:创造与灵活` 的行为表现。**

`targets_index` 内含可被命中的完整清单：`sections` / `clusters`（含成员题）/ `TMP_report_subscales` / `TMP_constructs` / `SEL_report_subscales` / `DEV_report_subscales` / `DEV_constructs` / `INT_report_subscales` / `INT_constructs` / `LRN_report_subscales` / `FAM_report_subscales`，以及 `crosswalk_brief_to_item_bank` 与 `coverage_note`。

---

## 4. 分析 skill 如何检索与裁剪

1. **按画像选条**：读 scoring 输出的个体内相对位 → 对**相对突出**的构念/兴趣领域，选以其为主 `targets` 的活动并用 `difficulty_ladder.harder` 顺势拔高；对**相对待发展**的，选同 `targets` 活动并从 `easier` 起步、措辞用「多创造机会」。
2. **按簇折叠**：画像里相对突出/待发展的是某个**簇**（如 focus_persistence）时，直接用簇键检索；报告对每簇只写一条叙述（与 scoring-config 的「每簇只占基线一席」一致），不要把簇拆成多条独立优势。
3. **按气质裁剪**：读 TMP 画像（高活跃 / 慢热 / 高负性情绪等）→ 套用对应 `temperament_fit_notes`，**优先匹配而非纠正气质**。
4. **按年龄启用**：仅推 `age_bands` 含该孩子段位的活动。
5. **三条建议线**：按 `type` 分别取 `game`（游戏）/ `exercise`（锻炼）/ `companionship`（陪伴）各若干，给家长成套建议。`ACT-FAM-*` 与 `ACT-ATL-*` 中的家长策略类（过程表扬、忍住手、情绪教练、视觉日程、权威型话术）可作为**贯穿底色**附加在任何推荐之上。
6. **兴趣两层**：INT A 层 8 领域（横向偏好）用 `INT-MOV…INT-SOC` 命中「顺势放大特长」的领域活动；B 层 4 品质信号用 `INT-INT/PER/SELF/MAS` 命中「保护心流 / 自主发起 / 掌握愉悦」类活动；二者不混合。

---

## 5. 证据强度约定（`evidence.strength`）

| 档 | 含义 | 用法 |
|---|---|---|
| **有据** | 可追溯到同行评审研究 / 元分析 / 权威机构指南（WHO、AAP、CDC）/ 国家课程框架（教育部《3–6 岁指南》）。`basis` 给出依据与方向。 | 可在面向家长文案中说明「有研究/指南支持」，但仍按原文的诚实力度（如「小到中等效应、需持续」）表述，不夸大为「包学会 / 变聪明 / 提分」。 |
| **一般性发展原理** | 仅有发展学共识 / OT 等专业实践通行做法 / 框架建议支撑，**无针对该具体玩法的 RCT**。 | 只说「有发展依据、合理而安全」，**不得**包装成「有研究证明的效果」。 |

诚实边界要点（已贯穿各条 `basis`）：
- **相关 ≠ 因果**：精细动作—学业、运动—执行功能、屏幕—结果等均为相关/预测证据，不作「练 X 就提 Y」的因果承诺。
- **感统**：前庭/本体觉游戏（转圈、秋千、推拉负重）一律按「促进平衡机能/身体觉知的一般身体游戏」推荐，**不向普通发展儿童宣称「感统训练疗效」**。
- **争议点谨慎措辞**：成长型思维过程表扬（效应量有争议、Gunderson 原文未测学业成就）、假装游戏→创造力（Lillard 等指出部分声称被夸大）、Tools of the Mind（RCT 证据不一致）、延迟满足长期预测力（有争议，仅取「策略可教+环境可信」机制）、多元智能（缺实证效度，领域≠智能）——均已在 `basis` 中保留限定。
- 简报参考表中标 🟡（细节待核）/ ⚪（原理）的条目，正式发布前应回到一手文献复核作者/卷期/数值。

---

## 6. 去重合并约定（`merged_from`）

许多经典活动在多份简报重复出现（如「红灯绿灯」见于 A1/A4/A5/A6/A8）。本库**合并为单条**、用 `merged_from` 记录来源卡片，避免重复下发。主要合并簇：

- **红灯绿灯/木头人** → `ACT-GM-007`（A1-07, A4-01, A5-05, A6-22, A8-11, A7-MOV-01 红灯停部分）
- **对话式共读 PEER** → `ACT-LANG-001`（A3-01, A6-20, A7-LAN-01, A8-05）
- **积木/磁力片搭建** → `ACT-COG-011`（A2-09, A4-12, A6-06 专注, A7-CON-01/02）
- **拼图** → `ACT-COG-009`（A2-20, A4-10, A6-05 拼图阶梯）
- **freeze/音乐停定格** → `ACT-COG-002`（A4-03, A5-09 定格, A6-22 冻住）
- **记忆翻牌** → `ACT-COG-005`（A4-06, A5-07）；**线性数字棋** → `ACT-COG-006`（A4-07, A7-LOG-02）
- **社会扮演/开商店看医生** → `ACT-SEL-016`（A5-19, A6-13, A7-PRE-02）；**过家家含计划** → `ACT-COG-018`（A4-19, A7-PRE-01）
- **特别时光** → `ACT-SEL-019`（A5-22, A8-04）；**平静角** → `ACT-SEL-009`（A5-12, A8-03）；**情绪脸谱** → `ACT-SEL-001`（A5-01, A8-02）
- **情绪教练/先共情后讲理** → `ACT-FAM-001`（A8-01, A8-14）；**先后约定/视觉流程** → `ACT-SEL-007`（A5-10, A6-07, A8-09 转换预告）
- **过程表扬/忍住手** → `ACT-ATL-014`/`ACT-ATL-016`（A6-17/19, A8-16）；**慢热靠近** → `ACT-FAM-006`+`ACT-SEL-022`（A8-12/15, A7-SOC-01）
- 开放美工、合作任务、轮流、自然探索、数数分类、听口令、每日叙事等同理合并。

共 31 条为合并条目；其余为单一来源 `source_card`。另有 5 条**桥接活动**（`ACT-INT-009/010`、`ACT-SEL-022`、`ACT-GM-025`、`ACT-FAM-012`）专为补齐 INT-MAS/INT-CON/INT-SELF、TMP 社交接近·趋避适应·冒险高强度愉悦、FAM 家庭学习环境等覆盖缺口而设。

---

## 7. 覆盖度自检（`generated_for.coverage_self_check`）

- **活动总数**：151（v1.0.0 仅 A1 大运动 24 条 → v1.1.0 补齐 A2–A8 全部专题）。
- **五大 section 全覆盖**：气质(TMP) / 社会情绪(SEL) / 发展(DEV) / 兴趣(INT) / 学习品质(LRN)，外加家庭养育(FAM)。每个 section 的**全部 report_subscale 至少被一条活动直接命中**。
- **5 组同义簇全覆盖**：resilience / focus_persistence / inhibitory_control / initiative / mastery 各 ≥11 条。
- **兴趣 8 领域 + 4 品质信号全覆盖**：INT-MOV…INT-SOC 与 INT-INT/PER/SELF/MAS 均 ≥2 条。
- **三条建议线 × 年龄段无空洞**：game / exercise / companionship 在每个 section 家族 × 3 个年龄段（3-4/4-5/5-6）均 ≥1 条（`domain_x_age_x_type_holes` 为空）。FAM 以 companionship 为主、辅以 game/exercise（符合「家长怎么做」的定位）。
- **气质 goodness-of-fit**：每条 `temperament_fit_notes` 均覆盖高活跃/慢热/高负性情绪等调整。

---

*免责再申明：本活动库为家庭层面的游戏/陪伴建议，非干预/治疗/诊断/训练课程，不承诺改变测评分数。活动以孩子兴趣与愉悦为先、以安全为前提。若家长对孩子某方面发展有持续担忧，请咨询儿科 / 妇幼保健 / 相关专业人员。*
