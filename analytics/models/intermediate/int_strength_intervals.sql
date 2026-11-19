{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
WITH shifts AS(
    SELECT 
        s.*,
        rs.season AS season,
        rs.position AS position,
        CASE
            WHEN rs.position = 'G' THEN true
            ELSE false
        END AS is_goalie,
    FROM {{ ref("stg_shifts") }} s
    JOIN {{ ref('stg_roster_spots') }} rs
        ON s.game_id = rs.game_id
        AND s.player_id = rs.player_id
),
boundaries AS (
    SELECT
        start_game_seconds AS boundary,
        game_id,
        period
    FROM shifts

    UNION 

    SELECT
        end_game_seconds AS boundary,
        game_id,
        period
    FROM shifts

    UNION

    SELECT
        (period - 1) * 1200 AS boundary,
        game_id,
        period
    FROM shifts
    GROUP BY game_id, period

    UNION
    SELECT
        CASE 
            WHEN period in (1, 2, 3) THEN period * 1200 
            ELSE max(end_game_seconds)
        END AS boundary,
        game_id,
        period
    FROM shifts
    GROUP BY game_id, period
),
intervals AS (
    SELECT 
        *,
        boundary AS interval_start,
        LEAD(boundary) OVER (PARTITION BY game_id, period ORDER BY boundary) AS interval_end,
    FROM boundaries
    QUALIFY interval_end IS NOT NULL
),
on_ice_counts AS (
    SELECT 
        sh.season,
        sh.game_id,
        sh.period,
        i.interval_start,
        i.interval_end,
        sh.team_abbrev,
        COUNT(*) FILTER (WHERE position <> 'G') AS team_skaters,
        least(COUNT(*) FILTER (WHERE position = 'G'), 1) AS team_goalie_in_net
    FROM intervals i
    JOIN shifts sh 
        ON sh.game_id = i.game_id
        AND sh.start_game_seconds <= i.interval_start AND sh.end_game_seconds >= i.interval_end
    GROUP BY sh.season, sh.game_id, sh.period, i.interval_start, i.interval_end, sh.team_abbrev
),
team_view AS (
    SELECT 
        team.season,
        team.game_id,
        team.period,
        team.interval_start,
        team.interval_end,
        team.team_abbrev,
        team.team_skaters,
        team.team_goalie_in_net,
        opp.team_abbrev AS opponent,
        opp.team_skaters AS opp_skaters,
        opp.team_goalie_in_net AS opp_goalie_in_net
    FROM on_ice_counts team
    JOIN on_ice_counts opp 
        ON team.game_id = opp.game_id
        AND team.interval_start = opp.interval_start
        AND team.interval_end = opp.interval_end
        AND team.team_abbrev != opp.team_abbrev
)
SELECT
    season,
    game_id,
    period,
    team_abbrev,
    team_skaters,
    team_goalie_in_net,
    opponent,
    opp_skaters,
    opp_goalie_in_net,
    interval_start,
    interval_end,
    interval_end - interval_start AS duration_seconds,
    {{ strength_state('team_skaters', 'opp_skaters') }} AS strength_state,
    {{ skater_state('team_skaters', 'opp_skaters') }} AS skater_state,
    current_timestamp AS loaded_at
FROM team_view