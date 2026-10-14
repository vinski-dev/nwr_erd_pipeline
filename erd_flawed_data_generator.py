import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
NUM_PLAYERS = 500
DAYS_OF_HISTORY = 90
START_DATE = datetime.today() - timedelta(days=DAYS_OF_HISTORY)
OUTPUT_DIR = "./flawed_erd_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating Base Identities...")
# Hidden underlying guest list to simulate the disconnected systems
guests = pd.DataFrame(
    {
        "guest_id": range(1, NUM_PLAYERS + 1),
        "cms_player_id": [f"CMS_{str(i).zfill(5)}" for i in range(1, NUM_PLAYERS + 1)],
        "member_no": [f"LOY_{str(i+1000).zfill(5)}" for i in range(1, NUM_PLAYERS + 1)],
    }
)

# ==========================================
# 1. BRONZE LAYER (Flawed Load Computations)
# ==========================================
print("Generating Bronze Layer...")

# bronze.loyalty_members
tiers = ["Bronze", "Silver", "Gold", "Platinum"]
bronze_loyalty_members = guests[["member_no"]].copy()
bronze_loyalty_members["tier"] = np.random.choice(tiers, NUM_PLAYERS, p=[0.6, 0.25, 0.1, 0.05])
bronze_loyalty_members["dob"] = [
    START_DATE - timedelta(days=random.randint(18 * 365, 70 * 365)) for _ in range(NUM_PLAYERS)
]
bronze_loyalty_members["enroll_date"] = [
    START_DATE - timedelta(days=random.randint(1, 1000)) for _ in range(NUM_PLAYERS)
]

# bronze.cms_ratings (Flaw: Computing theo & active flag on load)
num_ratings = NUM_PLAYERS * 20
rating_dates = [
    START_DATE + timedelta(days=random.randint(0, DAYS_OF_HISTORY), hours=random.randint(0, 23))
    for _ in range(num_ratings)
]
bronze_cms_ratings = pd.DataFrame(
    {
        "cms_player_id": np.random.choice(guests["cms_player_id"], num_ratings),
        "game_type": np.random.choice(["Slots", "Table"], num_ratings),
        "coin_in": np.random.uniform(50, 5000, num_ratings).round(2),
        "house_edge": np.random.choice([0.05, 0.12, 0.15], num_ratings),
        "rating_ts": rating_dates,
    }
)
# FLAW: Transformations happening in Bronze landing
bronze_cms_ratings["theo_amount"] = (bronze_cms_ratings["coin_in"] * bronze_cms_ratings["house_edge"]).round(2)
bronze_cms_ratings["is_active_flag"] = 1

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
    }
)

# ==========================================
# 2. SILVER LAYER (Destructive dimensions & mixed grains)
# ==========================================
print("Generating Silver Layer...")

# silver.dim_player (Flaw: Truncate and reload single current value, losing history)
# We mock a cross-reference join that somehow happened in ETL
silver_dim_player = pd.merge(guests[["cms_player_id", "member_no"]], bronze_loyalty_members, on="member_no")
silver_dim_player = silver_dim_player[["cms_player_id", "tier"]]

# silver.player_monthly_theo
bronze_cms_ratings["month"] = bronze_cms_ratings["rating_ts"].dt.to_period("M").astype(str)
silver_player_monthly_theo = bronze_cms_ratings.groupby(["cms_player_id", "month"])["theo_amount"].sum().reset_index()

# silver.fact_play (Flaw: Mixed grain fact table)
# Grain 1: Individual Ratings
ratings_grain = bronze_cms_ratings[["cms_player_id", "rating_ts", "coin_in", "theo_amount"]].copy()
ratings_grain.rename(columns={"rating_ts": "event_date"}, inplace=True)
ratings_grain["record_type"] = "RATING"

# Grain 2: Daily Summaries
daily_grain = bronze_cms_ratings.copy()
daily_grain["event_date"] = daily_grain["rating_ts"].dt.normalize()
daily_grain = daily_grain.groupby(["cms_player_id", "event_date"])[["coin_in", "theo_amount"]].sum().reset_index()
daily_grain["record_type"] = "DAILY_SUMMARY"

silver_fact_play = pd.concat([ratings_grain, daily_grain], ignore_index=True)

# ==========================================
# 3. GOLD LAYER (Detached logic & hardcoded BI models)
# ==========================================
print("Generating Gold Layer...")

# gold.exec_daily_dashboard
daily_totals = (
    daily_grain.groupby("event_date")
    .agg(kpi_theo_today=("theo_amount", "sum"), kpi_active_players=("cms_player_id", "nunique"))
    .reset_index()
)
daily_totals.rename(columns={"event_date": "run_date"}, inplace=True)
daily_totals["kpi_theo_mtd"] = daily_totals.groupby(daily_totals["run_date"].dt.to_period("M"))[
    "kpi_theo_today"
].cumsum()
daily_totals["top_segment_name"] = "Gold"  # Hardcoded/flawed aggregation
daily_totals["top_segment_theo"] = daily_totals["kpi_theo_today"] * 0.4
gold_exec_daily_dashboard = daily_totals

# gold.campaign_performance (Flaw: recomputing theo with a different formula in Gold)
gold_campaign_performance = pd.DataFrame(
    {
        "campaign_id": ["CAMP_01", "CAMP_02", "CAMP_03"],
        "total_invited": [5000, 2000, 1000],
        "total_redeemed": bronze_promo_redemptions.groupby("campaign_id").size().values,
    }
)
# FLAW: Formula mismatch. Silver used exact house edge, Gold uses flat 10% assumption.
gold_campaign_performance["recomputed_theo_generated"] = gold_campaign_performance["total_redeemed"] * 150 * 0.10

# ==========================================
# EXPORT
# ==========================================
datasets = {
    "bronze_cms_ratings": bronze_cms_ratings.drop(columns=["month"]),
    "bronze_loyalty_members": bronze_loyalty_members,
    "bronze_promo_redemptions": bronze_promo_redemptions,
    "silver_dim_player": silver_dim_player,
    "silver_player_monthly_theo": silver_player_monthly_theo,
    "silver_fact_play": silver_fact_play,
    "gold_exec_daily_dashboard": gold_exec_daily_dashboard,
    "gold_campaign_performance": gold_campaign_performance,
}

for name, df in datasets.items():
    df.to_csv(f"{OUTPUT_DIR}/{name}.csv", index=False)

print(f"Generation complete. Data saved to {OUTPUT_DIR}")
