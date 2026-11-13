WITH counts AS (
    SELECT 
        count(*) AS shots,
        count(*) FILTER (WHERE x_norm < 0) AS negative_x
    FROM clean.int_play_by_play
    WHERE type_desc_key IN ('shot-on-goal', 'missed-shot', 'blocked-shot', 'goal')
),
percents AS (
    SELECT 
        *,
        ROUND((negative_x / shots) * 100, 3) as percentage_neg
    FROM counts
)
SELECT 
    *
FROM percents
WHERE percentage_neg >= 2