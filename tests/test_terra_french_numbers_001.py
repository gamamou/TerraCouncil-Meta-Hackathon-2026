import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation
from terra_french_numbers_001 import integer_words

class FrenchSpeechTests(unittest.TestCase):
 def test_numeric_values(self):
  self.assertEqual(integer_words(71),"soixante et onze")
  self.assertEqual(integer_words(80),"quatre-vingts")
  p=spoken_pronunciation("Une mesure de 12 et de 3,5 unités.")
  self.assertIn("douze",p["spoken_text"])
  self.assertIn("trois virgule cinq",p["spoken_text"])
 def test_ambiguous_codes_blocked(self):
  for x in ("2021/2026","SITE_042","1-3","0007"):
   with self.subTest(x=x),self.assertRaises(ValueError):
    spoken_pronunciation("Observation "+x)
 def test_unsupported_symbols_still_blocked(self):
  with self.assertRaises(ValueError):
   spoken_pronunciation("Trace mining_alpha")
if __name__=="__main__":unittest.main()
