{{ config(materialized='ephemeral') }}

-- Joins each shipment to the weather observation closest to pickup time at
-- its origin city. Uses a lateral correlated subquery (QUALIFY-style).

with shipments as (
    select * from {{ ref('stg_shipments') }}
),

warehouses as (
    select * from {{ ref('warehouses') }}
),

weather as (
    select * from {{ ref('stg_weather') }}
),

shipments_with_city as (
    select
        s.*,
        w.city as origin_city
    from shipments s
    inner join warehouses w
        on s.origin_warehouse_id = w.warehouse_id
),

joined as (
    select
        s.*,
        wx.temp_c          as pickup_temp_c,
        wx.wind_speed_kmh  as pickup_wind_kmh,
        wx.condition_main  as pickup_condition,
        wx.precipitation_mm as pickup_precip_mm,
        wx.observed_ts     as pickup_weather_ts
    from shipments_with_city s
    left join weather wx
        on  wx.city = s.origin_city
        and wx.observed_ts between dateadd(hour, -2, s.pickup_ts) and dateadd(hour, 2, s.pickup_ts)
    qualify row_number() over (
        partition by s.shipment_id
        order by abs(datediff('minute', wx.observed_ts, s.pickup_ts)) asc nulls last
    ) = 1
)

select * from joined
