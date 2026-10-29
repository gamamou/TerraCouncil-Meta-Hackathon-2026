"""TERRA-VOICE-001: only source-bound, human-reviewed editorial suggestions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_council import plan_question
from dynamic_runtime import execute_dynamic
from terra_voice_editorial_001 import editorial_worksheet,_excerpt

def records():
 return [{"evidence_id":"LAND","dataset":"ESA WorldCover",
 "source":"fixture","observed_at":"2021","geography":"Boké, Guinea",
 "method":"fixture","license":"test","provenance":"fixture",
 "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
 "sectors":["mining"],"finding":"Recorded preliminary land classification."}]

def model(model,prompt,payload,key):
 e=payload["evidence"][0]
 return json.dumps({"observations":[{"evidence_id":e["evidence_id"],"finding":e["finding"]}],
 "hypotheses":["Possible impacts, unverified."],
 "investigations":["Vérifier les cartes originales. Compléter l'inventaire des observations.","Comparaison plus tard."],
 "abstentions":["Aucune causalité n'est prouvée."]},ensure_ascii=False)

class EditorialTests(unittest.TestCase):
 def test_bounded_exact_excerpt_and_human_review(self):
  p=plan_question("Que savons-nous de l'occupation du sol à Boké ?",records(),sector="mining")
  with tempfile.TemporaryDirectory() as d:
   trace=execute_dynamic(p,"HACK016-TEST-VOICE-001",d,"mock",caller=model)
   self.assertTrue(trace["status"].startswith("COMPLETED_"))
   ws=editorial_worksheet(trace)
  self.assertEqual(len(ws["turns"]),len(trace["steps"]))
  self.assertTrue(ws["review_required"])
  self.assertFalse(ws["automatic_tts_allowed"])
  self.assertEqual(ws["new_audio_calls"],0)
  for turn in ws["turns"]:
   self.assertIn(turn["suggested_extract"],turn["original_full_text"])
   self.assertFalse(turn["human_review_approved"])
 def test_no_midclaim_truncation(self):
  long="Question scientifique "+("étendue "*100)+"."
  self.assertEqual(_excerpt(long,120),"")
 def test_session_protection(self):
  with self.assertRaises((ValueError,KeyError)):
   editorial_worksheet({"status":"STARTED","run_id":"HACK016-WIP"})
 def test_ui_keeps_source_comparison_and_no_tts(self):
  root=Path(__file__).resolve().parents[1]
  html=(root/"ui"/"hack008.html").read_text(encoding="utf-8")
  server=(root/"src"/"local_council_server.py").read_text(encoding="utf-8")
  self.assertIn("dynamic-oral-worksheet",html)
  self.assertIn("dynamic-oral-worksheet",server)
  self.assertIn("Comparer à l'intervention scientifique originale",html)

if __name__=="__main__":unittest.main()
