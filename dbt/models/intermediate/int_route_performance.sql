{{ config(materialized='ephemeral') }}

-- Per-shipment performance metrics + route context for fact tables.

with shipments as (
    select * from {{ ref('int_shipment_weather') }}
),

routes as (
    select * from {{ ref('routes') }}
)

select
    s.shipment_id,
    s.vehicle_id,
    s.driver_id,
    s.route_id,
    s.origin_warehouse_id,
    s.dest_warehouse_id,
    s.pickup_ts,
    s.delivery_ts,
    s.scheduled_delivery_ts,
    s.pickup_date,
    s.status,
    s.weight_kg,
    r.distance_km                                         as route_distance_km,
    r.typical_duration_hrs,
    s.fuel_used_l,
    s.duration_hrs,
    s.delay_minutes,
    case
        when s.delay_minutes is null            then 'UNKNOWN'
        when s.delay_minutes <=  5               then 'ON_TIME'
        when s.delay_minutes <= 30               then 'SLIGHTLY_LATE'
        when s.delay_minutes <= 120              then 'LATE'
        else 'SEVERELY_LATE'
    end                                                   as delay_bucket,
    case when r.typical_duration_hrs > 0
         then s.duration_hrs / r.typical_duration_hrs
    end                                                   as duration_vs_typical_ratio,
    s.pickup_temp_c,
    s.pickup_wind_kmh,
    s.pickup_condition,
    s.pickup_precip_mm
from shipments s
left join routes r on s.route_id = r.route_id
