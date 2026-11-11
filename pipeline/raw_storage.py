RAW_PBP =  """
    WITH pbp_info AS (
        SELECT 
            id AS game_id,
            season AS season,
            awayTeam as away_team, 
            homeTeam as home_team,
            UNNEST(plays) AS play
        FROM read_json(?, columns:={id: 'BIGINT', season: 'BIGINT', plays: 'JSON[]', awayTeam: 'JSON', homeTeam: 'JSON'})
        )
        SELECT game_id, 
                season,
                (play->>'eventId')::BIGINT AS event_id,
                (play->'periodDescriptor'->>'number')::BIGINT AS period,
                (play->>'typeDescKey') AS type_desc_key,
                (play->>'typeCode')::INTEGER AS type_code,
                (play->>'sortOrder')::INTEGER AS sort_order,
                (play->'periodDescriptor'->>'periodType') AS period_type,
                (play->>'timeRemaining') AS time_remaining,
                (play->>'situationCode') AS situation_code,
                (play->>'homeTeamDefendingSide') AS home_team_defending_side,
                (away_team ->> 'id')::INTEGER AS away_team_id,
                away_team ->> 'abbrev' AS away_team_abbrev,
                (home_team ->> 'id')::INTEGER AS home_team_id,
                home_team ->> 'abbrev' AS home_team_abbrev,
                play->'details' AS details,
                current_timestamp AS loaded_at,
                (play->>'timeInPeriod')::VARCHAR as time_in_period
        FROM pbp_info
"""

RAW_BOXSCORE = """
    WITH boxscore_info AS (
        SELECT 
            id AS game_id,
            awayTeam AS away_team,
            homeTeam AS home_team,
            playerByGameStats AS player_game_stats
        FROM read_json(?, columns:={id: 'BIGINT', awayTeam: 'JSON', homeTeam: 'JSON', playerByGameStats: 'JSON'})
        ),
        players AS (
            SELECT game_id,
                'away' AS team_side,
                'forwards' as position_group,
                away_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'awayTeam'->'forwards')::JSON[]) AS player
            FROM boxscore_info
            UNION ALL
            SELECT game_id,
                'away' AS team_side,
                'defense' as position_group,
                away_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'awayTeam'->'defense')::JSON[]) AS player
            FROM boxscore_info
            UNION ALL
            SELECT game_id,
                'away' AS team_side,
                'goalies' as position_group,
                away_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'awayTeam'->'goalies')::JSON[]) AS player
            FROM boxscore_info
            UNION ALL
            SELECT game_id,
                'home' AS team_side,
                'forwards' as position_group,
                home_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'homeTeam'->'forwards')::JSON[]) AS player
            FROM boxscore_info
            UNION ALL
            SELECT game_id,
                'home' AS team_side,
                'defense' as position_group,
                home_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'homeTeam'->'defense')::JSON[]) AS player
            FROM boxscore_info
            UNION ALL
            SELECT game_id,
                'home' AS team_side,
                'goalies' as position_group,
                home_team ->> 'abbrev' AS team_abbrev,
                UNNEST((player_game_stats->'homeTeam'->'goalies')::JSON[]) AS player
            FROM boxscore_info
        )
        SELECT
            game_id, 
            team_side,
            team_abbrev,
            position_group,
            (player->>'playerId')::BIGINT AS player_id,
            (player->'name'->>'default') AS player_name,
            (player->>'sweaterNumber')::INTEGER as jersey_number,
            (player->>'position') as position,
            (player->>'toi') as toi,
            player AS stats,
            current_timestamp AS loaded_at
        FROM players
"""

RAW_SHIFTS = """
    WITH shift_info AS (
        SELECT 
            UNNEST(data) AS shifts
        FROM read_json(?, columns:={data: 'JSON[]'})
        )
        SELECT
            (shifts->>'gameId')::BIGINT AS game_id,
            (shifts->>'id')::BIGINT AS shift_id,
            (shifts->>'period')::BIGINT AS period,
            (shifts->>'playerId')::BIGINT AS player_id,
            (shifts->>'teamId')::INTEGER AS team_id,
            (shifts->>'teamAbbrev') AS team_abbrev,
            (shifts->>'shiftNumber')::INTEGER AS shift_number,
            (shifts->>'startTime') AS start_time,
            (shifts->>'endTime') AS end_time,
            (shifts->>'duration') AS duration,
            (shifts->>'typeCode')::BIGINT AS type_code,
            (shifts->>'detailCode')::BIGINT AS detail_code,
            current_timestamp AS loaded_at,
        FROM shift_info
"""

RAW_SCHEDULE = """
    WITH schedule_info AS (
        SELECT 
            UNNEST(games) AS game
        FROM read_json(?, columns:={games: 'JSON[]'})
        )
        SELECT
            ? AS team,
            (game->>'id')::BIGINT AS game_id,
            (game->>'season')::BIGINT AS season,
            (game->>'gameType')::BIGINT AS game_type,
            (game->>'gameDate') AS game_date,
            (game->>'gameState') AS game_state,
            (game->'awayTeam'->>'abbrev') AS away_team_abbrev,
            (game->'homeTeam'->>'abbrev') AS home_team_abbrev,
            (game->>'startTimeUTC') AS start_time_utc,
            (game->'awayTeam'->>'id')::INTEGER AS away_team_id,
            (game->'homeTeam'->>'id')::INTEGER AS home_team_id,
            (game->'venue'->>'default') AS venue,
            current_timestamp AS loaded_at,
        FROM schedule_info
"""