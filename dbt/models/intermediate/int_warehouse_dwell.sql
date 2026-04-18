{{ config(materialized='ephemeral') }}

-- Computes dwell time per shipment at each warehouse from paired
-- ARRIVAL / DEPARTURE events. Uses PIVOT (dynamic-style) to collapse the
-- event sequence into a single row per shipment-warehouse pair.

with events as (
    select
        warehouse_id,
        dock_id,
        shipment_id,
        event_type,
        event_ts,
        event_date
    from {{ ref('stg_warehouse_events') }}
    where event_type in ('ARRIVAL', 'DEPARTURE')
),

pivoted as (
    select
        warehouse_id,
        dock_id,
        shipment_id,
        max(case when event_type = 'ARRIVAL'   then event_ts end) as arrival_ts,
        max(case when event_type = 'DEPARTURE' then event_ts end) as departure_ts
    from events
    group by 1, 2, 3
)

select
    warehouse_id,
    dock_id,
    shipment_id,
    arrival_ts,
    departure_ts,
    to_date(arrival_ts)                                             as arrival_date,
    datediff('minute', arrival_ts, departure_ts)                    as dwell_minutes
from pivoted
where arrival_ts is not null
  and departure_ts is not null
  and departure_ts >= arrival_ts
