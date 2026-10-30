"""Offline guards for 010D2 audit and report."""
import sys,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d2_gpt_audit import assemble
from terra_council_010d2_report import summarize,report
class Test010D2(unittest.TestCase):
 def setUp(self):
  self.source="Scientifiquement exploratoire. Aucun constat de conformite."
  self.sha=hashlib.sha256(self.source.encode()).hexdigest()
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":[
   {"turn":i,"speaker":"esg" if i==4 else "chair","scientific_source_text":self.source}
   for i in range(1,20)]}
  self.claims=[{"claim_id":f"C{i:02d}","source_quote":q,"meaning":q,
   "importance":"MUST_KEEP" if i<4 else "METADATA_ONLY"} for i,q in enumerate([
   "Scientifiquement","exploratoire","Aucun constat","conformite"],1)]
  self.ex={"status":"CLAIMS_HUMAN_REVIEW_REQUIRED","source_sha256":self.sha,
   "claims":self.claims}
  self.g={"schema":"TERRA_COUNCIL_010D_GPT_REFERENCE_V1","role":"esg",
   "scientific_source_text":self.source,"spoken_text":"Exploratoire; aucune conformite."}
  self.rows=[{"claim_id":f"C{i:02d}","verdict":"PRESERVED" if i<4 else "METADATA_OMITTED"}
   for i in range(1,5)]
  self.audit={"source_sha256":self.sha,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
   "assessments":self.rows}
 def test_exact_source(self):
  self.assertEqual(assemble(self.p,self.ex,self.g)[1],self.sha)
  self.g["scientific_source_text"]="Altered."
  with self.assertRaises(ValueError):assemble(self.p,self.ex,self.g)
 def test_must_keep(self):
  s=summarize(self.audit,self.claims)
  self.assertEqual(s["must_keep_preserved"],3)
  self.assertEqual(s["metadata_omitted"],1)
 def test_human_gate(self):
  r=report(self.p,self.ex,self.g,self.audit,self.audit)
  self.assertFalse(r["scientific_approval"])
  self.assertFalse(r["audio_authorized"])
 def test_stale_audit(self):
  bad={**self.audit,"source_sha256":"bad"}
  with self.assertRaises(ValueError):report(self.p,self.ex,self.g,self.audit,bad)
if __name__=="__main__":unittest.main()
