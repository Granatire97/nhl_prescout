{{ config(severity='error') }}
SELECT *
FROM {{ ref('int_on_ice_validation') }}
WHERE (((actual_home_skaters + actual_home_goalie) > 6) 
    OR ((actual_away_skaters + actual_away_goalie) > 6))