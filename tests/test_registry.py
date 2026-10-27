"""HACK-001 smoke tests, no credentials or network calls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registry import load_registry, select_agents

class RegistryTests(unittest.TestCase):
    def test_registry_loads(self):
        self.assertEqual(load_registry()["pilot"]["status"], "NOT_FIELD_VALIDATED")

    def test_mining_has_critic(self):
        ids = {a["id"] for a in select_agents("mining")}
        self.assertIn("mining_industry", ids)
        self.assertIn("scientific_critic", ids)

    def test_unknown_sector_rejected(self):
        with self.assertRaises(ValueError):
            select_agents("nonexistent")

    def test_no_muse_code_dependency(self):
        self.assertIn("Muse Code not required", load_registry()["model_access"])

    def test_abstention_policy(self):
        self.assertEqual(load_registry()["evidence_contract"]["default_policy"], "ABSTAIN_ON_MISSING_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
