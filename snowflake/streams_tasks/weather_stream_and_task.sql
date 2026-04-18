-- ============================================================================
-- FleetPulse — Stream + Task: CDC on Weather observations
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;
use schema weather;

create table if not exists weather_typed (
    city             string          not null,
    observed_ts      timestamp_ntz   not null,
    temp_c           number(5, 2),
    feels_like_c     number(5, 2),
    humidity_pct     number(5, 2),
    pressure_hpa     number(7, 2),
    wind_speed_kmh   number(6, 2),
    wind_deg         number(5, 2),
    condition_main   string,
    condition_desc   string,
    visibility_km    number(6, 2),
    precipitation_mm number(6, 2),
    ingest_ts        timestamp_ntz   default current_timestamp(),
    constraint pk_weather_typed primary key (city, observed_ts)
);

create or replace stream stream_weather_new
    on table weather_observations
    append_only = true;

create or replace task task_merge_weather
    warehouse = ingest_wh
    schedule = '15 minute'
    when system$stream_has_data('fleetpulse_raw.weather.stream_weather_new')
as
merge into weather_typed t
using (
    select
        coalesce(city, record:name::string) as city,
        to_timestamp_ntz(record:dt::number) as observed_ts,
        record:main.temp::number(5, 2)          as temp_c,
        record:main.feels_like::number(5, 2)    as feels_like_c,
        record:main.humidity::number(5, 2)      as humidity_pct,
        record:main.pressure::number(7, 2)      as pressure_hpa,
        (record:wind.speed::number * 3.6)::number(6, 2) as wind_speed_kmh,
        record:wind.deg::number(5, 2)           as wind_deg,
        record:weather[0].main::string          as condition_main,
        record:weather[0].description::string   as condition_desc,
        (record:visibility::number / 1000)::number(6, 2) as visibility_km,
        coalesce(record:rain."1h"::number, record:snow."1h"::number, 0)::number(6, 2) as precipitation_mm
    from stream_weather_new
) s
on t.city = s.city and t.observed_ts = s.observed_ts
when not matched then
    insert (city, observed_ts, temp_c, feels_like_c, humidity_pct, pressure_hpa,
            wind_speed_kmh, wind_deg, condition_main, condition_desc,
            visibility_km, precipitation_mm)
    values (s.city, s.observed_ts, s.temp_c, s.feels_like_c, s.humidity_pct,
            s.pressure_hpa, s.wind_speed_kmh, s.wind_deg, s.condition_main,
            s.condition_desc, s.visibility_km, s.precipitation_mm);

alter task task_merge_weather resume;
