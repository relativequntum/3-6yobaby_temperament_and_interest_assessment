# 循证活动库 A8：家庭陪伴与养育策略（goodness-of-fit）

> 专题：基于 Baumrind 权威型 + Maccoby-Martin「回应×要求」二维，给**不同气质**（高活跃 / 慢热退缩 / 高负性情绪 / 低努力控制）与**不同家庭情境**（屏幕 / 睡眠 / 隔代 / 二胎）的高质量陪伴与引导话术；含亲子共玩、家庭惯例、情绪教练（emotion coaching）。
> 用途定位：本库由分析 skill 按孩子的**个体内画像**（TMP/SEL/LRN/FAM 各子维度的相对高低）挑选并裁剪，输出「游戏 / 锻炼 / 家庭陪伴」建议。本库属 **companionship（陪伴/养育策略）** 类，与 A1~A7 活动类（精细/大动作/语言/认知等）互补——A8 多为「家长怎么做、怎么说」，而非「孩子做什么任务」。
> 铁律（与全项目一致）：**非诊断、不贴标签、个体内相对比较、不报百分位**；严禁编造效果声明——每条写清「练什么（对应构念/能力）」与「依据」，依据弱者标注「一般性发展原理」而非伪造研究。
> 编制日期：2026-06-03 ｜ 文献核实状态见文末参考列表逐条标注。

---

## 0. 本专题的发展依据（简述）

### 0.1 为什么把「养育策略」做成可推荐的活动
本工具测的是孩子的**气质风格**与**学习/社会情绪优势**，但气质本身不是「好/坏」——决定发展结果的是**匹配度（goodness-of-fit）**：当环境的要求、期待与机会与孩子的气质相协调时，行为困难更少、优势更易发挥（Thomas & Chess 的 NYLS 传统；McClowry et al., 2008 的当代再阐释）。这正是把「针对这种气质，家长可以怎么做」做成可推荐内容的理论依据：A8 的每一条都是**为某种气质画像或家庭情境量身的「环境侧调整」**。

### 0.2 两个总框架
1. **Baumrind 权威型 + Maccoby-Martin 二维**：把养育拆成**回应性（responsiveness/温暖敏感）× 要求性（demandingness/结构规则）**。两者皆高 = 权威型（authoritative），与广泛的良好发展结果相关联（Baumrind, 1991；Maccoby & Martin, 1983）。本库所有话术都在**「高回应 + 适度清晰要求」**这一象限内设计。
   - **中国语境修正（务必）**：Chao（1994）指出华人以「管 / 教训（guan / chiao shun）」表达关爱与投入，「高要求」在华人家庭不等于「专制负面」。因此本库**不把高要求负面化**，而是把「温和而坚定地守住规则」与「先共情、再讲理」并列呈现，避免文化误读。
2. **情绪教练（Emotion Coaching，Gottman 元情绪传统）**：家长把孩子的情绪视为「联结与教导的时机」，做五步——①察觉孩子的情绪→②视情绪为亲近与教导机会→③共情地倾听与确认（validate）→④帮孩子给情绪命名→⑤在守住界限的同时一起想办法。多项研究将情绪教练取向与**更好的情绪调节、更少的内化/外化问题**相关联，且「教家长做情绪教练」在亲子干预中可行有效（Gottman et al., 1996/1997；近期回顾与早期母子序列研究，2024）。注意：多为**相关与小样本干预证据**，本库据此给「怎么说」的脚手架，不承诺疗效。

### 0.3 四种气质的「匹配」要点（贯穿全库）
| 气质画像（本工具 TMP 子维度高分） | 易出现的「不匹配」 | goodness-of-fit 调整方向 |
|---|---|---|
| **高活跃**（A1 活动水平高 / A3 高强度愉悦） | 被要求久坐、放电出口不足 → 冲突、被批评多 | 先给足身体活动出口，再要求安坐；把规则做成「动起来的规则」；多用正向关注 |
| **慢热退缩**（A2 害羞高 / NYLS 趋避偏退缩） | 被催促、被代劳、被贴「胆小」标签 → 退缩固化 | 预告+渐进暴露+**温和鼓励靠近**（不是只安慰躲避）；给适应时间，不强推 |
| **高负性情绪**（B1 挫折/愤怒 高 / B2 恐惧 高 / 可安抚性低） | 情绪被否定/被惩罚 → 升级、对立 | 情绪教练（先共情命名、再守界限）；可预测的惯例降低唤起 |
| **低努力控制**（C1 专注-坚持 低 / C2 抑制控制 低） | 期待超龄、负面纠正多 → 习得性放弃 | 拆小步、脚手架、过程表扬；用游戏练「等待/停」；环境减少诱惑 |

> 提醒：以上是**风格-策略的对应启发**，不是诊断分型；同一个孩子常跨多格，分析 skill 应按其**个体内最突出的 1~2 个维度**裁剪，并叠加 FAM 家庭情境。

---

## 1. 字段说明

