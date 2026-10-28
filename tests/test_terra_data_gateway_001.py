"""Offline tests for TERRA-DATA-GATEWAY-001; no HTTP performed."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import terra_data_gateway as gateway

class GatewayTests(unittest.TestCase):
    def test_manifest_load(self):
        d = gateway.read_manifest()
        self.assertEqual(d["schema_version"],"TERRA_DATA_GATEWAY_001")
        self.assertTrue(any(r["id"]=="CHENG_MIN085_087" for r in d["recovered_works"]))
    def test_nasa_point_not_aoi(self):
        p = gateway.request_plan("nasa-power",10.75,-14.25)
        self.assertEqual(p["spatial_unit"],"GRID_POINT_NOT_AOI")
        self.assertIn("PRECTOTCORR",p["url"])
        self.assertNotIn("api_key",p["url"].lower())
    def test_openaq_requires_private_key(self):
        p = gateway.request_plan("openaq-stations",10.75,-14.25)
        self.assertTrue(p["requires_key"])
        self.assertIn("radius=25000",p["url"])
        with self.assertRaises(ValueError):
            gateway.fetch(p)
    def test_stac_catalog_not_footprint(self):
        p=gateway.request_plan("earth-search",10.75,-14.25)
        self.assertEqual(p["scientific_status"],"CATALOG_DISCOVERY_ONLY")
    def test_invalid_coordinates_and_dates_rejected(self):
        with self.assertRaises(ValueError):
            gateway.request_plan("nasa-power",91,0)
        with self.assertRaises(ValueError):
            gateway.request_plan("nasa-power",10,-14,"20250109","20250101")
    def test_host_change_refused(self):
        p=gateway.request_plan("nasa-power",10,-14)
        p["url"]="https://attacker.example/payload"
        with self.assertRaises(ValueError):
            gateway.fetch(p)
    def test_local_provenance_save_is_quarantined_and_no_overwrite(self):
        p=gateway.request_plan("nasa-power",10.75,-14.25)
        payload=b'{"properties":{"parameter":{"T2M":{"20250101":24.3}}}}'
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"raw.json"
            entry=gateway.save_capture(p,payload,path)
            self.assertEqual(entry["validation_status"],"DOWNLOADED_UNVALIDATED")
            self.assertFalse(entry["field_validated"])
            self.assertEqual(entry["raw_sha256"],hashlib.sha256(payload).hexdigest())
            self.assertTrue(path.is_file())
            with self.assertRaises(ValueError):
                gateway.save_capture(p,payload,path)
    def test_fetch_mocks_no_real_network(self):
        class Fake:
            headers={}
            def __enter__(self):return self
            def __exit__(self,*_):return False
            def read(self,n):return b'{"results":[]}'
        seen=[]
        def opener(req,timeout):
            seen.append((req.full_url,timeout))
            return Fake()
        p=gateway.request_plan("openaq-stations",10.75,-14.25)
        raw,data=gateway.fetch(p,api_key="test-only",opener=opener)
        self.assertEqual(data["results"],[])
        self.assertEqual(len(seen),1)

if __name__=="__main__":unittest.main()
