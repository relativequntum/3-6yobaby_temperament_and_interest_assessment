# 循证活动库 A4｜认知 / 数理逻辑 / 问题解决 / 执行功能

> 面向【中国家长】的【3–6 岁幼儿】「发展优势 + 兴趣画像」**非诊断**测评工具配套活动库
> 用途：由分析 skill 按孩子的**个体内（ipsative）画像**挑选并裁剪，输出「游戏 / 锻炼 / 家庭陪伴」建议
> 专题覆盖：分类排序、数量空间、拼图迷宫、规则类桌游、记忆与抑制控制游戏（"红灯绿灯""西蒙说"等）
> 版本：v1.0 ｜ 编制日期：2026-06-03 ｜ 依据核实状态见文末「参考 / 依据列表」逐条标注

---

## ⚠️ 定位与使用铁律（务必前置）

1. **非诊断、非训练课程**：本活动库是「顺势养育 / 亲子陪伴」建议，不是认知训练疗程，更不用于矫正或诊断。任何"练 EF / 练数学"的表述都指**日常游戏中的自然练习机会**，不承诺测验分数提升。
2. **不编造效果声明**：每条活动的 `evidence` 字段，凡有同行评审 / 权威机构支撑的写明来源 key；仅有发展逻辑支撑的，**明确标注「一般性发展原理」**，绝不伪造研究。
3. **goodness-of-fit（气质契合）优先**：同一活动对高活跃 / 慢热 / 高负性情绪 / 低坚持的孩子要不同地裁剪（见每条 `temperament_fit_notes`），呼应本工具气质模块（专题01）的养育契合理念——不是"纠正气质"，而是"配合气质给机会"。
4. **构念对齐**：`targets` 字段对应本工具既有构念代码：
   - 发展领域（专题03）：`DEV-PS`（问题解决/认知）、`DEV-FM`（精细动作）、`DEV-COM`（语言）、`DEV-PSE`（个人-社会）。
   - 学习品质（专题05）：`LRN-A`（专注与坚持）、`LRN-B`（好奇与探索）、`LRN-C`（主动性）、`LRN-D`（创造与灵活）、`LRN-E`（掌握愉悦/挑战取向）、`LRN-F`（挫折恢复）。
   - 执行功能（在本工具中作为 `DEV-PS` / `LRN-A` / `LRN-D` 的行为表现，不单独诊断）：用 `EF-WM`（工作记忆）、`EF-INH`（抑制控制）、`EF-SHIFT`（认知灵活/转换）标注，仅作能力说明，**不做 EF 缺陷筛查**。
5. **安全第一**：凡含小零件（珠子、棋子、磁片）的活动，3 岁前后仍需警惕误吞；`safety_notes` 逐条标注。

---

## 0. 本域发展依据简述

**为什么"玩"能练认知与执行功能。** Diamond & Lee（2011, *Science*）系统综述指出：计算机训练、非计算机的规则类游戏、有氧运动、武术、瑜伽、正念，以及 Tools of the Mind、蒙台梭利等课程，都被证明可改善 4–12 岁儿童的执行功能；其共同机制是**反复练习 + 持续地把挑战往上调**——并明确指出"难度不增加的对照组不出现 EF 收益"（Diamond & Lee 2011）。这正是本库每条活动都设 `difficulty_ladder`（更易 / 更难各一句）的循证理由：**活动要随孩子变强而变难，才有意义**。

**执行功能三件套是入学准备的生物学基础**（Garon, Bryson & Smith 2008）：工作记忆（记住并操作信息）、抑制控制（憋住冲动、抗干扰）、认知灵活（规则切换）。学前期（约 3–6 岁）这三者持续快速发展，因此是介入的黄金窗口。本库大量"听指令做相反""按规则切换"的游戏，对应的正是抑制与转换——经典测评任务 Head-Toes-Knees-Shoulders（"我说摸头你就摸脚"）即同构于这类游戏，且该任务对学前儿童的学业表现有跨研究的预测效力（Ponitz et al. 2009；HTKS-R: Gonzales et al. 2021；元分析 2023）。

**数理逻辑的几条循证支柱：**
- **数量/数感**——线性数字棋盘游戏（类似"飞行棋/蛇梯棋"底排的 1→10 线性走格）经随机对照证明能提升低收入学前儿童的数字大小比较、数线估计、数数与数字识别，效果可维持约 9 周；**且"线性"优于"圆形"棋盘、数字格优于纯颜色格**（Ramani & Siegler 2008；Siegler & Ramani 2009；Laski & Siegler 2014）。这是"陪孩子玩棋盘走格、边走边数"建议的直接依据。
- **空间/几何**——积木搭建与拼图与同期及后续数学能力相关；空间能力可塑，早期积木/拼图经验能改变空间思维；积木游戏的随机对照试验显示对数学与执行功能的促进（Verdine et al. 2014；Casey et al. 2008；Schmitt et al. 2018 RCT；Hanline et al. / 2024 RCT）。家长**空间语言输入**（大小、形状、方位词：高、圆、边、旁边）越丰富，孩子日后空间能力越好（Pruden, Levine & Huttenlocher 2011；Verdine 等）。
- **分类 / 排序 / 模式（patterning）**——分类、序列与模式是早期数学的逻辑前体；学前模式能力可独立于一般认知、空间、工作记忆、语言，预测当期与后续的数学知识（Zippert et al. 2020；Nguyen 等综述传统）。这是"分类游戏、找规律接龙"建议的依据。

**与气质模块的接口（goodness-of-fit）：** 同样一套认知游戏，高活跃儿童需要把"坐着拼"改成"动着找"；慢热儿童需要更长预热、先旁观再上手；高负性情绪 / 低挫折恢复儿童需要把难度拆得更细、多用过程表扬（表扬努力与策略而非聪明，呼应专题05 的成长型思维前体）。**这不是降低标准，而是让挑战落在每个孩子"够得着"的区间**——与掌握动机"中等难度最优"的定义一致（专题05）。

---

## 活动卡片字段说明

每条活动含：`name` / `type`（game·exercise·companionship 可多选）/ `domain` / `targets`（本工具构念代码）/ `age_bands`（3-4 / 4-5 / 5-6 适用哪些）/ `materials` / `steps` / `difficulty_ladder`（更易·更难）/ `temperament_fit_notes` / `evidence`（来源 key 或"一般性发展原理"）/ `safety_notes`。
> 来源 key 见文末参考列表。`type` 中 companionship 指"以亲子关系/共同投入为主、认知练习为辅"的陪伴式玩法。

---

# 第一组：抑制控制 / 注意与规则游戏（红灯绿灯·西蒙说一类）

