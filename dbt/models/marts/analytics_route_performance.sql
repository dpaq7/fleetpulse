{{ config(materialized='view', schema='analytics') }}

-- Per-route performance summary + weather correlation.

with shipments as (
    select * from {{ ref('fact_shipments') }}
    where pickup_date >= dateadd(day, -90, current_date())
)

select
    route_id,
    origin_warehouse_id,
    dest_warehouse_id,
    count(*)                                         as shipment_count,
    round(avg(duration_hrs), 2)                      as avg_duration_hrs,
    round(avg(typical_duration_hrs), 2)              as baseline_hrs,
    round(avg(duration_vs_typical_ratio), 3)         as ratio_vs_typical,
    round(avg(delay_minutes), 1)                     as avg_delay_min,
    round(100.0 * sum(case when delay_bucket = 'ON_TIME' then 1 else 0 end)
                 / nullif(count(*), 0), 2)           as on_time_pct,
    round(avg(fuel_used_l / nullif(distance_km, 0) * 100), 2) as l_per_100km,
    round(avg(case when pickup_precip_mm > 0 then duration_hrs end), 2) as avg_duration_wet,
    round(avg(case when pickup_precip_mm = 0 then duration_hrs end), 2) as avg_duration_dry
from shipments
group by 1, 2, 3
order by shipment_count desc
