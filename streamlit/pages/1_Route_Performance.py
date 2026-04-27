"""Route performance page — per-route KPIs, wet/dry split, delay distribution."""
import plotly.express as px
import streamlit as st

from lib.data import get_route_performance

st.set_page_config(page_title="Route Performance", page_icon=":motorway:", layout="wide")
st.title("Route Performance")

df = get_route_performance().sort_values("on_time_pct", ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("On-time % by route")
    st.plotly_chart(
        px.bar(df, x="route_id", y="on_time_pct", color="ratio_vs_typical",
               color_continuous_scale="RdYlGn_r",
               labels={"on_time_pct": "On-time %", "ratio_vs_typical": "Duration vs. typical"}),
        use_container_width=True,
    )

with col2:
    st.subheader("Fuel efficiency (L / 100 km)")
    st.plotly_chart(
        px.box(df, y="l_per_100km", points="all"),
        use_container_width=True,
    )

st.subheader("Wet vs. dry duration")
melt = df.melt(id_vars=["route_id"],
               value_vars=["avg_duration_wet", "avg_duration_dry"],
               var_name="condition", value_name="duration_hrs")
st.plotly_chart(
    px.bar(melt, x="route_id", y="duration_hrs", color="condition", barmode="group"),
    use_container_width=True,
)

st.divider()
st.subheader("Raw data")
st.dataframe(df, use_container_width=True)
