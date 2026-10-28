"""HACK-016B: deterministic simulated dynamic model calls and saved sessions."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic

def sources():
    base={"source":"Synthetic fixture","observed_at":"2021","geography":"Boké, Guinea",
          "method":"Synthetic test","license":"test",
          "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
          "provenance":"mock","sectors":["mining"]}
    return [dict(base,evidence_id="TEST-LAND-016B",dataset="ESA WorldCover 2021",
                 finding="WorldCover 2021 land cover shares; does not prove mining impacts.")]

def fake_caller(model,instruction,payload,key):
    return json.dumps({"observations":[{"evidence_id":item["evidence_id"],
                                         "finding":item["finding"]} for item in payload["evidence"]],
                       "hypotheses":["The relation needs investigation."],
                       "investigations":["Verify changes in land-cover with updated reference data."],
                       "abstentions":["No current impacts can be concluded."]})

class DynamicRuntimeTests(unittest.TestCase):
    def test_saves_all_steps_and_rejects_duplicate(self):
        plan=plan_question("Occupation du sol à Boké ?",sources(),sector="mining")
        with TemporaryDirectory() as folder:
            trace=execute_dynamic(plan,"HACK016-TEST-OK-00001",folder,"mock",caller=fake_caller)
            self.assertEqual(trace["status"],"COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
            self.assertEqual(trace["calls_attempted"],len(plan["proposers"])+2)
            self.assertEqual(trace["steps"][-2]["model"],"muse-wonder-1.0")
            self.assertTrue((Path(folder)/"HACK016-TEST-OK-00001.json").exists())
            with self.assertRaises(ValueError):
                execute_dynamic(plan,"HACK016-TEST-OK-00001",folder,"mock",caller=fake_caller)
    def test_stops_on_false_claim_and_keeps_snapshot(self):
        plan=plan_question("Occupation du sol à Boké ?",sources(),sector="mining")
        def invalid(model,instruction,payload,key):
            return json.dumps({"observations":[{"evidence_id":"TEST-LAND-016B",
                               "finding":"Invented impact"}],
                               "hypotheses":[],"investigations":[],"abstentions":[]})
        with TemporaryDirectory() as folder:
            trace=execute_dynamic(plan,"HACK016-TEST-BLOCK-001",folder,"mock",caller=invalid)
            self.assertEqual(trace["status"],"STOPPED_DO_NOT_RETRY_BLINDLY")
            self.assertEqual(trace["calls_attempted"],1)
            self.assertTrue((Path(folder)/"HACK016-TEST-BLOCK-001.json").is_file())
    def test_no_calls_without_matching_evidence(self):
        plan=plan_question("Quelle concentration de PM10 ?",sources(),sector="mining")
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                execute_dynamic(plan,"HACK016-TEST-DUST-0001",folder,"mock",caller=fake_caller)

if __name__=="__main__":
    unittest.main()
