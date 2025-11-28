"""
Data Accumulator Agent
Fuses Monthly Hospital Stats with Daily Environmental Data (API) to create a comprehensive Daily Dataset.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import time
import calendar
import google.generativeai as genai
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MUMBAI_COORDS, MUMBAI_STATIONS, SURGE_FACTORS
from services.aqi_service import get_historical_aqi
from services.weather_service import weather_service
from data_generators.event_generator import EventGenerator

# Load environment variables
load_dotenv(".env.local")

class DataAccumulatorAgent:
    def __init__(self):
        self.start_date = datetime(2019, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        self.bed_file = r"real_data/total_bed_count.csv"
        self.monthly_file = r"real_data/synthetic_mumbai_monthly_full (1).csv"
        self.output_file = r"data/daily_patient_admissions_2019_2024.csv"
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            print("Gemini AI initialized.")
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found. AI features disabled.")
            
        self.aqi_cache = {} # Cache for monthly AQI generation
        
    def load_metadata(self):
        """Load hospital metadata"""
        print("Loading hospital metadata...")
        self.hospitals = pd.read_csv(self.bed_file)
        self.hospital_map = {}
        for _, row in self.hospitals.iterrows():
            full_id = row['Hospital_id']
            simple_id = full_id.split('_')[0]
            
            # Manual mapping adjustment
            if 'LOK' in simple_id: simple_id = 'SION'
            if 'NAI' in simple_id: simple_id = 'NAIR'
            if 'HIN' in simple_id: simple_id = 'HINDUJA'
            if 'LIL' in simple_id: simple_id = 'LILAVATI'
            if 'NAN' in simple_id: simple_id = 'NANAVATI'
            if 'BOM' in simple_id: simple_id = 'BOMBAY'
            if 'JAS' in simple_id: simple_id = 'JASLOK'
            if 'BRE' in simple_id: simple_id = 'BREACH'
            if 'SAI' in simple_id: simple_id = 'SAIFEE'
            if 'JUP' in simple_id: simple_id = 'JUPITER'
            if 'COO' in simple_id: simple_id = 'COOPER'
            
            # Skip Apollo
            if simple_id == 'APOLLO': continue
            
            self.hospital_map[simple_id] = {
                'full_id': row['Hospital_id'],
                'name': row['Hospital Name'],
                'location': row['Location'],
                'beds': row['total_number_of_beds']
            }
            
        print(f"Mapped {len(self.hospital_map)} hospitals.")

    def fetch_environmental_data(self):
        """Fetch historical AQI and Weather for the entire period (Chunked)"""
        print(f"Fetching environmental data from {self.start_date.date()} to {self.end_date.date()}...")
        
        self.weather_history = {}
        self.aqi_history = {}
        
        # Iterate year by year to avoid timeouts
        current_date = self.start_date
        while current_date <= self.end_date:
            year_end = datetime(current_date.year, 12, 31)
            if year_end > self.end_date:
                year_end = self.end_date
                
            start_str = current_date.strftime('%Y-%m-%d')
            end_str = year_end.strftime('%Y-%m-%d')
            
            print(f"  Fetching chunk: {start_str} to {end_str}...")
            
            try:
                # 1. Weather
                weather_chunk = weather_service.get_historical_weather(
                    MUMBAI_COORDS['latitude'], MUMBAI_COORDS['longitude'],
                    start_str, end_str
                )
                if weather_chunk:
                    self.weather_history.update(weather_chunk)
                else:
                    print(f"    Warning: No weather data for {start_str}")
                
                # 2. AQI
                aqi_chunk = get_historical_aqi(
                    MUMBAI_COORDS['latitude'], MUMBAI_COORDS['longitude'],
                    start_str, end_str
                )
                if aqi_chunk:
                    self.aqi_history.update(aqi_chunk)
                else:
                    print(f"    Warning: No AQI data for {start_str}")
                    
            except Exception as e:
                print(f"    Error fetching chunk {start_str}: {e}")
            
            # Move to next year
            current_date = year_end + timedelta(days=1)
            time.sleep(1) # Polite delay
        
        print(f"Fetched {len(self.weather_history)} weather records and {len(self.aqi_history)} AQI records.")
        
        # 3. Events
        print("Generating Events...")
        event_gen = EventGenerator()
        event_gen.start_date = self.start_date
        event_gen.end_date = self.end_date
        events_df = event_gen.generate()
        self.daily_events = event_gen.create_daily_event_marker(events_df)
        self.event_map = self.daily_events.set_index('date').to_dict('index')

    def get_gemini_aqi_for_month(self, year, month):
        """Use Gemini to generate realistic daily AQI for a whole month"""
        cache_key = f"{year}-{month}"
        if cache_key in self.aqi_cache:
            return self.aqi_cache[cache_key]
            
        if not self.model:
            days = calendar.monthrange(year, month)[1]
            return [self.get_fallback_aqi_heuristic(datetime(year, month, d)) for d in range(1, days+1)]

        try:
            days_in_month = calendar.monthrange(year, month)[1]
            prompt = f"""
            Generate a JSON list of {days_in_month} integers representing realistic daily AQI (Air Quality Index) values for Mumbai, India in {calendar.month_name[month]} {year}.
            Context:
            - Mumbai AQI is generally poor (150-300) in winter (Nov-Feb).
            - Moderate (100-150) in summer (Mar-May).
            - Good (50-80) in monsoon (Jun-Sep) due to rain.
            - Post-monsoon (Oct) is moderate.
            - 2020 had cleaner air due to lockdown.
            - Return ONLY the JSON list of integers, no markdown, no text.
            Example: [150, 155, 148, ...]
            """
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")
            import json
            aqi_list = json.loads(text)
            
            if len(aqi_list) != days_in_month:
                if len(aqi_list) < days_in_month:
                    aqi_list += [aqi_list[-1]] * (days_in_month - len(aqi_list))
                else:
                    aqi_list = aqi_list[:days_in_month]
            
            self.aqi_cache[cache_key] = aqi_list
            print(f"  Generated synthetic AQI for {calendar.month_name[month]} {year} using Gemini.")
            return aqi_list
            
        except Exception as e:
            print(f"  Error generating AQI with Gemini: {e}")
            days = calendar.monthrange(year, month)[1]
            return [self.get_fallback_aqi_heuristic(datetime(year, month, d)) for d in range(1, days+1)]

    def get_fallback_aqi_heuristic(self, date_obj):
        """Legacy heuristic fallback"""
        month = date_obj.month
        if month in [11, 12, 1, 2]: base, var = 200, 50
        elif month in [3, 4, 5]: base, var = 120, 30
        elif month in [6, 7, 8, 9]: base, var = 60, 20
        else: base, var = 100, 25
        return int(np.random.normal(base, var))

    def generate_surge_narrative(self, date_str, surge_mult, reasons):
        """Generate a descriptive surge reason using Gemini"""
        if not self.model or surge_mult < 1.3:
            return ", ".join(reasons) if reasons else "None"
            
        try:
            prompt = f"""
            Write a very short (max 10 words) medical/environmental reason for a hospital surge in Mumbai on {date_str}.
            Factors: {', '.join(reasons)}.
            Surge Multiplier: {surge_mult}x.
            Output simple text like: "Severe smog causing respiratory spike" or "Monsoon outbreak of waterborne diseases".
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return ", ".join(reasons)

    def generate_daily_data(self):
        """Core logic to fuse data"""
        print("Processing monthly data and generating daily records...")
        monthly_df = pd.read_csv(self.monthly_file)
        monthly_df['date'] = pd.to_datetime(monthly_df['date'], format='%d-%m-%Y')
        
        daily_records = []
        
        # Iterate through each month in the dataset
        for _, row in monthly_df.iterrows():
            month_start = row['date']
            hospital_key = row['hospital_id']
            
            if hospital_key not in self.hospital_map:
                if hospital_key == 'HBT': meta = self.hospital_map.get('HBT')
                else: continue
            else:
                meta = self.hospital_map[hospital_key]
            
            if not meta: continue

            days_in_month = calendar.monthrange(month_start.year, month_start.month)[1]
            total_monthly_ipd = row['ipd_count']
            avg_daily_ipd = total_monthly_ipd / days_in_month
            
            # Pre-fetch Gemini AQI for this month if needed
            month_aqi_list = []
            if any(d.strftime('%Y-%m-%d') not in self.aqi_history for d in [month_start.replace(day=i) for i in range(1, days_in_month+1)]):
                 month_aqi_list = self.get_gemini_aqi_for_month(month_start.year, month_start.month)

            for day in range(1, days_in_month + 1):
                current_date = month_start.replace(day=day)
                date_str = current_date.strftime('%Y-%m-%d')
                
                weather = self.weather_history.get(date_str, {'max_temp': 30, 'rainfall': 0})
                
                if date_str in self.aqi_history:
                    aqi = self.aqi_history[date_str]
                else:
                    aqi = month_aqi_list[day-1] if month_aqi_list else 100
                
                event_data = self.event_map.get(current_date, {})
                
                temp = weather['max_temp']
                rain = weather['rainfall']
                has_event = event_data.get('has_event', False)
                event_name = event_data.get('active_events', None)
                
                is_weekend = current_date.weekday() >= 5
                weekend_factor = 0.85 if is_weekend else 1.05
                noise = np.random.uniform(0.8, 1.2)
                
                surge_mult = 1.0
                reasons = []
                
                if aqi > 200: 
                    surge_mult += 0.2
                    reasons.append("Poor AQI")
                if aqi > 300:
                    surge_mult += 0.3
                    reasons.append("Very Poor AQI")
                if rain > 50:
                    surge_mult += 0.3
                    reasons.append("Heavy Rainfall")
                if temp > 36:
                    surge_mult += 0.2
                    reasons.append("Heatwave")
                if has_event:
                    surge_mult += 0.2
                    reasons.append(f"Event: {event_name}")
                
                base_admissions = int(avg_daily_ipd * weekend_factor * noise)
                total_admissions = int(base_admissions * surge_mult)
                
                weights = {'respiratory': 0.15, 'waterborne': 0.10, 'heat': 0.05, 'trauma': 0.20, 'other': 0.50}
                if aqi > 200: weights['respiratory'] += 0.2
                if rain > 20: weights['waterborne'] += 0.2
                if temp > 35: weights['heat'] += 0.15
                if has_event: weights['trauma'] += 0.15
                
                total_weight = sum(weights.values())
                weights = {k: v/total_weight for k, v in weights.items()}
                
                resp_adm = int(total_admissions * weights['respiratory'])
                water_adm = int(total_admissions * weights['waterborne'])
                heat_adm = int(total_admissions * weights['heat'])
                trauma_adm = int(total_admissions * weights['trauma'])
                other_adm = total_admissions - (resp_adm + water_adm + heat_adm + trauma_adm)
                
                severity = "None"
                if surge_mult > 1.5: severity = "Major"
                elif surge_mult > 1.2: severity = "Moderate"
                elif surge_mult > 1.1: severity = "Minor"
                
                surge_narrative = self.generate_surge_narrative(date_str, surge_mult, reasons)
                
                daily_records.append({
                    'date': date_str,
                    'hospital_id': meta['full_id'],
                    'Hospital name': meta['name'],
                    'Location': meta['location'],
                    'total_number_of_beds': meta['beds'],
                    'total_admissions': total_admissions,
                    'baseline_admissions': base_admissions,
                    'surge_multiplier': round(surge_mult, 2),
                    'is_surge': surge_mult > 1.1,
                    'surge_severity': severity,
                    'surge_reasons': surge_narrative,
                    'respiratory_admissions': resp_adm,
                    'waterborne_admissions': water_adm,
                    'heat_related_admissions': heat_adm,
                    'trauma_admissions': trauma_adm,
                    'other_admissions': other_adm,
                    'avg_aqi': aqi,
                    'temperature_c': temp,
                    'rainfall_mm': rain,
                    'active_events': event_name if has_event else "None"
                })
                
        df = pd.DataFrame(daily_records)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df.to_csv(self.output_file, index=False)
        print(f"Successfully generated {len(df)} daily records from 2019-2024.")
        print(f"Saved to: {self.output_file}")

if __name__ == "__main__":
    agent = DataAccumulatorAgent()
    agent.load_metadata()
    agent.fetch_environmental_data()
    agent.generate_daily_data()
