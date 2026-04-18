"""OpenWeatherMap loader.

Polls the current-weather endpoint for each warehouse city and writes each
response as a gzipped JSON file to the configured writer. Respects the free
tier's rate limit (60 calls/minute, 1,000 calls/day).

Usage:
    OPENWEATHER_API_KEY=... python -m ingest.weather_loader
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Iterable

import requests

from .reference_data import WAREHOUSES
from .utils import Writer, configure_logging, make_writer, partition_key

log = logging.getLogger("fleetpulse.ingest.weather")

API_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherLoaderError(RuntimeError):
    """Raised when weather fetching fails after retries."""


def fetch_one(city: str, lat: float, lng: float, api_key: str, *, timeout: float = 10.0, retries: int = 3) -> dict:
    """Fetch one city's weather, with exponential backoff on 429/5xx."""
    params = {"lat": lat, "lon": lng, "appid": api_key, "units": "metric"}
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(API_URL, params=params, timeout=timeout)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"{r.status_code}: {r.text[:200]}")
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001 — retry-aware wrapper
            last_exc = exc
            sleep = min(2**attempt, 30)
            log.warning("weather fetch %s failed (attempt %d/%d): %s — sleeping %ds", city, attempt, retries, exc, sleep)
            time.sleep(sleep)
    raise WeatherLoaderError(f"giving up on {city} after {retries} attempts: {last_exc}")


def load_cities(writer: Writer, cities: Iterable[dict], api_key: str, *, qps: float = 1.0) -> list[str]:
    """Fetch and write weather for each city. Returns list of output keys."""
    written: list[str] = []
    ts = datetime.now(timezone.utc)
    for city in cities:
        resp = fetch_one(city["city"], city["lat"], city["lng"], api_key)
        key = f"weather/{partition_key(ts)}/city={city['city']}/weather_{int(ts.timestamp())}.json.gz"
        written.append(writer.write_json_gz(key, [resp]))
        time.sleep(1.0 / qps)  # crude rate limit
    log.info("loaded %d cities", len(written))
    return written


def main() -> None:
    configure_logging()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qps", type=float, default=1.0, help="requests per second cap (default 1.0)")
    args = p.parse_args()

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise SystemExit("OPENWEATHER_API_KEY is not set")

    writer = make_writer()
    keys = load_cities(writer, WAREHOUSES, api_key, qps=args.qps)
    print(json.dumps({"written": keys}, indent=2))


if __name__ == "__main__":
    main()
