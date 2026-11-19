{% macro strength_state(team_skaters, opp_skaters) %}
    CASE
        WHEN {{ team_skaters }} = 1 OR {{ opp_skaters }} = 1 THEN 'PS'
        WHEN {{ team_skaters }} = 6 THEN 'EA'
        WHEN {{ opp_skaters }} = 6 THEN 'EN'
        WHEN {{ team_skaters }} > {{ opp_skaters }} THEN 'PP'
        WHEN {{ team_skaters }} < {{ opp_skaters }} THEN 'PK'
        ELSE 'EV'
    END
{%- endmacro %}