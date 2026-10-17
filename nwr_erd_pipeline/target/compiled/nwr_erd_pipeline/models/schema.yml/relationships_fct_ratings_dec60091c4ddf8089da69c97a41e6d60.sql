
    
    

with child as (
    select player_sk as from_field
    from (select * from `nwr-data-platform`.`dbt_erd_nwr_silver`.`fct_ratings` where player_sk != 'UNKNOWN_PLAYER') dbt_subquery
    where player_sk is not null
),

parent as (
    select player_sk as to_field
    from `nwr-data-platform`.`dbt_erd_nwr_silver`.`dim_players`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


