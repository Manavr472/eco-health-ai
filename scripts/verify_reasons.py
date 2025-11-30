import pandas as pd
try:
    df = pd.read_csv(r'd:\Desktop\eco-health-ai\data\daily_patient_admissions_2019_2024.csv')
    print(f"Total Rows: {len(df)}")
    print("Sample Surge Reasons:")
    print(df[['date', 'surge_multiplier', 'surge_reasons']].head(10))
    
    # Check for unique reasons to verify AI generation (vs static strings)
    unique_reasons = df['surge_reasons'].nunique()
    print(f"\nUnique Surge Reasons Count: {unique_reasons}")
    
    # Check for specific AI-like phrases
    ai_phrases = df[df['surge_reasons'].str.len() > 20]['surge_reasons'].head(5).tolist()
    print("\nLong/Complex Reasons (Potential AI):")
    for p in ai_phrases:
        print(f" - {p}")
        
except Exception as e:
    print(f"Error: {e}")
