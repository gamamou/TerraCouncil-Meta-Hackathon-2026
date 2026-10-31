"""TERRA-COUNCIL-009B protocol safety tests — no network."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from terra_council_009_route import propose_route
from terra_council_009b_chair_protocol import assemble_protocol, PHASES

class ChairProtocolTests(unittest.TestCase):
    def setUp(self):
        self.route = propose_route("Quels risques ESG pour une mine de bauxite à Boké ?")

    def test_chair_and_dynamic_roster(self):
        p = assemble_protocol(self.route)
        self.assertEqual(p["chair_role"], "scientific_chair")
        self.assertIn("esg", p["active_experts"])
        self.assertNotIn("agriculture", p["active_experts"])
        self.assertEqual(p["chair_opening"]["question_original"], self.route["question_original"])
        self.assertEqual(p["phases"], list(PHASES))

    def test_no_evidence_blocks_execution(self):
        p = assemble_protocol(self.route)
        self.assertEqual(p["scientific_status"], "BLOCKED_EVIDENCE_OR_EXPERTS")
        self.assertEqual(p["debate_turns"], [])
        self.assertEqual(p["meta_calls"], 0)
        self.assertEqual(p["elevenlabs_calls"], 0)

    def test_verified_evidence_opens_only_planning_gate(self):
        ev = [{"evidence_id":"FSDC:sample-1","source_version":"v1","claim":"Test fixture","evidence_status":"VERIFIED"}]
        p = assemble_protocol(self.route, ev)
        self.assertEqual(p["scientific_status"], "READY_FOR_MODEL_DEBATE")
        self.assertEqual(p["execution_status"], "PLAN_ONLY_NOT_EXECUTED")
        self.assertEqual(p["audio_status"], "NOT_GENERATED")

    def test_missing_provenance_rejected(self):
        with self.assertRaises(ValueError):
            assemble_protocol(self.route, [{"claim":"unsupported","evidence_status":"VERIFIED"}])

    def test_invalid_evidence_status_rejected(self):
        with self.assertRaises(ValueError):
            assemble_protocol(self.route, [{"evidence_id":"x","source_version":"1","claim":"x","evidence_status":"GUESS"}])

if __name__ == "__main__":
    unittest.main()
