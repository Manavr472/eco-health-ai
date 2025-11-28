"""
Resource Forecasting Model
Forecasts required resources (staff, supplies, beds) based on predicted patient surges
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import STAFF_RATIOS, SUPPLIES_PER_PATIENT


class ResourceForecaster:
    """Forecast healthcare resources based on predicted patient volumes"""
    
    def __init__(self):
        self.models = {}
        
    def _calculate_resource_requirements(self, admissions):
        """Calculate required resources for given admissions"""
        resources = {}
        
        # Staff requirements
        resources['doctors_needed'] = int(np.ceil(admissions * STAFF_RATIOS['doctors']))
        resources['nurses_needed'] = int(np.ceil(admissions * STAFF_RATIOS['nurses']))
        resources['support_staff_needed'] = int(np.ceil(admissions * STAFF_RATIOS['support_staff']))
        
        # Supply requirements
        resources['ppe_kits'] = int(admissions * SUPPLIES_PER_PATIENT['ppe_kits'])
        resources['oxygen_liters'] = int(admissions * SUPPLIES_PER_PATIENT['oxygen_liters'])
        resources['iv_fluids_ml'] = int(admissions * SUPPLIES_PER_PATIENT['iv_fluids_ml'])
        resources['medications_units'] = int(admissions * SUPPLIES_PER_PATIENT['medications_units'])
        resources['bed_linens'] = int(admissions * SUPPLIES_PER_PATIENT['bed_linens'])
        
        # Bed requirements (assuming 70% occupancy target)
        resources['beds_needed'] = int(np.ceil(admissions / 0.7))
        
        return resources
    
    def prepare_training_data(self, patient_df):
        """Prepare training data from historical patient admissions"""
        print("Preparing resource forecasting training data...")
        
        data = []
        for _, row in patient_df.iterrows():
            admissions = row['total_admissions']
            resources = self._calculate_resource_requirements(admissions)
            
            data.append({
                'date': row['date'],
                'hospital_id': row['hospital_id'],
                'total_admissions': admissions,
                'surge_multiplier': row['surge_multiplier'],
                'respiratory_admissions': row['respiratory_admissions'],
                'waterborne_admissions': row['waterborne_admissions'],
                'heat_related_admissions': row['heat_related_admissions'],
                'trauma_admissions': row['trauma_admissions'],
                **resources
            })
        
        df = pd.DataFrame(data)
        print(f"Prepared {len(df)} resource requirement records")
        
        return df
    
    def train(self, resource_df):
        """Train resource forecasting models"""
        print("\nTraining resource forecasting models...")
        
        # Features for prediction
        features = [
            'total_admissions', 'surge_multiplier',
            'respiratory_admissions', 'waterborne_admissions',
            'heat_related_admissions', 'trauma_admissions'
        ]
        
        # Targets to predict
        targets = [
            'doctors_needed', 'nurses_needed', 'support_staff_needed',
            'ppe_kits', 'oxygen_liters', 'iv_fluids_ml',
            'medications_units', 'bed_linens', 'beds_needed'
        ]
        
        X = resource_df[features]
        
        # Train a model for each resource type
        for target in targets:
            y = resource_df[target]
            
            # Use Linear Regression for interpretability
            model = LinearRegression()
            model.fit(X, y)
            
            # Evaluate
            score = model.score(X, y)
            
            self.models[target] = model
            print(f"  {target}: R² = {score:.3f}")
        
        print("\nResource forecasting models trained successfully!")
    
    def forecast(self, predicted_admissions, surge_multiplier=1.0, 
                 respiratory_pct=0.15, waterborne_pct=0.10, 
                 heat_related_pct=0.05, trauma_pct=0.20):
        """Forecast resources for predicted admissions"""
        
        # Calculate disease distribution
        respiratory = int(predicted_admissions * respiratory_pct)
        waterborne = int(predicted_admissions * waterborne_pct)
        heat_related = int(predicted_admissions * heat_related_pct)
        trauma = int(predicted_admissions * trauma_pct)
        
        # Prepare input features
        X = np.array([[
            predicted_admissions, surge_multiplier,
            respiratory, waterborne, heat_related, trauma
        ]])
        
        # Predict all resources
        forecast = {}
        for resource_name, model in self.models.items():
            predicted_value = model.predict(X)[0]
            forecast[resource_name] = max(0, int(np.round(predicted_value)))
        
        return forecast
    
    def forecast_surge_event(self, baseline_admissions, surge_factor):
        """Forecast resources for a surge event"""
        predicted_admissions = int(baseline_admissions * surge_factor)
        
        # Adjust disease distribution for surge type
        # For simplicity, using default distribution
        forecast = self.forecast(
            predicted_admissions,
            surge_multiplier=surge_factor
        )
        
        # Calculate additional resources needed (vs baseline)
        baseline_resources = self.forecast(baseline_admissions)
        
        additional_resources = {}
        for resource, value in forecast.items():
            additional = value - baseline_resources[resource]
            additional_resources[f'{resource}_additional'] = max(0, additional)
        
        return {
            'forecast': forecast,
            'baseline': baseline_resources,
            'additional': additional_resources,
            'predicted_admissions': predicted_admissions
        }
    
    def save(self, model_dir="saved_models"):
        """Save the trained models"""
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "resource_forecaster.pkl")
        joblib.dump(self.models, model_path)
        
        print(f"\nResource forecasting models saved to {model_dir}/")
    
    def load(self, model_dir="saved_models"):
        """Load trained models"""
        model_path = os.path.join(model_dir, "resource_forecaster.pkl")
        self.models = joblib.load(model_path)
        
        print(f"Resource forecasting models loaded from {model_dir}/")


if __name__ == "__main__":
    # Load patient admission data
    print("Loading patient admission data...")
    patient_df = pd.read_csv("data/patient_admissions.csv")
    patient_df['date'] = pd.to_datetime(patient_df['date'])
    
    # Create and train forecaster
    forecaster = ResourceForecaster()
    resource_df = forecaster.prepare_training_data(patient_df)
    forecaster.train(resource_df)
    
    # Save models
    forecaster.save()
    
    # Example forecast
    print("\n" + "="*70)
    print("Example Forecast for Surge Event")
    print("="*70)
    
    baseline = 150
    surge_factor = 2.0
    
    result = forecaster.forecast_surge_event(baseline, surge_factor)
    
    print(f"\nBaseline admissions: {baseline}")
    print(f"Surge factor: {surge_factor}x")
    print(f"Predicted admissions: {result['predicted_admissions']}")
    
    print("\nStaff Requirements:")
    print(f"  Doctors: {result['forecast']['doctors_needed']} (+{result['additional']['doctors_needed_additional']})")
    print(f"  Nurses: {result['forecast']['nurses_needed']} (+{result['additional']['nurses_needed_additional']})")
    print(f"  Support Staff: {result['forecast']['support_staff_needed']} (+{result['additional']['support_staff_needed_additional']})")
    
    print("\nSupply Requirements:")
    print(f"  PPE Kits: {result['forecast']['ppe_kits']} (+{result['additional']['ppe_kits_additional']})")
    print(f"  Oxygen (liters): {result['forecast']['oxygen_liters']} (+{result['additional']['oxygen_liters_additional']})")
    print(f"  IV Fluids (ml): {result['forecast']['iv_fluids_ml']} (+{result['additional']['iv_fluids_ml_additional']})")
    
    print("\nBed Requirements:")
    print(f"  Beds needed: {result['forecast']['beds_needed']} (+{result['additional']['beds_needed_additional']})")
    
    print("\n" + "="*70)
    print("Resource forecasting complete!")
    print("="*70)
