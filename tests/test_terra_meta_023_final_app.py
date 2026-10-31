import json,tempfile,unittest
from pathlib import Path
from tools import terra_meta_023_final_app as app
class FinalApplicationTests(unittest.TestCase):
 def test_existing_audio_recovered_without_calls(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/"artifacts").mkdir()
   audio=r/"audio_recovered_1";audio.mkdir()
   (audio/"council_audio_01.mp3").write_bytes(b"ID3test")
   (audio/"audio_manifest.json").write_text(json.dumps({"status":"AUDIO_GENERATED_UNREVIEWED",
    "audio_segments":[{"file":"council_audio_01.mp3"}]}))
   self.assertEqual(app.audio_for_session(r/"artifacts"),audio)
 def test_page_omits_transcripts(self):
  class Options: storage=Path("__terra_absent_history__")
  original=getattr(app.core,"ARGS",None);state=app.core.STATE.copy()
  try:
   app.core.ARGS=Options()
   app.core.STATE.update(session="__terra_missing__",audio=None,busy=False,phase="READY",message="Prêt")
   s=app.frontpage()
   self.assertIn("Council Theater",s)
   self.assertIn("/status",s)
   self.assertNotIn("Audio sans transcription publique",s)
   self.assertNotIn("SPARK_REVISION",s)
  finally:
   app.core.STATE.clear();app.core.STATE.update(state)
   if original is None:delattr(app.core,"ARGS")
   else:app.core.ARGS=original
if __name__=="__main__":unittest.main()
