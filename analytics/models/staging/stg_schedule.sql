{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT
    game_id, 
    season, 
    game_type,
    game_date::DATE AS game_date,
    start_time_utc::TIMESTAMP AS start_time_utc,
    game_state,
    home_team_abbrev,
    away_team_abbrev,
    home_team_id,
    away_team_id,
    venue,
    game_state IN('OFF', 'FINAL') AS is_completed,
    current_timestamp AS loaded_at
FROM {{source('raw', 'schedule')}}
QUALIFY ROW_NUMBER() OVER (PARTITION BY game_id ORDER BY loaded_at DESC) = 1
