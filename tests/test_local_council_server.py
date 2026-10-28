"""HACK-008: no-cost tests of local question orchestration and mandatory gates."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from local_council_server import make_plan, perform_run

def evidence():
    return [{"evidence_id":"TEST-008","dataset":"synthetic fixture","source":"unit test",
             "observed_at":"2021","geography":"Boké, Guinea","method":"mock",
             "license":"test-only","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"test","finding":"Synthetic record for unit test only.",
             "sectors":["mining"]}]

def response(finding="Synthetic record for unit test only."):
    return json.dumps({"observations":[{"evidence_id":"TEST-008","finding":finding}],
                       "hypotheses":["May require further inquiry, not proven"],
                       "investigations":["Examine current observations."],
                       "abstentions":["Mining impact cannot be concluded."]})

class LocalCouncilTests(unittest.TestCase):
    def test_real_question_selects_two_agents(self):
        job=make_plan("Quelles investigations prioritaires ?",evidence())
        self.assertEqual(job["status"],"EVIDENCE_READY_EXPLORATORY")
        self.assertGreaterEqual(len(job["proposers"]),2)

    def test_success_four_calls_with_trace(self):
        calls=[]
        def fake(model,instruction,payload,key):
            calls.append(model)
            return response()
        with tempfile.TemporaryDirectory() as td:
            result=perform_run("Question sur Boke",evidence(),"test-key","TEST-RUN-1",
                               Path(td),caller=fake)
            self.assertEqual(result["status"],"COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
            self.assertEqual(result["calls_attempted"],4)
            self.assertEqual(calls,["muse-spark-1.3","muse-spark-1.3",
                                    "muse-wonder-1.0","muse-spark-1.3"])
            saved=json.loads((Path(td)/"TEST-RUN-1.json").read_text(encoding="utf-8"))
            self.assertEqual(len(saved["steps"]),4)
            self.assertNotIn("test-key",json.dumps(saved))

    def test_bad_first_agent_stops_before_wonder(self):
        calls=[]
        def bad(model,instruction,payload,key):
            calls.append(model)
            return response("Mining impact is proven")
        with tempfile.TemporaryDirectory() as td:
            result=perform_run("Question",evidence(),"fake","TEST-BLOCK",
                               Path(td),caller=bad)
            self.assertEqual(result["status"],"STOPPED_VERIFICATION_BLOCK")
            self.assertEqual(result["calls_attempted"],1)
            self.assertEqual(len(calls),1)
            self.assertTrue((Path(td)/"TEST-BLOCK.json").exists())

    def test_failure_stops_no_retry(self):
        calls=[]
        def fail(*args):
            calls.append(1)
            raise RuntimeError("synthetic error")
        with tempfile.TemporaryDirectory() as td:
            result=perform_run("Question",evidence(),"fake","TEST-FAIL",
                               Path(td),caller=fail)
            self.assertEqual(result["status"],"STOPPED_CALL_FAILURE")
            self.assertEqual(len(calls),1)

    def test_no_evidence_means_zero_calls(self):
        calls=[]
        with tempfile.TemporaryDirectory() as td:
            result=perform_run("Question",[],"fake","TEST-ABSTAIN",
                               Path(td),caller=lambda *args:calls.append(1))
            self.assertEqual(result["status"],"ABSTAIN_NO_USABLE_EVIDENCE")
            self.assertEqual(result["calls_attempted"],0)
            self.assertEqual(calls,[])

    def test_missing_key_means_zero_calls(self):
        calls=[]
        with tempfile.TemporaryDirectory() as td:
            result=perform_run("Question",evidence(),"","TEST-NOKEY",
                               Path(td),caller=lambda *args:calls.append(1))
            self.assertEqual(result["status"],"BLOCKED_MISSING_MODEL_API_KEY")
            self.assertEqual(calls,[])

if __name__ == "__main__":
    unittest.main()
