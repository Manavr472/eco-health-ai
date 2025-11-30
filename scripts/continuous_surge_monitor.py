"""
Continuous Surge Prediction Monitor
Updates predictions every 30 seconds with detailed logging
"""

import pandas as pd
import os
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import MUMBAI_HOSPITALS
from src.services.aqi_service import get_real_time_aqi
from src.services.weather_service import weather_service
from src.services.event_service import event_service
from src.models.surge_predictor import surge_predictor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/prediction_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('prediction_agent')

# Load environment
load_dotenv(".env.local")

def get_hospital_baseline(hospital_code, target_date):
    """Get baseline admissions for a specific date from historical data"""
    try:
        df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        df['date'] = pd.to_datetime(df['date'])
        
        # Map to 2024 for lookup (same logic as API)
        lookup_date = target_date.replace(year=2024)
        
        hospital_data = df[
            (df['hospital_id'] == hospital_code) &
            (df['date'].dt.date == lookup_date.date())
        ]
        
        if not hospital_data.empty:
            return int(hospital_data.iloc[0]['baseline_admissions'])
    except Exception as e:
        logger.warning(f"Error getting baseline for {hospital_code} on {target_date}: {e}")
    
    return 150  # Default baseline

def calculate_admission_breakdown(total_admissions, aqi, weather, events):
    """Calculate breakdown of admissions by disease type"""
    # Base percentages
    respiratory_pct = 0.15
    waterborne_pct = 0.10
    heat_pct = 0.05
    trauma_pct = 0.20
    
    # Adjust based on conditions
    if aqi > 200:
        respiratory_pct += 0.10
    if weather.get('rainfall', 0) > 30:
        waterborne_pct += 0.10
    if weather.get('max_temp', 0) > 35:
        heat_pct += 0.08
    if events:
        trauma_pct += 0.12
    
    # Normalize to ensure percentages add up reasonably
    total_pct = respiratory_pct + waterborne_pct + heat_pct + trauma_pct
    other_pct = max(0, 1 - total_pct)
    
    return {
        'respiratory': int(total_admissions * respiratory_pct),
        'waterborne': int(total_admissions * waterborne_pct),
        'heat': int(total_admissions * heat_pct),
        'trauma': int(total_admissions * trauma_pct),
        'other': int(total_admissions * other_pct)
    }

def predict_for_all_hospitals():
    """Run 7-day predictions for all hospitals and log detailed reasoning"""
    today = datetime.now()
    
    logger.info("="*80)
    logger.info(f"[CYCLE START] Beginning 7-day prediction cycle")
    logger.info("="*80)
    
    predictions = []
    
    for hospital in MUMBAI_HOSPITALS:
        hospital_id = hospital['id']
        hospital_code = hospital['code']
        hospital_name = hospital['name']
        lat, lon = hospital['lat'], hospital['lon']
        
        logger.info("")
        logger.info(f"[HOSPITAL] {hospital_name} ({hospital_code})")
        logger.info("-"*80)
        
        # Predict for next 7 days
        for day_offset in range(7):
            target_date = today + timedelta(days=day_offset)
            target_date_str = target_date.strftime("%Y-%m-%d")
            
            day_label = "TODAY" if day_offset == 0 else f"DAY +{day_offset}"
            logger.info(f"[THOUGHT] Predicting for {target_date_str} ({day_label})")
            
            # Get AQI
            aqi_data = get_real_time_aqi(latitude=lat, longitude=lon)
            current_aqi = aqi_data['aqi'] if aqi_data else 150
            
            # Get Weather forecast
            weather = weather_service.get_forecast(lat, lon, days=day_offset+1)
            target_weather = weather.get(target_date_str, {})
            temp = target_weather.get('max_temp', 30)
            rainfall = target_weather.get('rainfall', 0)
            
            # Get Events
            events = event_service.get_events(target_date_str)
            
            if day_offset == 0:  # Log details only for today
                logger.info(f"[THOUGHT] AQI={current_aqi:.0f}, Temp={temp}°C, Rain={rainfall}mm, Events={events if events else 'None'}")
            
            # Run prediction
            prediction = surge_predictor.predict(target_date_str, current_aqi, target_weather, events)
            
            surge_multiplier = prediction['multiplier']
            severity = prediction['severity']
            narrative = prediction['narrative']
            
            # Get baseline for THIS specific date (same logic as API)
            baseline = get_hospital_baseline(hospital_code, target_date)
            
            # Calculate admissions
            total_admissions = int(baseline * surge_multiplier)
            breakdown = calculate_admission_breakdown(total_admissions, current_aqi, target_weather, events)
            
            logger.info(f"[ACTION] {day_label}: {total_admissions} patients (x{surge_multiplier:.1f}) - {narrative}")
            
            # Add to predictions
            predictions.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'prediction_date': target_date_str,
                'days_ahead': day_offset,
                'hospital_id': hospital_code,
                'hospital_name': hospital_name,
                'total_admissions': total_admissions,
                'baseline_admissions': baseline,
                'surge_multiplier': surge_multiplier,
                'surge_reasons': narrative,
                'respiratory_admissions': breakdown['respiratory'],
                'waterborne_admissions': breakdown['waterborne'],
                'heat_related_admissions': breakdown['heat'],
                'trauma_admissions': breakdown['trauma'],
                'other_admissions': breakdown['other']
            })
        
        logger.info(f"[COMPLETE] {hospital_name} 7-day forecast complete")
    
    logger.info("")
    logger.info("="*80)
    logger.info(f"[CYCLE END] Generated {len(predictions)} predictions ({len(MUMBAI_HOSPITALS)} hospitals × 7 days)")
    logger.info("="*80)
    
    return predictions

def main():
    """Main monitoring loop"""
    output_file = "data/continuous_surge_predictions.csv"
    
    logger.info("Continuous Surge Monitor Started")
    logger.info(f"Output File: {output_file}")
    logger.info(f"Update Interval: 30 seconds")
    logger.info(f"Monitoring {len(MUMBAI_HOSPITALS)} hospitals")
    logger.info("")
    
    # Create/overwrite CSV with headers
    pd.DataFrame(columns=[
        'timestamp', 'prediction_date', 'days_ahead', 'hospital_id', 'hospital_name',
        'total_admissions', 'baseline_admissions', 'surge_multiplier', 'surge_reasons',
        'respiratory_admissions', 'waterborne_admissions', 
        'heat_related_admissions', 'trauma_admissions', 'other_admissions'
    ]).to_csv(output_file, index=False)
    
    iteration = 0
    while True:
        iteration += 1
        logger.info(f"\n{'#'*80}")
        logger.info(f"ITERATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'#'*80}\n")
        
        try:
            # Run predictions for all hospitals
            predictions = predict_for_all_hospitals()
            
            # Append to CSV
            df = pd.DataFrame(predictions)
            df.to_csv(output_file, mode='a', header=False, index=False)
            logger.info(f"[SUCCESS] Predictions saved to {output_file}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error in prediction cycle: {e}")
        
        # Wait 30 seconds
        logger.info(f"[WAIT] Next update in 30 seconds...")
        logger.info("")
        time.sleep(30)

if __name__ == "__main__":
    main()
