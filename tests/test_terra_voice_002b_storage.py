"""Offline approval persistence checks. No APIs, audio, keys or Meta calls."""
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from terra_voice_approval_002 import prepare_review
from terra_voice_storage_002b import save_approval, load_verified_approval, read_approval_status

def worksheet():
    return {"session_id": "HACK016-TESTPERSIST123", "evidence_sha256": "e",
            "source_script_sha256": "s", "worksheet_sha256": "w",
            "turns": [{"turn": n, "source_model": "muse-wonder-1.0" if n == 5 else "muse-spark-1.3",
                       "source_stage_index": n - 1, "source_evidence_ids": ["E1"],
                       "original_full_text": "Je propose une vérification et souligne une limite.",
                       "suggested_extract": "Je propose une vérification.",
                       "editorial_flags": []} for n in range(1,7)]}

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.mock = patch("terra_voice_approval_002.editorial_worksheet",return_value=worksheet())
        self.mock.start()
        self.addCleanup(self.mock.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.trace = {"run_id": "HACK016-TESTPERSIST123"}
        self.edit = prepare_review(self.trace)
        for turn in self.edit["turns"]:
            turn.update(approved_text="Je propose une vérification.",
                        reviewed_against_original=True,
                        semantic_fidelity_confirmed=True,
                        pronunciation_checked=True)

    def test_exclusive_save_and_read(self):
        saved = save_approval(self.tmp.name,self.trace,self.edit,"Reviewer")
        self.assertTrue(saved["stored"])
        plan = load_verified_approval(self.tmp.name,self.trace,"spark","wonder")
        self.assertEqual(len(plan["inputs"]),6)
        self.assertFalse(plan["may_be_sent"])
        self.assertEqual(read_approval_status(self.tmp.name,self.trace["run_id"])["state"],
                         "APPROVED_FOR_VOICE_PREPARATION")
        with self.assertRaises(FileExistsError):
            save_approval(self.tmp.name,self.trace,self.edit,"Reviewer")

    def test_tampering_blocks_preflight(self):
        save_approval(self.tmp.name,self.trace,self.edit,"Reviewer")
        p=Path(self.tmp.name)/"Dynamic-HACK016"/"voice-approvals"/(self.trace["run_id"]+".json")
        import json
        data=json.loads(p.read_text(encoding="utf-8"))
        data["turns"][0]["approved_text"]="Phrase modifiée."
        p.write_text(json.dumps(data),encoding="utf-8")
        with self.assertRaises(ValueError):
            load_verified_approval(self.tmp.name,self.trace,"spark","wonder")

    def test_missing_approval_and_path_escape(self):
        with self.assertRaises(ValueError):
            load_verified_approval(self.tmp.name,self.trace,"spark","wonder")
        with self.assertRaises(ValueError):
            read_approval_status(self.tmp.name,"../../escape")
if __name__=="__main__": unittest.main()
