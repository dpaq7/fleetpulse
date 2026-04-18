from __future__ import annotations

from datetime import datetime, timezone

from ingest import warehouse_event_simulator
from ingest.utils import LocalWriter


def test_events_per_shipment_is_expected_multiple():
    # 4 events per role × 2 roles (origin + dest) = 8 per shipment
    rows = list(warehouse_event_simulator.generate_rows(
        n_shipments=5,
        start=datetime(2026, 4, 17, tzinfo=timezone.utc),
        seed=1,
    ))
    assert len(rows) == 5 * 8


def test_run_writes_file(tmp_writer: LocalWriter):
    key = warehouse_event_simulator.run(tmp_writer, shipments=3, seed=1)
    assert key.endswith(".csv.gz")
