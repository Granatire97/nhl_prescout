{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT
    game_id || ' - ' || event_id AS event_key,
    sort_order,
    game_id,
    event_id,
    period, 
    time_in_period,
    type_desc_key,
    situation_code,
    home_team_abbrev,
    away_team_abbrev,
    CASE 
        WHEN (details->>'eventOwnerTeamId')::INTEGER = home_team_id THEN home_team_abbrev
        WHEN (details->>'eventOwnerTeamId')::INTEGER = away_team_id THEN away_team_abbrev
        ELSE NULL
    END AS event_team_abbrev,
    details,
    current_timestamp AS loaded_at,
FROM {{source('raw', 'pbp_plays')}}

