"""009N offline validation tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009n_audit import audit
class Tests(unittest.TestCase):
 def setUp(self):
  roles=["scientific_chair"]+["mining","environment","esg","communities","agriculture"]+["scientific_chair"]+["mining","environment","esg"]+["scientific_chair"]+["environment","agriculture","communities"]+["scientific_chair"]+["esg","communities","mining","scientific_chair"]
  phases=["opening"]+["initial_position"]*5+["targeted_question"]+["response_to_prior"]*3+["targeted_question"]+["response_to_prior"]*3+["targeted_question"]+["response_to_prior"]*3+["decision_brief"]
  self.agenda={"evidence_ids":["E1"],"steps":[{"role":r,"phase":p,"max_words":330} for r,p in zip(roles,phases)]}
  turns=[{"role":r,"phase":p,"text":"Proposition methodologique, limites et incertitudes, priorites, conditions et arbitrages.",
          "evidence_ids":["E1"]} for r,p in zip(roles,phases)]
  turns[15]["evidence_ids"]=[]
  turns[17]["evidence_ids"]=[]
  self.debate={"status":"SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED",
    "decision_authorized":False,"audio_authorized":False,"turns":turns}
 def test_complete_requires_review(self):
  self.assertEqual(audit(self.debate,self.agenda)["status"],"HUMAN_SCIENTIFIC_REVIEW_REQUIRED")
 def test_recovered_flags(self):
  flags=audit(self.debate,self.agenda)["review_flags"]
  self.assertIn("TURN_18_RECOVERED_RESPONSE_REVIEW",flags)
 def test_role_guard(self):
  self.debate["turns"][3]["role"]="scientific_chair"
  self.assertIn("TURN_4_ROLE_PHASE",audit(self.debate,self.agenda)["issues"])
 def test_audio_guard(self):
  self.debate["audio_authorized"]=True
  self.assertIn("AUTHORIZATION_GATE_INVALID",audit(self.debate,self.agenda)["issues"])
if __name__=="__main__":unittest.main()
