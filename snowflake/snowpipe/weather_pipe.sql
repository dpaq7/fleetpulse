-- ============================================================================
-- FleetPulse — Snowpipe: Weather observations (JSON)
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;
use schema weather;

create or replace pipe pipe_weather
    auto_ingest = true
    comment = 'Continuously ingests OpenWeatherMap JSON from S3'
as
copy into weather_observations (record, city, file_name)
from (
    select
        $1,
        regexp_substr(metadata$filename, 'city=([^/]+)', 1, 1, 'e'),
        metadata$filename
    from @s_weather
)
file_format = (format_name = public.ff_json_gz)
on_error = 'continue';
