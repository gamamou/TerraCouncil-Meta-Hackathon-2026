"""TERRA-DEMO-001 — UI display + scientific debate + local original-data integration QA."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from dynamic_council import plan_question
from fsdc_evidence_expansion import attach_regional_context
from faith_environmental_context_002k import attach_environmental_context

QUESTION="Comment concilier extraction miniere, poussiere, foret, eau et communautes a Boke ?"
def fixture():
    return [{"evidence_id":"TEST-ESA-WORLDCOVER","dataset":"ESA WorldCover 2021",
      "source":"https://example.org","observed_at":"2021",
      "geography":"Boké, Guinea","method":"land cover pilot classification",
      "license":"TEST_ONLY","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "provenance":"TEST FIXTURE NOT BOKE SOURCE",
      "finding":"ESA WorldCover screened classification of the pilot rectangle.",
      "sectors":["mining"]}]

class IntegratedDemoTests(unittest.TestCase):
    def test_visible_dynamic_preview_contains_dust_methodology(self):
        html=(ROOT/"ui"/"hack008.html").read_text(encoding="utf-8")
        for s in ('plan.dust_protocol','item.missing_input','item.decision_test',
                  'Le débat dynamique exige une autorisation séparée.'):
            self.assertIn(s,html)
    def test_real_server_uses_same_science_context_for_preview_and_run(self):
        py=(ROOT/"src"/"local_council_server.py").read_text(encoding="utf-8")
        self.assertIn('selected=attach_environmental_context(attach_regional_context(',py)
        self.assertIn('plan=attach_environmental_context(attach_regional_context(',py)
        self.assertIn('request_data.get("plan_sha256")',py)
        self.assertIn('records=expand(a.hi,a.qa)',py)
    def test_dust_plan_context_is_present_but_no_dust_aoi_fact(self):
        p=attach_environmental_context(attach_regional_context(plan_question(
            QUESTION,fixture(),sector="mining")))
        self.assertEqual(p["dust_context_count"],3)
        self.assertEqual(len(p["dust_protocol"]),4)
        self.assertIn("dust",p["missing_topics"])
        self.assertFalse(p["dust_aoi_concentration_admitted"])
        self.assertEqual(len(p["evidence"]),1)
        self.assertTrue(p["status"].startswith("READY_"))
        self.assertEqual(len([x for x in p["regional_context"] if x["source_type"]=="FSMI_MODELED_REGIONAL_ATMOSPHERIC_CONTEXT"]),3)
    def test_voice_script_remains_review_gated(self):
        s=(ROOT/"src"/"dynamic_narration.py").read_text(encoding="utf-8")
        self.assertIn('"automatic_tts_allowed":False',s)
        self.assertIn('"review_required":True',s)

if __name__=="__main__":unittest.main()
