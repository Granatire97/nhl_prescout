{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
WITH schedule AS (
    SELECT 
        season,
        game_id,
        game_type, 
        game_date,
        home_team_abbrev AS team_abbrev,
        away_team_abbrev AS opponent,
        team_abbrev = home_team_abbrev AS is_home,
        is_completed
    FROM {{ ref("stg_schedule") }}
    WHERE is_home

    UNION ALL 

    SELECT 
        season,
        game_id,
        game_type, 
        game_date,
        away_team_abbrev AS team_abbrev,
        home_team_abbrev AS opponent,
        team_abbrev = home_team_abbrev AS is_home,
        is_completed
    FROM {{ ref("stg_schedule") }}
    WHERE not is_home
),
goals_count AS(
    SELECT
        s.*,
        COALESCE(COUNT(*) FILTER (WHERE pbp.type_desc_key = 'goal' AND pbp.period_type <> 'SO' AND pbp.event_team_abbrev = s.team_abbrev), 0) AS goals_for_count,
        COALESCE(COUNT(*) FILTER (WHERE pbp.type_desc_key = 'goal' AND pbp.period_type <> 'SO' AND pbp.event_team_abbrev = s.opponent), 0) AS goals_against_count,
        COALESCE(COUNT(*) FILTER (WHERE pbp.type_desc_key = 'goal' AND pbp.period_type = 'SO' AND pbp.event_team_abbrev = s.team_abbrev), 0) AS shootout_goals_for,
        COALESCE(COUNT(*) FILTER (WHERE pbp.type_desc_key = 'goal' AND pbp.period_type = 'SO' AND pbp.event_team_abbrev = s.opponent), 0) AS shootout_goals_against,
        CASE 
            WHEN shootout_goals_against > shootout_goals_for THEN ANY_VALUE(s.opponent)
            WHEN shootout_goals_against < shootout_goals_for THEN ANY_VALUE(s.team_abbrev)
            ELSE NULL
        END AS shootout_winner
    FROM schedule s
    LEFT JOIN {{ ref("stg_play_by_play")}} pbp
        ON s.game_id = pbp.game_id
    GROUP BY ALL
),
goals_total AS (
    SELECT
        season,
        game_id,
        game_type,
        game_date,
        team_abbrev,
        opponent,
        is_home, 
        CASE 
            WHEN team_abbrev = shootout_winner THEN goals_for_count + 1 ELSE goals_for_count
        END AS goals_for,
        CASE 
            WHEN team_abbrev != shootout_winner THEN goals_against_count + 1 ELSE goals_against_count
        END AS goals_against,
        is_completed
    FROM goals_count
),
last_period AS (
    SELECT
        pbp.game_id,
        max(pbp.period) AS last_period
    FROM {{ref("stg_play_by_play")}} pbp
    GROUP BY pbp.game_id
),
decision AS (
    SELECT 
        g.*,
        CASE 
            WHEN lp.game_id IS NULL THEN NULL
            WHEN lp.last_period > 3 THEN true 
            ELSE false
        END AS is_ot,
        CASE 
            WHEN lp.game_id IS NULL THEN NULL
            WHEN lp.last_period = 5 AND g.game_type = 2 THEN true 
            ELSE false
        END AS is_shootout,
        CASE 
            WHEN lp.game_id IS NULL THEN NULL
            WHEN (is_ot OR is_shootout) AND goals_against > goals_for THEN 'OTL'
            WHEN (not is_ot AND not is_shootout) AND goals_against > goals_for THEN 'L' 
            ELSE 'W' 
        END AS decision,
    FROM goals_total g
    LEFT JOIN last_period lp
        ON lp.game_id = g.game_id
    GROUP BY ALL
),
rest_days_game_number AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY team_abbrev, season, game_type ORDER BY game_date) AS team_game_number,
        date_diff('day', LAG(game_date) OVER (PARTITION BY team_abbrev, season ORDER BY game_date), game_date) - 1 AS rest_days,
        CASE 
            WHEN rest_days IS NULL THEN NULL
            WHEN rest_days = 0 THEN true 
            ELSE false
        END AS is_back_to_back
    FROM decision
    WHERE game_type != 1
)
SELECT
    *,
    current_timestamp AS loaded_at
FROM rest_days_game_number
