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
from fastapi import FastAPI, HTTPException, File, UploadFile
import io
from src.models.carbon_models import (
    ForecastRecord, CarbonReport, EmissionResult, HospitalReport,
    CarbonCreditReport, BEECompliance, EnergySavingsPlan, 
    CarbonCreditDetails, NABHVerifiedCredit, EnergyMeasure
)
from src.sustainability.energy import estimate_energy
from src.sustainability.emissions import calculate_carbon
from src.sustainability.baseline import estimate_baseline_energy, create_energy_alert
from src.sustainability.llm import generate_hospital_advisory, generate_general_advisory
from src.sustainability.llm_energy import estimate_energy_smart
from src.sustainability.bee_compliance import assess_bee_compliance, calculate_epi
from src.sustainability.savings_calculator import generate_savings_report

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Prediction Agent Logger
agent_logger = logging.getLogger('prediction_agent')
agent_logger.setLevel(logging.INFO)
if not agent_logger.handlers:
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'prediction_agent.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    agent_logger.addHandler(file_handler)

from src.core.config import API_CONFIG, MUMBAI_HOSPITALS
from src.services.aqi_service import get_real_time_aqi, get_historical_aqi
from src.services.weather_service import weather_service
from src.services.event_service import event_service
from src.models.surge_predictor import surge_predictor

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
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse(content="<h1>Eco-Health AI Platform</h1><p>Dashboard not found.</p>")

