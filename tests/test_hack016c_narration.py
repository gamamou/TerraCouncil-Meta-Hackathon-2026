"""Regression test: new oral content reflects actual session-specific findings."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_narration import build_dynamic_oral

def evidence():
    return [{"evidence_id":"LAND-TEST","dataset":"ESA WorldCover 2021",
             "source":"fixture","observed_at":"2021","geography":"Boké, Guinea",
             "method":"fixture","license":"test",
             "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"fixture","sectors":["mining"],
             "finding":"Land cover estimates are exploratory, not verified impacts."}]

def caller(model,prompt,payload,key):
    question=payload["question"]
    original=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":original["evidence_id"],
                "finding":original["finding"]}],
      "hypotheses":["Cette hypothèse nécessite une enquête."],
      "investigations":["Étudier : "+question],
      "abstentions":["Il manque une validation de terrain."]},ensure_ascii=False)

class DynamicNarrationTests(unittest.TestCase):
    def run_case(self,question,run_id,folder):
        plan=plan_question(question,evidence(),sector="mining")
        return execute_dynamic(plan,run_id,folder,"test",caller=caller)
    def test_two_questions_yield_different_oral_scripts(self):
        with TemporaryDirectory() as folder:
            a=self.run_case("Occupation du sol des villages ?","HACK016-TEST-A-2026",folder)
            b=self.run_case("Occupation du sol des cultures ?","HACK016-TEST-B-2026",folder)
            x=build_dynamic_oral(a)
            y=build_dynamic_oral(b)
            self.assertNotEqual(x["script_sha256"],y["script_sha256"])
            self.assertIn("villages",x["turns"][0]["text_to_review"])
            self.assertIn("cultures",y["turns"][0]["text_to_review"])
            self.assertEqual(x["type"],"EDITORIAL_RECONSTRUCTION_NOT_VERBATIM")
            self.assertFalse(x["automatic_tts_allowed"])
    def test_tampered_evidence_fails_closed(self):
        with TemporaryDirectory() as folder:
            result=self.run_case("Occupation du sol ?","HACK016-TEST-C-2026",folder)
            result["evidence_snapshot"][0]["finding"]="Faux chiffre."
            with self.assertRaises(ValueError):
                build_dynamic_oral(result)
    def test_incomplete_session_fails(self):
        with self.assertRaises(ValueError):
            build_dynamic_oral({"status":"STARTED"})
if __name__=="__main__":
    unittest.main()
