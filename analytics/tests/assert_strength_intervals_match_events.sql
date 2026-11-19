{{ config(severity='warn') }}
-- AC6: for shots and goals, the interval containing the event should have the same
-- skater and goalie counts as the event's situation code, on at least 99% of events.
WITH events AS (
    SELECT
        event_key,
        game_id,
        event_team_abbrev,
        event_game_seconds,
        event_skaters,
        opp_skaters,
        CASE WHEN is_home THEN home_goalie_in_net ELSE away_goalie_in_net END AS event_goalie_in_net,
        CASE WHEN is_home THEN away_goalie_in_net ELSE home_goalie_in_net END AS opp_goalie_in_net
    FROM {{ ref('fct_events') }}
    WHERE type_desc_key IN ('shot-on-goal', 'missed-shot', 'blocked-shot', 'goal')
      AND coalesce(strength_state, '') <> 'PS'
      AND game_id IN (SELECT DISTINCT game_id FROM {{ ref('int_strength_intervals') }})
),
matched AS (
    SELECT
        e.event_key,
        i.team_skaters      = e.event_skaters
        AND i.opp_skaters    = e.opp_skaters
        AND i.team_goalie_in_net = e.event_goalie_in_net
        AND i.opp_goalie_in_net  = e.opp_goalie_in_net AS is_match
    FROM events e
    LEFT JOIN {{ ref('int_strength_intervals') }} i
        ON  i.game_id = e.game_id
        AND i.team_abbrev = e.event_team_abbrev
        AND e.event_game_seconds >  i.interval_start
        AND e.event_game_seconds <= i.interval_end
)
SELECT
    count(*) AS events,
    count(*) FILTER (WHERE is_match) AS matched,
    round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) AS match_pct
FROM matched
HAVING round(100.0 * count(*) FILTER (WHERE is_match) / count(*), 2) < 99