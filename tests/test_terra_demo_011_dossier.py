import unittest
from tools.terra_meta_demo_011_dossier import build
class Dossier011(unittest.TestCase):
 def setUp(self):
  self.data={"MiningPermit":[{"shape_uid":str(i),"has_observed_footprint":False} for i in range(5)],
   "PilotCandidate":[{"shape_uid":str(i)} for i in range(5)],
   "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001"}],
   "PermitSpatialContext":[],"SiteRehabilitationRecommendation":[]}
 def test_incomplete_trace_never_approved(self):
  trace={"question":"rehabilitation","status":"GENERATED_NEEDS_SCIENTIFIC_REVIEW",
    "steps":[{"stage":"SPARK_REVISION","response":"Investigate SOL-CAT-00001"}]}
  dossier=build(self.data,trace)
  self.assertFalse(dossier["qa"]["automated_release_allowed"])
  self.assertIn("RESEARCH_COVERAGE_INCOMPLETE",dossier["qa"]["warnings"])
  self.assertEqual(dossier["scientific_readiness"]["decision_readiness"],"RESEARCH_INCOMPLETE")
 def test_invalid_citation_detected(self):
  trace={"question":"rehabilitation","status":"GENERATED_NEEDS_SCIENTIFIC_REVIEW",
   "steps":[{"stage":"SPARK_REVISION","response":"GUIDSHAPE:BAD00001 and SOL-CAT-99999"}]}
  d=build(self.data,trace)
  self.assertIn("UNKNOWN_SITE_REFERENCE",d["qa"]["warnings"])
  self.assertIn("UNKNOWN_SOLUTION_REFERENCE",d["qa"]["warnings"])
if __name__=="__main__":unittest.main()
