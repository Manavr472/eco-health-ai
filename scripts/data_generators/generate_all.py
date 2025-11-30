"""
Master Data Generation Script
Orchestrates all data generators to create the complete synthetic dataset
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aqi_generator import AQIGenerator
from weather_generator import WeatherGenerator
from event_generator import EventGenerator
from patient_surge_generator import PatientSurgeGenerator


def main():
    """Generate all synthetic data for Eco-Health AI"""
    
    print("=" * 70)
    print("ECO-HEALTH AI - SYNTHETIC DATA GENERATION")
    print("Mumbai Region - 5 Year Historical Dataset (2020-2024)")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    # Step 1: Generate AQI Data
    print("\n" + "=" * 70)
    print("STEP 1: Generating AQI Data")
    print("=" * 70)
    aqi_gen = AQIGenerator()
    aqi_df = aqi_gen.generate()
    aqi_gen.save(aqi_df)
    
    # Step 2: Generate Weather Data
    print("\n" + "=" * 70)
    print("STEP 2: Generating Weather Data")
    print("=" * 70)
    weather_gen = WeatherGenerator()
    weather_df = weather_gen.generate()
    weather_gen.save(weather_df)
    
    # Step 3: Generate Event Calendar
    print("\n" + "=" * 70)
    print("STEP 3: Generating Event Calendar")
    print("=" * 70)
    event_gen = EventGenerator()
    events_df = event_gen.generate()
    daily_events_df = event_gen.create_daily_event_marker(events_df)
    event_gen.save(events_df, daily_events_df)
    
    # Step 4: Generate Patient Admission Data
    print("\n" + "=" * 70)
    print("STEP 4: Generating Patient Admission Data")
    print("=" * 70)
    patient_gen = PatientSurgeGenerator(aqi_df, weather_df, daily_events_df)
    patient_df = patient_gen.generate()
    patient_gen.save(patient_df)
    
    # Summary Statistics
    print("\n" + "=" * 70)
    print("DATA GENERATION COMPLETE - SUMMARY")
    print("=" * 70)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✓ Generation completed in {duration:.2f} seconds")
    print(f"\nDatasets Created:")
    print(f"  • AQI Records: {len(aqi_df):,}")
    print(f"  • Weather Records: {len(weather_df):,}")
    print(f"  • Festival Events: {len(events_df):,}")
    print(f"  • Daily Event Markers: {len(daily_events_df):,}")
    print(f"  • Patient Admission Records: {len(patient_df):,}")
    
    print(f"\n✓ All data saved to 'data/' directory")
    
    # Key Insights
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    
    # AQI insights
    severe_aqi_days = aqi_df[aqi_df['category'].isin(['Very Poor', 'Severe'])].groupby('date').size()
    print(f"\n• Days with Very Poor/Severe AQI: {len(severe_aqi_days)}")
    
    # Weather insights
    extreme_weather_days = weather_df[
        (weather_df['is_extreme_heat']) | 
        (weather_df['is_heavy_rain']) | 
        (weather_df['is_storm'])
    ]
    print(f"• Days with extreme weather events: {len(extreme_weather_days)}")
    
    # Patient surge insights
    surge_days = patient_df[patient_df['is_surge']].groupby('date').size()
    print(f"• Days with patient surges: {len(surge_days)}")
    
    major_surges = patient_df[patient_df['surge_severity'].isin(['major', 'critical'])]
    print(f"• Major/Critical surge events: {len(major_surges)}")
    
    avg_daily_admissions = patient_df.groupby('date')['total_admissions'].sum().mean()
    print(f"• Average daily admissions (all hospitals): {avg_daily_admissions:.0f}")
    
    # Disease distribution
    print(f"\n Disease Distribution:")
    total_resp = patient_df['respiratory_admissions'].sum()
    total_water = patient_df['waterborne_admissions'].sum()
    total_heat = patient_df['heat_related_admissions'].sum()
    total_trauma = patient_df['trauma_admissions'].sum()
    total_other = patient_df['other_admissions'].sum()
    total_all = total_resp + total_water + total_heat + total_trauma + total_other
    
    print(f"  • Respiratory: {total_resp:,} ({total_resp/total_all*100:.1f}%)")
    print(f"  • Waterborne: {total_water:,} ({total_water/total_all*100:.1f}%)")
    print(f"  • Heat-related: {total_heat:,} ({total_heat/total_all*100:.1f}%)")
    print(f"  • Trauma: {total_trauma:,} ({total_trauma/total_all*100:.1f}%)")
    print(f"  • Other: {total_other:,} ({total_other/total_all*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("Data generation successful! Ready for model training.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
