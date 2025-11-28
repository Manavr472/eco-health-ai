import requests
from datetime import datetime, timedelta
import logging

class WeatherService:
    """Service to fetch weather forecast from Open-Meteo"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        self.logger = logging.getLogger('prediction_agent')
        
    def get_forecast(self, lat: float, lon: float, days: int = 7):
        """Get weather forecast for location"""
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": ["temperature_2m_max", "precipitation_sum"],
                "timezone": "Asia/Kolkata",
                "forecast_days": days
            }
            
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get('daily', {})
            dates = daily.get('time', [])
            temps = daily.get('temperature_2m_max', [])
            rains = daily.get('precipitation_sum', [])
            
            forecast = {}
            for i, date in enumerate(dates):
                forecast[date] = {
                    'max_temp': temps[i],
                    'rainfall': rains[i]
                }
                
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error fetching weather forecast: {e}")
            return {}

    def get_historical_weather(self, lat: float, lon: float, start_date: str, end_date: str):
        """Get historical weather data from Open-Meteo Archive"""
        try:
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": ["temperature_2m_max", "precipitation_sum"],
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get('daily', {})
            dates = daily.get('time', [])
            temps = daily.get('temperature_2m_max', [])
            rains = daily.get('precipitation_sum', [])
            
            history = {}
            for i, date in enumerate(dates):
                history[date] = {
                    'max_temp': temps[i],
                    'rainfall': rains[i]
                }
                
            return history
            
        except Exception as e:
            self.logger.error(f"Error fetching historical weather: {e}")
            return {}

# Singleton instance
weather_service = WeatherService()
