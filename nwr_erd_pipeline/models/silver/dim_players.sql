{{ config(
    materialized='table',
    cluster_by=['player_sk']
) }}

WITH loyalty AS (
    SELECT
        member_no,
        tier,
        dob,
        enroll_date
    FROM {{ source('casino_bronze', 'bronze_loyalty_members') }}
),

xref AS (
    SELECT
        member_no,
        cms_player_id
    FROM {{ source('casino_bronze', 'bronze_loyalty_cms_xref') }}
)

SELECT
    -- Generate an MD5 string surrogate key using the dbt_utils macro
    {{ dbt_utils.generate_surrogate_key(['l.member_no']) }} AS player_sk,
    x.cms_player_id,
    l.member_no,
    l.tier,
    l.dob,
    l.enroll_date,
    CURRENT_TIMESTAMP() AS dbt_updated_at
FROM loyalty l
LEFT JOIN xref x
    ON l.member_no = x.member_no