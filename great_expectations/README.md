# Great Expectations suites

These suites run on top of the dbt marts as a second line of defense against
schema drift and distribution shifts.

| Suite | Target | Scope |
|---|---|---|
| `fact_shipments.json` | `fleetpulse_marts.marts.fact_shipments` | row count, PK uniqueness, status enum, delay distribution |
| `fact_gps_pings.json` | `fleetpulse_marts.marts.fact_gps_pings` | coordinate bounds, speed distribution, no NULL timestamps |
| `analytics_fleet_kpis.json` | `fleetpulse_marts.analytics.analytics_fleet_kpis` | on-time % in `[0, 100]`, no future dates |

## Running

```bash
# one-time setup (creates ./great_expectations/ skeleton)
great_expectations init

# then run a checkpoint:
great_expectations checkpoint run fleetpulse_marts
```

In CI, we'll run suites via `pytest --gx-integration` after `dbt build` succeeds.
