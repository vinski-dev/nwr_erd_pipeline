
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select player_sk
from `nwr-data-platform`.`dbt_erd_nwr_silver`.`dim_players`
where player_sk is null



  
  
      
    ) dbt_internal_test