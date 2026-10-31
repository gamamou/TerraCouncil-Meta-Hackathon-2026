"""009O-D2 source and hash integrity tests; no API calls."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009o_d2_generate import load_and_verify
class Tests(unittest.TestCase):
 def test_integrity_and_stale_detection(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);j=root/"journal.json";c=root/"context.json";p=root/"packets.json"
   turns=[{"turn":i,"speaker":"mining","phase":"response_to_prior",
     "scientific_source_text":"source "+str(i)} for i in range(1,20)]
   j.write_text(json.dumps({"turns":[{"turn":i} for i in range(1,4)]}),encoding="utf-8")
   p.write_text(json.dumps({"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","turns":turns}),encoding="utf-8")
   context={"schema":"TERRA_COUNCIL_009O_D_CONTEXT_PLAN_V1",
    "journal_sha256":hashlib.sha256(j.read_bytes()).hexdigest(),"next_turn":4,
    "next_turn_context":{"immutable_scientific_source":"source 4","speaker":"mining",
      "phase":"response_to_prior","distinctive_domain_focus":"mining",
      "prior_spoken_context":[]}}
   c.write_text(json.dumps(context),encoding="utf-8")
   self.assertEqual(load_and_verify(c,j,p)[1]["turn"],4)
   j.write_text(j.read_text()+" ",encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"stale"):load_and_verify(c,j,p)
if __name__=="__main__":unittest.main()
