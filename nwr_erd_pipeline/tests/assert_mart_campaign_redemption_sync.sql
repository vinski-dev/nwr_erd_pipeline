select
    m.sk_campaign_id,
    m.sk_player_id,
    m.is_redeemed
from {{ ref('mart_campaign_performance') }} m
left join {{ ref('fct_campaign_redemption') }} r
  on m.sk_campaign_id = r.sk_campaign_id
  and m.sk_player_id = r.sk_player_id
where m.is_redeemed = true
  and r.sk_redemption_id is null