{# Example utility macro. Converts a numeric column in cents to dollars. #}
{% macro cents_to_dollars(column_name, precision=2) -%}
    round(({{ column_name }} / 100)::numeric(18, {{ precision }}), {{ precision }})
{%- endmacro %}