每条活动含：`name` / `type` / `domain` / `targets`（对应本工具构念/能力）/ `age_bands`（3-4 / 4-5 / 5-6 适用哪些）/ `materials` / `steps` / `difficulty_ladder`（更易 · 更难）/ `temperament_fit_notes` / `evidence` / `safety_notes`。
- `targets` 对应键示例：努力控制·专注-坚持（C1）、努力控制·抑制控制（C2）、外向性·活动水平（A1）、社交接近-害羞（A2）、负性情绪·挫折（B1）、负性情绪·恐惧（B2）、情绪调节（SEL）、亲社会/共情（SEL）、回应性 FAM-B、要求性/结构 FAM-A、屏幕媒体 FAM-D、睡眠作息 FAM-E、照看结构 FAM-G。
- `evidence` 强度分级：**[研究]**＝有同行评审实证/权威机构指南支撑；**[原理]**＝一般性发展原理或专家共识，无直接因果证据。

---

## 2. 候选活动（共 22 条）

### 模块一：情绪教练与情绪调节（emotion coaching）

#### A8-01　情绪教练五步法（家庭通用脚本）
- **type**: companionship
- **domain**: 社会情绪 / 养育策略
- **targets**: 情绪调节（SEL）、负性情绪·挫折/恐惧的支持（B1/B2）、回应性 FAM-B
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 无
- **steps**:
  1. 蹲到孩子视线高度，先停下手里的事（先连接，后纠正）。
  2. 给情绪命名并确认：「你现在很生气，因为积木倒了，对不对？」
  3. 不否定、不急着讲道理，先让情绪被听见（「难过是可以的」）。
  4. 守住界限同时给出路：「生气可以，但不能打人。我们可以跺脚 / 抱一下 / 一起再搭。」
  5. 平静后简短复盘一句：「下次倒了我们可以怎么办？」
- **difficulty_ladder**: 更易（3-4）：只做「命名+确认+抱一下」三步；更难（5-6）：让孩子自己说出感受词与一个应对办法。
- **temperament_fit_notes**: 高负性情绪：第 3 步停留更久，等唤起下降再进第 4 步；慢热/恐惧型：命名「紧张」并陪伴，不催；高活跃/低 EC：给身体性出路（跺脚、捏球）比讲道理有效。
- **evidence**: [研究] 情绪教练取向与更好的儿童情绪调节、更少内化/外化问题相关，且可教可学（Gottman et al., 1996/1997；2024 系统回顾/序列研究）。`EMO-COACH`
- **safety_notes**: 「守界限」指温和而坚定，非体罚；孩子攻击他人时先安全隔离再共情。

#### A8-02　情绪脸谱与「情绪天气」每日小聊
- **type**: companionship / game
- **domain**: 社会情绪
- **targets**: 情绪知识与表达（SEL-Denham）、情绪调节、语言
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 自画 4~6 张表情卡（开心/生气/难过/害怕），或绘本
- **steps**:
  1. 每天固定一刻（如晚饭后）问：「今天你的心情像什么天气？」
  2. 用表情卡或天气比喻让孩子选一个并说说为什么。
  3. 家长也说自己的一种情绪做示范（「我今天有点累，像阴天」）。
  4. 读绘本时顺带指认角色情绪。
- **difficulty_ladder**: 更易：只指认开心/难过两种；更难：区分「生气」与「失望」「紧张」等细分情绪。
- **temperament_fit_notes**: 慢热/内向：用画/比喻代替开口更省力；高负性情绪：先练「平静时谈情绪」，避免只在崩溃时才提。
- **evidence**: [研究] 学前情绪知识（识别/理解情绪）预测同伴接纳与入学社会胜任（Denham et al., 2003）。`Denh`
- **safety_notes**: 无特别风险；不强迫孩子表态。

#### A8-03　「冷静角」与平静工具箱（共建）
- **type**: companionship / exercise
- **domain**: 社会情绪 / 自我调节
- **targets**: 情绪调节（SEL）、抑制控制（C2）、负性情绪可安抚性
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 角落坐垫、毛绒玩具、可捏的软球、绘本
- **steps**:
  1. 和孩子一起布置一个「不是惩罚、是帮自己平静」的小角落。
  2. 平静时教 2~3 个降温法：吹蜡烛式深呼吸、抱玩具、捏球。
  3. 情绪上来时温和邀请（不命令）：「要不要去你的平静角？我陪你。」
  4. 平静后回到原情境。
- **difficulty_ladder**: 更易：家长全程陪同；更难：孩子能自己识别「我需要冷静一下」并主动使用。
- **temperament_fit_notes**: 高活跃/高负性情绪最受益；务必**与惩罚区分**，否则失效；恐惧型不单独留置，需陪伴。
- **evidence**: [原理] 自我调节支持策略（前置情境调整、注意转移、呼吸）符合 Gross 情绪调节过程模型与情绪教练「守界限+给出路」逻辑；具体「冷静角」工具为实务共识，作一般性原理处理。`ThompER`/`EMO-COACH`
- **safety_notes**: 角落须在成人视线内、无小物件吞咽风险。

### 模块二：亲子共玩与高质量陪伴

#### A8-04　每日 15 分钟「孩子做主」特别时光（child-directed special time）
- **type**: companionship / game
- **domain**: 亲子关系 / 社会情绪
- **targets**: 回应性 FAM-B、依恋/关系（SEL-Attachment）、掌握动机·自主（LRN）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 孩子自选的玩具
- **steps**:
  1. 每天固定 10~15 分钟，全程不看手机。
  2. 让孩子决定玩什么、怎么玩；家长跟随、描述、不指挥不纠错（PRIDE 式：描述、模仿、具体表扬、享受）。
  3. 给这段时间起名「我们的特别时光」，强化其仪式感。
