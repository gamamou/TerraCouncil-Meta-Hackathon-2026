"""TERRA-DATA-002: offline synthetic regression tests (no external data or models)."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_scientific_evidence_bridge_002 import SOURCES,inspect,build_report,sha256_bytes

class TestFaithBridge002(unittest.TestCase):
    def test_source_inventory(self):
        self.assertEqual(len(SOURCES),7)
        self.assertEqual(SOURCES["FSMI_HANSEN_640"]["expected_rows"],640)
    def test_cheng_quarantine_not_area(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/SOURCES["FSMI_CHENG_CLASSES"]["filename"]
            v={"status":"CHENG_HISTORICAL_CLASSIFICATION_COUNTS_ONLY",
               "doi":"10.5281/zenodo.15726306","display_polygons":707,
               "source_site_count":199,"area_estimate_authorized":False,
               "company_attribution_verified":False}
            p.write_text(json.dumps(v),encoding="utf-8")
            x=inspect("FSMI_CHENG_CLASSES",p,sha256_bytes(p.read_bytes()))
            self.assertEqual(x["historical_polygon_observations"],707)
            self.assertFalse(x["council_evidence_generated"])
            self.assertEqual(x["source_identity"],"SHA256_VERIFIED")
            v["company_attribution_verified"]=True
            p.write_text(json.dumps(v),encoding="utf-8")
            with self.assertRaises(ValueError):inspect("FSMI_CHENG_CLASSES",p)
    def test_historic_overlap_count_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/SOURCES["MAUS_LEGACY_572"]["filename"]
            with p.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=["guidLicense","maus_ov_ha","has_maus"])
                w.writeheader()
                for i in range(572):
                    w.writerow({"guidLicense":str(i),"maus_ov_ha":"1" if i<35 else "0","has_maus":"Yes" if i<35 else "No"})
            x=inspect("MAUS_LEGACY_572",p)
            self.assertEqual(x["observed_row_count"],572)
            self.assertIn("NOT_NATIONAL",x["source_scientific_status"])
            with self.assertRaises(ValueError):inspect("MAUS_LEGACY_572",p,"f"*64)
            report=build_report({"MAUS_LEGACY_572":{"path":str(p)}})
            self.assertEqual(report["evidence_record_count"],0)
            self.assertEqual(report["network_calls"],0)
    def test_malformed_cams_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/SOURCES["FSMI_CAMS_REGIONAL"]["filename"]
            obj={"policy":"FSMI_CAMS_AIR_QUALITY_001",
                 "status":"PUBLIC_CAMS_REGIONAL_MODEL_CONTEXT_NOT_GROUND_MONITORING",
                 "reference_period":"2026-09-01/2026-09-30",
                 "sensed_pm_observations":0,"mine_attribution_established":False,
                 "approved_mine_aois":0,"records":[{}]*9}
            p.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):inspect("FSMI_CAMS_REGIONAL",p)
            obj["records"]=[{}]*10
            p.write_text(json.dumps(obj))
            self.assertEqual(inspect("FSMI_CAMS_REGIONAL",p)["observed_row_count"],10)
    def test_symlinks_are_not_read(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/SOURCES["FSMI_CHENG_CLASSES"]["filename"]
            target=root/"original.json";target.write_text("{}")
            try:p.symlink_to(target)
            except (OSError,NotImplementedError):self.skipTest("No symlink privileges")
            with self.assertRaises(ValueError):inspect("FSMI_CHENG_CLASSES",p)
    def test_wrong_asset(self):
        with self.assertRaises(ValueError):inspect("UNTRUSTED","/missing")
    def test_missing_inputs_no_success_claim(self):
        report=build_report({})
        self.assertEqual(report["assets"],[])
        self.assertEqual(report["status"],"RECOVERY_INTAKE_NOT_SCIENCE_ADMISSION")

if __name__=="__main__":unittest.main()
