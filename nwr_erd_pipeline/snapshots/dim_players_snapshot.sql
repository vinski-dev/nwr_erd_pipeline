
{% snapshot snp_players %}

{{
    config(
        target_database='nwr-data-platform',
        target_schema='snapshots',
        unique_key='player_natural_key',
        strategy='check',
        check_cols=['email', 'first_name', 'last_name', 'loyalty_tier']
    )
}}

select * from {{ ref('int_player_identity_map') }}

{% endsnapshot %}