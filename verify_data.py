import pandas as pd
import os

file_path = r'd:\Desktop\eco-health-ai\data\daily_patient_admissions_2019_2024.csv'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    df = pd.read_csv(file_path)
    print(f"Total Records: {len(df)}")
    
    # Check Hospitals
    unique_hospitals = df['hospital_id'].unique()
    print(f"Unique Hospitals Found: {len(unique_hospitals)}")
    print("Hospital IDs:")
    for h in unique_hospitals:
        print(f" - {h}")
        
    # Check AQI
    print("\nAQI Stats:")
    print(f"Non-Null Count: {df['avg_aqi'].count()}")
    print(f"Mean AQI: {df['avg_aqi'].mean()}")
    print(f"Min AQI: {df['avg_aqi'].min()}")
    print(f"Max AQI: {df['avg_aqi'].max()}")
    
    # Check for default values (assuming 100 is default if logic failed)
    default_count = df[df['avg_aqi'] == 100].shape[0]
    print(f"Rows with AQI=100 (Potential Default): {default_count}")
