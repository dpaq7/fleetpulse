"""Weather polling DAG.

Hourly OpenWeatherMap polling for each warehouse city.
Free tier: 1,000 calls/day — 8 cities × 24 hours = 192 calls/day. Safe.
"""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="weather_poller",
    description="Hourly OpenWeatherMap current-weather pull",
    schedule="0 * * * *",
    start_date=pendulum.datetime(2026, 4, 1, tz="UTC"),
    catchup=False,
    tags=["fleetpulse", "streaming"],
    max_active_runs=1,
) as dag:

    poll = BashOperator(
        task_id="poll_weather",
        bash_command="python -m ingest.weather_loader --qps 1.0",
        env={"FLEETPULSE_WRITER": "s3"},
        append_env=True,
    )
