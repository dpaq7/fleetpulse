-- ============================================================================
-- FleetPulse — Roles & Grants
-- Creates a dev, ci, and prod role with least-privilege access.
-- Run as: ACCOUNTADMIN
-- ============================================================================
use role accountadmin;

create role if not exists fleetpulse_dev_role;
create role if not exists fleetpulse_ci_role;
create role if not exists fleetpulse_prod_role;

-- Role hierarchy: all roles roll up into SYSADMIN
grant role fleetpulse_dev_role  to role sysadmin;
grant role fleetpulse_ci_role   to role sysadmin;
grant role fleetpulse_prod_role to role sysadmin;

-- Warehouse usage
grant usage on warehouse ingest_wh    to role fleetpulse_dev_role;
grant usage on warehouse transform_wh to role fleetpulse_dev_role;
grant usage on warehouse analytics_wh to role fleetpulse_dev_role;

grant usage on warehouse transform_wh to role fleetpulse_ci_role;

grant usage on warehouse ingest_wh    to role fleetpulse_prod_role;
grant usage on warehouse transform_wh to role fleetpulse_prod_role;
grant usage on warehouse analytics_wh to role fleetpulse_prod_role;

-- Database access
grant usage on database fleetpulse_raw     to role fleetpulse_dev_role;
grant usage on database fleetpulse_staging to role fleetpulse_dev_role;
grant usage on database fleetpulse_marts   to role fleetpulse_dev_role;

grant usage on all schemas in database fleetpulse_raw     to role fleetpulse_dev_role;
grant usage on all schemas in database fleetpulse_staging to role fleetpulse_dev_role;
grant usage on all schemas in database fleetpulse_marts   to role fleetpulse_dev_role;

grant select on all tables    in database fleetpulse_raw to role fleetpulse_dev_role;
grant select on future tables in database fleetpulse_raw to role fleetpulse_dev_role;

-- dev role needs write in staging + marts for dbt
grant create schema on database fleetpulse_staging to role fleetpulse_dev_role;
grant create schema on database fleetpulse_marts   to role fleetpulse_dev_role;

grant all privileges on schema fleetpulse_staging.dev to role fleetpulse_dev_role;
grant all privileges on schema fleetpulse_marts.dev   to role fleetpulse_dev_role;

-- CI role: write only to ci schemas
grant usage on database fleetpulse_raw     to role fleetpulse_ci_role;
grant usage on database fleetpulse_staging to role fleetpulse_ci_role;
grant usage on database fleetpulse_marts   to role fleetpulse_ci_role;
grant select on all tables in database fleetpulse_raw to role fleetpulse_ci_role;
grant all privileges on schema fleetpulse_staging.ci to role fleetpulse_ci_role;
grant all privileges on schema fleetpulse_marts.ci   to role fleetpulse_ci_role;

-- prod role: full write to prod schemas
grant all privileges on schema fleetpulse_staging.prod   to role fleetpulse_prod_role;
grant all privileges on schema fleetpulse_marts.prod     to role fleetpulse_prod_role;
grant all privileges on schema fleetpulse_marts.analytics to role fleetpulse_prod_role;

-- ============================================================================
-- Create service users (passwords to be set manually after creation)
-- ============================================================================
-- create user fleetpulse_dev password = '<set-me>' default_role = fleetpulse_dev_role default_warehouse = transform_wh;
-- create user fleetpulse_ci  password = '<set-me>' default_role = fleetpulse_ci_role  default_warehouse = transform_wh;
-- create user fleetpulse_prod password = '<set-me>' default_role = fleetpulse_prod_role default_warehouse = transform_wh;

-- grant role fleetpulse_dev_role  to user fleetpulse_dev;
-- grant role fleetpulse_ci_role   to user fleetpulse_ci;
-- grant role fleetpulse_prod_role to user fleetpulse_prod;
