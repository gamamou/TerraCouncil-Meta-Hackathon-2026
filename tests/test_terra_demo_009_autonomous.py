import tempfile,unittest,json
from pathlib import Path
from tools.terra_meta_demo_009_autonomous import extract_action,run

class TestDemo009(unittest.TestCase):
 def test_action_parser(self):
  self.assertEqual(extract_action('Je consulte FAITH. {"tool":"discover_faith_data"}')["tool"],"discover_faith_data")
  with self.assertRaises(ValueError):extract_action('{"tool":"match_rehabilitation_solutions"}')
 def test_offline_execution_and_audit(self):
  data={"PilotCandidate":[{"shape_uid":str(i)} for i in range(5)],
        "MiningPermit":[{"shape_uid":str(i),"national_rank":i} for i in range(5)],
        "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001","solution_name":"Inspection"}]}
  calls=[]
  def mock(model,instruction,payload,key):
   calls.append(model)
   if len(calls)==1:return "Je dois examiner les candidats et les permis."
   if len(calls)==2:return '{"tool":"query_faith_data","entity":"PilotCandidate","limit":5}'
   if len(calls)==3:return '{"tool":"query_faith_data","entity":"RehabilitationSolution","limit":5}'
   if len(calls)==4:return "Les choix restent conditionnels."
   return "Les cinq candidats nécessitent une vérification. SOL-CAT-00001."
  with tempfile.TemporaryDirectory() as temp:
   target=Path(temp)/"trace.json"
   result=run(data,"Quels sites prioritaires?", "fake",target,caller=mock)
   self.assertEqual(result["status"],"GENERATED_NEEDS_SCIENTIFIC_REVIEW")
   self.assertEqual(len(calls),5)
   self.assertEqual(calls[-2:],["muse-wonder-1.0","muse-spark-1.3"])
   self.assertEqual(len([x for x in result["steps"] if x["stage"].startswith("FAITH_TOOL_RESULT")]),2)
   self.assertEqual(json.loads(target.read_text())["citation_check"]["unknown_solution_ids"],[])
if __name__=="__main__":unittest.main()
