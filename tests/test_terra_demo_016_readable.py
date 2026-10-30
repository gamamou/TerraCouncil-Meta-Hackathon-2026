import unittest
from tools.terra_meta_demo_016_readable import render,tracker
class TestDemo016(unittest.TestCase):
 def test_escape_and_original_text(self):
  b={"question":"<script>alert(1)</script>","executive_brief":{"scientific_readiness":"NOT_READY",
      "council_recommendations_verbatim":"No evidence < 5",
      "critic_assessment_verbatim":"Check field"},"follow_up":{"proposed_investigations":[]}}
  h=render(b)
  self.assertNotIn("<script>",h)
  self.assertIn("No evidence &lt; 5",h)
 def test_tracker_never_approved(self):
  b={"passport":{"session_id":"session"},"follow_up":{"proposed_investigations":[
    {"task_id":"INV-001","action":"Survey site","proposed_owner_role":"Scientist","status":"PROPOSED_NOT_AUTHORIZED"}]}}
  t=tracker(b)
  self.assertEqual(t["tasks"][0]["status"],"PROPOSED_NOT_AUTHORIZED")
  self.assertIsNone(t["tasks"][0]["owner_assigned"])
  self.assertEqual(t["status"],"DRAFT_UNAUTHORIZED")
if __name__=="__main__":unittest.main()
