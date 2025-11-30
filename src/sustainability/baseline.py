"""
Baseline energy calculation and alert generation.
Based on BEE (Bureau of Energy Efficiency) India standards.
"""

from src.core.config import (
    WARNING_THRESHOLD,
    CRITICAL_THRESHOLD,
    BASELINE_ENERGY_FACTOR_PER_PATIENT,
    BASELINE_DURATION_DAYS
)
from src.models.carbon_models import EnergyAlert, AlertLevel


def estimate_baseline_energy(baseline_admissions: int, duration_days: int = BASELINE_DURATION_DAYS) -> float:
    """
    Estimate baseline energy consumption for a hospital.
    
    Args:
        baseline_admissions: Number of baseline patient admissions
        duration_days: Duration of the period in days
    
    Returns:
        Baseline energy consumption in kWh
    
    Formula:
        baseline_energy = baseline_admissions * energy_per_patient_per_day * duration_days
    """
    baseline_energy_kwh = baseline_admissions * BASELINE_ENERGY_FACTOR_PER_PATIENT * duration_days
    return baseline_energy_kwh


def create_energy_alert(
    current_energy_kwh: float,
    baseline_energy_kwh: float
) -> EnergyAlert:
    """
    Create an energy alert based on current vs baseline energy consumption.
    
    Args:
        current_energy_kwh: Current energy consumption in kWh
        baseline_energy_kwh: Baseline energy consumption in kWh
    
    Returns:
        EnergyAlert object with alert level and details
    
    Alert Levels (Based on BEE/ECBC standards):
        - NORMAL: Within acceptable range
        - WARNING: 15-25% above baseline (approaching non-compliance)
        - CRITICAL: >25% above baseline (ECBC non-compliant)
    """
    # Calculate percentage above baseline
    if baseline_energy_kwh > 0:
        percentage_above = ((current_energy_kwh - baseline_energy_kwh) / baseline_energy_kwh) * 100
    else:
        percentage_above = 0.0
    
    # Determine alert level
    if percentage_above >= CRITICAL_THRESHOLD:
        alert_level = AlertLevel.CRITICAL
        threshold_exceeded = True
        message = f"🚨 CRITICAL: Energy consumption is {percentage_above:.1f}% above baseline. ECBC non-compliant - immediate action required!"
    elif percentage_above >= WARNING_THRESHOLD:
        alert_level = AlertLevel.WARNING
        threshold_exceeded = True
        message = f"⚠️ WARNING: Energy consumption is {percentage_above:.1f}% above baseline. Approaching non-compliance threshold."
    else:
        alert_level = AlertLevel.NORMAL
        threshold_exceeded = False
        if percentage_above > 0:
            message = f"✅ NORMAL: Energy consumption is {percentage_above:.1f}% above baseline. Within acceptable range."
        else:
            message = f"✅ NORMAL: Energy consumption is within baseline. Excellent performance!"
    
    return EnergyAlert(
        alert_level=alert_level,
        current_energy_kwh=current_energy_kwh,
        baseline_energy_kwh=baseline_energy_kwh,
        percentage_above_baseline=round(percentage_above, 2),
        threshold_exceeded=threshold_exceeded,
        message=message
    )
