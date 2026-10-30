import json,tempfile,unittest
from pathlib import Path
from tools.terra_meta_demo_010b_adaptive import run,coverage,parse_decision

def fixture():
    return {"PilotCandidate":[{"shape_uid":str(i)} for i in range(5)],
      "MiningPermit":[{"shape_uid":str(i)} for i in range(5)],
      "RehabilitationSolution":[{"solution_id":"SOL-CAT-00001","solution_name":"Field inspection"}],
      "PermitSpatialContext":[],"SiteRehabilitationRecommendation":[]}

class TestAdaptive010B(unittest.TestCase):
    def test_coverage(self):
        cov=coverage(fixture(),[],"propose rehabilitation interventions")
        self.assertEqual(len(cov["missing_required"]),3)
        self.assertIn("PermitSpatialContext",cov["unavailable_sources"])
    def test_reject_unauthorized(self):
        with self.assertRaises(ValueError):parse_decision('{"tool":"run_python"}')
    def test_model_selected_three_sources(self):
        decisions=iter(['{"tool":"query_faith_data","entity":"MiningPermit","limit":50}',
           '{"tool":"query_faith_data","entity":"PilotCandidate","limit":50}',
           '{"tool":"query_faith_data","entity":"RehabilitationSolution","limit":50}',
           '{"tool":"finish_research","reason":"All relevant sources consulted"}'])
        def mock(model,instruction,payload,key):
            if "Plan essential" in instruction:return "Need 3 entities."
            if "JSON tool decision" in instruction:return next(decisions)
            if model=="muse-wonder-1.0":return "No field-validated footprint."
            return "No final five, conditional inspection only. SOL-CAT-00001."
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"test.json"
            result=run(fixture(),"Choose five sites and rehabilitation interventions", "test",path,mock,5)
            self.assertEqual(result["status"],"GENERATED_NEEDS_SCIENTIFIC_REVIEW")
            self.assertTrue(result["coverage"]["is_complete"])
            self.assertEqual(len([x for x in result["steps"] if x["stage"].startswith("FAITH_TOOL_RESULT")]),3)
            self.assertEqual(json.loads(path.read_text())["citation_check"]["unknown_solution_ids"],[])
    def test_reject_early_stop(self):
        choices=iter(['{"tool":"finish_research","reason":"done"}',
          '{"tool":"query_faith_data","entity":"MiningPermit"}',
          '{"tool":"query_faith_data","entity":"PilotCandidate"}',
          '{"tool":"query_faith_data","entity":"RehabilitationSolution"}'])
        def mock(model,instruction,payload,key):
            if "Plan essential" in instruction:return "Need research."
            if "JSON tool decision" in instruction:return next(choices)
            if model=="muse-wonder-1.0":return "Critique"
            return "Final needs review"
        with tempfile.TemporaryDirectory() as folder:
            result=run(fixture(),"rehabilitation solutions","test",Path(folder)/"log.json",mock,4)
            self.assertTrue(any(x["stage"]=="COVERAGE_GATE_REJECTED_STOP" for x in result["steps"]))
            self.assertTrue(result["coverage"]["is_complete"])
if __name__=="__main__":unittest.main()
