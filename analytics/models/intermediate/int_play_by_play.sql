{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT
    event_key,
    sort_order,
    game_id,
    event_id,
    period,
    period_type,
    time_in_period,
    {{ mmss_to_seconds('time_in_period') }} AS event_period_seconds,
    (period - 1) * 1200 + event_period_seconds AS event_game_seconds,
    type_desc_key,
    home_team_abbrev,
    away_team_abbrev,
    event_team_abbrev,
    home_team_defending_side,
    (details->>'xCoord')::INTEGER AS x_raw,
    (details->>'yCoord')::INTEGER AS y_raw,
    details,
    situation_code,
    CASE
        WHEN SUBSTRING(situation_code, 1, 1)::INTEGER = 1 THEN 1 ELSE 0
    END AS away_goalie_in_net,
    CASE
        WHEN SUBSTRING(situation_code, 4, 1)::INTEGER = 1 THEN 1 ELSE 0
    END AS home_goalie_in_net,
    SUBSTRING(situation_code, 2, 1)::INTEGER AS away_skaters,
    SUBSTRING(situation_code, 3, 1)::INTEGER AS home_skaters,
    event_team_abbrev = home_team_abbrev AS is_home,
    CASE 
        WHEN is_home IS NULL THEN NULL
        WHEN is_home THEN away_team_abbrev
        ELSE home_team_abbrev
    END AS opponent,
    CASE 
        WHEN is_home IS NULL THEN NULL
        WHEN is_home THEN home_skaters
        ELSE away_skaters
    END AS event_skaters,
    CASE 
        WHEN is_home IS NULL THEN NULL
        WHEN is_home THEN away_skaters
        ELSE home_skaters
    END AS opp_skaters,
    CASE 
        WHEN is_home IS NULL THEN NULL
        WHEN is_home AND away_goalie_in_net = 0 THEN true
        WHEN is_home = FALSE AND home_goalie_in_net = 0 THEN true 
        ELSE false
    END AS is_empty_net_against,
    CASE
        WHEN is_home IS NULL THEN NULL
        WHEN event_skaters = 1 OR opp_skaters = 1 THEN 'PS'
        WHEN event_skaters = 6 THEN 'EA'
        WHEN opp_skaters = 6 THEN 'EN'
        WHEN event_skaters > opp_skaters THEN 'PP'
        WHEN event_skaters < opp_skaters THEN 'PK'
    ELSE 'EV'
    END AS strength_state,
    event_skaters || 'v' || opp_skaters AS skater_state,
    CASE 
        WHEN is_home IS NULL OR home_team_defending_side IS NULL THEN NULL 
        WHEN (is_home AND home_team_defending_side = 'left') OR (is_home = false AND home_team_defending_side = 'right') THEN x_raw
        ELSE -x_raw
    END AS x_norm,
        CASE 
        WHEN is_home IS NULL OR home_team_defending_side IS NULL THEN NULL 
        WHEN (is_home AND home_team_defending_side = 'left') OR (is_home = false AND home_team_defending_side = 'right') THEN y_raw
        ELSE -y_raw
    END AS y_norm,
    CASE 
        WHEN type_desc_key IN ('shot-on-goal', 'missed-shot', 'blocked-shot', 'goal') THEN
            ROUND(SQRT(POWER(89 - x_norm, 2) + POWER(y_norm, 2)), 3)
        ELSE NULL 
    END AS shot_distance,
    CASE 
        WHEN type_desc_key IN ('shot-on-goal', 'missed-shot', 'blocked-shot', 'goal') THEN
            ROUND(DEGREES(ATAN2(ABS(y_norm), 89 - x_norm)), 3)
        ELSE NULL 
    END AS shot_angle,
    current_timestamp AS loaded_at
FROM {{ ref("stg_play_by_play")}}
WHERE COALESCE(period_type, '') <> 'SO' 
   AND COALESCE(type_desc_key, '') <> 'game-end'

