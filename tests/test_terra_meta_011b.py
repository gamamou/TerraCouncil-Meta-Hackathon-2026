"""011B offline planner tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_meta_011b_planner import policy
E={"schema":"TERRA_META_011B_EVIDENCE_V1","sources":[]}
class PlannerTests(unittest.TestCase):
 def test_missing_evidence_is_explicit(self):
  p=policy("Quel risque minier pour les communautés ?",E,8,12)
  self.assertEqual(p["evidence_status"],"INSUFFICIENT_EVIDENCE")
  self.assertIn("mining",p["selected_experts"])
  self.assertIn("communities",p["selected_experts"])
  self.assertFalse(p["model_calls_authorized"])
  self.assertFalse(p["audio_authorized"])
 def test_reject_unproven_source_metadata(self):
  with self.assertRaises(ValueError):policy("eau",{"schema":E["schema"],"sources":[{"id":"unknown"}]},8,12)
 def test_limits_are_enforced(self):
  with self.assertRaises(ValueError):policy("eau",E,2,12)
  with self.assertRaises(ValueError):policy("eau",E,8,-1)
 def test_role_sequence_and_cap(self):
  p=policy("Agriculture et eau",E,4,0)
  self.assertEqual(p["turn_count"],4)
  self.assertEqual(p["steps"][0]["role"],"president")
  self.assertEqual(p["steps"][-1]["role"],"president")
  self.assertEqual(p["actual_meta_calls"],0)
 def test_screening_is_not_validation(self):
  evidence={"schema":E["schema"],"sources":[{"id":"sample","provider":"test","version":"1","license":"test",
    "provenance":"test","coverage":"test","limitations":"not field verified","validation":"SCREENED_NOT_FIELD_VALIDATED"}]}
  p=policy("eau",evidence,8,12)
  self.assertEqual(p["evidence_status"],"SCREENING_READY_NOT_FIELD_VALIDATED")
  self.assertFalse(p["may_form_empirical_conclusions"])
if __name__=="__main__":unittest.main()
