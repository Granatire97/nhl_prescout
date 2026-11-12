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
    current_timestamp AS loaded_at
FROM {{ ref("stg_play_by_play")}}
WHERE COALESCE(period_type, '') <> 'SO' 
   AND COALESCE(type_desc_key, '') <> 'game-end'

