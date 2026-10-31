"""009M no-network checks for 19-turn Muse debate."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009m_runner import validate,check

def fixture():
    roles=["mining","environment","esg","communities","agriculture"]
    steps=[{"role":"scientific_chair","phase":"opening","max_words":160}]
    steps += [{"role":r,"phase":"initial_position","max_words":150} for r in roles]
    steps += [{"role":"scientific_chair","phase":"targeted_question","max_words":85} for _ in range(3)]
    steps += [{"role":"mining","phase":"response_to_prior","max_words":120} for _ in range(9)]
    steps += [{"role":"scientific_chair","phase":"decision_brief","max_words":330}]
    return {"schema":"TERRA_COUNCIL_009K_AGENDA_V1","decision_authorized":False,
            "evidence_ids":["E1"],"steps":steps}
class Test009M(unittest.TestCase):
    def test_plan_ready(self):self.assertEqual(len(validate(fixture())),19)
    def test_decision_guard(self):
        p=fixture();p["decision_authorized"]=True
        with self.assertRaises(ValueError):validate(p)
    def test_missing_evidence(self):
        p=fixture();p["evidence_ids"]=[]
        with self.assertRaises(ValueError):validate(p)
    def test_valid_response(self):
        x=check({"role":"mining","phase":"initial_position","text":"Point provisoire.",
          "evidence_ids":["E1"]},{"role":"mining","phase":"initial_position","max_words":150},{"E1"})
        self.assertEqual(x["role"],"mining")
    def test_no_unsupported_reference(self):
        with self.assertRaises(ValueError):
            check({"role":"mining","phase":"initial_position","text":"Test",
              "evidence_ids":["FAKE"]},{"role":"mining","phase":"initial_position","max_words":150},{"E1"})
    def test_oversized_response(self):
        with self.assertRaises(ValueError):
            check({"role":"mining","phase":"initial_position","text":"too long",
              "evidence_ids":["E1"]},{"role":"mining","phase":"initial_position","max_words":1},{"E1"})
if __name__=="__main__":unittest.main()
