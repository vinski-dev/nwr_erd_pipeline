
    
    

with dbt_test__target as (

  select cms_rating_id as unique_field
  from `nwr-data-platform`.`dbt_erd_nwr_silver`.`fct_ratings`
  where cms_rating_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


