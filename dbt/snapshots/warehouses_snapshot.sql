{% snapshot warehouses_snapshot %}
    {{
        config(
            target_schema='snapshots',
            unique_key='warehouse_id',
            strategy='check',
            check_cols=['name', 'city', 'province', 'total_docks', 'capacity_pallets'],
            invalidate_hard_deletes=True
        )
    }}
    select * from {{ ref('warehouses') }}
{% endsnapshot %}
