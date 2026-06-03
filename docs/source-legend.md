# Source Legend（题库 source 缩写键 → 完整文献映射）

> 版本：2026-06-03 ｜ 负责人：版权/许可合规复核（只读 item-bank，不改题库）
> 用途：把 `docs/item-bank.json` 每题 `source` 字段里出现的**每个缩写键**逐一映射到 `docs/理论依据与方法学.md §9 参考文献总表`的完整条目，杜绝「孤儿 key」（题库出现但此处查不到）与「多余 key」（此处列了但题库未用）。
> 边界声明：本工具所有题目均为**中文自编**，下列文献仅为「灵感来源构念 + 出处」的留痕（ITC 2017 跨文化改编留痕），**不代表照抄任何原题文字**。受版权量表的采用/未采用边界详见 `docs/许可与对齐边界表.md`。

---

## 0. 提取方法与对照口径

- **提取范围**：`item-bank.json` 全部 6 个 section（TMP / SEL / DEV / INT / LRN / FAM）+ OPEN 开放题，逐题取 `source` 字段。
- **拆分规则**：`source` 形如 `"EAS1984/Rothbart2001"` 的复合串，按 `/` 拆为原子键分别登记。
- **可核实性图例**（沿用 §9）：✅ 已核实关键书目；🟡 部分细节待核；⚠️ 仅二手/有已知问题。
- **§9 条目号**：指向 `理论依据与方法学.md §9` 的编号，便于回查完整 DOI/卷期。

---

## 1. 题库出现的全部 source 键（逐一映射，A→Z 大致按 section 出现序）

