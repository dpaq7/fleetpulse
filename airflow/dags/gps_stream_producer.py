"""Streaming GPS producer DAG.

Generates 15 minutes of GPS pings every 15 minutes and uploads to S3,
where Snowpipe auto-ingests them. Simulates the continuous telemetry feed.
"""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="gps_stream_producer",
    description="Every-15-minute synthetic GPS ping generator",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2026, 4, 1, tz="UTC"),
    catchup=False,
    tags=["fleetpulse", "streaming"],
    max_active_runs=1,
) as dag:

    produce = BashOperator(
        task_id="produce_gps_batch",
        bash_command=(
            "python -m ingest.gps_simulator "
            "--vehicles 15 --duration-min 15 --ping-sec 5"
        ),
        env={"FLEETPULSE_WRITER": "s3"},
        append_env=True,
    )
