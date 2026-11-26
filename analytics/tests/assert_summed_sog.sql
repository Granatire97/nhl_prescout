{{ config(severity='warn') }}
-- ALL shots_for per team = boxscore skater SOG + shots taken by goalies
-- (goalie boxscore rows have no SOG, but play-by-play does).
WITH boxscore AS (
    SELECT game_id, team_abbrev, sum(coalesce(shots_on_goal, 0)) AS box_sog
    FROM {{ ref('stg_boxscore_players') }}
    GROUP BY game_id, team_abbrev
),
goalie_shots AS (
    SELECT p.game_id, rs.team_abbrev, count(*) AS goalie_sog
    FROM {{ ref('stg_play_by_play') }} p
    JOIN {{ ref('stg_roster_spots') }} rs
      ON rs.game_id = p.game_id
     AND rs.player_id = coalesce(p.details->>'shootingPlayerId', p.details->>'scoringPlayerId')::BIGINT
    WHERE p.type_desc_key IN ('shot-on-goal', 'goal')
      AND p.period_type <> 'SO'
      AND rs.position = 'G'
    GROUP BY p.game_id, rs.team_abbrev
),
model AS (
    SELECT game_id, team_abbrev, shots_for
    FROM {{ ref('fct_team_game_strength') }}
    WHERE strength_bucket = 'ALL'
)
SELECT
    m.game_id,
    m.team_abbrev,
    m.shots_for,
    b.box_sog,
    coalesce(g.goalie_sog, 0) AS goalie_sog
FROM model m
JOIN boxscore b
  ON b.game_id = m.game_id AND b.team_abbrev = m.team_abbrev
LEFT JOIN goalie_shots g
  ON g.game_id = m.game_id AND g.team_abbrev = m.team_abbrev
WHERE m.shots_for <> b.box_sog + coalesce(g.goalie_sog, 0)