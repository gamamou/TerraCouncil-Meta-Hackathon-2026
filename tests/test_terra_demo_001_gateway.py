import unittest
from src.terra_demo_001_faith_gateway import Gateway,invoke
class TestGateway(unittest.TestCase):
 def setUp(self):
  self.g=Gateway({"PilotCandidate":[{"shape_uid":"A","score_0_100":100,"private_field":"SECRET"}],
                  "RehabilitationSolution":[{"solution_id":"SOL1","solution_name":"Stabilisation"}]})
 def test_no_private_fields(self):
  r=invoke(self.g,{"tool":"query_faith_data","entity":"PilotCandidate"})
  self.assertNotIn("private_field",r[0])
 def test_exact_reference(self):
  self.assertEqual(self.g.get_faith_record("PilotCandidate","A")[0]["shape_uid"],"A")
  self.assertEqual(self.g.get_faith_record("PilotCandidate","B"),[])
 def test_not_a_matching_algorithm(self):
  self.assertEqual(self.g.query_faith_data("RehabilitationSolution")[0]["solution_id"],"SOL1")
  with self.assertRaises(ValueError):invoke(self.g,{"tool":"match_rehabilitation_solutions"})
if __name__=="__main__":unittest.main()
