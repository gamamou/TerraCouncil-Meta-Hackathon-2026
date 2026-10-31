"""009F evidence boundary tests; all fixtures synthetic."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from terra_council_009f_evidence import adapt_session,EXPLORATORY,CONTEXT,BLOCKED

def fixture():
    return {"run_id":"SAMPLE","question":"Investigations?","human_review_required":True,
      "evidence_sha256":"declared","evidence_snapshot":[{
       "evidence_id":"E1","dataset":"Sample v1","source":"https://example.org/data",
       "observed_at":"2021","method":"screening only",
       "validation_status":"SCREENED_NOT_FIELD_VALIDATED",
       "provenance":"fixture hash","finding":"Illustrative, not real",
       "usage":"exploratory_only"}],
      "regional_context":[{"evidence_id":"C1","claim":"Illustrative context",
        "validation_status":"SOURCE_REPORTED_NOT_INDEPENDENTLY_AUDITED",
        "coverage_relation":"REGIONAL_CONTEXT_NOT_AOI_OVERLAP_ESTABLISHED"}]}
class EvidenceTests(unittest.TestCase):
    def test_screening_stays_exploratory(self):
        x=adapt_session(fixture(),"sha")
        self.assertEqual(x["claims"][0]["admissibility"],EXPLORATORY)
        self.assertEqual(x["claims"][0]["decision_admissibility"],BLOCKED)
        self.assertFalse(x["decision_authorized"])
    def test_context_not_promoted(self):
        x=adapt_session(fixture(),"sha")
        self.assertEqual(x["context_only"][0]["admissibility"],CONTEXT)
    def test_unknown_validation_blocks(self):
        x=fixture();x["evidence_snapshot"][0]["validation_status"]="VERIFIED"
        with self.assertRaises(ValueError):adapt_session(x,"sha")
    def test_duplicate_ids_blocks(self):
        x=fixture();x["evidence_snapshot"]*=2
        with self.assertRaises(ValueError):adapt_session(x,"sha")
    def test_missing_provenance_blocks(self):
        x=fixture();x["evidence_snapshot"][0].pop("provenance")
        with self.assertRaises(ValueError):adapt_session(x,"sha")
    def test_review_flag_required(self):
        x=fixture();x["human_review_required"]=False
        with self.assertRaises(ValueError):adapt_session(x,"sha")
if __name__=="__main__":unittest.main()
