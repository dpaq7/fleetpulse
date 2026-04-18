{{ config(materialized='table', schema='marts') }}

with snap as (
    select * from {{ ref('drivers_snapshot') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['driver_id', 'dbt_valid_from']) }} as driver_sk,
    driver_id,
    name,
    license_class,
    hire_date,
    years_experience,
    dbt_valid_from as valid_from,
    dbt_valid_to   as valid_to,
    case when dbt_valid_to is null then true else false end as is_current
from snap
