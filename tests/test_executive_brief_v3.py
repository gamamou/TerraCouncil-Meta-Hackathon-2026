"""Validate visual V3 report creation without Meta or external services."""
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from executive_brief_v3 import export_v3, VERSION

class ExecutiveV3Tests(unittest.TestCase):
    def test_version_and_pdf(self):
        try:
            import reportlab
        except ImportError:
            self.skipTest("ReportLab not installed")
        evidence=[
            {"evidence_id":"TEST-001","dataset":"WorldPop 2026",
             "finding":"Test population; not exposure.", "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "observed_at":"2026","source":"Synthetic fixture"},
            {"evidence_id":"TEST-002","dataset":"ESA WorldCover 2021",
             "finding":"Test land classes; not mining impact.", "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "observed_at":"2021","source":"Synthetic fixture"}
        ]
        step={"checked_publication":{
            "observations":[], "hypotheses":[{"text":"Test-only uncertainty."}],
            "investigations":[{"text":"Investigate source."}],
            "abstentions":[{"text":"No impact conclusion."}]}}
        data={"run_id":"HACK008-TEST-012","question":"Quelles études pour Boké ?",
              "sha256":"abcde123","evidence":evidence,"steps":[step,step,step,step]}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"report-V3.pdf"
            export_v3(data,path)
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))
            self.assertGreater(path.stat().st_size,4000)
            self.assertTrue(VERSION.startswith("EXECUTIVE_BRIEF_V3"))
            with self.assertRaises(ValueError):
                export_v3(data,path)

if __name__=="__main__":unittest.main()
