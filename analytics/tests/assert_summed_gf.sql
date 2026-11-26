-- depends_on: {{ ref('fct_team_games') }}
-- depends_on: {{ ref('fct_team_game_strength') }}
{{ config(severity='warning') }}
WITH team_games AS (
    SELECT
        game_id,
        CASE 
            WHEN ANY_VALUE(is_shootout) THEN SUM(goals_for) - 1
            ELSE SUM(goals_for)
        END AS summed_goals_for
    FROM {{ ref("fct_team_games")}}
    GROUP BY game_id,
),
game_strength AS (
    SELECT 
        game_id,
        SUM(goals_for) AS summed_gf
    FROM {{ ref("fct_team_game_strength")}}
    WHERE strength_bucket = 'ALL'
    GROUP BY game_id
)
SELECT 
    tg.game_id,
    tg.summed_goals_for,
    gs.summed_gf
FROM team_games tg
JOIN game_strength gs
    ON tg.game_id = gs.game_id
WHERE tg.summed_goals_for != gs.summed_gf