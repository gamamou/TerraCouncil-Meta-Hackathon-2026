import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation
from terra_voice_segmentation_001 import segment_spoken_turns
class SpokenLength(unittest.TestCase):
 def test_expansion_longer_than_source_cap(self):
  text=("12 "*300).strip()
  spoken=spoken_pronunciation(text)["spoken_text"]
  self.assertGreater(len(spoken),1100)
  self.assertLessEqual(len(spoken),2000)
 def test_source_cap_still_enforced(self):
  with self.assertRaises(ValueError):
   spoken_pronunciation("a"*1101)
 def test_segment_bound_kept(self):
  with self.assertRaises(ValueError):
   segment_spoken_turns([{"spoken_text":"a"*2001}]*3)
if __name__=="__main__":unittest.main()
