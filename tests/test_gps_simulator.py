from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone

from ingest import gps_simulator
from ingest.utils import LocalWriter


def test_ping_fields_present_and_typed():
    fleet = gps_simulator.build_fleet(3, seed=1)
    ts = datetime(2026, 4, 17, 12, tzinfo=timezone.utc)
    rec = gps_simulator.simulate_ping(fleet[0], ts, progress=0.5)
    for key in ("ping_id", "vehicle_id", "timestamp", "lat", "lng", "speed_kmh", "fuel_level_pct"):
        assert key in rec
    assert -90 <= rec["lat"] <= 90
    assert -180 <= rec["lng"] <= 180
    assert 0 <= rec["speed_kmh"] <= 150


def test_run_writes_files(tmp_writer: LocalWriter):
    written = gps_simulator.run(
        writer=tmp_writer,
        n_vehicles=2,
        duration_min=2,
        ping_sec=30,
        start_ts=datetime(2026, 4, 17, 12, tzinfo=timezone.utc),
        seed=123,
    )
    assert written, "expected at least one file"

    # Verify at least one file parses as valid JSON array of pings
    with gzip.open(written[0], "rt") as fh:
        records = json.load(fh)
    assert records and all("ping_id" in r for r in records)
