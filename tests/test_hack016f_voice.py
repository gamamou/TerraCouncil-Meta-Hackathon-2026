"""HACK-016F: no paid calls in tests; source-bound voice with mock provider."""
import base64
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from dynamic_voice_workflow import synthesis,get_status,read_asset

def sources():
    return [{"evidence_id":"LAND","dataset":"ESA WorldCover 2021",
             "source":"mock","observed_at":"2021","geography":"Boké, Guinea",
             "method":"test","license":"test","validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"test","sectors":["mining"],
             "finding":"WorldCover is an exploratory land-cover dataset."}]
def model(model,prompt,payload,key):
    e=payload["evidence"][0]
    return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
       "hypotheses":["Hypothèse à vérifier."],
       "investigations":["Étudier les territoires concernés."],
       "abstentions":["Aucun impact ne peut être démontré."]},ensure_ascii=False)
def provider(payload,key):
    assert payload["model_id"]=="eleven_v4"
    return {"audio_base64":base64.b64encode(b"MP3"*800).decode("ascii"),
      "voice_segments":[{"dialogue_input_index":i,
          "start_time_seconds":float(i),"end_time_seconds":float(i+1)}
          for i in range(len(payload["inputs"]))]}

class DynamicVoiceTests(unittest.TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory()
        self.plan=plan_question("Occupation du sol près de Boké",sources(),sector="mining")
        self.trace=execute_dynamic(self.plan,"HACK016-TEST-VOICE-2026",
            self.folder.name,"mock",caller=model)
    def tearDown(self):self.folder.cleanup()
    def test_requires_separate_paid_consent(self):
        with self.assertRaises(ValueError):
            synthesis(self.folder.name,self.trace,"spark","wonder","key",
                consent=False,caller=provider)
    def test_generates_one_version_and_blocks_retry(self):
        state=synthesis(self.folder.name,self.trace,"spark","wonder","key",
             consent=True,caller=provider)
        self.assertEqual(state["state"],"READY")
        self.assertTrue(read_asset(self.folder.name,self.trace["run_id"],"audio").startswith(b"MP3"))
        with self.assertRaises(FileExistsError):
            synthesis(self.folder.name,self.trace,"spark","wonder","key",
                consent=True,caller=provider)
    def test_english_requires_review_without_paid_call(self):
        self.trace["steps"][0]["checked_publication"]["investigations"][0]["text"]="Further investigation is necessary."
        with self.assertRaises(ValueError):
            synthesis(self.folder.name,self.trace,"spark","wonder","key",
                consent=True,caller=provider)
        self.assertEqual(get_status(self.folder.name,self.trace["run_id"])["state"],"NOT_REQUESTED")
if __name__=="__main__":unittest.main()
