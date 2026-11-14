{{ config(severity='warn') }}
-- flags overlapping line changes in the NHL shift data, found in 6 games in 2025-26: 0703, 0846, 0970, 1005, 1163 and 1235.
SELECT *
FROM {{ ref('int_on_ice_validation') }}
WHERE (((actual_home_skaters + actual_home_goalie) > 6) 
    OR ((actual_away_skaters + actual_away_goalie) > 6))