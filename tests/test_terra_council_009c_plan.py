"""009C tests: prove chair flow and refusal without scientific evidence."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from terra_council_009_route import propose_route
from terra_council_009c_plan import compile_plan

class CouncilPlanTests(unittest.TestCase):
    def setUp(self):
        self.route = propose_route("Quels risques ESG pour une mine de bauxite à Boké ?")
        self.evidence = [{"evidence_id":"FSDC-DEMO-001","source_version":"test-1",
                          "claim":"Synthetic fixture, not real-world evidence",
                          "evidence_status":"VERIFIED"}]

    def test_no_evidence_refused(self):
        with self.assertRaises(ValueError):
            compile_plan(self.route, [])

    def test_chair_opens_and_closes(self):
        plan=compile_plan(self.route,self.evidence)
        self.assertEqual(plan["steps"][0]["phase"], "opening")
        self.assertEqual(plan["steps"][-1]["phase"], "deliberation")
        self.assertEqual(plan["steps"][0]["role"], "scientific_chair")

    def test_dynamic_roles(self):
        plan=compile_plan(self.route,self.evidence)
        self.assertIn("esg",plan["active_experts"])
        self.assertNotIn("agriculture",plan["active_experts"])

    def test_no_service_is_called(self):
        plan=compile_plan(self.route,self.evidence)
        self.assertEqual(plan["muse_calls_executed"],0)
        self.assertFalse(plan["audio_authorized"])
        self.assertFalse(plan["pdf_authorized"])

    def test_unverified_evidence_refused(self):
        invalid=[{**self.evidence[0], "evidence_status":"LIMITED"}]
        with self.assertRaises(ValueError):
            compile_plan(self.route,invalid)

    def test_duplicate_ids_refused(self):
        with self.assertRaises(ValueError):
            compile_plan(self.route,self.evidence*2)

if __name__=="__main__":
    unittest.main()