## A4-01 红灯绿灯（中国版"一二三木头人"）
- **name**：红灯绿灯 / 一二三木头人
- **type**：game, exercise
- **domain**：执行功能·大运动
- **targets**：`EF-INH`（抑制控制）、`LRN-A`（专注与坚持）、`DEV-PSE`（守规则）、`DEV-GM`（大运动）
- **age_bands**：3-4 / 4-5 / 5-6
- **materials**：无；一片能跑动的空地（客厅/小区空地/公园）
- **steps**：
  1. 大人当"灯"，背对孩子喊"绿灯"——孩子可以往前走/跑。
  2. 喊"红灯"并转身——孩子必须立刻定住不动。
  3. 谁红灯时还动就退回起点；先摸到大人者赢，可交换当"灯"。
- **difficulty_ladder**：更易——只用"红/绿"两口令、动作慢、红灯停的时间短；更难——加"黄灯=慢动作"第三规则、口令变快、或改成"说红才停、说绿才走"的相反规则（增量挑战，符合 Diamond & Lee 的难度递增原则）。
- **temperament_fit_notes**：高活跃儿童最爱、也最需要——先从短回合开始，把"定住"做成有趣的雕塑造型而非压制；慢热儿童让其先当"灯"或旁观一两轮再加入；高负性情绪/低挫折恢复儿童淡化输赢、退回起点说成"再来一次的机会"，多夸"你刚才停得真稳"。
- **evidence**："停—走"对反应抑制的练习有同行评审支撑：此类"听信号憋住动作"的游戏与 HTKS 自我调节任务同构，后者经元分析预测学业表现（Ponitz2009 / HTKS-R / Meta2023）；Diamond&Lee2011 把规则类动作游戏列为可改善 EF 的活动。
- **safety_notes**：场地清空障碍与尖角；急停急转防滑倒，室内穿防滑袜或光脚；人多时划定边界防碰撞。

## A4-02 西蒙说 / "队长说"
- **name**：西蒙说（可本土化为"队长说""老师说"）
- **type**：game
- **domain**：执行功能·语言
- **targets**：`EF-INH`、`EF-WM`、`LRN-A`、`DEV-COM`（听指令）
- **age_bands**：3-4（简化）/ 4-5 / 5-6
- **materials**：无
- **steps**：
  1. 大人发指令："西蒙说，摸鼻子"——孩子要照做。
  2. 若指令前**没有**"西蒙说"（如直接说"摸鼻子"），孩子要**忍住不做**。
  3. 做错的人不淘汰，只是笑一笑继续（非淘汰制更护情绪）。
- **difficulty_ladder**：更易——动作慢、"西蒙说"出现频率高、只用身体大动作；更难——加快节奏、混入"陷阱指令"更多、或叠加"做相反"（说摸头要摸脚）。
- **temperament_fit_notes**：低坚持/易分心儿童每轮 5–8 个指令即可，常赢一下保持动机；高活跃儿童用全身大动作版消耗精力；慢热儿童先由其发指令当"西蒙"建立掌控感。
- **evidence**：抑制控制 + 工作记忆（要记住"有没有西蒙说"这条规则并据此抑制）；与 HTKS"按规则抑制优势反应"同机制（HTKS-R / Ponitz2009）；Harvard Center on the Developing Child EF 活动指南将此类游戏列为 3–5 岁 EF 练习（Harvard CDC EF Activities）。
- **safety_notes**：避免要求危险动作（如闭眼转圈、爬高）；指令保持安全可控。

## A4-03 音乐停—定住（Freeze Dance）
- **name**：音乐停就定住（跳舞定格）
- **type**：game, exercise
- **domain**：执行功能·大运动·音乐
- **targets**：`EF-INH`、`LRN-A`、`DEV-GM`、（兴趣）音乐律动
- **age_bands**：3-4 / 4-5 / 5-6
- **materials**：手机/音箱放音乐
- **steps**：
  1. 音乐响时尽情跳舞，音乐一停立刻定住像雕塑。
  2. 谁还动谁就来当"暂停音乐的人"（轮流主导）。
  3. 进阶：音乐停时不仅定住，还要摆出指定主题造型（"小动物""一棵树"）。
- **difficulty_ladder**：更易——停顿前给预告、定格时间短；更难——加"慢速音乐要慢动作、快速音乐要快动作"的速度切换（练认知灵活 `EF-SHIFT`）。
- **temperament_fit_notes**：高活跃 / 高负性情绪儿童尤其适合——把躁动转化为合法的"动—静"切换，定住后的平静本身是情绪调节练习；慢热儿童允许小幅度动作起步。
- **evidence**：经典"freeze game"是 Harvard CDC 与多项 EF 游戏方案中的抑制控制活动（Harvard CDC EF Activities；Bodrova/Halperin 系活动综述 SpringerECE2024）。
- **safety_notes**：清空场地；定格造型不鼓励单脚长时间硬撑以免摔倒。

## A4-04 反着做 / 相反游戏（"我说摸头你摸脚"）
- **name**：相反指令游戏（Opposite Game）
- **type**：game
- **domain**：执行功能
- **targets**：`EF-INH`、`EF-SHIFT`、`EF-WM`、`LRN-D`（灵活）
- **age_bands**：4-5 / 5-6（3-4 段仅用一对最简单相反）
- **materials**：无
- **steps**：
  1. 约定一对相反规则："我说摸头，你就摸脚；我说摸脚，你就摸头"。
  2. 大人随机出口令，孩子做相反动作。
  3. 熟练后增加第二对（"我说大声你就小声、我说快你就慢"）。
- **difficulty_ladder**：更易——只一对相反、节奏慢；更难——两对规则交叉（这正是 HTKS-R 的"四指令"结构），或中途宣布"现在规则换回来"练 `EF-SHIFT`。
- **temperament_fit_notes**：低坚持儿童从一对开始、回合短；高负性情绪儿童把"做错"演成滑稽桥段，避免挫败；5–6 岁高能力儿童可挑战四指令版获得掌握愉悦（`LRN-E`）。
- **evidence**：直接对应 Head-Toes-Knees-Shoulders 自我调节任务的游戏化形式，HTKS 需同时调用工作记忆、抑制与认知灵活，并预测学业表现（Ponitz et al. 2009；HTKS-R Gonzales et al. 2021；元分析 Frontiers 2023）。
- **safety_notes**：纯口令动作，低风险；避免相反规则导致危险动作。

