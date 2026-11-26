{{ config(severity='error') }}
-- AC4/AC5: attempts blocked against a team (CA - FA) should equal the team's
-- summed boxscore blocked_shots, on at least 99% of team-games.
WITH model_blocks AS (
    SELECT
        game_id,
        team_abbrev,
        corsi_against - fenwick_against AS blocked_against
    FROM {{ ref('fct_team_game_strength') }}
    WHERE strength_bucket = 'ALL'
),
boxscore_blocks AS (
    SELECT
        game_id,
        team_abbrev,
        sum(coalesce(blocked_shots, 0)) AS blocked_shots
    FROM {{ ref('stg_boxscore_players') }}
    GROUP BY game_id, team_abbrev
),
compared AS (
    SELECT
        m.game_id,
        m.team_abbrev,
        m.blocked_against,
        b.blocked_shots,
        m.blocked_against = b.blocked_shots AS is_match
    FROM model_blocks m
    JOIN boxscore_blocks b
      ON b.game_id = m.game_id
     AND b.team_abbrev = m.team_abbrev
)
SELECT
    count(*) AS team_games,
    count(*) FILTER (WHERE is_match) AS matched,
    round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) AS match_pct
FROM compared
HAVING round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) < 99