"""Anomaly alerts — recent overspeed, harsh-accel, low-fuel events."""
import plotly.express as px
import streamlit as st

from lib.data import get_anomalies

st.set_page_config(page_title="Anomaly Alerts", page_icon=":rotating_light:", layout="wide")
st.title("Anomaly Alerts")

df = get_anomalies()

col1, col2, col3 = st.columns(3)
col1.metric("Overspeed (7d)",       int((df["anomaly_type"] == "OVERSPEED").sum()))
col2.metric("Harsh accel (7d)",     int((df["anomaly_type"] == "HARSH_ACCELERATION").sum()))
col3.metric("Low fuel alerts (7d)", int((df["anomaly_type"] == "LOW_FUEL").sum()))

st.subheader("Anomaly timeline")
st.plotly_chart(
    px.scatter(df, x="event_ts", y="speed_kmh", color="anomaly_type", hover_data=["vehicle_id"]),
    use_container_width=True,
)

st.subheader("Recent events")
st.dataframe(df.head(100), use_container_width=True)
