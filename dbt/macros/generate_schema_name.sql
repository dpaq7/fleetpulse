{#
    Custom schema naming: respect custom_schema_name when set in the model
    config, otherwise use the target's default schema. This keeps dev/ci/prod
    cleanly separated per target without prefixing.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
