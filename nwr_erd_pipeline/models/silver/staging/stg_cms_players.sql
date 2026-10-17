select
    cms_player_id,
    first_name,
    last_name,
    email,
    cast(dob as date) as dob,
    _loaded_at
from {{ source('bronze', 'cms_players') }}
