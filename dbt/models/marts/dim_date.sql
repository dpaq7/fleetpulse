{{ config(materialized='table', schema='marts') }}

-- Calendar dimension — uses dbt_utils.date_spine for 2022-01-01 → 2027-12-31.

with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2022-01-01' as date)",
        end_date="cast('2028-01-01' as date)"
    ) }}
),

holidays as (
    select distinct cast("date" as date) as holiday_date from {{ ref('holidays') }}
),

calendar as (
    select
        cast(date_day as date)                      as date_key,
        date_day                                    as full_date,
        year(date_day)                              as year,
        quarter(date_day)                           as quarter,
        month(date_day)                             as month,
        monthname(date_day)                         as month_name,
        day(date_day)                               as day_of_month,
        dayofweek(date_day)                         as day_of_week_num,
        dayname(date_day)                           as day_of_week,
        weekofyear(date_day)                        as week_of_year,
        case when dayofweek(date_day) in (0, 6) then true else false end as is_weekend,
        case when h.holiday_date is not null then true else false end    as is_holiday
    from spine
    left join holidays h on cast(spine.date_day as date) = h.holiday_date
)

select * from calendar
