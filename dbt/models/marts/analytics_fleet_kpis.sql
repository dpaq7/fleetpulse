{{ config(materialized='view', schema='analytics') }}

-- Per-day fleet KPIs for the dashboard landing page.

with shipments as (
    select * from {{ ref('fact_shipments') }}
)

select
    pickup_date                                            as activity_date,
    count(*)                                               as total_shipments,
    sum(case when status = 'DELIVERED' then 1 else 0 end)  as delivered_count,
    sum(case when delay_bucket = 'ON_TIME' then 1 else 0 end) as on_time_count,
    round(100.0 * sum(case when delay_bucket = 'ON_TIME' then 1 else 0 end)
                 / nullif(count(*), 0), 2)                 as on_time_pct,
    round(avg(delay_minutes), 1)                           as avg_delay_min,
    round(avg(duration_hrs), 2)                            as avg_duration_hrs,
    sum(distance_km)                                       as total_distance_km,
    sum(fuel_used_l)                                       as total_fuel_l,
    count(distinct vehicle_id)                             as active_vehicles
from shipments
group by 1
order by 1 desc
