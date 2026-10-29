"""010B: offline validation tests; no Meta calls."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010b_reasoning import evidence_for,payload,check
class Tests(unittest.TestCase):
 def setUp(self):
  self.manifest={"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1",
    "decision_authorized":False,"claims":[{"evidence_id":"E1",
    "finding":"Cartographie exploratoire","limitations":"Pas de validation terrain",
    "admissibility":"ADMISSIBLE_FOR_EXPLORATORY_DEBATE",
    "original_validation_status":"SCREENED_NOT_FIELD_VALIDATED"}]}
 def test_reasoning_parameter(self):
  self.assertEqual(payload("muse-spark-1.3","high","Question",evidence_for(self.manifest))["reasoning_effort"],"high")
 def test_guard(self):
  with self.assertRaises(ValueError):check({"decision_authorized":True,"findings":[]},evidence_for(self.manifest))
 def test_refs(self):
  with self.assertRaises(ValueError):check({"decision_authorized":False,"findings":[{"statement":"x","evidence_ids":["BAD"]}]},evidence_for(self.manifest))
 def test_manifest(self):
  self.manifest["decision_authorized"]=True
  with self.assertRaises(ValueError):evidence_for(self.manifest)
if __name__=="__main__":unittest.main()
