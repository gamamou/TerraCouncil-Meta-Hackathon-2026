import json,tempfile,unittest
from pathlib import Path
from tools.terra_audio_002_live import parse_dialogue,chunks,run
class Audio002(unittest.TestCase):
 def test_dialogue_and_chunking(self):
  s='{"dialogue":[{"speaker":"spark","text":"Bonjour."},{"speaker":"wonder","text":"Une nuance."}]}'
  turns=parse_dialogue(s)
  self.assertEqual(len(chunks(turns,max_chars=12)),2)
 def test_session_new_audio(self):
  with tempfile.TemporaryDirectory() as temp:
   session=Path(temp)/"input";session.mkdir()
   (session/"01_trace.json").write_text(json.dumps({"status":"GENERATED_NEEDS_SCIENTIFIC_REVIEW",
    "question":"test","steps":[{"stage":"WONDER_CRITIQUE","response":"Check data"},
    {"stage":"SPARK_REVISION","response":"Remain cautious"}]}))
   calls=[]
   def model(model,instruction,payload,key):
    calls.append("meta");return '{"dialogue":[{"speaker":"spark","text":"Bonjour."},{"speaker":"wonder","text":"Attention aux preuves."}]}'
   def voice(inputs,key):
    calls.append("eleven");return b"M"*128
   out=Path(temp)/"audio"
   result=run(session,out,"fake","fake",{"spark":"voice1","wonder":"voice2"},model,voice)
   self.assertEqual(result["status"],"AUDIO_GENERATED_UNREVIEWED")
   self.assertEqual(calls,["meta","eleven"])
   self.assertTrue((out/"council_audio_01.mp3").exists())
   self.assertEqual(result["audio_policy"],"HACKATHON_AUDIO_ADAPTATION_ACCEPTED_POST_HACKATHON_VALIDATION_REQUIRED")
   with self.assertRaises(FileExistsError):run(session,out,"fake","fake",{"spark":"a","wonder":"b"},model,voice)
if __name__=="__main__":unittest.main()
