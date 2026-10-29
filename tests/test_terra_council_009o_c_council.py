"""009O-C offline source and candidate tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009o_c_council import check_candidate
class Tests(unittest.TestCase):
 def setUp(self):
  self.item={"turn":2,"speaker":"mining","phase":"initial_position",
    "scientific_source_text":"Ces observations ne sont pas validees sur le terrain.",
    "source_evidence_ids":[]}
 def test_keeps_source(self):
  x=check_candidate(self.item,{"role":"mining","phase":"initial_position",
    "spoken_text":"Les observations restent exploratoires."})
  self.assertEqual(x["source_text"],self.item["scientific_source_text"])
  self.assertEqual(x["semantic_review"],"PENDING_HUMAN_REVIEW")
 def test_reject_wrong_role(self):
  with self.assertRaises(ValueError):check_candidate(self.item,{"role":"esg",
    "phase":"initial_position","spoken_text":"Texte"})
 def test_reject_empty(self):
  with self.assertRaises(ValueError):check_candidate(self.item,{"role":"mining",
    "phase":"initial_position","spoken_text":""})
if __name__=="__main__":unittest.main()
