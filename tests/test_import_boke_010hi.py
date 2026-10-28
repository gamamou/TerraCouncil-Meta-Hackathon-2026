"""HACK-004: source-aware adapter tests without network or model calls."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from import_boke_010hi import records
from verified_council import prepare
from verification import verify_submission

def fixtures():
    bbox = [-14.5, 10.5, -14.0, 11.0]
    hi = {
        "schema_version":"010H-I-1",
        "status":"MULTIDOMAIN_SCREENED_NOT_FIELD_VALIDATED",
        "aoi_bbox_epsg4326":bbox,
        "source_evidence":{
            "water_climate":{"evidence_json_sha256":"chirps-sha"},
            "communities":{
                "dataset":"WorldPop 2026", "url":"https://example.org/worldpop",
                "license":"CC BY 4.0", "sha256":"pop-sha",
                "assessment":"ESTIMATED_POPULATION_NOT_EXPOSURE",
                "measurement":{"not_a_census": True,"estimated_people_sum_cells": 10.5}
            },
            "landcover":{
                "dataset":"ESA WorldCover 2021", "url":"https://example.org/worldcover",
                "license":"CC BY 4.0", "sha256":"cover-sha",
                "assessment":"LAND_COVER_PROXY_NOT_BIODIVERSITY_SURVEY",
                "measurement":{"classes":{k:{"name":name,"area_weighted_share_pct":i}
                    for i,(k,name) in enumerate([
                        ("10","Tree cover"),("40","Cropland"),("50","Built-up"),
                        ("80","Permanent water"),("95","Mangroves")],1)}}
            }
        }
    }
    qa = {"schema_version":"010H-J-QA-1", "status":"READY_FOR_EXPLORATORY_COUNCIL",
          "aoi_bbox_epsg4326":bbox, "scientific_validation":"NOT_FIELD_VALIDATED",
          "errors":[], "input_files_sha256":{"worldpop":"pop-sha","worldcover":"cover-sha","chirps":"chirps-sha"}}
    return hi,qa

class ImportTests(unittest.TestCase):
    def test_source_records_are_exploratory(self):
        hi,qa = fixtures()
        evidence=records(hi,qa)
        self.assertEqual(len(evidence),2)
        self.assertTrue(all(x["validation_status"]=="SCREENED_NOT_FIELD_VALIDATED" for x in evidence))
        job=prepare("Question?", evidence)
        self.assertEqual(job["status"],"EVIDENCE_READY_EXPLORATORY")
        self.assertEqual(len(job["gate"]["evidence"]),2)

    def test_lie_about_raster_hash_fails(self):
        hi,qa=fixtures()
        qa["input_files_sha256"]["worldpop"]="changed"
        with self.assertRaises(ValueError):
            records(hi,qa)

    def test_lie_about_validation_fails(self):
        hi,qa=fixtures()
        hi["status"]="FIELD_VALIDATED"
        with self.assertRaises(ValueError):
            records(hi,qa)

    def test_census_flag_required(self):
        hi,qa=fixtures()
        hi["source_evidence"]["communities"]["measurement"]["not_a_census"]=False
        with self.assertRaises(ValueError):
            records(hi,qa)

    def test_geography_required(self):
        hi,qa=fixtures()
        qa["aoi_bbox_epsg4326"]=[-12,10,-11,11]
        with self.assertRaises(ValueError):
            records(hi,qa)

    def test_unsupported_claim_blocked(self):
        hi,qa=fixtures()
        job=prepare("Question?",records(hi,qa))
        x=job["gate"]["evidence"][0]
        payload={"observations":[{"evidence_id":x["evidence_id"],"finding":"Mining caused exposure"}],
                 "hypotheses":[],"investigations":[],"abstentions":[]}
        self.assertEqual(verify_submission(payload,job["gate"]["evidence"],
                            job["gate"]["evidence_sha256"])["status"],"BLOCKED")

if __name__ == "__main__":
    unittest.main()
