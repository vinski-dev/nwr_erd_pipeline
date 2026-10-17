{{ config(
    materialized='table',
    partition_by={
      "field": "play_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=['player_sk']
) }}

WITH daily_aggregate AS (
    SELECT
        player_sk,
        CAST(rating_ts AS DATE) AS play_date,
        SUM(coin_in) AS total_coin_in,
        SUM(theoretical_win) AS total_theoretical_win
    FROM {{ ref('fct_ratings') }}
    GROUP BY
        player_sk,
        CAST(rating_ts AS DATE)
),

player_dim AS (
    SELECT
        player_sk,
        first_name,
        last_name,
        loyalty_tier
    FROM {{ ref('dim_players') }}
    -- Safely ensure 1 row per player_sk in case dim_players holds multiple rows
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY player_sk
        ORDER BY loyalty_tier DESC
    ) = 1
)

SELECT
    a.player_sk,
    a.play_date,
    d.first_name,
    d.last_name,
    d.loyalty_tier,
    a.total_coin_in,
    a.total_theoretical_win
FROM daily_aggregate a
LEFT JOIN player_dim d
    ON a.player_sk = d.player_sk
