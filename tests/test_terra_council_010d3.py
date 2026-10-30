"""010D3 tests: role isolation, source locks, context gate, no fabricated approval."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010d3_dialogue import packet_source,previous_context,validate_oral,path
class Tests(unittest.TestCase):
 def setUp(self):
  self.src="Aucune autorisation de developpement ne peut etre conclue."
  self.p={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":[
   {"turn":i,"speaker":("chair" if i==1 else "mining" if i==2
    else "environment" if i==3 else "esg"),"scientific_source_text":self.src}
   for i in range(1,20)]}
  self.claims=[{"claim_id":"C01","importance":"MUST_KEEP"}]
 def test_roles(self):
  self.assertEqual([packet_source(self.p,i)[0] for i in (1,2,3)],
   ["president","mining","environment"])
 def test_source(self):
  self.assertEqual(packet_source(self.p,1)[2],hashlib.sha256(self.src.encode()).hexdigest())
 def test_missing_context_blocks(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):previous_context(t,2)
 def test_prior_audit_has_to_match_oral(self):
  with tempfile.TemporaryDirectory() as t:
   spoken="Bonjour, conseil scientifique."
   sha=hashlib.sha256(self.src.encode()).hexdigest()
   path(t,1,"oral").write_text(json.dumps({"status":"ORAL_HUMAN_REVIEW_REQUIRED",
    "source_sha256":sha,"role":"president","spoken_text":spoken}),encoding="utf-8")
   path(t,1,"audit").write_text(json.dumps({"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
    "source_sha256":sha,"oral_sha256":"wrong"}),encoding="utf-8")
   with self.assertRaises(ValueError):previous_context(t,2)
 def test_oral_role_guard(self):
  data={"role":"mining","spoken_text":"Aucun resultat confirme.","covered_claim_ids":["C01"],
   "metadata_omitted_claim_ids":[],"context_reference":"aucune"}
  self.assertTrue(validate_oral(data,"mining",self.claims))
  with self.assertRaises(ValueError):validate_oral(data,"president",self.claims)
if __name__=="__main__":unittest.main()
