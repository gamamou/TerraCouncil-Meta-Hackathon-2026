"""HACK-011: pre-flight review approval and source binding, zero external calls."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

from local_council_server import perform_run
from natural_french_dialogue import oral_storyboard
from approve_oral_script import reviewed_manifest
from render_session_audio import build_payload

def evidence():
    common={"source":"synthetic","observed_at":"2021","geography":"Boké, Guinea",
            "method":"test","license":"test","provenance":"test",
            "validation_status":"SCREENED_NOT_FIELD_VALIDATED","sectors":["mining"]}
    return [
        {**common,"evidence_id":"TESTPOP","dataset":"WorldPop 2026",
         "finding":"Test population estimate; no exposure."},
        {**common,"evidence_id":"TESTLAND","dataset":"ESA WorldCover 2021",
         "finding":"Test land cover; no mining effect."}
    ]
def fake():
    return json.dumps({
        "observations":[
            {"evidence_id":"TESTPOP","finding":"Test population estimate; no exposure."},
            {"evidence_id":"TESTLAND","finding":"Test land cover; no mining effect."}
        ],
        "hypotheses":["Rectangular AOI and demography remain uncertain."],
        "investigations":["Investigate current land-cover, water, climate, mangroves, biodiversity, hydrology and population."],
        "abstentions":["No observed mining impact can be confirmed."]
    })

class ReviewTests(unittest.TestCase):
    def setup(self,dir):
        e=evidence()
        t=perform_run("Quelles investigations à Boké ?",e,"fake","HACK008-TEST-REVIEW-01",
                      Path(dir),caller=lambda *args:fake())
        return t,e,oral_storyboard(t,e)

    def test_review_required_before_tts(self):
        with TemporaryDirectory() as d:
            t,e,draft=self.setup(d)
            with self.assertRaises(ValueError):
                build_payload(draft,"spark","wonder")
            reviewed=reviewed_manifest(draft,t,e)
            self.assertTrue(reviewed["human_review_complete"])
            self.assertEqual(len(build_payload(reviewed,"spark","wonder")["inputs"]),4)

    def test_edit_text_only(self):
        with TemporaryDirectory() as d:
            t,e,draft=self.setup(d)
            draft["turns"][0]["text_to_review"]="Nous proposons de vérifier les communautés sur le terrain."
            approved=reviewed_manifest(draft,t,e)
            self.assertEqual(approved["turns"][0]["text_to_review"],
                             "Nous proposons de vérifier les communautés sur le terrain.")

    def test_changed_source_attribution_rejected(self):
        with TemporaryDirectory() as d:
            t,e,draft=self.setup(d)
            draft["turns"][1]["speaker"]="Expert autre"
            with self.assertRaises(ValueError):
                reviewed_manifest(draft,t,e)

    def test_suspicious_spoken_symbols_rejected(self):
        with TemporaryDirectory() as d:
            t,e,draft=self.setup(d)
            draft["turns"][0]["text_to_review"]="Voir TEST_ID_9 http://example.com."
            with self.assertRaises(ValueError):
                reviewed_manifest(draft,t,e)

    def test_changed_evidence_fingerprint_rejected(self):
        with TemporaryDirectory() as d:
            t,e,draft=self.setup(d)
            draft["evidence_sha256"]="tampered"
            with self.assertRaises(ValueError):
                reviewed_manifest(draft,t,e)

if __name__=="__main__":
    unittest.main()
