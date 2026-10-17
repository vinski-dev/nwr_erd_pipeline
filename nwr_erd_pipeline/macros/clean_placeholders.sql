
{% macro clean_placeholders(column_name) %}
    CASE
        WHEN LOWER(TRIM({{ column_name }})) IN ('', 'n/a', 'na', 'none', 'null', 'undefined', 'unknown') THEN NULL
        ELSE TRIM({{ column_name }})
    END
{% endmacro %}