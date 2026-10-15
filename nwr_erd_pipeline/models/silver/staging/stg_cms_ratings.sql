WITH source AS (
    SELECT * FROM {{ source('bronze', 'cms_ratings') }}
)
SELECT
    {{ dbt_utils.generate_surrogate_key(['cms_player_id', 'rating_ts', 'game_type']) }} AS sk_rating_id,
    CAST(cms_player_id AS STRING) AS cms_player_id,
    CAST(rating_ts AS TIMESTAMP) AS rating_ts,
    CAST(game_type AS STRING) AS game_type,
    CAST(coin_in AS FLOAT64) AS coin_in,
    CAST(house_edge AS FLOAT64) AS house_edge,
    CAST(_loaded_at AS TIMESTAMP) AS source_loaded_at
FROM source