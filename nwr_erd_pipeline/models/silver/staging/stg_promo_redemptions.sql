select
    campaign_id,
    member_no,
    cast(redemption_ts as timestamp) as redemption_ts,
    cast(offer_amount as numeric) as offer_amount,
    _loaded_at
from {{ source('bronze', 'promo_redemptions') }}