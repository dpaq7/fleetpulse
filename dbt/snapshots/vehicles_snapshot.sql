{% snapshot vehicles_snapshot %}
    {{
        config(
            target_schema='snapshots',
            unique_key='vehicle_id',
            strategy='check',
            check_cols=['make', 'model', 'year', 'fuel_type', 'capacity_kg', 'status'],
            invalidate_hard_deletes=True
        )
    }}
    select * from {{ ref('vehicles') }}
{% endsnapshot %}
