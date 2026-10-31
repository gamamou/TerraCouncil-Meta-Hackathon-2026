import json,tempfile,unittest
from pathlib import Path
from tools import terra_meta_023_final_app as ui
from tools.terra_audio_002_resume import prepare
from tools.terra_audio_027_english import translate_dialogue
class EnglishInterfaceTests(unittest.TestCase):
 def test_english_audio_discovery(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"artifacts").mkdir()
   audio=root/"audio_en_demo";audio.mkdir()
   (audio/"council_audio_01.mp3").write_bytes(b"test")
   (audio/"audio_manifest.json").write_text(json.dumps({"status":"AUDIO_GENERATED_UNREVIEWED",
      "audio_segments":[{"file":"council_audio_01.mp3"}]}))
   self.assertEqual(ui.audio_for_session(root/"artifacts","en"),audio)
   self.assertIsNone(ui.audio_for_session(root/"artifacts","fr"))
 def test_english_language_payload(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   raw='{"dialogue":[{"speaker":"spark","text":"Hello"},{"speaker":"wonder","text":"Yet"}]}'
   (root/"internal_oral_script.json").write_text(json.dumps({"raw_meta_output":raw}))
   turns,payloads=prepare(root,{"spark":"one","wonder":"two"},"eleven_v4","en")
   self.assertEqual(payloads[0]["language_code"],"en")
   self.assertEqual({t["speaker"] for t in turns},{"spark","wonder"})
 def test_translation_preserves_two_roles(self):
  raw='{"dialogue":[{"speaker":"spark","text":"Oui"},{"speaker":"wonder","text":"Non"}]}'
  result=translate_dialogue(raw,"unused",lambda model,instruction,payload,key:'{"dialogue":[{"speaker":"spark","text":"Yes"},{"speaker":"wonder","text":"No"}]}')
  self.assertIn("Yes",result)
if __name__=="__main__":unittest.main()
