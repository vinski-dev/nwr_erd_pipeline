

SELECT
    sk_player_id,
    cms_player_id,
    member_no,
    first_name,
    last_name,
    dob,
    tier,
    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,
    CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current
FROM `nwr-data-platform`.`silver`.`dim_players_snapshot`