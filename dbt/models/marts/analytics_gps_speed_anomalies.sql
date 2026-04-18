{{ config(materialized='view', schema='analytics') }}

-- Candidate anomalies: large speed delta between consecutive pings, or
-- implausibly high speed. Feeds the Anomaly Alerts dashboard page.

with pings as (
    select * from {{ ref('fact_gps_pings') }}
    where event_date >= dateadd(day, -7, current_date())
)

select
    ping_id,
    vehicle_id,
    shipment_id,
    event_ts,
    latitude,
    longitude,
    speed_kmh,
    speed_delta_kmh,
    seconds_since_prev,
    case
        when speed_kmh > 140           then 'OVERSPEED'
        when abs(speed_delta_kmh) > 40 and seconds_since_prev <= 30 then 'HARSH_ACCELERATION'
        when fuel_level_pct < 10       then 'LOW_FUEL'
    end as anomaly_type
from pings
where speed_kmh > 140
   or (abs(speed_delta_kmh) > 40 and seconds_since_prev <= 30)
   or fuel_level_pct < 10
