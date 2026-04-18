# Streams & Tasks

Snowflake Streams + Tasks implement near-real-time CDC without external orchestration.

| Stream | Task | Schedule | Target |
|---|---|---|---|
| `stream_gps_events_new` | `task_merge_gps_events` | every 5 min | `gps_events_typed` |
| `stream_weather_new`    | `task_merge_weather`    | every 15 min | `weather_typed` |

## Monitoring

```sql
-- Pending data
select system$stream_has_data('fleetpulse_raw.gps.stream_gps_events_new');

-- Task history
select *
from table(information_schema.task_history(
    scheduled_time_range_start=>dateadd(hour, -2, current_timestamp()),
    task_name=>'task_merge_gps_events'
))
order by scheduled_time desc;
```

## Pause / resume

```sql
alter task task_merge_gps_events suspend;
alter task task_merge_gps_events resume;
```
