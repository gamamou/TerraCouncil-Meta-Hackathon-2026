import unittest
from src.terra_meta_013b_muse_runtime import run

class TestMuseRuntime(unittest.TestCase):
 def test_model_selects_valid_actions(self):
  choices=iter([
   {"tool":"query_evidence","id":"E1"},
   {"tool":"record_finding","summary":"Recorded measurement A","evidence_ids":["E1"]},
   {"tool":"submit_decision","summary":"Provisional; more data needed","finding_ids":["F1"]}
  ])
  def model(model,instructions,payload,key):return next(choices)
  result=run("Explain metric", [{"evidence_id":"E1","finding":"Recorded measurement A"}],"fake",caller=model)
  self.assertEqual(result["status"],"PROVISIONAL_HUMAN_REVIEW")
  self.assertEqual(len(result["steps"]),3)
 def test_rejects_fabricated_fact(self):
  choices=iter([
   {"tool":"record_finding","summary":"invented","evidence_ids":["E1"]},
   {"tool":"submit_decision","summary":"Unsupported","finding_ids":["F1"]}
  ])
  result=run("What is known?",[{"evidence_id":"E1","finding":"Recorded measurement A"}],"fake",caller=lambda *a:next(choices))
  self.assertEqual(result["steps"][0]["verification"]["reason"],"FINDING_NOT_EXACT_SOURCE")
  self.assertIsNone(result["decision"])
 def test_abstain_without_evidence(self):
  self.assertEqual(run("Q",[],"fake")["status"],"ABSTAIN_NO_EVIDENCE")
if __name__=="__main__":unittest.main()
