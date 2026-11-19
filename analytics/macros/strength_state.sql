{% macro skater_state(team_skaters, opp_skaters) %}
    ({{ team_skaters }} || 'v' || {{ opp_skaters }})
{%- endmacro %}