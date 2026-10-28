"""HACK-016 deterministic dynamic selection and independent verification."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_debate import run_dynamic

def evidence():
    base={"source":"test","observed_at":"2021","geography":"Boké, Guinea",
          "method":"synthetic","license":"test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
          "provenance":"mock","sectors":["mining"]}
    return [
      dict(base,evidence_id="POP",dataset="WorldPop 2026",
           finding="WorldPop population raster cell sum; not exposure."),
      dict(base,evidence_id="LAND",dataset="ESA WorldCover 2021",
           finding="WorldCover land cover shares, not mining impact.")
    ]
def mock(model,instruction,payload,key):
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}
             for e in payload["evidence"]],
             "hypotheses":["No proven causal effects."],
             "investigations":["Investigate the question-specific domain."],
             "abstentions":["Missing relevant field measurements."]})

class DynamicTests(unittest.TestCase):
    def test_dust_only_abstains(self):
        p=plan_question("Quelles concentrations PM10 de poussière à Boké ?",evidence(),sector="mining")
        self.assertEqual(p["status"],"ABSTAIN_NO_QUESTION_RELEVANT_EVIDENCE")
        self.assertEqual(p["model_calls_planned"],0)
        self.assertIn("dust",p["missing_topics"])
    def test_land_evidence_runs_new_meta_positions(self):
        p=plan_question("Quel est le contexte de l'occupation du sol ?",evidence(),sector="mining")
        self.assertEqual(len(p["evidence"]),1)
        self.assertEqual(p["evidence"][0]["evidence_id"],"LAND")
        result=run_dynamic(p,"mock",caller=mock)
        self.assertEqual(result["status"],"STRUCTURAL_CHECKS_PASSED_HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["calls_attempted"],len(p["proposers"])+2)
    def test_question_and_sources_drive_distinct_plans(self):
        a=plan_question("Population des villages",evidence(),sector="mining")
        b=plan_question("Occupation du sol",evidence(),sector="mining")
        self.assertNotEqual(a["evidence_sha256"],b["evidence_sha256"])
    def test_no_key_rejected(self):
        p=plan_question("Occupation du sol",evidence(),sector="mining")
        with self.assertRaises(ValueError):run_dynamic(p,"")

if __name__=="__main__":
    unittest.main()
