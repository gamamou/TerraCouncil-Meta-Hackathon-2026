import unittest
from tools.terra_meta_demo_012_action_plan import plan
class ActionPlan012(unittest.TestCase):
 def test_gap_tasks_not_site_prescriptions(self):
  d={"schema_version":"DEMO-011","question":"Which five?",
   "qa":{"warnings":["RESEARCH_COVERAGE_INCOMPLETE","TRACE_HAS_NO_SNAPSHOT_HASH"]},
   "scientific_readiness":{"decision_readiness":"RESEARCH_INCOMPLETE",
     "coverage":{"is_complete":False},
     "checkpoints":{"site_footprint_evidence_present":False,
       "site_spatial_evidence_present":False,"site_degradation_diagnostics_present":False,
       "catalog_consulted":False}}}
  r=plan(d)
  self.assertGreaterEqual(len(r["tasks"]),6)
  self.assertTrue(all(t["status"]=="PROPOSED_NOT_AUTHORIZED" and t["site_scope"]=="NOT_ASSIGNED" for t in r["tasks"]))
  self.assertEqual(r["authorization"],"PLANNING_ONLY_REQUIRES_HUMAN_APPROVAL")
 def test_bad_input(self):
  with self.assertRaises(ValueError):plan({"schema_version":"fake"})
if __name__=="__main__":unittest.main()
