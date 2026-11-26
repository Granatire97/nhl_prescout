WITH boxscore AS (
    SELECT
        game_id,
        SUM(shots_on_goal) AS summed_boxscore_sog
    FROM {{ ref("stg_boxscore_players")}}
    GROUP BY game_id
),
game_strength AS (
    SELECT 
        game_id,
        SUM(shots_for) AS summed_gs_sog
    FROM {{ ref("fct_team_game_strength")}}
    WHERE strength_bucket = 'ALL'
    GROUP BY game_id
)
SELECT 
    b.game_id,
    b.summed_boxscore_sog,
    gs.summed_gs_sog
FROM boxscore b
JOIN game_strength gs
    ON b.game_id = gs.game_id
WHERE b.summed_boxscore_sog != gs.summed_gs_sog