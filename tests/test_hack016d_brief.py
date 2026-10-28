"""Dynamic brief integrity tests. No Meta, ElevenLabs or external requests."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_brief import brief_data,build_dynamic_pdf

def records():
    return [{"evidence_id":"LAND-TEST","dataset":"ESA WorldCover 2021",
      "source":"test","observed_at":"2021","geography":"Boké, Guinea",
      "method":"synthetic","license":"test",
      "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "provenance":"test","sectors":["mining"],
      "finding":"WorldCover land cover shares, not validated impacts."}]

def model(model,prompt,payload,key):
    e=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],
      "finding":e["finding"]}],
      "hypotheses":["Étude exploratoire."],
      "investigations":["Étudier : "+payload["question"]],
      "abstentions":["Impacts non démontrés."]},ensure_ascii=False)

class DynamicBriefTests(unittest.TestCase):
    def sample(self,folder):
        p=plan_question("Occupation du sol près des villages ?",records(),sector="mining")
        return execute_dynamic(p,"HACK016-TEST-BRIEF-0001",folder,"test",caller=model)
    def test_brief_exactly_binds_evidence_and_question(self):
        with TemporaryDirectory() as folder:
            trace=self.sample(folder)
            data=brief_data(trace)
            self.assertEqual(data["question"],trace["question"])
            self.assertEqual(data["evidence_sha256"],trace["evidence_sha256"])
            trace["evidence_snapshot"][0]["finding"]="Invented"
            with self.assertRaises(ValueError):brief_data(trace)
    def test_pdf_with_optional_reportlab(self):
        try:import reportlab
        except ImportError:self.skipTest("ReportLab unavailable")
        with TemporaryDirectory() as folder:
            trace=self.sample(folder)
            path=Path(folder)/"dynamic.pdf"
            build_dynamic_pdf(trace,path)
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))
            with self.assertRaises(ValueError):build_dynamic_pdf(trace,path)
if __name__=="__main__":
    unittest.main()
