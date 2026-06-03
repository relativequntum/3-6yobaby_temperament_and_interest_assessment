# tests/ — 金标准样例一致性门禁 (T-6)

本目录把「金标准样例 `questionnaire/sample-export.json` 必须与题库
`docs/item-bank.json` 及导出契约 `schema/export.schema.json` 保持一致」
固化为一个可执行校验脚本，可用于本地自查或接入 CI / pre-commit。

## 脚本

- `validate_sample.py` —— 对样例做四项断言：
  - **(a)** 样例通过 `schema/export.schema.json`（JSON Schema **draft 2020-12**，
    用 Python `jsonschema.Draft202012Validator`）。
  - **(b)** 每条 `response.anchor_shown` ∈ 对应题 `anchors_by_band[response.age_band]` ∪ `{null}`
    （杜绝杜撰锚点）。
  - **(c)** 每条 `response.question_text` 与题库对应题 `text` **逐字一致**
    （开放题 `open_ended` 的题干同样校验）。
  - **(d)** 每条 `response` 的 `cluster` / `report_subscale` / `consistency_pair_id`
    与题库一致（题库缺该键时按 `null` 处理，与前端 `buildExport` 口径一致）。

题库事实源采用 `docs/item-bank.json`（完整含题干/锚点/簇/配对；
`questionnaire/index.html` 内联的是它的副本）。

## 依赖

- Python 3.8+
- `jsonschema`（>= 4，支持 draft 2020-12）。本机已随 Python 环境提供；
  如缺失：`python -m pip install jsonschema`
- 无需联网，纯本地运行。

## 运行

在仓库任意目录下（脚本自带相对定位）：

```bash
python tests/validate_sample.py
```

Windows PowerShell：

```powershell
python .\tests\validate_sample.py
# 或 py .\tests\validate_sample.py
```

- **退出码 0**：全部通过（打印 `T-6 PASS`）。
- **退出码 1**：存在不一致，逐条打印 `[FAIL] ...`（含 item_id、字段、样例值与题库值对照）。

## 重新生成金标准样例

样例由真实问卷 `questionnaire/index.html` 的 `buildExport()` 产出（4 岁、出生月
约 `2021-12` → 年龄段 `4-5`）。若题库/契约变更，请按当时方法用 Playwright 复用
本机 Chromium、经 `file://` 加载 `index.html` 完整作答后导出覆盖本样例，再运行本门禁确认通过。
