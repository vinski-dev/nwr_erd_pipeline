import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
NUM_PLAYERS = 500
DAYS_OF_HISTORY = 90
START_DATE = datetime.today() - timedelta(days=DAYS_OF_HISTORY)
OUTPUT_DIR = "./optimized_erd_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating Base Identities...")
# Hidden underlying truth mapping
guests = pd.DataFrame(
    {
        "player_sk": range(1, NUM_PLAYERS + 1),  # Surrogate key to be generated in Silver
        "cms_player_id": [f"CMS_{str(i).zfill(5)}" for i in range(1, NUM_PLAYERS + 1)],
        "member_no": [f"LOY_{str(i+1000).zfill(5)}" for i in range(1, NUM_PLAYERS + 1)],
    }
)

# ==========================================
# 1. BRONZE LAYER (Raw, Append-Only)
# ==========================================
print("Generating Bronze Layer...")

# bronze.loyalty_members (No computations)
bronze_loyalty_members = guests[["member_no"]].copy()
bronze_loyalty_members["tier"] = np.random.choice(["Bronze", "Silver", "Gold"], NUM_PLAYERS, p=[0.7, 0.2, 0.1])
bronze_loyalty_members["dob"] = [
    START_DATE - timedelta(days=random.randint(18 * 365, 70 * 365)) for _ in range(NUM_PLAYERS)
]
bronze_loyalty_members["enroll_date"] = [
    START_DATE - timedelta(days=random.randint(1, 1000)) for _ in range(NUM_PLAYERS)
]
bronze_loyalty_members["_loaded_at"] = datetime.now()

# bronze.loyalty_cms_xref (Crucial for identity resolution)
bronze_loyalty_cms_xref = guests[["member_no", "cms_player_id"]].copy()

# bronze.cms_ratings (Raw, no theo calculation)
num_ratings = NUM_PLAYERS * 20
rating_dates = [
    START_DATE + timedelta(days=random.randint(0, DAYS_OF_HISTORY), hours=random.randint(0, 23))
    for _ in range(num_ratings)
]
bronze_cms_ratings = pd.DataFrame(
    {
        "cms_rating_id": range(1, num_ratings + 1),
        "cms_player_id": np.random.choice(guests["cms_player_id"], num_ratings),
        "game_type": np.random.choice(["Slots", "Table"], num_ratings),
        "coin_in": np.random.uniform(50, 5000, num_ratings).round(2),
        "house_edge": np.random.choice([0.05, 0.12, 0.15], num_ratings),
        "rating_ts": rating_dates,
        "_loaded_at": datetime.now(),
    }
)

# bronze.promo_redemptions
num_redemptions = int(NUM_PLAYERS * 5)
bronze_promo_redemptions = pd.DataFrame(
    {
        "redemption_id": range(1, num_redemptions + 1),
        "campaign_id": np.random.choice(["CAMP_01", "CAMP_02", "CAMP_03"], num_redemptions),
        "member_no": np.random.choice(guests["member_no"], num_redemptions),
        "redeemed_ts": [
            START_DATE + timedelta(days=random.randint(0, DAYS_OF_HISTORY)) for _ in range(num_redemptions)
        ],
        "_loaded_at": datetime.now(),
    }
)

# ==========================================
# 2. SILVER LAYER (Conformed, Dimensional)
# ==========================================
# print("Generating Silver Layer...")

# # silver.dim_campaign
# silver_dim_campaign = pd.DataFrame(
#     {
#         "campaign_sk": [1, 2, 3],
#         "campaign_id": ["CAMP_01", "CAMP_02", "CAMP_03"],
#         "campaign_name": ["Spring Fling", "High Roller Weekend", "Slot Tournament"],
#         "total_invited": [5000, 2000, 1000],  # Mock static dimension attribute
#     }
# )

# # silver.dim_player (SCD Type 2 Implementation)
# dim_player_base = pd.merge(guests, bronze_loyalty_members, on="member_no")
# dim_player_base["dbt_valid_from"] = dim_player_base["enroll_date"]
# dim_player_base["dbt_valid_to"] = pd.to_datetime("2099-12-31")
# dim_player_base["is_current"] = True

# # Simulate some tier upgrades to demonstrate SCD2
# upgraded_players = dim_player_base.sample(frac=0.1).copy()
# upgrade_date = START_DATE + timedelta(days=45)
# # Expire old records
# dim_player_base.loc[dim_player_base["player_sk"].isin(upgraded_players["player_sk"]), "dbt_valid_to"] = upgrade_date
# dim_player_base.loc[dim_player_base["player_sk"].isin(upgraded_players["player_sk"]), "is_current"] = False
# # Create new active records
# upgraded_players["tier"] = "Platinum"
# upgraded_players["dbt_valid_from"] = upgrade_date
# upgraded_players["dbt_valid_to"] = pd.to_datetime("2099-12-31")
# upgraded_players["is_current"] = True

# silver_dim_player = (
#     pd.concat([dim_player_base, upgraded_players]).sort_values(["player_sk", "dbt_valid_from"]).reset_index(drop=True)
# )

