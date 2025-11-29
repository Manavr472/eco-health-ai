"""
Configuration file for Eco-Health AI Platform
Mumbai Region Specific Settings
"""

from datetime import datetime, timedelta
from typing import Dict, List

# ============= MUMBAI REGION CONFIGURATION =============

# Mumbai AQI Monitoring Stations
MUMBAI_STATIONS = [
    "Bandra", "Andheri", "Borivali", "Colaba", "Worli",
    "Kurla", "Malad", "Powai", "Chembur", "Navi Mumbai"
]

# Geographic coordinates for weather modeling
MUMBAI_COORDS = {
    "latitude": 19.0760,
    "longitude": 72.8777
}

# ============= DATA GENERATION SETTINGS =============

# Synthetic data time range (5 years as per user requirement)
DATA_START_DATE = datetime(2023, 1, 1)
DATA_END_DATE = datetime(2025, 12, 31)
TOTAL_DAYS = (DATA_END_DATE - DATA_START_DATE).days + 1

# Data generation parameters
NUM_HOSPITALS = 14  # 14 major Mumbai hospitals
BASELINE_DAILY_ADMISSIONS = 150  # Average daily admissions per hospital

# Hospital Locations and Coordinates (from real data)
MUMBAI_HOSPITALS = [
    {"id": 1, "code": "KEM_H1", "name": "King Edward Memorial Hospital", "location": "Parel", "lat": 19.0060, "lon": 72.8423},
    {"id": 2, "code": "LOK_H2", "name": "Lokmanya Tilak Hospital", "location": "Sion", "lat": 19.0430, "lon": 72.8616},
    {"id": 3, "code": "NAI_H3", "name": "BYL Nair Hospital", "location": "Mumbai Central", "lat": 18.9654, "lon": 72.8182},
    {"id": 4, "code": "JJ_H4", "name": "JJ Hospital", "location": "Mumbai Central", "lat": 18.9627, "lon": 72.8313},
    {"id": 5, "code": "HIN_H5", "name": "Hinduja Hospital", "location": "Mahim", "lat": 19.0401, "lon": 72.8408},
    {"id": 6, "code": "LIL_H6", "name": "Lilavati Hospital", "location": "Bandra West", "lat": 19.0596, "lon": 72.8295},
    {"id": 7, "code": "NAN_H7", "name": "NANAVATI", "location": "Vile Parle", "lat": 19.1036, "lon": 72.8354},
    {"id": 8, "code": "BOM_H8", "name": "Bombay Hospital", "location": "Marine Lines", "lat": 18.9515, "lon": 72.8234},
    {"id": 9, "code": "JAS_H9", "name": "Jaslok Hospital & Research Centre", "location": "Tardeo", "lat": 18.9703, "lon": 72.8087},
    {"id": 10, "code": "BRE_H10", "name": "Breach Candy Hospital Trust", "location": "Breach Candy", "lat": 18.9730, "lon": 72.8008},
    {"id": 11, "code": "SAI_H11", "name": "Saifee Hospital", "location": "Charni Road", "lat": 18.9540, "lon": 72.8180},
    {"id": 13, "code": "JUP_H13", "name": "Jupiter Hospital", "location": "Thane West", "lat": 19.2183, "lon": 72.9781},
    {"id": 14, "code": "COO_H14", "name": "Dr. R N Cooper Hospital", "location": "Juhu", "lat": 19.1019, "lon": 72.8267},
    {"id": 15, "code": "HBT_H15", "name": "HBT (Thackeray) Trauma Care", "location": "Jogeshwari East", "lat": 19.1366, "lon": 72.8509}
]

# ============= MUMBAI FESTIVAL CALENDAR =============

# Major festivals that impact patient surges
ANNUAL_FESTIVALS = {
    "Diwali": [
        {"start": "2020-11-14", "end": "2020-11-16"},
        {"start": "2021-11-04", "end": "2021-11-06"},
        {"start": "2022-10-24", "end": "2022-10-26"},
        {"start": "2023-11-12", "end": "2023-11-14"},
        {"start": "2024-11-01", "end": "2024-11-03"},
    ],
    "Ganesh Chaturthi": [
        {"start": "2020-08-22", "end": "2020-09-01"},
        {"start": "2021-09-10", "end": "2021-09-19"},
        {"start": "2022-08-31", "end": "2022-09-09"},
        {"start": "2023-09-19", "end": "2023-09-28"},
        {"start": "2024-09-07", "end": "2024-09-17"},
    ],
    "Holi": [
        {"start": "2020-03-09", "end": "2020-03-10"},
        {"start": "2021-03-28", "end": "2021-03-29"},
        {"start": "2022-03-17", "end": "2022-03-18"},
        {"start": "2023-03-07", "end": "2023-03-08"},
        {"start": "2024-03-25", "end": "2024-03-26"},
    ],
    "Navratri": [
        {"start": "2020-10-17", "end": "2020-10-25"},
        {"start": "2021-10-07", "end": "2021-10-15"},
        {"start": "2022-09-26", "end": "2022-10-04"},
        {"start": "2023-10-15", "end": "2023-10-23"},
        {"start": "2024-10-03", "end": "2024-10-11"},
    ]
}

