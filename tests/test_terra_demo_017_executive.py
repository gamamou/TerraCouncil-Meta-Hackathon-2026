import unittest
from tools.terra_meta_demo_017_executive import render
class Executive017(unittest.TestCase):
 def sample(self):
  return {"schema_version":"DEMO-015","question":"Mine <risk>",
   "executive_brief":{"scientific_readiness":"RESEARCH_INCOMPLETE",
    "research_coverage":{"is_complete":False,"consulted":["MiningPermit"],"missing_required":["RehabilitationSolution"]},
    "evidence_limitations":["No field proof"],"council_recommendations_verbatim":"NO TOP 5: <unverified>",
    "critic_assessment_verbatim":"Wonder: more evidence needed"},
   "follow_up":{"proposed_investigations":[{"task_id":"INV-001","action":"Inspect imagery","status":"PROPOSED_NOT_AUTHORIZED"}]},
   "passport":{"status":"UNREVIEWED_INTERNAL"},"audio":{"status":"NOT_GENERATED"}}
 def test_report_retains_claims_and_guardrails(self):
  h=render(self.sample())
  self.assertIn("NO TOP 5: &lt;unverified&gt;",h)
  self.assertIn("Wonder: more evidence needed",h)
  self.assertIn("RehabilitationSolution",h)
  self.assertIn("PROPOSED_NOT_AUTHORIZED",h)
  self.assertIn("NOT_GENERATED",h)
  self.assertNotIn("<risk>",h)
 def test_reject_bad_schema(self):
  with self.assertRaises(ValueError):render({"schema_version":"BAD"})
if __name__=="__main__":unittest.main()
