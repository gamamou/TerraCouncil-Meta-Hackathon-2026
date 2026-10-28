"""HACK-015: durable single-attempt protections, no actual TTS or Meta calls."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from voice_workflow import paths,status,read_audio

class VoiceWorkflowTests(unittest.TestCase):
    def test_unrequested_session(self):
        with TemporaryDirectory() as d:
            self.assertEqual(status(d,"HACK008-TEST-VOICE-001")["state"],"NOT_REQUESTED")
    def test_bad_id_rejected(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ValueError): paths(d,"../../private")
    def test_failed_claim_is_not_reset(self):
        with TemporaryDirectory() as d:
            v=paths(d,"HACK008-TEST-VOICE-001")
            v["base"].mkdir(parents=True)
            v["claim"].write_text(json.dumps({"state":"FAILED_OR_INDETERMINATE_DO_NOT_RETRY"}),encoding="utf-8")
            self.assertEqual(status(d,"HACK008-TEST-VOICE-001")["state"],
                             "FAILED_OR_INDETERMINATE_DO_NOT_RETRY")
            with self.assertRaises(ValueError):
                read_audio(d,"HACK008-TEST-VOICE-001","audio")
    def test_timing_and_audio_not_read_before_completed_claim(self):
        with TemporaryDirectory() as d:
            v=paths(d,"HACK008-TEST-VOICE-001")
            v["base"].mkdir(parents=True)
            v["audio"].write_bytes(b"TEST")
            v["timing"].write_text("{}",encoding="utf-8")
            with self.assertRaises(ValueError):
                read_audio(d,"HACK008-TEST-VOICE-001","audio")
if __name__=="__main__":
    unittest.main()
