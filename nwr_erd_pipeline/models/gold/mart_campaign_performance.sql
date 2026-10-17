{{ config(
    materialized='table',
    cluster_by=['campaign_id']
) }}

WITH campaign_redemptions AS (
    SELECT *
    FROM {{ ref('fct_campaign_redemption') }}
),

player_daily AS (
    -- Aggregate to strictly 1 row per player_sk + play_date to prevent fan-out
    -- (Note: If your mart_player_daily_summary uses player_master_sk instead of player_sk,
    -- swap player_sk to player_master_sk inside this CTE only!)
    SELECT
        player_sk,
        CAST(play_date AS DATE) AS play_date,
        SUM(total_coin_in) AS total_coin_in,
        SUM(total_theoretical_win) AS total_theoretical_win
    FROM {{ ref('mart_player_daily_summary') }}
    GROUP BY 1, 2
)

SELECT
    c.sk_redemption_id,
    c.sk_campaign_id,
    c.campaign_id,
    c.redemption_date,
    c.player_sk,
    c.cms_player_id,
    c.offer_amount,

    -- Evaluating if the player generated theo on the exact day they redeemed the offer
    COALESCE(pd.total_coin_in, 0) AS trip_coin_in,
    COALESCE(pd.total_theoretical_win, 0) AS trip_theoretical_win,

    -- ROI Calculation
    (COALESCE(pd.total_theoretical_win, 0) - c.offer_amount) AS campaign_net_margin

FROM campaign_redemptions c
LEFT JOIN player_daily pd
    ON c.player_sk = pd.player_sk
    AND CAST(c.redemption_date AS DATE) = pd.play_date