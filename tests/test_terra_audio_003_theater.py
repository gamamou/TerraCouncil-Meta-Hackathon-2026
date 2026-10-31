import hashlib,json,tempfile,unittest
from pathlib import Path
from tools.terra_audio_003_theater import assemble
class Theater003(unittest.TestCase):
 def test_audio_integrity_and_no_transcript(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/"session";a=p/"audio";s.mkdir();a.mkdir()
   (s/"05_scientific_brief.json").write_text(json.dumps({"question":"Study","executive_brief":{"scientific_readiness":"RESEARCH_INCOMPLETE"}}))
   (s/"04_passport_preview.json").write_text(json.dumps({"session_id":"test","passport_status":"UNREVIEWED_INTERNAL"}))
   audio=b"ID3"+b"x"*400
   (a/"council_audio_01.mp3").write_bytes(audio)
   (a/"audio_manifest.json").write_text(json.dumps({"status":"AUDIO_GENERATED_UNREVIEWED",
       "model":"eleven_v4","audio_segments":[{"file":"council_audio_01.mp3",
       "sha256":hashlib.sha256(audio).hexdigest()}]}))
   res=assemble(s,a,p/"out")
   self.assertEqual(len(res["audio_tracks"]),1)
   page=(p/"out"/"council_theater.html").read_text()
   self.assertIn("<audio controls",page)
   self.assertNotIn("transcription originale",page)
   self.assertEqual((p/"out"/"audio_01.mp3").read_bytes(),audio)
   with self.assertRaises(FileExistsError):assemble(s,a,p/"out")
if __name__=="__main__":unittest.main()
