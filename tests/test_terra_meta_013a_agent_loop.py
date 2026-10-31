import unittest
from src.terra_meta_013a_agent_loop import agent_loop,execute,CouncilState
class TestCouncil(unittest.TestCase):
 def test_refuses_unsupported(self):
  s=CouncilState("Question",{"e1":{"id":"e1","status":"SCREENED"}})
  self.assertFalse(execute(s,{"tool":"record_finding","summary":"unproven","evidence_ids":["bad"]})["ok"])
  self.assertEqual(s.findings,[])
 def test_model_chosen_actions(self):
  actions=iter([{"tool":"record_finding","summary":"Measured result requires review","evidence_ids":["e1"]},
    {"tool":"submit_decision","summary":"Provisional result","finding_ids":["F1"]}])
  s=agent_loop("What does the metric mean?",{"e1":{"id":"e1","status":"SCREENED"}},lambda _:next(actions))
  self.assertEqual(s.decision["status"],"PROVISIONAL_REQUIRES_HUMAN_REVIEW")
  self.assertEqual(len(s.events),2)
 def test_unknown_tool(self):
  self.assertFalse(execute(CouncilState("q",{}),{"tool":"delete_sources"})["ok"])
if __name__=="__main__":unittest.main()
