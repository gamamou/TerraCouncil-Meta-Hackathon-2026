import tempfile, unittest, json
from pathlib import Path
from tools import terra_meta_020_end_to_end as app
class Unified020(unittest.TestCase):
 def test_history_only_completed_sessions(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   s=root/"session_a"/"artifacts";s.mkdir(parents=True)
   (s/"05_scientific_brief.json").write_text("{}")
   (root/"session_b").mkdir()
   found=app.sessions(root)
   self.assertEqual(found,[s])
 def test_page_question_and_no_transcript(self):
  old=app.STATE.copy()
  class Args:storage=Path("__unavailable_terra_test__")
  prior=getattr(app,"ARGS",None)
  try:
   app.ARGS=Args()
   app.STATE.update({"busy":False,"phase":"READY","message":"Prêt","session":"missing","audio":None})
   p=app.webpage()
   self.assertIn('action="/start"',p)
   self.assertIn('name="audio"',p)
   self.assertIn("Decision Passport",p)
   self.assertNotIn("SPARK_REVISION",p)
   self.assertNotIn('location.reload()',p)
  finally:
   app.STATE.clear();app.STATE.update(old)
   if prior is None:delattr(app,"ARGS")
   else:app.ARGS=prior
if __name__=="__main__":unittest.main()
