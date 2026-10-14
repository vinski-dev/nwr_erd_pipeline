
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- This query replaces Query 3.
-- If it returns any rows, the dbt test will fail and flag the bad data.

SELECT
    cms_rating_id,
    rating_ts,
    coin_in,
    house_edge,
    theo_amount
FROM `nwr-data-platform`.`dbt_erd_nwr`.`fct_ratings`
WHERE
    coin_in < 0
    OR house_edge < 0
    OR house_edge > 1
    OR theo_amount < 0
  
  
      
    ) dbt_internal_test