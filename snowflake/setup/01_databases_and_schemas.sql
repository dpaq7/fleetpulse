-- ============================================================================
-- FleetPulse — Databases & Schemas
-- Run as: ACCOUNTADMIN (or SYSADMIN after roles granted)
-- ============================================================================
use role sysadmin;

create database if not exists fleetpulse_raw
    comment = 'FleetPulse raw landing zone (Snowpipe + bulk loads)';

create database if not exists fleetpulse_staging
    comment = 'FleetPulse staging layer (dbt views)';

create database if not exists fleetpulse_marts
    comment = 'FleetPulse presentation layer (dbt tables: facts + dims)';

-- RAW schemas (one per source)
use database fleetpulse_raw;
create schema if not exists gps          comment = 'GPS telemetry (JSON variant)';
create schema if not exists shipments    comment = 'Shipment records (CSV bulk)';
create schema if not exists warehouse    comment = 'Warehouse IoT events';
create schema if not exists weather      comment = 'OpenWeatherMap responses';
create schema if not exists seeds        comment = 'Reference data';

-- STAGING schemas
use database fleetpulse_staging;
create schema if not exists dev          comment = 'Developer sandbox';
create schema if not exists ci           comment = 'CI build schema';
create schema if not exists prod         comment = 'Production staging views';

-- MARTS schemas
use database fleetpulse_marts;
create schema if not exists dev          comment = 'Developer sandbox';
create schema if not exists ci           comment = 'CI build schema';
create schema if not exists prod         comment = 'Production marts';
create schema if not exists analytics    comment = 'BI / dashboard-facing views';
