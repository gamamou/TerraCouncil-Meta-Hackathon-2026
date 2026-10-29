import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation
class IdentifierSpeech(unittest.TestCase):
 def test_alpha_separator(self):
  self.assertIn("risque minier",spoken_pronunciation("risque_minier")["spoken_text"])
 def test_ambiguous_identifiers_rejected(self):
  for term in ("EVIDENCE_001","A__B","X_Y","trace_2026"):
   with self.subTest(term=term),self.assertRaises(ValueError):
    spoken_pronunciation(term)
if __name__=="__main__":unittest.main()
