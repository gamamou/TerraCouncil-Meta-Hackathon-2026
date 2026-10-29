import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation

class DecimalPrecision(unittest.TestCase):
 def test_fractional_digits_preserved(self):
  for raw,digits in [("1,234","deux trois quatre"),("0.00012","zéro zéro zéro un deux"),("12,12345678","un deux trois quatre cinq six sept huit")]:
   with self.subTest(raw=raw):
    result=spoken_pronunciation("mesure "+raw)["spoken_text"]
    self.assertIn(" virgule "+digits,result)
 def test_reject_oversized_fraction(self):
  with self.assertRaises(ValueError):
   spoken_pronunciation("mesure 1,123456789")
if __name__=="__main__":unittest.main()
