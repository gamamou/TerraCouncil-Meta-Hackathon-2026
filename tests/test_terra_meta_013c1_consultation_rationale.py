import unittest
from src.terra_meta_013c_adaptive_council import run

E={"evidence_id":"E1","finding":"Confirmed wording in screened source"}
class TestRationale(unittest.TestCase):
 def test_no_consultation_explained(self):
  actions=iter([
   {"tool":"record_finding","summary":E["finding"],"evidence_ids":["E1"]},
   {"tool":"submit_decision","summary":"Provisional only","finding_ids":["F1"],
    "consultation_rationale":"One observation suffices to explain the concept; no cross-sector judgement."}
  ])
  r=run("Explain a concept",[E],"fake",caller=lambda *a:next(actions))
  self.assertEqual(r["consultations"],[])
  self.assertTrue(r["consultation_explained"])
  self.assertIn("no cross-sector",r["consultation_rationale"])
 def test_consultation_reason_saved(self):
  acts=iter([
   {"tool":"record_finding","summary":E["finding"],"evidence_ids":["E1"]},
   {"tool":"consult_scientific_agent","domain":"environment","question":"Assess interpretation limits",
    "reason":"Distinct environmental scrutiny is helpful","evidence_ids":["E1"]},
   {"tool":"submit_decision","summary":"Provisional","finding_ids":["F1"]}
  ])
  def call(model,*args):
   if model=="muse-wonder-1.0":
    return {"observations":[{"evidence_id":"E1","finding":E["finding"]}],
      "interpretation":[],"limits":["Not field validated"],"recommendations":[]}
   return next(acts)
  r=run("Assess",[E],"fake",caller=call)
  self.assertTrue(r["consultation_explained"])
  self.assertEqual(r["consultations"][0]["reason"],"Distinct environmental scrutiny is helpful")
if __name__=="__main__":unittest.main()
