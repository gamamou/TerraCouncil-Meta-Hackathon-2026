import unittest
from tools.terra_demo_003_preflight import preflight
class TestDemo003(unittest.TestCase):
 def test_requires_five_real_joins(self):
  candidates=[{"shape_uid":str(i),"score_0_100":100} for i in range(5)]
  d={"PilotCandidate":candidates,
     "MiningPermit":[{"shape_uid":str(i)} for i in range(4)],
     "RehabilitationSolution":[{"solution_id":"CAT1"}]}
  self.assertEqual(preflight(d)["status"],"BLOCKED_INSUFFICIENT_PERMIT_JOINS")
 def test_allows_exploratory_when_joins_exist(self):
  candidates=[{"shape_uid":str(i),"score_0_100":100} for i in range(5)]
  d={"PilotCandidate":candidates,
     "MiningPermit":[{"shape_uid":str(i),"has_observed_footprint":False} for i in range(5)],
     "RehabilitationSolution":[{"solution_id":"CAT1"}]}
  r=preflight(d)
  self.assertEqual(r["status"],"READY_FOR_EXPLORATORY_MUSE_DEMO")
  self.assertEqual(r["audit"]["candidates_with_unique_spatial_context"],0)
if __name__=="__main__":unittest.main()
