
  
    

    create or replace table `nwr-data-platform`.`dbt_erd_nwr`.`fct_daily_player_kpi`
      
    partition by date_day
    cluster by player_sk

    
    OPTIONS()
    as (
      

WITH daily_aggregates AS (
    SELECT
        EXTRACT(DATE FROM rating_ts) AS date_day,
        player_sk,
        SUM(coin_in) AS daily_coin_in,
        SUM(theo_amount) AS daily_theo
    FROM `nwr-data-platform`.`dbt_erd_nwr`.`fct_ratings`
    WHERE player_sk IS NOT NULL
    GROUP BY 1, 2
),

rolling_metrics AS (
    SELECT
        date_day,
        player_sk,
        daily_coin_in,
        daily_theo,
        -- BigQuery optimized rolling 30-day sum using UNIX_DATE
        SUM(daily_theo) OVER (
            PARTITION BY player_sk
            ORDER BY UNIX_DATE(date_day)
            RANGE BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS rolling_30d_theo
    FROM daily_aggregates
)

SELECT
    date_day,
    player_sk,
    daily_coin_in,
    daily_theo,
    rolling_30d_theo,
    -- Player is considered "Active" if they generated theo in the last 30 days
    IF(rolling_30d_theo > 0, TRUE, FALSE) AS is_active_flag
FROM rolling_metrics
    );
  