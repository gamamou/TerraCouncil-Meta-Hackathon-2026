import json,tempfile,unittest
from pathlib import Path
from tools.terra_meta_demo_005_three_stage import run

class TestDemo005(unittest.TestCase):
 def test_three_stages_and_checkpoint(self):
  data={"PilotCandidate":[{"shape_uid":str(i),"score_0_100":100} for i in range(5)],
        "MiningPermit":[{"shape_uid":str(i),"national_rank":i,
         "has_observed_footprint":False,"confidence_level":"low"} for i in range(5)],
        "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001","solution_name":"Suivi"}]}
  seen=[]
  def mock(model,instruction,payload,key):
   seen.append(model)
   return "Conclusion provisoire, besoin de validation terrain."
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/"trace.json"
   result=run(data,"Proposer cinq candidats", "fake",output,caller=mock)
   self.assertEqual(result["status"],"GENERATED_NEEDS_SCIENTIFIC_REVIEW")
   self.assertEqual(len(result["calls"]),3)
   self.assertEqual(seen,["muse-spark-1.3","muse-wonder-1.0","muse-spark-1.3"])
   self.assertEqual(json.loads(output.read_text())["status"],"GENERATED_NEEDS_SCIENTIFIC_REVIEW")
 def test_preserve_partial_progress_on_failure(self):
  data={"PilotCandidate":[{"shape_uid":str(i)} for i in range(5)],
        "MiningPermit":[{"shape_uid":str(i)} for i in range(5)],
        "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001"}]}
  calls=[]
  def flaky(model,instruction,payload,key):
   calls.append(model)
   if len(calls)==2:raise RuntimeError("test failure")
   return "Spark preview"
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/"trace.json"
   result=run(data,"Question", "fake",output,caller=flaky)
   self.assertEqual(result["status"],"INTERRUPTED_DO_NOT_AUTORETRY")
   self.assertEqual(len(result["calls"]),1)
   self.assertEqual(json.loads(output.read_text())["calls"][0]["stage"],"SPARK_INITIAL")
if __name__=="__main__":unittest.main()
