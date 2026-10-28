"""TERRA-DATA-001 local recovery tests; mock scientific files only."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_asset_recovery_001 import classify, scan

class Recovery001Tests(unittest.TestCase):
    def test_no_roadmap_false_positive(self):
        self.assertEqual(classify("ROADMAP.md"),[])
        self.assertEqual(classify("transport_roadmap.json"),[])
    def test_specific_source_names(self):
        self.assertIn("MAUS_V2_SOURCE",classify("global_mining_polygons_v2.gpkg"))
        self.assertIn("GUINEA_CADASTRE",classify("official_guinea_cadastre_final_clean.geojson"))
        self.assertIn("CHENG_FUNCTIONAL_CLASS",classify("Cheng_open_pit_results.csv"))
        self.assertIn("FSDC_AIR_DUST",classify("FSMI_AERMOD_PM10.OUT"))
    def test_real_file_hash_and_duplicate_grouping(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            a=root/"global_mining_polygons_v2.gpkg"
            b=root/"extra"
            b.mkdir()
            (b/a.name).write_bytes(b"fixture")
            a.write_bytes(b"fixture")
            result=scan([root],inspect_zip=False)
            self.assertEqual(result["matches_count"],2)
            self.assertEqual(result["unique_content_groups"],1)
            self.assertEqual(result["duplicates_possible"],1)
            self.assertEqual(result["matches"][0]["sha256"],hashlib.sha256(b"fixture").hexdigest())
            self.assertEqual(result["scientific_status"],"INVENTORY_NOT_VALIDATED")
            self.assertEqual(a.read_bytes(),b"fixture")
    def test_zip_members_only_not_extracted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with zipfile.ZipFile(root/"archive.zip","w") as archive:
                archive.writestr("source/Cheng_open_pit_results.csv","header\\n")
                archive.writestr("source/ROADMAP.md","not evidence")
            result=scan([root])
            self.assertEqual(result["matches_count"],1)
            self.assertEqual(result["matches"][0]["source_kind"],"ZIP_ENTRY_NOT_EXTRACTED")
            self.assertFalse((root/"source").exists())
    def test_no_source_destruction_and_missing_root(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"CHIRPS_2025.nc").write_bytes(b"placeholder")
            result=scan([root,root/"missing"])
            self.assertEqual(result["errors"][0]["type"],"MISSING_ROOT")
            self.assertEqual((root/"CHIRPS_2025.nc").read_bytes(),b"placeholder")
    def test_no_trust_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"official_guinea_cadastre_final_clean.geojson").write_text('{"type":"FeatureCollection"}')
            result=scan([root])
            self.assertEqual(result["scientific_status"],"INVENTORY_NOT_VALIDATED")
            self.assertEqual(result["matches"][0]["source_integrity"],"UNASSESSED")

if __name__=="__main__":unittest.main()
