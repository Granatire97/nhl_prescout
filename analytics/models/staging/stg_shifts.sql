{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
WITH shifts AS (
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
)
SELECT *
FROM shifts s1 
WHERE NOT EXISTS(
    SELECT 1
    FROM shifts s2 
    WHERE 
        s1.game_id = s2.game_id
        AND s1.player_id = s2.player_id
        AND s1.period = s2.period
        AND s1.shift_id <> s2.shift_id
        AND ((s2.start_game_seconds <= s1.start_game_seconds) AND (s2.end_game_seconds >= s1.end_game_seconds))
        AND (
            (s2.end_game_seconds - s2.start_game_seconds) > (s1.end_game_seconds - s1.start_game_seconds)
            OR ((s2.end_game_seconds - s2.start_game_seconds) = (s1.end_game_seconds - s1.start_game_seconds)
                AND s2.shift_id < s1.shift_id)
        )
)