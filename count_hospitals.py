import pandas as pd
import os

file_path = r"d:\Desktop\eco-health-ai\real_data\synthetic_mumbai_monthly_full (1).csv"

try:
    df = pd.read_csv(file_path)
    unique_ids = df['hospital_id'].unique()
    print(f"Count: {len(unique_ids)}")
    print(f"IDs: {list(unique_ids)}")
except Exception as e:
    print(f"Error: {e}")