## A4-05 我的小熊去散步（记忆—抑制混合的"叠叠口令"）
- **name**：叠加口令记忆游戏（"小熊先拍手，再跺脚……"）
- **type**：game, companionship
- **domain**：执行功能·语言
- **targets**：`EF-WM`、`LRN-A`、`DEV-COM`
- **age_bands**：4-5 / 5-6
- **materials**：无（可用玩偶当"主角"增加趣味）
- **steps**：
  1. 第一人说一个动作："小熊先拍手。"
  2. 下一人要先重复前面的、再加一个："小熊先拍手，再跺脚。"
  3. 依次叠加，谁漏了或顺序错了就重开新一轮（不羞辱）。
- **difficulty_ladder**：更易——2–3 个动作封顶、可用图卡提示；更难——延长到 5–6 步、或加"倒着复述"。
- **temperament_fit_notes**：工作记忆负荷大，低坚持/易挫折儿童封顶 3 步并多给"差一点点，再来"；慢热儿童先听大人和家人玩一轮再上。
- **evidence**：工作记忆的容量与序列保持练习；属一般性发展原理叠加 Harvard CDC"记忆类游戏练工作记忆"的方案思路（Harvard CDC EF Activities）。
- **safety_notes**：纯语言游戏，无风险。

---

# 第二组：记忆与配对 / 桌游类（规则类桌游·记忆翻牌）

## A4-06 记忆翻牌配对（Memory / 翻翻乐）
- **name**：记忆翻牌配对
- **type**：game, companionship
- **domain**：执行功能·认知
- **targets**：`EF-WM`、`LRN-A`、`DEV-PS`、`DEV-PSE`（轮流）
- **age_bands**：3-4（4–6 对）/ 4-5（6–8 对）/ 5-6（8–12 对）
- **materials**：成对的图卡（可用旧扑克、自制贴纸卡、或两副相同图案的卡片）
- **steps**：
  1. 所有卡片图案朝下打乱铺开。
  2. 轮流每次翻两张，图案相同就收走并再翻一次，不同就翻回原位。
  3. 记住翻过的位置，配对多者"赢"（弱化竞争，重在一起找）。
- **difficulty_ladder**：更易——减少对数、用差异大的图案；更难——增加对数、用相似图案（如不同颜色的同一动物）逼迫更精细的工作记忆。
- **temperament_fit_notes**：低坚持儿童用 4 对起步、回合快；高活跃儿童可把卡片铺在地上"翻完跑去拿"加动作；高负性情绪儿童采取"合作模式"——全家一起翻、目标是清空全桌而非比谁多。
- **evidence**：视觉空间工作记忆的经典练习；Harvard CDC 将配对/记忆类卡牌游戏列为学前工作记忆活动（Harvard CDC EF Activities）；属循证活动框架内常见项。
- **safety_notes**：卡片边缘防割手；3 岁幼儿防把小卡片放入口中。

## A4-07 数字走格棋（线性数字棋盘 / 蛇梯棋底排）
- **name**：线性数字走格棋（自制"1→10/20"跑道）
- **type**：game, companionship
- **domain**：数理逻辑·认知
- **targets**：`DEV-PS`（数感）、数量与数序、`LRN-A`、`DEV-PSE`（轮流）
- **age_bands**：3-4（1→10）/ 4-5（1→20）/ 5-6（1→20 加简单加减）
- **materials**：自制一条横排格子跑道（纸上画 10–20 个并排方格、标 1…10/20）、一个骰子（或写 1–2 的转盘）、小棋子
- **steps**：
  1. 掷骰子，走对应步数，**每走一格大声念出落在哪个数**（"6、7、8！"），而非只念骰子点数。
  2. 谁先走到终点谁完成（重在过程，不强调输赢）。
  3. 5–6 岁可加"踩到带星的格子前进 2 格"等小规则。
- **difficulty_ladder**：更易——跑道短到 1→10、每次走 1 格、大人陪念；更难——延长到 1→20、用两颗骰子相加决定步数（顺带练加法）、或倒着从 20 走回 1。
- **temperament_fit_notes**：低坚持儿童用 1→10 短跑道、一局两三分钟；高活跃儿童把"跑道"画在地上用身体当棋子走；慢热儿童先看大人走一轮。**关键**：务必走"线性横排"且念出落点数字——研究显示线性优于圆形、数字格优于纯颜色格。
- **evidence**：随机对照证据较强——Ramani & Siegler 2008 / Siegler & Ramani 2009：玩线性数字棋盘约 1 小时提升数字大小比较、数线估计、数数、数字识别，且维持约 9 周；线性优于圆形（Ramani&Siegler2008）；"念出落点数字"的编码方式更有效（Laski & Siegler 2014）。
- **safety_notes**：骰子/棋子为小零件，3 岁前后防误吞；地面版注意走动安全。

## A4-08 规则类儿童桌游（Uno 初阶 / 颜色形状配对桌游 / 鼹鼠井字等）
- **name**：简单规则桌游（颜色—形状匹配、轮流出牌类）
- **type**：game, companionship
- **domain**：执行功能·认知·社会
- **targets**：`EF-INH`（等轮次、忍住不抢）、`EF-SHIFT`（按颜色/数字切换匹配）、`DEV-PSE`（轮流守规）、`LRN-F`（输了能恢复）
- **age_bands**：4-5（极简规则）/ 5-6（含 Uno 初阶、井字棋）
- **materials**：一副适龄桌游或自制颜色/数字配对卡
- **steps**：
  1. 讲清一两条核心规则（如"出的牌要和上一张同色或同数字"）。
  2. 轮流出牌/落子，强调"轮到谁、要等"。
  3. 一局结束复盘一句"这局你怎么想到那样走的"。
- **difficulty_ladder**：更易——去掉特殊牌只保留"同色/同数字接龙"；更难——加入特殊牌（反转、跳过）或引入需要预判对手的井字棋。
- **temperament_fit_notes**：**高负性情绪/低挫折恢复儿童是重点照顾对象**——先玩"合作型"或"无输赢"桌游，赢输话术改为"这局我运气好/下局看你的"；高活跃儿童选回合短、节奏快的；慢热儿童先两人玩、熟了再多人。
- **evidence**：规则类桌游练抑制（等轮次）、转换（按变化的匹配维度切换）与社会守规；Diamond&Lee2011 将规则类游戏列为 EF 促进活动；"玩桌游频繁的孩子空间/数学相关测试更好"（puzzles/blocks/board games 频率研究 Levine/PsychSci）。输赢情境也是挫折恢复（`LRN-F`，专题05）的天然练习场。
- **safety_notes**：小牌/小棋子防误吞；竞争情绪管理见 temperament 注。

