"""
BEE (Bureau of Energy Efficiency) India Compliance Module
Implements star rating system and energy performance benchmarking for hospitals.
"""

from typing import Dict, List, Tuple
from datetime import datetime

# BEE Star Rating Thresholds (kWh per bed per year)
BEE_STAR_RATINGS = {
    5: {"max_epi_kwh_bed": 6528, "label": "Highly Efficient", "percentile": "Top 20%"},
    4: {"max_epi_kwh_bed": 8140, "label": "Efficient", "percentile": "Top 40%"},
    3: {"max_epi_kwh_bed": 9752, "label": "Moderately Efficient", "percentile": "Top 60%"},
    2: {"max_epi_kwh_bed": 11364, "label": "Below Average", "percentile": "Bottom 40%"},
    1: {"max_epi_kwh_bed": float('inf'), "label": "Poor", "percentile": "Bottom 20%"}
}

# BEE Best Practices with Evidence-Based Savings
BEE_BEST_PRACTICES = {
    "hvac_vfd_chillers": {
        "name": "Variable Frequency Drive (VFD) for Chillers",
        "category": "HVAC",
        "savings_percentage": 0.25,
        "cost_inr_per_bed": 15000,
        "payback_months": 18,
        "priority": "HIGH",
        "description": "Install VFDs on chiller compressors for better capacity control"
    },
    "led_lighting": {
        "name": "LED Lighting Retrofit",
        "category": "Lighting",
        "savings_percentage": 0.15,
        "cost_inr_per_bed": 5000,
        "payback_months": 12,
        "priority": "HIGH",
        "description": "Replace all conventional lighting with LED fixtures"
    },
    "solar_water_heater": {
        "name": "Solar Water Heating System",
        "category": "Water Heating",
        "savings_percentage": 0.10,
        "cost_inr_per_bed": 8000,
        "payback_months": 24,
        "priority": "MEDIUM",
        "description": "Install solar thermal or hybrid water heating systems"
    },
    "building_envelope": {
        "name": "Building Envelope Improvements",
        "category": "Building",
        "savings_percentage": 0.12,
        "cost_inr_per_bed": 20000,
        "payback_months": 36,
        "priority": "MEDIUM",
        "description": "Upgrade to spectrally-selective glazing and improve insulation"
    },
    "equipment_standby": {
        "name": "Medical Equipment Standby Mode",
        "category": "Equipment",
        "savings_percentage": 0.08,
        "cost_inr_per_bed": 2000,
        "payback_months": 6,
        "priority": "HIGH",
        "description": "Enable low-power modes for imaging and diagnostic equipment"
    },
    "hvac_optimization": {
        "name": "HVAC System Optimization",
        "category": "HVAC",
        "savings_percentage": 0.15,
        "cost_inr_per_bed": 8000,
        "payback_months": 15,
        "priority": "HIGH",
        "description": "Optimize HVAC schedules, zoning, and temperature setpoints"
    },
    "energy_monitoring": {
        "name": "Real-time Energy Monitoring System",
        "category": "Management",
        "savings_percentage": 0.05,
        "cost_inr_per_bed": 3000,
        "payback_months": 12,
        "priority": "MEDIUM",
        "description": "Install sub-metering and energy management system"
    }
}


def calculate_epi(energy_kwh: float, num_beds: int, duration_days: int = 365) -> float:
    """
    Calculate Energy Performance Index (EPI) per BEE standards.
    
    Args:
        energy_kwh: Total energy consumption in kWh
        num_beds: Number of hospital beds
        duration_days: Period duration (default 365 for annual)
    
    Returns:
        EPI in kWh per bed (annualized)
    """
    if num_beds <= 0:
        raise ValueError("Number of beds must be greater than 0")
    
    # Annualize if not a full year
    annual_energy = energy_kwh * (365 / duration_days)
    epi_per_bed = annual_energy / num_beds
    
    return round(epi_per_bed, 2)


def get_star_rating(epi_kwh_per_bed: float) -> int:
    """
    Determine BEE star rating based on EPI.
    
    Args:
        epi_kwh_per_bed: Energy Performance Index (kWh/bed/year)
    
    Returns:
        Star rating (1-5)
    """
    for stars in range(5, 0, -1):
        if epi_kwh_per_bed <= BEE_STAR_RATINGS[stars]["max_epi_kwh_bed"]:
            return stars
    return 1


