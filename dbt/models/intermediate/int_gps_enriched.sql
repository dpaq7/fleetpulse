{{ config(materialized='ephemeral') }}

-- GPS pings enriched with the previous ping for the same vehicle.
-- Enables speed-delta + distance-between-pings analytics downstream.

with gps as (
    select * from {{ ref('stg_gps_events') }}
),

lagged as (
    select
        ping_id,
        vehicle_id,
        shipment_id,
        event_ts,
        event_date,
        latitude,
        longitude,
        speed_kmh,
        fuel_level_pct,
        odometer_km,
        lag(event_ts)  over (partition by vehicle_id order by event_ts) as prev_event_ts,
        lag(latitude)  over (partition by vehicle_id order by event_ts) as prev_lat,
        lag(longitude) over (partition by vehicle_id order by event_ts) as prev_lng,
        lag(speed_kmh) over (partition by vehicle_id order by event_ts) as prev_speed_kmh,
        lag(odometer_km) over (partition by vehicle_id order by event_ts) as prev_odometer_km
    from gps
),

derived as (
    select
        *,
        datediff('second', prev_event_ts, event_ts)                as seconds_since_prev,
        speed_kmh - coalesce(prev_speed_kmh, speed_kmh)            as speed_delta_kmh,
        coalesce(odometer_km - prev_odometer_km, 0)                as distance_delta_km
    from lagged
)

select * from derived