## A4-09 找不同 / 视觉搜索
- **name**：找不同·视觉搜索（"图里几只猫？""哪里不一样？"）
- **type**：game, companionship
- **domain**：认知·注意
- **targets**：`LRN-A`（持续注意）、`DEV-PS`、`EF-INH`（抗干扰）
- **age_bands**：3-4（找一样东西）/ 4-5 / 5-6（两图找 5 处不同）
- **materials**：找不同绘本/打印图、或随手用两幅相似实景（摆好两盘略不同的水果）
- **steps**：
  1. 给出目标（"找出图里所有红色的东西""两张图哪里不一样"）。
  2. 孩子逐一指出，大人确认并数数。
  3. 进阶让孩子出题考大人（角色反转，强化主动性 `LRN-C`）。
- **difficulty_ladder**：更易——目标少且明显、画面简单；更难——目标多/不同点细微、加时间小挑战。
- **temperament_fit_notes**：适合慢热/安静型孩子的强项展示场；高活跃儿童改成"满屋找 X"的走动版；低坚持儿童每张图只设 2–3 个目标。
- **evidence**：持续性注意与视觉搜索练习；一般性发展原理（持续注意在 3–5 岁大幅提升，专题05 §3 综合 Garon2008）。
- **safety_notes**：实景版注意所选物品安全、无尖锐。

---

# 第三组：拼图 / 迷宫 / 空间搭建

## A4-10 拼图（Jigsaw Puzzle）
- **name**：拼图
- **type**：game, companionship
- **domain**：空间·精细动作·问题解决
- **targets**：空间能力、`DEV-PS`、`DEV-FM`、`LRN-A`、`LRN-F`（卡住不放弃）
- **age_bands**：3-4（4–12 片大块）/ 4-5（12–24 片）/ 5-6（24–60 片）
- **materials**：适龄拼图（木质大块/纸板均可）
- **steps**：
  1. 先看完整图样，鼓励"先找四个角和边"。
  2. 按颜色/形状分堆，再逐块试拼。
  3. 卡住时引导用空间语言提示（"这块的直边应该靠外""转一下看看"）。
- **difficulty_ladder**：更易——减少块数/选带底图轮廓的；更难——增加块数、去掉参考图、或限时。
- **temperament_fit_notes**：**高负性情绪/低挫折恢复儿童**从远低于其能力的块数起步，确保"做成"的掌握愉悦（`LRN-E`），卡住先共情再拆小步；高活跃儿童分段完成、允许中途起身；慢热儿童陪拼前几块"破冰"。
- **evidence**：拼图游戏与空间技能、数学相关，且空间能力可塑（puzzle play 2–4 岁可改变空间思维：Levine/PsychSci；Verdine2014 空间-数学关联）；卡住—再试是挫折恢复与坚持的练习。
- **safety_notes**：小块拼图防 3 岁幼儿误吞；木质拼图防边角。

## A4-11 走迷宫
- **name**：走迷宫（纸面/地面）
- **type**：game, exercise
- **domain**：空间·问题解决·精细动作
- **targets**：空间规划、`DEV-PS`、`EF-INH`（不越线）、`DEV-FM`（笔控）、`LRN-A`
- **age_bands**：3-4（超简单宽路）/ 4-5 / 5-6（多岔路）
- **materials**：迷宫打印页 + 笔；或用胶带在地上贴出"大迷宫"用身体走
- **steps**：
  1. 纸面版：用手指先走一遍找通路，再用笔画线不出界。
  2. 走错回头试别的岔路（练"此路不通就换路"= 灵活）。
  3. 地面版：身体沿胶带路线走/爬到终点。
- **difficulty_ladder**：更易——路宽、岔路少、可用手指；更难——岔路多、死胡同多、必须用笔不出界。
- **temperament_fit_notes**：高活跃儿童首选**地面身体迷宫**消耗精力又练规划；低坚持儿童用短迷宫、走通即大力表扬；慢热儿童先手指走熟再上笔。
- **evidence**：空间规划与视觉-动作协调；"先想再走"含抑制成分。一般性发展原理 + 空间技能可塑文献（Levine/PsychSci）。
- **safety_notes**：地面版地胶防滑、清空障碍；笔尖朝向安全。

## A4-12 积木/磁力片搭建（照图搭 + 自由搭）
- **name**：积木与磁力片搭建
- **type**：game, exercise, companionship
- **domain**：空间·问题解决·精细动作·创造
- **targets**：空间能力、`DEV-PS`、`DEV-FM`、`LRN-D`（创造）、`LRN-A`、（数学）几何/数量
- **age_bands**：3-4 / 4-5 / 5-6
- **materials**：木积木 / 乐高大颗粒 / 磁力片等任意一种
- **steps**：
  1. **照图搭**：给一张简单结构图或样品，让孩子照搭（练空间对应）。
  2. **自由搭**：给主题（"搭一座能过车的桥""最高的塔"）让其自由创造。
  3. 搭时多用空间语言旁白："你把长的放在**下面**当**底**，短的放**上面**。"
- **difficulty_ladder**：更易——少量大块、照简单图；更难——增加块数、照更复杂图、或给约束条件（"只用 10 块搭最高"）。
- **temperament_fit_notes**：高活跃儿童给大空间和大颗粒、允许推倒重来（推倒也是因果探索）；高负性情绪儿童在"塔倒了"时示范"倒了没关系，我们看看怎么搭更稳"（成长型思维前体，`LRN-F`）；慢热儿童先模仿大人搭。
- **evidence**：积木搭建与空间、数学、执行功能相关并有 RCT 证据（Schmitt et al. 2018 半结构化积木 RCT；2024 低收入样本 RCT；Verdine2014 空间装配-数学；Casey2008）；**家长空间语言旁白**提升空间能力（Pruden, Levine & Huttenlocher 2011）。
- **safety_notes**：大颗粒优先防误吞；磁力片注意磁珠类产品的吞咽危险（选正规大片磁力片，避免小磁珠）；搭高防倒塌砸到。

## A4-13 七巧板 / 形状拼摆
- **name**：七巧板与几何形状拼摆
- **type**：game, companionship
- **domain**：空间·几何·精细动作
- **targets**：空间旋转/组合、几何概念、`DEV-PS`、`DEV-FM`、`LRN-D`
- **age_bands**：4-5（照轮廓拼）/ 5-6（自由造型/无轮廓）
- **materials**：七巧板（木/泡棉/纸自制均可）
- **steps**：
  1. 给一个目标轮廓（鱼、房子、帆船），让孩子用七块拼满。
  2. 引导命名形状与方位（"把**三角形**转一下，**尖角**朝上"）。
  3. 进阶让孩子自创造型并命名。
