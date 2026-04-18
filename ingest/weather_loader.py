"""OpenWeatherMap loader.

Polls the OpenWeatherMap current-weather endpoint for each warehouse city,
writes responses to S3 as JSON, and lands them in RAW.WEATHER via Snowpipe.

Rate limit: free tier is 1,000 calls/day, 60 calls/min.

TODO (Phase 1):
    - City list from dim_warehouse
    - Exponential backoff on 429
    - Idempotent keys: s3://.../weather/dt=YYYY-MM-DD/hh=HH/city.json
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError("weather_loader: implement in Phase 1")


if __name__ == "__main__":
    main()
