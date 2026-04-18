"""Warehouse IoT event simulator.

Emits dock-scan events (ARRIVAL, SCAN_IN, SCAN_OUT, DEPARTURE) per shipment
arriving at or departing from a warehouse. Written as gzipped CSV for bulk
COPY INTO `fleetpulse_raw.warehouse.warehouse_events`.
"""
from __future__ import annotations

import argparse
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .reference_data import ROUTES, WAREHOUSES
from .utils import Writer, configure_logging, make_writer, partition_key

log = logging.getLogger("fleetpulse.ingest.warehouse")

HEADER = ["event_id", "warehouse_id", "dock_id", "shipment_id", "event_type", "pallet_count", "event_ts"]

EVENT_SEQUENCE = ["ARRIVAL", "SCAN_IN", "SCAN_OUT", "DEPARTURE"]


def _random_warehouse(route_role: str) -> dict:
    return random.choice(WAREHOUSES)


def generate_rows(n_shipments: int, start: datetime, *, seed: int | None = 42) -> Iterable[list]:
    if seed is not None:
        random.seed(seed)
    for _ in range(n_shipments):
        route = random.choice(ROUTES)
        shipment_id = f"S-{uuid.uuid4().hex[:12].upper()}"
        pallets = random.randint(6, 28)
        for warehouse_id, role_offset in (
            (route["origin_warehouse_id"], 0),
            (route["dest_warehouse_id"], int(route["typical_duration_hrs"] * 60)),
        ):
            dock_id = f"{warehouse_id}-D{random.randint(1, 24):02d}"
            base_ts = start + timedelta(minutes=role_offset + random.randint(0, 300))
            cumulative = 0
            for i, event_type in enumerate(EVENT_SEQUENCE):
                cumulative += random.randint(2, 15)
                yield [
                    str(uuid.uuid4()),
                    warehouse_id,
                    dock_id,
                    shipment_id,
                    event_type,
                    pallets if event_type in ("SCAN_IN", "SCAN_OUT") else 0,
                    (base_ts + timedelta(minutes=cumulative)).strftime("%Y-%m-%d %H:%M:%S"),
                ]


def run(writer: Writer, shipments: int, start: datetime | None = None, seed: int | None = 42) -> str:
    start = start or (datetime.now(timezone.utc) - timedelta(days=1))
    ts = datetime.now(timezone.utc)
    key = f"warehouse/{partition_key(ts)}/events_{int(ts.timestamp())}.csv.gz"
    return writer.write_csv_gz(key, HEADER, generate_rows(shipments, start, seed=seed))


def main() -> None:
    configure_logging()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shipments", type=int, default=5000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    writer = make_writer()
    key = run(writer, args.shipments, seed=args.seed)
    print(key)


if __name__ == "__main__":
    main()
