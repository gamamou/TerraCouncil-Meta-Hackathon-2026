"""HACK-014: in-browser source-bound manuscript approval preflight.
Zero external calls.
"""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from local_council_server import perform_run
from natural_french_dialogue import oral_storyboard
from approve_oral_script import reviewed_manifest
from render_session_audio import build_payload

def sources():
    base={"source":"test fixture","observed_at":"2021","geography":"Boké, Guinea",
          "method":"test","license":"synthetic test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
          "provenance":"mock","sectors":["mining"]}
    return [
        dict(base,evidence_id="POPTEST",dataset="WorldPop 2026",
             finding="Synthetic population raster sum; no exposed population."),
        dict(base,evidence_id="LANDTEST",dataset="ESA WorldCover 2021",
             finding="Synthetic cover classification; no mining impact.")
    ]
def response():
    return json.dumps({
      "observations":[{"evidence_id":x["evidence_id"],"finding":x["finding"]} for x in sources()],
      "hypotheses":["Rectangular geography is uncertain."],
      "investigations":["Verify demography, land-cover, water, hydrology, mangroves, biodiversity and climate."],
      "abstentions":["No mining impacts proven."]
    })
class BrowserReviewTests(unittest.TestCase):
    def fixtures(self,where):
        src=sources()
        trace=perform_run("Quels risques étudier à Boké ?",src,"mock",
                          "HACK008-TEST-014",Path(where),caller=lambda *a:response())
        return src,trace,oral_storyboard(trace,src)
    def test_approved_script_cannot_be_longer_than_limit(self):
        with TemporaryDirectory() as where:
            src,trace,draft=self.fixtures(where)
            draft["turns"][0]["text_to_review"]="Voici une réflexion. "*100
            with self.assertRaises(ValueError):
                reviewed_manifest(draft,trace,src)
    def test_review_and_tts_preflight(self):
        with TemporaryDirectory() as where:
            src,trace,draft=self.fixtures(where)
            with self.assertRaises(ValueError):
                build_payload(draft,"spark","wonder")
            reviewed=reviewed_manifest(draft,trace,src)
            payload=build_payload(reviewed,"spark","wonder")
            self.assertEqual(len(payload["inputs"]),4)
            self.assertEqual(payload["model_id"],"eleven_v4")
    def test_change_attribution_rejected(self):
        with TemporaryDirectory() as where:
            src,trace,draft=self.fixtures(where)
            draft["turns"][2]["source_model"]="muse-spark-1.3"
            with self.assertRaises(ValueError):
                reviewed_manifest(draft,trace,src)

if __name__=="__main__":
    unittest.main()
