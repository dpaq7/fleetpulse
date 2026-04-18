-- ============================================================================
-- FleetPulse — Snowpipe: GPS events (JSON)
-- Event-driven auto-ingest from s3://fleetpulse-raw/gps/
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;
use schema gps;

create or replace pipe pipe_gps_events
    auto_ingest = true
    comment = 'Continuously ingests GPS ping JSON files from S3'
as
copy into gps_events (record, file_name, file_row_number)
from (
    select
        $1,
        metadata$filename,
        metadata$file_row_number
    from @s_gps_events
)
file_format = (format_name = public.ff_json_gz)
on_error = 'continue';

-- Grab the notification channel ARN for the S3 → SQS event notification:
-- show pipes like 'pipe_gps_events';
-- copy the NOTIFICATION_CHANNEL value into the S3 bucket event config.
