{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw_weather', 'weather_typed') }}
)

select
    city,
    observed_ts,
    to_date(observed_ts)         as observed_date,
    temp_c,
    feels_like_c,
    humidity_pct,
    pressure_hpa,
    wind_speed_kmh,
    wind_deg,
    condition_main,
    condition_desc,
    visibility_km,
    precipitation_mm,
    ingest_ts
from source
where observed_ts is not null
qualify row_number() over (partition by city, observed_ts order by ingest_ts desc) = 1
