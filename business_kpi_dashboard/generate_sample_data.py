"""
generate_sample_data.py
------------------------
Generates a realistic sample sales dataset for the Business KPI Dashboard.
Run this once to create data/sales_data.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---- Configuration ----
NUM_ROWS = 3000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

regions = ["North", "South", "East", "West", "Central"]
products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
feedback_samples = [
    "Excellent service, very satisfied with the product quality.",
    "The delivery was late and support was not helpful.",
    "Great value for money, will buy again.",
    "Average experience, nothing special.",
    "Terrible experience, product was damaged.",
    "Loved it! Exceeded my expectations.",
    "Customer support resolved my issue quickly, thank you.",
    "Not worth the price, quite disappointed.",
    "Good quality but shipping took too long.",
    "Fantastic product, highly recommend to others.",
]

# ---- Generate random dates ----
date_range_days = (END_DATE - START_DATE).days
random_days = np.random.randint(0, date_range_days, NUM_ROWS)
dates = [START_DATE + timedelta(days=int(d)) for d in random_days]

# ---- Generate customer IDs (simulate growth: more customers over time) ----
customer_ids = np.random.randint(1000, 1000 + NUM_ROWS // 2, NUM_ROWS)

# ---- Build dataframe ----
df = pd.DataFrame({
    "Date": dates,
    "CustomerID": customer_ids,
    "Region": np.random.choice(regions, NUM_ROWS, p=[0.25, 0.2, 0.2, 0.2, 0.15]),
    "Product": np.random.choice(products, NUM_ROWS),
})

# Revenue influenced by product and some randomness/seasonality
base_price = df["Product"].map({
    "Product A": 120, "Product B": 80, "Product C": 200,
    "Product D": 150, "Product E": 60
})
quantity = np.random.randint(1, 15, NUM_ROWS)
seasonality = 1 + 0.15 * np.sin(2 * np.pi * pd.to_datetime(df["Date"]).dt.month / 12)

df["Quantity"] = quantity
df["Revenue"] = (base_price * quantity * seasonality * np.random.uniform(0.85, 1.15, NUM_ROWS)).round(2)
df["Cost"] = (df["Revenue"] * np.random.uniform(0.45, 0.7, NUM_ROWS)).round(2)
df["Profit"] = (df["Revenue"] - df["Cost"]).round(2)

# Add customer feedback text (for sentiment analysis with TextBlob)
df["Feedback"] = np.random.choice(feedback_samples, NUM_ROWS)

df = df.sort_values("Date").reset_index(drop=True)
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

df.to_csv("data/sales_data.csv", index=False)
print(f"Sample data generated: data/sales_data.csv ({len(df)} rows)")
