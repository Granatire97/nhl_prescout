{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
WITH lists AS (
    SELECT 
        ei.event_key,
        list(ei.player_id ORDER BY ei.player_id) FILTER (WHERE is_event_team AND NOT is_goalie AND position IN ('C', 'L', 'R')) AS event_team_forward_ids,
        list(ei.player_id ORDER BY ei.player_id) FILTER (WHERE is_event_team AND NOT is_goalie AND position = 'D') AS event_team_defenseman_ids,
        max(player_id) FILTER (WHERE is_event_team AND is_goalie) AS event_team_goalie_id,
        list(ei.player_id ORDER BY ei.player_id) FILTER (WHERE NOT is_event_team AND NOT is_goalie AND position IN ('C', 'L', 'R')) AS opponent_team_forward_ids,
        list(ei.player_id ORDER BY ei.player_id) FILTER (WHERE NOT is_event_team AND NOT is_goalie AND position = 'D') AS opponent_team_defenseman_ids,
        max(player_id) FILTER (WHERE NOT is_event_team AND is_goalie) AS opponent_team_goalie_id
    FROM {{ ref("int_events_on_ice")}} ei
    GROUP BY ei.event_key
)
SELECT
    pbp.*,
    l.event_team_forward_ids,
    l.event_team_defenseman_ids,
    l.event_team_goalie_id,
    l.opponent_team_forward_ids,
    l.opponent_team_defenseman_ids,
    l.opponent_team_goalie_id
FROM {{ ref("int_play_by_play") }} pbp
LEFT JOIN lists l
    ON pbp.event_key = l.event_key