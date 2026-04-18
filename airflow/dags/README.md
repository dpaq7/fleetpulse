# Airflow DAGs

| DAG | Schedule | Purpose |
|---|---|---|
| `gps_stream_producer` | every 15 min | Generate 15 min of synthetic GPS pings → S3 → Snowpipe |
| `weather_poller` | hourly | Poll OpenWeatherMap for each warehouse city → S3 → Snowpipe |
| `fleetpulse_daily` | 02:00 UTC | Generate shipments + warehouse events, run dbt snapshot + build + source freshness |

## Local stack

```bash
make airflow-up          # starts postgres + scheduler + webserver on :8080
# login: admin / admin (dev default from docker-compose)
```

The simulator scripts (`ingest.gps_simulator`, etc.) are on the image's
PYTHONPATH via the repo root volume mount.
