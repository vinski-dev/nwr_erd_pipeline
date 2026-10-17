{{ config(severity = 'error') }}

WITH silver_summary AS (
    SELECT
        campaign_id,
        SUM(offer_amount) AS silver_offer_amount
    FROM {{ ref('fct_campaign_redemption') }}
    GROUP BY campaign_id
),

gold_summary AS (
    SELECT
        campaign_id,
        SUM(offer_amount) AS gold_offer_amount
    FROM {{ ref('mart_campaign_performance') }}
    GROUP BY campaign_id
)

SELECT
    COALESCE(s.campaign_id, g.campaign_id) AS campaign_id,
    s.silver_offer_amount,
    g.gold_offer_amount
FROM silver_summary AS s
FULL OUTER JOIN gold_summary AS g
    ON s.campaign_id = g.campaign_id
WHERE COALESCE(s.silver_offer_amount, 0) != COALESCE(g.gold_offer_amount, 0)
