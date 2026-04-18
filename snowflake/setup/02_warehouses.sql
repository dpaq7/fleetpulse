-- ============================================================================
-- FleetPulse — Virtual Warehouses
-- Sized for trial-account budget; all auto-suspend at 60s.
-- ============================================================================
use role sysadmin;

create warehouse if not exists ingest_wh
    warehouse_size = xsmall
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true
    comment = 'Snowpipe + COPY INTO bulk loads';

create warehouse if not exists transform_wh
    warehouse_size = small
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true
    comment = 'dbt builds';

create warehouse if not exists analytics_wh
    warehouse_size = small
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true
    comment = 'Streamlit + ad-hoc analysts';
