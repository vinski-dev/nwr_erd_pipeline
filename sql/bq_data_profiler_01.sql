-- 1. Define your dataset and the specific list of tables to profile
DECLARE project_dataset STRING DEFAULT 'nwr-data-platform.bronze';
DECLARE target_tables ARRAY<STRING> DEFAULT ['cms_players', 'cms_ratings', 'loyalty_members', 'promo_redemptions'];

DECLARE current_table STRING;
DECLARE dynamic_sql STRING;

-- 2. Create a temporary table to hold the consolidated results
CREATE TEMP TABLE ProfilingResults (
    table_name STRING,
    column_name STRING,
    data_type STRING,
    total_rows INT64,
    non_null_count INT64,
    null_count INT64,
    null_percentage FLOAT64,
    distinct_values INT64
);

-- 3. Loop through each table in the array
FOR t IN (SELECT table_name FROM UNNEST(target_tables) AS table_name)
DO
    SET current_table = t.table_name;

    -- Generate the dynamic profiling SQL for the current table
    SET dynamic_sql = (
        SELECT STRING_AGG(
            FORMAT("""
                SELECT
                    '%s' AS table_name,
                    '%s' AS column_name,
                    '%s' AS data_type,
                    COUNT(*) AS total_rows,
                    COUNT(%s) AS non_null_count,
                    COUNTIF(%s IS NULL) AS null_count,
                    ROUND(COUNTIF(%s IS NULL) / COUNT(*) * 100, 2) AS null_percentage,
                    APPROX_COUNT_DISTINCT(%s) AS distinct_values
                FROM `%s.%s`
            """,
            current_table, column_name, data_type, column_name, column_name, column_name, column_name, project_dataset, current_table),
            " UNION ALL "
        )
        -- Note: Ensure this matches your project_dataset
        FROM `nwr-data-platform.bronze.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = current_table
    );

    -- 4. Execute the generated SQL and append to the temp table
    IF dynamic_sql IS NOT NULL THEN
        EXECUTE IMMEDIATE 'INSERT INTO ProfilingResults ' || dynamic_sql;
    END IF;

END FOR;

-- 5. Return the final consolidated results
SSELECT
    table_name,
    column_name,
    data_type,
    total_rows,
    distinct_values,
    null_percentage,

    -- 1. The Primary Key Test
    CASE
        WHEN total_rows = 0 THEN 'Empty Table'
        WHEN distinct_values = total_rows THEN '✅ Possible PK (100% Unique)'
        ELSE 'Contains Duplicates'
    END AS uniqueness_status,

    -- 2. The Categorical Test
    CASE
        WHEN distinct_values <= 50 AND total_rows > 50 THEN '📊 Categorical (Dashboard Filter)'
        WHEN data_type IN ('INT64', 'FLOAT64', 'NUMERIC') AND distinct_values > 50 THEN '📈 Continuous Metric'
        ELSE 'High Cardinality / Text'
    END AS column_grain,

    -- 3. The Null Check
    CASE
        WHEN null_percentage > 0 THEN CONCAT('⚠️ ', CAST(null_percentage AS STRING), '% Null')
        ELSE '✅ 100% Complete'
    END AS completeness_status

FROM ProfilingResults
ORDER BY table_name, column_name;