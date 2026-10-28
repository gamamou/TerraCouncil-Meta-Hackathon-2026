"""HACK-006: 0-cost orchestration tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from live_pilot import pilot
from continue_debate import stage_run

def sample():
    return [{"evidence_id":"TEST001","dataset":"TEST","source":"TEST","observed_at":"2021",
             "geography":"Boké, Guinea","method":"test","license":"test",
             "validation_status":"SCREENED_NOT_FIELD_VALIDATED","provenance":"synthetic",
             "finding":"Only a synthetic test.","sectors":["mining"]}]
def text():
    return '{"observations":[{"evidence_id":"TEST001","finding":"Only a synthetic test."}],"hypotheses":[],"investigations":["Investigate."],"abstentions":["No impact evidence."]}'
def spark():
    return pilot("Investigations?",sample(),execute=True,sharing_approved=True,api_key="fake",caller=lambda *a:text())
class DebateTests(unittest.TestCase):
    def test_dry_run_is_no_call(self):
        calls=[]
        r=stage_run("critique",sample(),spark(),caller=lambda *a:calls.append(a))
        self.assertEqual(r["calls_attempted"],0)
        self.assertEqual(calls,[])
    def test_critique_is_wonder_only(self):
        calls=[]
        def fake(model,*args):
            calls.append(model);return text()
        x=stage_run("critique",sample(),spark(),execute=True,sharing_approved=True,api_key="fake",caller=fake)
        self.assertEqual(x["status"],"PASSED_STRUCTURAL_GATES")
        self.assertEqual(calls,["muse-wonder-1.0"])
    def test_revision_requires_wonder(self):
        with self.assertRaises(ValueError):
            stage_run("revision",sample(),spark())
    def test_revision_is_spark(self):
        wonder=stage_run("critique",sample(),spark(),execute=True,sharing_approved=True,api_key="fake",caller=lambda *a:text())
        seen=[]
        def fake(model,*args):
            seen.append(model);return text()
        final=stage_run("revision",sample(),spark(),wonder,execute=True,sharing_approved=True,api_key="fake",caller=fake)
        self.assertEqual(final["status"],"PASSED_STRUCTURAL_GATES")
        self.assertEqual(seen,["muse-spark-1.3"])
    def test_evidence_change_blocks(self):
        altered=sample();altered[0]["finding"]="altered"
        with self.assertRaises(ValueError):
            stage_run("critique",altered,spark())
    def test_invalid_wonder_blocks_revision(self):
        wonder=stage_run("critique",sample(),spark(),execute=True,sharing_approved=True,api_key="fake",caller=lambda *a:'{}')
        self.assertEqual(wonder["status"],"BLOCKED_BY_INDEPENDENT_VERIFIER")
        with self.assertRaises(ValueError):
            stage_run("revision",sample(),spark(),wonder)
if __name__=="__main__":unittest.main()