- **difficulty_ladder**：更易——给带内部分割线的轮廓（明示每块位置）；更难——只给外轮廓、或完全自由创作。
- **temperament_fit_notes**：慢热/安静型的优势舞台；高活跃儿童设"限时拼一个"的小挑战增加投入；低坚持儿童从 2–3 块的简单图形起步。
- **evidence**：空间旋转与组合、几何概念；空间技能可塑文献（Levine/PsychSci）+ 几何形状/拼图促进入学准备（Verdine2014 "Finding the missing piece"传统）。
- **safety_notes**：小块防误吞；木片防边角。

---

# 第四组：分类 / 排序 / 模式（数理逻辑的逻辑前体）

## A4-14 分类整理游戏（按颜色/形状/用途归类）
- **name**：分类整理（"把它们分成几堆"）
- **type**：game, companionship
- **domain**：数理逻辑·认知
- **targets**：分类（classification）、`DEV-PS`、`EF-SHIFT`（换一种标准再分）、`DEV-PSE`（顺带整理习惯）
- **age_bands**：3-4（一个标准）/ 4-5（两个标准）/ 5-6（自定义标准+解释）
- **materials**：家里现成的——纽扣、积木、袜子、餐具、玩具小车、豆子（大颗）
- **steps**：
  1. 给一堆混合物品，请孩子"把一样的放一起"。
  2. 问"你是怎么分的？"让其说出标准（按颜色？大小？）。
  3. **换标准再分一次**（"刚才按颜色，现在能按大小分吗？"）——练灵活。
- **difficulty_ladder**：更易——只两类、差异明显（红 vs 蓝）；更难——多类、引入"既红又大"的二维分类、或让孩子自创分类标准并说明。
- **temperament_fit_notes**：可融入日常（收拾玩具、配袜子）减轻坚持负担；高活跃儿童做成"限时分拣赛";慢热儿童从熟悉物品开始。
- **evidence**：分类是早期数学逻辑前体；"换标准再分"对应认知灵活；分类/序列/模式预测后续算术（Zippert et al. 2020 模式预测数学；分类-序列-计数预测算术传统 Stock 等）。
- **safety_notes**：豆子/纽扣等小颗粒防 3 岁幼儿误吞，优先用大件物品。

## A4-15 排大小 / 排序列（Seriation）
- **name**：从小到大排排队（序列）
- **type**：game, companionship
- **domain**：数理逻辑·认知
- **targets**：序列/seriation、量的比较、`DEV-PS`、`DEV-COM`（比较词：更高/更矮）
- **age_bands**：3-4（3 个排序）/ 4-5（5 个）/ 5-6（7+ 个或双向）
- **materials**：套碗/套杯、不同长短的吸管或棍、全家鞋子、积木条
- **steps**：
  1. 给 3–5 个明显不同大小/长短的物品，请孩子"从小到大排好队"。
  2. 边排边说比较词："这个比那个**更长**。"
  3. 进阶：插入一个新物品，问"它该排在哪儿？"
- **difficulty_ladder**：更易——3 个、差异大；更难——增加数量、差异变小、或"从大到小"反向排、双属性排序。
- **temperament_fit_notes**：用孩子感兴趣的物（爱车的排车、爱玩偶的排玩偶）提升兴趣（`LRN-B`）；低坚持儿童 3 个起步；高活跃儿童用全家人按身高排队的"真人版"。
- **evidence**：序列是 Piaget 经典逻辑运算，亦为早期数学预测因子（分类-序列-计数预测算术成就传统）；比较词输入促进语言与数学概念（一般性发展原理 + 空间/量词语言文献 Pruden2011 邻域）。
- **safety_notes**：棍/吸管不戳眼；小物防误吞。

## A4-16 找规律接龙（Patterning）
- **name**：找规律·接下来是什么（模式接龙）
- **type**：game, companionship
- **domain**：数理逻辑·认知
- **targets**：模式/patterning、`DEV-PS`、`EF-WM`、`LRN-D`（创造自己的规律）
- **age_bands**：3-4（AB 模式）/ 4-5（ABB/AABB）/ 5-6（ABC、增长模式、自创）
- **materials**：任意可排列的小物——积木、纽扣、雪花片、画笔颜色、拍手/跺脚动作
- **steps**：
  1. 大人摆一段规律（红蓝红蓝……），请孩子说/摆"**接下来**是什么"。
  2. 让孩子**复制**这个规律，再让他**自创**一个规律考大人。
  3. 进阶用动作/声音做模式（拍手-拍手-跺脚，重复）。
- **difficulty_ladder**：更易——AB 两元素、实物摆；更难——ABC/AABB/递增模式、抽象到动作或声音、找"中间缺的那个"。
- **temperament_fit_notes**：动作/声音版适合高活跃儿童（边动边找规律）；慢热儿童先看再做；自创规律环节给主动性强的孩子发挥（`LRN-C`）。
- **evidence**：**学前模式能力独立预测当期与后续数学知识**（超出年龄、空间、工作记忆、语言；Zippert et al. 2020）；patterning 是早期数学核心。
- **safety_notes**：小物防误吞；声音版控制音量。

## A4-17 数数与一一对应（日常数感）
- **name**：到处数一数（一一对应数数）
- **type**：companionship, game
- **domain**：数理逻辑·认知·语言
- **targets**：数数/基数、一一对应、`DEV-PS`、`DEV-COM`
- **age_bands**：3-4（数到 5–10）/ 4-5（到 10–20）/ 5-6（到 20+、简单加减）
- **materials**：无；用生活实物（楼梯、葡萄、积木、手指）
- **steps**：
  1. 日常情境一边指一边数："一、二、三……"——强调**每个物体点一下、数一个**（一一对应）。
  2. 数完问"一共几个？"（理解最后一个数 = 总数，基数原则）。
  3. 5–6 岁玩"再加一个变几个/拿走一个剩几个"。
- **difficulty_ladder**：更易——数 1–5、大人陪点；更难——数更多、跳着数（2、4、6）、口头加减。
- **temperament_fit_notes**：嵌入日常（上楼梯、分水果）几乎零负担，适合所有气质；高活跃儿童边走边数台阶；低坚持儿童每次只数一小组。
- **evidence**：数数与基数是数感基础；日常数学对话与数感发展相关（早期数学游戏化传统 Ramani/Eason Kappan；与线性棋盘的数数收益一致 Ramani&Siegler2008）。
- **safety_notes**：用食物数时注意卫生与噎食风险（葡萄等切小）。

---

# 第五组：问题解决 / 推理 / 假装规划（综合执行功能）

