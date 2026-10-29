import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from terra_agent_voice_registry_001 import voice_map_for_roles,voice_mapping_template
class Registry(unittest.TestCase):
 def test_role_not_model_mapping(self):
  roles=["mining","agriculture","mining","final_synthesis"]
  mapping={"mining":"voice-A","agriculture":"voice-B","final_synthesis":"voice-C"}
  self.assertEqual(voice_map_for_roles(roles,mapping)["mining"],"voice-A")
  self.assertEqual(len(voice_mapping_template(roles)),3)
 def test_reject_duplicate_voice(self):
  with self.assertRaises(ValueError):
   voice_map_for_roles(["mining","agriculture"],{"mining":"same","agriculture":"same"})
 def test_reject_missing_voice(self):
  with self.assertRaises(ValueError):
   voice_map_for_roles(["mining","agriculture"],{"mining":"one"})
if __name__=="__main__":unittest.main()
