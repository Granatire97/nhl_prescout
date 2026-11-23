{{ config(severity='warn') }}
SELECT
    a.game_id,
    a.team AS team_a,
    b.team AS team_b,
    a.goals_for AS team_a_gf,
    b.goals_against AS team_b_ga
FROM {{ ref("fct_team_games") }} a
FULL OUTER JOIN {{ ref("fct_team_games") }} b
    ON a.game_id = b.game_id
    AND a.team != b.team
WHERE a.goals_for IS DISTINCT FROM b.goals_against;