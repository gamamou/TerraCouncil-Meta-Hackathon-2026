"""009G: synthetic fixtures only; never invoke external models."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009g_exploratory import make_plan, ADMITTED

def fixture():
    return {"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1",
     "question":"Quels risques environnementaux et ESG pour une mine de bauxite ?",
     "scientific_status":"EXPLORATORY_DISCUSSION_ONLY",
     "decision_authorized":False,"human_review_required":True,
     "claims":[{"evidence_id":"TEST-1","source_version":"example",
       "finding":"Illustration seulement", "source":"https://example.org",
       "method":"test","limitations":"No field validation",
       "admissibility":ADMITTED,
       "decision_admissibility":"NOT_ADMISSIBLE_FOR_DECISION",
       "original_validation_status":"SCREENED_NOT_FIELD_VALIDATED"}]}
class TestExploratoryCouncil(unittest.TestCase):
    def test_opening_and_deliberation(self):
        p=make_plan(fixture())
        self.assertEqual(p["steps"][0]["role"],"scientific_chair")
        self.assertEqual(p["steps"][-1]["phase"],"deliberation")
        self.assertIn("esg",p["active_experts"])
        self.assertFalse(p["decision_authorized"])
        self.assertEqual(p["meta_calls"],0)
    def test_no_evidence_rejected(self):
        x=fixture();x["claims"]=[]
        with self.assertRaises(ValueError):make_plan(x)
    def test_status_promotion_rejected(self):
        x=fixture();x["claims"][0]["original_validation_status"]="VERIFIED"
        with self.assertRaises(ValueError):make_plan(x)
    def test_decision_authorization_rejected(self):
        x=fixture();x["decision_authorized"]=True
        with self.assertRaises(ValueError):make_plan(x)
    def test_duplicates_rejected(self):
        x=fixture();x["claims"]*=2
        with self.assertRaises(ValueError):make_plan(x)
    def test_context_not_evidence(self):
        x=fixture();x["context_only"]=[{"evidence_id":"CTX","admissibility":"CONTEXT_ONLY"}]
        p=make_plan(x)
        self.assertNotIn("CTX",[e["evidence_id"] for e in p["evidence"]])
if __name__=="__main__":unittest.main()
