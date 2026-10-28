"""TERRA-DATA-002M: verify actual modeled-dust council integration without API billing."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question,plan_fingerprint
from faith_environmental_context_002k import attach_environmental_context
from dynamic_runtime import execute_dynamic

Q="Comment concilier extraction miniere, poussiere, foret, eau et communautes a Boke ?"
def local_source():
    return [{"evidence_id":"TEST-WORLDCOVER-AOI","dataset":"ESA WorldCover 2021",
      "source":"https://example.org/test","observed_at":"2021",
      "geography":"Boké, Guinea","method":"Raster pilot land cover screening",
      "license":"TEST_ONLY","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "provenance":"TEST FIXTURE not real Boké","finding":"WorldCover preliminary pilot land cover.",
      "sectors":["mining"]}]

class DustDebateTests(unittest.TestCase):
    def make_plan(self):
        return attach_environmental_context(plan_question(Q,local_source(),sector="mining"))
    def test_protocol_and_no_fake_dust_observation(self):
        p=self.make_plan()
        self.assertEqual(len(p["dust_protocol"]),4)
        self.assertEqual(p["dust_context_count"],3)
        self.assertFalse(p["dust_aoi_concentration_admitted"])
        self.assertEqual([r["evidence_id"] for r in p["evidence"]],["TEST-WORLDCOVER-AOI"])
        self.assertIn("dust",p["missing_topics"])
        self.assertEqual(p["plan_sha256"],plan_fingerprint(p))
    def test_protocol_change_breaks_consent_plan_id(self):
        p=self.make_plan()
        changed=dict(p)
        changed["scientific_protocol_sha256"]="tampered"
        self.assertNotEqual(plan_fingerprint(changed),p["plan_sha256"])
    def test_mock_spark_wonder_receives_four_investigations(self):
        p=self.make_plan()
        calls=[]
        def mock(model, instruction, payload, key):
            calls.append((model,payload))
            self.assertEqual(len(payload["dust_protocol"]),4)
            self.assertEqual(len(payload["evidence"]),1)
            e=payload["evidence"][0]
            return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
                "hypotheses":["Tester les autres sources de particules sans attribution minière."],
                "investigations":["Surveiller les PM10 et PM2.5 avec protocole de calibration."],
                "abstentions":["Aucune concentration minière locale observée admise."]},ensure_ascii=False)
        with tempfile.TemporaryDirectory() as d:
            result=execute_dynamic(p,"TEST-DUST-002M",d,"MOCK",caller=mock)
            self.assertEqual(result["status"],"COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
            self.assertEqual(len(result["dust_protocol"]),4)
            self.assertEqual(result["scientific_protocol_sha256"],p["scientific_protocol_sha256"])
        self.assertTrue(any(model=="muse-wonder-1.0" for model,_ in calls))
    def test_edge_preview_exposes_protocol(self):
        source=(Path(__file__).resolve().parents[1]/"src"/"local_council_server.py").read_text(encoding="utf-8")
        self.assertIn('"dust_protocol":selected.get("dust_protocol",[])',source)
        self.assertIn('"scientific_protocol_sha256":selected.get("scientific_protocol_sha256")',source)

if __name__=="__main__":unittest.main()