- **difficulty_ladder**: 更易：先从 5 分钟、单一玩具开始；更难：把「孩子主导」延伸到家务小协作中。
- **temperament_fit_notes**: 慢热/内向孩子在一对一里更易打开；高活跃孩子可选动态游戏；二胎家庭给每个孩子**单独**的特别时光（见 A8-19）。
- **evidence**: [研究] 家长「跟随式/儿童主导」游戏与积极陪伴和较少行为问题相关（亲子游戏系统综述 2022）；父母「玩兴（playfulness）」与更好的幼儿情绪调节、更低负性相关（2024 研究综述）；行为亲子训练（Incredible Years/Triple P）以「专属正向关注」为核心成分并降低行为问题。`PLAY-REV`/`PCIT-IY`
- **safety_notes**: 选择适龄、安全玩具；避免把特别时光当作交换条件。

#### A8-05　亲子共读「对话式阅读」（dialogic reading）
- **type**: companionship / game
- **domain**: 语言 / 亲子关系
- **targets**: 语言（DEV）、专注-坚持（C1）、好奇心（LRN）、回应性 FAM-B、家庭学习环境 FAM-C
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 适龄绘本
- **steps**:
  1. 不只是念，而是多提开放问题（「你猜接下来会怎样？」）。
  2. 跟着孩子的兴趣点停留、扩展他的话（孩子说「狗」→「对，一只毛茸茸的大狗在跑」）。
  3. 表扬具体内容，让孩子轮流「讲」给你听。
- **difficulty_ladder**: 更易（3-4）：指图命名、翻页；更难（5-6）：讨论因果、预测结局、联系生活。
- **temperament_fit_notes**: 高活跃：选互动/翻翻书、缩短单次时长；慢热：从孩子熟悉的书开始降低门槛。
- **evidence**: [研究] 家庭语言输入量/质量（含共读、藏书、亲子言语）是 SES 影响早期词汇的关键中介（Hoff, 2003）；共读是 HOME 学习环境核心刺激项（Bradley & Caldwell, 1979）。`HOFF2003`/`HOME1979`
- **safety_notes**: 无。

#### A8-06　家庭「修理/做饭」真实任务共做
- **type**: companionship / exercise
- **domain**: 生活自理 / 学习品质
- **targets**: 专注-坚持（C1）、掌握动机（LRN）、精细/大动作、亲社会（帮忙）
- **age_bands**: 4-5 / 5-6（3-4 仅做最简步骤）
- **materials**: 家务真实材料（洗菜、择菜、拧螺丝玩具工具、叠衣）
- **steps**:
  1. 选一个孩子能参与的真实小任务，拆成他能完成的 1~2 步。
  2. 让他真正「负责」一小块，完成后描述他的努力（过程表扬）。
  3. 不替他做完，卡住时给提示而非答案（脚手架）。
- **difficulty_ladder**: 更易：只交一步（如把择好的菜放碗里）；更难：负责一道简单菜的完整小流程。
- **temperament_fit_notes**: 低 EC：步骤更短、即时肯定；高活跃：选需要动手走动的任务；慢热：先旁观再上手。
- **evidence**: [研究] 自主支持式脚手架（在孩子能力略上方给恰当协助、给选择而非施压）促进幼儿自我调节（自主支持实验研究）；过程表扬与「努力/策略」反馈支持掌握动机与坚持（praise balance 研究；Gunderson et al., 2013）。`SCAFFOLD`/`Mindset`
- **safety_notes**: 刀具/灶火/工具全程成人在旁；只交安全步骤。

### 模块三：家庭惯例与生活结构（routines）

#### A8-07　可预测的睡前惯例「四步固定流程」
- **type**: companionship
- **domain**: 作息健康 / 自我调节
- **targets**: 睡眠作息 FAM-E、情绪调节（SEL）、要求性/结构 FAM-A
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 无（可用流程图卡）
- **steps**:
  1. 固定 3~4 个步骤同序进行：洗漱→换睡衣→共读一本→关灯抱一下。
  2. 每天同一时间、同一顺序，越规律越好。
  3. 睡前 1 小时不看屏幕、调暗灯光。
- **difficulty_ladder**: 更易：先固定「读书+关灯」两步；更难：让孩子自己看流程图执行各步。
- **temperament_fit_notes**: 高负性情绪/慢热：可预测性显著降低入睡焦虑；高活跃：睡前提前留出放电时间，惯例中安排「由动到静」的过渡。
- **evidence**: [研究] 一致的睡前惯例与更好睡眠呈**剂量依赖**关系、并与更少行为问题相关（Mindell et al., 2015，n=10,085，跨 13 地区）；早期一致睡前惯例与 3 岁更好的情绪调节相关（2025）。`Mindell2015`/`BedtimeRoutine`
- **safety_notes**: 睡眠环境安全（无窒息风险物品）。

#### A8-08　屏幕时间「共看+约定+缓冲」三件套
- **type**: companionship
- **domain**: 媒体使用 / 亲子互动
- **targets**: 屏幕媒体 FAM-D、情绪调节（关屏过渡）、抑制控制（C2）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 计时器
- **steps**:
  1. **约定**：一起定「看什么、多久、什么时候」，用计时器而非家长口头喊停。
  2. **共看**：尽量陪看并就内容聊几句（把被动观看变互动）。
  3. **缓冲**：结束前 2 分钟预告（「还有 2 分钟」），结束后安排一个有吸引力的线下活动接住注意。
