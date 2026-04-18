"""Shared utilities for FleetPulse ingestion modules."""
from __future__ import annotations

import gzip
import io
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

log = logging.getLogger("fleetpulse.ingest")


def configure_logging(level: str = "INFO") -> None:
    """Standardize log format across ingestion scripts."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


class Writer(Protocol):
    """Abstract destination for produced records."""

    def write_json_gz(self, key: str, records: Iterable[dict]) -> str: ...
    def write_csv_gz(self, key: str, header: list[str], rows: Iterable[list[Any]]) -> str: ...


@dataclass
class LocalWriter:
    """Writes to a local directory. Mirrors S3 key layout for easy migration."""

    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        p = self.root / key
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write_json_gz(self, key: str, records: Iterable[dict]) -> str:
        path = self._path(key)
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            fh.write("[")
            first = True
            for rec in records:
                if not first:
                    fh.write(",")
                fh.write(json.dumps(rec, separators=(",", ":")))
                first = False
            fh.write("]")
        log.info("wrote %s", path)
        return str(path)

    def write_csv_gz(self, key: str, header: list[str], rows: Iterable[list[Any]]) -> str:
        import csv

        path = self._path(key)
        with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            count = 0
            for row in rows:
                w.writerow(row)
                count += 1
        log.info("wrote %s (%d rows)", path, count)
        return str(path)


@dataclass
class S3Writer:
    """Writes to S3. Boto3 is imported lazily so the module works without AWS."""

    bucket: str
    region: str | None = None

    def __post_init__(self) -> None:
        import boto3  # noqa: F401 — lazy import deferred until actually needed

        self._client = __import__("boto3").client("s3", region_name=self.region)

    def _put(self, key: str, body: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=self.bucket, Key=key, Body=body, ContentType=content_type
        )
        uri = f"s3://{self.bucket}/{key}"
        log.info("uploaded %s (%d bytes)", uri, len(body))
        return uri

    def write_json_gz(self, key: str, records: Iterable[dict]) -> str:
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(b"[")
            first = True
            for rec in records:
                if not first:
                    gz.write(b",")
                gz.write(json.dumps(rec, separators=(",", ":")).encode())
                first = False
            gz.write(b"]")
        return self._put(key, buf.getvalue(), "application/gzip")

    def write_csv_gz(self, key: str, header: list[str], rows: Iterable[list[Any]]) -> str:
        import csv

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            text_wrapper = io.TextIOWrapper(gz, encoding="utf-8", newline="")
            w = csv.writer(text_wrapper)
            w.writerow(header)
            for row in rows:
                w.writerow(row)
            text_wrapper.flush()
        return self._put(key, buf.getvalue(), "application/gzip")


def make_writer(target: str | None = None) -> Writer:
    """Select writer from env: `S3_BUCKET` uses S3, otherwise local `./data/raw/`."""
    target = target or os.environ.get("FLEETPULSE_WRITER", "local")
    if target == "s3":
        bucket = os.environ["AWS_S3_BUCKET"]
        region = os.environ.get("AWS_REGION", "us-east-1")
        return S3Writer(bucket=bucket, region=region)
    root = Path(os.environ.get("FLEETPULSE_LOCAL_ROOT", "data/raw"))
    return LocalWriter(root=root)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def partition_key(ts: datetime) -> str:
    """S3 key prefix: `dt=YYYY-MM-DD/hh=HH/`."""
    return ts.astimezone(timezone.utc).strftime("dt=%Y-%m-%d/hh=%H")


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points in kilometers."""
    import math

    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
