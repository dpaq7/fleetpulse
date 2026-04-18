# Snowpipe

Event-driven auto-ingestion pipes. Each pipe has a corresponding S3 → SQS
notification (retrieve via `SHOW PIPES` and wire into the bucket event config).

| Pipe | Source | Target |
|---|---|---|
| `pipe_gps_events` | `s3://fleetpulse-raw/gps/` | `fleetpulse_raw.gps.gps_events` |
| `pipe_weather`    | `s3://fleetpulse-raw/weather/` | `fleetpulse_raw.weather.weather_observations` |

## Shipment + warehouse loads

These are bulk/hourly, not streaming — loaded via Airflow `COPY INTO` tasks
rather than Snowpipe. See `airflow/dags/fleetpulse_daily.py`.

## Monitoring

```sql
-- Pipe status
select system$pipe_status('fleetpulse_raw.gps.pipe_gps_events');

-- Recent files
select *
from table(information_schema.copy_history(
    table_name=>'fleetpulse_raw.gps.gps_events',
    start_time=>dateadd(hour, -24, current_timestamp())
));
```
