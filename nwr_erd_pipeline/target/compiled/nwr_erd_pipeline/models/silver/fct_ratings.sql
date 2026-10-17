

WITH ratings AS (
    SELECT
        cms_player_id,
        rating_ts,
        game_type,
        coin_in,
        house_edge,
        _loaded_at
    FROM `nwr-data-platform`.`dbt_erd_nwr_silver`.`stg_cms_ratings`
),

identities AS (
    SELECT
        player_sk,
        cms_player_id
    FROM `nwr-data-platform`.`dbt_erd_nwr_silver`.`int_player_identity_map`
    WHERE cms_player_id IS NOT NULL
)


SELECT
    to_hex(md5(cast(coalesce(cast(r.cms_player_id as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(r.rating_ts as string), '_dbt_utils_surrogate_key_null_') as string)))
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