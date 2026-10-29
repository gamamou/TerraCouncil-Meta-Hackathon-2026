"""010C offline guards; no Meta calls."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_010c_runner import checked
class Tests(unittest.TestCase):
 def setUp(self):
  self.step={"turn":1,"role":"scientific_chair","phase":"opening",
   "model":"muse-wonder-1.0","max_words":100}
 def test_valid(self):
  a=checked({"role":"scientific_chair","phase":"opening","text":"Ouverture du conseil.",
   "evidence_ids":[]} ,self.step,{"E1"})
  self.assertEqual(a["model"],"muse-wonder-1.0")
 def test_wrong_role(self):
  with self.assertRaises(ValueError):checked({"role":"mining","phase":"opening",
    "text":"x","evidence_ids":[]},self.step,{"E1"})
 def test_fake_citation(self):
  with self.assertRaises(ValueError):checked({"role":"scientific_chair","phase":"opening",
    "text":"x","evidence_ids":["FAKE"]},self.step,{"E1"})
 def test_long_turn(self):
  self.step["max_words"]=2
  with self.assertRaises(ValueError):checked({"role":"scientific_chair","phase":"opening",
    "text":"one two three","evidence_ids":[]},self.step,{"E1"})
if __name__=="__main__":unittest.main()