# Mount UI directory for static files (css, js)
app.mount("/css", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "js")), name="js")



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
        
        # Fetch Events using event_service
        events = event_service.get_events(today_str)
        event_display = ', '.join(events) if events else None
        
        current_aqi = real_aqi_data['aqi'] if real_aqi_data else float(latest_data['avg_aqi'])
        
        return {
            "date": latest_date.strftime("%Y-%m-%d"),
            "aqi": current_aqi,
            "location": hospital["location"],
            "temperature_c": float(latest_data['temperature_c']),
            "rainfall_mm": rainfall,  # Use live weather data
            "active_events": event_display,  # Use live event service data
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
    """
    Get resource recommendations for hospital (NESCO-based)
    Kept for backward compatibility, redirects to resource service
    """
    try:
        from services.resource_service import resource_service
        
        # Map integer ID to CSV ID
        csv_id_map = {
            1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "HIN_H5",
            6: "LIL_H6", 7: "NAN_H7", 8: "BOM_H8", 9: "JAS_H9", 10: "BRE_H10",
            11: "SAI_H11", 13: "JUP_H13", 14: "COO_H14", 15: "HBT_H15"
        }
        target_hospital_id = csv_id_map.get(hospital_id, "KEM_H1")
        
        # Get resource recommendations
        result = resource_service.get_recommendations(target_hospital_id)
        
        if isinstance(result, dict) and "error" in result:
            return {"message": "No recommendation data available"}
        
        # Format for backward compatibility with old dashboard format
        recommendation_data = result if isinstance(result, dict) else result[0]
        supplies = recommendation_data.get('supplies_status', [])
        
        # Convert to old format for compatibility
        recommendations = []
        
        # Group by status
        critical_supplies = [s for s in supplies if s['status'] == 'CRITICAL']
        low_supplies = [s for s in supplies if s['status'] == 'LOW']
        
        if critical_supplies:
            recommendations.append({
                'category': 'Critical Supply Shortage',
                'priority': 'URGENT',
                'action': 'ORDER IMMEDIATELY - Critical Stock Levels',
                'icon': '🚨',
                'details': [
                    f"{s['item_name']}: {s['current_stock']}/{s['projected_need']} ({s['stock_percentage']:.0f}%)"
                    for s in critical_supplies[:5]
                ]
            })
        
        if low_supplies:
            recommendations.append({
                'category': 'Low Supply Warning',
                'priority': 'HIGH',
                'action': 'Restock Soon - Running Low',
                'icon': '⚠️',
                'details': [
                    f"{s['item_name']}: Order {s['quantity_to_order']} units"
                    for s in low_supplies[:5]
                ]
            })
        
        # Add readiness summary
        summary = recommendation_data.get('summary', {})
        total_ok = summary.get('ok_items', 0)
        total_items = summary.get('total_items', 10)
        readiness_score = int((total_ok / total_items) * 100) if total_items > 0 else 100
        
        return {
            'readiness_score': readiness_score,
            'recommendations': recommendations,
            'action_timeline': [
                {
                    'date': 'Today',
                    'action': f"Order {s['item_name']}: {s['quantity_to_order']} units",
                    'priority': 'URGENT' if s['status'] == 'CRITICAL' else 'HIGH',
                    'category': 'Supply'
                }
                for s in supplies if s['quantity_to_order'] > 0
            ][:7]
        }
        
    except Exception as e:
        agent_logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/forecast")
async def get_department_forecast(hospital_id: int = 1):
    """Get department-level admissions forecast for a hospital"""
    try:
        from services.resource_service import resource_service
        
        # Map integer ID to CSV ID
        csv_id_map = {
            1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "HIN_H5",
            6: "LIL_H6", 7: "NAN_H7", 8: "BOM_H8", 9: "JAS_H9", 10: "BRE_H10",
            11: "SAI_H11", 13: "JUP_H13", 14: "COO_H14", 15: "HBT_H15"
        }
        target_hospital_id = csv_id_map.get(hospital_id, "KEM_H1")
        
        # Get surge data which has department breakdowns
        surge_data = resource_service.get_latest_surge_data()
        
        if not surge_data or target_hospital_id not in surge_data:
            return {"error": "No department data available"}
        
        admissions = surge_data[target_hospital_id]
        
        # Get predictions for surge growth
       
        # For now use a simple 1.3x multiplier for predictions
        # In future, could integrate with surge_predictor for more accurate forecasts
        surge_multiplier = 1.3
        
        # Department mapping - convert from admission types to hospital departments
        departments = {
            "emergency": {
                "current": admissions.get('trauma', 0),
                "predicted": int(admissions.get('trauma', 0) * surge_multiplier),
                "name": "Emergency"
            },
            "respiratory": {
                "current": admissions.get('respiratory', 0),
                "predicted": int(admissions.get('respiratory', 0) * surge_multiplier),
                "name": "Respiratory"
            },
            "cardiology": {
                "current": int(admissions.get('other', 0) * 0.3),  # 30% of other
                "predicted": int(admissions.get('other', 0) * 0.3 * 1.22),
                "name": "Cardiology"
            },
            "general": {
                "current": admissions.get('waterborne', 0) +  admissions.get('heat_related', 0) + int(admissions.get('other', 0) * 0.7),
                "predicted": int((admissions.get('waterborne', 0) + admissions.get('heat_related', 0) + int(admissions.get('other', 0) * 0.7)) * 1.14),
                "name": "General Ward"
            }
        }
        
        return {
            "hospital_id": target_hospital_id,
            "departments": departments,
            "total_current": sum(d['current'] for d in departments.values()),
            "total_predicted": sum(d['predicted'] for d in departments.values())
        }
        
    except Exception as e:
        agent_logger.error(f"Department forecast error: {e}")
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


# === RESOURCE RECOMMENDATIONS ENDPOINT ===

@app.get("/api/resources/recommendations")
async def get_resource_recommendations(hospital_id: Optional[int] = None):
    """
    Get medical supply recommendations based on surge predictions
    Uses NESCO logic without modifying surge_predictor
    """
    try:
        from services.resource_service import resource_service
        
        # Map integer ID to CSV ID if provided
        target_hospital_id = None
        if hospital_id:
            csv_id_map = {
                1: "KEM_H1", 2: "LOK_H2", 3: "NAI_H3", 4: "JJ_H4", 5: "HIN_H5",
                6: "LIL_H6", 7: "NAN_H7", 8: "BOM_H8", 9: "JAS_H9", 10: "BRE_H10",
                11: "SAI_H11", 13: "JUP_H13", 14: "COO_H14", 15: "HBT_H15"
            }
            target_hospital_id = csv_id_map.get(hospital_id)
            
            if not target_hospital_id:
                raise HTTPException(status_code=404, detail=f"Hospital ID {hospital_id} not found")
        
        # Get recommendations
        recommendations = resource_service.get_recommendations(target_hospital_id)
        
        return {
            "success": True,
            "recommendations": recommendations if isinstance(recommendations, list) else [recommendations]
        }
        
    except Exception as e:
        agent_logger.error(f"Resource recommendations error: {e}")
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


# Carbon-Agent

@app.post("/analyze", response_model=CarbonReport)
async def analyze_surge_data(file: UploadFile = File(...)):
    """
    Analyzes a patient surge CSV file and returns a detailed carbon emission report
    with per-hospital energy monitoring and baseline alerts.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV.")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Validate columns
        required_cols = {"timestamp", "hospital_id", "total_admissions", "baseline_admissions", 
                        "surge_multiplier", "surge_reasons", "respiratory_admissions", 
                        "waterborne_admissions", "heat_related_admissions", "trauma_admissions", 
                        "other_admissions"}
        if not required_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Missing columns. Required: {required_cols}")
            
        # Initialize aggregates
        hospital_reports: List[HospitalReport] = []
        results: List[EmissionResult] = []
        total_patients = 0
        total_energy = 0.0
        total_emissions = 0.0
        
        # Process each row (each represents a hospital forecast)
        for index, row in df.iterrows():
            # Validate Row
            try:
                record = ForecastRecord(**row.to_dict())
            except Exception as e:
                print(f"Skipping invalid row {index}: {e}")
                continue
            
            # Calculate surge patients
            surge_patients = record.total_admissions - record.baseline_admissions
            
            # Prepare data for LLM energy estimation
            forecast_data = {
                "baseline_admissions": record.baseline_admissions,
                "respiratory_admissions": record.respiratory_admissions,
                "waterborne_admissions": record.waterborne_admissions,
                "heat_related_admissions": record.heat_related_admissions,
                "trauma_admissions": record.trauma_admissions,
                "other_admissions": record.other_admissions
            }
            
            # 1. Estimate CURRENT energy (for total admissions)
            current_energy_kwh, energy_reasoning = estimate_energy_smart(forecast_data)
            
            # 2. Estimate BASELINE energy (for baseline admissions only)
            baseline_energy_kwh = estimate_baseline_energy(
                baseline_admissions=record.baseline_admissions,
                duration_days=7  # Default 7-day surge period
            )
            
            # 3. Create energy alert (compare current vs baseline)
            energy_alert = create_energy_alert(
                current_energy_kwh=current_energy_kwh,
                baseline_energy_kwh=baseline_energy_kwh
            )
            
            # 4. Calculate Carbon Emissions
            emission_result = calculate_carbon(
                record_id=f"{record.hospital_id}-{record.timestamp}",
                energy_kwh=current_energy_kwh,
                scope="Scope 2",
                energy_reasoning=energy_reasoning
            )
            
            # 5. Generate hospital-specific solutions
            hospital_data = {
                "hospital_id": record.hospital_id,
                "alert_level": energy_alert.alert_level.value,
                "surge_reasons": record.surge_reasons,
                "current_energy_kwh": current_energy_kwh,
                "baseline_energy_kwh": baseline_energy_kwh,
                "percentage_above_baseline": energy_alert.percentage_above_baseline,
                "surge_patients": surge_patients
            }
            solutions = generate_hospital_advisory(hospital_data)
            
            # 6. Create hospital report
            hospital_report = HospitalReport(
                hospital_id=record.hospital_id,
                timestamp=record.timestamp,
                surge_patients=surge_patients,
                baseline_admissions=record.baseline_admissions,
                total_admissions=record.total_admissions,
                surge_reasons=record.surge_reasons,
                current_energy_kwh=round(current_energy_kwh, 2),
                baseline_energy_kwh=round(baseline_energy_kwh, 2),
                energy_alert=energy_alert,
                emissions_kg=round(emission_result.total_emissions_kg, 2),
                emissions_tons=round(emission_result.total_emissions_tons, 2),
                solutions=solutions,
                emission_result=emission_result
            )
            hospital_reports.append(hospital_report)
            
            # Update aggregates
            total_patients += surge_patients
            total_energy += current_energy_kwh
            total_emissions += emission_result.total_emissions_kg
            results.append(emission_result)
            
        # Generate overall advisory
        summary_data = {
            "total_patients": total_patients,
            "total_energy": round(total_energy, 2),
            "total_emissions": round(total_emissions, 2),
            "surge_reasons": ", ".join(set([r.surge_reasons for r in hospital_reports]))
        }
        general_advisory = generate_general_advisory(summary_data)
        
        return CarbonReport(
            total_surge_patients=total_patients,
            total_energy_kwh=round(total_energy, 2),
            total_emissions_kg=round(total_emissions, 2),
            hospital_reports=hospital_reports,
            results=results,
            general_advisory=general_advisory
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/carbon/monitor", response_model=CarbonReport)
async def monitor_live_carbon():
    """
    Monitor real-time carbon emissions based on the latest surge predictions.
    Reads from the continuous surge monitoring system.
    """
    csv_path = "data/continuous_surge_predictions.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Live surge data not found. Ensure continuous_surge_monitor.py is running.")
        
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        
        if df.empty:
             raise HTTPException(status_code=404, detail="No data available in surge monitor.")
             
        # Filter for the LATEST batch of predictions (most recent timestamp)
        latest_timestamp = df['timestamp'].max()
        latest_df = df[df['timestamp'] == latest_timestamp]
        
        # Initialize aggregates
        hospital_reports: List[HospitalReport] = []
        results: List[EmissionResult] = []
        total_patients = 0
        total_energy = 0.0
        total_emissions = 0.0
        
        for index, row in latest_df.iterrows():
            # Prepare forecast data for energy estimation
            forecast_data = {
                "baseline_admissions": int(row['baseline_admissions']),
                "respiratory_admissions": int(row['respiratory_admissions']),
                "waterborne_admissions": int(row['waterborne_admissions']),
                "heat_related_admissions": int(row['heat_related_admissions']),
                "trauma_admissions": int(row['trauma_admissions']),
                "other_admissions": int(row['other_admissions'])
            }
            
            # 1. Estimate CURRENT energy
            current_energy_kwh, energy_reasoning = estimate_energy_smart(forecast_data)
            
            # 2. Estimate BASELINE energy
            baseline_energy_kwh = estimate_baseline_energy(
                baseline_admissions=int(row['baseline_admissions']),
                duration_days=1  # Daily estimate for live monitor
            )
            
            # 3. Create energy alert
            energy_alert = create_energy_alert(
                current_energy_kwh=current_energy_kwh,
                baseline_energy_kwh=baseline_energy_kwh
            )
            
            # 4. Calculate Carbon Emissions
            emission_result = calculate_carbon(
                record_id=f"{row['hospital_id']}-{row['timestamp']}",
                energy_kwh=current_energy_kwh,
                scope="Scope 2",
                energy_reasoning=energy_reasoning
            )
            
            # 5. Generate hospital-specific solutions
            surge_patients = int(row['total_admissions'] - row['baseline_admissions'])
            hospital_data = {
                "hospital_id": row['hospital_id'],
                "alert_level": energy_alert.alert_level.value,
                "surge_reasons": row['surge_reasons'],
                "current_energy_kwh": current_energy_kwh,
                "baseline_energy_kwh": baseline_energy_kwh,
                "percentage_above_baseline": energy_alert.percentage_above_baseline,
                "surge_patients": surge_patients
            }
            solutions = generate_hospital_advisory(hospital_data)
            
            # 6. Create hospital report
            hospital_report = HospitalReport(
                hospital_id=row['hospital_id'],
                timestamp=row['timestamp'],
                surge_patients=surge_patients,
                baseline_admissions=int(row['baseline_admissions']),
                total_admissions=int(row['total_admissions']),
                surge_reasons=row['surge_reasons'],
                current_energy_kwh=round(current_energy_kwh, 2),
                baseline_energy_kwh=round(baseline_energy_kwh, 2),
                energy_alert=energy_alert,
                emissions_kg=round(emission_result.total_emissions_kg, 2),
                emissions_tons=round(emission_result.total_emissions_tons, 2),
                solutions=solutions,
                emission_result=emission_result
            )
            hospital_reports.append(hospital_report)
            
            # Update aggregates
            total_patients += surge_patients
            total_energy += current_energy_kwh
            total_emissions += emission_result.total_emissions_kg
            results.append(emission_result)
            
        # Generate overall advisory
        summary_data = {
            "total_patients": total_patients,
            "total_energy": round(total_energy, 2),
            "total_emissions": round(total_emissions, 2),
            "surge_reasons": "Live Surge Monitoring Data"
        }
        general_advisory = generate_general_advisory(summary_data)
        
        return CarbonReport(
            total_surge_patients=total_patients,
            total_energy_kwh=round(total_energy, 2),
            total_emissions_kg=round(total_emissions, 2),
            hospital_reports=hospital_reports,
            results=results,
            general_advisory=general_advisory
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/carbon/credits", response_model=CarbonCreditReport)
async def generate_carbon_credits(
    hospital_id: str,
    num_beds: int = 500,
    apply_all_measures: bool = False
):
    """
    Generate carbon credits based on energy savings potential.
    
    This endpoint:
    1. Reads current energy consumption from /api/carbon/monitor
    2. Assesses BEE compliance and star rating
    3. Calculates potential energy savings from BEE best practices
    4. Converts savings to carbon credits
    5. Returns comprehensive report with ROI analysis
    
    Args:
        hospital_id: Hospital identifier (e.g., 'KEM_H1')
        num_beds: Number of hospital beds (default: 500)
        apply_all_measures: Apply all recommended measures (default: False, applies top 3)
    
    Returns:
        CarbonCreditReport with BEE compliance, savings plan, and carbon credits
    """
    csv_path = "data/continuous_surge_predictions.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=404,
            detail="Live surge data not found. Ensure continuous_surge_monitor.py is running."
        )
    
    try:
        # Read CSV and get latest data for the hospital
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data available in surge monitor.")
        
        # Filter for latest timestamp and specific hospital
        latest_timestamp = df['timestamp'].max()
        hospital_df = df[
            (df['timestamp'] == latest_timestamp) &
            (df['hospital_id'] == hospital_id)
        ]
        
        if hospital_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for hospital {hospital_id} in latest predictions."
            )
        
        # Get hospital data
        row = hospital_df.iloc[0]
        
        # Prepare forecast data for energy estimation
        forecast_data = {
            "baseline_admissions": int(row['baseline_admissions']),
            "respiratory_admissions": int(row['respiratory_admissions']),
            "waterborne_admissions": int(row['waterborne_admissions']),
            "heat_related_admissions": int(row['heat_related_admissions']),
            "trauma_admissions": int(row['trauma_admissions']),
            "other_admissions": int(row['other_admissions'])
        }
        
        # Estimate current energy (daily, so annualize it)
        daily_energy_kwh, _ = estimate_energy_smart(forecast_data)
        annual_energy_kwh = daily_energy_kwh * 365
        
        # Calculate baseline energy
        baseline_energy_kwh = estimate_baseline_energy(
            baseline_admissions=int(row['baseline_admissions']),
            duration_days=365
        )
        
        # Create energy alert
        energy_alert = create_energy_alert(
            current_energy_kwh=annual_energy_kwh,
            baseline_energy_kwh=baseline_energy_kwh
        )
        
        # BEE Compliance Assessment
        bee_assessment = assess_bee_compliance(annual_energy_kwh, num_beds, 365)
        bee_compliance = BEECompliance(**bee_assessment)
        
        # Generate Savings Report
        savings_report = generate_savings_report(
            hospital_id=hospital_id,
            current_energy_kwh=annual_energy_kwh,
            alert_level=energy_alert.alert_level.value,
            num_beds=num_beds,
            apply_all_measures=apply_all_measures
        )
        
        # Convert measures to EnergyMeasure models
        energy_measures = [
            EnergyMeasure(**measure)
            for measure in savings_report["energy_savings"]["measures"]
        ]
        
        # Create EnergySavingsPlan
        energy_savings_plan = EnergySavingsPlan(
            hospital_id=hospital_id,
            current_energy_kwh=savings_report["current_state"]["energy_kwh"],
            alert_level=savings_report["current_state"]["alert_level"],
            num_beds=savings_report["current_state"]["num_beds"],
            total_savings_kwh=savings_report["energy_savings"]["total_savings_kwh"],
            savings_percentage=savings_report["energy_savings"]["savings_percentage"],
            new_energy_kwh=savings_report["energy_savings"]["new_energy_kwh"],
            measures_applied=savings_report["energy_savings"]["measures_applied"],
            measures=energy_measures,
            annual_cost_savings_inr=savings_report["financial_impact"]["annual_cost_savings_inr"],
            implementation_cost_inr=savings_report["financial_impact"]["implementation_cost_inr"],
            payback_period_months=savings_report["financial_impact"]["payback_period_months"],
            roi_percentage=savings_report["financial_impact"]["roi_percentage"]
        )
        
        # Create CarbonCreditDetails
        carbon_credits = CarbonCreditDetails(**savings_report["carbon_credits"])
        
        # Generate Credit ID
        credit_id = f"CC-{hospital_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create NABH Verified Credit (initially PENDING)
        verified_credit = NABHVerifiedCredit(
            credit_id=credit_id,
            hospital_id=hospital_id,
            saved_energy_kwh=carbon_credits.saved_energy_kwh,
            saved_emissions_tons=carbon_credits.saved_emissions_tons,
            credit_value_usd=carbon_credits.credit_value_usd,
            credit_value_inr=carbon_credits.credit_value_inr,
            bee_star_improvement=bee_compliance.next_star_rating - bee_compliance.current_star_rating,
            nabh_verification_status="PENDING",
            blockchain_hash=None,  # Will be set after blockchain tokenization
            verification_documents=[]
        )
        
        # Return complete report
        return CarbonCreditReport(
            hospital_id=hospital_id,
            bee_compliance=bee_compliance,
            energy_savings=energy_savings_plan,
            carbon_credits=carbon_credits,
            verified_credit=verified_credit,
            recommended_measures=savings_report["recommended_measures"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
