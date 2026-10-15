{{ config(
    materialized='incremental',
    unique_key='sk_rating_id',

    partition_by={
         "field": "rating_ts",
        "data_type": "timestamp",
        "granularity": "day"

    }
) }}

WITH ratings AS (
    SELECT * FROM {{ ref('stg_cms_ratings') }}

    -- The incremental magic happens here:
    {% if is_incremental() %}
        WHERE source_loaded_at > (SELECT MAX(rating_ts) FROM {{ this }})
    {% endif %}
),

identities AS (
    SELECT
        sk_player_id,
        cms_player_id
    FROM {{ ref('int_player_identity_map') }}
    WHERE cms_player_id IS NOT NULL
)

SELECT
    r.sk_rating_id,
    i.sk_player_id,
    r.rating_ts,
    r.game_type,
    r.coin_in,
    r.house_edge,
    (r.coin_in * r.house_edge) AS theo_amount
FROM ratings r
JOIN identities i ON r.cms_player_id = i.cms_player_id
