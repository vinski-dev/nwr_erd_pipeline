
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- This query replaces Query 3.
-- If it returns any rows, the dbt test will fail and flag the bad data.

SELECT
    sk_rating_id, -- Used to be cms_rating_id
    player_sk,
    coin_in,
    theoretical_win
FROM `nwr-data-platform`.`dbt_erd_nwr_silver`.`fct_ratings`
WHERE coin_in < 0 OR theoretical_win < 0
  
  
      
    ) dbt_internal_test