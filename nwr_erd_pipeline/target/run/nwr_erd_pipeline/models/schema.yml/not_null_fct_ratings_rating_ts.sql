
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select rating_ts
from `nwr-data-platform`.`dbt_erd_nwr_silver`.`fct_ratings`
where rating_ts is null



  
  
      
    ) dbt_internal_test