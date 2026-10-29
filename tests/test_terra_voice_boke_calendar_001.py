import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation

class BokeCalendar(unittest.TestCase):
 def test_known_window(self):
  out=spoken_pronunciation("Reclassification Sentinel-2 2025-2026 sur le site.")
  self.assertIn("deux mille vingt-cinq à deux mille vingt-six",out["spoken_text"])
 def test_months(self):
  out=spoken_pronunciation("période 2022-10 à 2023-01")
  self.assertIn("octobre deux mille vingt-deux",out["spoken_text"])
  self.assertIn("janvier deux mille vingt-trois",out["spoken_text"])
 def test_utc(self):
  out=spoken_pronunciation("période 20260716_232803_UTC")
  self.assertIn("juillet deux mille vingt-six",out["spoken_text"])
  self.assertIn("U T C",out["spoken_text"])
 def test_bad_dates_rejected(self):
  for raw in ("2026-13","2024-2029","20260230_232803_UTC","20260716_252803_UTC"):
   with self.subTest(raw=raw),self.assertRaises(ValueError):
    spoken_pronunciation("période "+raw)
if __name__=="__main__":unittest.main()
