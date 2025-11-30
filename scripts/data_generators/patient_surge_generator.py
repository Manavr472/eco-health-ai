"""
Patient Surge Generator for Mumbai Hospitals
Generates realistic patient admission data correlated with AQI, weather, and events
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DATA_START_DATE, DATA_END_DATE, NUM_HOSPITALS,
    BASELINE_DAILY_ADMISSIONS, SURGE_FACTORS, DISEASE_PATTERNS
)


class PatientSurgeGenerator:
    """Generate synthetic patient admission data with realistic surges"""
    
    def __init__(self, aqi_df, weather_df, events_df):
        self.start_date = DATA_START_DATE
        self.end_date = DATA_END_DATE
        self.num_hospitals = NUM_HOSPITALS
        self.baseline = BASELINE_DAILY_ADMISSIONS
        
        # External data
        self.aqi_df = aqi_df
        self.weather_df = weather_df
        self.events_df = events_df
        
        # Prepare merged data for easier lookup
        self._prepare_data()
    
    def _prepare_data(self):
        """Merge all external data by date"""
        # Average AQI across all stations per day
        aqi_daily = self.aqi_df.groupby('date').agg({
            'aqi': 'mean'
        }).reset_index()
        aqi_daily = aqi_daily.rename(columns={'aqi': 'avg_aqi'})
        
        # Merge weather data
        self.daily_data = pd.merge(aqi_daily, self.weather_df, on='date', how='outer')
        
        # Merge event data
        self.daily_data = pd.merge(self.daily_data, self.events_df, on='date', how='left')
        
        # Fill NaN values in event columns
        self.daily_data['has_event'] = self.daily_data['has_event'].fillna(False)
        self.daily_data['event_severity'] = self.daily_data['event_severity'].fillna(0)
        self.daily_data['is_pre_event'] = self.daily_data['is_pre_event'].fillna(False)
        self.daily_data['is_post_event'] = self.daily_data['is_post_event'].fillna(False)
        
        # Sort by date
        self.daily_data = self.daily_data.sort_values('date').reset_index(drop=True)
    
    def _calculate_surge_multiplier(self, row):
        """Calculate surge multiplier based on all factors"""
        multiplier = 1.0
        surge_reasons = []
        
        # AQI-based surge
        if row['avg_aqi'] > 400:
            multiplier *= SURGE_FACTORS['aqi_severe']
            surge_reasons.append('Severe AQI')
        elif row['avg_aqi'] > 300:
            multiplier *= SURGE_FACTORS['aqi_very_poor']
            surge_reasons.append('Very Poor AQI')
        
        # Rainfall-based surge
        if row['rainfall_mm'] > 50:
            multiplier *= SURGE_FACTORS['heavy_rainfall']
            surge_reasons.append('Heavy Rainfall')
        
        # Temperature-based surge
        if row['temperature_c'] > 36:
            multiplier *= SURGE_FACTORS['extreme_heat']
            surge_reasons.append('Extreme Heat')
        
        # Event-based surge
        if row['has_event']:
            if 'Diwali' in str(row['active_events']):
                multiplier *= SURGE_FACTORS['pollution_event']
                surge_reasons.append('Diwali Pollution')
            elif 'Ganesh Chaturthi' in str(row['active_events']):
                multiplier *= SURGE_FACTORS['festival_injuries']
                surge_reasons.append('Festival Crowd')
            else:
                multiplier *= 1.3
                surge_reasons.append('Festival Event')
        
        # Seasonal flu (winter months)
        if row['season'] == 'winter':
            multiplier *= 1.2  # Mild seasonal increase
            if 'Seasonal Flu' not in surge_reasons:
                surge_reasons.append('Seasonal Flu')
        
        # Pre/Post event effects
        if row['is_pre_event']:
            multiplier *= 1.1
        if row['is_post_event']:
            multiplier *= 1.15
        
        return multiplier, surge_reasons
    
    def _generate_disease_distribution(self, row, total_admissions):
        """Generate disease-specific admission counts"""
        diseases = {}
        
        # Respiratory diseases (correlated with AQI)
        resp_baseline = total_admissions * DISEASE_PATTERNS['respiratory']['baseline_percentage']
        if row['avg_aqi'] > DISEASE_PATTERNS['respiratory']['aqi_threshold']:
            resp_surge = DISEASE_PATTERNS['respiratory']['surge_factor']
            diseases['respiratory'] = int(resp_baseline * resp_surge)
        else:
            diseases['respiratory'] = int(resp_baseline)
        
        # Waterborne diseases (correlated with rainfall)
        water_baseline = total_admissions * DISEASE_PATTERNS['waterborne']['baseline_percentage']
        if row['rainfall_mm'] > DISEASE_PATTERNS['waterborne']['rainfall_threshold']:
            water_surge = DISEASE_PATTERNS['waterborne']['surge_factor']
            diseases['waterborne'] = int(water_baseline * water_surge)
        else:
            diseases['waterborne'] = int(water_baseline)
        
        # Heat-related illnesses
        heat_baseline = total_admissions * DISEASE_PATTERNS['heat_related']['baseline_percentage']
        if row['temperature_c'] > DISEASE_PATTERNS['heat_related']['temperature_threshold']:
            heat_surge = DISEASE_PATTERNS['heat_related']['surge_factor']
            diseases['heat_related'] = int(heat_baseline * heat_surge)
        else:
            diseases['heat_related'] = int(heat_baseline)
        
        # Trauma/Injuries (correlated with festivals)
        trauma_baseline = total_admissions * DISEASE_PATTERNS['trauma']['baseline_percentage']
        if row['has_event']:
            trauma_surge = DISEASE_PATTERNS['trauma']['surge_factor']
            diseases['trauma'] = int(trauma_baseline * trauma_surge)
        else:
            diseases['trauma'] = int(trauma_baseline)
        
        # Other diseases (remainder)
        diseases['other'] = max(0, total_admissions - sum(diseases.values()))
        
        return diseases
    
    def generate(self):
        """Generate complete patient admission dataset"""
        data = []
        
        print(f"Generating patient admission data for {self.num_hospitals} hospitals...")
        print(f"Date range: {self.start_date} to {self.end_date}")
        
        for idx, row in self.daily_data.iterrows():
            date = row['date']
            
            # Calculate surge multiplier
            surge_mult, surge_reasons = self._calculate_surge_multiplier(row)
            
            # Generate for each hospital
            for hospital_id in range(1, self.num_hospitals + 1):
                # Hospital-specific variation (some hospitals larger/smaller)
                hospital_factor = 1.0 + (hospital_id - self.num_hospitals/2) * 0.1
                
                # Calculate base admissions for this hospital
                base_admissions = self.baseline * hospital_factor
                
                # Add day-of-week pattern
                day_of_week = date.weekday()
                weekday_factor = 0.9 if day_of_week >= 5 else 1.0
                
                # Calculate total admissions with surge
                expected_admissions = base_admissions * weekday_factor * surge_mult
                
                # Add random noise
                noise = np.random.normal(1.0, 0.15)
                total_admissions = int(expected_admissions * noise)
                total_admissions = max(10, total_admissions)  # Minimum 10 admissions
                
                # Generate disease distribution
                disease_dist = self._generate_disease_distribution(row, total_admissions)
                
                # Determine if this is a surge event
                is_surge = surge_mult > 1.3
                surge_severity = 'none'
                if surge_mult > 2.0:
                    surge_severity = 'critical'
                elif surge_mult > 1.7:
                    surge_severity = 'major'
                elif surge_mult > 1.4:
                    surge_severity = 'moderate'
                elif surge_mult > 1.2:
                    surge_severity = 'minor'
                
                data.append({
                    'date': date,
                    'hospital_id': hospital_id,
                    'hospital_name': f'Mumbai Hospital {hospital_id}',
                    'total_admissions': total_admissions,
                    'baseline_admissions': int(base_admissions),
                    'surge_multiplier': round(surge_mult, 2),
                    'is_surge': is_surge,
                    'surge_severity': surge_severity,
                    'surge_reasons': ', '.join(surge_reasons) if surge_reasons else 'None',
                    'respiratory_admissions': disease_dist['respiratory'],
                    'waterborne_admissions': disease_dist['waterborne'],
                    'heat_related_admissions': disease_dist['heat_related'],
                    'trauma_admissions': disease_dist['trauma'],
                    'other_admissions': disease_dist['other'],
                    'avg_aqi': round(row['avg_aqi'], 2),
                    'temperature_c': row['temperature_c'],
                    'rainfall_mm': row['rainfall_mm'],
                    'active_events': row['active_events'] if row['has_event'] else None
                })
        
        df = pd.DataFrame(data)
        
        print(f"\nGenerated {len(df)} patient admission records")
        print(f"Total admissions: {df['total_admissions'].sum():,}")
        print(f"\nSurge Statistics:")
        print(df.groupby('surge_severity').size())
        print(f"\nAverage admissions by hospital:")
        print(df.groupby('hospital_id')['total_admissions'].mean().round(0))
        
        return df
    
    def save(self, df, filepath="data/patient_admissions.csv"):
        """Save patient admission data to CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"\nSaved patient admission data to {filepath}")


if __name__ == "__main__":
    # Load previously generated data
    print("Loading external data...")
    aqi_df = pd.read_csv("data/aqi_data.csv")
    aqi_df['date'] = pd.to_datetime(aqi_df['date'])
    
    weather_df = pd.read_csv("data/weather_data.csv")
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    
    events_df = pd.read_csv("data/daily_events.csv")
    events_df['date'] = pd.to_datetime(events_df['date'])
    
    # Generate patient data
    generator = PatientSurgeGenerator(aqi_df, weather_df, events_df)
    patient_df = generator.generate()
    generator.save(patient_df)
    
    # Display surge events
    print("\nTop 10 surge events:")
    surge_df = patient_df[patient_df['is_surge']].sort_values('surge_multiplier', ascending=False)
    print(surge_df[['date', 'hospital_name', 'total_admissions', 'surge_multiplier', 'surge_reasons']].head(10))
