# FleetPulse dbt project

`dbt-snowflake` project that builds the FleetPulse analytics warehouse:

```
staging (views)  →  intermediate (ephemeral)  →  marts (incremental + clustered)
                                               ↘  snapshots (SCD2)  → dims
                                                marts → analytics (views) → Streamlit
```

See [../docs/architecture.md](../docs/architecture.md) for diagrams and [../docs/ADR/](../docs/ADR/) for the design decisions.

## Layout

| Path | What lives here |
| --- | --- |
| `models/staging/` | One view per raw source, typed + de-duped via `QUALIFY` |
| `models/intermediate/` | Ephemeral CTEs — `int_gps_enriched`, `int_shipment_weather`, `int_route_performance`, `int_warehouse_dwell` |
| `models/marts/` | Facts (incremental + merge + clustered) and conformed dims |
| `models/marts/` (analytics_*) | Dashboard-facing views consumed by Streamlit |
| `snapshots/` | SCD2 history for `drivers`, `vehicles`, `warehouses` (check strategy) |
| `seeds/` | Static reference CSVs: `drivers`, `vehicles`, `warehouses`, `routes`, `holidays` |
| `tests/` | Custom data tests: coordinate bounds, delivery-after-pickup, FK integrity |
| `macros/` | `cents_to_dollars`, `delay_bucket`, `generate_schema_name` |

## Running

Live (requires Snowflake + env vars from `.env`):

```bash
cp profiles.yml.example ~/.dbt/profiles.yml   # one-time
dbt deps
dbt seed
dbt snapshot
dbt build          # run + test all models
dbt source freshness
```

Parse-only (no warehouse needed — validates the manifest compiles):

```bash
dbt parse --profiles-dir . --profile-dir-overrides profiles.yml.demo
# or:
DBT_PROFILES_DIR=. dbt parse --profile fleetpulse  # if profiles.yml.demo symlinked to profiles.yml
```

Useful during development or in CI when Snowflake credentials aren't available.

## Documentation catalog

`dbt docs generate` builds a browseable catalog of the project (model lineage, column descriptions, test coverage). It requires a **live warehouse connection** to introspect columns — there is no offline mode. Once credentials are configured:

```bash
dbt docs generate --static   # writes static_index.html
dbt docs serve               # or serve locally on :8080
```

Host the generated `static_index.html` on GitHub Pages or an S3 static site to publish the catalog.

## Conventions

- Snake-case everything (tables, columns, model names).
- Staging models prefixed `stg_`, intermediates `int_`, marts use their business name (`fact_`, `dim_`), analytics views prefixed `analytics_`.
- Every mart references dims via `{dim}.is_current` to pick the active SCD2 row ([ADR-0002](../docs/ADR/)).
- Intermediate models are ephemeral by default — they inline as CTEs, no Snowflake objects ([ADR-0003](../docs/ADR/0003-ephemeral-intermediate-models.md)).
- Incremental facts use `merge` strategy with a 1-day overlap window (`dateadd(day, -1, max(...))`) to absorb late-arriving rows without full rebuilds.
