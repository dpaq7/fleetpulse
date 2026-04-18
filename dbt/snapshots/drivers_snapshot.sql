{% snapshot drivers_snapshot %}
    {{
        config(
            target_schema='snapshots',
            unique_key='driver_id',
            strategy='check',
            check_cols=['name', 'license_class', 'years_experience'],
            invalidate_hard_deletes=True
        )
    }}
    select * from {{ ref('drivers') }}
{% endsnapshot %}
