from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone

from ingest.utils import LocalWriter, haversine_km, iso_z, partition_key


def test_partition_key_is_utc_hour_bucket():
    ts = datetime(2026, 4, 17, 19, 30, tzinfo=timezone.utc)
    assert partition_key(ts) == "dt=2026-04-17/hh=19"


def test_iso_z_is_zulu():
    ts = datetime(2026, 4, 17, 19, 30, tzinfo=timezone.utc)
    assert iso_z(ts).endswith("Z")


def test_haversine_toronto_to_montreal_is_realistic():
    # Toronto → Montreal is ~504 km as the crow flies
    km = haversine_km(43.6532, -79.3832, 45.5019, -73.5674)
    assert 480 < km < 520


def test_local_writer_roundtrip_json_gz(tmp_writer: LocalWriter):
    records = [{"a": 1}, {"a": 2, "nested": {"b": True}}]
    key = "test/foo.json.gz"
    out = tmp_writer.write_json_gz(key, records)
    with gzip.open(out, "rt") as fh:
        data = json.load(fh)
    assert data == records


def test_local_writer_csv_has_header(tmp_writer: LocalWriter):
    rows = [[1, "a"], [2, "b"]]
    out = tmp_writer.write_csv_gz("test/foo.csv.gz", ["id", "name"], rows)
    with gzip.open(out, "rt") as fh:
        assert fh.readline().strip() == "id,name"