- **difficulty_ladder**: 更易：先固定「计时器+预告」；更难：让孩子参与制定家庭媒体规则并自我监督。
- **temperament_fit_notes**: 低 EC/高负性情绪：关屏冲突最大，**预告+缓冲活动**比讲道理有效；高活跃：关屏后直接转向身体活动。
- **evidence**: [研究] AAP 强调 2-5 岁高质量节目≤1 小时，**共看、内容质量、沟通**比单纯时长更预测良好结果；WHO 2019 久坐屏幕≤1 小时、越少越好。`AAP2016MEDIA`/`WHO2019`
- **safety_notes**: 睡前 1 小时避免屏幕（影响入睡，见 A8-07）。

#### A8-09　家庭「视觉日程表」与转换预告
- **type**: companionship / game
- **domain**: 自我调节 / 生活结构
- **targets**: 要求性/结构 FAM-A、抑制控制·转换（C2）、情绪调节
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 几张图卡/磁贴表示日常环节
- **steps**:
  1. 把一天关键环节做成图卡，按顺序贴在孩子看得到处。
  2. 每个转换前用图卡预告：「玩完这个，下面是吃饭。」
  3. 完成一项让孩子翻牌/摘下，给掌控感。
- **difficulty_ladder**: 更易：只做「现在—接下来」两格；更难：孩子自己排次日日程。
- **temperament_fit_notes**: 慢热/高负性情绪：预告减少「被突然打断」的对抗；低 EC：可视结构补足内部计划能力。
- **evidence**: [原理] 可预测的结构与转换预告是权威型「高要求」的温和实现方式（Baumrind, 1991；Maccoby & Martin, 1983）；与睡前/惯例证据一致，但「视觉日程表」具体形式作一般性原理。`BAUMRIND1991`/`MACCOBY1983`
- **safety_notes**: 无。

### 模块四：高活跃 / 爱冒险气质（A1 活动水平、A3 高强度愉悦高）

#### A8-10　每日「放电」身体活动优先（先动后静）
- **type**: exercise / companionship
- **domain**: 大动作 / 自我调节
- **targets**: 外向性·活动水平（A1）、专注-坚持（C1，间接）、睡眠（FAM-E，间接）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 户外/室内空间，球、跳绳等
- **steps**:
  1. 每天保证充足身体活动（WHO：3-4 岁全天各类活动≥180 分钟）。
  2. 在需要孩子安坐的活动（吃饭、共读）**之前**安排活动出口。
  3. 把「跑跳」做成有规则的游戏（见 A8-11），既放电又练规则。
- **difficulty_ladder**: 更易：客厅障碍跑；更难：有目标的运动（投篮计数、跳格子）。
- **temperament_fit_notes**: 高活跃是**优势**（运动潜力、精力）——叙事用「精力充沛」而非「坐不住」；不要用「罚站/久坐」对待高活跃孩子。
- **evidence**: [研究] WHO 2019：3-4 岁每天≥180 分钟身体活动；身体活动是该年龄段健康指南核心。`WHO2019`
- **safety_notes**: 场地无尖角、地面防滑；攀爬有人看护。

#### A8-11　规则性大动作游戏：红灯停绿灯行 / 木头人
- **type**: game / exercise
- **domain**: 自我调节 / 大动作
- **targets**: 抑制控制（C2）、活动水平的建设性出口（A1）
- **age_bands**: 3-4（简化）/ 4-5 / 5-6
- **materials**: 无
- **steps**:
  1. 「绿灯」跑、「红灯」立刻停住；停得住就赢。
  2. 逐渐加规则（「红灯」单脚站、加「黄灯」慢走）。
  3. 轮流当指挥，练等待与轮流。
- **difficulty_ladder**: 更易（3-4）：只玩「停 1~2 秒」；更难（5-6）：多指令切换（红停/黄慢/蓝倒退）。
- **temperament_fit_notes**: 高活跃孩子最受益——把「停下」练成游戏而非禁令；低 EC 从最短停顿起步、多鼓励。
- **evidence**: [研究] 抑制控制（抑制优势反应）在 3-6 岁快速发展，是核心执行功能之一（Diamond, 2013；Kochanska et al., 2000）；「红灯绿灯」类游戏是经典抑制控制练习。`Diam`/`Koch`
- **safety_notes**: 急停在防滑平地，避免追逐碰撞。

### 模块五：慢热退缩气质（A2 害羞高 / 趋避偏退缩）

#### A8-12　「预告+渐进暴露」融入新环境
- **type**: companionship
- **domain**: 社会情绪 / 适应
- **targets**: 社交接近-害羞（A2）、负性情绪·恐惧（B2）、回应性 FAM-B
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 无
- **steps**:
  1. 去新场合前先讲会发生什么、有谁（预告降低不确定）。
  2. 给孩子「观察期」，允许先在旁边看，不催「快去玩」。
  3. **温和鼓励靠近**（「我们一起走过去看看那个滑梯好吗」），而不是只安慰其退缩。
  4. 孩子迈出一步就具体肯定靠近行为。