| # | 题库 source 缩写键 | 出现题号（示例/全部） | 完整文献（精简） | §9 条目 | 可核实性 |
|---|---|---|---|---|---|
| 1 | `EAS1984` | TMP-01,02,03 | Buss, A. H., & Plomin, R. (1984). *Temperament: Early Developing Personality Traits*. Erlbaum.（EAS 模型） | 6 | ✅ |
| 2 | `Rothbart2001` | TMP-01,03,04,06~17,19（CBQ 全段主出处） | Rothbart, Ahadi, Hershey & Fisher (2001). Investigations of temperament at three to seven years: The CBQ. *Child Development*, 72(5), 1394-1408.（题库 `Rothbart2001` ＝ §9 `ROTH2001`） | 1 | ✅ |
| 3 | `NYLS1977` | TMP-05 | Thomas, A., & Chess, S. (1977). *Temperament and Development*. Brunner/Mazel.（NYLS 九维度/三类型/goodness-of-fit） | 5 | 🟡 |
| 4 | `PR2006` | TMP-13,16,18 | Putnam, S. P., & Rothbart, M. K. (2006). Short and very short forms of the CBQ. *J. Personality Assessment*, 87(1).（题库 `PR2006` ＝ §9 `PUTN2006`） | 2 | 🟡 |
| 5 | `DECA-SR` | SEL-01,03,05 | LeBuffe & Naglieri (2012). *DECA-P2*，自我调节(Self-Regulation)保护因子。题库 `DECA-SR`/`DECA-IN`/`DECA-AT` 均指 DECA-P2 的三保护因子分支(SR/Initiative/Attachment) | 10 | ✅ |
| 6 | `ThompER` | SEL-01,02,03 | Thompson, R. A. (1994). Emotion Regulation: A Theme in Search of Definition. *Monographs SRCD*, 59(2-3). | 21 | ✅/🟡 |
| 7 | `Denh` | SEL-02 | Denham, S. A., et al. (2003). Preschool Emotional Competence. *Child Development*, 74(1), 238-256. | 28 | ✅ |
| 8 | `Koch` | SEL-04,06 | Kochanska, G., Murray, K. T., & Harlan, E. T. (2000). Effortful Control in Early Childhood. *Developmental Psychology*, 36(2), 220-232. | 20 | ✅ |
| 9 | `Diam` | SEL-04,05,06 | Diamond, A. (2013). Executive Functions. *Annual Review of Psychology*, 64, 135-168. | 18 | ✅ |
| 10 | `DECA-IN` | SEL-07,08,09 | LeBuffe & Naglieri (2012). *DECA-P2*，主动性(Initiative)保护因子。 | 10 | ✅ |
| 11 | `ASQSE2` | SEL-07 | Squires, Bricker & Twombly (2015). *ASQ:SE-2 User's Guide*. Brookes. | 17 | ✅ |
| 12 | `DECA-AT` | SEL-10,11,12 | LeBuffe & Naglieri (2012). *DECA-P2*，依恋/关系(Attachment/Relationships)保护因子。 | 10 | ✅ |
| 13 | `ZW` | SEL-10,13 | Zahn-Waxler, C., et al. (1992). Development of concern for others. *Developmental Psychology*, 28(1), 126-136. | 27 | 🟡 |
| 14 | `Eisen` | SEL-12,16 | Eisenberg, Fabes & Spinrad (2006). Prosocial Development. In *Handbook of Child Psychology, Vol.3*. | 23 | ✅ |
| 15 | `Hoff` | SEL-13,16 | Hoffman, M. L. (2000). *Empathy and Moral Development*. Cambridge UP.（注：题库共情线索的 `Hoff` ＝ Hoffman2000，**与家庭语言环境的 `HOFFxxxx`=Erika Hoff 系列不同人，勿混**） | 25 | ✅ |
| 16 | `Dunf` | SEL-14,15 | Dunfield, K. A. (2014). A construct divided: prosocial behavior as helping, sharing, and comforting. *Frontiers in Psychology*, 5:958. | 26 | ✅ |
| 17 | `SDQ-Pro` | SEL-14,15 | Goodman, R. (1997). SDQ — **亲社会(Prosocial)分量表**。题库 `SDQ-Pro` ＝ §9 `SDQ1997` 的亲社会侧（题库注：SEL 计分已去除 SDQ 亲社会出处，详见边界表 SEL/SDQ 行） | 13 | ✅ |
| 18 | `ASQ3` | DEV-01 | Squires, J., & Bricker, D. (2009). *ASQ-3*. Brookes.（题库 `ASQ3` ＝ §9 `ASQ`） | 30 | ✅ |
| 19 | `CDC2022` | DEV-01,02,03,06~15 | Zubler, J. M., et al. (2022). Evidence-Informed Milestones for Developmental Surveillance. *Pediatrics*, 149(3). | 31 | ✅ |
| 20 | `ECM-II` | DEV-02,04~08,11,12,13,15 | WS/T 580—2017《0 岁~6 岁儿童发育行为评估量表》（儿心量表-II）。题库 `ECM-II` ＝ §9 `ERXIN2017`/`WS-T580` | 35 | ✅ |
| 21 | `WHO-MGRS` | DEV-04,05 | WHO Multicentre Growth Reference Study; Wijnhoven et al. (2006). *Acta Paediatrica*, 95(Suppl 450), 86-95. | 34 | ✅ |
| 22 | `DAP` | DEV-06 | Goodenough (1926) / Harris (1963)《画人测验》（Draw-A-Person，身体部位数随龄增加） | 36 | ⚠️ |
| 23 | `HR2006` | INT-01,02,03,04,07；INT-12,13；OPEN-02 | Hidi, S., & Renninger, K. A. (2006). The Four-Phase Model of Interest Development. *Educational Psychologist*, 41(2), 111-127. | 38 | ✅ |
| 24 | `MOE2012` | INT-01~08；DEV/SEL/LRN 多处对齐 | 中华人民共和国教育部 (2012)《3-6 岁儿童学习与发展指南》（健康/语言/社会/科学/艺术五领域）。 | 81 | ✅ |
| 25 | `ALEXANDER2008` | INT-06 | Alexander, J. M., et al. (2008). The development of conceptual interests in young children. *Cognitive Development*, 23(2), 324-334. | 49 | 🟡 |
| 26 | `SDQ1997` | INT-08（社交扮演兴趣的领域背书） | Goodman, R. (1997). The Strengths and Difficulties Questionnaire: A research note. *J. Child Psychology & Psychiatry*, 38(5), 581-586. | 13 | ✅ |
| 27 | `FLOW-CSZ` | INT-09 | Csikszentmihalyi, M. (1990/2014). *Flow* / *Applications of Flow in Human Development*. Springer.（心流/沉浸） | 47 | ✅ |
| 28 | `MORGAN-DMQ` | INT-10,11,14,15 | Morgan, G. A., et al. (2017). The revised Dimensions of Mastery Questionnaire (DMQ 18). *HERJ*, 7(2), 48-67.（题库 `MORGAN-DMQ`/`DMQ18` 同源 DMQ 18） | 41 | ✅ |
| 29 | `DMQ18` | LRN-01,03,10,12,13 | 同上 Morgan et al. (2017) DMQ 18。 | 41 | ✅ |
| 30 | `EF` | LRN-01,02,07,08,09 | Garon, N., Bryson, S. E., & Smith, I. M. (2008). Executive function in preschoolers: an integrative framework. *Psychological Bulletin*, 134(1), 31-60.（题库 `EF` ＝ §9 `Garon2008`） | 55 | ✅ |
| 31 | `ELOF` | LRN-03,06,07,14 | Office of Head Start. *Head Start Early Learning Outcomes Framework (ELOF)* — Approaches to Learning (P-ATL 10/11/12). | 58 | ✅ |
| 32 | `ID-YC` | LRN-04,05 | Tang, S., et al. (2024). Validation of the I-/D-type epistemic curiosity scale among young Chinese children. *BMC Psychology*, 12:795.（题库 `ID-YC` ＝ §9 `Tang2024`） | 45 | ✅ |
| 33 | `Jirout` | LRN-04 | Jirout, J., & Klahr, D. (2012). Children's scientific curiosity. *Developmental Review*, 32(2), 125-160. | 46 | ✅ |
| 34 | `Hyson` | LRN-06 | Hyson, M. (2008). *Enthusiastic and Engaged Learners*. Teachers College Press / NAEYC. | 57 | ✅ |
| 35 | `DMQ_def` | LRN-11,14 | Morgan, G. A., et al. (2009). *The Dimensions of Mastery Questionnaire (DMQ) Manual* (DMQ 17 定义).（题库 `DMQ_def` ＝ §9 `DMQ_manual2009`/`DMQ_def`） | 42 | ✅ |
| 36 | `Mindset` | LRN-10,11,12,13 | Gunderson, E. A., et al. (2013). Parent praise predicts children's motivational frameworks. *Child Development*, 84(5), 1526-1541.（题库 `Mindset` ＝ §9 `Gunderson2013`/`Mindset`；成长型思维前体） | 61 | ✅ |
| 37 | `PSDQ2001` | FAM-01,03 | Robinson, C. C., et al. (2001). The Parenting Styles and Dimensions Questionnaire (PSDQ). In *Handbook of Family Measurement Techniques, Vol.3*. | 68 | ✅ |
| 38 | `MACCOBY1983` | FAM-01 | Maccoby, E. E., & Martin, J. A. (1983). Socialization in the context of the family. In *Handbook of Child Psychology, Vol.4*. | 67 | 🟡 |
| 39 | `BAUMRIND1991` | FAM-02 | Baumrind, D. (1991). The influence of parenting style on adolescent competence. *J. Early Adolescence*, 11(1), 56-95.（另见 §9-65 BAUMRIND1971） | 66 | ✅ |
| 40 | `CHAO1994` | FAM-02,12 | Chao, R. K. (1994). Beyond parental control… Chinese parenting through the cultural notion of training. *Child Development*, 65(4), 1111-1119. | 69 | ✅ |
| 41 | `HOME1979` | FAM-03,05,07 | Bradley, R. H., & Caldwell, B. M. (1979). Home Observation for Measurement of the Environment (preschool scale). *Am. J. Mental Deficiency*, 84(3), 235-244. | 70 | ✅ |
| 42 | `HOFF2018` | FAM-04,11 | Hoff, E. (2018). Bilingual development in children of immigrant families. *Child Development Perspectives*, 12(2), 80-86. | 78 | ✅ |
| 43 | `HOFF2003` | FAM-05,06 | Hoff, E. (2003). The specificity of environmental influence: SES affects early vocabulary via maternal speech. *Child Development*, 74(5), 1368-1378. | 76 | ✅ |
| 44 | `HOME1988` | FAM-06 | Bradley, R. H., Caldwell, B. M., et al. (1988). HOME Inventory for families with children 6-10. *Contemporary Educational Psychology*, 13(1), 58-71. | 71 | ✅ |
| 45 | `WHO2019` | FAM-08 | WHO (2019). *Guidelines on physical activity, sedentary behaviour and sleep for children under 5*. Geneva. | 72 | ✅ |
| 46 | `AAP2016MEDIA` | FAM-08,09 | AAP Council on Communications and Media (2016). Media and Young Minds. *Pediatrics*, 138(5), e20162591.（题库 `AAP2016MEDIA` ＝ §9 `AAP2016MEDIA`） | 73 | ✅ |
| 47 | `AASM2016` | FAM-10 | Paruthi, S., et al. (2016). Recommended amount of sleep for pediatric populations (AASM consensus). *J. Clin. Sleep Med.*, 12(6), 785-786. | 74 | ✅ |
| 48 | `NSF2015` | FAM-10 | Hirshkowitz, M., et al. (2015). National Sleep Foundation's sleep time duration recommendations. *Sleep Health*, 1(1), 40-43. | 75 | ✅ |
| 49 | `WS-T579` | FAM-10 | 国家卫健委《WS/T 579-2017 0 岁～5 岁儿童睡眠卫生指南》（题库写作 `WS-T579`，§9 同键）。 | 82 | ✅ |
| 50 | `HOFF2012` | FAM-11 | Hoff, E., et al. (2012). Dual language exposure and early bilingual development. *J. Child Language*, 39(1), 1-27. | 77 | ✅ |
| 51 | `XU2024` | FAM-12,13 | Xu, W., Parra, G. R., & Carter, M. K. (2024). Intergenerational coparenting and child development: a systematic review. *J. Family Theory & Review*, 16(4), 834-856. | 79 | ✅ |
| 52 | `MEAS` | OPEN-01,03 | 内部约定键：「测量/需求采集」用途标记，方法学锚定 AERA/APA/NCME (2014)《Standards》（§9 `STD2014`）；非独立文献，OPEN 题与 `STD2014`/`AAP2020` 联用。 | 86 | ✅（约定键，见 §3 备注） |
| 53 | `STD2014` | OPEN-01 | AERA, APA, & NCME (2014). *Standards for Educational and Psychological Testing*. AERA. | 86 | ✅ |
| 54 | `DELOACHE2007` | OPEN-02 | DeLoache, J. S., Simcock, G., & Macari, S. (2007). Extremely intense interests in very young children. *Developmental Psychology*, 43(6), 1579-1586. | 48 | ✅ |
| 55 | `AAP2020` | OPEN-03 | Council on Children with Disabilities; Section on Developmental and Behavioral Pediatrics (2020). Promoting optimal development. *Pediatrics*, 145(1), e20193449. | 94 | ✅ |

