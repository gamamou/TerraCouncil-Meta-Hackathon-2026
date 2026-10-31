import unittest
from tools.terra_demo_002_join_audit import audit
class TestJoinAudit(unittest.TestCase):
 def test_shape_uid_not_key_alias(self):
  d={"PilotCandidate":[{"shape_uid":"A","score_0_100":100,"permit_record_key":"pilot|A"}],
     "MiningPermit":[{"shape_uid":"A","permit_record_key":"national|A","score_0_100":100}],
     "PermitSpatialContext":[],"RehabilitationSolution":[{"solution_id":"S1"}]}
  r=audit(d)
  self.assertEqual(r["candidates_with_unique_permit"],1)
  self.assertEqual(r["candidates_with_unique_spatial_context"],0)
  self.assertEqual(r["site_join_audit"][0]["spatial_coverage"],"NOT_CONFIRMED")
 def test_no_false_unique_join(self):
  d={"PilotCandidate":[{"shape_uid":"X"}],"MiningPermit":[{"shape_uid":"X"},{"shape_uid":"X"}]}
  self.assertEqual(audit(d)["site_join_audit"][0]["permit_match_count"],2)
if __name__=="__main__":unittest.main()
