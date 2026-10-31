import unittest
from tools.terra_meta_025_pdf import generate
class ExecutivePDF(unittest.TestCase):
 def test_concise_and_detailed_pdfs_in_two_languages(self):
  data={"question":"Résilience climatique","executive_brief":{
     "scientific_readiness":"EVIDENCE_NOT_READY_FOR_SITE_PRESCRIPTIONS",
     "council_recommendations_verbatim":"# Synthèse\nApproche intégrée conditionnelle, sans recommandation de site.",
     "critic_assessment_verbatim":"# Conclusion\nLes données locales sont insuffisantes.",
     "evidence_limitations":["Aucune preuve locale validée"]},
     "follow_up":{"proposed_investigations":[{"action":"Vérifier les sources"}]}}
  for lang in ("fr","en"):
   for detailed in (True,False):
    pdf=generate("brief",data,language=lang,detailed=detailed)
    self.assertTrue(pdf.startswith(b"%PDF"))
    self.assertGreater(len(pdf),800)
if __name__=="__main__":unittest.main()
