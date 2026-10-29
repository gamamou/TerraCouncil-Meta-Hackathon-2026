import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from terra_voice_segmentation_001 import segment_spoken_turns
class SegmentTests(unittest.TestCase):
 def test_six_turns_lossless(self):
  original=[{"spoken_text":"A"*754},{"spoken_text":"B"*500},{"spoken_text":"C"*800},
            {"spoken_text":"D"*901},{"spoken_text":"E"*300},{"spoken_text":"F"*300}]
  plan=segment_spoken_turns(original)
  self.assertEqual("".join(x["text"] for b in plan["batches"] for x in b["inputs"]),
                   "".join(x["spoken_text"] for x in original))
  self.assertTrue(all(sum(len(x["text"]) for x in b["inputs"])<=2000 for b in plan["batches"]))
  self.assertFalse(plan["tts_authorized"])
  self.assertEqual(plan["provider_calls"],0)
 def test_reject_overlong_and_missing(self):
  with self.assertRaises(ValueError):
   segment_spoken_turns([{"spoken_text":"A"*2001}]*3)
  with self.assertRaises(ValueError):
   segment_spoken_turns([{"spoken_text":"hello"},{"spoken_text":""},{"spoken_text":"hi"}])
if __name__=="__main__":unittest.main()
