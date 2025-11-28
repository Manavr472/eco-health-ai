"""
FastAPI Main Application
RESTful API for Eco-Health AI Platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Prediction Agent Logger
agent_logger = logging.getLogger('prediction_agent')
agent_logger.setLevel(logging.INFO)
if not agent_logger.handlers:
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'prediction_agent.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    agent_logger.addHandler(file_handler)

from config import API_CONFIG, MUMBAI_HOSPITALS
from services.aqi_service import get_real_time_aqi, get_historical_aqi
from services.weather_service import weather_service
from services.event_service import event_service
from models.surge_predictor import surge_predictor

# Initialize FastAPI app
app = FastAPI(
    title=API_CONFIG['title'],
    description=API_CONFIG['description'],
    version=API_CONFIG['version']
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SurgePredictionRequest(BaseModel):
    hospital_id: int
    date: str

class SurgePredictionResponse(BaseModel):
    date: str
    hospital_id: int
    predicted_admissions: int
    surge_multiplier: float
    surge_level: str
    confidence: float

class RecommendationResponse(BaseModel):
    surge_level: str
    total_actions: int
    recommendations: List[dict]

class CarbonCreditResponse(BaseModel):
    credit_id: str
    carbon_tons: float
    value_usd: float
    timestamp: str
    block_hash: str


# === ROOT ENDPOINT ===

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "../dashboard/index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse(content="<h1>Eco-Health AI Platform</h1><p>Dashboard coming soon...</p>")


# === HEALTH CHECK ===

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": API_CONFIG['version']
    }


# === DATA ENDPOINTS ===

@app.get("/api/data/latest")
async def get_latest_data(hospital_id: int = 1):
    """Get latest external data (AQI, weather, events) for specific hospital location"""
    try:
        # Load latest data
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        # Get today's date
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        
        # Map to 2024 for data lookup (since we are in 2025)
        lookup_date = today.replace(year=2024).strftime("%Y-%m-%d")
        
        # Map integer ID to CSV ID
        csv_id_map = {1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "RAJ_H5"}
        target_csv_id = csv_id_map.get(hospital_id, "KEM_H1")

        # Try to find data for today (mapped to 2024), otherwise fallback to latest available
        # Filter by hospital first
        hospital_df = patient_df[patient_df['hospital_id'] == target_csv_id]
        
        if lookup_date in hospital_df['date'].dt.strftime("%Y-%m-%d").values:
            latest_data = hospital_df[hospital_df['date'] == lookup_date].iloc[0]
            latest_date = pd.to_datetime(today_str) # Use actual today for display
        else:
            latest_date = hospital_df['date'].max()
            latest_data = hospital_df[hospital_df['date'] == latest_date].iloc[0]
        
        # Get hospital coordinates
        hospital = next((h for h in MUMBAI_HOSPITALS if h["id"] == hospital_id), MUMBAI_HOSPITALS[0])
        
        # Fetch real-time AQI for hospital location
        real_aqi_data = get_real_time_aqi(latitude=hospital["lat"], longitude=hospital["lon"])
        
        # Fetch real-time Weather (Rainfall)
        weather = weather_service.get_forecast(hospital['lat'], hospital['lon'], days=1)
        today_weather = weather.get(today_str, {})
        rainfall = today_weather.get('rainfall', 0.0)
        
        # Fetch Events
        events = event_service.get_events(today_str)
        event_display = events[0] if events else "None"
        
        current_aqi = real_aqi_data['aqi'] if real_aqi_data else float(latest_data['avg_aqi'])
        
        return {
            "date": latest_date.strftime("%Y-%m-%d"),
            "aqi": current_aqi,
            "location": hospital["location"],
            "temperature_c": float(latest_data['temperature_c']),
            "rainfall_mm": float(latest_data['rainfall_mm']),
            "active_events": latest_data['active_events'] if pd.notna(latest_data['active_events']) else None,
            "total_admissions_today": int(patient_df[patient_df['date'] == lookup_date]['total_admissions'].sum())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@app.get("/api/data/stats")
async def get_data_stats():
    """Get overall data statistics"""
    try:
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        return {
            "total_records": len(patient_df),
            "date_range": {
                "start": patient_df['date'].min().strftime("%Y-%m-%d"),
                "end": patient_df['date'].max().strftime("%Y-%m-%d")
            },
            "total_admissions": int(patient_df['total_admissions'].sum()),
            "avg_daily_admissions": float(patient_df.groupby('date')['total_admissions'].sum().mean()),
            "surge_events": int(patient_df[patient_df['is_surge']].groupby('date').size().count()),
            "hospitals": int(patient_df['hospital_id'].nunique())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        


@app.get("/api/data/historical")
async def get_historical_data(hospital_id: int = 1, days: int = 30):
    """Get real historical data from CSV for accurate trends"""
    try:
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        # Get data up to today
        today = datetime.now()
        start_date = today - timedelta(days=days)
        
        # Map range to 2024 for lookup
        lookup_start = start_date.replace(year=2024)
        lookup_end = today.replace(year=2024)
        
        # Map integer ID to CSV ID
        csv_id_map = {1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "RAJ_H5"}
        target_csv_id = csv_id_map.get(hospital_id, "KEM_H1")
        
        historical_data = patient_df[
            (patient_df['date'] >= lookup_start) &
            (patient_df['date'] <= lookup_end) &
            (patient_df['hospital_id'] == target_csv_id)
        ].sort_values('date')
        
        # Remap dates back to current year for display
        display_dates = [d.replace(year=today.year).strftime('%Y-%m-%d') for d in historical_data['date']]
        
        # Fetch real historical AQI from Open-Meteo
        hospital = next((h for h in MUMBAI_HOSPITALS if h["id"] == hospital_id), MUMBAI_HOSPITALS[0])
        
        # We need to fetch data for the display dates (which are current year)
        # But wait, Open-Meteo might not have future data if today is very recent?
        # Actually, display_dates ends at 'today'. So it's fine.
        
        real_history = get_historical_aqi(
            hospital["lat"], 
            hospital["lon"], 
            display_dates[0], 
            display_dates[-1]
        )
        
        # Map API data to dates, fallback to CSV if missing
        final_aqi = []
        for date_str, csv_aqi in zip(display_dates, historical_data['avg_aqi'].tolist()):
            # Use real data if available, otherwise fallback to CSV
            base_aqi = real_history.get(date_str, csv_aqi)
            final_aqi.append(base_aqi)
            
        # Ensure the last data point (today) matches the current real-time AQI for consistency
        # This prevents discrepancy between "Current AQI" card and the chart's last point
        if display_dates and display_dates[-1] == datetime.now().strftime("%Y-%m-%d"):
            current_real = get_real_time_aqi(hospital["lat"], hospital["lon"])
            if current_real:
                final_aqi[-1] = current_real['aqi']
        
        return {
            "dates": display_dates,
            "aqi": final_aqi,
            "admissions": historical_data['total_admissions'].tolist(),
            "temperature": historical_data['temperature_c'].tolist(),
            "rainfall": historical_data['rainfall_mm'].tolist(),
            "events": historical_data['active_events'].fillna('None').tolist(),
            "surge_multiplier": historical_data['surge_multiplier'].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/correlation")
async def get_correlation_analysis(hospital_id: int = 1):
    """Analyze correlation between external factors and admissions"""
    try:
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        # Map integer ID to CSV ID
        csv_id_map = {1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "RAJ_H5"}
        target_csv_id = csv_id_map.get(hospital_id, "KEM_H1")
        
        # Filter by hospital
        hospital_data = patient_df[patient_df['hospital_id'] == target_csv_id]
        
        # Get last 90 days
        latest_date = hospital_data['date'].max ()
        start_date = latest_date - timedelta(days=90)
        recent_data = hospital_data[hospital_data['date'] >= start_date]
        
        # Identify surge events and their causes
        surges = recent_data[recent_data['is_surge'] == True].copy()
        
        surge_events = []
        for _, surge in surges.iterrows():
            causes = []
            if surge['avg_aqi'] > 200:
                causes.append(f"High AQI ({int(surge['avg_aqi'])})")
            if surge['rainfall_mm'] > 50:
                causes.append(f"Heavy Rainfall ({int(surge['rainfall_mm'])}mm)")
            if pd.notna(surge['active_events']) and surge['active_events'] != 'None':
                causes.append(f"Event: {surge['active_events']}")
            
            surge_events.append({
                'date': surge['date'].strftime('%Y-%m-%d'),
                'admissions': int(surge['total_admissions']),
                'multiplier': float(surge['surge_multiplier']),
                'causes': causes,
                'severity': surge['surge_severity']
            })
        
        return {
            'surge_events': surge_events[-10:],  # Last 10 surges
            'correlations': {
                'aqi_vs_admissions': float(recent_data[['avg_aqi', 'total_admissions']].corr().iloc[0, 1]),
                'rainfall_vs_admissions': float(recent_data[['rainfall_mm', 'total_admissions']].corr().iloc[0, 1]),
                'temp_vs_admissions': float(recent_data[['temperature_c', 'total_admissions']].corr().iloc[0, 1])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === PREDICTION ENDPOINTS ===

@app.get("/api/predictions/surge")
async def predict_surge(hospital_id: int = 1, days_ahead: int = 7):
    """Get surge predictions for next N days (max 14) using Gemini + Historical Data"""
    if days_ahead > 14:
        days_ahead = 14
        
    try:
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        # Start predictions from tomorrow
        start_date = datetime.now()
        
        # 1. Fetch Environmental Data (Forecasts)
        hospital = next((h for h in MUMBAI_HOSPITALS if h['id'] == hospital_id), MUMBAI_HOSPITALS[0])
        lat, lon = hospital['lat'], hospital['lon']
        
        # AQI Forecast (Limit to 4 days as API restricts range)
        aqi_end_date = start_date + timedelta(days=4)
        aqi_data = get_historical_aqi(lat, lon, 
                                    (start_date + timedelta(days=1)).strftime('%Y-%m-%d'), 
                                    aqi_end_date.strftime('%Y-%m-%d'))
        
        # Weather Forecast
        weather_data = weather_service.get_forecast(lat, lon, days=days_ahead + 1)
        
        predictions = []
        
        for days in range(1, days_ahead + 1):
            target_date = start_date + timedelta(days=days)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Get inputs for this day
            daily_aqi = aqi_data.get(date_str, 150) # Default to Moderate if missing
            daily_weather = weather_data.get(date_str, {})
            daily_events = event_service.get_events(date_str)
            
            # Predict using Gemini-enhanced model
            prediction = surge_predictor.predict(date_str, daily_aqi, daily_weather, daily_events)
            
            # Calculate admissions (Hybrid: Historical Baseline * Live Multiplier)
            # Find historical baseline from previous year (2024)
            lookup_date = target_date.replace(year=2024)
            
            # Map integer ID to CSV ID
            # Updated to match all 14 hospitals from data
            csv_id_map = {
                1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "HIN_H5",
                6: "LIL_H6", 7: "NAN_H7", 8: "BOM_H8", 9: "JAS_H9", 10: "BRE_H10",
                11: "SAI_H11", 13: "JUP_H13", 14: "COO_H14", 15: "HBT_H15"
            }
            target_csv_id = csv_id_map.get(hospital_id, "KEM_H1")
            
            hist_data = patient_df[
                (patient_df['date'].dt.date == lookup_date.date()) &
                (patient_df['hospital_id'] == target_csv_id)
            ]
            
            baseline_admissions = 120 # Default
            if not hist_data.empty:
                baseline_admissions = int(hist_data.iloc[0]['baseline_admissions'])
            
            predicted_admissions = int(baseline_admissions * prediction['multiplier'])
            
            predictions.append({
                "date": date_str,
                "predicted_admissions": predicted_admissions,
                "surge_multiplier": prediction['multiplier'],
                "surge_level": prediction['severity'],
                "surge_reasons": prediction['narrative'], # AI Narrative
                "confidence": 0.85
            })
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === RECOMMENDATION ENDPOINTS ===

@app.get("/api/recommendations")
async def get_recommendations(hospital_id: int = 1, days_ahead: int = 5):
    """Get AI agent recommendations for a specific hospital"""
    try:
        from agent.resource_recommendation_agent import ResourceRecommendationAgent
        
        # Load patient data
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        patient_df['date'] = pd.to_datetime(patient_df['date'])
        
        # Get today's date
        today = datetime.now()
        target_date = today + timedelta(days=days_ahead)
        
        # Map to 2024 for lookup
        lookup_start = today.replace(year=2024)
        lookup_end = target_date.replace(year=2024)
        
        # Map integer ID to CSV ID
        csv_id_map = {1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "RAJ_H5"}
        target_csv_id = csv_id_map.get(hospital_id, "KEM_H1")
        
        # Get surge prediction data for next N days
        future_data = patient_df[
            (patient_df['date'] > lookup_start) & 
            (patient_df['date'] <= lookup_end) &
            (patient_df['hospital_id'] == target_csv_id)
        ]
        
        if future_data.empty:
            return {"message": "No prediction data available"}
        
        # Find the highest surge in the next period
        max_surge_row = future_data.loc[future_data['surge_multiplier'].idxmax()]
        
        surge_prediction = {
            'date': max_surge_row['date'].strftime('%Y-%m-%d'),
            'predicted_admissions': int(max_surge_row['total_admissions']),
            'surge_multiplier': float(max_surge_row['surge_multiplier']),
            'resource_forecast': {
                'doctors_needed': int(max_surge_row['total_admissions'] / 15),
                'nurses_needed': int(max_surge_row['total_admissions'] / 5),
                'support_staff_needed': int(max_surge_row['total_admissions'] / 10),
                'ppe_kits': int(max_surge_row['total_admissions'] * 2),
                'oxygen_liters': int(max_surge_row['total_admissions'] * 10),
                'iv_fluids_ml': int(max_surge_row['total_admissions'] * 500),
                'medications_units': int(max_surge_row['total_admissions'] * 5),
                'bed_linens': int(max_surge_row['total_admissions'] * 2)
            }
        }
        
        # Current resources (simulated - in production would come from hospital DB)
        current_resources = {
            'doctors': 12,
            'nurses': 35,
            'support_staff': 18,
            'ppe_kits': 200,
            'oxygen_liters': 1000,
            'iv_fluids_ml': 50000,
            'medications_units': 500,
            'bed_linens': 300
        }
        
        # Initialize agent and get plan
        agent = ResourceRecommendationAgent()
        plan = agent.generate_comprehensive_resource_plan(
            surge_prediction=surge_prediction,
            current_resources=current_resources,
            days_until_surge=days_ahead
        )
        
        # Format recommendations for dashboard
        recommendations = []
        
        # Staff recommendations
        staff_needed = []
        for staff_type, details in plan['staff_allocation'].items():
            if details['to_deploy'] > 0:
                staff_needed.append(f"{details['to_deploy']} {staff_type.replace('_', ' ')}")
        
        if staff_needed:
            recommendations.append({
                'category': 'Staff Deployment',
                'priority': 'HIGH' if plan['readiness_score'] < 80 else 'MEDIUM',
                'action': 'Deploy Additional Medical Staff',
                'details': [
                    f"Activate on-call roster for {item}"
                    for item in staff_needed[:3]
                ]
            })
        
        # Supply recommendations
        urgent_supplies = [s for s in plan['supply_procurement'] if s['priority'] > 70]
        if urgent_supplies:
            supply_details = []
            for supply in urgent_supplies[:3]:
                supply_name = supply['supply'].replace('_', ' ').title()
                supply_details.append(f"Order {supply['to_order']:,} {supply_name}")
            
            recommendations.append({
                'category': 'Supply Procurement',
                'priority': 'URGENT' if any(s['priority'] > 80 for s in urgent_supplies) else 'HIGH',
                'action': 'Emergency Supply Ordering',
                'details': supply_details
            })
        
        # Public health advisory
        # Use real-time AQI if available, otherwise fallback to prediction
        
        # Get hospital coordinates
        hospital = next((h for h in MUMBAI_HOSPITALS if h["id"] == hospital_id), MUMBAI_HOSPITALS[0])
        
        real_aqi_data = get_real_time_aqi(latitude=hospital["lat"], longitude=hospital["lon"])
        current_aqi = real_aqi_data['aqi'] if real_aqi_data else max_surge_row.get('avg_aqi', 0)
        
        if current_aqi > 200:
            recommendations.append({
                'category': 'Public Health Advisory',
                'priority': 'MEDIUM',
                'action': 'Issue AQI Alert to Community',
                'details': [
                    f"Current AQI is {current_aqi} (Poor)",
                    'Minimize outdoor activities due to poor air quality',
                    'Advise vulnerable groups to stay indoors',
                    'Visit hospital only for emergencies'
                ]
            })
        
        # Facility management
        if surge_prediction['surge_multiplier'] > 1.5:
            recommendations.append({
                'category': 'Facility Management',
                'priority': 'NORMAL',
                'action': 'Prepare Additional Bed Capacity',
                'details': [
                    f"Convert wards to surge capacity",
                    f"Prepare {int(surge_prediction['predicted_admissions'] * 0.2)} additional beds",
                    'Stock extra bed linens and equipment'
                ]
            })
        
        return {
            'surge_info': {
                'date': surge_prediction['date'],
                'multiplier': surge_prediction['surge_multiplier'],
                'predicted_admissions': surge_prediction['predicted_admissions']
            },
            'readiness_score': plan['readiness_score'],
            'recommendations': recommendations,
            'action_timeline': plan['action_timeline'][:7]  # Top 7 actions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === AGENT SIMULATION ENDPOINT ===

@app.post("/api/agent/simulate")
async def simulate_agent_response(scenario: str = "diwali_surge"):
    """Simulate AI agent response for a specific scenario"""
    try:
        from agent.resource_recommendation_agent import ResourceRecommendationAgent
        
        scenarios = {
            'diwali_surge': {
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'predicted_admissions': 300,
                'surge_multiplier': 2.0,
                'resource_forecast': {
                    'doctors_needed': 20,
                    'nurses_needed': 60,
                    'support_staff_needed': 30,
                    'ppe_kits': 600,
                    'oxygen_liters': 3000,
                    'iv_fluids_ml': 150000,
                    'medications_units': 1500,
                    'bed_linens': 600
                }
            },
            'monsoon_surge': {
                'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'predicted_admissions': 240,
                'surge_multiplier': 1.6,
                'resource_forecast': {
                    'doctors_needed': 16,
                    'nurses_needed': 48,
                    'support_staff_needed': 24,
                    'ppe_kits': 480,
                    'oxygen_liters': 2400,
                    'iv_fluids_ml': 120000,
                    'medications_units': 1200,
                    'bed_linens': 480
                }
            }
        }
        
        surge_prediction = scenarios.get(scenario, scenarios['diwali_surge'])
        
        current_resources = {
            'doctors': 12, 'nurses': 35, 'support_staff': 18,
            'ppe_kits': 200, 'oxygen_liters': 1000,
            'iv_fluids_ml': 50000, 'medications_units': 500,
            'bed_linens': 300
        }
        
        agent = ResourceRecommendationAgent()
        plan = agent.generate_comprehensive_resource_plan(
            surge_prediction=surge_prediction,
            current_resources=current_resources,
            days_until_surge=5
        )
        
        return {
            'scenario': scenario,
            'plan': plan,
            'agent_status': 'active'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === SUSTAINABILITY ENDPOINTS ===

@app.get("/api/sustainability/carbon-credits")
async def get_carbon_credits():
    """Get all carbon credits"""
    try:
        # Load blockchain data if it exists
        blockchain_path = "data/carbon_credit_blockchain.json"
        
        if os.path.exists(blockchain_path):
            import json
            with open(blockchain_path, 'r') as f:
                blockchain_data = json.load(f)
            
            return {
                "total_credits_issued": len(blockchain_data.get('registry', [])),
                "total_tons_co2": blockchain_data.get('total_credits', 0),
                "credits": blockchain_data.get('registry', [])
            }
        else:
            return {
                "total_credits_issued": 0,
                "total_tons_co2": 0,
                "credits": [],
                "message": "No carbon credits generated yet"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sustainability/impact")
async def get_sustainability_impact():
    """Get overall sustainability impact"""
    try:
        # Calculate from patient data
        patient_df = pd.read_csv("data/daily_patient_admissions_2019_2024.csv")
        
        # Simplified calculation
        total_surge_events = patient_df[patient_df['is_surge']].groupby('date').size().count()
        
        # Estimate: avg 2 tons CO2 reduction per surge event
        estimated_reduction_tons = total_surge_events * 2.0
        estimated_value_usd = estimated_reduction_tons * 25
        
        return {
            "total_surge_events_optimized": int(total_surge_events),
            "estimated_carbon_reduction_tons": float(estimated_reduction_tons),
            "estimated_value_usd": float(estimated_value_usd),
            "avg_reduction_per_event_tons": 2.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === HOSPITAL ENDPOINTS ===

@app.get("/api/hospitals")
async def get_hospitals():
    """Get list of hospitals"""
    return {
        "hospitals": MUMBAI_HOSPITALS
    }


# Mount static files for dashboard
dashboard_dir = os.path.join(os.path.dirname(__file__), "../dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        reload=API_CONFIG['reload']
    )
