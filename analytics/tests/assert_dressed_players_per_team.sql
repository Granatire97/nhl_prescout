{{ config(severity='warn') }}
SELECT game_id, team_id, count(*) AS dressed
FROM {{ ref('stg_roster_spots') }}
GROUP BY game_id, team_id
HAVING count(*) NOT BETWEEN 18 AND 20