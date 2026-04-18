-- ============================================================================
-- FleetPulse — Raw Landing Tables
-- VARIANT for JSON sources, typed columns for CSV.
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;

-- ---------------------------------------------------------------------------
-- GPS telemetry (JSON)
-- ---------------------------------------------------------------------------
use schema gps;
create table if not exists gps_events (
    record           variant         not null,
    file_name        string,
    file_row_number  number,
    ingest_ts        timestamp_ntz   default current_timestamp()
)
cluster by (to_date(record:timestamp::timestamp_ntz))
comment = 'Raw GPS pings from Snowpipe (S3 JSON)';

-- ---------------------------------------------------------------------------
-- Weather (JSON from OpenWeatherMap)
-- ---------------------------------------------------------------------------
use schema weather;
create table if not exists weather_observations (
    record           variant         not null,
    city             string,
    file_name        string,
    ingest_ts        timestamp_ntz   default current_timestamp()
)
cluster by (city, to_date(record:dt::number))
comment = 'Raw weather responses from OpenWeatherMap API';

-- ---------------------------------------------------------------------------
-- Shipments (CSV bulk, ~500K rows)
-- ---------------------------------------------------------------------------
use schema shipments;
create table if not exists shipments (
    shipment_id      string          not null,
    vehicle_id       string,
    driver_id        string,
    route_id         string,
    origin_warehouse_id  string,
    dest_warehouse_id    string,
    pickup_ts        timestamp_ntz,
    delivery_ts      timestamp_ntz,
    scheduled_delivery_ts timestamp_ntz,
    weight_kg        number(10, 2),
    distance_km      number(10, 2),
    fuel_used_l      number(10, 2),
    status           string,
    ingest_ts        timestamp_ntz   default current_timestamp()
)
cluster by (to_date(pickup_ts))
comment = 'Raw shipment records (CSV bulk load)';

-- ---------------------------------------------------------------------------
-- Warehouse events (CSV)
-- ---------------------------------------------------------------------------
use schema warehouse;
create table if not exists warehouse_events (
    event_id         string          not null,
    warehouse_id     string,
    dock_id          string,
    shipment_id      string,
    event_type       string,  -- ARRIVAL / DEPARTURE / SCAN_IN / SCAN_OUT
    pallet_count     number(6, 0),
    event_ts         timestamp_ntz,
    ingest_ts        timestamp_ntz   default current_timestamp()
)
cluster by (to_date(event_ts), warehouse_id)
comment = 'Raw warehouse IoT events (CSV bulk load)';

-- ---------------------------------------------------------------------------
-- Seed: source-of-truth reference data (loaded via dbt seed for portability)
-- ---------------------------------------------------------------------------
use schema seeds;
-- populated by dbt seed; DDL intentionally omitted here.
