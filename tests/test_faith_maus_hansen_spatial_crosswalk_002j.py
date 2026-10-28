"""TERRA-DATA-002J — synthetic geometry QA; no real values fabricated."""
import csv
import hashlib
import sqlite3
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from faith_maus_hansen_spatial_crosswalk_002j import crosswalk, gpkg_wkb, ZONES

try:
    from shapely.geometry import box
except ImportError:
    box=None

@unittest.skipUnless(box is not None,"shapely required")
class SpatialCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d=Path(self.tmp.name)
        self.g=d/"maus_test.gpkg"
        self.c=d/"maus_evidence_640_v101.csv"
        with sqlite3.connect(self.g) as db:
            db.executescript("""
            CREATE TABLE gpkg_geometry_columns (
                table_name TEXT,column_name TEXT,geometry_type_name TEXT,
                srs_id INTEGER,z INTEGER,m INTEGER);
            CREATE TABLE mock_maus(fid INTEGER PRIMARY KEY,geom BLOB);
            INSERT INTO gpkg_geometry_columns VALUES
                ('mock_maus','geom','POLYGON',4326,0,0);
            """)
            rows=[]
            for fid in range(1,129):
                # Two synthetic AOI hits; 126 outside the rectangle.
                geom=box(-14.4,10.6,-14.3,10.7) if fid<3 else box(-12.0,9.0,-11.9,9.1)
                # GeoPackage 8-byte header, zero envelope, EPSG 4326.
                blob=b"GP"+bytes([0,1])+struct.pack("<i",4326)+geom.wkb
                rows.append((fid,blob))
            db.executemany("INSERT INTO mock_maus(fid,geom) VALUES (?,?)",rows)
        cols=["maus_fid","zone","hansen_source","hansen_qa","maus_to_permit",
              "maus_to_company","causal_attribution"]
        with self.c.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=cols)
            writer.writeheader()
            for fid in range(1,129):
                for zone in sorted(ZONES):
                    writer.writerow({"maus_fid":fid,"zone":zone,
                        "hansen_source":"Hansen GFC v1.13","hansen_qa":"FULL",
                        "maus_to_permit":"UNVERIFIED","maus_to_company":"UNVERIFIED",
                        "causal_attribution":"NOT_ESTABLISHED"})

    def test_original_fids_only_and_no_raster_recalculation(self):
        result=crosswalk(self.g,self.c)
        self.assertEqual(result["total_national_maus_screening_fids"],128)
        self.assertEqual(result["full_source_fids_intersecting_rectangle"],2)
        self.assertEqual(result["council_evidence"],[])
        self.assertEqual(result["council_admission"],"NONE")
        self.assertEqual(result["new_scientific_raster_calculations"],0)

    def test_source_hash_guard(self):
        with self.assertRaises(ValueError):
            crosswalk(self.g,self.c,"0"*64)

    def test_causal_attribution_guard(self):
        text=self.c.read_text(encoding="utf-8")
        self.c.write_text(text.replace("NOT_ESTABLISHED","CONFIRMED",1),encoding="utf-8")
        with self.assertRaises(ValueError):
            crosswalk(self.g,self.c)

    def test_gpkg_envelope_offset(self):
        from shapely.geometry import Point
        geom=Point(0,0)
        blob=b"GP"+bytes([0,3])+struct.pack("<i",4326)+b"\x00"*32+geom.wkb
        self.assertEqual(gpkg_wkb(blob),geom.wkb)

if __name__=="__main__":
    unittest.main()
