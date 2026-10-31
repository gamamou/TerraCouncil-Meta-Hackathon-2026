import unittest
from tools.terra_audio_002_live import parse_dialogue
class VoiceLabels(unittest.TestCase):
 def test_voice_aliases(self):
  d='{"dialogue":[{"speaker":"Spark","text":"Bonjour"},{"speaker":"Wonder","text":"Attention"}]}'
  self.assertEqual([t["speaker"] for t in parse_dialogue(d)],["spark","wonder"])
 def test_moderator_is_assigned_existing_voice(self):
  d='{"dialogue":[{"speaker":"moderator","text":"Bienvenue"},{"speaker":"wonder","text":"Nuance"}]}'
  self.assertEqual(parse_dialogue(d)[0]["speaker"],"spark")
 def test_expert_maps_to_critical_voice(self):
  d='{"dialogue":[{"speaker":"spark","text":"Bonjour"},{"speaker":"expert","text":"Observations"}]}'
  self.assertEqual([t["speaker"] for t in parse_dialogue(d)],["spark","wonder"])
 def test_unknown_role_falls_back_but_keeps_original_role(self):
  d='{"dialogue":[{"speaker":"sage","text":"Bonjour"},{"speaker":"wonder","text":"Nuance"}]}'
  turns=parse_dialogue(d)
  self.assertEqual(turns[0]["speaker"],"wonder")
  self.assertEqual(turns[0]["original_speaker"],"sage")
  self.assertEqual(turns[0]["text"],"Bonjour")
 def test_missing_role_is_error(self):
  d='{"dialogue":[{"speaker":"","text":"Bonjour"},{"speaker":"wonder","text":"Nuance"}]}'
  with self.assertRaisesRegex(ValueError,"Missing speaker"):parse_dialogue(d)
if __name__=="__main__":unittest.main()
