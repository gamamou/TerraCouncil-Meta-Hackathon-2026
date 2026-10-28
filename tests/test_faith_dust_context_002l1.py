"""TERRA-DATA-002L1 — atmospheric data remains contextual and truthful."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question,plan_fingerprint
from faith_environmental_context_002k import attach_environmental_context
from faith_dust_context_002l1 import read_dust

class DustContextTests(unittest.TestCase):
    def test_dust_in_real_dynamic_plan(self):
        p=plan_question("Poussiere et extraction miniere a Boke ?",[],geography="Boké, Guinea")
        x=attach_environmental_context(p)
        self.assertEqual(x["dust_context_count"],3)
        self.assertFalse(x["dust_aoi_concentration_admitted"])
        self.assertEqual(x["evidence"],[])
        self.assertEqual(x["status"],"ABSTAIN_NO_QUESTION_RELEVANT_EVIDENCE")
        self.assertEqual(x["plan_sha256"],plan_fingerprint(x))
        self.assertEqual({v["evidence_id"] for v in x["regional_context"] if v.get("source_type")=="FSMI_MODELED_REGIONAL_ATMOSPHERIC_CONTEXT"},
            {"FAITH-CAMS-AIR-SEPT2026","FAITH-WIND-SEPT2026","FAITH-AERMOD-EPA-REFERENCE"})
    def test_no_dust_question_no_dust_context(self):
        p=plan_question("Extraction miniere a Boke ?",[],geography="Boké, Guinea")
        x=attach_environmental_context(p)
        self.assertEqual(x.get("dust_context_count"),0)
    def test_real_source_cannot_promote_local_sensor(self):
        d=read_dust()
        d["sources"][0]["ground_sensor_measurements"]=1
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"tampered.json"
            p.write_text(json.dumps(d),encoding="utf-8")
            with self.assertRaises(ValueError):read_dust(p)
    def test_usa_so2_not_guinea_pm(self):
        d=read_dust()
        self.assertEqual(d["sources"][2]["benchmark_pollutant"],"SO2")
        self.assertFalse(d["sources"][2]["validated_guinea_mine_dispersion"])

if __name__=="__main__":unittest.main()