---

## 2. 孤儿 key 检查（题库出现 → 此表必须能查到）

**结论：无孤儿 key。** 上表第 1 列已覆盖 `item-bank.json` 全部题目 `source` 字段拆分后的**每一个原子键**（共 55 个去重原子键），逐一映射到 §9 完整条目。

- 唯一需特别说明的是 `MEAS`：它**不是** §9 里的独立文献编号，而是 OPEN 开放题（OPEN-01/03）的内部用途标记键，方法学背书为 `STD2014`（§9-86）与 `AAP2020`（§9-94）。已在上表第 52 行明确登记，故**不构成孤儿 key**，但建议正式发布前在 §9 显式补一行「`MEAS` ＝ 内部需求采集约定键，非外部文献」以彻底消歧。

---

## 3. 多余 key 检查（此表/§9 列出 → 题库未实际使用）

下列出现在 `理论依据与方法学.md`（§3 映射表或 §9 文献表）但**题库 `source` 字段未直接写入**的 key，属「方法学支撑但未挂在某具体题 source 上」，于本工具**不算违规**（它们是构念背书/反例/方法学旁证），但为透明起见标出，避免误以为题库引用了它们：

| §文档中的 key | 状态 | 说明 |
|---|---|---|
| `Kotelnikova2015` / `Ahadi1993` / `McClowry2008` / `Sleddens2011`(9a) | 多余（仅 §9 背书） | CBQ 因子分析/跨文化/匹配度旁证，未挂具体题 source。 |
| `Siu2024` / `DECA-validity`(BulotskyShearer2013) | 多余（仅 §9 背书） | DECA-P2 中文化与效度旁证；题库只用 `DECA-SR/IN/AT`。 |
| `Du2008` / `Gao2013` / `SDQ_HK`(Wong2025) | 多余（仅 §9 背书） | SDQ 中国信效度/常模旁证（佐证「不报百分位」），未挂题。 |
| `CBCL` / `CBCL2011` | 多余（仅 §9 背书） | 作为「问题侧、本工具不采用」的反向参照，题库刻意不引。 |
| `Carlson2005`(Carl) / `CHEXI`(Thorell2008) / `Gross2007` | 多余（仅 §9 背书） | EF/情绪调节理论背景，未挂具体题。 |
| `RenningerHidi2016` / `Schiefele2009` / `DMQ_manual2009` 期刊版 `Józsa&Morgan2015` / `Neitzel2019` / `White1959` / `OECD-SSES` | 多余（仅 §9 背书） | 兴趣/掌握动机/学习品质理论纵深，未挂题。 |
| `KaminsDweck1999` / `Xu2023_praiseBalance` / `Vitiello2017` | 多余（仅 §9 背书） | 表扬方式/动机框架旁证，题库 LRN 只挂 `Mindset`(Gunderson2013)。 |
| `BAUMRIND1971` | 多余（§9-65） | 题库 FAM-02 只挂 `BAUMRIND1991`；1971 为同作者更早源。 |
| `2025留守研究` / 隔代养育(2018) / 非父母照护(PMC8818854) / 运动指南(2018) | 多余（仅 §9 背书） | 中国养育文化语境背景，非题目 source。 |
| `Waterhouse2023/2006` / `Gardner1983` | 多余（仅 §9 背书） | 多元智能=neuromyth 的反例/领域命名参照，**刻意不作测量依据**。 |
| `ITC2017` / `MEADE12` / `WARD23` / `SATIS` / `REFGRP` / `IDISC` / `WENG04` / `PARSCALE` / `BERS` / `IPS` / `CDC_LTSAE` | 多余（仅 §9 背书） | 测量方法学/伦理/计时/ipsative 等，支撑计分与质量逻辑，非具体题 source。 |
| `Schmidt2022`(已撤稿) / `SDB_LIT`(已删除) | 多余且失效 | §9-29 已撤稿、§9-98 已删除，**任何场合不得作依据**；题库本就未引。 |

> 上述「多余」均为**良性**：它们使方法学链条完整，但不是题目层面的灵感出处。题库 `source` 只登记「最直接的灵感来源」，符合「对齐有据、表达自创」的留痕原则。

---

## 4. 一句话校验

题库出现的 **55 个原子 source 键** 全部可在本表 §1 查到（**无孤儿 key**）；本表 §3 另标出 ~40 个仅作方法学背书、题库未直接挂载的 **多余 key**（含 2 个已撤稿/已删除、不得作依据者）。
