"""HACK-016J: no new external calls; matrix must be grounded in actual session."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_decision_matrix import decision_matrix
from dynamic_brief import build_dynamic_pdf

def source():
    return [{"evidence_id":"WORLD-LAND-TEST","dataset":"ESA WorldCover 2021",
      "source":"test","observed_at":"2021","geography":"Boké, Guinea",
      "method":"test","license":"test","provenance":"test",
      "validation_status":"SCREENED_NOT_FIELD_VALIDATED","sectors":["mining","agriculture"],
      "finding":"WorldCover 2021 land cover only, not current change."}]

def fake(model,instruction,payload,key):
    obs=payload["evidence"][0]
    return json.dumps({
     "observations":[{"evidence_id":obs["evidence_id"],"finding":obs["finding"]}],
     "hypotheses":["Hypothèse incertaine."],
     "investigations":["Examiner la question scientifique : "+payload["question"]],
     "abstentions":["Aucun impact minier démontré."]},ensure_ascii=False)

class MatrixTests(unittest.TestCase):
    def session(self,folder,question,identifier):
        plan=plan_question(question,source(),sector="mining")
        return execute_dynamic(plan,identifier,folder,"mock",caller=fake)
    def test_matrix_records_source_limits_and_no_invented_rank(self):
        with TemporaryDirectory() as folder:
            trace=self.session(folder,"Occupation du sol à Boké ?","HACK016-J-TEST-001")
            result=decision_matrix(trace)
            self.assertEqual(result["source_ids"],["WORLD-LAND-TEST"])
            self.assertEqual(len(result["options"]),len(trace["proposers"]))
            self.assertTrue(all(x["priority"]=="NOT_ASSESSED" for x in result["options"]))
            self.assertTrue(all(x["estimated_cost"]=="NOT_AVAILABLE" for x in result["options"]))
            self.assertTrue(all(x["evidence_ids"]==["WORLD-LAND-TEST"] for x in result["options"]))
            self.assertTrue(result["scientific_critic_issues"])
    def test_questions_change_matrix(self):
        with TemporaryDirectory() as folder:
            a=decision_matrix(self.session(folder,"Occupation du sol des villages ?","HACK016-J-TEST-A"))
            b=decision_matrix(self.session(folder,"Occupation du sol des cultures ?","HACK016-J-TEST-B"))
            self.assertNotEqual(a["matrix_sha256"],b["matrix_sha256"])
    def test_tampered_data_fails_closed(self):
        with TemporaryDirectory() as folder:
            t=self.session(folder,"Occupation du sol ?","HACK016-J-TEST-C")
            t["evidence_snapshot"][0]["finding"]="Fabricated value."
            with self.assertRaises(ValueError):decision_matrix(t)
    def test_pdf_v2_creates_without_overwrite(self):
        try:import reportlab
        except ImportError:self.skipTest("ReportLab unavailable")
        with TemporaryDirectory() as folder:
            t=self.session(folder,"Occupation du sol à Boké ?","HACK016-J-TEST-D")
            pdf=Path(folder)/"new.pdf"
            build_dynamic_pdf(t,pdf)
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
            with self.assertRaises(ValueError):build_dynamic_pdf(t,pdf)

if __name__=="__main__":unittest.main()
