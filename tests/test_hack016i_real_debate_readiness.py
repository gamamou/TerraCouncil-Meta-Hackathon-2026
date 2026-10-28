"""HACK-016I: question-bound plans and strict FSDC schema with mocked models."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question,plan_fingerprint
from dynamic_runtime import execute_dynamic,SCHEMA

def evidence():
    return [{"evidence_id":"BOKE-LAND","dataset":"WorldCover",
      "source":"fixture","observed_at":"2021","geography":"Boké, Guinea",
      "method":"synthetic","license":"test","provenance":"test",
      "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "sectors":["mining"],"finding":"WorldCover land cover is preliminary."}]

def model(model,prompt,payload,key):
    e=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
      "hypotheses":["Une relation reste à étudier."],
      "investigations":["Examiner la question : "+payload["question"]],
      "abstentions":["Aucun impact démontré."]},ensure_ascii=False)

class DynamicBoundPlanTests(unittest.TestCase):
    def test_same_evidence_different_questions_have_different_plans(self):
        first=plan_question("Occupation du sol pour les villages ?",evidence(),sector="mining")
        second=plan_question("Occupation du sol pour les cultures ?",evidence(),sector="mining")
        self.assertEqual(first["evidence_sha256"],second["evidence_sha256"])
        self.assertNotEqual(first["plan_sha256"],second["plan_sha256"])
        self.assertEqual(first["plan_sha256"],plan_fingerprint(first))
    def test_all_mock_steps_are_source_bound(self):
        p=plan_question("Occupation du sol à Boké ?",evidence(),sector="mining")
        with TemporaryDirectory() as root:
            t=execute_dynamic(p,"HACK016-TEST-I-2026",root,"test",caller=model)
            self.assertEqual(t["status"],"COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
            self.assertEqual(t["plan_sha256"],p["plan_sha256"])
            self.assertEqual(t["calls_attempted"],len(p["proposers"])+2)
            self.assertIn("No markdown",SCHEMA)
    def test_no_dust_evidence_for_air_quality(self):
        p=plan_question("Mesures de PM10 à Boké ?",evidence(),sector="mining")
        self.assertEqual(p["status"],"ABSTAIN_NO_QUESTION_RELEVANT_EVIDENCE")
        self.assertEqual(p["model_calls_planned"],0)
if __name__=="__main__":unittest.main()
