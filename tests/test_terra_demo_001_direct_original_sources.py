"""TERRA-DEMO-001: demo entrypoint regression without Meta/ElevenLabs/network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,MagicMock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import local_council_server as server

class DirectOriginalEvidenceTests(unittest.TestCase):
    def test_direct_010hi_010hj_uses_existing_validation_and_no_apis(self):
        app=MagicMock()
        e=[{"evidence_id":"SCREENED-TEST-POP"}]
        with patch.object(sys,"argv",["local_council_server.py","--hi","original_hi.json","--qa","original_qa.json"]), \
             patch("faith_indicator_expansion_002g.expand",return_value=e) as expand, \
             patch("faith_chirps_aoi_guard_002i.check",return_value={"status":"REFERENCED_NOT_QUANTIFIED","accepted":[]}) as chirps, \
             patch.object(server,"make_plan",return_value={"gate":{"evidence":e},"status":"EVIDENCE_READY_EXPLORATORY"}), \
             patch.object(server,"App",return_value=app) as app_factory, \
             patch.object(server,"UI") as ui:
            ui.exists.return_value=True
            server.main()
            expand.assert_called_once_with("original_hi.json","original_qa.json")
            chirps.assert_called_once_with("original_hi.json","original_qa.json")
            self.assertEqual(app_factory.call_args.args[1],e)
            app.serve_forever.assert_called_once()
    def test_existing_evidence_mode_retained(self):
        e=[{"evidence_id":"SCREENED-TEST-POP"}]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"evidence.json"
            path.write_text(json.dumps(e),encoding="utf-8")
            with patch.object(sys,"argv",["local_council_server.py","--evidence",str(path)]), \
                 patch.object(server,"make_plan",return_value={"gate":{"evidence":e},"status":"EVIDENCE_READY_EXPLORATORY"}), \
                 patch.object(server,"App",return_value=MagicMock()) as app_factory, \
                 patch.object(server,"UI") as ui:
                ui.exists.return_value=True
                server.main()
                self.assertEqual(app_factory.call_args.args[1],e)
    def test_no_sources_refused(self):
        with patch.object(sys,"argv",["local_council_server.py"]):
            with self.assertRaisesRegex(ValueError,"Supply --evidence"):
                server.main()
    def test_both_source_modes_refused(self):
        with patch.object(sys,"argv",["local_council_server.py","--evidence","a.json","--hi","b.json","--qa","c.json"]):
            with self.assertRaisesRegex(ValueError,"either --evidence"):
                server.main()
    def test_partial_original_pair_refused(self):
        with patch.object(sys,"argv",["local_council_server.py","--hi","b.json"]):
            with self.assertRaisesRegex(ValueError,"Both original"):
                server.main()

if __name__=="__main__":unittest.main()
