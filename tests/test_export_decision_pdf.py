"""HACK-009 — session report source-integrity checks (no network or TTS)."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from local_council_server import perform_run, read_session_file
from export_decision_pdf import validate_session

def evidence():
    return [{"evidence_id":"TEST-REPORT","dataset":"Test fixture",
             "source":"Synthetic fixture", "observed_at":"2021",
             "geography":"Boké, Guinea", "method":"test", "license":"test",
             "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"test", "finding":"Synthetic test-only observation",
             "sectors":["mining"]}]

def mock_response():
    return json.dumps({"observations":[{"evidence_id":"TEST-REPORT",
             "finding":"Synthetic test-only observation"}],
             "hypotheses":["Hypothesis is unverified"],
             "investigations":["Check source"],"abstentions":["No impact proven"]})

class ReportTests(unittest.TestCase):
    def make_trace(self, directory):
        return perform_run("Which investigations?",evidence(),"fake","HACK008-TEST-REPORT-01",
                           directory,caller=lambda *a: mock_response())
    def test_verified_trace_accepted(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            trace=self.make_trace(Path(d))
            record=validate_session(trace,evidence())
            self.assertEqual(len(record["steps"]),4)
    def test_changed_evidence_rejected(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            trace=self.make_trace(Path(d))
            e=evidence();e[0]["finding"]="Changed"
            with self.assertRaises(ValueError):validate_session(trace,e)
    def test_incomplete_session_rejected(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            trace=self.make_trace(Path(d));trace["status"]="STOPPED_VERIFICATION_BLOCK"
            with self.assertRaises(ValueError):validate_session(trace,evidence())
    def test_saved_session_can_be_reopened(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            trace=self.make_trace(Path(d))
            saved=read_session_file(Path(d),trace["run_id"])
            self.assertEqual(saved["run_id"],trace["run_id"])
            self.assertIsNone(read_session_file(Path(d),"../../private"))
    def test_pdf_generates_if_reportlab_available(self):
        from tempfile import TemporaryDirectory
        try: import reportlab
        except ImportError: self.skipTest("Optional reportlab not installed")
        from export_decision_pdf import export_pdf
        with TemporaryDirectory() as d:
            data=validate_session(self.make_trace(Path(d)),evidence())
            out=Path(d)/"report.pdf"
            export_pdf(data,out)
            self.assertTrue(out.read_bytes().startswith(b"%PDF"))

if __name__=="__main__":unittest.main()
