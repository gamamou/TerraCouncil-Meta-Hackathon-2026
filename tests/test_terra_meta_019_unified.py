import unittest
from tools.terra_meta_019_unified import page,STATE
class Unified019(unittest.TestCase):
 def test_landing_page_no_transcript(self):
  old=STATE.copy()
  try:
   STATE.update({"busy":False,"message":"Prêt","session":"missing","audio":None})
   p=page()
   self.assertIn("Votre question scientifique",p)
   self.assertIn('action="/start"',p)
   self.assertIn("Decision Passport",p)
   self.assertNotIn("SPARK_REVISION",p)
   self.assertNotIn("<audio controls",p)
  finally:STATE.clear();STATE.update(old)
if __name__=="__main__":unittest.main()
