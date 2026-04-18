{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        cluster_by=['event_date', 'warehouse_id'],
        schema='marts'
    )
}}

-- Grain: one row per warehouse event. Joined to dwell measures where ARRIVAL
-- is paired with DEPARTURE for the same (warehouse, shipment).

with events as (
    select * from {{ ref('stg_warehouse_events') }}
    {% if is_incremental() %}
      where event_ts >= coalesce(
          (select dateadd(hour, -2, max(event_ts)) from {{ this }}),
          '1900-01-01'::timestamp
      )
    {% endif %}
),

dwell as (
    select * from {{ ref('int_warehouse_dwell') }}
),

dock_util as (
    select
        warehouse_id,
        event_date,
        count(*) / nullif(24.0, 0) as events_per_hour
    from events
    group by 1, 2
)

select
    e.event_id,
    e.warehouse_id,
    e.dock_id,
    e.shipment_id,
    e.event_type,
    e.event_ts,
    e.event_date,
    e.pallet_count,
    d.dwell_minutes,
    du.events_per_hour
from events e
left join dwell    d  on e.shipment_id = d.shipment_id and e.warehouse_id = d.warehouse_id
left join dock_util du on e.warehouse_id = du.warehouse_id and e.event_date = du.event_date
