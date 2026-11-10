{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT
    shift_id,
    game_id, 
    player_id,
    team_id, 
    team_abbrev,
    period, 
    shift_number,
    {{ mmss_to_seconds('start_time') }} AS start_period_seconds,
    {{ mmss_to_seconds('end_time') }} AS end_period_seconds,
    (period - 1) * 1200 + start_period_seconds AS start_game_seconds,
    (period - 1) * 1200 + end_period_seconds AS end_game_seconds,
    end_period_seconds - start_period_seconds AS duration_seconds,
    current_timestamp AS loaded_at
FROM {{source('raw', 'shifts')}}
WHERE type_code = 517