-- Each team's intervals must cover the whole game with no gaps:
-- total duration = last interval end, and regulation is at least 3600 seconds.
WITH per_team AS (
    SELECT
        game_id,
        team_abbrev,
        sum(duration_seconds) AS covered_seconds,
        max(interval_end)     AS game_end_seconds
    FROM {{ ref('int_strength_intervals') }}
    GROUP BY game_id, team_abbrev
)
SELECT *
FROM per_team
WHERE covered_seconds <> game_end_seconds
   OR game_end_seconds < 3600