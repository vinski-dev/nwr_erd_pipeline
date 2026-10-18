-- 1. Define your target dataset and table
DECLARE project_dataset STRING DEFAULT 'nwr-data-platform.bronze';
DECLARE target_table STRING DEFAULT 'cms_players';

DECLARE full_table_path STRING;
DECLARE dynamic_sql STRING;

SET full_table_path = project_dataset || '.' || target_table;

-- 2. Build the dynamic SQL string using INFORMATION_SCHEMA
SET dynamic_sql = (
  SELECT STRING_AGG(
    FORMAT("""
      SELECT
        '%s' AS column_name,
        '%s' AS data_type,
        COUNT(*) AS total_rows,
        COUNT(%s) AS non_null_count,
        COUNTIF(%s IS NULL) AS null_count,
        ROUND(COUNTIF(%s IS NULL) / COUNT(*) * 100, 2) AS null_percentage,
        APPROX_COUNT_DISTINCT(%s) AS distinct_values
      FROM `%s`
    """,
    column_name, data_type, column_name, column_name, column_name, column_name, full_table_path),
    " UNION ALL "
  )
  FROM `nwr-data-platform.bronze.INFORMATION_SCHEMA.COLUMNS` -- Change '.bronze.' if profiling silver/gold
  WHERE table_name = target_table
);

-- 3. Execute the generated query
EXECUTE IMMEDIATE dynamic_sql;