# ============= AQI PARAMETERS =============

# AQI Categories and thresholds
AQI_CATEGORIES = {
    "Good": (0, 50),
    "Satisfactory": (51, 100),
    "Moderate": (101, 200),
    "Poor": (201, 300),
    "Very Poor": (301, 400),
    "Severe": (401, 500)
}

# Mumbai AQI baseline and seasonal variations
AQI_BASELINE = 120  # Mumbai typical AQI
AQI_STD_DEV = 30
MONSOON_AQI_REDUCTION = 40  # AQI improves during monsoon
WINTER_AQI_INCREASE = 50    # AQI worsens in winter
DIWALI_AQI_SPIKE = 200      # Massive spike during Diwali

# ============= WEATHER PARAMETERS =============

# Mumbai monsoon season
MONSOON_START_MONTH = 6  # June
MONSOON_END_MONTH = 9    # September

# Temperature ranges (Celsius)
SUMMER_TEMP_RANGE = (28, 38)
MONSOON_TEMP_RANGE = (24, 32)
WINTER_TEMP_RANGE = (18, 30)

# Rainfall (mm per day)
MONSOON_RAINFALL_MEAN = 25
MONSOON_RAINFALL_STD = 15
NON_MONSOON_RAINFALL_PROB = 0.05

# Humidity
MONSOON_HUMIDITY_RANGE = (75, 95)
NON_MONSOON_HUMIDITY_RANGE = (50, 75)

# ============= PATIENT SURGE PARAMETERS =============

# Surge multipliers based on conditions
SURGE_FACTORS = {
    "aqi_very_poor": 1.5,      # AQI > 300
    "aqi_severe": 2.0,         # AQI > 400
    "heavy_rainfall": 1.4,     # Rainfall > 50mm
    "extreme_heat": 1.3,       # Temp > 36°C
    "festival_injuries": 1.6,  # Ganesh Chaturthi
    "pollution_event": 2.5,    # Diwali
    "seasonal_flu": 1.7        # Winter months
}

# Disease correlations
DISEASE_PATTERNS = {
    "respiratory": {
        "aqi_threshold": 200,
        "surge_factor": 2.0,
        "baseline_percentage": 0.15
    },
    "waterborne": {
        "rainfall_threshold": 30,
        "surge_factor": 1.8,
        "baseline_percentage": 0.10
    },
    "heat_related": {
        "temperature_threshold": 36,
        "surge_factor": 1.5,
        "baseline_percentage": 0.05
    },
    "trauma": {
        "festival_correlation": True,
        "surge_factor": 1.6,
        "baseline_percentage": 0.20
    }
}

# ============= RESOURCE REQUIREMENTS =============

# Staff-to-patient ratios
STAFF_RATIOS = {
    "doctors": 1/15,      # 1 doctor per 15 patients
    "nurses": 1/5,        # 1 nurse per 5 patients
    "support_staff": 1/10  # 1 support staff per 10 patients
}

# Supply requirements per patient
SUPPLIES_PER_PATIENT = {
    "ppe_kits": 2,
    "oxygen_liters": 10,
    "iv_fluids_ml": 500,
    "medications_units": 5,
    "bed_linens": 2
}

# ============= CARBON EMISSION PARAMETERS =============

# Baseline emissions (kg CO2 per unit)
CARBON_EMISSIONS = {
    "electricity_kwh": 0.82,        # Per kWh in Mumbai
    "oxygen_production": 0.3,       # Per liter
    "medical_waste_kg": 0.5,        # Per kg disposal
    "water_liter": 0.001,           # Per liter
    "supply_transport_km": 0.15,    # Per km
    "staff_commute_km": 0.12        # Per km
}

# Resource consumption per patient
RESOURCE_CONSUMPTION = {
    "electricity_kwh_per_patient": 50,     # Per day
    "water_liters_per_patient": 200,       # Per day
    "medical_waste_kg_per_patient": 3,     # Per day
    "avg_supply_distance_km": 25,          # Average transport
    "avg_staff_commute_km": 15             # Per staff member
}

