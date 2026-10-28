"""HACK-016K: source-literal quantification, no invented metrics or trends."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_quantification import quantify
from dynamic_brief import build_dynamic_pdf

def sources():
    return [{"evidence_id":"BOKE-LC-2021","dataset":"ESA WorldCover 2021 v200",
     "source":"test","observed_at":"2021","geography":"Boké, Guinea",
     "method":"AOI area-weighted cover shares","license":"test",
     "provenance":"test fixture","sectors":["mining"],
     "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
     "finding":"ESA WorldCover 2021 AOI area-weighted cover shares: Tree cover 50.613%, Cropland 2.262%, Built-up 0.846%, Permanent water 0.528%, Mangroves 0.493%; 2021 snapshot is not a 2026 change or a mining impact."}]
def mock(model,prompt,payload,key):
    e=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
        "hypotheses":["Changement à vérifier."],
        "investigations":["Comparer aux observations récentes."],
        "abstentions":["Aucun impact établi."]},ensure_ascii=False)

class QuantificationTests(unittest.TestCase):
    def session(self,folder):
        p=plan_question("Occupation du sol à Boké ?",sources(),sector="mining")
        return execute_dynamic(p,"HACK016-TEST-K-001",folder,"mock",caller=mock)
    def test_five_worldcover_values_are_exact(self):
        with TemporaryDirectory() as folder:
            q=quantify(self.session(folder))
            self.assertEqual([m["value"] for m in q["metrics"]],
                [50.613,2.262,0.846,0.528,0.493])
            self.assertTrue(all(m["evidence_id"]=="BOKE-LC-2021" for m in q["metrics"]))
            self.assertFalse(q["trend_available"])
            self.assertFalse(q["causal_impact_established"])
    def test_source_mutation_fails(self):
        with TemporaryDirectory() as folder:
            t=self.session(folder)
            t["evidence_snapshot"][0]["finding"]="Invented claim"
            with self.assertRaises(ValueError):quantify(t)
    def test_v3_pdf_does_not_overwrite(self):
        try:import reportlab
        except ImportError:self.skipTest("ReportLab absent")
        with TemporaryDirectory() as folder:
            trace=self.session(folder)
            file=Path(folder)/"report-v3.pdf"
            build_dynamic_pdf(trace,file)
            self.assertTrue(file.read_bytes().startswith(b"%PDF"))
            with self.assertRaises(ValueError):build_dynamic_pdf(trace,file)
if __name__=="__main__":unittest.main()
