"""
AQI (Air Quality Index) Data Generator for Mumbai
Generates realistic synthetic AQI data with seasonal patterns and event-based spikes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    MUMBAI_STATIONS, DATA_START_DATE, DATA_END_DATE,
    AQI_BASELINE, AQI_STD_DEV, MONSOON_AQI_REDUCTION,
    WINTER_AQI_INCREASE, DIWALI_AQI_SPIKE, ANNUAL_FESTIVALS,
    MONSOON_START_MONTH, MONSOON_END_MONTH
)


class AQIGenerator:
    """Generate synthetic AQI data for Mumbai monitoring stations"""
    
    def __init__(self):
        self.start_date = DATA_START_DATE
        self.end_date = DATA_END_DATE
        self.stations = MUMBAI_STATIONS
        
    def _is_monsoon(self, date):
        """Check if date falls in monsoon season"""
        return MONSOON_START_MONTH <= date.month <= MONSOON_END_MONTH
    
    def _is_winter(self, date):
        """Check if date falls in winter (Nov-Feb)"""
        return date.month in [11, 12, 1, 2]
    
    def _is_diwali_period(self, date):
        """Check if date is during Diwali festival"""
        for diwali in ANNUAL_FESTIVALS["Diwali"]:
            start = datetime.strptime(diwali["start"], "%Y-%m-%d")
            end = datetime.strptime(diwali["end"], "%Y-%m-%d")
            # Extended pollution period (5 days before to 7 days after)
            if (start - timedelta(days=5)) <= date <= (end + timedelta(days=7)):
                # Peak during festival days
                if start <= date <= end:
                    return 2.0  # Peak pollution
                else:
                    return 1.5  # Elevated pollution
        return 1.0
    
    def _get_base_aqi(self, date, station_idx):
        """Calculate base AQI for a given date and station"""
        # Start with baseline
        base_aqi = AQI_BASELINE
        
        # Station-specific offset (some areas more polluted)
        station_offset = (station_idx - len(self.stations) / 2) * 10
        base_aqi += station_offset
        
        # Seasonal adjustments
        if self._is_monsoon(date):
            base_aqi -= MONSOON_AQI_REDUCTION
        elif self._is_winter(date):
            base_aqi += WINTER_AQI_INCREASE
        
        # Weekly pattern (weekdays vs weekends)
        if date.weekday() >= 5:  # Weekend
            base_aqi -= 20  # Less traffic pollution
        
        # Daily pattern would go here, but we're doing daily averages
        
        return max(0, base_aqi)
    
    def _add_diwali_spike(self, aqi, date):
        """Add Diwali-related pollution spike"""
        diwali_factor = self._is_diwali_period(date)
        if diwali_factor > 1.0:
            # Add spike proportional to base AQI
            spike = (diwali_factor - 1.0) * DIWALI_AQI_SPIKE
            return aqi + spike
        return aqi
    
    def _add_random_events(self, aqi, date, station_idx):
        """Add random pollution events (construction, fires, etc.)"""
        # 5% chance of random event on any day
        np.random.seed(int(date.timestamp()) + station_idx)
        if np.random.random() < 0.05:
            event_magnitude = np.random.uniform(50, 150)
            return aqi + event_magnitude
        return aqi
    
    def generate(self):
        """Generate complete AQI dataset"""
        data = []
        current_date = self.start_date
        
        print(f"Generating AQI data from {self.start_date} to {self.end_date}...")
        
        while current_date <= self.end_date:
            for station_idx, station in enumerate(self.stations):
                # Get base AQI for this date and station
                base_aqi = self._get_base_aqi(current_date, station_idx)
                
                # Add random noise
                noise = np.random.normal(0, AQI_STD_DEV)
                aqi = base_aqi + noise
                
                # Add Diwali spike if applicable
                aqi = self._add_diwali_spike(aqi, current_date)
                
                # Add random events
                aqi = self._add_random_events(aqi, current_date, station_idx)
                
                # Ensure AQI is within valid range (0-500)
                aqi = np.clip(aqi, 0, 500)
                
                # Categorize AQI
                category = self._categorize_aqi(aqi)
                
                data.append({
                    'date': current_date,
                    'station': station,
                    'aqi': round(aqi, 2),
                    'category': category,
                    'is_monsoon': self._is_monsoon(current_date),
                    'is_winter': self._is_winter(current_date),
                    'diwali_factor': self._is_diwali_period(current_date)
                })
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(data)
        print(f"Generated {len(df)} AQI records for {len(self.stations)} stations")
        print(f"AQI Statistics:")
        print(df.groupby('category')['aqi'].count())
        
        return df
    
    def _categorize_aqi(self, aqi):
        """Categorize AQI value"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Satisfactory"
        elif aqi <= 200:
            return "Moderate"
        elif aqi <= 300:
            return "Poor"
        elif aqi <= 400:
            return "Very Poor"
        else:
            return "Severe"
    
    def save(self, df, filepath="data/aqi_data.csv"):
        """Save AQI data to CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Saved AQI data to {filepath}")


if __name__ == "__main__":
    generator = AQIGenerator()
    aqi_df = generator.generate()
    generator.save(aqi_df)
    
    # Display sample
    print("\nSample AQI data:")
    print(aqi_df.head(20))
    print("\nAQI by station (mean):")
    print(aqi_df.groupby('station')['aqi'].mean().round(2))
