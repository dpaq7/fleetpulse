{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw_warehouse', 'warehouse_events') }}
)

select
    event_id,
    warehouse_id,
    dock_id,
    shipment_id,
    upper(event_type)            as event_type,
    pallet_count,
    event_ts,
    to_date(event_ts)            as event_date,
    ingest_ts
from source
where event_ts is not null
qualify row_number() over (partition by event_id order by ingest_ts desc) = 1
