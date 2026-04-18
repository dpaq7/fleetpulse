"""GPS telemetry simulator.

Generates synthetic GPS pings (vehicle_id, lat, lng, speed_kmh, fuel_level_pct,
heading, timestamp) and writes them as JSON to S3, where Snowpipe auto-ingests
them into RAW.GPS_EVENTS.

TODO (Phase 1):
    - Route-aware path generator between origin/dest pairs from dim_route
    - Configurable fleet size and ping interval (default 5s)
    - Batched S3 uploads via boto3
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError("gps_simulator: implement in Phase 1")


if __name__ == "__main__":
    main()
