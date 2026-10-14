-- back compat for old kwarg name
  
  
        
            
            
            
            
        
    

    

    merge into `nwr-data-platform`.`dbt_erd_nwr`.`fct_ratings` as DBT_INTERNAL_DEST
        using (

WITH ratings AS (
    SELECT * FROM `nwr-data-platform`.`casino_platform`.`bronze_cms_ratings`

    -- Incremental logic: only process new data on subsequent runs
    
        WHERE rating_ts > (SELECT MAX(rating_ts) FROM `nwr-data-platform`.`dbt_erd_nwr`.`fct_ratings`)
    
),

xref AS (
    SELECT member_no, cms_player_id
    FROM `nwr-data-platform`.`casino_platform`.`bronze_loyalty_cms_xref`
)

SELECT
    r.cms_rating_id,
    -- Generate an MD5 string surrogate key using the dbt_utils macro
    to_hex(md5(cast(coalesce(cast(x.member_no as string), '_dbt_utils_surrogate_key_null_') as string))) AS player_sk,
    r.game_type,
    r.rating_ts,
    r.coin_in,
    r.house_edge,

    -- CENTRALIZED LOGIC: Compute Theo here, never in Gold
    ROUND(r.coin_in * r.house_edge, 2) AS theo_amount
FROM ratings r
LEFT JOIN xref x
    ON r.cms_player_id = x.cms_player_id
        ) as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.cms_rating_id = DBT_INTERNAL_DEST.cms_rating_id))

    
    when matched then update set
        `cms_rating_id` = DBT_INTERNAL_SOURCE.`cms_rating_id`,`player_sk` = DBT_INTERNAL_SOURCE.`player_sk`,`game_type` = DBT_INTERNAL_SOURCE.`game_type`,`rating_ts` = DBT_INTERNAL_SOURCE.`rating_ts`,`coin_in` = DBT_INTERNAL_SOURCE.`coin_in`,`house_edge` = DBT_INTERNAL_SOURCE.`house_edge`,`theo_amount` = DBT_INTERNAL_SOURCE.`theo_amount`
    

    when not matched then insert
        (`cms_rating_id`, `player_sk`, `game_type`, `rating_ts`, `coin_in`, `house_edge`, `theo_amount`)
    values
        (`cms_rating_id`, `player_sk`, `game_type`, `rating_ts`, `coin_in`, `house_edge`, `theo_amount`)


    