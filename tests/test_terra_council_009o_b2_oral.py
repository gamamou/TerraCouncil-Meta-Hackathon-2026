"""Offline tests for 009O-B2."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009o_b2_oral import validate,review
class Tests(unittest.TestCase):
 def setUp(self):
  self.t={"speaker":"scientific_chair","phase":"opening","scientific_source_text":"Bienvenue. Nos donnees sont non validees sur le terrain. Aucune autorisation."}
  self.s={"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1","audio_authorized":False,"turns":[self.t]+[{}]*18}
 def test_pilot(self):self.assertEqual(validate(self.s,1),self.t)
 def test_only_opening(self):
  with self.assertRaises(ValueError):validate(self.s,2)
 def test_wrong_role(self):
  with self.assertRaises(ValueError):review({"role":"mining","phase":"opening","spoken_text":"Bonjour"},self.t)
 def test_technical_flag(self):
  flags=review({"role":"scientific_chair","phase":"opening","spoken_text":"AOI."},self.t)
  self.assertIn("OPAQUE_TECHNICAL_TERMS",flags)
if __name__=="__main__":unittest.main()
