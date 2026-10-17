-- tests/assert_crossover_guests_exist.sql
-- If this test fails, it means the intermediate identity spine is broken
-- and no longer successfully linking hotel and casino records together.

WITH crossover_calc AS (
    SELECT COUNT(DISTINCT d.guest_master_sk) AS crossover_count
    FROM {{ ref('dim_players') }} d
    -- INNER JOIN forces the engine to only keep guests present in BOTH fact tables
    INNER JOIN {{ ref('fct_gaming_revenue') }} c
        ON d.guest_master_sk = c.guest_master_sk
    INNER JOIN {{ ref('fct_hotel_revenue') }} h
        ON d.guest_master_sk = h.guest_master_sk
)

SELECT
    'Identity spine failure: No cross-over guests found' AS failure_reason,
    crossover_count
FROM crossover_calc
-- The test will only return a row (and FAIL) if the count drops to 0
WHERE crossover_count = 0
