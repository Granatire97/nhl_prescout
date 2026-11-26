{{ config(severity='error') }}
SELECT
    a.game_id,
    a.team_abbrev AS team_a,
    b.team_abbrev AS team_b,
    a.corsi_for AS team_a_cf,
    b.corsi_against AS team_b_ca
FROM {{ ref("fct_team_game_strength") }} a
FULL OUTER JOIN {{ ref("fct_team_game_strength") }} b
    ON a.game_id = b.game_id
    AND a.team_abbrev != b.team_abbrev
WHERE a.corsi_for == b.corsi_against