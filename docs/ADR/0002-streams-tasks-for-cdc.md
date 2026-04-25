# 2. Streams + Tasks for sub-15-min CDC, dbt for batch

Date: 2026-04-24

## Status

Accepted

## Context

The dashboard needs near-real-time visibility on GPS pings (target freshness: 5 min) and weather observations (15 min). Shipments and warehouse events are fine on a daily cadence.

Two ways to keep marts fresh:
1. Run `dbt build` on a 5-minute cron.
2. Use Snowflake-native Streams + Tasks for the high-cadence sources, and let dbt handle the batch refresh once a day.

Option (1) is conceptually simple but has problems on a trial Snowflake account:
- Even a no-op dbt invocation pays a few seconds of warehouse spin-up plus dbt CLI overhead, every five minutes, all day.
- Incremental models with merges into clustered tables don't always finish in under five minutes; back-to-back runs would queue and wedge.
- dbt's strength is *modelling*, not change capture. Reaching for it to do CDC is paying a lot of cost for a feature it doesn't optimize for.

## Decision

Run two cadences, with a clean handoff between them:

- **Streams + Tasks (Snowflake-native)** for GPS and weather. Append-only stream on each `RAW.*` VARIANT table; a task wakes every 5 (GPS) or 15 (weather) minutes, gated by `when system$stream_has_data(...)`, and merges newly-arrived rows into a *typed* downstream table (`gps_events_typed`, `weather_observations_typed`). See [`snowflake/streams_tasks/gps_stream_and_task.sql`](../../snowflake/streams_tasks/gps_stream_and_task.sql).
- **dbt** reads the *typed* tables (not the raw VARIANTs) in [`stg_gps_events`](../../dbt/models/staging/stg_gps_events.sql) etc., and rebuilds marts on the Airflow daily DAG. Marts are still incremental + merge + clustered for cost.

The `when system$stream_has_data` predicate is the key cost mechanism: idle periods spin nothing up.

## Consequences

**Easier:**
- Sub-15-min freshness without paying dbt overhead 96 times a day.
- Cost scales with actual data volume, not wall-clock time.
- dbt models stay clean — they always read typed columns, never `record:foo::string` extraction.
- Each cadence can fail independently; a wedged dbt build doesn't stall CDC.

**Harder:**
- Two systems to operate (Tasks history in Snowflake UI; dbt logs in Airflow). Documented in [`docs/architecture.md`](../architecture.md).
- Schema changes have to land in *three* places: the typed table DDL, the task's MERGE, and the dbt staging model.
- The typed table is a duplication of state — we accept this in exchange for clean separation of concerns.
