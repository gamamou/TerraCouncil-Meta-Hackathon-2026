"""Offline regression: T11 010D7B resumes into T12 with immutable provenance."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d6_runner import safe_previous,digest,output
class RecoveryBridgeTests(unittest.TestCase):
 def test_t11_flagged_excluded_without_loss(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);plan={"turns":[],"prior_audited_context":[]}
   for turn in range(5,11):
    speech=f"Turn {turn}"
    o={"status":"ORAL_HUMAN_REVIEW_REQUIRED","role":"esg","spoken_text":speech,"source_sha256":"source"}
    a={"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED","source_sha256":"source","oral_sha256":digest(speech),
       "assessments":[{"claim_id":"C01","verdict":"PRESERVED"}],"unsupported_additions":[],
       "critical_omissions":[],"numerical_mutations":[]}
    output(root,turn,"oral").write_text(json.dumps(o),encoding="utf8")
    output(root,turn,"audit").write_text(json.dumps(a),encoding="utf8")
   rec={"status":"RECOVERED_CLAIMS_HUMAN_REVIEW_REQUIRED","source_sha256":"s11"}
   (root/"Boke-010D7-T11-extract-recovered.json").write_text(json.dumps(rec),encoding="utf8")
   chain=digest(json.dumps(rec,ensure_ascii=False,sort_keys=True))
   speech="Question eau"
   oral={"status":"ORAL_HUMAN_REVIEW_REQUIRED","role":"president","spoken_text":speech,
     "source_sha256":"s11","recovery_sha256":chain}
   audit={"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED","source_sha256":"s11","oral_sha256":digest(speech),
     "recovery_sha256":chain,"assessments":[{"claim_id":"C05","verdict":"PARTIAL"}],
     "unsupported_additions":["dès le départ"],"critical_omissions":[],"numerical_mutations":[]}
   (root/"Boke-010D7B-T11-oral.json").write_text(json.dumps(oral),encoding="utf8")
   (root/"Boke-010D7B-T11-audit.json").write_text(json.dumps(audit),encoding="utf8")
   context,excluded=safe_previous(root,plan,12)
   self.assertEqual(len(context),6)
   self.assertEqual(excluded,[11])
   audit["recovery_sha256"]="forged"
   (root/"Boke-010D7B-T11-audit.json").write_text(json.dumps(audit),encoding="utf8")
   with self.assertRaises(ValueError):safe_previous(root,plan,12)
if __name__=="__main__":unittest.main()
