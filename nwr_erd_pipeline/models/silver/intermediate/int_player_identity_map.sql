-- Inside int_player_identity_map.sql
WITH cms AS (
    SELECT cms_player_id, first_name, last_name, dob FROM {{ ref('stg_cms_players') }}
),
loyalty AS (
    SELECT member_no, first_name, last_name, dob, tier FROM {{ ref('stg_loyalty_members') }}
),
matched AS (
    SELECT
        c.cms_player_id,
        l.member_no,
        COALESCE(c.first_name, l.first_name) AS first_name,
        COALESCE(c.last_name, l.last_name) AS last_name,
        COALESCE(c.dob, l.dob) AS dob,
        l.tier  -- Make sure this is here!
    FROM cms c
    FULL OUTER JOIN loyalty l
        ON c.first_name = l.first_name
        AND c.last_name = l.last_name
        AND c.dob = l.dob
)
SELECT
    {{ dbt_utils.generate_surrogate_key(['first_name', 'last_name', 'dob']) }} AS sk_player_id,
    cms_player_id,
    member_no,
    first_name,
    last_name,
    dob,
    tier -- And make sure it is output here!
FROM matched
