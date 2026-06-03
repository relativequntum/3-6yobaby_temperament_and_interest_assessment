#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""score.py 的单元测试（纯标准库 unittest）。

覆盖 T-11 与计分契约六条：
  ①同一 cluster 成员同时高 → 只产生 1 个合并指标、不出现多个独立优势；
  ②单题子维度不进基线/不排序；
  ③全高分样例 → 不出现假性「劣势/待发展」、不全维齐涨、growth 对原始高项为空或仅带「仍很常见」；
  ④反向题翻转正确；
  ⑤like5/freq5 分基线；
  ⑥缺字段/越界/越龄段输入的稳健处理。

并用 sample-export.json 与构造样例（全高/全低/全同/极端）跑通。

运行：
    python -m unittest skill/tests/test_scoring.py -v
或   python skill/tests/test_scoring.py
"""

import copy
import json
import os
import sys
import unittest

_THIS = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "skill", "scripts"))

import score  # noqa: E402

CONFIG = json.load(
    open(os.path.join(REPO_ROOT, "skill", "scoring", "scoring-config.json"), encoding="utf-8")
)
SCHEMA = json.load(
    open(os.path.join(REPO_ROOT, "schema", "export.schema.json"), encoding="utf-8")
)
SAMPLE = json.load(
    open(os.path.join(REPO_ROOT, "questionnaire", "sample-export.json"), encoding="utf-8")
)


# ---------------------------------------------------------------------------
# 构造工具：基于真实样例造「全高/全低/全同」等极端输入
# ---------------------------------------------------------------------------
def _build_export(value_fn, band="4-5", quality_overrides=None, identity=None):
    """以 sample-export 结构为模板，按 value_fn(resp)->raw_value 重写每题作答。

    freq5/like5 的 value 用 1-5；single/multi 保留原值（FAM 不计分）。
    自动放慢计时以避免 fast_response 干扰置信度测试。
    """
    exp = copy.deepcopy(SAMPLE)
    exp["age_band"] = band
    for resp in exp["responses"]:
        if resp["scale"] in ("freq5", "like5"):
            resp["raw_value"] = value_fn(resp)
    # 放慢计时：每题 ~6 秒，避免 fast_response
    n = len(exp["responses"])
    exp["meta"]["timing"]["total_active_sec"] = n * 6
    exp["meta"]["timing"]["per_section_sec"] = {
        k: max(1, n) for k in exp["meta"]["timing"]["per_section_sec"]
    }
    # 关闭前端预置旗标，专测 skill 侧逻辑
    q = exp["meta"]["quality"]
    q["straightlining_flag"] = False
    q["fast_response_flag"] = False
    q["high_missing_flag"] = False
    q["inconsistency_flag"] = False
    q["longstring_max"] = 1
    if quality_overrides:
        q.update(quality_overrides)
    if identity is not None:
        exp["_identity_extra"] = identity
    return exp


def all_value(v):
    return lambda resp: v


def oriented_high(resp):
    """让“同向后高”的样例：正向题给 5，反向题给 1（翻转后=5）。"""
    return 1 if resp.get("reverse") else 5


def oriented_low(resp):
    """同向后低：正向题给 1，反向题给 5（翻转后=1）。"""
    return 5 if resp.get("reverse") else 1


def run(export):
    return score.score_export(export, CONFIG, SCHEMA)


# ---------------------------------------------------------------------------
class TestSchemaAndSample(unittest.TestCase):
    def test_sample_validates_and_scores(self):
        prof = run(SAMPLE)
        self.assertIn("sections", prof)
        self.assertIn("clusters", prof)
        self.assertEqual(prof["meta"]["nickname"], "豆豆")
        # 5 个簇全部产出
        self.assertEqual(len(prof["clusters"]), 5)
        # 反向题 14 道全部记录
        self.assertEqual(len(prof["reverse_applied"]), 14)

    def test_determinism(self):
        a = json.dumps(run(SAMPLE), ensure_ascii=False, sort_keys=True)
        b = json.dumps(run(copy.deepcopy(SAMPLE)), ensure_ascii=False, sort_keys=True)
        self.assertEqual(a, b)


# ---------------------------------------------------------------------------
class TestClusterMerge(unittest.TestCase):
    """① 同一 cluster 成员同时高 → 只产生 1 个合并指标，不拆成多个独立优势。"""

    def test_single_merged_metric_per_cluster(self):
        # 让 focus_persistence 全部成员同向后=5（明显最高）
        fp_members = set(CONFIG["clusters"]["focus_persistence"]["members"])

        def vfn(resp):
            iid = resp["item_id"]
            if iid in fp_members:
                return oriented_high(resp)
            return 3 if not resp.get("reverse") else 3

        prof = run(_build_export(vfn))
        clusters = [c for c in prof["clusters"] if c["cluster"] == "focus_persistence"]
        # 恰好一个合并指标
        self.assertEqual(len(clusters), 1)
        self.assertTrue(clusters[0]["merged_single_metric"])
        self.assertTrue(clusters[0]["counts_in_baseline_once"])

        # 优势列表里 focus_persistence 只出现一次，且不以 TMP/LRN/INT 子条目重复
        strength_names = [s["name"] for s in prof["relative_strengths_top"]]
        self.assertEqual(strength_names.count("专注-坚持"), 1)
        # 不得把簇成员所在子维度也单列为独立优势（优势条目里没有任何 cluster 重复名）
        cluster_refs = [s["ref"] for s in prof["relative_strengths_top"] if s["kind"] == "cluster"]
        self.assertEqual(len(cluster_refs), len(set(cluster_refs)))

    def test_baseline_counts_cluster_once(self):
        """基线单位中每个簇只占一席（不按题量放大）。"""
        prof = run(SAMPLE)
        units = prof["baseline"]["n_units"]
        cluster_units = [u for u in units if u["kind"] == "cluster"]
        ids = [u["id"] for u in cluster_units]
        self.assertEqual(len(ids), len(set(ids)))
        # 5 个簇都在样例中有题 → 5 个簇单位
        self.assertEqual(set(ids), set(CONFIG["clusters"].keys()))


# ---------------------------------------------------------------------------
class TestSingleItemHandling(unittest.TestCase):
    """② 单题子维度不进基线、不排序。"""

    def test_standalone_excluded_from_baseline(self):
        prof = run(SAMPLE)
        units = prof["baseline"]["n_units"]
        # TMP-03/04/05 所在子维度（社交接近/害羞慢热/趋避适应）不得作为基线单位
        standalone_subscales = {"社交接近", "害羞/慢热", "趋避/适应"}
        for u in units:
            if u["kind"] == "subscale":
                self.assertNotIn(u["id"][1], standalone_subscales)

    def test_subscales_never_ranked(self):
        prof = run(SAMPLE)
        for sub in prof["subscales"]:
            self.assertFalse(sub["ranked"])
            self.assertEqual(sub["caveat"], CONFIG["aggregation"]["subscale_caveat"])
        # standalone 单题子维度标记为剔除基线
        flagged = [s for s in prof["subscales"] if s["standalone_single_item"]]
        self.assertTrue(all(s["excluded_from_baseline"] for s in flagged))


# ---------------------------------------------------------------------------
class TestReverse(unittest.TestCase):
    """④ 反向题翻转正确。"""

    def test_flip_formula(self):
        self.assertEqual(score.Scorer.flip("freq5", 1), 5)
        self.assertEqual(score.Scorer.flip("freq5", 5), 1)
        self.assertEqual(score.Scorer.flip("like5", 2), 4)
        # 非数值/非 5 点不翻转
        self.assertEqual(score.Scorer.flip("single", "many"), "many")

    def test_reverse_then_oriented_high(self):
        """反向题原始=1，翻转后应为 5；该题应被记录在 reverse_applied。"""
        exp = _build_export(oriented_high)  # 正向5/反向1 → 同向全 5
        prof = run(exp)
        for rec in prof["reverse_applied"]:
            self.assertEqual(rec["oriented"], 6 - rec["raw_value"])
        # 同向全 5 → 每个簇合并均值=5.0
        for c in prof["clusters"]:
            self.assertAlmostEqual(c["raw_mean"], 5.0, places=3)

    def test_reverse_consistency_pair_detection(self):
        """一致性配对：正反向题“同方向”地填（都填高原始值）→ 同向化后矛盾。"""
        # SEL-08 正向填5、SEL-09 反向填5（翻转后=1）→ 一致；
        # 这里反过来制造矛盾：cp 两题原始都填极端但语义相反
        exp = _build_export(all_value(3))
        for resp in exp["responses"]:
            if resp["item_id"] == "SEL-08":  # 正向
                resp["raw_value"] = 5
            if resp["item_id"] == "SEL-09":  # 反向，填 5 → 翻转后 1，与 5 差 4
                resp["raw_value"] = 5
        prof = run(exp)
        self.assertTrue(prof["data_quality"]["flags"]["inconsistency"])


# ---------------------------------------------------------------------------
class TestLike5Freq5Separation(unittest.TestCase):
    """⑤ like5（兴趣领域）与 freq5（行为）分基线，禁止跨量表合并。"""

    def test_like5_not_in_freq5_baseline(self):
        # 把 8 个 like5 领域全部抬到 5，freq5 全填 3。
        def vfn(resp):
            if resp["scale"] == "like5":
                return 5
            return oriented_low(resp) if False else 3

        exp = _build_export(vfn)
        prof = run(exp)
        # 基线只应反映 freq5≈3，而非被 like5=5 抬高
        self.assertLess(prof["baseline"]["freq5_person_mean"], 3.5)
        self.assertGreater(prof["baseline"]["freq5_person_mean"], 2.5)
        # 基线单位中不含 INT-01..08 任何 like5 子维度
        like_subs = {CONFIG["items"][f"INT-0{i}"]["report_subscale"] for i in range(1, 9)}
        for u in prof["baseline"]["n_units"]:
            if u["kind"] == "subscale":
                self.assertNotIn(u["id"][1], like_subs)

    def test_interest_map_separate_ranking(self):
        prof = run(SAMPLE)
        imap = prof["interest_map"]["domains"]
        self.assertEqual(len(imap), 8)
        ranks = [d["rank"] for d in imap]
        self.assertEqual(sorted(ranks), list(range(1, 9)))
        # 排名按原始喜爱度降序
        likes = [d["like5_raw"] for d in imap]
        self.assertEqual(likes, sorted(likes, reverse=True))


# ---------------------------------------------------------------------------
class TestT11Guard(unittest.TestCase):
    """③ + T-11 核心：全高分样例的人为低点防护。"""

    def setUp(self):
        self.exp_high = _build_export(oriented_high)  # 同向全 5
        self.prof_high = run(self.exp_high)

    def test_all_high_no_false_weakness(self):
        # 所有 section / cluster 原始 band 都应为「高」
        for s in self.prof_high["sections"]:
            self.assertEqual(s["raw_band"]["level"], "高")
        for c in self.prof_high["clusters"]:
            self.assertEqual(c["raw_band"]["level"], "高")

    def test_all_high_growth_empty_of_protected(self):
        """全高分 → growth_areas.items 不得含任何原始高项；应为空或仅防护标记。"""
        growth = self.prof_high["growth_areas_top"]
        # 实际 growth items 必须为空（因为没有任何“原始非高”的相对低项）
        self.assertEqual(growth["items"], [])
        # 任何相对偏低项都应进入 protected_high_relative_low，并带“仍很常见”措辞
        for p in growth["protected_high_relative_low"]:
            self.assertEqual(p["raw_band"]["level"], "高")
            self.assertIn("仍很常见", p["note"])

    def test_all_high_no_growth_label_on_high(self):
        """全高分 → 任何 section/cluster 都不得出现「相对还在发展中」(劣势式) 标签。"""
        labels = [s["relative_label"] for s in self.prof_high["sections"]]
        labels += [c["relative_label"] for c in self.prof_high["clusters"]]
        self.assertNotIn("相对还在发展中", labels)
        # 相对偏低的高分项只能是保护性措辞
        for s in self.prof_high["sections"] + self.prof_high["clusters"]:
            if s["within_child_relative"] is not None and s["within_child_relative"] <= -0.30:
                self.assertEqual(s["relative_label"], "相对没那么突出但仍很常见")

    def test_not_all_dimensions_inflated(self):
        """不全维齐涨：即便全高，中心化后仍有分化（相对位有正有负或为零）。"""
        rels = [c["within_child_relative"] for c in self.prof_high["clusters"]]
        # 中心化保证均值≈0，不可能全为正
        self.assertTrue(any(r <= 0 for r in rels) or all(abs(r) < 1e-6 for r in rels))

    def test_all_same_flat_profile(self):
        """全同分（同向全 3）→ 相对位全 0，无任何项被误标劣势。"""
        exp = _build_export(all_value(3))
        prof = run(exp)
        for c in prof["clusters"]:
            self.assertAlmostEqual(c["within_child_relative"], 0.0, places=2)
        self.assertEqual(prof["growth_areas_top"]["items"], [])

    def test_all_low_growth_allowed_not_diagnostic(self):
        """全低分 → growth 可有内容，但措辞非诊断；不触发临床结论。"""
        exp = _build_export(oriented_low)  # 同向全 1
        prof = run(exp)
        for c in prof["clusters"]:
            self.assertEqual(c["raw_band"]["level"], "低")
        # 全低且全同 → 相对位≈0，growth.items 仍为空（无分化）
        self.assertEqual(prof["growth_areas_top"]["items"], [])
        # notes 始终含非诊断声明
        self.assertTrue(any("非诊断" in n for n in prof["notes"]))


# ---------------------------------------------------------------------------
class TestExtremeAndRobustness(unittest.TestCase):
    """⑥ 缺字段/越界/越龄段/极端输入稳健处理。"""

    def test_missing_responses_robust(self):
        exp = _build_export(all_value(4))
        # 让部分 freq5 题未作答（raw_value=null）
        cleared = 0
        for resp in exp["responses"]:
            if resp["scale"] == "freq5" and cleared < 5:
                resp["raw_value"] = None
                resp["value_label"] = ""
                cleared += 1
        prof = run(exp)  # 不应抛异常
        self.assertIn("sections", prof)
        self.assertGreaterEqual(prof["data_quality"]["flags"]["missing_ratio"], 0.0)

    def test_out_of_range_band_fallback(self):
        exp = _build_export(all_value(4), band="4-5")
        exp["age_band"] = "out_of_range"
        exp["child"]["age_months_at_submit"] = 80  # 超过 5-6 上限 → 回退 5-6
        prof = run(exp)
        self.assertEqual(prof["meta"]["age_band"], "out_of_range")
        # notes 含越界提示
        self.assertTrue(any("越界" in n for n in prof["notes"]))
        # 仍产出 section
        self.assertTrue(len(prof["sections"]) >= 1)

    def test_extreme_high_missing_flag(self):
        exp = _build_export(all_value(4))
        # 清空过半 freq5 → high_missing
        for resp in exp["responses"]:
            if resp["scale"] == "freq5":
                resp["raw_value"] = None
        prof = run(exp)
        self.assertTrue(prof["data_quality"]["flags"]["high_missing"])
        # 高缺答 → 置信度不为 high
        self.assertNotEqual(prof["data_quality"]["confidence"], "high")

    def test_familiarity_low_lowers_confidence(self):
        exp = _build_export(all_value(4), identity={"relationship": "other_caregiver", "daily_contact": "lt1"})
        prof = run(exp)
        self.assertTrue(prof["data_quality"]["flags"]["familiarity_low"])
        self.assertIn(prof["data_quality"]["confidence"], ("med", "low"))

    def test_bad_input_raises(self):
        with self.assertRaises(score.ScoringError):
            score.score_export([], CONFIG, SCHEMA)  # 非对象
        with self.assertRaises(score.ScoringError):
            # schema 校验失败：删除必填字段
            broken = copy.deepcopy(SAMPLE)
            del broken["consent"]
            score.score_export(broken, CONFIG, SCHEMA)

    def test_unknown_item_ignored(self):
        exp = _build_export(all_value(4))
        # 注入一个配置未登记的题（仍满足 schema 的 response 结构）
        ghost = copy.deepcopy(exp["responses"][0])
        ghost["item_id"] = "ZZZ-99"
        exp["responses"].append(ghost)
        prof = run(exp)  # 不应崩溃；ZZZ-99 被忽略
        self.assertIn("clusters", prof)


# ---------------------------------------------------------------------------
class TestRedFlags(unittest.TestCase):
    def test_red_flag_triggers_on_dev_floor(self):
        """DEV 某领域全部原始=1 且数据可信、熟悉度高 → 触发温和软转介。"""
        exp = _build_export(all_value(4), identity={"relationship": "mother", "daily_contact": "gt6"})
        # 把 DEV 沟通/语言 (DEV-01..03) 全部置最低档=1
        for resp in exp["responses"]:
            if resp["item_id"] in ("DEV-01", "DEV-02", "DEV-03"):
                resp["raw_value"] = 1
        prof = run(exp)
        kinds = [rf["type"] for rf in prof["red_flags"]]
        self.assertIn("soft_referral", kinds)
        rf = next(r for r in prof["red_flags"] if r["type"] == "soft_referral")
        self.assertTrue(rf["non_diagnostic"])
        # 红线：措辞中绝不含诊断词
        for word in ("自闭", "发育迟缓", "多动"):
            self.assertNotIn(word, rf["wording"])

    def test_red_flag_suppressed_when_familiarity_low(self):
        exp = _build_export(all_value(4), identity={"relationship": "other_caregiver", "daily_contact": "lt1"})
        for resp in exp["responses"]:
            if resp["item_id"] in ("DEV-01", "DEV-02", "DEV-03"):
                resp["raw_value"] = 1
        prof = run(exp)
        # 熟悉度低 → 保守不触发
        self.assertEqual(prof["red_flags"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
