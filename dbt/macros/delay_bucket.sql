{# Reusable delay-bucket expression. Accepts a minutes column. #}
{% macro delay_bucket(minutes_col) -%}
    case
        when {{ minutes_col }} is null       then 'UNKNOWN'
        when {{ minutes_col }} <= 5          then 'ON_TIME'
        when {{ minutes_col }} <= 30         then 'SLIGHTLY_LATE'
        when {{ minutes_col }} <= 120        then 'LATE'
        else 'SEVERELY_LATE'
    end
{%- endmacro %}
