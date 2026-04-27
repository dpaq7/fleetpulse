# 3. Ephemeral intermediate models

Date: 2026-04-24

## Status

Accepted

## Context

The transformation layer has four intermediate models that exist purely to compose the marts:

- `int_gps_enriched` — adds lag-based prev-ping columns to staged GPS events
- `int_shipment_weather` — joins shipments to the nearest weather observation
- `int_route_performance` — combines shipments + dimensional fields into route metrics
- `int_warehouse_dwell` — aggregates dock events into per-shipment dwell time

None of these are queried by the dashboard. They exist so the marts (`fact_shipments`, `fact_gps_pings`, `fact_warehouse_events`) stay readable.

Default dbt materialization is `view`. That means each `int_*` would land in Snowflake as a view, consuming an object slot and showing up in any schema browse. Materializing as `table` would be even worse — physical storage for a layer the dashboard never reads.

## Decision

Configure the `intermediate` directory as `materialized: ephemeral` in [`dbt/dbt_project.yml`](../../dbt/dbt_project.yml):

```yaml
models:
  fleetpulse:
    intermediate:
      +materialized: ephemeral
```

Ephemeral models are inlined as CTEs into every model that `ref()`s them. There is no Snowflake object — the `int_*` SQL becomes a CTE in the compiled mart query.

## Consequences

**Easier:**
- The marts schema only contains things downstream consumers actually read.
- Refactoring the intermediate logic is purely a dbt-internal change; nothing depends on a Snowflake object name.
- Catalog browsers (e.g. Snowsight) show only meaningful objects.

**Harder:**
- `select * from fleetpulse_dev.int_gps_enriched` doesn't work — the table doesn't exist. To debug an intermediate, run `dbt compile` and read the inlined CTE in `target/compiled/...`.
- Ephemeral models can't be tested with dbt schema tests directly (tests run against materialized objects). Tests have to run against the downstream marts that consume them. In practice this is fine — the invariants we care about are properties of the marts.
- If two marts both reference the same ephemeral model, the CTE is duplicated in each compiled query. The query optimizer handles this fine in Snowflake, but it's worth knowing if a future model ever joins to the same `int_*` more than once.
