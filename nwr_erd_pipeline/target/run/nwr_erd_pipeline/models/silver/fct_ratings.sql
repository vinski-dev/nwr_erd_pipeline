
  
    

    create or replace table `nwr-data-platform`.`dbt_erd_nwr_silver`.`fct_ratings`
      
    partition by timestamp_trunc(rating_ts, day)
    

    
    OPTIONS()
    as (
      

WITH ratings AS (
    SELECT * FROM `nwr-data-platform`.`dbt_erd_nwr_silver`.`stg_cms_ratings`

    -- The incremental magic happens here:
    
),

identities AS (
    SELECT
        sk_player_id,
        cms_player_id
    FROM `nwr-data-platform`.`dbt_erd_nwr_silver`.`int_player_identity_map`
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
    );
  