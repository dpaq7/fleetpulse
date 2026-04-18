"""Reference data for the simulators.

These constants are the source of truth for what later becomes
`dim_vehicle`, `dim_warehouse`, `dim_route`, and `dim_driver`.
They also back the dbt seeds in `dbt/seeds/`.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Warehouses (cities anchor the fleet)
# ---------------------------------------------------------------------------
WAREHOUSES: list[dict] = [
    {"warehouse_id": "W-TOR-01", "name": "Toronto DC",    "city": "Toronto",    "province": "ON", "lat": 43.6532, "lng": -79.3832, "total_docks": 24, "capacity_pallets": 2400},
    {"warehouse_id": "W-MIS-01", "name": "Mississauga FC", "city": "Mississauga", "province": "ON", "lat": 43.5890, "lng": -79.6441, "total_docks": 32, "capacity_pallets": 3200},
    {"warehouse_id": "W-MTL-01", "name": "Montreal DC",   "city": "Montreal",   "province": "QC", "lat": 45.5019, "lng": -73.5674, "total_docks": 20, "capacity_pallets": 2000},
    {"warehouse_id": "W-OTT-01", "name": "Ottawa DC",     "city": "Ottawa",     "province": "ON", "lat": 45.4215, "lng": -75.6972, "total_docks": 12, "capacity_pallets": 1200},
    {"warehouse_id": "W-HAM-01", "name": "Hamilton XDock","city": "Hamilton",   "province": "ON", "lat": 43.2557, "lng": -79.8711, "total_docks": 16, "capacity_pallets": 1600},
    {"warehouse_id": "W-LON-01", "name": "London DC",     "city": "London",     "province": "ON", "lat": 42.9849, "lng": -81.2453, "total_docks": 14, "capacity_pallets": 1400},
    {"warehouse_id": "W-WIN-01", "name": "Windsor XDock", "city": "Windsor",    "province": "ON", "lat": 42.3149, "lng": -83.0364, "total_docks": 10, "capacity_pallets": 1000},
    {"warehouse_id": "W-QUE-01", "name": "Quebec City DC","city": "Quebec City","province": "QC", "lat": 46.8139, "lng": -71.2080, "total_docks": 12, "capacity_pallets": 1200},
]

# ---------------------------------------------------------------------------
# Routes (selected origin → destination pairs)
# ---------------------------------------------------------------------------
ROUTES: list[dict] = [
    {"route_id": "R-001", "origin_warehouse_id": "W-TOR-01", "dest_warehouse_id": "W-MTL-01", "distance_km": 541, "typical_duration_hrs": 6.0},
    {"route_id": "R-002", "origin_warehouse_id": "W-MIS-01", "dest_warehouse_id": "W-OTT-01", "distance_km": 448, "typical_duration_hrs": 5.0},
    {"route_id": "R-003", "origin_warehouse_id": "W-TOR-01", "dest_warehouse_id": "W-HAM-01", "distance_km":  68, "typical_duration_hrs": 1.0},
    {"route_id": "R-004", "origin_warehouse_id": "W-HAM-01", "dest_warehouse_id": "W-LON-01", "distance_km": 131, "typical_duration_hrs": 1.75},
    {"route_id": "R-005", "origin_warehouse_id": "W-LON-01", "dest_warehouse_id": "W-WIN-01", "distance_km": 193, "typical_duration_hrs": 2.25},
    {"route_id": "R-006", "origin_warehouse_id": "W-MTL-01", "dest_warehouse_id": "W-QUE-01", "distance_km": 253, "typical_duration_hrs": 2.75},
    {"route_id": "R-007", "origin_warehouse_id": "W-MIS-01", "dest_warehouse_id": "W-MTL-01", "distance_km": 580, "typical_duration_hrs": 6.5},
    {"route_id": "R-008", "origin_warehouse_id": "W-OTT-01", "dest_warehouse_id": "W-TOR-01", "distance_km": 450, "typical_duration_hrs": 5.0},
]

# ---------------------------------------------------------------------------
# Fleet
# ---------------------------------------------------------------------------
VEHICLES: list[dict] = [
    {"vehicle_id": f"V-{i:04d}", "make": make, "model": model, "year": year, "fuel_type": fuel, "capacity_kg": cap, "status": "ACTIVE"}
    for i, (make, model, year, fuel, cap) in enumerate(
        [
            ("Freightliner", "Cascadia",   2023, "DIESEL", 16000),
            ("Volvo",         "VNL 760",   2022, "DIESEL", 17500),
            ("Kenworth",      "T680",      2024, "DIESEL", 16500),
            ("Peterbilt",     "579",       2022, "DIESEL", 17000),
            ("Tesla",         "Semi",      2024, "ELECTRIC", 18000),
            ("International", "LT Series", 2021, "DIESEL", 15500),
            ("Mack",          "Anthem",    2023, "DIESEL", 16000),
            ("Freightliner",  "eCascadia", 2024, "ELECTRIC", 17500),
            ("Volvo",         "FH16",      2023, "DIESEL", 17800),
            ("Kenworth",      "T880",      2022, "DIESEL", 16200),
            ("Peterbilt",     "389",       2021, "DIESEL", 16800),
            ("Tesla",         "Semi",      2024, "ELECTRIC", 18000),
            ("Mack",          "Pinnacle",  2023, "DIESEL", 16000),
            ("International", "RH Series", 2022, "DIESEL", 15500),
            ("Freightliner",  "Cascadia",  2023, "DIESEL", 16000),
        ],
        start=1,
    )
]

# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------
_DRIVER_NAMES = [
    "Ava Singh", "Marcus Chen", "Priya Patel", "Jean Tremblay", "Liam O'Connor",
    "Sofia Rossi", "David Nguyen", "Fatima Al-Sayed", "Ethan Brown", "Isabella Kim",
    "Noah Williams", "Maya Johnson", "Arjun Kapoor", "Chloe Dubois", "Lucas Martin",
    "Zoe Taylor", "Ryan Thompson", "Amelia Clark", "Oliver Wright", "Hannah Lee",
]

DRIVERS: list[dict] = [
    {
        "driver_id": f"D-{i:04d}",
        "name": name,
        "license_class": "AZ",
        "hire_date": f"20{20 - (i % 8):02d}-{(i % 12) + 1:02d}-15",
        "years_experience": 3 + (i % 15),
    }
    for i, name in enumerate(_DRIVER_NAMES, start=1)
]