- **difficulty_ladder**: 更易：家长全程陪同、目标只是「待在那里」；更难：孩子独立加入一个小活动。
- **temperament_fit_notes**: 关键区分：**表扬「靠近」，而非强化「黏人/回避」**；不贴「胆小」标签；给时间但不替他回避。
- **evidence**: [研究] 对害羞/抑制型幼儿，**温和鼓励靠近**（而非过度保护或只安慰回避）可促进其社交调节、降低后续焦虑风险；过度保护反而强化退缩与焦虑（gentle encouragement 研究 2019；抑制气质×养育系统综述 2024）。`SHY-ENCOURAGE`
- **safety_notes**: 渐进、尊重孩子节奏，绝不强推或嘲笑。

#### A8-13　角色扮演「预演」社交脚本
- **type**: game / companionship
- **domain**: 社会情绪 / 语言
- **targets**: 社交接近（A2）、亲社会（SEL）、语言、自我效能
- **age_bands**: 4-5 / 5-6（3-4 用玩偶简化）
- **materials**: 玩偶/家庭成员扮演
- **steps**:
  1. 在家用玩偶预演「怎么加入小朋友」：先看、再问「我可以一起玩吗」。
  2. 家长先示范，再换孩子当主角。
  3. 把成功的句子变成他的「口袋话」备用。
- **difficulty_ladder**: 更易：只练打招呼一句；更难：演「被拒绝了怎么办」的备选方案。
- **temperament_fit_notes**: 慢热孩子在低风险的家中预演能降低真实场景焦虑；不强求当场表演给外人看。
- **evidence**: [原理] 社交脚本预演/示范符合社会学习与「鼓励靠近」干预思路（见 A8-12 证据）；具体玩偶预演形式作一般性发展原理。`SHY-ENCOURAGE`
- **safety_notes**: 无。

### 模块六：高负性情绪气质（B1 挫折/愤怒、B2 恐惧高，可安抚性低）

#### A8-14　「先共情后讲理」的冲突降温脚本
- **type**: companionship
- **domain**: 社会情绪 / 养育策略
- **targets**: 情绪调节（SEL）、负性情绪·挫折（B1）、回应性 FAM-B + 要求性 FAM-A 的平衡
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 无
- **steps**:
  1. 孩子发脾气时，先降低自己的音量与姿态（家长先稳）。
  2. 共情命名 + 确认（A8-01 第 2~3 步），等唤起下降。
  3. 平静后温和而坚定地重申界限与选择（「打人不行，你可以选 A 或 B」）。
- **difficulty_ladder**: 更易：只做「先稳住自己+命名情绪」；更难：引导孩子自己提出解决办法。
- **temperament_fit_notes**: 高负性情绪孩子升温快、降温慢——**别在高峰期讲道理**；可安抚性低者需更长等待与更可预测的回应。
- **evidence**: [研究] 情绪教练（共情、确认、再引导）与更好情绪调节、更少外化问题相关（见 A8-01）；权威型「高回应+清晰要求」与良好适应相关（Baumrind, 1991）。`EMO-COACH`/`BAUMRIND1991`
- **safety_notes**: 高峰期先保证人身安全（防自伤/伤人），再处理情绪。

#### A8-15　恐惧/担心的「勇敢小步」陪伴
- **type**: companionship
- **domain**: 社会情绪
- **targets**: 负性情绪·恐惧（B2）、情绪调节、自我效能
- **age_bands**: 4-5 / 5-6（3-4 以陪伴安抚为主）
- **materials**: 无
- **steps**:
  1. 承认害怕真实存在（不嘲笑、不否定「这有什么好怕的」）。
  2. 把害怕的事拆成很小的台阶，一次只前进一小步。
  3. 每完成一小步具体肯定其「勇敢」（表扬靠近行为，不强化回避）。
- **difficulty_ladder**: 更易：家长陪着完成；更难：孩子自己完成并说出「我做到了」。
- **temperament_fit_notes**: 恐惧型最忌「过度保护」与「硬推」两个极端，走中间的渐进鼓励路线（同 A8-12）。
- **evidence**: [研究] 渐进暴露 + 鼓励靠近、避免过度保护，与抑制/恐惧型儿童更好调节、更低焦虑相关（见 A8-12）。`SHY-ENCOURAGE`
- **safety_notes**: 渐进、尊重节奏；涉及真实危险的恐惧（如车流）应保留合理警觉，不脱敏。

### 模块七：低努力控制（C1 专注-坚持、C2 抑制控制相对低）

#### A8-16　「拆小步 + 过程表扬」练坚持
- **type**: companionship / game
- **domain**: 学习品质 / 自我调节
- **targets**: 专注-坚持（C1）、掌握动机（LRN）、成长型思维前体
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 拼图、积木等有完成感的材料
- **steps**:
  1. 把任务拆成孩子「跳一跳够得着」的小步。
  2. 卡住时给提示而非代劳（脚手架）。
  3. 表扬**努力与策略**（「你试了好几种方法」），而非只夸「你真聪明」。
- **difficulty_ladder**: 更易：步骤极短、即时肯定；更难：让孩子先说计划再执行。
- **temperament_fit_notes**: 低 EC 孩子需要把成功体验前置，避免长期受挫导致放弃；高负性情绪者卡住易崩，提示要更早。
- **evidence**: [研究] 过程表扬（努力/策略）预测更适应的动机框架（Gunderson et al., 2013）；自主支持脚手架促进自我调节（自主支持实验）；过程与个人表扬的平衡预测坚持与掌握愉悦（praise balance 研究）。`Mindset`/`SCAFFOLD`
- **safety_notes**: 无。

