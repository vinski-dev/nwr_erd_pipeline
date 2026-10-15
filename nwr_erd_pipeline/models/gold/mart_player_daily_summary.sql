{{ config(materialized='table') }}

WITH daily_play AS (
    SELECT
        sk_player_id,
        CAST(rating_ts AS DATE) AS date_day,
        SUM(coin_in) AS daily_coin_in,
        SUM(theo_amount) AS daily_theo
    FROM {{ ref('fct_ratings') }}
    GROUP BY 1, 2
),

lagged_play AS (
    SELECT
        date_day,
        sk_player_id,
        daily_coin_in,
        daily_theo,
        -- Window function to find the previous date of play
        LAG(date_day)
            OVER (PARTITION BY sk_player_id ORDER BY date_day)
            AS previous_play_date
    FROM daily_play
)

SELECT
    p.date_day,
    p.sk_player_id,
    d.tier,
    p.daily_coin_in,
    p.daily_theo,
    -- Calculate days since last play for activity tracking
    DATE_DIFF(p.date_day, p.previous_play_date, DAY) AS days_since_last_play,
    -- Boolean flag for quick BI filtering on active players
    CASE
        WHEN DATE_DIFF(CURRENT_DATE(), p.date_day, DAY) <= 30 THEN TRUE ELSE
            FALSE
    END AS is_active_30d
FROM lagged_play p
JOIN {{ ref('dim_players') }} d ON p.sk_player_id = d.sk_player_id
