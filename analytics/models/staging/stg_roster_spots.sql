{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='game_id'
    )
}}
SELECT 
    game_id,
    season, 
    team_id, 
    team_abbrev,
    player_id,
    first_name, 
    last_name, 
    first_name || ' ' || last_name AS player_name,
    jersey_number, 
    position,
    current_timestamp AS loaded_at
FROM {{ source('raw', 'roster_spots') }}
