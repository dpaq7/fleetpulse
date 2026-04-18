-- Fails if any delivered shipment has delivery_ts before pickup_ts.
select
    shipment_id,
    pickup_ts,
    delivery_ts
from {{ ref('stg_shipments') }}
where delivery_ts is not null
  and delivery_ts < pickup_ts
