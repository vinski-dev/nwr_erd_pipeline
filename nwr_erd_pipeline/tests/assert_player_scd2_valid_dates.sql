select
    sk_player_id,
    valid_from,
    valid_to
from {{ ref('dim_players') }}
where valid_from >= valid_to
