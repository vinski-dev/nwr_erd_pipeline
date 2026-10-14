WITH daily_kpi AS (
    SELECT * FROM {{ ref('fct_daily_player_kpi') }}
),

daily_summary AS (
    SELECT
        date_day AS run_date,
        SUM(daily_theo) AS kpi_theo_today,
        COUNT(DISTINCT IF(is_active_flag, player_sk, NULL)) AS kpi_active_players
    FROM daily_kpi
    GROUP BY 1
)

SELECT
    run_date,
    kpi_theo_today,
    -- Month-to-date calculation using window functions
    SUM(kpi_theo_today) OVER (
        PARTITION BY EXTRACT(YEAR FROM run_date), EXTRACT(MONTH FROM run_date)
        ORDER BY run_date
    ) AS kpi_theo_mtd,
    kpi_active_players
FROM daily_summary