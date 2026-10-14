SELECT  FROM `nwr-data-platform.dbt_erd_nwr.dim_players` LIMIT 1000

--Uniqueness & Duplication Check (Silver Layer)
--This query validates that your surrogate keys and primary keys are truly unique. Any result greater than --0 indicates a duplication issue originating from the Bronze layer or a flawed join.

SELECT
    'dim_player' AS table_name,
    'Duplicate player_sk' AS anomaly_type,
    COUNT(player_sk) - COUNT(DISTINCT player_sk) AS anomaly_count
FROM `nwr-data-platform.dbt_erd_nwr.dim_players`
UNION ALL
SELECT
    'fct_ratings',
    'Duplicate cms_rating_id',
    COUNT(cms_rating_id) - COUNT(DISTINCT cms_rating_id)
FROM `nwr-data-platform.dbt_erd_nwr.fct_ratings`;


--2. Referential Integrity (Orphaned Records)
--This checks for logical leaks where transaction data exists, but the player identity is missing. This --often happens if the bronze_loyalty_cms_xref table is missing mappings.
----expected output -- should not return anything
SELECT
    r.cms_rating_id,
    r.player_sk AS missing_player_sk,
    r.rating_ts,
    r.coin_in
FROM `nwr-data-platform.dbt_erd_nwr.fct_ratings` r
LEFT JOIN `nwr-data-platform.dbt_erd_nwr.dim_players` p
    ON r.player_sk = p.player_sk
WHERE p.player_sk IS NULL;

--3. Business Logic & Metric Anomalies
--This flags mathematically impossible scenarios in your transactional data, such as negative coin-in, --invalid house edge percentages, or missing timestamps.
--expected output -- should not return anything
SELECT
    cms_rating_id,
    rating_ts,
    coin_in,
    house_edge,
    theo_amount,
    CASE
        WHEN rating_ts IS NULL THEN 'Missing Timestamp'
        WHEN coin_in < 0 THEN 'Negative Coin-In'
        WHEN house_edge < 0 OR house_edge > 1 THEN 'Invalid House Edge Ratio'
        WHEN theo_amount < 0 THEN 'Negative Theo'
    END AS anomaly_reason
FROM `nwr-data-platform.dbt_erd_nwr.fct_ratings`
WHERE
    rating_ts IS NULL
    OR coin_in < 0
    OR house_edge < 0
    OR house_edge > 1
    OR theo_amount < 0;