#### A8-17　「等一等」延迟与轮流小游戏
- **type**: game / companionship
- **domain**: 自我调节
- **targets**: 抑制控制（C2）、延迟满足、亲社会·轮流
- **age_bands**: 3-4（几秒）/ 4-5 / 5-6
- **materials**: 计时器、桌游、零食（可选）
- **steps**:
  1. 玩需要轮流的小游戏，用「轮到你了」明确等待结束。
  2. 把「等待」游戏化：「我们一起数到 10 再拆礼物。」
  3. 逐步延长可等待时间，等成功就肯定。
- **difficulty_ladder**: 更易（3-4）：等几秒；更难（5-6）：为更大奖励延迟（类「棉花糖」情境）。
- **temperament_fit_notes**: 低 EC 从极短等待起步、频繁成功体验；高活跃可加入身体动作帮等待（「等的时候我们拍手」）。
- **evidence**: [研究] 抑制控制/延迟满足是 3-6 岁快速发展的核心 EC（Diamond, 2013；Kochanska et al., 2000）；轮流游戏是其自然练习场。`Diam`/`Koch`
- **safety_notes**: 不把等待变成挫败惩罚；零食等待量小、防噎。

#### A8-18　减少诱惑的「环境前置调整」
- **type**: companionship
- **domain**: 自我调节 / 家庭环境
- **targets**: 抑制控制（C2，环境支持）、要求性/结构 FAM-A
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 收纳盒/分区
- **steps**:
  1. 做需要专注的事时，先收走无关玩具/关掉背景电视（减少分心源）。
  2. 把诱惑物放到看不见处（情境调整优于事后管教）。
  3. 给专注区一个固定的「干活角」。
- **difficulty_ladder**: 更易：家长替孩子整理环境；更难：孩子自己学会「开始前先收走分心的东西」。
- **temperament_fit_notes**: 低 EC/高活跃孩子的自控更依赖外部环境支持，这是合理且有效的「外部脚手架」，不是溺爱。
- **evidence**: [原理] 「情境调整 / 注意分配」是 Gross 情绪调节过程模型中的前因聚焦策略，迁移到注意管理为一般性原理；背景电视干扰幼儿专注亦有媒体研究支持。`ThompER`/`AAP2016MEDIA`
- **safety_notes**: 无。

### 模块八：家庭情境（隔代 / 二胎 / 多照看人一致性）

#### A8-19　二胎家庭：每个孩子的「专属特别时光」
- **type**: companionship
- **domain**: 亲子关系 / 社会情绪
- **targets**: 依恋/关系（SEL）、情绪调节、照看结构 FAM-G
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 无
- **steps**:
  1. 给老大每天固定一段**只属于他**的一对一时光（哪怕 10 分钟）。
  2. 接纳并命名其复杂情绪：「弟弟来了，你有时高兴、有时也有点失落，这都正常。」
  3. 邀请（不强迫）参与照顾婴儿的小任务，建立「我是哥哥/姐姐」的胜任感。
- **difficulty_ladder**: 更易：固定一段一对一；更难：让老大主导一个和弟妹一起玩的小活动。
- **temperament_fit_notes**: 高负性情绪/慢热的老大过渡期反应更明显，需更多可预测的专属关注；切忌拿两娃比较。
- **evidence**: [研究] 多数老大在弟妹出生后**适应良好、个体差异大**（攻击行为仅短期上升后回落），并非普遍长期紊乱（Volling, 2017，Monographs SRCD）；「专属一对一时光+接纳情绪+参与照顾」是常见循证实践建议（家长教育资源）。`Volling2017`
- **safety_notes**: 让幼儿「帮忙照顾婴儿」须全程成人监督。

#### A8-20　隔代/多照看人：家庭规则「对齐三件事」
- **type**: companionship
- **domain**: 养育协同 / 家庭环境
- **targets**: 共养一致性 FAM-G、要求性/结构 FAM-A、情绪调节（间接）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 一张写下家庭核心规则的小纸/家庭群
- **steps**:
  1. 父母与祖辈先就**最重要的 3 条**（如睡觉时间、屏幕规则、安全底线）达成一致。
  2. 不在孩子面前互相否定；分歧私下沟通。
  3. 把一致的规则用孩子能懂的话告诉他，各照看人口径统一。
- **difficulty_ladder**: 更易：先统一 1 条（如睡前流程）；更难：建立每周简短「带娃沟通」。
- **temperament_fit_notes**: 低 EC/高负性情绪孩子对「规则不一致」尤其敏感（钻空子或焦虑），一致性收益最大。
- **evidence**: [研究] 良好的代际共养（祖辈参与+共养一致）与儿童社会能力、执行功能、依恋安全正相关（Xu et al., 2024 系统综述）；规则一致性是结构性养育的一般要素。`XU2024`/`MACCOBY1983`
- **safety_notes**: 沟通对事不对人，避免在孩子面前的家庭冲突。

#### A8-21　隔代养育：把祖辈的优势变成「专属陪伴项目」
- **type**: companionship / game
- **domain**: 亲子/祖辈关系 / 兴趣
- **targets**: 照看结构 FAM-G、回应性 FAM-B、兴趣领域（按孩子画像）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 因项目而定（如包饺子、种花、唱老歌、讲家史）
- **steps**:
  1. 找一件祖辈擅长且孩子可参与的活动，做成「和爷爷/奶奶才做的事」。
  2. 鼓励祖辈用「描述+提问」的对话式陪伴（同 A8-04/05 思路）。
  3. 让孩子的兴趣画像引导项目选择（爱动手→手工烹饪；爱故事→家族故事）。
