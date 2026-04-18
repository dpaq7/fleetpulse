{{ config(materialized='table', schema='marts') }}

-- SCD2 dimension from the snapshot table.

with snap as (
    select * from {{ ref('vehicles_snapshot') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['vehicle_id', 'dbt_valid_from']) }} as vehicle_sk,
    vehicle_id,
    make,
    model,
    year,
    fuel_type,
    capacity_kg,
    status,
    dbt_valid_from as valid_from,
    dbt_valid_to   as valid_to,
    case when dbt_valid_to is null then true else false end as is_current
from snap
