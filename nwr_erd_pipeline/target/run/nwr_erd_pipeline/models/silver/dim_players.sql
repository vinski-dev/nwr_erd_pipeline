
  
    

    create or replace table `nwr-data-platform`.`dbt_erd_nwr`.`dim_players`
      
    
    cluster by player_sk

    
    OPTIONS()
    as (
      

WITH loyalty AS (
    SELECT
        member_no,
        tier,
        dob,
        enroll_date
    FROM `nwr-data-platform`.`casino_platform`.`bronze_loyalty_members`
),

xref AS (
    SELECT
        member_no,
        cms_player_id
    FROM `nwr-data-platform`.`casino_platform`.`bronze_loyalty_cms_xref`
)

SELECT
    -- Generate an MD5 string surrogate key using the dbt_utils macro
    to_hex(md5(cast(coalesce(cast(l.member_no as string), '_dbt_utils_surrogate_key_null_') as string))) AS player_sk,
    x.cms_player_id,
    l.member_no,
    l.tier,
    l.dob,
    l.enroll_date,
    CURRENT_TIMESTAMP() AS dbt_updated_at
FROM loyalty l
LEFT JOIN xref x
    ON l.member_no = x.member_no
    );
  