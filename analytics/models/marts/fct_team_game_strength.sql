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
            WHEN e.skater_state = '5v5' THEN '5v5'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.strength_state = 'PP' THEN 'PP'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        CASE 
            WHEN e.strength_state = 'PK' THEN 'PK'
        END AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, strength_bucket

    UNION ALL 

    SELECT
        e.game_id,
        e.event_team_abbrev,
        'ALL' AS strength_bucket,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'blocked-shot' OR e.type_desc_key = 'goal')) AS corsi_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'missed-shot' OR e.type_desc_key = 'goal')) AS fenwick_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'shot-on-goal' OR e.type_desc_key = 'goal')) AS shots_for,
        COUNT(*) FILTER (WHERE (e.type_desc_key = 'goal')) AS goals_for
    FROM {{ ref("fct_events")}} e
    WHERE e.event_team_abbrev IS NOT NULL AND strength_bucket IS NOT NULL
    GROUP BY e.game_id, e.event_team_abbrev, strength_bucket
),
events_with_against AS (
    SELECT 
        a.*,
        b.corsi_for AS corsi_against,
        b.fenwick_for AS fenwick_against,
        b.shots_for AS shots_against,
        b.goals_for AS goals_against
    FROM event_for_counts a
    LEFT JOIN event_for_counts b
        ON a.game_id = b.game_id
        AND a.strength_bucket = b.strength_bucket
        AND a.event_team_abbrev <> b.event_team_abbrev
),
game_info AS(
    SELECT 
        sb.*,
        tg.game_date,
        tg.opponent,
        tg.is_home
    FROM strength_bucket sb
    JOIN {{ref("fct_team_games")}} tg 
        ON sb.game_id = tg.game_id
        AND sb.team_abbrev = tg.team_abbrev
)
SELECT 
    g.game_id,
    g.game_date,
    g.team_abbrev,
    g.opponent,
    g.is_home,
    g.strength_bucket,
    g.toi_seconds,
    e.corsi_for,
    e.corsi_against,
    e.fenwick_for,
    e.fenwick_against,
    e.shots_for,
    e.shots_against,
    e.goals_for,
    e.goals_against,
    current_timestamp as loaded_at
FROM game_info g
JOIN events_with_against e
    ON g.game_id = e.game_id 
    AND g.team_abbrev = e.event_team_abbrev
    AND g.strength_bucket = e.strength_bucket

