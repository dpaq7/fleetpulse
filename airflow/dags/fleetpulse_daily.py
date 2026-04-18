"""FleetPulse daily pipeline.

Runs once a day (02:00 UTC):
    1. Generate today's synthetic shipment batch + warehouse events
    2. COPY INTO Snowflake RAW via Snowpipe-bypass (bulk load)
    3. dbt snapshot + dbt build (target=prod)
    4. dbt source freshness + dbt test

Snowpipe handles GPS + weather continuously; this DAG covers the batch path.
"""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

DEFAULT_ARGS = {
    "owner": "fleetpulse",
    "retries": 2,
    "retry_delay": pendulum.duration(minutes=5),
}

DBT_DIR = "/opt/airflow/dbt"

with DAG(
    dag_id="fleetpulse_daily",
    description="End-of-day FleetPulse batch + dbt build",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 4, 1, tz="UTC"),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["fleetpulse", "daily", "dbt"],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id="start")

    generate_shipments = BashOperator(
        task_id="generate_shipments",
        bash_command=(
            "python -m ingest.shipment_generator "
            "--rows 5000 "
            "--start {{ ds }} --end {{ ds }}"
        ),
        env={"FLEETPULSE_WRITER": "s3"},
        append_env=True,
    )

    generate_warehouse_events = BashOperator(
        task_id="generate_warehouse_events",
        bash_command="python -m ingest.warehouse_event_simulator --shipments 5000",
        env={"FLEETPULSE_WRITER": "s3"},
        append_env=True,
    )

    # ----- dbt -----
    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"cd {DBT_DIR} && dbt snapshot --target prod",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_DIR} && dbt build --target prod --select state:modified+ --defer --state ./target-prod",
    )

    dbt_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"cd {DBT_DIR} && dbt source freshness --target prod",
        trigger_rule="all_done",
    )

    done = EmptyOperator(task_id="done", trigger_rule="all_done")

    start >> [generate_shipments, generate_warehouse_events] >> dbt_snapshot >> dbt_build >> dbt_freshness >> done
