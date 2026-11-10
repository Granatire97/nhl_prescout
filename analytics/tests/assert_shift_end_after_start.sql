SELECT * 
FROM {{ ref('stg_shifts') }}
WHERE end_game_seconds < start_game_seconds