# # silver.fct_rating (Calculate Theo here, assign player_sk)
# silver_fct_rating = pd.merge(bronze_cms_ratings, guests[["cms_player_id", "player_sk"]], on="cms_player_id", how="left")
# silver_fct_rating["rating_sk"] = silver_fct_rating["cms_rating_id"]
# silver_fct_rating["theo_amount"] = (silver_fct_rating["coin_in"] * silver_fct_rating["house_edge"]).round(
#     2
# )  # Calculated ONCE
# silver_fct_rating = silver_fct_rating[["rating_sk", "player_sk", "rating_ts", "game_type", "coin_in", "theo_amount"]]

# # silver.fct_campaign_redemption
# silver_fct_campaign_redemption = pd.merge(
#     bronze_promo_redemptions, guests[["member_no", "player_sk"]], on="member_no", how="left"
# )
# silver_fct_campaign_redemption = pd.merge(
#     silver_fct_campaign_redemption, silver_dim_campaign[["campaign_id", "campaign_sk"]], on="campaign_id", how="left"
# )
# silver_fct_campaign_redemption["redemption_sk"] = silver_fct_campaign_redemption["redemption_id"]
# silver_fct_campaign_redemption = silver_fct_campaign_redemption[
#     ["redemption_sk", "campaign_sk", "player_sk", "redeemed_ts"]
# ]

# # ==========================================
# # 3. GOLD LAYER (Aggregated, Business-Level)
# # ==========================================
# print("Generating Gold Layer...")

# # gold.fct_daily_player_kpi (Snapshot Fact - safe for BI)
# silver_fct_rating["date_day"] = silver_fct_rating["rating_ts"].dt.normalize()
# gold_fct_daily_player_kpi = (
#     silver_fct_rating.groupby(["date_day", "player_sk"])
#     .agg(daily_theo=("theo_amount", "sum"), daily_coin_in=("coin_in", "sum"))
#     .reset_index()
# )

# # Calculate 30-day rolling theo using pandas (simulating Snowflake window functions)
# gold_fct_daily_player_kpi = gold_fct_daily_player_kpi.sort_values(by=["player_sk", "date_day"])
# gold_fct_daily_player_kpi = gold_fct_daily_player_kpi.set_index("date_day")
# gold_fct_daily_player_kpi["rolling_30d_theo"] = (
#     gold_fct_daily_player_kpi.groupby("player_sk")["daily_theo"].rolling("30D").sum().reset_index(level=0, drop=True)
# )
# gold_fct_daily_player_kpi = gold_fct_daily_player_kpi.reset_index()
# gold_fct_daily_player_kpi["is_active_flag"] = np.where(gold_fct_daily_player_kpi["rolling_30d_theo"] > 0, True, False)

# # gold.mart_campaign_performance (DRY - joins to silver facts instead of guessing)
# campaign_redemptions = silver_fct_campaign_redemption.groupby("campaign_sk").size().reset_index(name="total_redeemed")
# gold_mart_campaign_performance = pd.merge(
#     silver_dim_campaign, campaign_redemptions, on="campaign_sk", how="left"
# ).fillna(0)
# gold_mart_campaign_performance["redemption_rate"] = (
#     gold_mart_campaign_performance["total_redeemed"] / gold_mart_campaign_performance["total_invited"]
# ).round(4)

# # Mocking incremental theo (in SQL this would be a join between fct_redemption and fct_rating based on time windows)
# # Here we just randomly allocate a portion of total theo to campaigns to illustrate the column exists
# total_theo = silver_fct_rating["theo_amount"].sum()
# gold_mart_campaign_performance["incremental_theo_generated"] = (
#     gold_mart_campaign_performance["total_redeemed"] * 125
# ).round(2)

# # gold.mart_exec_daily (Clean BI presentation)
# gold_mart_exec_daily = (
#     gold_fct_daily_player_kpi.groupby("date_day")
#     .agg(kpi_theo_today=("daily_theo", "sum"), kpi_active_players=("player_sk", "nunique"))
#     .reset_index()
# )
# gold_mart_exec_daily["kpi_theo_mtd"] = gold_mart_exec_daily.groupby(gold_mart_exec_daily["date_day"].dt.to_period("M"))[
#     "kpi_theo_today"
# ].cumsum()

# ==========================================
# EXPORT
# ==========================================
datasets = {
    "bronze_cms_ratings": bronze_cms_ratings,
    "bronze_loyalty_members": bronze_loyalty_members,
    "bronze_loyalty_cms_xref": bronze_loyalty_cms_xref,
    "bronze_promo_redemptions": bronze_promo_redemptions,
    # "silver_dim_player": silver_dim_player,
    # "silver_dim_campaign": silver_dim_campaign,
    # "silver_fct_rating": silver_fct_rating,
    # "silver_fct_campaign_redemption": silver_fct_campaign_redemption,
    # "gold_fct_daily_player_kpi": gold_fct_daily_player_kpi,
    # "gold_mart_campaign_performance": gold_mart_campaign_performance,
    # "gold_mart_exec_daily": gold_mart_exec_daily,
}

for name, df in datasets.items():
    df.to_csv(f"{OUTPUT_DIR}/{name}.csv", index=False)

print(f"Generation complete. Data saved to {OUTPUT_DIR}")
