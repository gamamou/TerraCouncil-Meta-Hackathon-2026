"""TERRA-DATA-002E: test real recovered point contract and fail-closed guards."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_boke_context_guard_002e import inspect_context,SOURCE

class BokeContextTests(unittest.TestCase):
    def test_real_faith_context_not_pilot_observation(self):
        x=inspect_context()
        self.assertEqual(x["context_status"],"REFERENCE_POINT_OUTSIDE_PILOT_AOI")
        self.assertEqual(x["inside_exploratory_rectangle"],False)
        self.assertEqual(x["council_evidence"],[])
        self.assertEqual(x["model_calls"],0)
    def test_values_provenance_kept(self):
        x=inspect_context()
        self.assertEqual(x["values_observed_in_existing_faith_snapshot"]["rain_2025_mm"],1944.2)
        self.assertEqual(x["values_observed_in_existing_faith_snapshot"]["temp_anomaly_2025_c"],0.41)
        self.assertEqual(x["source_scientific_status"],"COMPUTED_SCREENING_UNREVIEWED")
    def test_geometry_tampering_blocks(self):
        obj=json.loads(SOURCE.read_text(encoding="utf-8"))
        obj["point_inside_pilot_rectangle"]=True
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"tampered.json"
            path.write_text(json.dumps(obj),encoding="utf-8")
            with self.assertRaises(ValueError):inspect_context(path)
    def test_status_promotion_blocks(self):
        obj=json.loads(SOURCE.read_text(encoding="utf-8"))
        obj["council_admission"]=True
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"promoted.json"
            path.write_text(json.dumps(obj),encoding="utf-8")
            with self.assertRaises(ValueError):inspect_context(path)

if __name__=="__main__":unittest.main()
