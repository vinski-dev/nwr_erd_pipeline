
{% snapshot dim_players_snapshot %}

{{ config(
    target_schema='silver',
    unique_key='sk_player_id',
    strategy='check',
    check_cols=['tier', 'last_name', 'first_name']
) }}

SELECT * FROM {{ ref('int_player_identity_map') }}

{% endsnapshot %}