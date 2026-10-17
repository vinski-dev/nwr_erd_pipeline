{{
    config(
        materialized='table'
    )
}}

with snapshots as (
    select *
    from {{ ref('snp_players') }}
),

gaming_activity as (
    select
        cms_player_id,
        sum(coin_in) as lifetime_coin_in,
        count(1) as total_ratings_count
    from {{ ref('stg_cms_ratings') }}
    group by 1
)

select
    -- 1. Entity-Level Lifetime Key (Repeats across historical rows for the same player)
    {{ dbt_utils.generate_surrogate_key(['snapshots.player_natural_key']) }} as player_sk,

    -- 2. Row-Level Version Surrogate Key (100% UNIQUE per row/version)
    {{ dbt_utils.generate_surrogate_key(['snapshots.player_natural_key', 'snapshots.dbt_valid_from']) }} as player_version_sk,

    snapshots.player_natural_key,
    snapshots.cms_player_id,
    snapshots.member_no,
    snapshots.first_name,
    snapshots.last_name,
    snapshots.email,
    snapshots.dob,
    snapshots.loyalty_tier,
    snapshots.enroll_date,

    -- SCD Type 2 Audit Columns
    snapshots.dbt_valid_from as valid_from,
    snapshots.dbt_valid_to as valid_to,
    case when snapshots.dbt_valid_to is null then true else false end as is_current,

    -- Aggregated Metrics
    coalesce(g.lifetime_coin_in, 0) as lifetime_coin_in,
    coalesce(g.total_ratings_count, 0) as total_ratings_count,

    -- Official Enterprise Segmentation Logic
    case
        when snapshots.cms_player_id is not null and coalesce(g.lifetime_coin_in, 0) > 0 then true
        else false
    end as is_gaming_active,

    case
        when snapshots.cms_player_id is not null and coalesce(g.lifetime_coin_in, 0) > 0 then 'Casino Active'
        else 'Hotel / Loyalty Only'
    end as guest_segment,

    current_timestamp() as _updated_at

from snapshots
left join gaming_activity g
    on snapshots.cms_player_id = g.cms_player_id