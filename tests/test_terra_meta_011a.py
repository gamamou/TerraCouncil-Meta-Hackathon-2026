"""011A offline guard tests: no data synthesis or silent overwrites."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_meta_011a_consolidate import assemble,sha
class GuardTests(unittest.TestCase):
 def test_invalid_packets_rejected(self):
  with self.assertRaises(ValueError):assemble(Path("."),{"schema":"wrong","turns":[]})
 def test_stable_hash(self):
  self.assertEqual(sha("abc"),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
if __name__=="__main__":unittest.main()
