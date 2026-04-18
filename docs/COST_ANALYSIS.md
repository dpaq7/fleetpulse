# Cost Analysis

FleetPulse is designed to run at **$0** during development by stacking free tiers.

| Service                     | Tier            | Limit / Credit              | Notes                               |
| --------------------------- | --------------- | --------------------------- | ----------------------------------- |
| Snowflake                   | 30-day trial    | $400 credits                | Sufficient for 7-week build         |
| AWS S3                      | Free tier       | 5 GB + 20K GET + 2K PUT/mo  | Snowpipe ingest bucket              |
| OpenWeatherMap              | Free            | 1,000 calls/day             | Hourly polling for 10 warehouses OK |
| GitHub Actions              | Free (public)   | Unlimited minutes           | CI for dbt build + tests            |
| Streamlit Community Cloud   | Free            | 1 GB RAM, 1 app             | Public dashboard hosting            |
| Apache Airflow              | Local Docker    | N/A                         | Runs on dev machine                 |

## Post-trial plan

After the Snowflake trial expires, options include:
- Pause project and export final dbt docs + screenshots for portfolio
- Upgrade to Snowflake Standard edition (~$2/credit, X-Small WH = $2/hr)
- Migrate marts to DuckDB for local-only demo mode
