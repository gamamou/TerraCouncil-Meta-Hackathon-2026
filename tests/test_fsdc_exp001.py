"""FSDC-EXP-001: real documentary discovery with strict no-AOI/no-debate rules."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from fsdc_evidence_expansion import compare_question,load_context_registry

def local():
    return [{"evidence_id":"BOKE-LAND","dataset":"ESA WorldCover 2021",
      "source":"test","observed_at":"2021","geography":"Boké, Guinea",
      "method":"AOI cover shares","license":"test","provenance":"test",
      "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
      "sectors":["mining"],
      "finding":"WorldCover 2021 land cover shares; does not establish impact."}]

class EvidenceExpansionTests(unittest.TestCase):
    def test_real_documentary_source_registered_and_separated(self):
        sources=load_context_registry()
        self.assertEqual(len(sources),2)
        self.assertTrue(all(s["coverage_relation"]=="REGIONAL_CONTEXT_NOT_AOI_OVERLAP_ESTABLISHED" for s in sources))
        self.assertTrue(all(s["source_url"].startswith("https://") for s in sources))
    def test_new_governance_context_does_not_become_aoi_observation(self):
        result=compare_question("Quels financements FODEL et quelle occupation du sol à Boké ?",local())
        self.assertEqual(result["baseline"]["observation_ids"],["BOKE-LAND"])
        self.assertEqual(result["contextual_sources_added"],1)
        self.assertEqual(len(result["unverified_candidates"]),1)
        self.assertEqual(result["aoi_scientific_observations_added"],0)
        self.assertEqual(result["model_calls"],0)
        self.assertFalse(result["debate_rerun_performed"])
        self.assertEqual(result["scientific_conclusion_changed"],"NOT_EVALUATED_NO_NEW_DEBATE")
    def test_outside_boke_rejects_contextual_inference(self):
        result=compare_question("Quels financements et quelle occupation du sol à Conakry ?",local())
        self.assertEqual(result["contextual_sources_added"],0)
    def test_dust_is_still_not_established(self):
        result=compare_question("Quelles concentrations PM10 à Boké ?",local())
        self.assertEqual(result["baseline"]["status"],"ABSTAIN_NO_QUESTION_RELEVANT_EVIDENCE")
        self.assertEqual(result["contextual_sources_added"],0)
if __name__=="__main__":unittest.main()
