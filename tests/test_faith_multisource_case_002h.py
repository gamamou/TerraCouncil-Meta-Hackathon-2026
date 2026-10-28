"""TERRA-DATA-002H tests: separate scientific observation and context lanes."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import faith_multisource_case_002h as module

def source_record(i,dataset,finding):
    return {"evidence_id":i,"dataset":dataset,"source":"https://example.org/data",
        "observed_at":"2021","geography":"Boké, Guinea",
        "method":"Screened land cover and population raster analysis",
        "license":"CC BY 4.0","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
        "provenance":"Test fixture, not an actual Boké result",
        "finding":finding,"sectors":["mining","environment","agriculture"]}

class MultisourceTests(unittest.TestCase):
    def _case(self):
        records=[
            source_record("TEST-WORLDCOVER","ESA WorldCover 2021","2021 land cover forest share screened."),
            source_record("TEST-WORLDPOP","WorldPop 2026","2026 population raster sum screened.")
        ]
        with patch.object(module,"expand",return_value=records):
            return module.case_file("test_hi","test_qa")
    def test_real_documentary_lane_not_as_aoi_evidence(self):
        x=self._case()
        self.assertEqual(x["evidence_count"],2)
        self.assertTrue(x["regional_documentary_context_count"]>=1)
        self.assertTrue(all(y["validation_status"]=="SCREENED_NOT_FIELD_VALIDATED" for y in x["plan"]["evidence"]))
        self.assertTrue(all(y["evidence_id"] not in [z["evidence_id"] for z in x["plan"]["evidence"]]
            for y in x["plan"]["regional_context"]))
    def test_climate_excluded(self):
        x=self._case()
        self.assertTrue(x["climate_reference"]["not_an_aoi_observation"])
        self.assertFalse(x["dust_local_numeric_concentration_admitted"])
        self.assertEqual(x["model_calls_executed"],0)
    def test_original_chirps_hash_is_not_an_observation(self):
        x=self._case()
        self.assertEqual(x["chirps_status"],module.CHIRPS_ROLE)
        self.assertIn("dust",x["plan"]["missing_topics"])
    def test_no_source_transmission(self):
        x=self._case()
        self.assertEqual(x["external_requests_executed"],0)
        self.assertEqual(x["publication_gate"],"HUMAN_SOURCE_AND_LICENSE_REVIEW_REQUIRED")

if __name__=="__main__":unittest.main()
