"""Pytest fixtures shared across tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from ingest.utils import LocalWriter


@pytest.fixture
def tmp_writer(tmp_path: Path) -> LocalWriter:
    return LocalWriter(root=tmp_path / "raw")
