import unittest
from chamber_visuals import visual_cues

class ChamberTests(unittest.TestCase):
    def test_reject_unverified(self):
        with self.assertRaises((ValueError,KeyError,TypeError)):
            visual_cues({"status":"UNVERIFIED"},[])
    def test_reject_missing_sources(self):
        with self.assertRaises((ValueError,KeyError,TypeError)):
            visual_cues({},[])
if __name__ == "__main__":
    unittest.main()
