-- back compat for old kwarg name
  
  
        
            
            
            
            
        
    

    

    merge into `nwr-data-platform`.`silver`.`fct_ratings` as DBT_INTERNAL_DEST
        using (

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
        ) as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.sk_rating_id = DBT_INTERNAL_DEST.sk_rating_id))

    
    when matched then update set
        `sk_rating_id` = DBT_INTERNAL_SOURCE.`sk_rating_id`,`sk_player_id` = DBT_INTERNAL_SOURCE.`sk_player_id`,`rating_ts` = DBT_INTERNAL_SOURCE.`rating_ts`,`game_type` = DBT_INTERNAL_SOURCE.`game_type`,`coin_in` = DBT_INTERNAL_SOURCE.`coin_in`,`house_edge` = DBT_INTERNAL_SOURCE.`house_edge`,`theo_amount` = DBT_INTERNAL_SOURCE.`theo_amount`
    

    when not matched then insert
        (`sk_rating_id`, `sk_player_id`, `rating_ts`, `game_type`, `coin_in`, `house_edge`, `theo_amount`)
    values
        (`sk_rating_id`, `sk_player_id`, `rating_ts`, `game_type`, `coin_in`, `house_edge`, `theo_amount`)


    