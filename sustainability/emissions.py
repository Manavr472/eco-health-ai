from models.carbon_models import EmissionResult, CalculationLog, EmissionFactor
from .factors import FACTOR_DB

def calculate_carbon(record_id: str, energy_kwh: float, scope: str = "Scope 2", energy_reasoning: str = None) -> EmissionResult:
    """
    Calculates carbon emissions deterministically.
    """
    factor: EmissionFactor = FACTOR_DB.get(scope, FACTOR_DB["Scope 2"])
    
    emissions_kg = energy_kwh * factor.value
    emissions_tons = emissions_kg / 1000.0
    
    # Create Audit Log
    log = CalculationLog(
        formula="emissions_kg = energy_kWh * emission_factor",
        arithmetic=f"{energy_kwh:.2f} * {factor.value} = {emissions_kg:.2f}",
        result=emissions_kg
    )
    
    return EmissionResult(
        record_id=record_id,
        energy_consumption_kwh=energy_kwh,
        total_emissions_kg=round(emissions_kg, 2),
        total_emissions_tons=round(emissions_tons, 4),
        scope=scope,
        factor_used=factor,
        energy_reasoning=energy_reasoning,
        calculation_log=log
    )
