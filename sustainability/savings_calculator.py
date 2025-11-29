"""
Energy Savings Calculator
Estimates potential energy savings and carbon credit generation.
"""

from typing import Dict, List
from .bee_compliance import calculate_savings_potential, get_recommended_measures
from .factors import GRID_INDIA_CEA


def estimate_energy_savings(
    current_energy_kwh: float,
    alert_level: str,
    num_beds: int,
    apply_all_measures: bool = False
) -> Dict:
    """
    Estimate energy savings based on alert level and BEE best practices.
    
    Args:
        current_energy_kwh: Current energy consumption
        alert_level: Alert level (NORMAL, WARNING, CRITICAL)
        num_beds: Number of hospital beds
        apply_all_measures: If True, apply all recommended measures
    
    Returns:
        Savings estimate with measures
    """
    # Get recommended measures based on alert level
    recommended_measures = get_recommended_measures(0, alert_level, num_beds)
    
    if apply_all_measures:
        measure_ids = [m["measure_id"] for m in recommended_measures]
    else:
        # Apply top 3 high-priority measures
        high_priority = [m for m in recommended_measures if m["priority"] == "HIGH"]
        measure_ids = [m["measure_id"] for m in high_priority[:3]]
    
    # Calculate savings
    savings = calculate_savings_potential(current_energy_kwh, measure_ids, num_beds)
    
    return {
        **savings,
        "recommended_measures": recommended_measures,
        "applied_measures": measure_ids
    }


def calculate_carbon_credits(
    saved_energy_kwh: float,
    grid_factor: float = GRID_INDIA_CEA.value
) -> Dict:
    """
    Calculate carbon credits from energy savings.
    
    Args:
        saved_energy_kwh: Energy saved in kWh
        grid_factor: Grid emission factor (kgCO2/kWh)
    
    Returns:
        Carbon credit details
    """
    # Calculate emissions avoided
    saved_emissions_kg = saved_energy_kwh * grid_factor
    saved_emissions_tons = saved_emissions_kg / 1000
    
    # Carbon credit market value (Indian voluntary market)
    market_price_usd_per_ton = 25.0
    credit_value_usd = saved_emissions_tons * market_price_usd_per_ton
    
    # Convert to INR (approximate rate)
    usd_to_inr = 83.0
    credit_value_inr = credit_value_usd * usd_to_inr
    
    return {
        "saved_energy_kwh": round(saved_energy_kwh, 2),
        "saved_emissions_kg": round(saved_emissions_kg, 2),
        "saved_emissions_tons": round(saved_emissions_tons, 4),
        "carbon_credits_tons": round(saved_emissions_tons, 4),
        "credit_value_usd": round(credit_value_usd, 2),
        "credit_value_inr": round(credit_value_inr, 2),
        "grid_emission_factor": grid_factor,
        "market_price_usd_per_ton": market_price_usd_per_ton
    }


def generate_savings_report(
    hospital_id: str,
    current_energy_kwh: float,
    alert_level: str,
    num_beds: int,
    apply_all_measures: bool = False
) -> Dict:
    """
    Generate comprehensive savings and carbon credit report.
    
    Args:
        hospital_id: Hospital identifier
        current_energy_kwh: Current energy consumption
        alert_level: Energy alert level
        num_beds: Number of beds
        apply_all_measures: Whether to apply all measures
    
    Returns:
        Complete savings report with carbon credits
    """
    # Calculate energy savings
    savings = estimate_energy_savings(
        current_energy_kwh,
        alert_level,
        num_beds,
        apply_all_measures
    )
    
    # Calculate carbon credits
    credits = calculate_carbon_credits(savings["total_savings_kwh"])
    
    # Calculate new energy consumption
    new_energy_kwh = current_energy_kwh - savings["total_savings_kwh"]
    
    return {
        "hospital_id": hospital_id,
        "current_state": {
            "energy_kwh": current_energy_kwh,
            "alert_level": alert_level,
            "num_beds": num_beds
        },
        "energy_savings": {
            "total_savings_kwh": savings["total_savings_kwh"],
            "savings_percentage": savings["total_savings_percentage"],
            "new_energy_kwh": round(new_energy_kwh, 2),
            "measures_applied": len(savings["applied_measures"]),
            "measures": savings["measures"]
        },
        "financial_impact": {
            "annual_cost_savings_inr": savings["annual_cost_savings_inr"],
            "implementation_cost_inr": savings["implementation_cost_inr"],
            "payback_period_months": savings["payback_period_months"],
            "roi_percentage": savings["roi_percentage"]
        },
        "carbon_credits": credits,
        "recommended_measures": savings["recommended_measures"]
    }
