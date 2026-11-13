{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT 
    v.event_key || ' - ' || s.player_id AS event_ice_key,
    v.event_key,
    v.sort_order,
    v.game_id,
    v.event_game_seconds,
    v.type_desc_key,
    CASE
        WHEN v.event_team_abbrev IS NULL THEN NULL
        WHEN s.team_abbrev = v.event_team_abbrev THEN true
        ELSE false
    END AS is_event_team,
    s.player_id,
    s.team_id,
    s.team_abbrev,
    s.shift_id,
    rs.position,
    rs.jersey_number,
    CASE
        WHEN rs.position = 'G' THEN true
        ELSE false
    END AS is_goalie,
    current_timestamp AS loaded_at
FROM  {{ ref("stg_shifts")}} s
JOIN {{ ref("int_play_by_play")}} v
    ON v.game_id = s.game_id
    AND v.period = s.period
    AND (CASE WHEN v.type_desc_key = 'faceoff' THEN (s.start_game_seconds <= v.event_game_seconds AND v.event_game_seconds < s.end_game_seconds) ELSE (s.start_game_seconds < v.event_game_seconds AND v.event_game_seconds <= s.end_game_seconds) END)
JOIN {{ ref('stg_roster_spots') }} rs
    ON s.game_id = rs.game_id
    AND s.player_id = rs.player_id
    

