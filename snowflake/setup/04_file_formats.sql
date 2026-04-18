-- ============================================================================
-- FleetPulse — File Formats
-- ============================================================================
use role sysadmin;
use database fleetpulse_raw;

create or replace file format public.ff_json_gz
    type = json
    compression = gzip
    strip_outer_array = true
    comment = 'Gzipped JSON arrays from S3 (GPS + weather)';

create or replace file format public.ff_csv_gz
    type = csv
    compression = gzip
    field_delimiter = ','
    skip_header = 1
    field_optionally_enclosed_by = '"'
    empty_field_as_null = true
    null_if = ('', 'NULL', 'null')
    trim_space = true
    comment = 'Gzipped CSV for historical shipment + warehouse files';
