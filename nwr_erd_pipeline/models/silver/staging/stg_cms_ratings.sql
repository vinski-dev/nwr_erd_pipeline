select
    cms_player_id,
    cast(rating_ts as timestamp) as rating_ts,

    game_type,
    cast(coin_in as numeric) as coin_in,
        
    cast(house_edge as numeric) as house_edge,
    _loaded_at
from {{ source('bronze', 'cms_ratings') }}
