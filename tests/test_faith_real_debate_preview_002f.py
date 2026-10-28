"""TERRA-DATA-002F: no model or extra empirical claims in previews."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_real_debate_preview_002f import preview

class RealDebatePreviewTests(unittest.TestCase):
    def test_no_evidence_abstains(self):
        r=preview([],"multidomain")
        self.assertEqual(r["evidence_count"],0)
        self.assertTrue(r["plan"]["status"].startswith("ABSTAIN"))
        self.assertEqual(r["model_calls_executed"],0)
        self.assertEqual(r["external_requests_executed"],0)
    def test_climate_point_not_pilot_evidence(self):
        r=preview([],"climate")
        self.assertTrue(r["climate_context"]["outside_pilot"])
        self.assertTrue(r["climate_context"]["not_citable_for_pilot"])
    def test_all_questions_preserve_exclusion(self):
        for scenario in ("land","multidomain","climate"):
            with self.subTest(scenario=scenario):
                r=preview([],scenario)
                self.assertEqual(r["evidence_count"],0)
                self.assertTrue(r["climate_context"]["not_citable_for_pilot"])
    def test_reject_unknown_scenario(self):
        with self.assertRaises(ValueError):
            preview([],"fabricated")
    def test_reject_nonlist_evidence(self):
        with self.assertRaises(ValueError):
            preview({"finding":"fake"},"land")

if __name__=="__main__":
    unittest.main()
