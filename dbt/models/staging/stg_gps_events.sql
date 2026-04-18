{{ config(materialized='view') }}

-- Clean, typed staging view over the 5-minute-merged GPS table.
-- Casts, dedupe via QUALIFY, basic coordinate sanity.

with source as (
    select * from {{ source('raw_gps', 'gps_events_typed') }}
),

renamed as (
    select
        ping_id,
        vehicle_id,
        shipment_id,
        event_ts,
        to_date(event_ts)                        as event_date,
        latitude,
        longitude,
        speed_kmh,
        heading_deg,
        fuel_level_pct,
        odometer_km,
        ingest_ts
    from source
    where latitude  between -90  and 90
      and longitude between -180 and 180
)

select *
from renamed
qualify row_number() over (partition by ping_id order by ingest_ts desc) = 1
