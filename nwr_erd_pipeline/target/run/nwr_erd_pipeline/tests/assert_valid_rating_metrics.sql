
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- This query replaces Query 3.
-- If it returns any rows, the dbt test will fail and flag the bad data.

SELECT
    sk_rating_id, -- Used to be cms_rating_id
    sk_player_id,
    coin_in,
    theo_amount
FROM `nwr-data-platform`.`silver`.`fct_ratings`
WHERE coin_in < 0 OR theo_amount < 0
  
  
      
    ) dbt_internal_test