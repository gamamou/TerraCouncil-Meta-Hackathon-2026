import unittest
from tools.terra_audio_002_live import parse_dialogue
class VoiceLabels(unittest.TestCase):
 def test_voice_aliases(self):
  d='{"dialogue":[{"speaker":"Spark","text":"Bonjour"},{"speaker":"Wonder","text":"Attention"}]}'
  self.assertEqual([t["speaker"] for t in parse_dialogue(d)],["spark","wonder"])
 def test_moderator_is_assigned_existing_voice(self):
  d='{"dialogue":[{"speaker":"moderator","text":"Bienvenue"},{"speaker":"wonder","text":"Nuance"}]}'
  self.assertEqual(parse_dialogue(d)[0]["speaker"],"spark")
 def test_unknown_role_remains_visible(self):
  d='{"dialogue":[{"speaker":"agent-climat","text":"Bonjour"},{"speaker":"wonder","text":"Nuance"}]}'
  with self.assertRaisesRegex(ValueError,"agent-climat"):parse_dialogue(d)
if __name__=="__main__":unittest.main()
