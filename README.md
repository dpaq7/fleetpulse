# FleetPulse

> Real-time logistics analytics platform: Snowflake + dbt + Airflow + Streamlit

FleetPulse is a portfolio-grade data engineering project that simulates a production logistics analytics system. It ingests GPS telemetry, shipment records, weather, and warehouse IoT signals, processes them through a Snowflake-based analytics warehouse, and delivers insights via a live Streamlit dashboard.

## Architecture

```
  Sources                  Ingestion               Warehouse              Serving
  -------                  ---------               ---------              -------
  GPS Simulator  ─┐
  OpenWeather API ┼─► S3 ─► Snowpipe ─► RAW ─► dbt ─► STAGING ─► MARTS ─► Streamlit
  Shipments CSV   │                      │                                   │
  Warehouse IoT  ─┘                   Streams+Tasks                      Plotly / Map
                                      (5-min CDC)
```

See `FleetPulse_Project_Blueprint.docx` for the full design spec and `docs/architecture.md` for diagrams.

## Tech Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| Warehouse      | Snowflake (trial)                   |
| Storage        | AWS S3 (free tier)                  |
| Transformation | dbt Core (`dbt-snowflake`)          |
| Orchestration  | Apache Airflow (Docker)             |
| Ingestion      | Snowpipe + Python                   |
| Quality        | dbt tests + Great Expectations      |
| Dashboard      | Streamlit (Community Cloud)         |
| CI/CD          | GitHub Actions                      |
| Language       | Python 3.11 + SQL                   |

## Quickstart

```bash
# 1. Install dependencies
make install

# 2. Configure credentials
cp .env.example .env
# edit .env with your Snowflake + AWS + OpenWeather keys

# 3. Configure dbt profile
cp dbt/profiles.yml.example ~/.dbt/profiles.yml

# 4. Run dbt build
make build

# 5. Launch Airflow (Docker)
make airflow-up

# 6. Run the dashboard
make run-dashboard
```

## Roadmap

- **Phase 1 (Weeks 1-2):** Snowflake foundations, Snowpipe, Python loaders, weather API
- **Phase 2 (Weeks 3-4):** dbt star schema (20+ models), clustering, optimization
- **Phase 3 (Week 5):** Data quality (60+ tests), GitHub Actions, pre-commit hooks
- **Phase 4 (Week 6):** Streams + Tasks, Streamlit multi-page dashboard
- **Phase 5 (Week 7):** Documentation, ADRs, portfolio polish

## License

MIT — see [LICENSE](LICENSE).
