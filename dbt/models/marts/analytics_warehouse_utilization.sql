{{ config(materialized='view', schema='analytics') }}

with events as (
    select * from {{ ref('fact_warehouse_events') }}
    where event_date >= dateadd(day, -30, current_date())
),

by_warehouse_day as (
    select
        warehouse_id,
        event_date,
        count(distinct dock_id)                           as docks_in_use,
        count(distinct shipment_id)                       as shipments_processed,
        sum(pallet_count)                                 as pallets_moved,
        round(avg(dwell_minutes), 1)                      as avg_dwell_min
    from events
    group by 1, 2
)

select
    wd.*,
    w.name                                                as warehouse_name,
    w.city,
    w.total_docks,
    round(100.0 * wd.docks_in_use / nullif(w.total_docks, 0), 2) as dock_utilization_pct
from by_warehouse_day wd
inner join {{ ref('dim_warehouse') }} w
    on wd.warehouse_id = w.warehouse_id and w.is_current
order by event_date desc, warehouse_id
