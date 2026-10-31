import tempfile,unittest
from pathlib import Path
from tools.terra_meta_026_translation import get_english
from tools.terra_meta_025_pdf import generate
class BilingualDeliverableTests(unittest.TestCase):
 def test_english_cached_without_repeated_model_call(self):
  calls=[]
  def fake(model,instruction,payload,key):
   calls.append(payload["source_text"])
   return "English: "+payload["source_text"]
  brief={"question":"Question initiale","executive_brief":{
   "council_recommendations_verbatim":"Réponse", "critic_assessment_verbatim":"Critique",
   "scientific_readiness":"NOT_READY","evidence_limitations":[]}}
  with tempfile.TemporaryDirectory() as temp:
   first=get_english("brief",brief,temp,"fake",fake)
   second=get_english("brief",brief,temp,None,fake)
   self.assertEqual(first,second)
   self.assertEqual(len(calls),3)
   self.assertEqual(first["executive_brief"]["scientific_readiness"],"NOT_READY")
 def test_pdf_both_languages(self):
  for language in ("fr","en"):
   for kind in ("brief","passport"):
    data={"question":"FAITH","executive_brief":{"council_recommendations_verbatim":"Conclusion",
      "critic_assessment_verbatim":"Objection","evidence_limitations":[]},
      "session_id":"s1","passport_status":"PENDING","human_review":{"status":"PENDING"}}
    self.assertTrue(generate(kind,data,language=language).startswith(b"%PDF"))
if __name__=="__main__":unittest.main()
