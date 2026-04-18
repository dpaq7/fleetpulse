-- ============================================================================
-- FleetPulse — External Stages (S3)
-- Replace the storage_integration and url values with your own.
-- Pre-req: a Snowflake STORAGE INTEGRATION + matching AWS IAM role.
-- ============================================================================
use role accountadmin;

-- Storage integration (one-time setup; requires IAM role ARN)
create storage integration if not exists fleetpulse_s3_int
    type = external_stage
    storage_provider = 's3'
    enabled = true
    storage_aws_role_arn = 'arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/fleetpulse-snowflake-role'
    storage_allowed_locations = ('s3://fleetpulse-raw/');

grant usage on integration fleetpulse_s3_int to role sysadmin;

use role sysadmin;
use database fleetpulse_raw;
use schema gps;

create or replace stage s_gps_events
    storage_integration = fleetpulse_s3_int
    url = 's3://fleetpulse-raw/gps/'
    file_format = public.ff_json_gz
    comment = 'GPS event landing stage (Snowpipe source)';

use schema weather;
create or replace stage s_weather
    storage_integration = fleetpulse_s3_int
    url = 's3://fleetpulse-raw/weather/'
    file_format = public.ff_json_gz;

use schema shipments;
create or replace stage s_shipments
    storage_integration = fleetpulse_s3_int
    url = 's3://fleetpulse-raw/shipments/'
    file_format = public.ff_csv_gz;

use schema warehouse;
create or replace stage s_warehouse_events
    storage_integration = fleetpulse_s3_int
    url = 's3://fleetpulse-raw/warehouse/'
    file_format = public.ff_csv_gz;