def assess_bee_compliance(energy_kwh: float, num_beds: int, duration_days: int = 365) -> Dict:
    """
    Comprehensive BEE compliance assessment.
    
    Args:
        energy_kwh: Total energy consumption
        num_beds: Number of beds
        duration_days: Period duration
    
    Returns:
        Detailed compliance report
    """
    epi = calculate_epi(energy_kwh, num_beds, duration_days)
    current_rating = get_star_rating(epi)
    rating_info = BEE_STAR_RATINGS[current_rating]
    
    # Calculate gap to next star rating
    next_rating = min(current_rating + 1, 5)
    if next_rating > current_rating:
        target_epi = BEE_STAR_RATINGS[next_rating]["max_epi_kwh_bed"]
        improvement_needed_kwh = (epi - target_epi) * num_beds
        improvement_percentage = ((epi - target_epi) / epi) * 100
    else:
        improvement_needed_kwh = 0
        improvement_percentage = 0
    
    return {
        "epi_kwh_per_bed": epi,
        "current_star_rating": current_rating,
        "rating_label": rating_info["label"],
        "percentile": rating_info["percentile"],
        "compliance_status": "COMPLIANT" if current_rating >= 3 else "NON_COMPLIANT",
        "next_star_rating": next_rating,
        "improvement_needed_kwh": round(improvement_needed_kwh, 2),
        "improvement_percentage": round(improvement_percentage, 2),
        "is_top_performer": current_rating >= 4
    }


def get_recommended_measures(current_rating: int, alert_level: str, num_beds: int) -> List[Dict]:
    """
    Get BEE-recommended energy saving measures based on current performance.
    
    Args:
        current_rating: Current BEE star rating
        alert_level: Energy alert level (NORMAL, WARNING, CRITICAL)
        num_beds: Number of beds for cost estimation
    
    Returns:
        List of recommended measures with details
    """
    recommendations = []
    
    # Prioritize based on alert level
    if alert_level == "CRITICAL":
        priority_measures = ["hvac_vfd_chillers", "led_lighting", "hvac_optimization", "equipment_standby"]
    elif alert_level == "WARNING":
        priority_measures = ["hvac_optimization", "led_lighting", "solar_water_heater", "energy_monitoring"]
    else:  # NORMAL
        priority_measures = ["energy_monitoring", "equipment_standby", "solar_water_heater"]
    
    for measure_id in priority_measures:
        if measure_id in BEE_BEST_PRACTICES:
            practice = BEE_BEST_PRACTICES[measure_id].copy()
            practice["measure_id"] = measure_id
            practice["estimated_cost_inr"] = practice["cost_inr_per_bed"] * num_beds
            recommendations.append(practice)
    
    return recommendations


def calculate_savings_potential(
    current_energy_kwh: float,
    measures: List[str],
    num_beds: int
) -> Dict:
    """
    Calculate potential energy and cost savings from implementing BEE measures.
    
    Args:
        current_energy_kwh: Current annual energy consumption
        measures: List of measure IDs to implement
        num_beds: Number of beds
    
    Returns:
        Detailed savings analysis
    """
    total_savings_kwh = 0
    total_cost_inr = 0
    measure_details = []
    
    for measure_id in measures:
        if measure_id in BEE_BEST_PRACTICES:
            practice = BEE_BEST_PRACTICES[measure_id]
            savings_kwh = current_energy_kwh * practice["savings_percentage"]
            cost_inr = practice["cost_inr_per_bed"] * num_beds
            
            total_savings_kwh += savings_kwh
            total_cost_inr += cost_inr
            
            measure_details.append({
                "measure_id": measure_id,
                "name": practice["name"],
                "savings_kwh": round(savings_kwh, 2),
                "savings_percentage": practice["savings_percentage"] * 100,
                "cost_inr": cost_inr
            })
    
    # Calculate financial metrics (assuming ₹8/kWh electricity cost)
    electricity_rate_inr = 8.0
    annual_savings_inr = total_savings_kwh * electricity_rate_inr
    
    if total_cost_inr > 0:
        payback_months = (total_cost_inr / annual_savings_inr) * 12
    else:
        payback_months = 0
    
    return {
        "total_savings_kwh": round(total_savings_kwh, 2),
        "total_savings_percentage": round((total_savings_kwh / current_energy_kwh) * 100, 2),
        "annual_cost_savings_inr": round(annual_savings_inr, 2),
        "implementation_cost_inr": round(total_cost_inr, 2),
        "payback_period_months": round(payback_months, 1),
        "roi_percentage": round((annual_savings_inr / total_cost_inr) * 100, 2) if total_cost_inr > 0 else 0,
        "measures": measure_details
    }
