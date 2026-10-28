"""HACK-016E: audit is deterministic, fails closed and cannot authorize TTS."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_narration import build_dynamic_oral
from dynamic_oral_audit import verify_oral

def sources():
    return [{"evidence_id":"WORLD-TEST","dataset":"ESA WorldCover 2021",
             "source":"test","observed_at":"2021","geography":"Boké, Guinea",
             "method":"synthetic","license":"test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"fixture","sectors":["mining"],
             "finding":"WorldCover land cover is exploratory, not proof of damage."}]
def model(model,prompt,payload,key):
    evidence=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":evidence["evidence_id"],
         "finding":evidence["finding"]}],
         "hypotheses":["Hypothèse à vérifier."],
         "investigations":["Examiner le territoire concerné."],
         "abstentions":["Les données ne démontrent aucun impact."]},ensure_ascii=False)

class FidelityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        plan=plan_question("Occupation du sol et cultures ?",sources(),sector="mining")
        self.trace=execute_dynamic(plan,"HACK016-TEST-AUDIT-2026",self.tmp.name,"mock",caller=model)
    def tearDown(self):self.tmp.cleanup()
    def test_exact_source_extraction(self):
        report=verify_oral(self.trace)
        self.assertEqual(report["status"],"EXACT_EXTRACTION_CHECK_PASSED")
        self.assertFalse(report["tts_authorized"])
        self.assertEqual(report["new_ai_calls"],0)
    def test_edited_text_requires_review(self):
        edited=build_dynamic_oral(self.trace)
        edited["turns"][0]["text_to_review"]="Tout est sans risque."
        check=verify_oral(self.trace,edited)
        self.assertEqual(check["status"],"REVIEW_REQUIRED")
        self.assertIn("EDITORIAL_CHANGE_NEEDS_SEMANTIC_REVIEW",check["checks"][0]["issues"])
    def test_protected_provenance_rejected(self):
        edited=build_dynamic_oral(self.trace)
        edited["turns"][0]["source_model"]="other-model"
        with self.assertRaises(ValueError):verify_oral(self.trace,edited)
    def test_changed_evidence_rejected(self):
        self.trace["evidence_snapshot"][0]["finding"]="Altered"
        with self.assertRaises(ValueError):verify_oral(self.trace)
if __name__=="__main__":unittest.main()
