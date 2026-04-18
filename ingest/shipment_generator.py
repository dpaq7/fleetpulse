"""Historical shipment CSV generator.

Produces a ~500K row synthetic shipment history for bulk COPY INTO
`fleetpulse_raw.shipments.shipments`. Delays are correlated loosely with
day-of-week (weekends smoother) and seasonality (winter months noisier) so
the eventual dashboard tells a realistic story.

Usage:
    python -m ingest.shipment_generator --rows 500000 --start 2024-01-01 --end 2025-12-31
"""
from __future__ import annotations

import argparse
import logging
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from .reference_data import DRIVERS, ROUTES, VEHICLES
from .utils import Writer, configure_logging, make_writer, partition_key

log = logging.getLogger("fleetpulse.ingest.shipments")

HEADER = [
    "shipment_id", "vehicle_id", "driver_id", "route_id",
    "origin_warehouse_id", "dest_warehouse_id",
    "pickup_ts", "delivery_ts", "scheduled_delivery_ts",
    "weight_kg", "distance_km", "fuel_used_l", "status",
]

STATUSES = ["DELIVERED", "DELIVERED", "DELIVERED", "DELIVERED", "DELAYED", "IN_TRANSIT", "CANCELLED"]


def _delay_minutes(pickup: datetime) -> int:
    """Draw a realistic delay. Negative = early."""
    # Weekend bias: smoother
    weekend = pickup.weekday() >= 5
    # Winter bias: noisier (Dec-Feb)
    winter = pickup.month in (12, 1, 2)
    mu = -2 if weekend else 6
    sigma = 30 if winter else 15
    return int(random.gauss(mu, sigma))


def generate_rows(n: int, start: date, end: date, seed: int | None = 42) -> Iterable[list]:
    if seed is not None:
        random.seed(seed)
    span_days = max(1, (end - start).days)
    for _ in range(n):
        route = random.choice(ROUTES)
        vehicle = random.choice(VEHICLES)
        driver = random.choice(DRIVERS)

        day_offset = random.randint(0, span_days)
        pickup_ts = datetime.combine(start + timedelta(days=day_offset), datetime.min.time(), tzinfo=timezone.utc)
        pickup_ts = pickup_ts.replace(hour=random.randint(4, 20), minute=random.randint(0, 59))

        scheduled_duration = timedelta(hours=route["typical_duration_hrs"])
        scheduled_delivery = pickup_ts + scheduled_duration
        actual_delivery = scheduled_delivery + timedelta(minutes=_delay_minutes(pickup_ts))

        status = random.choices(STATUSES, weights=[60, 60, 60, 60, 25, 10, 5])[0]
        if status == "IN_TRANSIT":
            delivery_str = ""
        elif status == "CANCELLED":
            delivery_str = ""
            actual_delivery = None
        else:
            delivery_str = actual_delivery.strftime("%Y-%m-%d %H:%M:%S")

        weight_kg = round(random.uniform(1500, float(vehicle["capacity_kg"])), 2)
        # Fuel usage: diesel ~35 L/100km at 16 t, electric ~75 kWh/100km (report in L-equiv here as 0 for EV for simplicity)
        if vehicle["fuel_type"] == "ELECTRIC":
            fuel_used = 0.0
        else:
            fuel_used = round(route["distance_km"] * random.uniform(0.30, 0.42), 2)

        yield [
            f"S-{uuid.uuid4().hex[:12].upper()}",
            vehicle["vehicle_id"],
            driver["driver_id"],
            route["route_id"],
            route["origin_warehouse_id"],
            route["dest_warehouse_id"],
            pickup_ts.strftime("%Y-%m-%d %H:%M:%S"),
            delivery_str,
            scheduled_delivery.strftime("%Y-%m-%d %H:%M:%S"),
            weight_kg,
            route["distance_km"],
            fuel_used,
            status,
        ]


def run(writer: Writer, rows: int, start: date, end: date, seed: int | None = 42) -> str:
    ts = datetime.now(timezone.utc)
    key = f"shipments/{partition_key(ts)}/shipments_{int(ts.timestamp())}.csv.gz"
    return writer.write_csv_gz(key, HEADER, generate_rows(rows, start, end, seed=seed))


def main() -> None:
    configure_logging()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rows", type=int, default=500_000)
    p.add_argument("--start", type=date.fromisoformat, default=date(2024, 1, 1))
    p.add_argument("--end", type=date.fromisoformat, default=date.today())
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    writer = make_writer()
    key = run(writer, args.rows, args.start, args.end, seed=args.seed)
    print(key)


if __name__ == "__main__":
    main()
