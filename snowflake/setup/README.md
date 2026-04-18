# Snowflake Setup

Run these scripts in order — once per environment — as `ACCOUNTADMIN`.

| # | Script | Role | Purpose |
|---|---|---|---|
| 01 | `01_databases_and_schemas.sql` | `SYSADMIN` | Create `FLEETPULSE_RAW`, `_STAGING`, `_MARTS` + schemas |
| 02 | `02_warehouses.sql` | `SYSADMIN` | `INGEST_WH` (XS), `TRANSFORM_WH` (S), `ANALYTICS_WH` (S) |
| 03 | `03_roles_and_grants.sql` | `ACCOUNTADMIN` | `FLEETPULSE_DEV_ROLE`, `_CI_ROLE`, `_PROD_ROLE` + grants |
| 04 | `04_file_formats.sql` | `SYSADMIN` | JSON + CSV formats |
| 05 | `05_stages.sql` | `ACCOUNTADMIN` | S3 storage integration + external stages |
| 06 | `06_raw_tables.sql` | `SYSADMIN` | `GPS_EVENTS`, `WEATHER_OBSERVATIONS`, `SHIPMENTS`, `WAREHOUSE_EVENTS` |

After 01-06, proceed to:

- `../snowpipe/` — event-driven auto-ingest pipes
- `../streams_tasks/` — CDC streams + 5-minute refresh tasks

## Quick run

```bash
# SnowSQL
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USER \
  -f snowflake/setup/01_databases_and_schemas.sql

# Or paste sequentially into the Snowsight UI.
```

## Post-setup

Create the dev user manually (uncomment block in `03_roles_and_grants.sql`), then populate `.env` with:

```
SNOWFLAKE_ACCOUNT=<org-account>
SNOWFLAKE_USER=fleetpulse_dev
SNOWFLAKE_PASSWORD=<set>
SNOWFLAKE_ROLE=FLEETPULSE_DEV_ROLE
SNOWFLAKE_WAREHOUSE=TRANSFORM_WH
SNOWFLAKE_DATABASE=FLEETPULSE_MARTS
SNOWFLAKE_SCHEMA=DEV
```
