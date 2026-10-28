"""HACK-007 no-cost dashboard tests using synthetic evidence and fake model outputs."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from live_pilot import pilot
from continue_debate import stage_run
from build_council_ui import assemble, make_html

def source():
    return [{"evidence_id":"TEST-UI-1","dataset":"Synthetic test only",
             "source":"unit test","observed_at":"2021","geography":"Boké, Guinea",
             "method":"mock","license":"test only",
             "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
             "provenance":"test","finding":"Synthetic observation for unit tests.",
             "sectors":["mining"]}]

RESPONSE = ('{"observations":[{"evidence_id":"TEST-UI-1",'
            '"finding":"Synthetic observation for unit tests."}],'
            '"hypotheses":["Unknown."],"investigations":["Study."],'
            '"abstentions":["No conclusion."]}')

def traces():
    e=source()
    s=pilot("What should we investigate?",e,execute=True,
            sharing_approved=True,api_key="fake",
            caller=lambda *args:RESPONSE)
    w=stage_run("critique",e,s,execute=True,
                sharing_approved=True,api_key="fake",caller=lambda *args:RESPONSE)
    r=stage_run("revision",e,s,w,execute=True,
                sharing_approved=True,api_key="fake",caller=lambda *args:RESPONSE)
    return e,s,w,r

class CouncilUITests(unittest.TestCase):
    def test_builds_three_stage_replay(self):
        data=assemble(*traces())
        self.assertEqual(len(data["sessions"]),3)
        self.assertEqual(data["model_calls_in_replay"],0)

    def test_embeds_validated_evidence(self):
        data=assemble(*traces())
        output=make_html(data)
        self.assertIn("TEST-UI-1",output)
        self.assertIn("muse-wonder-1.0",output)
        self.assertIn("Nouvelle question non exécutée",output)

    def test_rejects_modified_sources(self):
        evidence,s,w,r=traces()
        evidence[0]["finding"]="CHANGED"
        with self.assertRaises(ValueError):
            assemble(evidence,s,w,r)

    def test_rejects_invalid_stage(self):
        evidence,s,w,r=traces()
        w["status"]="BLOCKED_BY_INDEPENDENT_VERIFIER"
        with self.assertRaises(ValueError):
            assemble(evidence,s,w,r)

    def test_untrusted_text_cannot_close_script(self):
        data=assemble(*traces())
        data["question"]="</script><img src=x onerror=alert(1)>"
        output=make_html(data)
        self.assertNotIn("</script><img",output)
        self.assertIn("\\u003c/script\\u003e",output)

if __name__=="__main__":
    unittest.main()
