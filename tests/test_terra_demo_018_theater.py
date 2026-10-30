import unittest,tempfile,json
from pathlib import Path
from tools.terra_meta_demo_018_theater import build,render
class Theater018(unittest.TestCase):
 def test_source_exact_and_no_fake_audio(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   (root/"01_trace.json").write_text(json.dumps({"question":"A < B","steps":[
    {"stage":"SPARK_RESEARCH_PLAN","response":"Explore safely","model":"muse-spark-1.3"},
    {"stage":"WONDER_CRITIQUE","response":"No evidence","model":"muse-wonder-1.0"},
    {"stage":"SPARK_REVISION","response":"<NO FINAL DECISION>","model":"muse-spark-1.3"}]}))
   (root/"05_scientific_brief.json").write_text(json.dumps({"family":{"status":"NOT_CLASSIFIED_BY_MODEL"},
    "executive_brief":{"scientific_readiness":"RESEARCH_INCOMPLETE"},
    "follow_up":{"proposed_investigations":[{"action":"Inspect","status":"PROPOSED_NOT_AUTHORIZED"}]}}))
   (root/"04_passport_preview.json").write_text(json.dumps({"session_id":"x","passport_status":"UNREVIEWED_INTERNAL"}))
   x=build(root)
   self.assertEqual(x["audio"]["status"],"NOT_GENERATED")
   self.assertEqual(len(x["interventions"]),3)
   self.assertEqual(x["interventions"][-1]["text"],"<NO FINAL DECISION>")
   h=render(x)
   self.assertIn("&lt;NO FINAL DECISION&gt;",h)
   self.assertNotIn("<NO FINAL DECISION>",h)
if __name__=="__main__":unittest.main()
