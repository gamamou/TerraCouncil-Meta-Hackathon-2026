"""009H contextual roster tests. Synthetic data; no API calls."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009h_composition import compose
from terra_council_009g_exploratory import ADMITTED

def fixture(question="Quelles investigations scientifiques et garanties faut-il prioriser avant une décision de développement minier à Boké ?"):
    def claim(eid,dataset):
        return {"evidence_id":eid,"source_version":"test","finding":"Illustrative",
         "source":"https://example.org","method":"test","limitations":"Exploratory",
         "admissibility":ADMITTED,"decision_admissibility":"NOT_ADMISSIBLE_FOR_DECISION",
         "original_validation_status":"SCREENED_NOT_FIELD_VALIDATED","dataset":dataset}
    return {"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1","question":question,
     "scientific_status":"EXPLORATORY_DISCUSSION_ONLY","decision_authorized":False,
     "human_review_required":True,"claims":[claim("E1","WorldPop population"),claim("E2","WorldCover cropland")]}
class Tests009H(unittest.TestCase):
    def test_boke_experts(self):
        p=compose(fixture())
        self.assertEqual(p["active_experts"],["mining","environment","esg","communities","agriculture"])
    def test_chair_and_call_count(self):
        p=compose(fixture())
        self.assertEqual(p["steps"][0]["role"],"scientific_chair")
        self.assertEqual(p["steps"][-1]["phase"],"deliberation")
        self.assertEqual(len(p["steps"]),13)
        self.assertEqual(p["meta_calls"],0)
    def test_no_unsupported_decision(self):
        p=compose(fixture())
        self.assertFalse(p["decision_authorized"])
        self.assertFalse(p["audio_authorized"])
    def test_narrow_question_no_experts_forced(self):
        p=compose(fixture("Quels sont les risques miniers ?"))
        self.assertEqual(p["active_experts"],["mining","communities"])
        self.assertNotIn("esg",p["active_experts"])
    def test_invalid_admissibility_rejected(self):
        x=fixture();x["claims"][0]["original_validation_status"]="VERIFIED"
        with self.assertRaises(ValueError):compose(x)
if __name__=="__main__":unittest.main()
