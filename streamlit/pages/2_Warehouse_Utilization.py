"""Warehouse utilization — dock usage and dwell time by warehouse."""
import plotly.express as px
import streamlit as st

from lib.data import get_warehouse_utilization

st.set_page_config(page_title="Warehouse Utilization", page_icon=":package:", layout="wide")
st.title("Warehouse Utilization")

df = get_warehouse_utilization()
latest = df.sort_values("event_date").groupby("warehouse_id").tail(1)

col1, col2, col3 = st.columns(3)
col1.metric("Warehouses", df["warehouse_id"].nunique())
col2.metric("Avg dock utilization (latest)", f"{latest['dock_utilization_pct'].mean():.1f}%")
col3.metric("Avg dwell (min, latest)", f"{latest['avg_dwell_min'].mean():.1f}")

st.divider()

st.subheader("Dock utilization heatmap (30d)")
pivot = df.pivot_table(
    index="warehouse_name", columns="event_date",
    values="dock_utilization_pct", aggfunc="mean",
)
st.plotly_chart(
    px.imshow(pivot, aspect="auto", color_continuous_scale="Blues",
              labels={"color": "Dock util %"}),
    use_container_width=True,
)

st.subheader("Avg dwell per warehouse (latest day)")
st.plotly_chart(
    px.bar(latest.sort_values("avg_dwell_min", ascending=False),
           x="warehouse_name", y="avg_dwell_min", color="city"),
    use_container_width=True,
)

st.subheader("Pallets moved — rolling 30d")
st.plotly_chart(
    px.line(df, x="event_date", y="pallets_moved", color="warehouse_name"),
    use_container_width=True,
)
