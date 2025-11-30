"""
Master Training Script
Trains all ML models using synthetic data
"""

import sys
import os
from datetime import datetime
import pandas as pd

# Add project root to path
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.surge_predictor import SurgePredictorModel
from src.models.resource_forecaster import ResourceForecaster


def main():
    print("=" * 70)
    print("ECO-HEALTH AI - MODEL TRAINING PIPELINE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load patient admission data (contains all merged external data)
    print("\n► Loading patient admission data...")
    try:
        patient_df = pd.read_csv("data/patient_admissions.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        print(f"✓ Loaded {len(patient_df):,} patient admission records")
    except FileNotFoundError:
        print("✗ Error: patient_admissions.csv not found!")
        print("  Please run data_generators/generate_all.py first")
        return
    
    # Train Surge Prediction Model
    print("\n" + "=" * 70)
    print("TRAINING SURGE PREDICTION MODEL")
    print("=" * 70)
    
    surge_model = SurgePredictorModel()
    X, y, processed_df = surge_model.prepare_data(patient_df)
    metrics = surge_model.train(X, y)
    surge_model.save()
    
    # Train Resource Forecasting Model
    print("\n" + "=" * 70)
    print("TRAINING RESOURCE FORECASTING MODEL")
    print("=" * 70)
    
    resource_forecaster = ResourceForecaster()
    resource_df = resource_forecaster.prepare_training_data(patient_df)
    resource_forecaster.train(resource_df)
    resource_forecaster.save()
    
    # Summary
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    
    print("\n✓ Surge Predictor:")
    print(f"    Accuracy: {metrics['accuracy']*100:.1f}%")
    print(f"    R² Score: {metrics['r2']:.3f}")
    print(f"    MAE: {metrics['mae']:.2f} patients")
    
    print("\n✓ Resource Forecaster: Trained for 9 resource types")
    
    print(f"\n✓ All models saved to 'saved_models/' directory")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Models are ready for deployment!")


if __name__ == "__main__":
    main()
