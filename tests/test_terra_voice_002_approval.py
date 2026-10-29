"""TERRA-VOICE-002 unit tests: no Meta or ElevenLabs calls."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from terra_voice_approval_002 import prepare_review, approve, voice_payload

def worksheet():
    return {"session_id": "HACK016-TEST", "evidence_sha256": "evidence",
            "source_script_sha256": "script", "worksheet_sha256": "worksheet",
            "turns": [{"turn": n, "source_model": "muse-wonder-1.0" if n == 5 else "muse-spark-1.3",
                       "source_stage_index": n - 1, "source_evidence_ids": ["E1"],
                       "original_full_text": "Je propose une vérification et rappelle les limites scientifiques.",
                       "suggested_extract": "Je propose une vérification.",
                       "editorial_flags": ["SOURCE_ARGUMENTS_OMITTED_CHECK_SEMANTIC_FIDELITY"]}
                      for n in range(1, 7)]}

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.patch = patch("terra_voice_approval_002.editorial_worksheet", return_value=worksheet())
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.trace = {"run_id": "HACK016-TEST"}
        self.draft = prepare_review(self.trace)
        for item in self.draft["turns"]:
            item["approved_text"] = "Je propose une vérification."
            item["reviewed_against_original"] = True
            item["semantic_fidelity_confirmed"] = True
            item["pronunciation_checked"] = True

    def test_complete_approval_prepares_six_turns_without_tts(self):
        record = approve(self.trace, self.draft, "Scientific reviewer", approved_at="2026-10-28T00:00:00Z")
        plan = voice_payload(self.trace, record, "spark-id", "wonder-id")
        self.assertEqual(len(plan["inputs"]), 6)
        self.assertEqual(plan["inputs"][4]["voice_id"], "wonder-id")
        self.assertFalse(plan["may_be_sent"])
        self.assertEqual(plan["new_meta_calls"], 0)
        self.assertEqual(plan["new_audio_calls"], 0)

    def test_missing_review_is_rejected(self):
        self.draft["turns"][2]["semantic_fidelity_confirmed"] = False
        with self.assertRaises(ValueError):
            approve(self.trace, self.draft, "Scientific reviewer")

    def test_source_tampering_is_rejected(self):
        self.draft["turns"][0]["original_sha256"] = "changed"
        with self.assertRaises(ValueError):
            approve(self.trace, self.draft, "Scientific reviewer")

    def test_approved_text_mutation_is_detected(self):
        record = approve(self.trace, self.draft, "Scientific reviewer")
        record["turns"][0]["approved_text"] = "Autre phrase."
        with self.assertRaises(ValueError):
            voice_payload(self.trace, record, "spark-id", "wonder-id")

    def test_wrong_session_is_rejected(self):
        self.draft["session_id"] = "OTHER"
        with self.assertRaises(ValueError):
            approve(self.trace, self.draft, "Scientific reviewer")

    def test_overlong_or_technical_text_is_rejected(self):
        self.draft["turns"][0]["approved_text"] = "x" * 1801
        with self.assertRaises(ValueError):
            approve(self.trace, self.draft, "Scientific reviewer")

    def test_same_voice_is_rejected(self):
        record = approve(self.trace, self.draft, "Scientific reviewer")
        with self.assertRaises(ValueError):
            voice_payload(self.trace, record, "same", "same")

if __name__ == "__main__":
    unittest.main()