## A4-18 这是什么·猜猜看（二十问/属性推理）
- **name**：猜猜我想的是什么（属性推理）
- **type**：game, companionship
- **domain**：认知·语言·推理
- **targets**：`DEV-PS`（逻辑推理）、`DEV-COM`、`LRN-B`（好奇追问）、`EF-WM`
- **age_bands**：4-5（具体物+少量线索）/ 5-6（提问式二十问）
- **materials**：无（可借身边物品）
- **steps**：
  1. 大人心里想一个东西，给线索："它是红色的、圆的、能吃。"
  2. 孩子根据线索猜（苹果？）。
  3. 5–6 岁反过来：孩子想，大人用"是不是会动？""比球大吗？"提问逼近——孩子学着用属性回答。
- **difficulty_ladder**：更易——给足线索直接猜；更难——孩子主动提问缩小范围（练假设检验与逻辑）。
- **temperament_fit_notes**：慢热/安静型语言强项发挥；高活跃儿童配合"猜中就去把那个东西找来"的动作版；低坚持儿童用 2–3 条强线索快速命中保持成就感。
- **evidence**：属性推理与假设检验、词汇；一般性发展原理（好奇心信息缺口 + 语言-认知）；好奇追问对应 `LRN-B`（专题05 / Jirout）。
- **safety_notes**：纯语言，无风险。

## A4-19 假装游戏与角色扮演（含"计划—执行"）
- **name**：过家家 / 主题假装游戏（开商店、当医生、做饭）
- **type**：game, companionship
- **domain**：执行功能·社会·语言·创造
- **targets**：`EF-WM`（记住角色与情节）、`EF-INH`（按角色行事、忍住跳戏）、`LRN-D`（创造）、`DEV-PSE`、`DEV-COM`
- **age_bands**：3-4（简单角色）/ 4-5 / 5-6（多角色、有情节计划）
- **materials**：家里现成道具（玩偶、空盒当收银台、毛巾当被子）
- **steps**：
  1. 和孩子一起定主题与角色（"你当医生、我当病人"）。
  2. 鼓励先简单"计划"一下情节（"先挂号、再看病、再拿药"）——这一步是关键的执行功能练习。
  3. 玩中维持角色、推进情节，大人适度跟随而非主导。
- **difficulty_ladder**：更易——单一角色、跟随孩子；更难——多角色切换、加入冲突情节需协商、玩前画/说出"剧本计划"。
- **temperament_fit_notes**：慢热儿童用熟悉主题、先旁观再入戏；高活跃儿童给动作型角色（消防员、运动员）；高负性情绪儿童借角色练情绪表达（"医生怎么安慰病人"）。
- **evidence**：成熟的假装游戏 + 自我语言（private speech）+ 情节计划是 Tools of the Mind 提升自我调节/EF 的核心机制（Diamond&Lee2011；Tools of the Mind RCT 证据 Solomon et al. 2018，效果在初始多动/注意问题儿童更显著）。
- **safety_notes**：道具安全无尖锐；避免危险情节模仿（如真用药/明火）。

## A4-20 拆装与因果探索（拧螺丝、看怎么动）
- **name**：拆装·因果探索（拧螺丝玩具、齿轮、坡道滚球）
- **type**：game, exercise, companionship
- **domain**：问题解决·精细动作·科学探究
- **targets**：`DEV-PS`、`DEV-FM`、`LRN-B`（探索）、因果推理
- **age_bands**：3-4（粗大拆装/滚球）/ 4-5 / 5-6（拧螺丝、齿轮、简单机关）
- **materials**：儿童螺丝玩具、齿轮玩具、或自制"斜坡滚球"（书本垫高 + 球/小车）、可拆的旧物（清洁安全的）
- **steps**：
  1. 给可安全拆装的物，让孩子探索"怎么拆开/装回""怎么让球滚得更远"。
  2. 多问开放问题："你觉得为什么会这样？""换个角度试试？"
  3. 鼓励预测—验证（"你猜哪个坡滚得快？我们试试"）。
- **difficulty_ladder**：更易——大件、单一动作；更难——多步骤组装、变量更多（坡度、球重）的因果对比。
- **temperament_fit_notes**：高活跃/动手型儿童的强项舞台；慢热儿童先看演示；低坚持儿童把任务拆成"先拆这一个"。
- **evidence**：因果探索与"预测-验证"是科学探究式好奇（`LRN-B`）；一般性发展原理 + 科学好奇心信息缺口理论（Jirout & Klahr 2012，专题05）。
- **safety_notes**：**重点**——拆装物须无锐边、无可吞小零件、非电器/非真有螺丝隐患；齿轮夹手注意；旧物须清洁消毒、确认安全方可给孩子。

## A4-21 厨房里的数学与科学（量、序、变化）
- **name**：厨房小帮手（量勺、分份、看变化）
- **type**：companionship, game
- **domain**：数理逻辑·科学·精细动作·自理
- **targets**：`DEV-PS`（量/数/序）、`DEV-FM`、`DEV-PSE`（自理与帮手）、`LRN-C`（主动）、`DEV-COM`（量词）
- **age_bands**：3-4（数/倒/搅）/ 4-5（量勺、按步骤）/ 5-6（看时间、对半分、简单测量）
- **materials**：安全的厨房活动——洗菜、数鸡蛋、量米、按食谱步骤摆料、分饼干
- **steps**：
  1. 让孩子参与可控步骤：数出 6 个饺子、量 2 勺面粉、把饼干"每人分到一样多"。
  2. 用语言带出数学概念："我们需要**两**杯水""把它**对半**分""**先**洗**再**切"。
  3. 观察变化（水加热冒泡、面糊变稠）引发科学好奇。
- **difficulty_ladder**：更易——只做数/倒/搅；更难——按多步食谱顺序执行（练工作记忆与序列）、做简单均分与测量。
- **temperament_fit_notes**：高负性情绪儿童在"我帮上忙了"中获得胜任感（`LRN-E`）；高活跃儿童给搅拌/揉面等大动作任务；慢热儿童从旁观和递东西开始。
- **evidence**：日常情境中的数量、序列、测量与因果；日常数学对话促进数感（Ramani/Eason Kappan 早期数学游戏化）；多步骤食谱执行练工作记忆与计划（一般性发展原理 + EF 框架 Garon2008）。
- **safety_notes**：**远离明火、刀具、热源、电器**；只分配绝对安全的步骤；食材防噎、注意过敏与卫生；全程大人在旁。

