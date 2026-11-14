{{ config(severity='error') }}
SELECT
    actual_home_skaters + actual_home_goalie AS actual_home_skaters,
    actual_away_skaters + actual_away_goalie AS actual_away_skaters
FROM {{ ref('int_on_ice_validation') }}
WHERE actual_home_skaters > 6 OR actual_away_skaters > 6