# Optimization savings (percentage reduction in chaos vs optimized)
OPTIMIZATION_BENEFITS = {
    "energy_reduction": 0.25,       # 25% energy savings
    "supply_waste_reduction": 0.40,  # 40% less waste
    "transport_optimization": 0.30,  # 30% fewer trips
    "staff_efficiency": 0.20         # 20% better utilization
}

# ============= BLOCKCHAIN SETTINGS =============

BLOCKCHAIN_CONFIG = {
    "network_name": "EcoHealthChain",
    "token_name": "CARBON",
    "token_symbol": "ECO",
    "decimals": 18,
    "genesis_hash": "0x" + "0" * 64,
    "min_credits_for_tokenization": 1.0  # Minimum tons CO2
}

# Carbon credit market value (USD per ton CO2)
CARBON_CREDIT_PRICE_USD = 25  # Conservative estimate

# ============= ML MODEL PARAMETERS =============

MODEL_CONFIG = {
    "test_size": 0.2,              # 20% test split
    "random_state": 42,
    "cv_folds": 5,                 # Cross-validation folds
    "prediction_horizon_days": 7,  # Predict 7 days ahead
    "min_accuracy_threshold": 0.75 # Minimum acceptable accuracy
}

# Feature engineering
FEATURE_LAG_DAYS = [1, 3, 7, 14]  # Lagged features to create
ROLLING_WINDOW_DAYS = [7, 14, 30]  # Rolling statistics

# ============= AGENT CONFIGURATION =============

AGENT_CONFIG = {
    "monitoring_interval_seconds": 300,  # Check every 5 minutes
    "surge_prediction_threshold": 0.3,    # 30% increase triggers alert
    "severe_surge_threshold": 0.5,        # 50% increase = severe
    "advance_warning_days": 5,            # Warn 5 days before surge
    "recommendation_confidence_min": 0.7,  # Min confidence for action
}

# Recommendation thresholds
RECOMMENDATION_THRESHOLDS = {
    "minor_surge": 1.2,    # 20% increase
    "moderate_surge": 1.4,  # 40% increase
    "major_surge": 1.7,     # 70% increase
    "critical_surge": 2.0   # 100% increase
}

# ============= API CONFIGURATION =============

API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "title": "Eco-Health AI Platform",
    "description": "Agentic AI for Sustainable Hospital Operations - Mumbai Region",
    "version": "1.0.0"
}

# ============= DATABASE CONFIGURATION =============

DATABASE_CONFIG = {
    "db_path": "database/eco_health.db",
    "echo": False,  # SQL logging
    "pool_size": 5,
    "max_overflow": 10
}

# ============= PATHS =============

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============= LOGGING =============

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "eco_health.log"),
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}


# ------------------------------------------
# CARBON CONFIGURATION
# --------------------------------------------

"""
Configuration constants for Carbon Agent.
Based on Bureau of Energy Efficiency (BEE) India standards.
"""

# BEE Energy Performance Index (EPI) Benchmarks (kWh/m²/year)
# Source: BEE Star Rating Program for Hospital Buildings
EPI_BENCHMARKS = {
    "warm_humid": 275,    # Coastal regions (Mumbai, Chennai, Kolkata)
    "composite": 264,     # North India (Delhi, Jaipur, Lucknow)
    "hot_dry": 261,       # Western India (Ahmedabad, Jodhpur)
    "moderate": 247       # Hill stations and temperate regions
}

# Minimum acceptable EPI (Industry standard from CII)
MINIMUM_EPI = 200  # kWh/m²/year

# Alert Thresholds (Based on ECBC 2017 compliance)
# Percentage above baseline EPI for climate zone
WARNING_THRESHOLD = 15   # 15% above baseline - approaching non-compliance
CRITICAL_THRESHOLD = 25  # 25% above baseline - ECBC non-compliant, immediate action required

# Climate zone for this deployment (Mumbai)
DEFAULT_CLIMATE_ZONE = "warm_humid"

# Energy factors for baseline calculation
# Based on average hospital energy consumption patterns
BASELINE_ENERGY_FACTOR_PER_PATIENT = 50  # kWh per patient per day
BASELINE_DURATION_DAYS = 7  # Default duration for surge events

# Emission factor (India grid)
# Source: CEA (Central Electricity Authority) CO2 Baseline Database
EMISSION_FACTOR_INDIA = 0.82  # kgCO2/kWh

# References:
# - Bureau of Energy Efficiency (BEE) Star Rating Program
# - Energy Conservation Building Code (ECBC) 2017
# - National Hospital Energy Consumption Survey 2023
# - CEA CO2 Baseline Database V18
