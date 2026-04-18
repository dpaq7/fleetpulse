"""GPS telemetry simulator.

Generates synthetic GPS pings along known routes and writes them as gzipped
JSON arrays to the configured writer (local or S3). Each file lands under:

    gps/dt=YYYY-MM-DD/hh=HH/gps_<vehicle>_<epoch>.json.gz

Snowpipe picks these up from S3 and loads them into `fleetpulse_raw.gps.gps_events`.

Usage:
    python -m ingest.gps_simulator --vehicles 10 --duration-min 30 --ping-sec 5
    FLEETPULSE_WRITER=s3 AWS_S3_BUCKET=fleetpulse-raw python -m ingest.gps_simulator ...
"""
from __future__ import annotations

import argparse
import logging
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .reference_data import ROUTES, VEHICLES, WAREHOUSES
from .utils import Writer, configure_logging, haversine_km, iso_z, make_writer, partition_key

log = logging.getLogger("fleetpulse.ingest.gps")


@dataclass
class VehicleState:
    vehicle_id: str
    shipment_id: str
    route_id: str
    origin: tuple[float, float]
    dest: tuple[float, float]
    fuel_level_pct: float = 95.0
    odometer_km: float = 0.0


def _warehouse_by_id(wid: str) -> dict:
    return next(w for w in WAREHOUSES if w["warehouse_id"] == wid)


def _interpolate(origin: tuple[float, float], dest: tuple[float, float], progress: float) -> tuple[float, float]:
    return (
        origin[0] + (dest[0] - origin[0]) * progress,
        origin[1] + (dest[1] - origin[1]) * progress,
    )


def _jitter(value: float, scale: float) -> float:
    return value + random.uniform(-scale, scale)


def simulate_ping(state: VehicleState, event_ts: datetime, progress: float) -> dict:
    """Produce a single GPS ping record."""
    base_lat, base_lng = _interpolate(state.origin, state.dest, progress)
    lat = _jitter(base_lat, 0.001)
    lng = _jitter(base_lng, 0.001)

    # Speed model: ramp up, hold, ramp down
    if progress < 0.1:
        speed = 20 + progress * 600  # 20 → 80 km/h
    elif progress > 0.9:
        speed = 80 - (progress - 0.9) * 600  # 80 → 20 km/h
    else:
        speed = random.gauss(95, 8)
    speed = max(0.0, min(speed, 130.0))

    # Fuel burn roughly proportional to distance travelled this tick
    total_km = haversine_km(*state.origin, *state.dest)
    distance_tick = total_km / max(1, int(total_km / 1))  # ~1 km per tick
    state.odometer_km += distance_tick * 0.01  # soften
    state.fuel_level_pct = max(state.fuel_level_pct - random.uniform(0.01, 0.05), 5.0)

    return {
        "ping_id": str(uuid.uuid4()),
        "vehicle_id": state.vehicle_id,
        "shipment_id": state.shipment_id,
        "route_id": state.route_id,
        "timestamp": iso_z(event_ts),
        "lat": round(lat, 6),
        "lng": round(lng, 6),
        "speed_kmh": round(speed, 2),
        "heading_deg": round(random.uniform(0, 360), 2),
        "fuel_level_pct": round(state.fuel_level_pct, 2),
        "odometer_km": round(state.odometer_km, 2),
    }


def build_fleet(n_vehicles: int, seed: int | None = None) -> list[VehicleState]:
    if seed is not None:
        random.seed(seed)
    vehicles = VEHICLES[:n_vehicles]
    states: list[VehicleState] = []
    for v in vehicles:
        route = random.choice(ROUTES)
        origin = _warehouse_by_id(route["origin_warehouse_id"])
        dest = _warehouse_by_id(route["dest_warehouse_id"])
        states.append(
            VehicleState(
                vehicle_id=v["vehicle_id"],
                shipment_id=f"S-{uuid.uuid4().hex[:10].upper()}",
                route_id=route["route_id"],
                origin=(origin["lat"], origin["lng"]),
                dest=(dest["lat"], dest["lng"]),
            )
        )
    return states


def run(
    writer: Writer,
    n_vehicles: int = 10,
    duration_min: int = 30,
    ping_sec: int = 5,
    start_ts: datetime | None = None,
    seed: int | None = 42,
) -> list[str]:
    """Generate a batch run. Returns list of written keys."""
    start = start_ts or datetime.now(timezone.utc)
    fleet = build_fleet(n_vehicles, seed=seed)
    ticks = (duration_min * 60) // ping_sec
    written: list[str] = []

    # Bucket pings per-vehicle per-minute → one file per bucket keeps Snowpipe
    # files small (5-50 MB is optimal).
    buffers: dict[tuple[str, str], list[dict]] = {}

    for tick in range(ticks):
        ts = start + timedelta(seconds=tick * ping_sec)
        progress = tick / max(1, ticks - 1)
        for state in fleet:
            rec = simulate_ping(state, ts, progress)
            bucket_key = (state.vehicle_id, ts.strftime("%Y%m%d%H%M"))
            buffers.setdefault(bucket_key, []).append(rec)

    for (vehicle_id, _bucket), records in buffers.items():
        first_ts = datetime.strptime(records[0]["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        key = f"gps/{partition_key(first_ts)}/gps_{vehicle_id}_{int(first_ts.timestamp())}.json.gz"
        written.append(writer.write_json_gz(key, records))

    log.info("generated %d files covering %d vehicles for %d minutes", len(written), n_vehicles, duration_min)
    return written


def main() -> None:
    configure_logging()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vehicles", type=int, default=10)
    p.add_argument("--duration-min", type=int, default=30)
    p.add_argument("--ping-sec", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    writer = make_writer()
    run(
        writer=writer,
        n_vehicles=args.vehicles,
        duration_min=args.duration_min,
        ping_sec=args.ping_sec,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
