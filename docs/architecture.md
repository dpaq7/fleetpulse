# Architecture

> System design overview. See `FleetPulse_Project_Blueprint.docx` for full spec.

## Layers

1. **Ingestion** — Python loaders push source data to S3; Snowpipe auto-ingests to `FLEETPULSE_RAW`.
2. **CDC** — Snowflake Streams on `RAW.GPS_EVENTS`, consumed by a Task every 5 minutes.
3. **Transformation** — dbt models: `staging` (views) → `intermediate` (ephemeral) → `marts` (tables, clustered).
4. **Serving** — Streamlit dashboard queries `FLEETPULSE_MARTS` directly via the Snowflake connector.

## Warehouses

| Warehouse      | Size    | Auto-suspend | Use                       |
| -------------- | ------- | ------------ | ------------------------- |
| INGEST_WH      | X-Small | 60s          | Snowpipe + bulk loads     |
| TRANSFORM_WH   | Small   | 60s          | dbt builds                |
| ANALYTICS_WH   | Small   | 60s          | Streamlit + ad-hoc queries|

## Star Schema

- **Facts:** `fact_shipments`, `fact_gps_pings`, `fact_warehouse_events`
- **Dims:** `dim_vehicle` (SCD2), `dim_route`, `dim_warehouse` (SCD2), `dim_driver` (SCD2), `dim_date`, `dim_weather`

## Data Freshness Targets

- GPS pings: 5 min (Streams + Tasks)
- Shipments: 1 hour (batch)
- Warehouse events: 1 hour (batch)
- Weather: event-driven polling
