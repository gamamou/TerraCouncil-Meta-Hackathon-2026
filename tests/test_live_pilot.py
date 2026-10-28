"""No external model calls: HACK-005 pilot safeguards."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from live_pilot import pilot

def evidence():
    return [{"evidence_id":"TEST-001","dataset":"Synthetic local test","source":"test",
             "observed_at":"2026-01-01","geography":"Boké, Guinea","method":"mock",
             "license":"test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"unit-test","finding":"Test-only observation, no scientific claim.",
             "sectors":["mining"]}]

def valid_text():
    return json.dumps({"observations":[{"evidence_id":"TEST-001",
               "finding":"Test-only observation, no scientific claim."}],
               "hypotheses":[], "investigations":["Investigate locally"],
               "abstentions":["No impact inference."]})

class PilotTests(unittest.TestCase):
    def test_default_no_calls(self):
        calls=[]
        x=pilot("What next?", evidence(), caller=lambda *a:calls.append(a))
        self.assertEqual(x["calls_attempted"],0)
        self.assertEqual(calls,[])

    def test_key_and_consent_gate(self):
        with self.assertRaises(ValueError):
            pilot("What next?",evidence(),execute=True,api_key="fake")
        with self.assertRaises(ValueError):
            pilot("What next?",evidence(),execute=True,share_approved=True)

    def test_mock_one_call(self):
        calls=[]
        def fake(*args):
            calls.append(args)
            return valid_text()
        x=pilot("What next?",evidence(),execute=True,share_approved=True,api_key="fake",caller=fake)
        self.assertEqual(len(calls),1)
        self.assertEqual(x["status"],"FIRST_META_RESPONSE_PASSED_STRUCTURAL_GATES")

    def test_mock_bad_claim_blocked(self):
        bad=json.loads(valid_text())
        bad["observations"][0]["finding"]="Mining impact confirmed"
        x=pilot("What next?",evidence(),execute=True,share_approved=True,api_key="fake",
                caller=lambda *a:json.dumps(bad))
        self.assertEqual(x["status"],"FIRST_META_RESPONSE_BLOCKED")

    def test_fail_no_retry(self):
        calls=[]
        def fail(*args):
            calls.append(args)
            raise RuntimeError("Test call failed")
        x=pilot("What next?",evidence(),execute=True,share_approved=True,api_key="fake",caller=fail)
        self.assertEqual(len(calls),1)
        self.assertEqual(x["status"],"CALL_FAILED_DO_NOT_RETRY_BLINDLY")

    def test_empty_records_zero_calls_even_if_execute(self):
        calls=[]
        x=pilot("What next?",[],execute=True,share_approved=True,api_key="fake",caller=lambda *args:calls.append(args))
        self.assertEqual(x["status"],"ABSTAIN_NO_USABLE_EVIDENCE")
        self.assertFalse(calls)

if __name__ == "__main__":
    unittest.main()