- **difficulty_ladder**: 更易：一个固定小活动；更难：祖孙合作完成一个小作品/小种植。
- **temperament_fit_notes**: 慢热孩子常在熟悉的祖辈面前更放松，是练社交与语言的低压力场；尊重祖辈节奏，不强加方法。
- **evidence**: [原理] 利用祖辈优势的专属陪伴呼应代际共养的积极面（Xu et al., 2024）与「跟随兴趣的高回应陪伴」（HOME 回应性/Hoff 输入质量）；具体项目形式作一般性原理。`XU2024`/`HOME1979`
- **safety_notes**: 烹饪/种植涉及刀火/小物件须监护。

#### A8-22　全家「权威型」自检与温和坚定话术卡
- **type**: companionship
- **domain**: 养育策略（元层面）
- **targets**: 回应性 FAM-B × 要求性 FAM-A 的平衡（权威型）
- **age_bands**: 3-4 / 4-5 / 5-6
- **materials**: 一张话术卡
- **steps**:
  1. 自检两问：今天我**回应**了孩子的情绪吗？我**清晰且一致**地守住了重要规则吗？
  2. 用「温和而坚定」三句式：先共情（「我知道你还想玩」）→ 给界限（「但现在要睡觉了」）→ 给有限选择（「你想先刷牙还是先换睡衣」）。
  3. 避免两个极端：只回应不要求（放任）/ 只要求不回应（严苛）。
- **difficulty_ladder**: 更易：每天只挑一个场景练三句式；更难：全家照看人统一使用同一套话术。
- **temperament_fit_notes**: 对所有气质适用，是裁剪其他条目的「底色」；中国家庭语境下「要求/管」是关爱表达，关键是同时保持高回应（Chao, 1994）。
- **evidence**: [研究] 权威型（高回应+高要求）与广泛良好发展结果相关（Baumrind, 1991；Maccoby & Martin, 1983）；华人「管/教训」语境修正（Chao, 1994）。`BAUMRIND1991`/`MACCOBY1983`/`CHAO1994`
- **safety_notes**: 「坚定」非严厉/体罚；有限选择须都是家长可接受的选项。

---

## 3. 覆盖度自检

- **年龄段**：三段（3-4 / 4-5 / 5-6）全覆盖；多数条目三段通用，A8-06/13/15 等标注更适用 4-5/5-6，3-4 给简化版。
- **type 覆盖**：companionship（全部 22 条主类型）；其中含 game 成分 8 条、exercise 成分 4 条——符合本专题以「陪伴/养育策略」为主、辅以亲子共玩与身体活动的定位。
- **气质覆盖（goodness-of-fit）**：高活跃（10/11）、慢热退缩（12/13）、高负性情绪（14/15）、低努力控制（16/17/18）四类各有专项，外加通用底色（01/22）。
- **家庭情境覆盖**：屏幕（08）、睡眠（07）、隔代/多照看人（20/21）、二胎（19）、结构/转换（09/18）。
- **对应本工具构念**：情绪调节/情绪知识（SEL）、依恋关系（SEL）、亲社会（SEL）、专注-坚持 C1、抑制控制 C2、活动水平 A1、社交-害羞 A2、负性情绪 B1/B2、掌握动机/成长型思维（LRN）、回应性 FAM-B、要求性 FAM-A、屏幕 FAM-D、睡眠 FAM-E、照看结构 FAM-G。

---

## 4. 参考 / 依据列表

> 图例：✅ 已检索并核对关键信息；🟡 经多源印证、未逐字核对全文；[原理] 一般性发展原理，无直接因果证据。复用本项目 `docs/source-legend.md` 已有键者标「（已有键）」，新增键给新缩写并建议正式发布前回原文复核。

