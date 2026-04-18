-- Fails if any GPS ping has coordinates outside Canadian road-network bounds
-- (generous buffer; tighten later if simulator is constrained).
select
    ping_id,
    latitude,
    longitude
from {{ ref('stg_gps_events') }}
where latitude  not between 40 and 75
   or longitude not between -142 and -50