## A4-22 走与跳的"脑筋急转弯"运动（跨域 EF + 大运动）
- **name**：身体版执行功能游戏（按颜色跳格、听数字做动作）
- **type**：exercise, game
- **domain**：执行功能·大运动
- **targets**：`EF-INH`、`EF-SHIFT`、`EF-WM`、`DEV-GM`、`LRN-A`
- **age_bands**：4-5 / 5-6（3-4 用最简单版）
- **materials**：地上贴几张彩色纸/呼啦圈，或粉笔画格子
- **steps**：
  1. 约定规则："听到'红'跳到红圈，听到'蓝'跳到蓝圈"。
  2. 进阶加抑制/转换："听到'红'反而跳到蓝""数字是单数就单脚站"。
  3. 规则中途切换，考验灵活与记忆。
- **difficulty_ladder**：更易——颜色-位置直接对应、慢速；更难——加"做相反""叠加两条规则""规则突然变"。
- **temperament_fit_notes**：**为高活跃儿童量身**——把抽象 EF 练习装进跑跳，既消耗精力又练自控；低坚持儿童回合短、规则少；慢热儿童先慢走版。
- **evidence**：把抑制/转换/工作记忆嵌入有氧运动，符合 Diamond&Lee2011"运动 + 认知挑战联合"的有效路径；与 HTKS 的"听指令做（相反）动作"同构（Ponitz2009 / HTKS-R）。
- **safety_notes**：地面防滑、清空障碍；跳跃落地缓冲；穿防滑鞋或光脚。

---

## 覆盖度自检

| 维度 | 覆盖情况 |
|---|---|
| **活动条数** | 22 条（A4-01 ~ A4-22） |
| **年龄段** | 3-4 / 4-5 / 5-6 三段均覆盖；多数活动三段通用并给按龄裁剪，少数（如 A4-04/05/16 进阶、A4-18）偏 4-5/5-6 |
| **type** | game（绝大多数）、exercise（A4-01/03/11/12/20/22 等）、companionship（A4-05/06/07/08/10/17/18/19/21 等）均有覆盖 |
| **执行功能三件套** | 抑制 `EF-INH`（01/02/03/04/08/22…）、工作记忆 `EF-WM`（05/06/16/18/19/22…）、转换 `EF-SHIFT`（04/08/14/22…）齐全 |
| **数理逻辑** | 数感/数数（07/17/21）、空间/几何（10/11/12/13）、分类（14）、序列（15）、模式（16） |
| **拼图迷宫** | 拼图 A4-10、迷宫 A4-11、七巧板 A4-13 |
| **规则类桌游** | A4-07 数字棋、A4-08 规则桌游、A4-06 记忆翻牌 |
| **抑制/记忆游戏** | 红灯绿灯 A4-01、西蒙说 A4-02、Freeze A4-03、相反游戏 A4-04、叠加口令 A4-05 |
| **对应本工具构念** | 学习品质 LRN-A/B/C/D/E/F、发展领域 DEV-PS/FM/COM/PSE、EF 行为标记 EF-WM/INH/SHIFT 全部映射；并在每条 `temperament_fit_notes` 体现与气质模块（专题01）的 goodness-of-fit |

---

## 参考 / 依据列表

> 标注规则：✅=同行评审/权威机构一手来源，核心信息经本轮检索核实；🟡=来源可靠、部分细节（卷期/页码/确切样本）建议查原文核实；**原理性**=仅有一般性发展原理支撑，已在活动中如实标注，未挂具体研究。

**执行功能·总论与方法**
1. ✅ **Diamond, A., & Lee, K. (2011).** Interventions shown to aid executive function development in children 4 to 12 years old. *Science, 333*(6045), 959–964. DOI: 10.1126/science.1204529 ｜ PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3159917/ （规则游戏/运动/武术/瑜伽/正念/Tools of the Mind 等均可改善 EF；**核心原则：EF 须被持续挑战、难度不递增则无收益**——本库 `difficulty_ladder` 的依据）。
2. ✅ **Garon, N., Bryson, S. E., & Smith, I. M. (2008).** Executive function in preschoolers: A review using an integrative framework. *Psychological Bulletin, 134*(1), 31–60. DOI: 10.1037/0033-2909.134.1.31 ｜ https://pubmed.ncbi.nlm.nih.gov/18193994/ （学前 EF 三成分：工作记忆、抑制、转换；入学准备的生物学基础）。
3. ✅ **Harvard University, Center on the Developing Child.** *Activities Guide: Enhancing and Practicing Executive Function Skills with Children from Infancy to Adolescence*（含 3–5 岁的冻结游戏、西蒙说、配对/记忆类、安静专注游戏等 EF 活动）. https://developingchild.harvard.edu/resources/handouts-tools/activities-guide-enhancing-and-practicing-executive-function-skills/ ｜ 3–5 岁 PDF: https://developingchild.harvard.edu/wp-content/uploads/2024/10/Executive-Function-Activities-for-3-to-5-year-olds.pdf （权威机构活动指南；引用为活动类型出处，未逐字复制）。

**抑制控制 / 自我调节任务（红灯绿灯·西蒙说·相反游戏的对应测评）**
4. ✅ **Ponitz, C. C., McClelland, M. M., Matthews, J. S., & Morrison, F. J. (2009).** A structured observation of behavioral self-regulation and its contribution to kindergarten outcomes. *Developmental Psychology, 45*(3), 605–619. DOI: 10.1037/a0015365 ｜ https://pubmed.ncbi.nlm.nih.gov/19413419/ （Head-Toes-Knees-Shoulders 任务：做相反动作，调用工作记忆+抑制+认知灵活，预测学业；"相反游戏/西蒙说"类游戏的循证对应）。
5. ✅ **Gonzales, C. R., Bowles, R., Geldhof, G. J., Cameron, C. E., Tracy, A., & McClelland, M. M. (2021).** The Head-Toes-Knees-Shoulders Revised (HTKS-R): Development and psychometric properties of a revision to reduce floor effects. *Early Childhood Research Quarterly, 56*, 320–332.（HTKS-R 修订版，四指令"相反"结构——本库 A4-04 进阶版的同构来源）〔卷期 🟡 建议核对〕。
6. ✅ **Duncan, R. J., et al.（meta-analysis, 2023）.** A meta-analysis of the validity of the Head-Toes-Knees-Shoulders task in predicting young children's academic performance. *Frontiers in Psychology, 14*, 1124235. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1124235/full （HTKS 预测学业表现的跨研究效力）〔作者全名 🟡 建议核对〕。
7. 🟡 **Bardack, S., et al. / Springer (2024).** Using Games and Activities to Increase Inhibitory Control Skills in Kindergarten-aged Children. *Early Childhood Education Journal.* DOI: 10.1007/s10643-024-01847-x ｜ https://link.springer.com/article/10.1007/s10643-024-01847-x （Simon Says、Freeze、Opposite Game 等练抑制控制的活动方案；作者/卷期 🟡 需核实原文）。
8. 🟡 **（系统性玩耍提升学前 EF 的纵向研究）** Executive Functions Can Be Improved in Preschoolers Through Systematic Playing in Educational Settings. *Frontiers in Psychology (2019), 10,* 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC6734167/ （结构化游戏可提升学前 EF）〔作者全名/细节 🟡 需核实〕。

