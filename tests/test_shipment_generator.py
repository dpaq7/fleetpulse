from __future__ import annotations

from datetime import date

from ingest import shipment_generator
from ingest.utils import LocalWriter


def test_generator_respects_row_count():
    rows = list(shipment_generator.generate_rows(
        n=50,
        start=date(2025, 1, 1),
        end=date(2025, 3, 31),
        seed=7,
    ))
    assert len(rows) == 50
    # Every row has the expected number of columns
    assert all(len(r) == len(shipment_generator.HEADER) for r in rows)


def test_statuses_are_valid():
    rows = list(shipment_generator.generate_rows(100, date(2025, 1, 1), date(2025, 1, 31)))
    status_idx = shipment_generator.HEADER.index("status")
    valid = {"DELIVERED", "DELAYED", "IN_TRANSIT", "CANCELLED"}
    assert {r[status_idx] for r in rows} <= valid


def test_run_creates_csv_gz(tmp_writer: LocalWriter):
    key = shipment_generator.run(tmp_writer, rows=10, start=date(2025, 1, 1), end=date(2025, 1, 31), seed=42)
    assert key.endswith(".csv.gz")
