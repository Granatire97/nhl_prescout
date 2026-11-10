{% macro mmss_to_seconds(col) %}
    (split_part({{col }}, ':', 1)::INTEGER * 60 + split_part({{ col }}, ':', 2)::INTEGER)
{%- endmacro %}