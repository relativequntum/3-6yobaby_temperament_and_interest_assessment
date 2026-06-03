#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-6 一致性门禁 (consistency gate).

断言金标准样例 questionnaire/sample-export.json 与题库 docs/item-bank.json、
契约 schema/export.schema.json 完全一致：

  (a) sample-export.json 通过 schema/export.schema.json (JSON Schema draft 2020-12,
      用 python 的 jsonschema.Draft202012Validator)。
  (b) 每条 response 的 anchor_shown ∈ 对应题 anchors_by_band[该题 age_band] ∪ {null}。
  (c) 每条 response 的 question_text == 题库对应题 text（逐字）。
  (d) 每条 response 的 cluster / report_subscale / consistency_pair_id 与题库一致
      （题库缺该键时按 null 处理）。

对正常样例应全部通过 (exit 0)。任何不一致都会汇总打印并以 exit 1 失败，
适合放进 CI / pre-commit 作为门禁。

依赖：仅标准库 + jsonschema (>=4, 已随 Python 环境提供，离线可用)。
运行：见同目录 README.md。
"""

import json
import os
import sys

# ---- 路径（相对脚本定位，可从任意 cwd 运行）-------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLE = os.path.join(ROOT, "questionnaire", "sample-export.json")
SCHEMA = os.path.join(ROOT, "schema", "export.schema.json")
BANK = os.path.join(ROOT, "docs", "item-bank.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_bank_index(bank):
    """item_id -> 题库题对象。OPEN 题也收进来（开放题只查 text）。"""
    idx = {}
    for section in bank.get("sections", []):
        for item in section.get("items", []):
            idx[item["id"]] = item
    return idx


def main():
    errors = []

    # ---- 文件存在性 -------------------------------------------------------
    for label, path in (("sample", SAMPLE), ("schema", SCHEMA), ("item-bank", BANK)):
        if not os.path.isfile(path):
            errors.append("找不到 %s 文件: %s" % (label, path))
    if errors:
        for e in errors:
            print("[FAIL]", e)
        return 1

    sample = load_json(SAMPLE)
    schema = load_json(SCHEMA)
    bank = load_json(BANK)
    bank_idx = build_bank_index(bank)

    # ---- (a) schema 校验 (draft 2020-12) ----------------------------------
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("[FAIL] 缺少 jsonschema 库。请先安装：python -m pip install jsonschema")
        return 1

    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(sample), key=lambda e: list(e.path))
    if schema_errors:
        for e in schema_errors:
            loc = "/".join(str(p) for p in e.path) or "(root)"
            errors.append("(a) schema 不通过 @ %s : %s" % (loc, e.message))
    else:
        print("[OK] (a) schema(draft2020-12) 校验通过")

    # ---- 逐条 response 检查 (b)(c)(d) -------------------------------------
    ab_err = ct_err = field_err = 0
    for r in sample.get("responses", []):
        iid = r.get("item_id")
        item = bank_idx.get(iid)
        if item is None:
            errors.append("题库中找不到题目 %s（样例引用了不存在的题）" % iid)
            continue

        # (c) question_text 逐字一致
        if r.get("question_text") != item.get("text"):
            ct_err += 1
            errors.append(
                "(c) %s question_text 与题库 text 不一致:\n     样例: %r\n     题库: %r"
                % (iid, r.get("question_text"), item.get("text"))
            )

        # (b) anchor_shown ∈ anchors_by_band[age_band] ∪ {null}
        band = r.get("age_band")
        anchors = item.get("anchors_by_band")  # 可能为 None
        allowed = set()
        if isinstance(anchors, dict):
            v = anchors.get(band)
            if v is not None:
                allowed.add(v)
        anchor_shown = r.get("anchor_shown")
        if anchor_shown is not None and anchor_shown not in allowed:
            ab_err += 1
            errors.append(
                "(b) %s anchor_shown 不在 anchors_by_band[%s]∪{null} 内:\n     anchor_shown: %r\n     允许集: %r"
                % (iid, band, anchor_shown, sorted(allowed))
            )

        # (d) cluster / report_subscale / consistency_pair_id 与题库一致
        #     题库缺该键时按 null 处理（与前端 buildExport 的 x!==undefined?x:null 一致）。
        for key in ("cluster", "report_subscale", "consistency_pair_id"):
            bank_val = item.get(key, None)
            samp_val = r.get(key, None)
            if samp_val != bank_val:
                field_err += 1
                errors.append(
                    "(d) %s 字段 %s 与题库不一致: 样例=%r 题库=%r"
                    % (iid, key, samp_val, bank_val)
                )

    if ab_err == 0:
        print("[OK] (b) 所有 anchor_shown 均属对应题本龄段锚点∪{null}")
    if ct_err == 0:
        print("[OK] (c) 所有 question_text 与题库 text 逐字一致")
    if field_err == 0:
        print("[OK] (d) 所有 cluster/report_subscale/consistency_pair_id 与题库一致")

    # ---- open_ended 的 question_text 也对题库逐字校验（属(c)语义延伸）------
    for o in sample.get("open_ended", []):
        iid = o.get("item_id")
        item = bank_idx.get(iid)
        if item is None:
            errors.append("题库中找不到开放题 %s" % iid)
        elif o.get("question_text") != item.get("text"):
            errors.append(
                "(c) 开放题 %s question_text 与题库 text 不一致:\n     样例: %r\n     题库: %r"
                % (iid, o.get("question_text"), item.get("text"))
            )

    # ---- 汇总 -------------------------------------------------------------
    if errors:
        print("\n==== 校验失败，共 %d 处问题 ====" % len(errors))
        for e in errors:
            print("[FAIL]", e)
        return 1

    print("\n==== 全部通过：样例与题库/契约一致 (T-6 PASS) ====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
