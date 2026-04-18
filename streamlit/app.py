"""FleetPulse dashboard — landing page.

The dashboard connects to Snowflake if credentials are available, otherwise
falls back to an in-memory mock dataset so the app runs end-to-end offline.
"""
from __future__ import annotations

import streamlit as st

from lib.data import get_fleet_kpis, is_live

st.set_page_config(page_title="FleetPulse", page_icon=":truck:", layout="wide")

st.title("FleetPulse")
st.caption("Real-time logistics analytics — Snowflake + dbt + Airflow + Streamlit")

if not is_live():
    st.warning(
        "Running in **demo mode** — no Snowflake credentials detected. "
        "Set SNOWFLAKE_* env vars (or Streamlit secrets) to connect live."
    )

kpis = get_fleet_kpis(days=30)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Shipments (30d)", f"{int(kpis['total_shipments'].sum()):,}")
col2.metric("On-time %", f"{kpis['on_time_pct'].mean():.1f}%")
col3.metric("Avg delay (min)", f"{kpis['avg_delay_min'].mean():.1f}")
col4.metric("Distance driven (km)", f"{int(kpis['total_distance_km'].sum()):,}")

st.divider()
st.subheader("Daily shipment volume")
st.bar_chart(kpis.set_index("activity_date")["total_shipments"])

st.subheader("On-time % trend")
st.line_chart(kpis.set_index("activity_date")["on_time_pct"])

st.divider()
st.caption(
    "Explore route performance, warehouse utilization, and anomaly alerts "
    "via the left-hand navigation →"
)
