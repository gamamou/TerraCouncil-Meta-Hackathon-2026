"""HACK-010 — audio synthesis consent, timing and no-retry safeguards."""
import base64
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from render_session_audio import build_payload, render_one

def manifest():
    return {
        "session_id":"HACK008-TEST-AUDIO", "recording_status":"NOT_GENERATED",
        "human_review_required":True,"human_review_complete":True,
        "approval_type":"USER_REVIEWED_EDITORIAL_RECONSTRUCTION","script_sha256":"testhash",
        "scientific_validation":"SCREENED_NOT_FIELD_VALIDATED",
        "type":"EDITORIAL_RECONSTRUCTION_NOT_VERBATIM",
        "turns":[{"speaker":"Speaker "+str(i+1),
                  "source_model":"muse-wonder-1.0" if i==2 else "muse-spark-1.3",
                  "text_to_review":"Nous devons poursuivre les vérifications de terrain."}
                 for i in range(4)]
    }

class AudioTests(unittest.TestCase):
    def test_payload_no_technical_escapes(self):
        payload=build_payload(manifest(),"spark-voice","wonder-voice")
        self.assertEqual(payload["model_id"],"eleven_v4")
        self.assertEqual(len(payload["inputs"]),4)
        self.assertEqual(payload["inputs"][2]["voice_id"],"wonder-voice")
        self.assertEqual(payload["inputs"][1]["voice_id"],"spark-voice")

    def test_no_call_without_explicit_approvals(self):
        calls=[]
        with TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                render_one(manifest(),d,"spark","wonder","fake",
                           caller=lambda *a:calls.append(1))
            self.assertEqual(calls,[])

    def test_mock_one_call_and_timestamps(self):
        calls=[]
        def fake(payload,key):
            calls.append(payload)
            return {"audio_base64":base64.b64encode(b"ID3"+b"x"*1300).decode("ascii"),
                    "voice_segments":[{"dialogue_input_index":i,
                                       "start_time_seconds":i*5.,
                                       "end_time_seconds":(i+1)*5.}
                                      for i in range(4)]}
        with TemporaryDirectory() as d:
            audio,times=render_one(manifest(),d,"spark","wonder","fake",
                          i_reviewed_script=True,approve_cost_and_sharing=True,caller=fake)
            self.assertEqual(len(calls),1)
            self.assertTrue(audio.is_file())
            obj=json.loads(times.read_text(encoding="utf-8"))
            self.assertEqual(obj["session_id"],manifest()["session_id"])
            self.assertEqual(len(obj["timeline"]),4)
            self.assertNotIn("fake",times.read_text(encoding="utf-8"))

    def test_no_overwrite_and_no_repeat(self):
        def fake(p,k):
            return {"audio_base64":base64.b64encode(b"ID3"+b"x"*1300).decode(),
                    "voice_segments":[{"dialogue_input_index":0,
                                      "start_time_seconds":0,"end_time_seconds":1}]}
        with TemporaryDirectory() as d:
            kwargs=dict(i_reviewed_script=True,approve_cost_and_sharing=True,caller=fake)
            render_one(manifest(),d,"spark","wonder","fake",**kwargs)
            with self.assertRaises(ValueError):
                render_one(manifest(),d,"spark","wonder","fake",**kwargs)
if __name__=="__main__":
    unittest.main()
