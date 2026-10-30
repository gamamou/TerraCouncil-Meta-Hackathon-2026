import unittest
from tools.terra_meta_demo_015_brief import assemble,classify
class Brief015(unittest.TestCase):
 def test_offline_brief_preserves_model_text(self):
  d={"schema_version":"DEMO-011","question":"Which sites?",
    "council":{"spark_revision":"UNCERTAIN: need field visit","wonder_critique":"Not enough evidence"},
    "scientific_readiness":{"decision_readiness":"EVIDENCE_NOT_READY_FOR_SITE_PRESCRIPTIONS","limitations":["no footprint"]},
    "research_coverage":{"is_complete":True}}
  b=assemble(d,{"tasks":[{"status":"PROPOSED_NOT_AUTHORIZED"}]},{"session_id":"test","passport_status":"UNREVIEWED_INTERNAL"})
  self.assertEqual(b["executive_brief"]["council_recommendations_verbatim"],"UNCERTAIN: need field visit")
  self.assertEqual(b["family"]["status"],"NOT_CLASSIFIED_BY_MODEL")
  self.assertEqual(b["follow_up"]["tracking_state"],"NOT_STARTED_PENDING_HUMAN_AUTHORIZATION")
 def test_meta_controls_family(self):
  calls=[]
  def fake(model,instruction,payload,key):
   calls.append(payload["question"]);return '{"families":["risk"],"rationale":"uncertainty"}'
  c=classify("Analyze uncertainty","fake",fake)
  self.assertIn('"risk"',c["raw_response"])
  self.assertEqual(calls,["Analyze uncertainty"])
if __name__=="__main__":unittest.main()
