"""No-network tests for Muse 009D runtime safeguards."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009d_muse import validate_plan,check_response
from terra_council_009_route import propose_route
from terra_council_009c_plan import compile_plan

class TestMuseRunner(unittest.TestCase):
    def setUp(self):
        route=propose_route("Quels risques ESG pour une mine de bauxite à Boké ?")
        self.plan=compile_plan(route,[{"evidence_id":"TEST-001","source_version":"fixture",
             "claim":"Synthetic test data only","evidence_status":"VERIFIED"}])
    def test_plan(self):
        self.assertEqual(validate_plan(self.plan),{"TEST-001"})
    def test_missing_evidence(self):
        self.plan["evidence"]=[]
        with self.assertRaises(ValueError):validate_plan(self.plan)
    def test_matching_turn(self):
        step={"role":"mining","phase":"position"}
        row=check_response({"role":"mining","phase":"position",
             "text":"An example, not a scientific conclusion.","evidence_ids":["TEST-001"]},step,{"TEST-001"})
        self.assertEqual(row["role"],"mining")
    def test_unknown_reference_rejected(self):
        with self.assertRaises(ValueError):
            check_response({"role":"mining","phase":"position","text":"x",
             "evidence_ids":["INVENTED"]},{"role":"mining","phase":"position"},{"TEST-001"})
    def test_empty_expert_refs_rejected(self):
        with self.assertRaises(ValueError):
            check_response({"role":"mining","phase":"position","text":"x",
             "evidence_ids":[]},{"role":"mining","phase":"position"},{"TEST-001"})
    def test_role_spoof_rejected(self):
        with self.assertRaises(ValueError):
            check_response({"role":"scientific_chair","phase":"position","text":"x",
             "evidence_ids":["TEST-001"]},{"role":"mining","phase":"position"},{"TEST-001"})

if __name__=="__main__":unittest.main()
