"""TERRA-VOICE-002D offline regression tests: provider must not run before review."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from terra_voice_approval_002 import prepare_review
from terra_voice_storage_002b import save_approval, load_verified_approval
from dynamic_voice_workflow import synthesis, get_status

def fixture():
    return {"session_id":"HACK016-TESTAUDIO12345","evidence_sha256":"e",
            "source_script_sha256":"s","worksheet_sha256":"w",
            "turns":[{"turn":i,"source_model":"muse-wonder-1.0" if i==5 else "muse-spark-1.3",
                      "source_stage_index":i-1,"source_evidence_ids":["E1"],
                      "original_full_text":"Je propose une vérification et souligne les limites.",
                      "suggested_extract":"Je propose une vérification.",
                      "editorial_flags":[]} for i in range(1,7)]}

class ApprovedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.mock=patch("terra_voice_approval_002.editorial_worksheet",return_value=fixture())
        self.mock.start()
        self.addCleanup(self.mock.stop)
        self.dir=tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.trace={"run_id":"HACK016-TESTAUDIO12345",
                    "steps":[{"role":"mining"} for _ in range(6)]}
        self.review=prepare_review(self.trace)
        for t in self.review["turns"]:
            t.update(approved_text="Je propose une vérification.",
                     reviewed_against_original=True,
                     semantic_fidelity_confirmed=True,pronunciation_checked=True)

    def test_unapproved_never_calls_provider(self):
        called=[]
        with self.assertRaises(ValueError):
            synthesis(self.dir.name,self.trace,"spark","wonder","secret",
                      consent=True,approved_plan={"not":"approved"},
                      caller=lambda payload,key:called.append(1))
        self.assertEqual(called,[])
        self.assertEqual(get_status(self.dir.name,self.trace["run_id"])["state"],"NOT_REQUESTED")

    def test_consent_required_prior_to_claim(self):
        save_approval(self.dir.name,self.trace,self.review,"Reviewer")
        approved=load_verified_approval(self.dir.name,self.trace,"spark","wonder")
        with self.assertRaises(ValueError):
            synthesis(self.dir.name,self.trace,"spark","wonder","secret",approved_plan=approved)
        self.assertEqual(get_status(self.dir.name,self.trace["run_id"])["state"],"NOT_REQUESTED")

    def test_one_attempt_even_when_provider_fails(self):
        save_approval(self.dir.name,self.trace,self.review,"Reviewer")
        approved=load_verified_approval(self.dir.name,self.trace,"spark","wonder")
        calls=[]
        def mock_provider(payload,key):
            calls.append((payload,key))
            raise RuntimeError("provider timeout")
        result=synthesis(self.dir.name,self.trace,"spark","wonder","secret",consent=True,
                         caller=mock_provider,approved_plan=approved)
        self.assertEqual(len(calls),1)
        self.assertEqual(len(calls[0][0]["inputs"]),6)
        self.assertEqual(result["state"],"FAILED_OR_INDETERMINATE_DO_NOT_RETRY")
        with self.assertRaises(FileExistsError):
            synthesis(self.dir.name,self.trace,"spark","wonder","secret",consent=True,
                      caller=mock_provider,approved_plan=approved)
        self.assertEqual(len(calls),1)

    def test_tampered_approval_is_rejected(self):
        save_approval(self.dir.name,self.trace,self.review,"Reviewer")
        approved=load_verified_approval(self.dir.name,self.trace,"spark","wonder")
        approved["inputs"][0]["text"]="Changed"
        with self.assertRaises(ValueError):
            synthesis(self.dir.name,self.trace,"spark","wonder","secret",consent=True,
                      caller=lambda *_:self.fail("network called"),approved_plan=approved)

if __name__=="__main__":unittest.main()
