{{
    config(
        materialized='view'
    )
}}

with cms_players as (
    select *
    from {{ ref('stg_cms_players') }}
),

loyalty_members as (
    select *
    from {{ ref('stg_loyalty_members') }}
),

joined_identities as (
    select
        -- Stable natural key resolved across systems
        coalesce(c.cms_player_id, l.member_no) as player_natural_key,
        c.cms_player_id,
        l.member_no,

        -- Conformed attributes (resolving overlaps via email PII)
        coalesce(c.email, l.email) as email,
        coalesce(c.first_name, l.first_name) as first_name,
        coalesce(c.last_name, l.last_name) as last_name,
        coalesce(c.dob, l.dob) as dob,

        -- Loyalty attributes
        l.tier as loyalty_tier,
        l.enroll_date,

        -- Source coverage tracking flags
        case when c.cms_player_id is not null then true else false end
            as has_casino_profile,
        case when l.member_no is not null then true else false end
            as has_loyalty_profile

    from cms_players c
    full outer join loyalty_members l
        on c.email = l.email
)

select
    {{ dbt_utils.generate_surrogate_key(['player_natural_key']) }} as player_sk,
    player_natural_key,
    cms_player_id,
    member_no,
    email,
    first_name,
    last_name,
    CAST(dob AS DATE) as dob,
    loyalty_tier,
    CAST(enroll_date AS DATE) as enroll_date,
    has_casino_profile,
    has_loyalty_profile
from joined_identities

UNION ALL

select
    'UNKNOWN_PLAYER' as player_sk,
    'UNKNOWN_NATURAL_KEY' as player_natural_key,
    'UNKNOWN' as cms_player_id,
    'UNKNOWN' as member_no,
    'unknown@casino.com' as email,
    'Unknown' as first_name,
    'Player' as last_name,
    CAST('1900-01-01' AS DATE) as dob,
    'Standard' as loyalty_tier,
    CAST('1900-01-01' AS DATE) as enroll_date,
    false as has_casino_profile,
    false as has_loyalty_profile
