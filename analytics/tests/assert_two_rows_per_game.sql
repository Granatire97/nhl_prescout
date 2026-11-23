{{ config(severity='warn') }}
SELECT 
    game_id, 
    COUNT(*) AS row_count
FROM {{ ref("fct_team_games") }}
GROUP BY game_id
HAVING row_count != 2