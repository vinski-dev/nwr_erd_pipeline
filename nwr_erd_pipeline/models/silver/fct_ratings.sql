{{ config(
    materialized='incremental',
    unique_key='cms_rating_id',
    partition_by={'field': 'rating_ts', 'data_type': 'timestamp', 'granularity': 'day'},
    cluster_by=['player_sk']
) }}

WITH ratings AS (
    SELECT * FROM {{ source('casino_bronze', 'bronze_cms_ratings') }}

    -- Incremental logic: only process new data on subsequent runs
    {% if is_incremental() %}
        WHERE rating_ts > (SELECT MAX(rating_ts) FROM {{ this }})
    {% endif %}
),

xref AS (
    SELECT member_no, cms_player_id
    FROM {{ source('casino_bronze', 'bronze_loyalty_cms_xref') }}
)

SELECT
    r.cms_rating_id,
    -- Generate an MD5 string surrogate key using the dbt_utils macro
    {{ dbt_utils.generate_surrogate_key(['x.member_no']) }} AS player_sk,
    r.game_type,
    r.rating_ts,
    r.coin_in,
    r.house_edge,

    -- CENTRALIZED LOGIC: Compute Theo here, never in Gold
    ROUND(r.coin_in * r.house_edge, 2) AS theo_amount
FROM ratings r
LEFT JOIN xref x
    ON r.cms_player_id = x.cms_player_id