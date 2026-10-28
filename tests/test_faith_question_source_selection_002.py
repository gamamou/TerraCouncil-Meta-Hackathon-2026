"""Offline TERRA-DATA-002D assertions, synthetic questions and real catalog metadata."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_question_source_selection_002 import source_readiness

class SourceReadinessTests(unittest.TestCase):
    def test_mining_questions_source_candidates_but_no_council_admission(self):
        result=source_readiness("Les mines de bauxite menacent elles les terres agricoles de Boké ?")
        self.assertGreater(result["matched_candidate_sources"],1)
        self.assertEqual(result["council_evidence_count"],0)
        self.assertEqual(result["model_calls_executed"],0)
        self.assertEqual(result["scientific_admission"],"NONE")
        self.assertTrue(result["council_status"].startswith("ABSTAIN"))
    def test_kankan_excluded_for_boke(self):
        result=source_readiness("Quels effets de la pluie et du climat sur les forêts et terres agricoles de Boké ?")
        kankan=[x for x in result["source_candidates"] if "KANKAN" in x["source_id"]]
        self.assertTrue(kankan)
        self.assertTrue(all(x["location_gate"]=="EXCLUDE_OTHER_REGION" for x in kankan))
    def test_dust_benchmark_not_guinea_measurement(self):
        result=source_readiness("Comment mesurer la poussière PM10 près des mines ?")
        bench=[x for x in result["source_candidates"] if x["source_id"]=="FSMI_AERMOD_REFERENCE"]
        self.assertEqual(len(bench),1)
        self.assertEqual(bench[0]["location_gate"],"EXCLUDE_OTHER_COUNTRY")
    def test_all_source_records_are_explicit_pointers(self):
        result=source_readiness("Comment concilier mines, poussière, forêt, eau et communautés de Boké ?")
        self.assertTrue(all(x["status"]=="CATALOG_POINTER_NOT_GEOSPATIAL_OBSERVATION"
            for x in result["source_candidates"]))
        self.assertEqual(result["external_requests_executed"],0)
    def test_input_guard(self):
        with self.assertRaises(ValueError):
            source_readiness("mine",geography="")

if __name__=="__main__":
    unittest.main()
