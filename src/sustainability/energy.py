def estimate_energy(patients: int, beds: int = 500) -> float:
    """Estimate daily energy consumption in kWh"""
    base_load = beds * 15 # 15 kWh per bed base load
    patient_load = patients * 10 # Additional 10 kWh per patient
    return base_load + patient_load
