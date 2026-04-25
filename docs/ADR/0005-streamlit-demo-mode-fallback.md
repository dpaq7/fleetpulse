# 5. Demo-mode fallback in the Streamlit dashboard

Date: 2026-04-24

## Status

Accepted

## Context

The Streamlit dashboard is the public face of the project. Reviewers — recruiters, hiring managers, peer engineers — should be able to clone the repo and see something working in under a minute, without provisioning Snowflake or copying secrets.

If the dashboard fails closed when secrets are missing (the default Streamlit behaviour), the reader's first impression is a stack trace from `st.secrets`, or a connection-refused error against Snowflake. That's the wrong message for a portfolio piece.

A separate concern: Streamlit Community Cloud previews don't always have Snowflake credentials wired up at deploy time. The app needs to come up regardless.

## Decision

Implement a *demo-mode fallback* in [`streamlit/lib/data.py`](../../streamlit/lib/data.py):

1. **Detect credentials** with `is_live()`: returns `True` only if all required `SNOWFLAKE_*` keys are present (via env var or `st.secrets`).
2. **Gate every public accessor** (`get_fleet_kpis`, `get_route_performance`, `get_warehouse_utilization`, `get_anomalies`) on `is_live()`. Live → real SQL against the `analytics` schema. Demo → seeded synthetic data drawn from `random.Random(42)`.
3. **Tolerate missing `secrets.toml`** (fixed in commit `135efe6`): wrap `st.secrets.get(...)` in try/except, since accessing `st.secrets` without a `.streamlit/secrets.toml` raises `StreamlitSecretNotFoundError`.
4. **Surface the mode to the user**: [`streamlit/app.py`](../../streamlit/app.py) shows a yellow "Running in demo mode" banner when `is_live()` is false, so a reviewer is never confused about what they're looking at.

Synthetic data is built from the same reference dimensions ([`ingest/reference_data.py`](../../ingest/reference_data.py): `ROUTES`, `WAREHOUSES`, `VEHICLES`) used by the simulators. So the dashboard structure, IDs, and counts match what a live load would produce — only the metric values are synthesised.

## Consequences

**Easier:**
- `make run-dashboard` works on a fresh clone with zero configuration.
- Streamlit Community Cloud deploys never break on missing secrets.
- Reviewers see a polished dashboard with consistent numbers (seeded `random` ensures determinism across reloads).
- The same code paths run in demo and live; no separate `demo_app.py` to drift.

**Harder:**
- Two query implementations per metric to keep in sync. If a SQL query changes shape, the mock has to match.
- A reviewer could mistake demo numbers for real ones. Mitigated by the visible "demo mode" banner.
- The mock data lives in code, not a fixture file. If a generator were ever pointed at the mock dataset for further pipeline development, it would need extracting. We accept this — the scope is dashboard previewing, not pipeline replay.
