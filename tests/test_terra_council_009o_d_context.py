"""009O-D offline tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009o_d_context import plan,overlap
class Tests(unittest.TestCase):
 def setUp(self):
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":[{"turn":i,"speaker":("scientific_chair" if i==1 else "mining"),"phase":"opening" if i==1 else "position","scientific_source_text":"Source "+str(i),"source_evidence_ids":[]} for i in range(1,20)]}
  self.j={"schema":"TERRA_COUNCIL_009O_C_V1","status":"PARTIAL_REVIEW_REQUIRED","turns":[{"turn":i,"speaker":("scientific_chair" if i==1 else "mining"),"source_text":"Source "+str(i),"spoken_text":"Intervention "+str(i),"review_flags":[]} for i in range(1,4)]}
 def test_next_turn_preserves_three(self):
  o=plan(self.p,self.j)
  self.assertEqual(o["next_turn"],4)
  self.assertEqual(o["oral_turns_preserved"],3)
  self.assertFalse(o["audio_authorized"])
 def test_source_mismatch_blocked(self):
  self.j["turns"][1]["source_text"]="wrong"
  with self.assertRaises(ValueError):plan(self.p,self.j)
 def test_no_semantic_approval(self):
  self.assertFalse(plan(self.p,self.j)["semantic_equivalence_verified"])
 def test_overlap(self):
  self.assertGreater(overlap("biodiversité évaluation eau","biodiversité évaluation terrain"),0)
if __name__=="__main__":unittest.main()
