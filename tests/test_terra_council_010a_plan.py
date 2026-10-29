"""010A offline orchestration guards."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010a_plan import plan
class Tests(unittest.TestCase):
 def setUp(self):
  self.m={"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1","decision_authorized":False,
   "question":"Boke?","claims":[{"evidence_id":"E1","admissibility":"ADMISSIBLE_FOR_EXPLORATORY_DEBATE",
   "original_validation_status":"SCREENED_NOT_FIELD_VALIDATED"}]}
  self.a={"schema":"TERRA_COUNCIL_009K_AGENDA_V1","question":"Boke?","evidence_ids":["E1"],
   "steps":[{"role":"scientific_chair" if i in (0,18) else "mining",
   "phase":"opening" if i==0 else "decision_brief" if i==18 else "response_to_prior","max_words":120} for i in range(19)]}
 def test_models(self):
  x=plan(self.m,self.a)
  self.assertEqual(x["routing"][0]["model"],"muse-wonder-1.0")
  self.assertEqual(x["routing"][1]["model"],"muse-spark-1.3")
  self.assertEqual(x["api_calls"],0)
  self.assertFalse(x["audio_authorized"])
 def test_wrong_evidence(self):
  self.a["evidence_ids"]=["NOT_E1"]
  with self.assertRaises(ValueError):plan(self.m,self.a)
 def test_no_decision(self):
  self.m["decision_authorized"]=True
  with self.assertRaises(ValueError):plan(self.m,self.a)
if __name__=="__main__":unittest.main()
