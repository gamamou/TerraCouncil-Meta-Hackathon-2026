"""TERRA-DATA-002I strict CHIRPS source admission regression tests.

Uses simulated source structures only; makes no claim about local 010HI values.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import faith_chirps_aoi_guard_002i as mod

BASE=[{"evidence_id":"BOKE-010HI-POP-2026",
    "provenance":"010HI SHA256 source-hash; 010HJ QA source-hash",
    "sectors":["mining","environment","agriculture","simandou"]}]
BBOX=[-14.5,10.5,-14.0,11.0]
def source(measure=None):
    w={"evidence_json_sha256":"abc123","dataset":"CHIRPS v3"}
    if measure is not None:w["measurement"]=measure
    return {"source_evidence":{"water_climate":w}}
def valid_measure():
    return {"aoi_bbox_epsg4326":list(BBOX),
        "precip_mm":123.4,"period":"2025-09",
        "source_url":"https://example.org/chirps","license":"TEST-LICENSE"}

class ChirpsGuardTests(unittest.TestCase):
    def check(self,fixture):
        with patch.object(mod,"build",return_value=BASE),patch.object(mod,"read",return_value=fixture):
            return mod.check("unused_hi","unused_qa")
    def test_hash_alone_stays_unadmitted(self):
        r=self.check(source())
        self.assertEqual(r["status"],"REFERENCED_NOT_QUANTIFIED")
        self.assertEqual(len(r["accepted"]),0)
    def test_aoi_metadata_and_numeric_measurement_needed(self):
        r=self.check(source(valid_measure()))
        self.assertEqual(r["status"],"SCREENED_AOI_CHIRPS_MEASUREMENT")
        self.assertEqual(len(r["accepted"]),1)
        self.assertEqual(r["accepted"][0]["validation_status"],"SCREENED_NOT_FIELD_VALIDATED")
        self.assertIn("123.4 mm",r["accepted"][0]["finding"])
    def test_no_geographic_inference_from_kankan(self):
        m=valid_measure()
        m["aoi_bbox_epsg4326"]=[-10.0,10.0,-9.0,11.0]
        self.assertEqual(self.check(source(m))["status"],"ABSTAIN_MEASUREMENT_AOI_UNVERIFIED")
    def test_source_license_and_period_required(self):
        m=valid_measure()
        m.pop("license")
        self.assertEqual(self.check(source(m))["status"],"ABSTAIN_INCOMPLETE_MEASUREMENT_METADATA")
    def test_invalid_precipitation_blocked(self):
        m=valid_measure();m["precip_mm"]=-1
        self.assertEqual(self.check(source(m))["status"],"ABSTAIN_INVALID_MEASUREMENT")

if __name__=="__main__":unittest.main()
