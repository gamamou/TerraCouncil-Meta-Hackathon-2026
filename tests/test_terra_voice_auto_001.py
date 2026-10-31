"""Offline tests for automatic, source-bound speech preparation."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from terra_voice_auto_001 import automatic_oral_plan, automatic_oral_status

class AutomaticSpeechTests(unittest.TestCase):
    def setUp(self):
        self.trace={"run_id":"HACK016-TEST-AUTO"}
        self.plan={"session_id":"HACK016-TEST-AUTO",
                   "turns":[{"text_to_review":"Je propose une investigation."} for _ in range(6)],
                   "pronunciation_audit":[{"source_text":"Je propose une investigation."} for _ in range(6)],
                   "script_sha256":"digest"}

    def test_automatic_plan_never_grants_paid_consent(self):
        with patch("terra_voice_auto_001.prepare_voice", return_value=self.plan):
            p=automatic_oral_plan(self.trace,"spark","wonder")
        self.assertFalse(p["automatic_provider_dispatch"])
        self.assertTrue(p["requires_fresh_paid_consent"])
        self.assertFalse(p["semantic_paraphrase"])
        self.assertEqual(p["approval"],"NO_EDITORIAL_HUMAN_APPROVAL_REQUIRED")

    def test_source_mismatch_fails_closed(self):
        self.plan["pronunciation_audit"][0]["source_text"]="Modified claim"
        with patch("terra_voice_auto_001.prepare_voice", return_value=self.plan):
            with self.assertRaises(ValueError):
                automatic_oral_plan(self.trace,"spark","wonder")

    def test_unsafe_text_fails_closed_and_does_not_call_provider(self):
        with patch("terra_voice_auto_001.prepare_voice",side_effect=ValueError("Unsafe number")):
            result=automatic_oral_status(self.trace,"spark","wonder")
        self.assertEqual(result["state"],"NEEDS_REVIEW_OR_SOURCE_REPAIR")
        self.assertFalse(result["automatically_sendable"])
        self.assertEqual(result["provider_calls"],0)

if __name__=="__main__":unittest.main()
