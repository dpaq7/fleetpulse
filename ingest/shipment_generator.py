"""Historical shipment generator.

Produces ~500K synthetic shipment rows (shipment_id, vehicle_id, route_id,
pickup_ts, delivery_ts, weight_kg, status) as CSV for bulk COPY INTO
RAW.SHIPMENTS.

TODO (Phase 1):
    - Realistic delay distributions correlated with weather + day-of-week
    - Referential integrity against dim_vehicle / dim_route / dim_driver
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError("shipment_generator: implement in Phase 1")


if __name__ == "__main__":
    main()
