"""FSDC-RECOVERY-001: local-only discovery with controlled fixtures."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from fsdc_local_recovery import inventory,role

class RecoveryTests(unittest.TestCase):
    def test_categories(self):
        self.assertIn("OSM_GEOMETRY",role("OSM-BOKE-WATER_CLIMATE-2026.geojson"))
        self.assertIn("DUST_AERMOD",role("FSMI_091H_AERMOD_PM10_results.csv"))
        self.assertIn("CLIMATE_WATER",role("CHIRPS_reference.nc"))
        self.assertEqual(role("unrelated_notes_1999.txt"),[])
    def test_discovers_files_and_integrity_without_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            pairs={"010HI_evidence.json":b'{"test":true}',
                   "OSM-BOKE-MINING.geojson":b'{"type":"FeatureCollection","features":[]}',
                   "AERMOD_PM10_results.csv":b"hour,concentration\n",
                   "CHIRPS_2026.nc":b"fake-fixture",
                   "ordinary.txt":b"unrelated"}
            for name,content in pairs.items():
                (root/name).write_bytes(content)
            result=inventory([root])
            self.assertEqual(result["matched_count"],4)
            self.assertTrue(result["no_upload"])
            self.assertEqual(result["scientific_readiness"],"NOT_ASSESSED_METADATA_ONLY")
            self.assertTrue(all(x["hash_status"]=="HASHED" for x in result["matches"]))
            for name,content in pairs.items():
                self.assertEqual((root/name).read_bytes(),content)
    def test_missing_root_not_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            result=inventory([Path(temp)/"does-not-exist"])
            self.assertEqual(result["matched_count"],0)
            self.assertEqual(result["errors"][0]["error"],"ROOT_NOT_FOUND")
    def test_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"ordinary.txt").write_text("hello")
            try:(root/"PM10-linked.csv").symlink_to(root/"ordinary.txt")
            except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
            self.assertEqual(inventory([root])["matched_count"],0)
if __name__=="__main__":unittest.main()
