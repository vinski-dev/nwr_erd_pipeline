-- Streamlined Transformed Data Profiler (Complementing dbt tests)
-- Focuses purely on core table volumes and population status.

WITH model_volumes AS (

    -- 1. dim_players Volume & Population
    SELECT
        'dim_players' AS table_name,
        'table_row_count' AS checked_column,
        'Volume Check' AS anomaly_type,
        CAST(COUNT(*) AS STRING) AS anomaly_metric,
        CASE WHEN COUNT(*) > 0 THEN '✅ Populated' ELSE '⚠️ Empty Table' END AS status
    FROM `nwr-data-platform.dbt_erd_nwr_staging_silver.dim_players`

    UNION ALL

    -- 2. fct_campaign_redemption Volume & Population
    SELECT
        'fct_campaign_redemption' AS table_name,
        'table_row_count' AS checked_column,
        'Volume Check' AS anomaly_type,
        CAST(COUNT(*) AS STRING) AS anomaly_metric,
        CASE WHEN COUNT(*) > 0 THEN '✅ Populated' ELSE '⚠️ Empty Table' END AS status
    FROM `nwr-data-platform.dbt_erd_nwr_staging_silver.fct_campaign_redemption`

    UNION ALL

    -- 3. fct_ratings Volume & Population
    SELECT
        'fct_ratings' AS table_name,
        'table_row_count' AS checked_column,
        'Volume Check' AS anomaly_type,
        CAST(COUNT(*) AS STRING) AS anomaly_metric,
        CASE WHEN COUNT(*) > 0 THEN '✅ Populated' ELSE '⚠️ Empty Table' END AS status
    FROM `nwr-data-platform.dbt_erd_nwr_staging_silver.fct_ratings`
)

SELECT
    table_name,
    checked_column,
    anomaly_type,
    anomaly_metric,
    status
FROM model_volumes