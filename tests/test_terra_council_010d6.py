"""010D6 offline tests of guarded multi-agent continuation."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d6_runner import safe_previous,output
class Tests(unittest.TestCase):
 def test_flagged_turn_excluded(self):
  with tempfile.TemporaryDirectory() as root:
   plan={"turns":[{"turn":i,"status":"AUDITED_WITH_FLAGS_REVIEW_REQUIRED" if i==2 else "AUDITED_HUMAN_REVIEW_REQUIRED"} for i in (1,2,3,4)],
     "prior_audited_context":[{"turn":i,"role":"mining" if i==2 else "president","spoken_text":f"t{i}"} for i in (1,2,3,4)]}
   context,excluded=safe_previous(root,plan,5)
   self.assertEqual(excluded,[2])
   self.assertEqual([x["turn"] for x in context],[1,3,4])
 def test_requires_previous_turn_audited(self):
  with tempfile.TemporaryDirectory() as root:
   plan={"turns":[],"prior_audited_context":[]}
   with self.assertRaises(ValueError):safe_previous(root,plan,6)
 def test_prior_scientific_flags_quarantined(self):
  with tempfile.TemporaryDirectory() as root:
   plan={"turns":[],"prior_audited_context":[]}
   speech="Les donnees sont exploratoires."
   o={"role":"communities","spoken_text":speech,"source_sha256":"correct",
      "status":"ORAL_HUMAN_REVIEW_REQUIRED"}
   a={"source_sha256":"correct","status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
      "oral_sha256":hashlib.sha256(speech.encode()).hexdigest(),
      "unsupported_additions":["invented exposure"],"critical_omissions":[],
      "assessments":[{"claim_id":"C01","verdict":"PRESERVED"}]}
   output(root,5,"oral").write_text(json.dumps(o),encoding="utf-8")
   output(root,5,"audit").write_text(json.dumps(a),encoding="utf-8")
   included,excluded=safe_previous(root,plan,6)
   self.assertEqual(included,[])
   self.assertEqual(excluded,[5])
 def test_no_forged_hash(self):
  with tempfile.TemporaryDirectory() as root:
   plan={"turns":[],"prior_audited_context":[]}
   output(root,5,"oral").write_text(json.dumps({"role":"communities","spoken_text":"x","source_sha256":"sha"}),encoding="utf-8")
   output(root,5,"audit").write_text(json.dumps({"source_sha256":"sha","oral_sha256":"bad",
      "unsupported_additions":[],"critical_omissions":[],"assessments":[]}),encoding="utf-8")
   with self.assertRaises(ValueError):safe_previous(root,plan,6)
if __name__=="__main__":unittest.main()
