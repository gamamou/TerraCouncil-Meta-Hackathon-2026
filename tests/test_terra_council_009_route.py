"""Offline scientific routing QA for TERRA-COUNCIL-009."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from terra_council_009_route import propose_route

class RoutingTests(unittest.TestCase):
    def test_mining_esg_excludes_agriculture(self):
        result = propose_route("Quels risques ESG pour une mine de bauxite à Boké ?")
        self.assertIn("mining", result["agents_selected"])
        self.assertIn("esg", result["agents_selected"])
        self.assertNotIn("agriculture", result["agents_selected"])
        self.assertEqual(result["scientific_status"], "NOT_EVIDENCE_VALIDATED")
        self.assertEqual(result["audio_status"], "NOT_AUTHORIZED")

    def test_agriculture_includes_agriculture(self):
        result = propose_route("Quelle culture agricole de riz est adaptée ?")
        self.assertIn("agriculture", result["agents_selected"])
        self.assertNotIn("mining", result["agents_selected"])

    def test_muse_cannot_omit_explicit_domain(self):
        with self.assertRaises(ValueError):
            propose_route("Une mine de bauxite et ESG ?", ["mining"])

    def test_unknown_muse_agent_rejected(self):
        with self.assertRaises(ValueError):
            propose_route("Risques environnementaux", ["not_a_role"])

    def test_unknown_question_requires_review(self):
        result = propose_route("Bonjour, que faire ?")
        self.assertTrue(result["question_review_required"])
        self.assertEqual(result["capabilities"], {})

    def test_no_phantom_execution(self):
        result = propose_route("Énergie solaire à Conakry")
        self.assertEqual(result["meta_calls"], 0)
        self.assertEqual(result["elevenlabs_calls"], 0)
        self.assertTrue(all(v["status"] == "ADAPTER_NOT_CONNECTED" for v in result["capabilities"].values()))

if __name__ == "__main__":
    unittest.main()
