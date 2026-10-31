import unittest
from tools.terra_meta_demo_001_loop import parse,InvalidModelAction

class TestMetaActionParser(unittest.TestCase):
 def test_plain_json(self):
  self.assertEqual(parse('{"tool":"discover_faith_data"}')["tool"],"discover_faith_data")
 def test_fenced_json(self):
  self.assertEqual(parse('```json\n{"tool":"discover_faith_data"}\n```')["tool"],"discover_faith_data")
 def test_prefixed_explanation(self):
  self.assertEqual(parse('Je consulte les donnees.\n{"tool":"discover_faith_data"}')["tool"],"discover_faith_data")
 def test_empty_output_fails_safely(self):
  with self.assertRaises(InvalidModelAction):parse("")
 def test_prose_without_json_fails_safely(self):
  with self.assertRaises(InvalidModelAction):parse("Je recommande cinq sites.")
 def test_malformed_json_fails_safely(self):
  with self.assertRaises(InvalidModelAction):parse('{"tool":')
if __name__=="__main__":unittest.main()
