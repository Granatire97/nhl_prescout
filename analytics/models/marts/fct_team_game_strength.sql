{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
WITH strength_bucket AS (
    SELECT 
        si.game_id,
        si.team_abbrev,
        CASE 
            WHEN si.skater_state = '5v5' THEN '5v5'
        END AS strength_bucket,
        SUM(si.duration_seconds) AS toi_seconds
    FROM {{ ref("int_strength_intervals") }} si
    WHERE strength_bucket IS NOT NULL
    GROUP BY si.game_id, si.team_abbrev, strength_bucket

    UNION ALL 

    SELECT 
        si.game_id,
        si.team_abbrev,
        CASE 
            WHEN si.strength_state = 'PP' THEN 'PP'
        END AS strength_bucket,
        SUM(si.duration_seconds) AS toi_seconds
    FROM {{ ref("int_strength_intervals") }} si
    WHERE strength_bucket IS NOT NULL
    GROUP BY si.game_id, si.team_abbrev, strength_bucket

    UNION ALL 

    SELECT 
        si.game_id,
        si.team_abbrev,
        CASE 
            WHEN si.strength_state = 'PK' THEN 'PK'
        END AS strength_bucket,
        SUM(si.duration_seconds) AS toi_seconds
    FROM {{ ref("int_strength_intervals") }} si
    WHERE strength_bucket IS NOT NULL
    GROUP BY si.game_id, si.team_abbrev, strength_bucket

    UNION ALL 

    SELECT 
        si.game_id,
        si.team_abbrev,
        'ALL' AS strength_bucket,
        SUM(si.duration_seconds) AS toi_seconds
    FROM {{ ref("int_strength_intervals") }} si
    GROUP BY si.game_id, si.team_abbrev, strength_bucket
),
event_for_counts AS (
    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.event_team_abbrev = e.home_team_abbrev THEN e.away_team_abbrev 
            ELSE e.home_team_abbrev 
        END AS opponent_abbrev,
        CASE 
            WHEN e.skater_state = '5v5' THEN '5v5'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, opponent_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.event_team_abbrev = e.home_team_abbrev THEN e.away_team_abbrev 
            ELSE e.home_team_abbrev 
        END AS opponent_abbrev,
        CASE 
            WHEN e.strength_state = 'PP' THEN 'PP'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, opponent_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.event_team_abbrev = e.home_team_abbrev THEN e.away_team_abbrev 
            ELSE e.home_team_abbrev 
        END AS opponent_abbrev,
        CASE 
            WHEN e.strength_state = 'PK' THEN 'PK'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, opponent_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.event_team_abbrev = e.home_team_abbrev THEN e.away_team_abbrev 
            ELSE e.home_team_abbrev 
        END AS opponent_abbrev,
        'ALL' AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, opponent_abbrev, strength_bucket
),
events_with_against AS (
    SELECT
        coalesce(a.game_id, b.game_id) AS game_id,
        coalesce(a.event_team_abbrev, b.opponent_abbrev) AS event_team_abbrev,
        coalesce(a.strength_bucket,
                 CASE b.strength_bucket WHEN 'PP' THEN 'PK'
                                        WHEN 'PK' THEN 'PP'
                                        ELSE b.strength_bucket END) AS strength_bucket,
        coalesce(a.corsi_for, 0)   AS corsi_for,
        coalesce(a.fenwick_for, 0) AS fenwick_for,
        coalesce(a.shots_for, 0)   AS shots_for,
        coalesce(a.goals_for, 0)   AS goals_for,
        coalesce(b.corsi_for, 0)   AS corsi_against,
        coalesce(b.fenwick_for, 0) AS fenwick_against,
        coalesce(b.shots_for, 0)   AS shots_against,
        coalesce(b.goals_for, 0)   AS goals_against
    FROM event_for_counts a
    FULL OUTER JOIN event_for_counts b
        ON a.game_id = b.game_id
        AND b.strength_bucket = CASE a.strength_bucket
                                    WHEN 'PP' THEN 'PK'
                                    WHEN 'PK' THEN 'PP'
                                    ELSE a.strength_bucket
                                END
        AND a.event_team_abbrev <> b.event_team_abbrev
),
game_info AS(
    SELECT 
        sb.*,
        tg.game_date,
        tg.opponent,
        tg.is_home,
        tg.season, 
        tg.game_type
    FROM strength_bucket sb
    JOIN {{ref("fct_team_games")}} tg 
        ON sb.game_id = tg.game_id
        AND sb.team_abbrev = tg.team_abbrev
)
SELECT 
    g.season,
    g.game_id,
    g.game_date,
    g.game_type,
    g.team_abbrev,
    g.opponent,
    g.is_home,
    g.strength_bucket,
    g.toi_seconds,
    coalesce(e.corsi_for, 0) AS corsi_for,
    coalesce(e.corsi_against, 0) AS corsi_against,
    coalesce(e.fenwick_for, 0) AS fenwick_for,
    coalesce(e.fenwick_against, 0) AS fenwick_against,
    coalesce(e.shots_for, 0) AS shots_for,
    coalesce(e.shots_against, 0) AS shots_against,
    coalesce(e.goals_for, 0) AS goals_for,
    coalesce(e.goals_against, 0) AS goals_against,
    current_timestamp as loaded_at
FROM game_info g
LEFT JOIN events_with_against e
    ON g.game_id = e.game_id 
    AND g.team_abbrev = e.event_team_abbrev
    AND g.strength_bucket = e.strength_bucket

