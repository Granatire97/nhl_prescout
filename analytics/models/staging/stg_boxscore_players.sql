{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT
    game_id,
    CASE 
        WHEN team_side = 'home' THEN true ELSE false
    END AS is_home,
    team_abbrev,
    player_id,
    player_name,
    CASE 
        WHEN position_group = 'forwards' THEN 'F'
        WHEN position_group = 'defense' THEN 'D'
        WHEN position_group = 'goalies' THEN 'G'
    END AS position_group,
    jersey_number,
    position,
    (stats->>'goals')::INT AS goals, 
    (stats->>'assists')::INT AS assists,
    (stats->>'points')::INT AS points,
    {{ mmss_to_seconds('toi') }} AS toi_seconds,
    (stats->>'plusMinus')::INT AS plus_minus,
    (stats->>'pim')::INT AS penalty_minutes,
    (stats->>'hits')::INT AS hits,
    (stats->>'sog')::INT AS shots_on_goal,
    (stats->>'blockedShots')::INT AS blocked_shots,
    (stats->>'giveaways')::INT AS giveaways,
    (stats->>'takeaways')::INT AS takeaways,
    ROUND((stats->>'faceoffWinningPctg')::DOUBLE, 2) AS fo_pct,
    (stats->>'powerPlayGoals')::INT AS ppg,
    (stats->>'saves')::INT AS saves,
    (stats->>'shotsAgainst')::INT AS shots_against,
    (stats->>'goalsAgainst')::INT AS goals_against,
    ROUND((stats->>'savePctg')::DOUBLE, 2) AS save_pct,
    stats->>'decision' AS game_decision,
    current_timestamp AS loaded_at
FROM {{source('raw', 'boxscore_players') }}
