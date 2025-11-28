import pandas as pd
try:
    df = pd.read_csv(r'd:\Desktop\eco-health-ai\real_data\synthetic_mumbai_monthly_full (1).csv')
    print("Unique Hospital IDs:")
    print(df['hospital_id'].unique())
except Exception as e:
    print(f"Error: {e}")
