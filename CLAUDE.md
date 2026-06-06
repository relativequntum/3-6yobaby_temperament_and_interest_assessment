# CLAUDE.md · 3–6 岁幼儿发展优势与兴趣画像测评

> 给在此仓库工作的人与 agent 的总览。**这是地图与要点；细节见末尾「深读文档」。**

## 1. 这是什么
一套面向 **3–6 岁幼儿家长**的「发展优势 + 兴趣画像」**非诊断**测评工具。
家长在线填**自适应问卷** → 导出结构化 JSON → 由分析 **skill** 生成温暖、循证、个体内比较的画像报告（含游戏/锻炼/家庭陪伴建议）。
非商业、给朋友家长用。作者是一位 3 岁娃的父亲，重严谨、要扎实理论依据、用中文。

## 2. 三条铁律（贯穿全项目，任何改动都不能破）
1. **非诊断**：不下临床结论、不出诊断/筛查词（自闭/发育迟缓/多动/障碍/落后/达标…）、不制造焦虑。
2. **个体内（ipsative）**：只把孩子和**他自己**比；**绝不**报人群百分位/同龄常模（我们没有本地常模）。
3. **原始水平防护（代号 T-11）**：个体内中心化必然产生「相对低项」；**原始水平为高的项绝不写成劣势**，只说「相对没那么突出但仍很常见」。
其余：循证可溯源（建议挂真实活动 id）、温暖去刻板、据实标数据置信、红旗只软转介。

## 3. 现状
- **四阶段 MVP 全部完成**，经 3 轮第三方复核（R2/R3/R4）迭代到位。
- 计分引擎 **34 单测全过**；`tests/validate_sample.py` exit 0；活动库 **153 条**引文已清理。
- 进度详见 `git log` 与项目记忆 `~/.claude/.../memory/child-assessment-project.md`。

## 4. 完整工作闭环
```
questionnaire/index.html  自适应问卷(自包含离线,出生月→3-4/4-5/5-6 段切题)
  → 家长填 → 导出 JSON(还有 PDF/XLSX/MD)
  → 把 JSON 放进 inbox/<YYYY-MM-DD>/
  → 按 skill/SKILL.md 跑: score.py(计分) → select_activities.py(选活动) → Claude撰叙事 → render.py(出报告)
  → reports/{昵称-childid-日期}/ {report.md, report.html(手机), report.pdf(A4)}   原JSON归档 processed/
```

## 5. 目录/文件地图
- `questionnaire/index.html` — 自适应单文件问卷（分段进度条；5点量表；localStorage暂存；4种导出；**离线无CDN**；**内联了一份题库副本，必须与 `docs/item-bank.json` 逐字一致**）。`sample-export.json` = 导出样例(豆豆,4-5段)。
- `docs/item-bank.json` — **题库单一事实源**（95题：TMP19/SEL16/DEV15/INT15/LRN14/FAM13/OPEN3；评分题79）。每题挂 construct/report_subscale/cluster/reverse/anchors_by_band/consistency_pair_id/source。`item_bank_version` 现 **1.1.2**。
- `docs/问卷蓝图.md` — 人读蓝图（逐题清单+构念映射+覆盖声明+计分契约概述）。
- `docs/理论依据与方法学.md` — 带引用方法学；**§4.6-4.8 是计分契约**；含局限声明；~100 引用(少量诚实「待核」)。
- `docs/json-schema.md` + `schema/export.schema.json` — 导出 JSON 的人读说明 + 机读 JSON Schema(draft2020-12)。
- `docs/{许可与对齐边界表, source-legend, 引文对照表, 隐私说明}.md` — 版权边界 / source键→文献 / 引文对照 / 家长隐私说明。
- `skill/` — 分析 skill：
  - `SKILL.md` — **改报告前必读**：运行流程 + 报告大纲 + 叙事铁律(8条NEVER)。
  - `PROFILE_SCHEMA.md` — score.py 输出 `profile.json` 的契约。
  - `scoring/scoring-config.json`(+README) — 机读计分配置（构念/反向/簇/中心化/阈值/红旗）。
  - `activity_bank/activity-bank.json`(+README) — 循证活动库(153条)；`version` **1.1.1**(独立线)。
  - `scripts/`：`score.py`(确定性计分) `select_activities.py`(选活动) `charts.py`(内联SVG图) `render.py`(出MD/HTML/PDF)。
  - `templates/base.html`(响应式外壳)；`tests/test_scoring.py`(34单测,含T-11防护)。
- `tests/validate_sample.py` — 样例↔题库一致性 CI 门禁。
- `docs/sample-report/` — 豆豆(虚构)演示报告四件套（**可入库**）。
- `docs/review/` — 复核报告 R2/R3/R4 + 待办清单（审计轨迹）。
- **运行时数据(已 gitignore、绝不入库)**：`inbox/`(待分析) `processed/`(已归档) `reports/`(生成的真实报告) `work/`(skill中间产物)。

