import tempfile,unittest,json
from pathlib import Path
from tools.terra_meta_demo_013_integrated import write_bundle
class Integrated013(unittest.TestCase):
 def setUp(self):
  self.data={"MiningPermit":[{"shape_uid":str(i),"has_observed_footprint":False} for i in range(5)],
    "PilotCandidate":[{"shape_uid":str(i)} for i in range(5)],
    "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001"}],
    "PermitSpatialContext":[],"SiteRehabilitationRecommendation":[]}
 def test_replay_bundle_and_passport(self):
  trace={"status":"GENERATED_NEEDS_SCIENTIFIC_REVIEW","question":"rehabilitation",
         "steps":[{"stage":"SPARK_REVISION","response":"Insufficient evidence"}]}
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp)/"session"
   result=write_bundle(self.data,trace,folder,"session")
   self.assertEqual(result["status"],"BUNDLE_GENERATED_NEEDS_HUMAN_REVIEW")
   self.assertEqual(len(list(folder.glob("*.json"))),4)
   p=json.loads((folder/"04_passport_preview.json").read_text())
   self.assertFalse(p["human_review"]["approved"])
   self.assertEqual(p["audio"]["status"],"NOT_GENERATED")
   self.assertEqual(p["scientific_readiness"],"RESEARCH_INCOMPLETE")
   with self.assertRaises(FileExistsError):write_bundle(self.data,trace,folder,"session")
 def test_incomplete_trace_blocked(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(ValueError):write_bundle(self.data,{"status":"INTERRUPTED"},Path(temp)/"x","x")
if __name__=="__main__":unittest.main()
