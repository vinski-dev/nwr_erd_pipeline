

WITH ratings AS (
    SELECT * FROM `nwr-data-platform`.`silver`.`stg_cms_ratings`

    -- The incremental magic happens here:
    
        WHERE source_loaded_at > (SELECT MAX(rating_ts) FROM `nwr-data-platform`.`silver`.`fct_ratings`)
    
),

identities AS (
    SELECT
        sk_player_id,
        cms_player_id
    FROM `nwr-data-platform`.`silver`.`int_player_identity_map`
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