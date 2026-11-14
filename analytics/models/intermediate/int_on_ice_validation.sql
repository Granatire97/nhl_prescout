SELECT
    pbp.event_key,
    pbp.game_id,
    pbp.type_desc_key,
    pbp.strength_state,
    pbp.situation_code,
    COUNT(*) FILTER (WHERE ei.team_abbrev = pbp.home_team_abbrev AND NOT ei.is_goalie) AS actual_home_skaters,
    COUNT(*) FILTER (WHERE ei.team_abbrev = pbp.home_team_abbrev AND ei.is_goalie) AS actual_home_goalie,
    COUNT(*) FILTER (WHERE ei.team_abbrev = pbp.away_team_abbrev AND NOT ei.is_goalie) AS actual_away_skaters,
    COUNT(*) FILTER (WHERE ei.team_abbrev = pbp.away_team_abbrev AND ei.is_goalie) AS actual_away_goalie,
    pbp.home_skaters AS expected_home_skaters,
    pbp.home_goalie_in_net AS expected_home_goalie,
    pbp.away_skaters AS expected_away_skaters,
    pbp.away_goalie_in_net AS expected_away_goalie,
    CASE 
        WHEN ((actual_home_skaters = expected_home_skaters)
            AND (actual_home_goalie = expected_home_goalie)
            AND (actual_away_skaters = expected_away_skaters)
            AND (actual_away_goalie = expected_away_goalie)) THEN true 
        ELSE false
    END AS is_match
FROM {{ ref('int_play_by_play') }} pbp
LEFT JOIN {{ ref('int_events_on_ice') }} ei
    ON pbp.event_key = ei.event_key
GROUP BY pbp.event_key, expected_home_skaters,expected_away_skaters,
expected_home_goalie,expected_away_goalie, pbp.game_id, pbp.type_desc_key, pbp.strength_state,
pbp.situation_code
