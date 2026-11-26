{{ config(severity='error') }}
-- Attempts blocked against a team (CA - FA) include the opponent's shots blocked by
-- the opponent's own teammates. Remove those, then compare with the team's boxscore
-- blocked_shots on at least 99% of team-games.
WITH model_blocks AS (
    SELECT game_id, team_abbrev, opponent,
           corsi_against - fenwick_against AS blocked_against
    FROM {{ ref('fct_team_game_strength') }}
    WHERE strength_bucket = 'ALL'
),
teammate_blocks AS (
    -- shots a team had blocked by its own players
    SELECT p.game_id, p.event_team_abbrev AS shooting_team, count(*) AS teammate_blocked
    FROM {{ ref('stg_play_by_play') }} p
    JOIN {{ ref('stg_roster_spots') }} rs
      ON rs.game_id = p.game_id
     AND rs.player_id = (p.details->>'blockingPlayerId')::BIGINT
    WHERE p.type_desc_key = 'blocked-shot'
      AND rs.team_abbrev = p.event_team_abbrev
    GROUP BY p.game_id, p.event_team_abbrev
),
boxscore_blocks AS (
    SELECT game_id, team_abbrev, sum(coalesce(blocked_shots, 0)) AS blocked_shots
    FROM {{ ref('stg_boxscore_players') }}
    GROUP BY game_id, team_abbrev
),
compared AS (
    SELECT
        m.game_id,
        m.team_abbrev,
        m.blocked_against - coalesce(t.teammate_blocked, 0) AS blocked_by_team,
        b.blocked_shots,
        m.blocked_against - coalesce(t.teammate_blocked, 0) = b.blocked_shots AS is_match
    FROM model_blocks m
    LEFT JOIN teammate_blocks t
      ON t.game_id = m.game_id AND t.shooting_team = m.opponent
    JOIN boxscore_blocks b
      ON b.game_id = m.game_id AND b.team_abbrev = m.team_abbrev
)
SELECT
    count(*) AS team_games,
    count(*) FILTER (WHERE is_match) AS matched,
    round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) AS match_pct
FROM compared
HAVING round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) < 99