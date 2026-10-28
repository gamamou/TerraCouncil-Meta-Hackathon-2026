"""HACK-016G: pronunciation is deterministic and never alters scientific quantities."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from scientific_pronunciation import spoken_pronunciation
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_voice_plan import prepare_voice

def evidence():
    return [{"evidence_id":"LAND","dataset":"ESA WorldCover 2021",
        "source":"fixture","observed_at":"2021","geography":"Boké, Guinea",
        "method":"synthetic","license":"test","provenance":"fixture",
        "validation_status":"SCREENED_NOT_FIELD_VALIDATED","sectors":["mining"],
        "finding":"WorldCover provides contextual land cover observations only."}]
def model(model,prompt,payload,key):
    e=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],
        "finding":e["finding"]}],
        "hypotheses":["Contexte à étudier."],
        "investigations":["Étudier les questions PM10 et PM2.5 par AERMOD."],
        "abstentions":["Aucune exposition démontrée."]},ensure_ascii=False)
class PronunciationTests(unittest.TestCase):
    def test_exact_pm_terms_are_reversible_source_tokens(self):
        input_text="Étudier PM10, PM2.5 et AERMOD."
        result=spoken_pronunciation(input_text)
        self.assertEqual(result["spoken_text"],"Étudier P M dix, P M deux virgule cinq et A E R M O D.")
        self.assertEqual(len(result["normalizations"]),3)
        self.assertEqual(input_text,"Étudier PM10, PM2.5 et AERMOD.")
    def test_unknown_numeric_measurements_fail(self):
        for phrase in ("Mesure PM10 de 120 microgrammes.", "Hausse de 25 pour cent.",
                       "WorldCover 2021 montre 50 % de forêt."):
            with self.subTest(phrase=phrase):
                with self.assertRaises(ValueError):spoken_pronunciation(phrase)
    def test_english_requires_review(self):
        with self.assertRaises(ValueError):spoken_pronunciation("The evidence is missing.")
    def test_dynamic_voice_plan_preserves_original_proposition(self):
        with TemporaryDirectory() as folder:
            plan=plan_question("Occupation du sol près de Boké ?",evidence(),sector="mining")
            trace=execute_dynamic(plan,"HACK016-TEST-G-2026",folder,"mock",caller=model)
            candidate=prepare_voice(trace,"voice-spark","voice-wonder")
            spoken=candidate["payload"]["inputs"][0]["text"]
            original=candidate["turns"][0]["source_investigation"]
            self.assertIn("PM10",original)
            self.assertIn("P M dix",spoken)
            self.assertNotIn("PM10",spoken)
            self.assertEqual(candidate["scientific_validation"],"STRUCTURAL_ONLY_NOT_FIELD_VALIDATED")
            self.assertTrue(candidate["requires_paid_consent"])
if __name__=="__main__":unittest.main()
