import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from council import plan, validate_evidence, run_council, fingerprint

def evidence(status="ADMISSIBLE"):
    return {"evidence_id": "E-001", "dataset": "TEST-ONLY", "source": "TEST",
            "observed_at": "2026-01-01", "geography": "Boke", "method": "fixture",
            "license": "test-only", "validation_status": status, "provenance": "fixture",
            "finding": "A test-only finding, not an FSDC scientific conclusion",
            "sectors": ["mining"]}

class CouncilTests(unittest.TestCase):
    def test_absent_evidence_abstains(self):
        self.assertEqual(plan("What next?", "mining", [])["status"], "ABSTAIN_NO_ADMISSIBLE_EVIDENCE")

    def test_unvalidated_evidence_abstains(self):
        self.assertEqual(plan("What next?", "mining", [evidence("NOT_FIELD_VALIDATED")])["model_calls_planned"], 0)

    def test_cross_sector_rejected(self):
        self.assertFalse(validate_evidence([evidence()], "energy"))

    def test_missing_provenance_rejected(self):
        invalid = evidence()
        del invalid["license"]
        with self.assertRaises(ValueError):
            validate_evidence([invalid], "mining")

    def test_selected_agents_and_critic(self):
        job = plan("What next?", "mining", [evidence()])
        self.assertEqual(job["status"], "READY")
        self.assertEqual(job["critic"], "scientific_critic")
        self.assertLessEqual(len(job["proposers"]), 4)

    def test_mocked_calls_and_models(self):
        job = plan("What next?", "mining", [evidence()])
        calls = []
        def fake(model, instructions, payload, key):
            calls.append(model)
            return "fixture only"
        result = run_council(job, "test-key-not-live", fake)
        self.assertEqual(result["status"], "GENERATED_UNVERIFIED")
        self.assertEqual(len(calls), job["model_calls_planned"])
        self.assertEqual(calls[-2:], ["muse-wonder-1.0", "muse-spark-1.3"])

    def test_refuse_no_evidence_even_with_key(self):
        with self.assertRaises(ValueError):
            run_council(plan("Why?", "mining", []), "mock", lambda *args: None)

if __name__ == "__main__":
    unittest.main()