**已在本项目题库/source-legend 中、可直接复用的依据：**
1. ✅ `BAUMRIND1991` Baumrind, D. (1991). The influence of parenting style on adolescent competence and substance use. *Journal of Early Adolescence*, 11(1), 56–95.（已有键，权威型/二维基础）
2. 🟡 `MACCOBY1983` Maccoby, E. E., & Martin, J. A. (1983). Socialization in the context of the family. In *Handbook of Child Psychology, Vol. 4* (pp. 1–101). Wiley.（已有键，回应×要求二维）
3. ✅ `CHAO1994` Chao, R. K. (1994). Beyond parental control and authoritarian parenting style. *Child Development*, 65(4), 1111–1119.（已有键，华人「管/教训」修正）
4. ✅ `Denh` Denham, S. A., et al. (2003). Preschool emotional competence. *Child Development*, 74(1), 238–256.（已有键，A8-02）
5. ✅ `ThompER` Thompson, R. A. (1994). Emotion regulation: A theme in search of definition. *Monographs SRCD*, 59(2–3).（已有键，情绪调节过程，A8-03/18）
6. ✅ `Diam` Diamond, A. (2013). Executive functions. *Annual Review of Psychology*, 64, 135–168.（已有键，抑制控制，A8-11/17）
7. ✅ `Koch` Kochanska, G., Murray, K. T., & Harlan, E. T. (2000). Effortful control in early childhood. *Developmental Psychology*, 36(2), 220–232.（已有键，A8-11/17）
8. ✅ `Mindset` Gunderson, E. A., et al. (2013). Parent praise to 1- to 3-year-olds predicts children's motivational frameworks. *Child Development*, 84(5), 1526–1541.（已有键，过程表扬，A8-06/16）
9. ✅ `HOFF2003` Hoff, E. (2003). The specificity of environmental influence. *Child Development*, 74(5), 1368–1378.（已有键，共读/语言输入，A8-05）
10. ✅ `HOME1979` Bradley, R. H., & Caldwell, B. M. (1979). HOME (preschool scale). *Am. J. Mental Deficiency*, 84(3), 235–244.（已有键，回应性/共读/语言刺激，A8-05/21）
11. ✅ `AAP2016MEDIA` AAP Council on Communications and Media (2016). Media and Young Minds. *Pediatrics*, 138(5), e20162591.（已有键，共看/质量，A8-08/18）
12. ✅ `WHO2019` WHO (2019). *Guidelines on physical activity, sedentary behaviour and sleep for children under 5*. Geneva.（已有键，身体活动/屏幕/睡眠，A8-08/10）
13. ✅ `XU2024` Xu, W., Parra, G. R., & Carter, M. K. (2024). Intergenerational coparenting and child development: a systematic review. *J. Family Theory & Review*, 16(4), 834–856.（已有键，隔代共养，A8-20/21）
14. 🟡 `McClowry2008`（source-legend 已列为「方法学背书」键）McClowry, S. G., Rodriguez, E. T., & Koslowitz, R. (2008). Temperament-based intervention: Re-examining goodness of fit. *European Journal of Developmental Science*, 2(1–2), 120–135.（goodness-of-fit 当代再阐释 + INSIGHTS「Recognize-Reframe-Respond」三 R，A8 §0.1）

**本专题新增、本次检索核实的依据（建议正式发布前回原文逐值复核）：**
15. 🟡 `EMO-COACH` 情绪教练 / 元情绪：Gottman, J. M., Katz, L. F., & Hooven, C. (1996/1997). *Meta-Emotion: How Families Communicate Emotionally*；并见近期母子情绪教练序列研究（*Affective Science*, 2024, PMC12209066）与情绪社会化亲子干预 RCT 系统综述/元分析（2023, *J. Behavior Therapy & Exp. Psychiatry* 类）。依据强度：相关与小样本干预为主，**不承诺疗效**。
16. ✅ `Mindell2015` Mindell, J. A., et al. (2015). Bedtime routines for young children: A dose-dependent association with sleep outcomes. *Sleep*, 38(5), 717–722.（n=10,085，跨 13 地区；剂量依赖，A8-07）
17. 🟡 `BedtimeRoutine` 睡前惯例与发展结果回顾：Mindell & Williamson (2018). Benefits of a bedtime routine in young children. *Sleep Medicine Reviews*；及 2025 低收入家庭早期睡前惯例→3 岁情绪调节研究（*Early Childhood Research Quarterly* 类）。A8-07
18. 🟡 `SHY-ENCOURAGE` 害羞/抑制型养育：温和鼓励靠近研究（*Journal of Experimental Child Psychology*, 2019, gentle encouragement promotes shy toddlers' regulation）；抑制气质×养育与焦虑系统综述（2024, PMC11486786）；Fox et al. (2023) Annual Research Review, *JCPP*（行为抑制→焦虑路径，过度保护为风险）。A8-12/13/15
19. 🟡 `SCAFFOLD` 自主支持/脚手架：自主支持对学前自我调节的实验研究（*Journal of Applied Developmental Psychology*, 2018）；scaffolding 动机框架（PMC3827669）。A8-06/16/18
20. 🟡 `PLAY-REV` 亲子游戏与行为问题系统综述（2022, PMC9110017）；父母玩兴与幼儿情绪调节研究综述（2024）。A8-04
21. 🟡 `PCIT-IY` 行为亲子训练「专属正向关注/PRIDE」核心成分：Incredible Years（Webster-Stratton）与 Triple P（Sanders）项目证据综述（含 ADHD 症状/行为问题改善）。A8-04。依据强度：项目层面 RCT 较强，单条「特别时光」为成分级证据。
22. ✅ `Volling2017` Volling, B. L. (2017). Family transitions following the birth of a sibling. *Monographs of the Society for Research in Child Development*, 82(3).（关键修正：多数老大适应良好、个体差异大，攻击行为仅短期上升——**A8-19 据此不夸大「普遍嫉妒紊乱」**）

> 诚实声明：
> - 标 [原理] 的条目（A8-03 冷静角具体形式、A8-09 视觉日程表具体形式、A8-13 玩偶预演、A8-18 注意管理迁移、A8-21 祖辈项目）为一般性发展原理或实务共识，**无直接因果证据**，已在 evidence 字段如实标注。
> - 情绪教练（EMO-COACH）、亲子游戏（PLAY-REV）、行为亲子训练成分（PCIT-IY）多为**相关或项目层面证据**，本库只据此给「怎么做/怎么说」的脚手架，**不对单条活动承诺特定疗效**。
> - 新增键（15~21）多为本次检索的二手/摘要核实，**正式发布前应回原文核对作者全名、卷期页码与具体数值**，并按需登记入 `docs/source-legend.md` 与 `理论依据与方法学.md §9`。

*文件路径：docs/research/activities/A8-companionship-parenting.md*
