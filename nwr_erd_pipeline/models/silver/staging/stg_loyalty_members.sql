WITH source AS (
    SELECT * FROM {{ source('bronze', 'loyalty_members') }}
)
SELECT
    CAST(member_no AS STRING) AS member_no,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    CAST(dob AS DATE) AS dob,
    CAST(tier AS STRING) AS tier,
    CAST(enroll_date AS DATE) AS enroll_date,
    CAST(_loaded_at AS TIMESTAMP) AS source_loaded_at
FROM source