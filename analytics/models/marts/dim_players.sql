{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='player_key'
    )
}}
WITH ranked_rows AS (
    SELECT 
        player_id || ' - ' || season AS player_key,
        *,
        ROW_NUMBER() OVER (
            PARTITION BY player_id, season 
            ORDER BY loaded_at DESC
        ) AS rn
    FROM {{ ref("stg_roster_spots")}}
),
latest AS (
    SELECT *
    FROM ranked_rows
    WHERE rn = 1
), 
number_of_games AS (
    SELECT 
        player_id || ' - ' || season AS player_key,
        count(game_id) as games_played,
        STRING_AGG(DISTINCT team_abbrev::text, ', ' ORDER BY team_abbrev ASC) AS all_teams
    FROM {{ ref("stg_roster_spots")}}
    GROUP BY player_key
)
SELECT 
    l.player_key,
    l.season, 
    l.team_id, 
    l.team_abbrev,
    l.player_id,
    l.first_name, 
    l.last_name, 
    l.player_name,
    l.jersey_number, 
    l.position,
    ng.games_played,
    ng.all_teams,
    current_timestamp AS loaded_at
FROM latest l INNER JOIN number_of_games ng ON l.player_key = ng.player_key