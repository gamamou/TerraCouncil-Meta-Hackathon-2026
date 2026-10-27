"""HACK-003 structural verification tests; local fixtures only, zero model calls."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from verification import gate_evidence, verify_submission, evidence_hash
from verified_council import prepare, deliberate

def item(status="NOT_FIELD_VALIDATED", finding="Test-only mapped feature exists"):
    return {"evidence_id": "TEST-E-1", "dataset": "TEST_FIXTURE", "source": "LOCAL_TEST",
            "observed_at": "2026-01-01", "geography": "Boké, Guinea",
            "method": "synthetic fixture, not scientific evidence", "license": "test-only",
            "validation_status": status, "provenance": "test-function",
            "finding": finding, "sectors": ["mining"]}

def response(finding="Test-only mapped feature exists", eid="TEST-E-1"):
    return json.dumps({"observations": [{"evidence_id": eid, "finding": finding}],
                       "hypotheses": ["Possibly related; NOT demonstrated"],
                       "investigations": ["Verify on the ground"],
                       "abstentions": ["No impact claim is justified"]})

class VerificationTests(unittest.TestCase):
    def test_exploratory_without_status_upgrade(self):
        job = prepare("Which investigations?", [item()])
        self.assertEqual(job["status"], "EVIDENCE_READY_EXPLORATORY")
        self.assertEqual(job["gate"]["evidence"][0]["validation_status"], "NOT_FIELD_VALIDATED")

    def test_status_not_recognized_rejected(self):
        gate = gate_evidence([item("UNSUPPORTED")], "mining", "Boké, Guinea")
        self.assertEqual(gate["status"], "ABSTAIN_NO_USABLE_EVIDENCE")

    def test_geography_mismatch_abstains(self):
        gate = gate_evidence([item()], "mining", "Conakry, Guinea")
        self.assertEqual(gate["status"], "ABSTAIN_NO_USABLE_EVIDENCE")

    def test_incomplete_provenance_rejected(self):
        x = item(); x.pop("license")
        with self.assertRaises(ValueError):
            gate_evidence([x], "mining", "Boké, Guinea")

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            gate_evidence([item(), item()], "mining", "Boké, Guinea")

    def test_exact_finding_passes_only_structural_review(self):
        gate = gate_evidence([item()], "mining", "Boké, Guinea")
        result = verify_submission(response(), gate["evidence"], gate["evidence_sha256"])
        self.assertTrue(result["verified"])
        self.assertEqual(result["publication"]["observations"][0]["usage"], "exploratory_only")
        self.assertIn("HUMAN_REVIEW_REQUIRED", result["status"])

    def test_model_invented_finding_blocked(self):
        gate = gate_evidence([item()], "mining", "Boké, Guinea")
        result = verify_submission(response("Mining caused a health impact"), gate["evidence"], gate["evidence_sha256"])
        self.assertFalse(result["verified"])

    def test_model_invented_citation_blocked(self):
        gate = gate_evidence([item()], "mining", "Boké, Guinea")
        result = verify_submission(response(eid="UNKNOWN"), gate["evidence"], gate["evidence_sha256"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_fingerprint_tamper_blocked(self):
        gate = gate_evidence([item()], "mining", "Boké, Guinea")
        result = verify_submission(response(), gate["evidence"], "not-the-real-hash")
        self.assertEqual(result["status"], "BLOCKED_EVIDENCE_CHANGED")

    def test_extra_unchecked_field_blocked(self):
        gate = gate_evidence([item()], "mining", "Boké, Guinea")
        payload = json.loads(response()); payload["claim_of_impact"] = "confirmed"
        result = verify_submission(payload, gate["evidence"], gate["evidence_sha256"])
        self.assertFalse(result["verified"])

    def test_no_model_call_without_evidence(self):
        job = prepare("Why?", [])
        calls = []
        result = deliberate(job, "mock", lambda *args: calls.append(args))
        self.assertEqual(result["calls_attempted"], 0)
        self.assertEqual(calls, [])

    def test_bad_agent_blocked_before_critic(self):
        job = prepare("Question", [item()])
        calls = []
        def bad(model, instruction, payload, key):
            calls.append(model)
            return response(finding="False measurement")
        result = deliberate(job, "mock", bad)
        self.assertEqual(result["status"], "BLOCKED_BY_INDEPENDENT_VERIFIER")
        self.assertEqual(len(calls), 1)

    def test_mocked_full_flow_needs_human_review(self):
        job = prepare("Question", [item()])
        calls = []
        def good(model, instruction, payload, key):
            calls.append(model)
            return response()
        result = deliberate(job, "mock", good)
        self.assertEqual(result["status"], "STRUCTURALLY_VERIFIED_HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["calls_attempted"], job["model_calls_planned"])
        self.assertEqual(calls[-2:], ["muse-wonder-1.0", "muse-spark-1.3"])

if __name__ == "__main__":
    unittest.main()
