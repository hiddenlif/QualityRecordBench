from copy import deepcopy
import unittest
from qrb.generate import make_pack
from qrb.grade import InvalidSubmission, score, read_submission
from qrb.reference import review
from tempfile import TemporaryDirectory
from pathlib import Path


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.cases, gold = make_pack(34)
        self.gold = {"case_set_sha256": "unit-test", "reviews": gold}
        self.answer = {"reviews": [review(c) for c in self.cases]}

    def test_independent_reference_over_seeds(self):
        for seed in range(30):
            with self.subTest(seed=seed):
                cases, labels = make_pack(seed)
                got = score({"case_set_sha256": "test", "reviews": labels},
                            {"reviews": [review(c) for c in cases]})
                self.assertEqual(got["exact_matches"], 12)

    def test_fixed_seed_and_order_independence(self):
        self.assertEqual(make_pack(34), make_pack(34))
        self.assertNotEqual(make_pack(34)[0], make_pack(35)[0])
        revised = deepcopy(self.answer)
        revised["reviews"].reverse()
        for r in revised["reviews"]:
            r["findings"].reverse()
        self.assertEqual(score(self.gold, revised)["exact_matches"], 12)

    def test_no_work_and_always_hold(self):
        self.assertEqual(score(self.gold, {"reviews": []})["exact_matches"], 0)
        held = {"reviews": [dict(case_id=r["case_id"], decision="HOLD", findings=[])
                            for r in self.answer["reviews"]]}
        scored = score(self.gold, held)
        self.assertEqual((scored["decisions_correct"], scored["exact_matches"]), (9, 0))

    def test_always_ready_yields_only_clean_controls(self):
        ready = {"reviews": [dict(case_id=r["case_id"], decision="READY", findings=[])
                             for r in self.answer["reviews"]]}
        self.assertEqual(score(self.gold, ready)["exact_matches"], 3)

    def test_right_label_wrong_evidence_gets_no_case_credit(self):
        altered = deepcopy(self.answer)
        wrong = next(r for r in altered["reviews"] if r["findings"])
        case = next(c for c in self.cases if c["case_id"] == wrong["case_id"])
        decoy = next(row for row in case["evidence"] if row["entity"] != case["index"]["subject_id"])
        wrong["findings"][0]["evidence_id"] = decoy["evidence_id"]
        s = score(self.gold, altered)
        self.assertEqual((s["decisions_correct"], s["exact_matches"]), (12, 11))

    def test_extra_guesses_fail_exactness(self):
        altered = deepcopy(self.answer)
        wrong = next(r for r in altered["reviews"] if r["findings"])
        wrong["findings"].append({"code": "UNSUPPORTED", "evidence_id": "E-guessed"})
        self.assertEqual(score(self.gold, altered)["exact_matches"], 11)

    def test_duplicate_ids_and_findings_rejected(self):
        duplicate = deepcopy(self.answer)
        duplicate["reviews"][1] = duplicate["reviews"][0]
        with self.assertRaises(InvalidSubmission):
            score(self.gold, duplicate)
        duplicate = deepcopy(self.answer)
        item = next(r for r in duplicate["reviews"] if r["findings"])
        item["findings"].append(item["findings"][0])
        with self.assertRaises(InvalidSubmission):
            score(self.gold, duplicate)

    def test_duplicate_json_and_oversized_submissions_rejected(self):
        with TemporaryDirectory() as path:
            f = Path(path) / "bad.json"
            for raw in ('{"reviews":[],"reviews":[]}', " " * (256 * 1024 + 1)):
                f.write_text(raw)
                with self.assertRaises(InvalidSubmission):
                    read_submission(f)

    def test_one_fact_flips_each_workflow(self):
        for workflow, row_kind, field, value, expected_code in [
            ("BATCH_RECORD", "execution", "executed_revision", "r0", "BATCH_REVISION"),
            ("QC_SUMMARY", "summary", "count", -1, "QC_COUNT"),
            ("DEVIATION_PACKAGE", "closure", "closed_at", "2026-10-01T00:00:00Z", "DEV_EARLY_CLOSURE"),
        ]:
            c = deepcopy(next(c for c in self.cases if c["workflow"] == workflow and not review(c)["findings"]))
            self.assertEqual(review(c)["decision"], "READY")
            row = next(r for r in c["evidence"] if r["kind"] == row_kind and r["entity"] == c["index"]["subject_id"])
            row[field] = value
            self.assertEqual(review(c), dict(case_id=c["case_id"], decision="HOLD",
                                            findings=[dict(code=expected_code, evidence_id=row["evidence_id"])]))


if __name__ == "__main__":
    unittest.main()
