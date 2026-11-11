-- Lafreniere for Game Against Detroit
SELECT n FROM (
    SELECT count(*) AS n FROM {{ ref('stg_boxscore_players') }}
    WHERE game_id = 2026020017 AND player_id = 8482109 AND toi_seconds = 1290
) WHERE n != 1