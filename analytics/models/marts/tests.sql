-- SELECT
--     season,
--     game_id,
--     strength_state,
--     skater_state,
--     SUM(duration_seconds) AS total
-- FROM {{ref("int_strength_intervals")}}
-- WHERE game_id = 2025020001
-- GROUP BY season, game_id, strength_state, skater_state
-- HAVING total = 3240

SELECT DISTINCT type_desc_key
FROM {{ref("fct_events")}}