# Resume Alignment: FleetPulse

## Target Roles

- Junior data engineer
- Analytics engineer
- BI / data analyst with engineering responsibilities
- ML/data platform associate

## Skills Demonstrated

- Synthetic event generation for logistics analytics
- Snowflake schema and ingestion design
- dbt staging, intermediate, and mart modeling
- Data quality checks with dbt tests and Great Expectations suites
- Airflow DAG structure for orchestration
- Streamlit dashboard design with demo-mode fallbacks
- CI for linting, pytest, dbt parse, and optional warehouse build
- Architecture decisions, cost analysis, and implementation retrospectives

## Evidence-Based Resume Bullets

- Built a logistics analytics platform prototype with Python simulators, Snowflake setup scripts, dbt models, Airflow DAGs, and Streamlit dashboards for fleet KPIs, route performance, warehouse utilization, and anomaly alerts.
- Modeled a dbt analytics layer with 20 committed SQL models across staging, intermediate, and mart layers, plus custom tests and Great Expectations suites for data quality validation.
- Implemented credential-free Streamlit demo mode with deterministic synthetic data and committed dashboard screenshots so reviewers can inspect the analytics experience without live Snowflake or AWS credentials.

## Interview Talking Points

- Why demo mode is important for portfolio review and how it differs from live warehouse mode.
- How the dbt model layers separate raw ingestion, business logic, and dashboard-ready marts.
- Why CI uses dbt parse publicly while credentialed dbt build is gated by repository variables and secrets.
- How data quality responsibilities are split between dbt tests and Great Expectations suites.
- What would be needed to productionize the project: live warehouse credentials, monitoring, orchestration hardening, secrets management, and cost controls.

