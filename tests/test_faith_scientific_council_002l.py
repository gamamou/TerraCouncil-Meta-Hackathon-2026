"""002L — real HACK-016 runtime integration QA with mocked models, no API requests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question, plan_fingerprint
from fsdc_evidence_expansion import attach_regional_context
from faith_environmental_context_002k import attach_environmental_context
from dynamic_runtime import execute_dynamic,SCHEMA

QUESTION="Comment concilier extraction miniere, poussiere, foret, eau et communautes a Boke ?"

def records():
    return [{
      "evidence_id":"TEST-BOKE-AOI-2021-LAND",
      "dataset":"ESA WorldCover 2021",
      "source":"https://example.org/fixture","observed_at":"2021",
      "geography":"Boké, Guinea",
      "method":"ESA land cover AOI screened proxy",
      "license":"TEST_FIXTURE_ONLY",
      "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "provenance":"test fixture, NOT empirical Boké measurements",
      "finding":"ESA WorldCover pilot land cover classification is preliminary.",
      "sectors":["mining","agriculture","environment"]
    }]

def plan():
    return attach_environmental_context(attach_regional_context(
        plan_question(QUESTION,records(),geography="Boké, Guinea",sector="mining")))

class ScientificCouncilIntegrationTests(unittest.TestCase):
    def test_source_lanes_and_fingerprint(self):
        p=plan()
        self.assertEqual(len(p["evidence"]),1)
        self.assertEqual(p["environmental_context_count"],5)
        self.assertGreaterEqual(len(p["regional_context"]),5)
        self.assertEqual(p["plan_sha256"],plan_fingerprint(p))
        self.assertTrue(all(x["evidence_id"]!="FAITH-MAUS-HANSEN-640" for x in p["evidence"]))
        self.assertEqual(next(x for x in p["regional_context"] if x["evidence_id"]=="FAITH-CHENG-CPDM-CHAIN")
          ["metrics"]["verified_cheng_to_permit_count"],0)
    def test_context_changed_means_new_plan_authorization(self):
        p=plan()
        other=dict(p)
        other["regional_context"]=p["regional_context"][:-1]
        # A different source package MUST obtain a different consent-bound fingerprint.
        import hashlib
        from faith_environmental_context_002k import _canonical
        other["regional_context_sha256"]=hashlib.sha256(_canonical(other["regional_context"]).encode("utf-8")).hexdigest()
        self.assertNotEqual(plan_fingerprint(other),p["plan_sha256"])
    def test_mock_spark_wonder_receives_bounded_context(self):
        calls=[]
        def fake_call(model,prompt,payload,key):
            calls.append((model,prompt,payload))
            self.assertEqual(payload["regional_context"],p["regional_context"])
            self.assertTrue(all(x["evidence_id"].startswith("TEST-") for x in payload["evidence"]))
            e=payload["evidence"][0]
            return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
                "hypotheses":["Hypothèse comparative, non validée."],
                "investigations":["Verifier spatialement les sources et tester les hypothèses concurrentes."],
                "abstentions":["Aucun impact minier mesuré démontré sur l'AOI."]},ensure_ascii=False)
        p=plan()
        with tempfile.TemporaryDirectory() as d:
            result=execute_dynamic(p,"TEST-SCIENCE-002L",d,"MOCK_ONLY",caller=fake_call)
        self.assertEqual(result["status"],"COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
        self.assertEqual(result["calls_attempted"],len(p["proposers"])+2)
        self.assertTrue(any(model=="muse-wonder-1.0" for model,_,_ in calls))
        self.assertIn("COUNTS",SCHEMA)
        self.assertIn("pilot AOI",SCHEMA)
    def test_server_preview_and_execute_share_same_science_adapter(self):
        s=(Path(__file__).resolve().parents[1]/"src"/"local_council_server.py").read_text(encoding="utf-8")
        self.assertIn("selected=attach_environmental_context(attach_regional_context(",s)
        self.assertIn("plan=attach_environmental_context(attach_regional_context(",s)
        self.assertIn('source_url":e.get("source_url")',s)
        self.assertIn('request_data.get("plan_sha256")',s)

if __name__=="__main__":
    unittest.main()
