"""TERRA-UX-001: customer-facing workflow must preserve its critical DOM hooks."""
import re
import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"ui"/"hack008.html").read_text(encoding="utf-8")

class ProductionJourneyTests(unittest.TestCase):
    def test_primary_user_journey_is_clear(self):
        for label in ("1. Poser votre question","2. Le débat scientifique",
                      "3. Décisions et restitution","4. Écouter les agents"):
            self.assertIn(label,HTML)
        self.assertIn("Examiner les preuves disponibles",HTML)
        self.assertIn("Lancer le débat",HTML)
        self.assertIn("Archives et fonctions historiques",HTML)
    def test_old_and_new_handlers_not_removed(self):
        critical=("question","dynamic-preview","dynamic-run","dynamic-share","dynamic-cost",
                  "dynamic-history","dynamic-sessions","dynamic-results","dynamic-matrix",
                  "dynamic-oral","dynamic-voice-preview","dynamic-voice-generate",
                  "dynamic-voice-listen","fsdc-compare-output","dynamic-plan",
                  "run","share","billing","progress","decision","theater","oral-editor")
        for control in critical:
            self.assertEqual(len(re.findall(r'id="'+re.escape(control)+'"',HTML)),1,control)
    def test_archival_and_details_balanced(self):
        self.assertEqual(HTML.count("<details"),HTML.count("</details>"))
        self.assertIn('<details class="legacy-archive">',HTML)
        self.assertIn('<details class="source-details">',HTML)
        self.assertIn('<details class="science-details" id="fsdc-expansion">',HTML)
    def test_no_evidence_means_no_billable_call(self):
        self.assertIn('!dynamicPreview.status.startsWith("READY_")',HTML)
        self.assertIn('!dynamicPreview.source_ids.length',HTML)
        self.assertIn("Débat indisponible pour cette question",HTML)
        self.assertIn('plan_sha256:dynamicPreview.plan_sha256',HTML)
        self.assertIn("consent:true",HTML)
    def test_scientific_fidelity_and_audio_review_preserved(self):
        self.assertIn("plan.dust_protocol",HTML)
        self.assertIn("dynamic-voice-consent",HTML)
        self.assertIn("Une relecture humaine",HTML)
        self.assertIn("id=\"dynamic-matrix\"",HTML)

if __name__=="__main__":unittest.main()
