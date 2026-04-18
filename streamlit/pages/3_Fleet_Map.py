"""Fleet map — live(-ish) vehicle positions. Uses the anomalies feed as a
stand-in for recent pings so there's something to render in demo mode.
"""
import pydeck as pdk
import streamlit as st

from lib.data import get_anomalies

st.set_page_config(page_title="Fleet Map", page_icon=":world_map:", layout="wide")
st.title("Fleet Map")

df = get_anomalies()

if df.empty:
    st.info("No recent telemetry.")
    st.stop()

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=float(df["latitude"].mean()),
        longitude=float(df["longitude"].mean()),
        zoom=5,
        pitch=35,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_color="[200, 30, 0, 160]",
            get_radius=8000,
            pickable=True,
        ),
    ],
    tooltip={"text": "{vehicle_id}\n{anomaly_type}\n{speed_kmh} km/h"},
))

st.dataframe(df, use_container_width=True)
