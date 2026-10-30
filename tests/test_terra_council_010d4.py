"""010D4 offline tests of claim locks, prior-turn audits and oral candidate."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d4_director import plan_context,validate_candidate
from terra_council_010d3_dialogue import path
class Tests(unittest.TestCase):
 def setUp(self):
  self.src="Protocole ecrit et revue independante; pas de conformite."
  self.sha=hashlib.sha256(self.src.encode()).hexdigest()
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":[
   {"turn":i,"speaker":"esg" if i==4 else "scientific_chair",
    "scientific_source_text":self.src} for i in range(1,20)]}
  self.claims=[
   {"claim_id":f"C{i:02d}","source_quote":x,"meaning":x,
    "importance":"MUST_KEEP"} for i,x in enumerate([
     "Protocole","ecrit","revue","independante"],1)]
 def make(self,root):
  for i in range(1,4):
   speech=f"Intervention scientifique {i}, sans conclusion non prouvee."
   sha=hashlib.sha256(speech.encode()).hexdigest()
   path(root,i,"oral").write_text(json.dumps({"status":"ORAL_HUMAN_REVIEW_REQUIRED",
    "source_sha256":"s"+str(i),"role":"president","spoken_text":speech}),encoding="utf-8")
   path(root,i,"audit").write_text(json.dumps({"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
    "source_sha256":"s"+str(i),"oral_sha256":sha,
    "unsupported_additions":[],"critical_omissions":[]}),encoding="utf-8")
  claims_path=Path(root)/"claims.json"
  claims_path.write_text(json.dumps({"status":"CLAIMS_HUMAN_REVIEW_REQUIRED",
   "source_sha256":self.sha,"claims":self.claims}),encoding="utf-8")
  return claims_path
 def test_plan(self):
  with tempfile.TemporaryDirectory() as root:
   p=self.make(root);result=plan_context(root,self.p,p)
   self.assertEqual(result["current_role"],"esg")
   self.assertEqual(len(result["prior_audited_turns"]),3)
   self.assertEqual(len(result["must_preserve"]),4)
   self.assertFalse(result["audio_authorized"])
 def test_guard_on_changed_source(self):
  with tempfile.TemporaryDirectory() as root:
   p=self.make(root)
   self.p["turns"][3]["scientific_source_text"]="Source changed"
   with self.assertRaises(ValueError):plan_context(root,self.p,p)
 def test_block_unaudited_context(self):
  with tempfile.TemporaryDirectory() as root:
   p=self.make(root);path(root,2,"audit").unlink()
   with self.assertRaises(ValueError):plan_context(root,self.p,p)
 def test_candidate_role(self):
  d={"role":"esg","spoken_text":"mot "*95,"covered_claim_ids":["C01"],
     "metadata_omitted_claim_ids":[],"context_reference":"reponse a Mines"}
  self.assertTrue(validate_candidate(d,self.claims))
  d["role"]="mining"
  with self.assertRaises(ValueError):validate_candidate(d,self.claims)
if __name__=="__main__":unittest.main()