## 6. 计分契约要点（改 skill 必读 `docs/理论依据与方法学.md §4.6-4.8` + `scoring-config.json`）
- **5 组同义簇**(focus_persistence / inhibitory_control / initiative / resilience / mastery) 合并为单一指标、进个人基线只计一次，**绝不报成多个独立优势**。
- **个体内中心化**按「同量表/同 section」；like5(兴趣领域) 与 freq5(行为) **分基线**、不跨量表合并；**单题子维度不进基线、不排序**。
- **报告默认粒度 = section 层**；子维度仅定性、标「题少仅供参考」。
- 反向题翻转后同向；红旗保守触发(DEV原始最低档+数据可信)、软转介非诊断措辞；阈值在 `scoring-config.relative_label_thresholds`(±0.30)。

## 7. 报告（改报告前必读 `skill/SKILL.md`）
大纲：① 一页速览 → ② 概览 → ③《怎么读这份报告》(render 静态段：名词解释/怎么看图) → ④ 行动建议(游戏/锻炼/陪伴，竖排，**正文无编号无「有据」**，编号与依据进附录) → ⑤ 详细分析(气质[首现标英文 Temperament]/社会情绪/发展快照/兴趣/学习品质/家庭) → ⑥ 综合画像 → ⑦ 边界+复测 → ⑧ 附录(建议来源+方法学)。
叙事铁律见 SKILL.md §0/§4（NEVER：把相对低说成缺陷 / 给 protected_high 写待发展 / 报百分位 / 诊断 / 臆造 id 或效果 / 单题当独立优劣 / 忽略 confidence）。

## 8. 怎么跑 skill
```bash
# 环境(换机一次): pip install jsonschema playwright ; playwright install chromium
python skill/scripts/score.py inbox/<日期>/<某份>.json -o work/profile.json
python skill/scripts/select_activities.py work/profile.json -o work/candidates.json
# 然后 Claude 据 profile+candidates+方法学撰写叙事、富化活动 → work/rco.json (范本 docs/sample-report/rco.json)
python skill/scripts/render.py work/rco.json --profile work/profile.json -o reports/{昵称-childid后8位-日期}/
# 批量: Glob inbox/**/*.json 逐份独立跑; 完成后原 JSON 移 processed/
# 无 chromium 时 render.py 加 --no-pdf (仍出 MD/HTML)
```

## 9. 版本约定（**三条独立版本线，别混**）
- `item_bank_version`（题库内容版本，现 **1.1.2**）：item-bank/index.html内联/sample-export/scoring-config.source/profile/方法学/蓝图 **全仓对齐**。
- `activity-bank.json.version`（活动库自身，现 **1.1.1**）：独立线。
- 导出 `schema_version`（导出契约，**1.1**）与 题库内联 `ITEM_BANK.schema_version`（**1.0** 向后兼容）：两条独立线。`consent_version`（**1.1**）。
- **改 item-bank.json 内容**：必须同步 index.html 内联 + sample-export + 问卷蓝图 + bump item_bank_version + 重跑 `validate_sample.py` 与 `test_scoring.py`。

## 10. 隐私/数据治理
- 问卷纯静态、无后端、零联网；儿童数据不经过/不存留任何服务器。
- 身份最小必要 + 昵称化；`child_id` = `cid-` + 随机 UUID（**单次会话标识、不跨次关联、非纵向追踪**；复测需人工按昵称对应）。
- **真实儿童数据绝不入库**（仓库是 public）：`inbox/ processed/ reports/ work/` 已 gitignore。

## 11. 发布前 TODO（不阻断给朋友用）
1. **FLAG-B 版权**：SEL 前三块(自我调节/主动性/依恋) ≈ DECA-P2 三保护因子「汇编同构」，已搁置；商业化/公开发布前定（方案见 `docs/许可与对齐边界表.md` B-1~B-4）。
2. PA×EF 元分析(MHPA 2024;100575) 作者名待补。
3. `docs/research/activities/A1-A8.md` 研究卡侧引文未与 activity-bank 对齐（活动库本体已对齐）。

## 12. 给在此工作的 agent 的操作约定（重要）
- **跑 Workflow 不要自动 git commit/push**：用户用 Max 套餐 auto mode（分类器逐操作判风险），「直接推 main」默认被拦、连拦会熔断退回逐操作询问。**工作流只写文件 + 末尾只读汇报变更；用户验收满意后才由人/单独命令 push。**
- 已配 `.claude/settings.local.json`（本地、gitignore）allow `Bash(git push:*)` 等窄规则，使「用户下令后那次推送」不弹。
- 多轮工作模式：**我判断哪些值得改 → 用户拍板 → 工作流落地(不碰git) → 用户定型 push**。

## 13. 深读文档
- 设计/方法：`docs/理论依据与方法学.md`、`docs/问卷蓝图.md`
- skill 运行/报告规范：`skill/SKILL.md`、`skill/PROFILE_SCHEMA.md`
- 数据契约：`docs/json-schema.md`、`schema/export.schema.json`
- 版权/引文：`docs/许可与对齐边界表.md`、`docs/source-legend.md`、`docs/引文对照表.md`
- 复核轨迹：`docs/review/`（R2/R3/R4 + 待办清单）
