{{
    config(
        materialized='table',
        schema='silver'
    )
}}

WITH ratings AS (
    SELECT
        cms_player_id,
        rating_ts,
        game_type,
        coin_in,
        house_edge,
        _loaded_at
    FROM {{ ref('stg_cms_ratings') }}
),

identities AS (
    SELECT
        player_sk,
        cms_player_id
    FROM {{ ref('int_player_identity_map') }}
    WHERE cms_player_id IS NOT NULL
)


SELECT
    {{ dbt_utils.generate_surrogate_key(['r.cms_player_id', 'r.rating_ts']) }}
        AS sk_rating_id,
    i.player_sk,
    r.cms_player_id,
    r.game_type,
    r.coin_in,
    r.house_edge,
    (r.coin_in * r.house_edge) AS theoretical_win,
    r.rating_ts,
    r._loaded_at AS source_loaded_at
FROM ratings r
LEFT JOIN identities i

    ON r.cms_player_id = i.cms_player_id