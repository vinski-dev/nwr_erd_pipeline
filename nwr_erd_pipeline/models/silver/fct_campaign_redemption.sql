{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        partition_by={
            "field": "redemption_date",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by=['player_sk']
    )
}}

with redemptions as (
    select
        campaign_id,
        member_no,
        redemption_ts,
        redemption_ts as redemption_date,
        offer_amount,
        _loaded_at as source_loaded_at
    from {{ ref('stg_promo_redemptions') }}

    {% if is_incremental() %}
        where redemption_ts >= (
            select coalesce(max(redemption_ts), '1900-01-01')
            from {{ this }}
        )
    {% endif %}

    qualify row_number() over (
        partition by
            campaign_id, member_no, redemption_ts, offer_amount, _loaded_at
        order by campaign_id
    ) = 1
),

-- Sanitize and handle potential nulls cleanly before surrogate key generation
clean_redemptions as (
    select
        coalesce(campaign_id, 'UNKNOWN') as safe_campaign_id,
        coalesce(member_no, 'UNKNOWN') as safe_member_no,
        coalesce(cast(redemption_ts as string), '1900-01-01')
            as safe_redemption_ts,
        coalesce(cast(offer_amount as string), '0') as safe_offer_amount,
        coalesce(cast(source_loaded_at as string), '1900-01-01')
            as safe_loaded_at,
        redemption_date,
        offer_amount,
        source_loaded_at
    from redemptions
),

identities as (
    select
        player_sk,
        member_no,
        cms_player_id
    from {{ ref('int_player_identity_map') }}
    where member_no is not null
    qualify row_number() over (
        partition by member_no
        order by cms_player_id desc, player_sk
    ) = 1
)

select
    -- Clean, robust macro call using pre-sanitized column names
    {{ dbt_utils.generate_surrogate_key([
        'r.safe_campaign_id',
        'r.safe_member_no',
        'r.safe_redemption_ts',
        'r.safe_offer_amount',
        'r.safe_loaded_at'
    ]) }} as sk_redemption_id,
    coalesce(i.player_sk, 'UNKNOWN_PLAYER') as player_sk,
    i.cms_player_id,
    r.safe_campaign_id as campaign_id,
    {{ dbt_utils.generate_surrogate_key(['r.safe_campaign_id']) }}
        as sk_campaign_id,
    r.redemption_date,
    r.offer_amount,
    r.source_loaded_at
from clean_redemptions r
left join identities i
    on r.safe_member_no = i.member_no