**数感 / 线性数字棋盘（A4-07）**
9. ✅ **Ramani, G. B., & Siegler, R. S. (2008).** Promoting broad and stable improvements in low-income children's numerical knowledge through playing number board games. *Child Development, 79*(2), 375–394. DOI: 10.1111/j.1467-8624.2007.01131.x （线性数字棋盘 RCT：提升数量比较、数线估计、数数、数字识别；线性优于圆形）。
10. ✅ **Siegler, R. S., & Ramani, G. B. (2009).** Playing linear number board games—but not circular ones—improves low-income preschoolers' numerical understanding. *Journal of Educational Psychology, 101*(3), 545–560. DOI: 10.1037/a0014239 （线性 vs 圆形对比；约 1 小时游戏、收益维持约 9 周）。
11. ✅ **Laski, E. V., & Siegler, R. S. (2014).** Learning from number board games: You learn what you encode. *Developmental Psychology, 50*(3), 853–864. DOI: 10.1037/a0034321 ｜ https://siegler.tc.columbia.edu/wp-content/uploads/2019/02/2014-Laski-Siegler.pdf （"走格时念出落点数字"的编码方式最有效——本库 A4-07 步骤设计依据）。
12. 🟡 **Ramani, G. B., & Eason, S. H.** It all adds up: Learning early math through play and games. *Kappan/Phi Delta Kappan.* https://kappanonline.org/early-math-play-games-ramani-eason/ （实践综述：日常游戏与数学对话促进数感；实践来源）。

**空间 / 积木 / 拼图（A4-10/11/12/13）**
13. ✅ **Verdine, B. N., Golinkoff, R. M., Hirsh-Pasek, K., Newcombe, N. S., Filipowicz, A. T., & Chang, A. (2014).** Deconstructing building blocks: Preschoolers' spatial assembly performance relates to early mathematics skills. *Child Development, 85*(3), 1062–1076. ｜ PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962809/ （空间装配能力与早期数学相关）。
14. ✅ **Schmitt, S. A., Korucu, I., Napoli, A. R., Bryant, L. M., & Purpura, D. J. (2018).** Using block play to enhance preschool children's mathematics and executive functioning: A randomized controlled trial. *Early Childhood Research Quarterly, 44*, 181–191. https://www.sciencedirect.com/science/article/abs/pii/S0885200618300310 （半结构化积木游戏 RCT，促进数学与执行功能）。
15. 🟡 **（2024 低收入样本积木 RCT）** Testing block play as an effective mechanism for promoting early math, executive function, and spatial skills in preschoolers from low-income backgrounds. *Early Childhood Research Quarterly (2024).* https://www.sciencedirect.com/science/article/abs/pii/S0885200624001911 〔作者/卷期 🟡 需核实〕。
16. ✅ **Pruden, S. M., Levine, S. C., & Huttenlocher, J. (2011).** Children's spatial thinking: Does talk about the spatial world matter? *Developmental Science, 14*(6), 1417–1430. ｜ PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3372906/ （家长空间语言输入预测幼儿日后空间能力——本库"空间语言旁白"建议依据）。
17. 🟡 **Levine, S. C., et al. / Psychological Science（puzzle & block play）.** 玩拼图/积木/桌游频繁的幼儿空间测试表现更好；拼图游戏（2–4 岁）可改变空间思维. https://www.psychologicalscience.org/news/releases/playing-with-puzzles-and-blocks-may-build-childrens-spatial-skills.html （机构新闻稿转述同行评审研究；建议追原始论文 Levine et al. 2012, *Dev. Psych.* / Jirout & Newcombe 2015 核实）。

**分类 / 排序 / 模式（A4-14/15/16）**
18. ✅ **Zippert, E. L., Clayback, K., & Rittle-Johnson, B. (2019/2020).** Not just IQ: Patterning predicts preschoolers' math knowledge beyond fluid reasoning. *British Journal of Developmental Psychology / 相关.* PDF: https://cdn.vanderbilt.edu/vu-sub/wp-content/uploads/sites/280/2023/07/19032253/ZippertClaybackBRJ.pdf （**模式能力独立于年龄、空间、工作记忆、语言，预测当期与后续数学知识**）〔确切期刊/卷期 🟡 建议核对〕。
19. 🟡 **Stock, P., Desoete, A., & Roeyers, H.（分类-序列-计数传统）.** Classification, seriation, and counting as predictors of arithmetic achievement.（Piagetian 逻辑运算预测算术）https://www.researchgate.net/publication/247782444 （传统证据线；作者/年份/卷期 🟡 需核实原文）。

**假装游戏 / 自我调节课程（A4-19）**
20. ✅ **Solomon, T., et al. (2017/2018).** A cluster randomized-controlled trial of the impact of the Tools of the Mind curriculum on self-regulation in Canadian preschoolers. *Frontiers in Psychology, 8,* 2366. ｜ PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC5782823/ （成熟假装游戏+自我语言+计划提升自我调节；效果在初始高多动/注意问题儿童更显著——结果有边界，已如实标注）〔作者全名 🟡 建议核对〕。

**好奇心 / 探究（A4-18/20，跨引专题05）**
21. ✅ **Jirout, J., & Klahr, D. (2012).** Children's scientific curiosity: In search of an operational definition of an elusive concept. *Developmental Review, 32*(2), 125–160.（科学好奇=对期望不确定性的阈值，信息缺口理论；A4-18/20 探究式好奇依据，亦见本工具专题05）。

**跨专题对齐（非新增文献，指向本工具既有简报）**
22. 本库构念代码（DEV-* / LRN-* / EF-*）与气质 goodness-of-fit 裁剪，对齐本工具：专题03《发展领域快照》、专题05《学习品质/approaches-to-learning》、专题01《气质》。活动选用与裁剪逻辑须与上述简报的"非诊断、个体内相对比较"定位一致。

---

*免责再申明：本活动库为家庭陪伴与顺势养育建议，非认知训练疗程、非诊断或矫正工具。所有"练某能力"均指日常游戏中的自然练习机会，不承诺测验分数提升。标 🟡 条目在正式上线前应回到一手文献复核；标"原理性"的活动不得在面向家长的文案中包装成"有研究证明的效果"。*
