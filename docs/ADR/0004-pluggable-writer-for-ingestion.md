# 4. Pluggable LocalWriter / S3Writer for ingestion

Date: 2026-04-24

## Status

Accepted

## Context

Four ingest modules produce data: `gps_simulator`, `weather_loader`, `shipment_generator`, `warehouse_event_simulator`. In production they all write to S3 so Snowpipe / `COPY INTO` can pick the files up. In dev, we want to:

- Run the generators on a laptop without an AWS account.
- Run unit tests without mocking boto3 in every test.
- Generate sample data into a local directory for the demo dashboard.

The naive approach — write directly to S3 with `boto3.client('s3').put_object(...)` in each module — would force every dev to have AWS credentials before they could even run the simulators, and would make tests entangled with mocking infrastructure they don't care about.

## Decision

Define a minimal `Writer` protocol in [`ingest/utils.py`](../../ingest/utils.py):

```python
class Writer(Protocol):
    def write_json_gz(self, key: str, records: Iterable[dict]) -> str: ...
    def write_csv_gz(self, key: str, header: list[str], rows: Iterable[list]) -> str: ...
```

Two implementations:
- `LocalWriter(root: Path)` — writes gzipped files under a local directory, mirroring the S3 key layout (`dt=YYYY-MM-DD/hh=HH/...`) so files generated locally can later be uploaded to S3 verbatim.
- `S3Writer(bucket: str)` — uses boto3, imported lazily so the module doesn't blow up if boto3 isn't installed.

A factory `make_writer()` reads `FLEETPULSE_WRITER` from env: `s3` selects `S3Writer`, anything else (including unset) selects `LocalWriter` with `data/raw/` as the root.

Every generator constructs its writer via `make_writer()` and uses only the protocol methods.

## Consequences

**Easier:**
- New devs run `python -m ingest.gps_simulator` immediately after `pip install` — no AWS setup.
- Unit tests in [`tests/`](../../tests/) construct a `LocalWriter(root=tmp_path)` and assert against real files. No mocks, no fixtures for boto3 stubbing.
- Production deploys flip a single env var.
- The same partitioned key layout is used in both writers, so `aws s3 cp --recursive data/raw/ s3://fleetpulse-raw/` is a valid one-shot bulk-load if needed.

**Harder:**
- The protocol locks the file format vocabulary at JSON-gz and CSV-gz. Adding a new format (e.g. Parquet) means extending the protocol and both implementations, not just one.
- Two code paths to keep in sync. We accept this — the surface area is tiny (two methods × two implementations) and tested.
- `S3Writer` failures (auth, network) only surface when actually used in production; demo runs never exercise it. Mitigated by the CI's optional `dbt-build` step which does hit live infrastructure when `ENABLE_DBT_CI` is set.
