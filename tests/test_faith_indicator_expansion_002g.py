"""Offline tests for original-input scientific indicator expansion."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_indicator_expansion_002g import expand,summary

def originals():
    bbox=[-14.5,10.5,-14.0,11.0]
    labels={"10":"Tree cover","40":"Cropland","50":"Built-up","80":"Permanent water","95":"Mangroves"}
    hi={"schema_version":"010H-I-1","status":"MULTIDOMAIN_SCREENED_NOT_FIELD_VALIDATED",
        "aoi_bbox_epsg4326":bbox,"source_evidence":{
        "water_climate":{"evidence_json_sha256":"chirps-source-sha"},
        "communities":{"dataset":"WorldPop 2026","url":"https://example.org/pop","license":"CC BY 4.0",
          "sha256":"pop-sha","assessment":"ESTIMATED_POPULATION_NOT_EXPOSURE",
          "measurement":{"not_a_census":True,"estimated_people_sum_cells":100}},
        "landcover":{"dataset":"ESA WorldCover 2021","url":"https://example.org/cover","license":"CC BY 4.0",
          "sha256":"cover-sha","assessment":"LAND_COVER_PROXY_NOT_BIODIVERSITY_SURVEY",
          "measurement":{"classes":{k:{"name":name,"area_weighted_share_pct":i}
             for i,(k,name) in enumerate(labels.items(),1)}}}}}
    qa={"schema_version":"010H-J-QA-1","status":"READY_FOR_EXPLORATORY_COUNCIL",
        "aoi_bbox_epsg4326":bbox,"errors":[],"scientific_validation":"NOT_FIELD_VALIDATED",
        "input_files_sha256":{"worldpop":"pop-sha","worldcover":"cover-sha","chirps":"chirps-source-sha"}}
    return hi,qa

def run(hi,qa):
    with tempfile.TemporaryDirectory() as d:
        a,b=Path(d)/"hi.json",Path(d)/"qa.json"
        a.write_text(json.dumps(hi),encoding="utf-8")
        b.write_text(json.dumps(qa),encoding="utf-8")
        return expand(a,b)

class ExpansionTests(unittest.TestCase):
    def test_six_metric_records_but_only_two_source_families(self):
        hi,qa=originals()
        records=run(hi,qa)
        self.assertEqual(len(records),6)
        self.assertEqual(len({x["evidence_id"] for x in records}),6)
        self.assertEqual(summary(records)["independent_scientific_source_families"],2)
        self.assertEqual(summary(records)["h016_selected_evidence"],6)
        self.assertIn("dust",summary(records)["missing_topics"])
    def test_exact_source_values_and_original_qa_not_upgraded(self):
        hi,qa=originals()
        records=run(hi,qa)
        self.assertTrue(all(x["validation_status"]=="SCREENED_NOT_FIELD_VALIDATED" for x in records))
        self.assertIn("1%",records[1]["finding"])
        self.assertIn("5%",records[5]["finding"])
        self.assertTrue(all("pop-sha" in x["provenance"] for x in records))
    def test_original_mismatched_hash_rejected(self):
        hi,qa=originals()
        qa["input_files_sha256"]["worldcover"]="changed"
        with self.assertRaises(ValueError):run(hi,qa)
    def test_original_aoi_change_rejected(self):
        hi,qa=originals()
        hi["aoi_bbox_epsg4326"]=[-14.7,10.5,-14,11]
        with self.assertRaises(ValueError):run(hi,qa)
    def test_invalid_percentage_rejected(self):
        hi,qa=originals()
        hi["source_evidence"]["landcover"]["measurement"]["classes"]["10"]["area_weighted_share_pct"]=120
        with self.assertRaises(ValueError):run(hi,qa)

if __name__=="__main__":unittest.main()
