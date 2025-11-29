from models.carbon_models import SurgeRecord

# Heuristic Energy Factors (kWh per patient per day)
# These are estimates based on hospital energy intensity data.
# Trauma: High intensity (Surgery, ICU, Ventilators) -> ~15 kWh/day
# Heat Borne: High intensity (AC, Cooling) -> ~12 kWh/day
# Air Borne: Medium intensity (Isolation, Filtration) -> ~8 kWh/day
# Water Borne: Low/Medium intensity (IVs, Monitoring) -> ~6 kWh/day

ENERGY_FACTORS = {
    "Trauma": 15.0,
    "Heat Borne": 12.0,
    "Air Borne": 8.0,
    "Water Borne": 6.0
}

BASE_HOSPITAL_LOAD_KWH = 5000.0 # Daily baseline for a medium hospital

def estimate_energy(record: SurgeRecord) -> float:
    """
    Estimates the TOTAL energy consumption (Base + Surge) for the duration of the event.
    """
    per_patient_factor = ENERGY_FACTORS.get(record.event_type, 5.0)
    
    daily_surge_load = record.surge_patients * per_patient_factor
    total_daily_load = BASE_HOSPITAL_LOAD_KWH + daily_surge_load
    
    total_energy = total_daily_load * record.duration_days
    
    return total_energy
