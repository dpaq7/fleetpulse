from __future__ import annotations

from ingest.reference_data import DRIVERS, ROUTES, VEHICLES, WAREHOUSES


def test_warehouse_ids_unique():
    ids = [w["warehouse_id"] for w in WAREHOUSES]
    assert len(ids) == len(set(ids))


def test_routes_reference_existing_warehouses():
    wh = {w["warehouse_id"] for w in WAREHOUSES}
    for r in ROUTES:
        assert r["origin_warehouse_id"] in wh
        assert r["dest_warehouse_id"] in wh


def test_vehicle_fuel_types_are_constrained():
    allowed = {"DIESEL", "ELECTRIC", "CNG", "HYBRID"}
    assert {v["fuel_type"] for v in VEHICLES} <= allowed


def test_drivers_have_unique_ids():
    ids = [d["driver_id"] for d in DRIVERS]
    assert len(ids) == len(set(ids))
