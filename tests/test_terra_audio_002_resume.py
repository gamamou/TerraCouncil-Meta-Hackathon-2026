import io,json,tempfile,unittest
from pathlib import Path
from urllib.error import HTTPError
from tools.terra_audio_002_resume import prepare,resume,convert
class ResumeAudio(unittest.TestCase):
 def test_replay_without_meta(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/"old";source.mkdir()
   (source/"internal_oral_script.json").write_text(json.dumps({"raw_meta_output":
    '{"dialogue":[{"speaker":"spark","text":"Bonjour."},{"speaker":"wonder","text":"Nuance."}]}'}))
   voices={"spark":"a","wonder":"b"}
   preview=resume(source,Path(d)/"new",None,voices)
   self.assertEqual(preview["status"],"PREVIEW_NO_API_CALLS")
   calls=[]
   def fake(payload,key):
    calls.append(payload);return b"ID3"+b"x"*150
   state=resume(source,Path(d)/"new","dummy",voices,execute=True,tts=fake)
   self.assertEqual(state["status"],"AUDIO_GENERATED_UNREVIEWED")
   self.assertEqual(calls[0]["model_id"],"eleven_v4")
   self.assertEqual(calls[0]["language_code"],"fr")
   self.assertTrue((Path(d)/"new"/"council_audio_01.mp3").is_file())
 def test_http_detail_preserved(self):
  e=HTTPError("https://api.elevenlabs.io/v1/text-to-dialogue",401,"Unauthorized",{},
    io.BytesIO(b'{"detail":{"status":"missing_permissions","message":"No permission"}}'))
  def fake(req,timeout):raise e
  with self.assertRaisesRegex(RuntimeError,"missing_permissions"):
   convert({"inputs":[],"model_id":"eleven_v4"},"dummy",fake)
if __name__=="__main__":unittest.main()
