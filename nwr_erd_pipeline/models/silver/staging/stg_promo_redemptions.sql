WITH source AS (
    SELECT * FROM {{ source('bronze', 'promo_redemptions') }}
)
SELECT
    {{ dbt_utils.generate_surrogate_key(['member_no', 'campaign_id', 'redemption_ts']) }} AS sk_redemption_id,
    CAST(campaign_id AS STRING) AS campaign_id,
    CAST(member_no AS STRING) AS member_no,
    CAST(redemption_ts AS TIMESTAMP) AS redemption_ts,
    CAST(offer_amount AS FLOAT64) AS offer_amount,
    CAST(_loaded_at AS TIMESTAMP) AS source_loaded_at
FROM source