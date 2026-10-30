import unittest
from tools.terra_meta_demo_010c_readiness import evaluate
class TestReadiness(unittest.TestCase):
 def setUp(self):
  self.data={"MiningPermit":[{"shape_uid":"a","has_observed_footprint":False}],
             "PilotCandidate":[{"shape_uid":"a"}],
             "RehabilitationSolution":[{"solution_id":"S"}],
             "PermitSpatialContext":[],"SiteRehabilitationRecommendation":[]}
 def test_complete_research_not_scientific_approval(self):
  trace={"status":"GENERATED_NEEDS_SCIENTIFIC_REVIEW","question":"rehabilitation interventions",
   "steps":[{"stage":"FAITH_TOOL_RESULT_"+str(i),"action":{"tool":"query_faith_data","entity":e},
     "result":[{"shape_uid":"a"}]} for i,e in enumerate(("MiningPermit","PilotCandidate","RehabilitationSolution"),1)]}
  result=evaluate(self.data,trace)
  self.assertTrue(result["coverage"]["is_complete"])
  self.assertEqual(result["decision_readiness"],"EVIDENCE_NOT_READY_FOR_SITE_PRESCRIPTIONS")
  self.assertEqual(result["authorization"],"NOT_AUTHORIZED_AUTOMATICALLY")
 def test_incomplete_catalog(self):
  trace={"question":"rehabilitation interventions","steps":[{"stage":"FAITH_TOOL_RESULT_1",
    "action":{"tool":"query_faith_data","entity":"MiningPermit"},"result":[{"shape_uid":"a"}]}]}
  self.assertEqual(evaluate(self.data,trace)["decision_readiness"],"RESEARCH_INCOMPLETE")
if __name__=="__main__":unittest.main()
