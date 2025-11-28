"""
Weather Data Generator for Mumbai
Generates realistic synthetic weather data including temperature, rainfall, and humidity
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DATA_START_DATE, DATA_END_DATE, MONSOON_START_MONTH, MONSOON_END_MONTH,
    SUMMER_TEMP_RANGE, MONSOON_TEMP_RANGE, WINTER_TEMP_RANGE,
    MONSOON_RAINFALL_MEAN, MONSOON_RAINFALL_STD, NON_MONSOON_RAINFALL_PROB,
    MONSOON_HUMIDITY_RANGE, NON_MONSOON_HUMIDITY_RANGE
)


class WeatherGenerator:
    """Generate synthetic weather data for Mumbai"""
    
    def __init__(self):
        self.start_date = DATA_START_DATE
        self.end_date = DATA_END_DATE
    
    def _get_season(self, date):
        """Determine season based on month"""
        month = date.month
        if MONSOON_START_MONTH <= month <= MONSOON_END_MONTH:
            return "monsoon"
        elif month in [3, 4, 5]:
            return "summer"
        elif month in [11, 12, 1, 2]:
            return "winter"
        else:
            return "post_monsoon"
    
    def _generate_temperature(self, date, season):
        """Generate temperature based on season"""
        if season == "summer":
            min_temp, max_temp = SUMMER_TEMP_RANGE
        elif season == "monsoon":
            min_temp, max_temp = MONSOON_TEMP_RANGE
        elif season == "winter":
            min_temp, max_temp = WINTER_TEMP_RANGE
        else:  # post_monsoon
            min_temp, max_temp = 25, 34
        
        # Add some variation
        mean_temp = (min_temp + max_temp) / 2
        std_temp = (max_temp - min_temp) / 4
        
        temp = np.random.normal(mean_temp, std_temp)
        return np.clip(temp, min_temp - 2, max_temp + 2)
    
    def _generate_rainfall(self, date, season):
        """Generate rainfall based on season"""
        if season == "monsoon":
            # Heavy monsoon rainfall
            rainfall = np.random.gamma(shape=2, scale=MONSOON_RAINFALL_MEAN/2)
            
            # Add extreme rainfall events
            if np.random.random() < 0.1:  # 10% chance of heavy rain
                rainfall *= np.random.uniform(2, 5)
            
        else:
            # Occasional rainfall in non-monsoon
            if np.random.random() < NON_MONSOON_RAINFALL_PROB:
                rainfall = np.random.exponential(scale=5)
            else:
                rainfall = 0
        
        return round(rainfall, 2)
    
    def _generate_humidity(self, date, season, rainfall):
        """Generate humidity based on season and rainfall"""
        if season == "monsoon" or rainfall > 0:
            min_hum, max_hum = MONSOON_HUMIDITY_RANGE
        else:
            min_hum, max_hum = NON_MONSOON_HUMIDITY_RANGE
        
        mean_hum = (min_hum + max_hum) / 2
        std_hum = (max_hum - min_hum) / 4
        
        humidity = np.random.normal(mean_hum, std_hum)
        
        # Adjust humidity based on rainfall
        if rainfall > 20:
            humidity += 10
        
        return np.clip(humidity, 20, 100)
    
    def _generate_wind_speed(self, date, season, rainfall):
        """Generate wind speed"""
        base_wind = 10  # km/h
        
        if season == "monsoon":
            base_wind = 20
        
        if rainfall > 30:  # Storm conditions
            base_wind = 40
        
        wind = np.random.gamma(shape=2, scale=base_wind/2)
        return round(wind, 1)
    
    def generate(self):
        """Generate complete weather dataset"""
        data = []
        current_date = self.start_date
        
        print(f"Generating weather data from {self.start_date} to {self.end_date}...")
        
        while current_date <= self.end_date:
            season = self._get_season(current_date)
            
            # Generate weather parameters
            temperature = self._generate_temperature(current_date, season)
            rainfall = self._generate_rainfall(current_date, season)
            humidity = self._generate_humidity(current_date, season, rainfall)
            wind_speed = self._generate_wind_speed(current_date, season, rainfall)
            
            # Classify weather conditions
            condition = self._classify_weather(temperature, rainfall, wind_speed)
            
            data.append({
                'date': current_date,
                'season': season,
                'temperature_c': round(temperature, 1),
                'rainfall_mm': rainfall,
                'humidity_percent': round(humidity, 1),
                'wind_speed_kmh': wind_speed,
                'condition': condition,
                'is_extreme_heat': temperature > 36,
                'is_heavy_rain': rainfall > 50,
                'is_storm': rainfall > 50 and wind_speed > 30
            })
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(data)
        print(f"Generated {len(df)} weather records")
        print(f"\nWeather Statistics by Season:")
        print(df.groupby('season')[['temperature_c', 'rainfall_mm', 'humidity_percent']].mean().round(2))
        
        return df
    
    def _classify_weather(self, temp, rain, wind):
        """Classify weather condition"""
        if rain > 50 and wind > 30:
            return "Storm"
        elif rain > 20:
            return "Heavy Rain"
        elif rain > 5:
            return "Rainy"
        elif temp > 35:
            return "Very Hot"
        elif temp > 30:
            return "Hot"
        elif temp < 20:
            return "Cool"
        else:
            return "Pleasant"
    
    def save(self, df, filepath="data/weather_data.csv"):
        """Save weather data to CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Saved weather data to {filepath}")


if __name__ == "__main__":
    generator = WeatherGenerator()
    weather_df = generator.generate()
    generator.save(weather_df)
    
    # Display sample
    print("\nSample weather data:")
    print(weather_df.head(20))
    print("\nExtreme events:")
    print(f"Extreme heat days: {weather_df['is_extreme_heat'].sum()}")
    print(f"Heavy rainfall days: {weather_df['is_heavy_rain'].sum()}")
    print(f"Storm days: {weather_df['is_storm'].sum()}")
