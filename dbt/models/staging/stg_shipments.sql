{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw_shipments', 'shipments') }}
),

cleaned as (
    select
        shipment_id,
        vehicle_id,
        driver_id,
        route_id,
        origin_warehouse_id,
        dest_warehouse_id,
        pickup_ts,
        delivery_ts,
        scheduled_delivery_ts,
        weight_kg,
        distance_km,
        fuel_used_l,
        upper(status)                              as status,
        to_date(pickup_ts)                         as pickup_date,
        datediff('minute', scheduled_delivery_ts, delivery_ts) as delay_minutes,
        case when delivery_ts is not null
             then datediff('minute', pickup_ts, delivery_ts) / 60.0
        end                                        as duration_hrs,
        ingest_ts
    from source
    where shipment_id is not null
      and pickup_ts is not null
)

select *
from cleaned
qualify row_number() over (partition by shipment_id order by ingest_ts desc) = 1
