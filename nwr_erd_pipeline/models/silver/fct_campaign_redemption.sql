WITH redemptions AS (
    SELECT * FROM {{ ref('stg_promo_redemptions') }}
),

identities AS (
    SELECT
        sk_player_id,
        member_no
    FROM {{ ref('int_player_identity_map') }}
    WHERE member_no IS NOT NULL
)

SELECT
    r.sk_redemption_id,
    -- Use the conformed sk_campaign_id to link to your dim_campaign model
    {{ dbt_utils.generate_surrogate_key(['r.campaign_id']) }} AS sk_campaign_id,
    i.sk_player_id,
    r.redemption_ts,
    r.offer_amount
FROM redemptions r
JOIN identities i ON r.member_no = i.member_no
