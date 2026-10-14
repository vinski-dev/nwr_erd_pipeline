
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select cms_rating_id
from `nwr-data-platform`.`dbt_erd_nwr`.`fct_ratings`
where cms_rating_id is null



  
  
      
    ) dbt_internal_test