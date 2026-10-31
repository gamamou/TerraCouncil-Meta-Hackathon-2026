"""010D offline schema and scientific immutability tests."""
import sys,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d_pipeline import source_info,validate_claims,verify_oral,verify_audit
from terra_council_010d_compare import compare
class Tests(unittest.TestCase):
 def setUp(self):
  self.source="Aucune conformite. Donnees WorldPop non validees terrain."
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1",
   "turns":[{"turn":i,"speaker":"esg" if i==4 else "mining",
    "scientific_source_text":self.source} for i in range(1,20)]}
  self.sha=hashlib.sha256(self.source.encode("utf-8")).hexdigest()
  self.claims=[{"claim_id":"C01","source_quote":"Aucune conformite",
   "meaning":"Pas de constat de conformite","importance":"MUST_KEEP"},
   {"claim_id":"C02","source_quote":"Donnees WorldPop",
   "meaning":"Donnees de population","importance":"MAY_SUMMARIZE"},
   {"claim_id":"C03","source_quote":"non validees terrain",
   "meaning":"Pas de validation terrain","importance":"MUST_KEEP"},
   {"claim_id":"C04","source_quote":"WorldPop",
   "meaning":"Nom de la source","importance":"METADATA_ONLY"}]
 def test_claim_quotes(self):
  self.assertEqual(len(validate_claims({"claims":self.claims},self.source)),4)
  self.claims[0]["source_quote"]="FAKE"
  with self.assertRaises(ValueError):validate_claims({"claims":self.claims},self.source)
 def test_oral_role(self):
  with self.assertRaises(ValueError):verify_oral({"role":"mining","spoken_text":"Hello",
   "covered_claim_ids":[],"metadata_omitted_claim_ids":[]},self.claims)
 def test_audit_complete(self):
  report={"assessments":[{"claim_id":c["claim_id"],"verdict":"PRESERVED"}
   for c in self.claims]}
  self.assertTrue(verify_audit(report,self.claims))
  report["assessments"].pop()
  with self.assertRaises(ValueError):verify_audit(report,self.claims)
 def test_comparison_source_guard(self):
  e={"source_sha256":self.sha,"status":"CLAIMS_HUMAN_REVIEW_REQUIRED","claims":self.claims}
  m={"source_sha256":self.sha,"status":"ORAL_HUMAN_REVIEW_REQUIRED",
   "spoken_text":"Aucune conformite, verification necessaire."}
  g={"schema":"TERRA_COUNCIL_010D_GPT_REFERENCE_V1","role":"esg",
   "scientific_source_text":self.source,"spoken_text":"Les donnees restent non validees."}
  self.assertEqual(len(compare(self.p,e,m,g)["candidates"]),2)
  g["scientific_source_text"]="Autre dossier."
  with self.assertRaises(ValueError):compare(self.p,e,m,g)
if __name__=="__main__":unittest.main()
