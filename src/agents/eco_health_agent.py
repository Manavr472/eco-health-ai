"""
Eco-Health AI Agent
Core autonomous agent implementing the continuous monitoring and decision-making loop
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import AGENT_CONFIG, BASELINE_DAILY_ADMISSIONS
from src.models.surge_predictor import SurgePredictorModel
from src.models.resource_forecaster import ResourceForecaster
from src.agents.recommendation_engine import RecommendationEngine


class EcoHealthAgent:
    """Autonomous AI agent for hospital surge management"""
    
    def __init__(self):
        self.surge_model = None
        self.resource_forecaster = None
        self.recommendation_engine = RecommendationEngine()
        self.monitoring_active = False
        self.prediction_history = []
        
    def initialize(self, surge_model_path="saved_models", resource_model_path="saved_models"):
        """Initialize the agent with trained models"""
        print("Initializing Eco-Health AI Agent...")
        
        # Load surge prediction model
        self.surge_model = SurgePredictorModel()
        self.surge_model.load(surge_model_path)
        print("✓ Surge prediction model loaded")
        
        # Load resource forecasting model
        self.resource_forecaster = ResourceForecaster()
        self.resource_forecaster.load(resource_model_path)
        print("✓ Resource forecasting model loaded")
        
        print("✓ Recommendation engine initialized")
        print("\nEco-Health AI Agent ready!")
    
    def analyze_current_conditions(self, date, external_data):
        """Analyze current external conditions"""
        # Extract relevant data for the specific date
        date_data = external_data[external_data['date'] == date]
        
        if date_data.empty:
            return None
        
        conditions = {
            'date': date,
            'avg_aqi': date_data['avg_aqi'].mean(),
            'temperature_c': date_data['temperature_c'].mean(),
            'rainfall_mm': date_data['rainfall_mm'].mean(),
            'has_event': date_data['has_event'].any(),
            'active_events': date_data['active_events'].iloc[0] if date_data['has_event'].any() else None,
            'event_severity': date_data['event_severity'].max(),
            'season': date_data['season'].iloc[0] if 'season' in date_data.columns else 'unknown'
        }
        
        return conditions
    
    def predict_patient_surge(self, future_date, external_data, hospital_id=1):
        """Predict patient surge for a future date"""
        
        # This is a simplified version - in production, would use live data feeds
        # For demo, we'll use the historical data as proxy for real-time data
        
        future_data = external_data[
            (external_data['date'] == future_date) &
            (external_data['hospital_id'] == hospital_id)
        ]
        
        if future_data.empty:
            return None
        
        # Extract features (should match training features)
        # For simplicity, using actual data - in production, would engineer features
        
        prediction = {
            'predicted_date': future_date,
            'hospital_id': hospital_id,
            'baseline_admissions': BASELINE_DAILY_ADMISSIONS,
            # In production, would use model.predict() here
            'predicted_admissions': future_data['total_admissions'].iloc[0],
            'surge_multiplier': future_data['surge_multiplier'].iloc[0],
            'conditions': self.analyze_current_conditions(future_date, external_data)
        }
        
        return prediction
    
    def assess_surge_risk(self, future_days=7, external_data=None):
        """Assess surge risk for the next N days"""
        
        if external_data is None:
            print("No external data provided")
            return []
        
        current_date = external_data['date'].max() - timedelta(days=future_days)
        risk_assessments = []
        
        for days_ahead in range(1, future_days + 1):
            target_date = current_date + timedelta(days=days_ahead)
            
            # Predict for multiple hospitals
            hospital_predictions = []
            for hospital_id in range(1, 6):  # 5 hospitals
                prediction = self.predict_patient_surge(target_date, external_data, hospital_id)
                if prediction:
                    hospital_predictions.append(prediction)
            
            if hospital_predictions:
                # Aggregate predictions
                avg_surge_multiplier = np.mean([p['surge_multiplier'] for p in hospital_predictions])
                total_predicted_admissions = sum([p['predicted_admissions'] for p in hospital_predictions])
                
                # Determine if action is needed
                action_needed = avg_surge_multiplier > AGENT_CONFIG['surge_prediction_threshold']
                
                risk_assessments.append({
                    'date': target_date,
                    'days_ahead': days_ahead,
                    'average_surge_multiplier': avg_surge_multiplier,
                    'total_predicted_admissions': total_predicted_admissions,
                    'action_needed': action_needed,
                    'hospital_predictions': hospital_predictions
                })
        
        return risk_assessments
    
    def generate_action_plan(self, risk_assessment):
        """Generate action plan based on risk assessment"""
        
        if not risk_assessment['action_needed']:
            return None
        
        # Get first hospital's prediction for details (they'll be similar)
        sample_prediction = risk_assessment['hospital_predictions'][0]
        
        # Forecast resources
        predicted_admissions = sample_prediction['predicted_admissions']
        surge_multiplier = sample_prediction['surge_multiplier']
        
        resource_forecast = self.resource_forecaster.forecast(
            predicted_admissions,
            surge_multiplier
        )
        
        baseline_forecast = self.resource_forecaster.forecast(
            int(predicted_admissions / surge_multiplier)
        )
        
        # Identify surge reasons
        conditions = sample_prediction['conditions']
        surge_reasons = []
        
        if conditions['avg_aqi'] > 400:
            surge_reasons.append('Severe AQI')
        elif conditions['avg_aqi'] > 300:
            surge_reasons.append('Very Poor AQI')
        
        if conditions['rainfall_mm'] > 50:
            surge_reasons.append('Heavy Rainfall')
        
        if conditions['temperature_c'] > 36:
            surge_reasons.append('Extreme Heat')
        
        if conditions['has_event']:
            if 'Diwali' in str(conditions['active_events']):
                surge_reasons.append('Diwali Pollution')
            elif 'Ganesh Chaturthi' in str(conditions['active_events']):
                surge_reasons.append('Festival Crowd')
            else:
                surge_reasons.append('Festival Event')
        
        # Generate comprehensive recommendations
        recommendations = self.recommendation_engine.generate_comprehensive_recommendations(
            surge_prediction=surge_multiplier,
            resource_forecast=resource_forecast,
            baseline_resources=baseline_forecast,
            surge_reasons=surge_reasons,
            prediction_date=risk_assessment['date']
        )
        
        action_plan = {
            'generated_at': datetime.now(),
            'target_date': risk_assessment['date'],
            'days_advance_warning': risk_assessment['days_ahead'],
            'surge_assessment': {
                'surge_multiplier': surge_multiplier,
                'predicted_total_admissions': risk_assessment['total_predicted_admissions'],
                'surge_level': recommendations['surge_level']
            },
            'trigger_conditions': surge_reasons,
            'resource_requirements': resource_forecast,
            'recommendations': recommendations['recommendations'],
            'priority_actions': [r for r in recommendations['recommendations'] if r['priority'] == 'HIGH']
        }
        
        return action_plan
    
    def autonomous_monitoring_cycle(self, external_data, cycles=1):
        """Run autonomous monitoring cycles"""
        
        print("\n" + "=" * 70)
        print("ECO-HEALTH AI AGENT - AUTONOMOUS MONITORING")
        print("=" * 70)
        
        for cycle in range(cycles):
            print(f"\n{'='*70}")
            print(f"Monitoring Cycle #{cycle + 1}")
            print(f"{'='*70}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Assess surge risk
            print("\n► Analyzing external data sources...")
            risk_assessments = self.assess_surge_risk(
                future_days=AGENT_CONFIG['advance_warning_days'],
                external_data=external_data
            )
            
            # Find high-risk days
            high_risk_days = [r for r in risk_assessments if r['action_needed']]
            
            print(f"► Risk analysis complete: {len(high_risk_days)} surge events detected")
            
            if not high_risk_days:
                print("✓ No surge events predicted. Operations normal.")
                continue
            
            # Generate action plans for high-risk days
            print(f"\n► Generating action plans for {len(high_risk_days)} surge events...")
            
            for risk in high_risk_days:
                print(f"\n{'─'*70}")
                print(f"SURGE ALERT: {risk['date'].strftime('%B %d, %Y')}")
                print(f"Days ahead: {risk['days_ahead']} | Surge multiplier: {risk['average_surge_multiplier']:.2f}x")
                
                action_plan = self.generate_action_plan(risk)
                
                if action_plan:
                    print(f"Action plan generated:")
                    print(f"  • Surge Level: {action_plan['surge_assessment']['surge_level'].upper()}")
                    print(f"  • Total Recommendations: {len(action_plan['recommendations'])}")
                    print(f"  • High Priority Actions: {len(action_plan['priority_actions'])}")
                    print(f"  • Trigger Conditions: {', '.join(action_plan['trigger_conditions'])}")
                    
                    # Store prediction
                    self.prediction_history.append(action_plan)
            
            print(f"\n✓ Monitoring cycle complete")
            
            # In production, would sleep between cycles
            if cycle < cycles - 1:
                print(f"Next cycle in {AGENT_CONFIG['monitoring_interval_seconds']} seconds...")
        
        print(f"\n{'='*70}")
        print(f"Autonomous monitoring complete. {len(self.prediction_history)} action plans generated.")
        print(f"{'='*70}")
        
        return self.prediction_history


if __name__ == "__main__":
    # Example: Load data and run agent
    print("Loading external data...")
    
    # Load patient data (contains all merged external data)
    patient_df = pd.read_csv("data/patient_admissions.csv")
    patient_df['date'] = pd.to_datetime(patient_df['date'])
    
    # Initialize agent (would load actual trained models)
    agent = EcoHealthAgent()
    # agent.initialize()  # Uncomment when models are trained
    
    # For demonstration without trained models
    print("\n" + "=" * 70)
    print("AGENT DEMONSTRATION (using historical data as proxy)")
    print("=" * 70)
    
    # Simplified demonstration
    engine = RecommendationEngine()
    
    # Find a major surge event in data
    major_surges = patient_df[patient_df['surge_severity'] == 'critical'].head(1)
    
    if not major_surges.empty:
        surge_event = major_surges.iloc[0]
        
        print(f"\nAnalyzing surge event on {surge_event['date']}")
        print(f"Surge multiplier: {surge_event['surge_multiplier']}x")
        print(f"Reasons: {surge_event['surge_reasons']}")
        
        # Generate recommendations
        resource_forecast = {
            'doctors_needed': int(surge_event['total_admissions'] * 1/15),
            'nurses_needed': int(surge_event['total_admissions'] * 1/5),
            'support_staff_needed': int(surge_event['total_admissions'] * 1/10),
            'ppe_kits': int(surge_event['total_admissions'] * 2),
            'oxygen_liters': int(surge_event['total_admissions'] * 10),
            'iv_fluids_ml': int(surge_event['total_admissions'] * 500),
            'medications_units': int(surge_event['total_admissions'] * 5),
            'beds_needed': int(np.ceil(surge_event['total_admissions'] / 0.7))
        }
        
        baseline_forecast = {k: int(v / surge_event['surge_multiplier']) for k, v in resource_forecast.items()}
        
        recommendations = engine.generate_comprehensive_recommendations(
            surge_prediction=surge_event['surge_multiplier'],
            resource_forecast=resource_forecast,
            baseline_resources=baseline_forecast,
            surge_reasons=surge_event['surge_reasons'].split(', '),
            prediction_date=pd.to_datetime(surge_event['date'])
        )
        
        print(f"\n{'='*70}")
        print("AGENT RECOMMENDATIONS")
        print(f"{'='*70}")
        print(f"Surge Level: {recommendations['surge_level'].upper()}")
        print(f"Total Actions: {recommendations['total_actions']}")
        
        for i, rec in enumerate(recommendations['recommendations'][:3], 1):  # Show first 3
            print(f"\n{i}. {rec['category']} [{rec['priority']}]")
            print(f"   {rec['action']}")
            for detail in rec['details'][:3]:  # Show first 3 details
                print(f"    • {detail}")
