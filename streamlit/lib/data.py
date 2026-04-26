"""Data access layer for the Streamlit dashboard.

If Snowflake credentials are present (via env vars or Streamlit secrets),
queries run against the live `analytics` schema. Otherwise, a deterministic
in-memory mock dataset is returned — useful for development, demos, and
Streamlit Community Cloud previews.
"""
from __future__ import annotations

import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit only puts the script's directory on sys.path. The demo-mode mocks
# read reference data (ROUTES, WAREHOUSES, VEHICLES) from `ingest.reference_data`
# which lives at the project root, so we add it here.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Live / demo detection
# ---------------------------------------------------------------------------


def _secret(key: str) -> str | None:
    """Fetch a credential from env var first, then st.secrets (tolerating a
    missing secrets.toml — accessing st.secrets without one raises)."""
    val = os.environ.get(key)
    if val:
        return val
    try:
        return st.secrets.get(key)  # type: ignore[no-any-return]
    except Exception:
        return None


_REQUIRED_KEYS = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")
_ALL_KEYS = _REQUIRED_KEYS + (
    "SNOWFLAKE_ROLE", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE",
)


def _creds() -> dict | None:
    if not all(_secret(k) for k in _REQUIRED_KEYS):
        return None
    return {k: _secret(k) for k in _ALL_KEYS}


def is_live() -> bool:
    return _creds() is not None


@st.cache_resource
def _conn():
    import snowflake.connector  # imported lazily

    c = _creds()
    return snowflake.connector.connect(
        account=c["SNOWFLAKE_ACCOUNT"],
        user=c["SNOWFLAKE_USER"],
        password=c["SNOWFLAKE_PASSWORD"],
        role=c.get("SNOWFLAKE_ROLE") or "FLEETPULSE_DEV_ROLE",
        warehouse=c.get("SNOWFLAKE_WAREHOUSE") or "ANALYTICS_WH",
        database=c.get("SNOWFLAKE_DATABASE") or "FLEETPULSE_MARTS",
        schema="ANALYTICS",
    )


@st.cache_data(ttl=300)
def _query(sql: str) -> pd.DataFrame:
    with _conn().cursor() as cur:
        cur.execute(sql)
        return cur.fetch_pandas_all()


# ---------------------------------------------------------------------------
# Demo mock data (seeded for determinism across page reloads)
# ---------------------------------------------------------------------------


def _seeded() -> random.Random:
    r = random.Random()
    r.seed(42)
    return r


def _mock_fleet_kpis(days: int) -> pd.DataFrame:
    r = _seeded()
    today = date.today()
    rows = []
    for i in range(days):
        d = today - timedelta(days=i)
        total = r.randint(80, 160)
        on_time_pct = round(r.uniform(78, 96), 1)
        rows.append({
            "activity_date": d,
            "total_shipments": total,
            "delivered_count": int(total * r.uniform(0.85, 0.98)),
            "on_time_count": int(total * on_time_pct / 100),
            "on_time_pct": on_time_pct,
            "avg_delay_min": round(r.uniform(2, 35), 1),
            "avg_duration_hrs": round(r.uniform(2.8, 6.5), 2),
            "total_distance_km": int(total * r.uniform(250, 520)),
            "total_fuel_l": int(total * r.uniform(80, 200)),
            "active_vehicles": r.randint(8, 15),
        })
    return pd.DataFrame(rows).sort_values("activity_date")


def _mock_route_performance() -> pd.DataFrame:
    from ingest.reference_data import ROUTES  # local import to avoid hard coupling

    r = _seeded()
    rows = []
    for route in ROUTES:
        baseline = route["typical_duration_hrs"]
        dur = round(r.uniform(baseline * 0.95, baseline * 1.25), 2)
        rows.append({
            "route_id": route["route_id"],
            "origin_warehouse_id": route["origin_warehouse_id"],
            "dest_warehouse_id": route["dest_warehouse_id"],
            "shipment_count": r.randint(40, 220),
            "avg_duration_hrs": dur,
            "baseline_hrs": baseline,
            "ratio_vs_typical": round(dur / baseline, 3),
            "avg_delay_min": round(r.uniform(1, 45), 1),
            "on_time_pct": round(r.uniform(65, 95), 2),
            "l_per_100km": round(r.uniform(28, 44), 2),
            "avg_duration_wet": round(dur * 1.15, 2),
            "avg_duration_dry": round(dur * 0.97, 2),
        })
    return pd.DataFrame(rows)


def _mock_warehouse_utilization() -> pd.DataFrame:
    from ingest.reference_data import WAREHOUSES

    r = _seeded()
    rows = []
    today = date.today()
    for days_ago in range(30):
        d = today - timedelta(days=days_ago)
        for w in WAREHOUSES:
            docks_in_use = r.randint(max(2, w["total_docks"] // 3), w["total_docks"])
            rows.append({
                "event_date": d,
                "warehouse_id": w["warehouse_id"],
                "warehouse_name": w["name"],
                "city": w["city"],
                "total_docks": w["total_docks"],
                "docks_in_use": docks_in_use,
                "shipments_processed": r.randint(8, 45),
                "pallets_moved": r.randint(60, 700),
                "avg_dwell_min": round(r.uniform(22, 85), 1),
                "dock_utilization_pct": round(100 * docks_in_use / w["total_docks"], 2),
            })
    return pd.DataFrame(rows)


def _mock_anomalies() -> pd.DataFrame:
    from ingest.reference_data import VEHICLES

    r = _seeded()
    types = ["OVERSPEED", "HARSH_ACCELERATION", "LOW_FUEL"]
    rows = []
    for _ in range(25):
        v = r.choice(VEHICLES)
        rows.append({
            "event_ts": pd.Timestamp.utcnow() - pd.Timedelta(hours=r.randint(0, 168)),
            "vehicle_id": v["vehicle_id"],
            "anomaly_type": r.choice(types),
            "speed_kmh": round(r.uniform(30, 155), 1),
            "speed_delta_kmh": round(r.uniform(-45, 45), 1),
            "latitude": round(r.uniform(42.5, 46.8), 4),
            "longitude": round(r.uniform(-83.0, -71.0), 4),
        })
    return pd.DataFrame(rows).sort_values("event_ts", ascending=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_fleet_kpis(days: int = 30) -> pd.DataFrame:
    if is_live():
        return _query(f"""
            select *
            from fleetpulse_marts.analytics.analytics_fleet_kpis
            where activity_date >= dateadd(day, -{days}, current_date())
            order by activity_date
        """).rename(columns=str.lower)
    return _mock_fleet_kpis(days)


def get_route_performance() -> pd.DataFrame:
    if is_live():
        return _query(
            "select * from fleetpulse_marts.analytics.analytics_route_performance"
        ).rename(columns=str.lower)
    return _mock_route_performance()


def get_warehouse_utilization() -> pd.DataFrame:
    if is_live():
        return _query(
            "select * from fleetpulse_marts.analytics.analytics_warehouse_utilization"
        ).rename(columns=str.lower)
    return _mock_warehouse_utilization()


def get_anomalies() -> pd.DataFrame:
    if is_live():
        return _query(
            "select * from fleetpulse_marts.analytics.analytics_gps_speed_anomalies "
            "order by event_ts desc limit 500"
        ).rename(columns=str.lower)
    return _mock_anomalies()
