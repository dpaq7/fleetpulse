-- Fails if any fact_shipments row has no matching current-version vehicle SK.
select
    fs.shipment_id,
    fs.vehicle_id
from {{ ref('fact_shipments') }} fs
left join {{ ref('dim_vehicle') }} v
    on fs.vehicle_sk = v.vehicle_sk
where v.vehicle_sk is null
  and fs.vehicle_id is not null
