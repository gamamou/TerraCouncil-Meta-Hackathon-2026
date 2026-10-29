"""009O offline tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009o_oral_prepare import prepare
class Tests(unittest.TestCase):
 def setUp(self):
  self.d={"status":"SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED",
          "turns":[{"role":"mining","phase":"position","text":"Source",
                    "evidence_ids":["E1"]} for _ in range(19)]}
  self.a={"schema":"TERRA_COUNCIL_009N_AUDIT_V1","issues":[],
          "status":"HUMAN_SCIENTIFIC_REVIEW_REQUIRED","review_flags":[]}
 def test_packets_keep_sources(self):
  x=prepare(self.d,self.a)
  self.assertEqual(len(x["turns"]),19)
  self.assertEqual(x["turns"][0]["scientific_source_text"],"Source")
 def test_audio_blocked(self):
  self.assertFalse(prepare(self.d,self.a)["audio_authorized"])
 def test_incomplete_rejected(self):
  self.d["turns"].pop()
  with self.assertRaises(ValueError):prepare(self.d,self.a)
 def test_audit_errors_rejected(self):
  self.a["issues"]=["FAIL"]
  with self.assertRaises(ValueError):prepare(self.d,self.a)
if __name__=="__main__":unittest.main()
