"""Offline tests for 009K agenda generation."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009k_agenda import compile_agenda,ROLES
def fixture():
    roles=[("scientific_chair","opening")]+[(r,"position") for r in ROLES]+[("scientific_chair","cross_examination")]+[(r,"rebuttal_and_revision") for r in ROLES]+[("scientific_chair","deliberation")]
    debate={"schema":"TERRA_COUNCIL_009I_V1","status":"SCIENTIFIC_REVIEW_REQUIRED",
            "decision_authorized":False,"turns":[{"role":r,"phase":p,"text":"Fixture, not scientific findings","evidence_ids":["E1"]} for r,p in roles]}
    manifest={"question":"Investigations?","decision_authorized":False,
              "claims":[{"evidence_id":"E1","admissibility":"ADMISSIBLE_FOR_EXPLORATORY_DEBATE"}]}
    return debate,manifest
class Tests009K(unittest.TestCase):
    def test_short_debate_plan(self):
        d,m=fixture();p=compile_agenda(d,m)
        self.assertEqual(len(p["steps"]),19)
        self.assertEqual(p["steps"][0]["role"],"scientific_chair")
        self.assertEqual(p["steps"][-1]["phase"],"decision_brief")
        self.assertEqual(p["meta_calls"],0)
    def test_preserve_decision_gate(self):
        d,m=fixture();p=compile_agenda(d,m)
        self.assertFalse(p["decision_authorized"])
        self.assertFalse(p["audio_authorized"])
    def test_unreviewed_status_rejected(self):
        d,m=fixture();d["status"]="IN_PROGRESS"
        with self.assertRaises(ValueError):compile_agenda(d,m)
    def test_missing_expert_rejected(self):
        d,m=fixture();d["turns"].pop(1)
        with self.assertRaises(ValueError):compile_agenda(d,m)
    def test_unknown_reference_rejected(self):
        d,m=fixture();d["turns"][0]["evidence_ids"]=["UNLISTED"]
        with self.assertRaises(ValueError):compile_agenda(d,m)
    def test_unauthorized_decision_rejected(self):
        d,m=fixture();m["decision_authorized"]=True
        with self.assertRaises(ValueError):compile_agenda(d,m)
if __name__=="__main__":unittest.main()
