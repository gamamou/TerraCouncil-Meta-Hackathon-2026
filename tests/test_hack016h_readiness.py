"""HACK-016H: readiness reports are offline, source-grounded and non-secret."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_readiness import inspect_readiness

def records():
    common={"source":"fixture","observed_at":"2021","geography":"Boké, Guinea",
        "method":"synthetic","license":"test",
        "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
        "provenance":"mock","sectors":["mining"]}
    return [
        dict(common,evidence_id="POP",dataset="WorldPop",
             finding="WorldPop estimated population for an area, not exposed people."),
        dict(common,evidence_id="LAND",dataset="WorldCover",
             finding="WorldCover land cover information, not verified impacts.")
    ]

class ReadinessTests(unittest.TestCase):
    def test_no_key_and_no_dynamic_history(self):
        with TemporaryDirectory() as folder:
            result=inspect_readiness(records(),folder,False,False)
            self.assertEqual(result["dynamic_session_count"],0)
            self.assertFalse(result["meta_key_available"])
            self.assertEqual(result["external_calls"],0)
            self.assertEqual(result["examples"][2]["source_ids"],[])
            self.assertEqual(result["examples"][2]["estimated_max_calls"],0)
    def test_legacy_and_dynamic_sessions_are_separate(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"HACK008-OLD.json").write_text("{}",encoding="utf-8")
            (root/"Dynamic-HACK016").mkdir()
            (root/"Dynamic-HACK016"/"HACK016-RECENT.json").write_text("{}",encoding="utf-8")
            result=inspect_readiness(records(),folder,True,False)
            self.assertEqual(result["legacy_session_count"],1)
            self.assertEqual(result["dynamic_session_count"],1)
            self.assertTrue(result["meta_key_available"])
            self.assertEqual(result["examples"][0]["source_ids"],["LAND"])
            self.assertEqual(result["examples"][1]["source_ids"],["POP"])
    def test_no_secrets_in_diagnostic(self):
        with TemporaryDirectory() as folder:
            result=inspect_readiness(records(),folder,True,True)
            self.assertEqual(set(["meta_key_available","voice_key_available"]).intersection(result),set(["meta_key_available","voice_key_available"]))
            self.assertNotIn("api_key",result)
if __name__=="__main__":unittest.main()
