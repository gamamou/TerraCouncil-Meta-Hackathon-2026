"""TERRA-COUNCIL-009I offline plan and scientific-safety tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009i_live import validate
from terra_council_009h_composition import compose
from terra_council_009g_exploratory import ADMITTED

def fixture():
    claims=[{"evidence_id":"TEST-1","source_version":"test",
      "finding":"synthetic fixture","source":"https://example.org",
      "method":"test","limitations":"not scientific evidence",
      "admissibility":ADMITTED,
      "decision_admissibility":"NOT_ADMISSIBLE_FOR_DECISION",
      "original_validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "dataset":"WorldPop population"}]
    m={"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1",
       "question":"Quelles investigations et garanties avant développement minier ?",
       "scientific_status":"EXPLORATORY_DISCUSSION_ONLY",
       "decision_authorized":False,"human_review_required":True,
       "claims":claims}
    return compose(m),m

class Test009I(unittest.TestCase):
    def test_plan_accepted(self):
        p,m=fixture()
        self.assertEqual(validate(p,m),{"TEST-1"})
    def test_question_mismatch(self):
        p,m=fixture();m["question"]="Autre question"
        with self.assertRaises(ValueError):validate(p,m)
    def test_missing_chair(self):
        p,m=fixture();p["steps"][0]["role"]="mining"
        with self.assertRaises(ValueError):validate(p,m)
    def test_admissibility_cannot_be_promoted(self):
        p,m=fixture();m["claims"][0]["original_validation_status"]="VERIFIED"
        with self.assertRaises(ValueError):validate(p,m)
    def test_no_decision_authorization(self):
        p,m=fixture();p["decision_authorized"]=True
        with self.assertRaises(ValueError):validate(p,m)
    def test_missing_human_review(self):
        p,m=fixture();m["human_review_required"]=False
        with self.assertRaises(ValueError):validate(p,m)

if __name__=="__main__":unittest.main()
