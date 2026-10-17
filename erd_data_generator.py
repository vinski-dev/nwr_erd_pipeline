import datetime
import numpy as np
import pandas as pd
from faker import Faker
from google.cloud import bigquery

# Initialize Faker and seeds for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)


def generate_and_load_bronze_data(dataset_id="bronze", num_profiles=1000, num_ratings=5000, num_redemptions=1500):
    load_timestamp = pd.Timestamp.now()

    print("Generating synthetic data...")

    # 1. Generate Base PII Profiles (The "True" Humans) - including email
    base_profiles = pd.DataFrame(
        [
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "dob": fake.date_of_birth(minimum_age=21, maximum_age=80),
            }
            for _ in range(num_profiles)
        ]
    )

    # 2. Build bronze.cms_players (80% of base profiles)
    cms_players = base_profiles.sample(frac=0.8, random_state=1).assign(
        cms_player_id=lambda x: ["CMS" + str(i).zfill(5) for i in range(len(x))],
        _loaded_at=load_timestamp,
    )[["cms_player_id", "first_name", "last_name", "email", "dob", "_loaded_at"]]

    # 3. Build bronze.loyalty_members (70% of base profiles - creating intentional overlap)
    loyalty_members = base_profiles.sample(frac=0.7, random_state=2).assign(
        member_no=lambda x: ["LOY" + str(i).zfill(5) for i in range(len(x))],
        tier=lambda x: np.random.choice(
            ["Classic", "Silver", "Gold", "Platinum"], size=len(x), p=[0.5, 0.3, 0.15, 0.05]
        ),
        enroll_date=lambda x: [fake.date_between(start_date="-5y", end_date="today") for _ in range(len(x))],
        _loaded_at=load_timestamp,
    )[
        [
            "member_no",
            "first_name",
            "last_name",
            "email",
            "dob",
            "tier",
            "enroll_date",
            "_loaded_at",
        ]
    ]

    # 4. Build bronze.cms_ratings (Strictly raw telemetry, no theo calculations)
    ratings = pd.DataFrame({"cms_player_id": np.random.choice(cms_players["cms_player_id"], size=num_ratings)}).assign(
        rating_ts=lambda x: [fake.date_time_between(start_date="-30d", end_date="now") for _ in range(len(x))],
        game_type=lambda x: np.random.choice(
            ["Slots", "Baccarat", "Blackjack", "Roulette"],
            size=len(x),
            p=[0.7, 0.1, 0.1, 0.1],
        ),
        coin_in=lambda x: np.round(np.random.uniform(50, 5000, len(x)), 2),
        house_edge=lambda x: np.where(x["game_type"] == "Slots", 0.08, 0.015),
        _loaded_at=load_timestamp,
    )[
        [
            "cms_player_id",
            "rating_ts",
            "game_type",
            "coin_in",
            "house_edge",
            "_loaded_at",
        ]
    ]

    # 5. Build bronze.promo_redemptions
    redemptions = pd.DataFrame(
        {"member_no": np.random.choice(loyalty_members["member_no"], size=num_redemptions)}
    ).assign(
        campaign_id=lambda x: np.random.choice(["CMP_001", "CMP_002", "CMP_003", "CMP_004"], size=len(x)),
        redemption_ts=lambda x: [fake.date_time_between(start_date="-30d", end_date="now") for _ in range(len(x))],
        offer_amount=lambda x: np.round(np.random.uniform(10, 250, len(x)), 2),
        _loaded_at=load_timestamp,
    )[
        ["campaign_id", "member_no", "redemption_ts", "offer_amount", "_loaded_at"]
    ]

    # Initialize BigQuery client
    client = bigquery.Client()
    tables = {
        "cms_players": cms_players,
        "loyalty_members": loyalty_members,
        "cms_ratings": ratings,
        "promo_redemptions": redemptions,
    }

    print(f"Loading data directly into BigQuery dataset `{client.project}.{dataset_id}`...")

    for table_name, df in tables.items():
        table_id = f"{client.project}.{dataset_id}.{table_name}"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")  # Replaces the table data on each run
        try:
            job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()  # Wait for the BQ job to complete
            print(f"Successfully loaded {len(df)} rows into {table_id}")
        except Exception as e:
            print(f"ERROR loading {table_id}: {e}")


if __name__ == "__main__":
    generate_and_load_bronze_data()
