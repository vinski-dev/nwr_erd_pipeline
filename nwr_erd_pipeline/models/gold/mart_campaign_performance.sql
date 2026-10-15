{{ config(materialized='table') }}

WITH redemptions AS (
    SELECT
        sk_campaign_id,
        sk_player_id,
        MIN(redemption_ts) AS first_redemption_ts,
        SUM(offer_amount) AS total_offer_amount
    FROM {{ ref('fct_campaign_redemption') }}
    GROUP BY 1, 2
),

player_play AS (
    SELECT
        sk_player_id,
        rating_ts,
        theo_amount
    FROM {{ ref('fct_ratings') }}
),

performance_calc AS (
    SELECT
        r.sk_campaign_id,
        r.sk_player_id,
        TRUE AS is_redeemed,
        r.total_offer_amount,
        -- Post-campaign play: Theo generated within 3 days AFTER redemption
        SUM(CASE
            WHEN
                p.rating_ts BETWEEN r.first_redemption_ts
                AND TIMESTAMP_ADD(r.first_redemption_ts, INTERVAL 3 DAY)
                THEN p.theo_amount
            ELSE 0
        END) AS post_campaign_theo,

        -- Baseline play: Theo generated in the 3 days PRIOR to redemption
        SUM(CASE
            WHEN
                p.rating_ts BETWEEN TIMESTAMP_SUB(
                    r.first_redemption_ts, INTERVAL 3 DAY
                )
                AND r.first_redemption_ts
                THEN p.theo_amount
            ELSE 0
        END) AS baseline_theo
    FROM redemptions r
    LEFT JOIN player_play p ON r.sk_player_id = p.sk_player_id
    GROUP BY 1, 2, 3, 4
)

SELECT
    sk_campaign_id,
    sk_player_id,
    is_redeemed,
    total_offer_amount,
    post_campaign_theo,
    baseline_theo,
    -- Core Business Metrics defined in one place
    (post_campaign_theo - baseline_theo) AS incremental_theo,
    SAFE_DIVIDE(total_offer_amount, post_campaign_theo) AS reinvestment_rate
FROM performance_calc
