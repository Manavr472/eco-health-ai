import requests
from datetime import datetime

def get_real_time_aqi(latitude: float = 19.0760, longitude: float = 72.8777):
    """
    Fetch real-time AQI from Open-Meteo API.
    Defaults to Mumbai coordinates.
    """
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "us_aqi",  # Requesting US AQI standard
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "current" in data and "us_aqi" in data["current"]:
            return {
                "aqi": data["current"]["us_aqi"],
                "timestamp": datetime.now().isoformat(),
                "source": "Open-Meteo Real-time API"
            }
        else:
            print("Warning: Unexpected API response structure")
            return None
            
    except Exception as e:
        print(f"Error fetching real-time AQI: {e}")
        return None

def get_historical_aqi(latitude: float, longitude: float, start_date: str, end_date: str):
    """
    Fetch historical AQI from Open-Meteo API and aggregate to daily averages.
    Dates should be in YYYY-MM-DD format.
    """
    try:
        # Use standard API for historical data (it supports history via start/end date)
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "us_aqi",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "hourly" in data and "time" in data["hourly"] and "us_aqi" in data["hourly"]:
            times = data["hourly"]["time"]
            aqi_values = data["hourly"]["us_aqi"]
            
            # Aggregate hourly to daily
            daily_aqi = {}
            
            for t, aqi in zip(times, aqi_values):
                if aqi is None: continue
                date_str = t.split("T")[0]
                if date_str not in daily_aqi:
                    daily_aqi[date_str] = []
                daily_aqi[date_str].append(aqi)
            
            # Calculate averages
            results = {}
            for date, values in daily_aqi.items():
                if values:
                    results[date] = int(sum(values) / len(values))
            
            return results
        else:
            return {}
            
    except Exception as e:
        print(f"Error fetching historical AQI: {e}")
        return {}
