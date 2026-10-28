"""TERRA-DATA-002K — scientific context is never promoted to local facts."""
import copy
import sys
import tempfile
import json
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_environmental_context_002k import (
    read_snapshot,attach_environmental_context,SNAPSHOT
)
from dynamic_council import plan_question,plan_fingerprint

QUESTION="Comment concilier extraction miniere, poussiere, foret, eau et communautes a Boke ?"

class EnvironmentalFusionTests(unittest.TestCase):
    def test_five_historic_sources_only_context(self):
        plan=plan_question(QUESTION,[],geography="Boké, Guinea")
        x=attach_environmental_context(plan)
        self.assertEqual(x["environmental_context_count"],5)
        self.assertEqual(len(x["evidence"]),0)
        self.assertTrue(all(z["coverage_relation"]=="NON_AOI_CONTEXT_NOT_GEOGRAPHICALLY_ADMITTED" for z in x["regional_context"]))
        self.assertEqual(x["plan_sha256"],plan_fingerprint(x))
        self.assertTrue(x["status"].startswith("ABSTAIN"))
    def test_source_coverage_counts_preserved(self):
        obj=read_snapshot()
        byid={x["id"]:x for x in obj["source_entries"]}
        self.assertEqual(byid["FAITH-MAUS-HANSEN-640"]["zone_rows"],640)
        self.assertEqual(byid["FAITH-MAUS-HANSEN-640"]["numeric_populated_rows"]["hansen_loss_30pct_rate"],239)
        self.assertEqual(byid["FAITH-CHENG-HISTORICAL-707"]["observations"],707)
        self.assertEqual(byid["FAITH-CHENG-CPDM-CHAIN"]["verified_cheng_to_permit_count"],0)
    def test_out_of_geography_no_environmental_context(self):
        plan=plan_question(QUESTION,[],geography="Kankan, Guinea")
        x=attach_environmental_context(plan)
        self.assertEqual(x["environmental_context_count"],0)
    def test_rejected_source_status_escalation(self):
        obj=read_snapshot()
        obj["source_entries"][0]["status"]="ADMISSIBLE"
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"modified.json"
            p.write_text(json.dumps(obj),encoding="utf-8")
            with self.assertRaises(ValueError):
                read_snapshot(p)
    def test_cheng_not_permit_verified(self):
        obj=read_snapshot()
        obj["source_entries"][3]["verified_cheng_to_permit_count"]=1
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"modified.json"
            p.write_text(json.dumps(obj),encoding="utf-8")
            with self.assertRaises(ValueError):
                read_snapshot(p)

if __name__=="__main__":
    unittest.main()
