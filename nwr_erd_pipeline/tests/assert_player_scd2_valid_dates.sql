select
    player_sk,
    valid_from,
    valid_to
from {{ ref('dim_players') }}
where valid_from >= valid_to
