
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}
        {{ default_schema }}

    {%- elif target.name == 'prod' -%}
        {# In production, strictly use the custom name #}
        {{ custom_schema_name | trim }}

    {%- else -%}
        {# In dev or CI, safely concatenate so it does not overwrite prod #}
        {{ default_schema }}_{{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}