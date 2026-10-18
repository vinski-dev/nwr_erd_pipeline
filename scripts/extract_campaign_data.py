import pandas as pd
from google.cloud import bigquery


def extract_campaign_data():
    print("Authenticating and fetching from BigQuery...")

    client = bigquery.Client(project="nwr-data-platform", location="US")

    # Query using the actual casino campaign columns
    query = """
        SELECT
            campaign_id,
            SUM(offer_amount) AS total_offer_amount,
            SUM(trip_coin_in) AS total_coin_in,
            SUM(trip_theoretical_win) AS total_theo_win,
            SUM(campaign_net_margin) AS total_net_margin
        FROM
            `nwr-data-platform.dbt_erd_nwr_prod_gold.mart_campaign_performance`
        WHERE
            DATE(redemption_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY
            campaign_id
    """

    print("Executing query...")
    df = client.query(query).to_dataframe()

    print("Processing metrics...")
    (
        df.assign(margin_roi=lambda x: (x["total_net_margin"] / x["total_offer_amount"]).round(2))
        .sort_values(by="margin_roi", ascending=False)
        .to_csv("campaign_summary_failsafe.csv", index=False)
    )

    print("Success! Live data secured locally in campaign_summary_failsafe.csv")


if __name__ == "__main__":
    extract_campaign_data()
