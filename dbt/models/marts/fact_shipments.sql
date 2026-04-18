{{
    config(
        materialized='incremental',
        unique_key='shipment_id',
        incremental_strategy='merge',
        cluster_by=['pickup_date', 'route_id'],
        schema='marts'
    )
}}

-- Grain: one row per shipment. Clustered on pickup_date + route_id for fast
-- route-level time-range queries.

with base as (
    select * from {{ ref('int_route_performance') }}
    {% if is_incremental() %}
      where pickup_ts >= coalesce(
          (select dateadd(day, -1, max(pickup_ts)) from {{ this }}),
          '1900-01-01'::timestamp
      )
    {% endif %}
),

joined as (
    select
        b.shipment_id,
        v.vehicle_sk,
        d.driver_sk,
        r.route_sk,
        ow.warehouse_sk   as origin_warehouse_sk,
        dw.warehouse_sk   as dest_warehouse_sk,
        b.vehicle_id,
        b.driver_id,
        b.route_id,
        b.origin_warehouse_id,
        b.dest_warehouse_id,
        b.pickup_ts,
        b.delivery_ts,
        b.scheduled_delivery_ts,
        b.pickup_date,
        b.status,
        b.weight_kg,
        b.route_distance_km      as distance_km,
        b.typical_duration_hrs,
        b.duration_hrs,
        b.delay_minutes,
        b.delay_bucket,
        b.duration_vs_typical_ratio,
        b.fuel_used_l,
        b.pickup_temp_c,
        b.pickup_wind_kmh,
        b.pickup_condition,
        b.pickup_precip_mm
    from base b
    left join {{ ref('dim_vehicle') }}    v  on b.vehicle_id = v.vehicle_id  and v.is_current
    left join {{ ref('dim_driver') }}     d  on b.driver_id  = d.driver_id   and d.is_current
    left join {{ ref('dim_route') }}      r  on b.route_id   = r.route_id
    left join {{ ref('dim_warehouse') }}  ow on b.origin_warehouse_id = ow.warehouse_id and ow.is_current
    left join {{ ref('dim_warehouse') }}  dw on b.dest_warehouse_id   = dw.warehouse_id and dw.is_current
)

select * from joined
