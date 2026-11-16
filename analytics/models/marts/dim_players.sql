{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='player_key'
    )
}}
WITH ranked_rows AS (
    SELECT 
        rs.player_id || ' - ' || rs.season AS player_key,
        rs.*,
        ROW_NUMBER() OVER (
            PARTITION BY rs.player_id, rs.season 
            ORDER BY s.game_date DESC, rs.game_id DESC
        ) AS rn
    FROM {{ ref("stg_roster_spots")}} rs
    JOIN {{ ref("stg_schedule") }} s ON 
        rs.game_id = s.game_id
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