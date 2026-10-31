import unittest
from src.terra_meta_013c_adaptive_council import run
E={"evidence_id":"E1","finding":"Verified source wording"}
class TestAdaptive(unittest.TestCase):
 def test_spark_selects_wonder_without_fixed_turns(self):
  actions=iter([
   {"tool":"record_finding","summary":"Verified source wording","evidence_ids":["E1"]},
   {"tool":"consult_scientific_agent","domain":"environment","question":"What are the limits?","evidence_ids":["E1"]},
   {"tool":"submit_decision","summary":"Provisional only","finding_ids":["F1"]}])
  def caller(model,prompt,payload,key):
   if model=="muse-wonder-1.0":
    return {"observations":[{"evidence_id":"E1","finding":"Verified source wording"}],
      "interpretation":["Tentative interpretation"],"limits":["Not field validated"],"recommendations":["Gather data"]}
   return next(actions)
  r=run("Assess evidence",[E],"fake",caller=caller)
  self.assertEqual(r["status"],"PROVISIONAL_HUMAN_REVIEW")
  self.assertEqual(len(r["consultations"]),1)
  self.assertEqual(len(r["steps"]),3)
 def test_blocks_expert_fabrication(self):
  choices=iter([{"tool":"consult_scientific_agent","domain":"environment","question":"Assess","evidence_ids":["E1"]},
                {"tool":"submit_decision","summary":"premature","finding_ids":["F1"]}])
  def caller(model,*args):
   if model=="muse-wonder-1.0":return {"observations":[{"evidence_id":"E1","finding":"Fabricated"}],"interpretation":[],"limits":[],"recommendations":[]}
   return next(choices)
  r=run("Evaluate",[E],"fake",caller=caller)
  self.assertEqual(r["steps"][0]["verification"]["reason"],"EXPERT_EVIDENCE_CHECK_FAILED")
  self.assertIsNone(r["decision"])
 def test_single_agent_allowed(self):
  actions=iter([{"tool":"record_finding","summary":"Verified source wording","evidence_ids":["E1"]},
                {"tool":"submit_decision","summary":"Provisional","finding_ids":["F1"]}])
  r=run("Explain",[E],"fake",caller=lambda *args:next(actions))
  self.assertEqual(r["consultations"],[])
if __name__=="__main__":unittest.main()
