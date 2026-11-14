{{ config(severity='warn') }}
WITH counts AS (
    SELECT 
        count(*) AS totals,
        count(*) FILTER (WHERE is_match) AS match_rate
    FROM {{ ref('int_on_ice_validation') }}
    WHERE type_desc_key NOT IN ('faceoff', 'period-end', 'period-start')
),
percents AS (
    SELECT 
        *,
        ROUND((match_rate / totals) * 100, 3) as percentage_match
    FROM counts
)
SELECT 
    *
FROM percents
WHERE percentage_match < 98