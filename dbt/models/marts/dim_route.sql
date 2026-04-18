{{ config(materialized='table', schema='marts') }}

-- Type-1 dimension: overwrite in place.

select
    {{ dbt_utils.generate_surrogate_key(['route_id']) }}    as route_sk,
    route_id,
    origin_warehouse_id,
    dest_warehouse_id,
    distance_km,
    typical_duration_hrs
from {{ ref('routes') }}
