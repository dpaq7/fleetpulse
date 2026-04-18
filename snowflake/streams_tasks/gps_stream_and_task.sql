-- ============================================================================
-- FleetPulse — Stream + Task: CDC on GPS events
-- Captures new rows from RAW.GPS_EVENTS every 5 minutes and merges them into
-- a parsed/typed table ready for dbt consumption.
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;
use schema gps;

-- ---------------------------------------------------------------------------
-- Parsed downstream table (typed view of the VARIANT)
-- ---------------------------------------------------------------------------
create table if not exists gps_events_typed (
    ping_id          string          not null,
    vehicle_id       string          not null,
    shipment_id      string,
    event_ts         timestamp_ntz   not null,
    latitude         number(9, 6),
    longitude        number(9, 6),
    speed_kmh        number(6, 2),
    heading_deg      number(5, 2),
    fuel_level_pct   number(5, 2),
    odometer_km      number(10, 2),
    ingest_ts        timestamp_ntz   default current_timestamp(),
    constraint pk_gps_events_typed primary key (ping_id)
)
cluster by (to_date(event_ts), vehicle_id)
comment = 'Typed GPS events, fed by stream every 5 minutes';

-- ---------------------------------------------------------------------------
-- Stream on the raw VARIANT table
-- ---------------------------------------------------------------------------
create or replace stream stream_gps_events_new
    on table gps_events
    append_only = true
    comment = 'Append-only CDC stream for Snowpipe-loaded GPS events';

-- ---------------------------------------------------------------------------
-- Task: runs every 5 minutes, merges new records into typed table
-- ---------------------------------------------------------------------------
create or replace task task_merge_gps_events
    warehouse = ingest_wh
    schedule = '5 minute'
    when system$stream_has_data('fleetpulse_raw.gps.stream_gps_events_new')
as
merge into gps_events_typed t
using (
    select
        record:ping_id::string        as ping_id,
        record:vehicle_id::string     as vehicle_id,
        record:shipment_id::string    as shipment_id,
        record:timestamp::timestamp_ntz as event_ts,
        record:lat::number(9, 6)      as latitude,
        record:lng::number(9, 6)      as longitude,
        record:speed_kmh::number(6, 2) as speed_kmh,
        record:heading_deg::number(5, 2) as heading_deg,
        record:fuel_level_pct::number(5, 2) as fuel_level_pct,
        record:odometer_km::number(10, 2) as odometer_km
    from stream_gps_events_new
    where record:ping_id is not null
) s
on t.ping_id = s.ping_id
when not matched then
    insert (ping_id, vehicle_id, shipment_id, event_ts, latitude, longitude,
            speed_kmh, heading_deg, fuel_level_pct, odometer_km)
    values (s.ping_id, s.vehicle_id, s.shipment_id, s.event_ts, s.latitude,
            s.longitude, s.speed_kmh, s.heading_deg, s.fuel_level_pct,
            s.odometer_km);

-- Resume the task (created suspended by default)
alter task task_merge_gps_events resume;
