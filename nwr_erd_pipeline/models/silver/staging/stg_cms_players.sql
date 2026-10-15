WITH source AS (
    SELECT * FROM {{ source('bronze', 'cms_players') }}
)
SELECT
    CAST(cms_player_id AS STRING) AS cms_player_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    CAST(dob AS DATE) AS dob,
    CAST(_loaded_at AS TIMESTAMP) AS source_loaded_at
FROM source