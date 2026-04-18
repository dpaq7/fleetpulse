{{
    config(
        materialized='incremental',
        unique_key='ping_id',
        incremental_strategy='merge',
        cluster_by=['event_date', 'vehicle_id'],
        schema='marts'
    )
}}

-- Grain: one row per GPS ping. Clustered on event_date + vehicle_id.

with base as (
    select * from {{ ref('int_gps_enriched') }}
    {% if is_incremental() %}
      where event_ts >= coalesce(
          (select dateadd(minute, -10, max(event_ts)) from {{ this }}),
          '1900-01-01'::timestamp
      )
    {% endif %}
)

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
    seconds_since_prev,
    speed_delta_kmh,
    distance_delta_km,
    ntile(4) over (partition by event_date order by speed_kmh) as speed_quartile
from base
