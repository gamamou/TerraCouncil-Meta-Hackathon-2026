"""HACK-010 tests: polished PDF and editorial spoken script use verified traces."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from local_council_server import perform_run
from export_decision_pdf import validate_session
from natural_french_dialogue import oral_storyboard
from elegant_decision_pdf import export_elegant_pdf

def evidence():
    base={"source":"test","observed_at":"2021","geography":"Boké, Guinea",
          "method":"synthetic test","license":"test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
          "provenance":"test only","sectors":["mining"]}
    return [
        {**base,"evidence_id":"TEST-POP","dataset":"WorldPop 2026",
         "finding":"Synthetic WorldPop test estimate; not exposed people."},
        {**base,"evidence_id":"TEST-COVER","dataset":"ESA WorldCover 2021",
         "finding":"Synthetic WorldCover classification; not mining impact."}
    ]

def text():
    return json.dumps({
        "observations":[
            {"evidence_id":"TEST-POP","finding":"Synthetic WorldPop test estimate; not exposed people."},
            {"evidence_id":"TEST-COVER","finding":"Synthetic WorldCover classification; not mining impact."}
        ],
        "hypotheses":["Rectangular perimeter not validated for population and land-cover change."],
        "investigations":["Study demography, water, hydrology, mangroves, biodiversity, climate, land-cover and current environmental conditions."],
        "abstentions":["Cannot conclude mining effects or investment approval."]
    })

class Hack010Tests(unittest.TestCase):
    def create(self, directory):
        return perform_run("Quelles investigations prioriser ?",evidence(),"fake","HACK008-TEST-PDF-001",
                           directory,caller=lambda *args:text())

    def test_oral_script_uses_no_model_calls_or_symbols(self):
        with TemporaryDirectory() as d:
            trace=self.create(Path(d))
            script=oral_storyboard(trace,evidence())
            self.assertEqual(len(script["turns"]),4)
            self.assertTrue(script["human_review_required"])
            self.assertFalse(script["human_review_complete"])
            for turn in script["turns"]:
                self.assertFalse(any(ch.isdigit() for ch in turn["text_to_review"]))
                self.assertNotIn("TEST-POP",turn["text_to_review"])
                self.assertFalse(turn["approved"])

    def test_unrelated_debate_rejected(self):
        with TemporaryDirectory() as d:
            trace=self.create(Path(d))
            for step in trace["steps"]:
                step["checked_publication"]["hypotheses"] = []
                step["checked_publication"]["investigations"] = [{"text":"A different plan", "label":"PROPOSED_INVESTIGATION_NOT_ESTABLISHED"}]
                step["checked_publication"]["abstentions"] = []
            trace["decision_support"] = trace["steps"][-1]["checked_publication"]
            with self.assertRaises(ValueError):
                oral_storyboard(trace,evidence())

    def test_elegant_pdf_generates(self):
        try: import reportlab
        except ImportError: self.skipTest("Optional reportlab not installed")
        with TemporaryDirectory() as d:
            data=validate_session(self.create(Path(d)),evidence())
            path=export_elegant_pdf(data,Path(d)/"elegant.pdf")
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))
            self.assertGreater(path.stat().st_size,2500)

    def test_changed_evidence_blocks_report(self):
        with TemporaryDirectory() as d:
            trace=self.create(Path(d))
            e=evidence();e[0]["finding"]="Tampered"
            with self.assertRaises(ValueError):
                validate_session(trace,e)

if __name__=="__main__":
    unittest.main()
