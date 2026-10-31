"""Offline regression: browser must check session-bound automatic readiness."""
import unittest
from pathlib import Path

class AutomaticVoiceUI(unittest.TestCase):
 def test_generation_requires_successful_automatic_preflight(self):
  html=(Path(__file__).resolve().parents[1]/"ui"/"hack008.html").read_text(encoding="utf-8")
  self.assertIn('automaticOralReadyFor!==dynamicActiveId',html)
  self.assertIn('/api/dynamic-voice-auto-status?id=',html)
  self.assertIn('oral.state==="READY_FOR_SEPARATELY_CONSENTED_VOICE"',html)
  self.assertIn('automaticOralReadyFor=null;',html)
  self.assertIn('approve_data_sharing:$("dynamic-voice-sharing").checked',html)
  self.assertIn('oral_mode:"automatic_source_bound"',html)
if __name__=="__main__":unittest.main()
