"""010D5 offline tests — 19 turns, no audio, no trust in altered audits."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d5_full_council import build
from terra_council_010d3_dialogue import path
class Tests(unittest.TestCase):
 def setUp(self):
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":[
   {"turn":i,"speaker":("scientific_chair" if i==1 else "mining" if i==2 else
   "environment" if i==3 else "esg" if i==4 else "communities"),
   "scientific_source_text":f"Source scientifique numero {i}."} for i in range(1,20)]}
 def seed(self,root):
  for i in (1,2,3):
   src=self.p["turns"][i-1]["scientific_source_text"]
   speech=f"Texte oral {i}"
   digest=hashlib.sha256(src.encode()).hexdigest()
   od={"source_sha256":digest,"status":"ORAL_HUMAN_REVIEW_REQUIRED","spoken_text":speech}
   ad={"source_sha256":digest,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
    "oral_sha256":hashlib.sha256(speech.encode()).hexdigest(),
    "unsupported_additions":["unjustified"] if i==2 else [],"critical_omissions":[]}
   path(root,i,"oral").write_text(json.dumps(od),encoding="utf-8")
   path(root,i,"audit").write_text(json.dumps(ad),encoding="utf-8")
 def test_whole_council(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);p=build(self.p,root)
   self.assertEqual(len(p["turns"]),19)
   self.assertEqual(p["turns"][3]["allowed_prior_turns"],[1,2,3])
   self.assertEqual(p["turns"][1]["status"],"AUDITED_WITH_FLAGS_REVIEW_REQUIRED")
   self.assertEqual(p["meta_calls"],0)
   self.assertFalse(p["audio_authorized"])
 def test_forged_source(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);self.p["turns"][0]["scientific_source_text"]="changed"
   with self.assertRaises(ValueError):build(self.p,root)
 def test_missing_audit(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);path(root,2,"audit").unlink()
   with self.assertRaises(ValueError):build(self.p,root)
 def test_unknown_role(self):
  with tempfile.TemporaryDirectory() as root:
   self.seed(root);self.p["turns"][10]["speaker"]="invented"
   with self.assertRaises(ValueError):build(self.p,root)
if __name__=="__main__":unittest.main()
