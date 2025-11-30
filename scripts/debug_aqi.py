import requests

def test_aqi(url, name):
    print(f"Testing {name}: {url}")
    params = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "start_date": "2020-01-01",
        "end_date": "2020-01-05",
        "hourly": "us_aqi,pm2_5,european_aqi",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "hourly" in data:
                print(f"Success! Keys: {data['hourly'].keys()}")
                if "us_aqi" in data["hourly"]: print(f"US AQI Sample: {data['hourly']['us_aqi'][:5]}")
                if "pm2_5" in data["hourly"]: print(f"PM2.5 Sample: {data['hourly']['pm2_5'][:5]}")
                if "european_aqi" in data["hourly"]: print(f"EU AQI Sample: {data['hourly']['european_aqi'][:5]}")
            else:
                print("Response JSON missing 'hourly' or 'us_aqi'")
                print(data.keys())
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

test_aqi("https://air-quality-api.open-meteo.com/v1/air-quality", "Air Quality API")
test_aqi("https://api.open-meteo.com/v1/air-quality", "Main API")

def test_aqi_custom(year, domains=None):
    print(f"Testing Year {year} (Domains: {domains})")
    params = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-01-05",
        "hourly": "us_aqi",
        "timezone": "auto"
    }
    if domains:
        params["domains"] = domains
        
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "hourly" in data and "us_aqi" in data["hourly"]:
                sample = data['hourly']['us_aqi'][:5]
                print(f"Success! Sample: {sample}")
                if all(v is None for v in sample):
                    print("  (All values are None)")
            else:
                print("  Missing hourly/us_aqi")
        else:
            print(f"  Error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  Exception: {e}")
    print("-" * 20)

test_aqi_custom(2024)
test_aqi_custom(2020)
test_aqi_custom(2020, "cams_global")
