{{ config(materialized='table', schema='marts') }}

with snap as (
    select * from {{ ref('warehouses_snapshot') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['warehouse_id', 'dbt_valid_from']) }} as warehouse_sk,
    warehouse_id,
    name,
    city,
    province,
    lat,
    lng,
    total_docks,
    capacity_pallets,
    dbt_valid_from as valid_from,
    dbt_valid_to   as valid_to,
    case when dbt_valid_to is null then true else false end as is_current
from snap
