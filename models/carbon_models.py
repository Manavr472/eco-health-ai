from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime
from enum import Enum

class SurgeRecord(BaseModel):
    """
    Represents a single row from the input CSV.
    """
    date: str = Field(..., description="Date of the record (YYYY-MM-DD)")
    event_type: Literal["Air Borne", "Water Borne", "Heat Borne", "Trauma"] = Field(..., description="Type of event causing the surge")
    surge_patients: int = Field(..., ge=0, description="Number of additional patients due to surge")
    duration_days: int = Field(..., ge=1, description="Duration of the surge event in days")

class ForecastRecord(BaseModel):
    """
    Represents input from the Forecasting Agent.
    """
    timestamp: str = Field(..., description="Timestamp of the forecast")
    hospital_id: str = Field(..., description="Hospital identifier")
    total_admissions: int = Field(..., ge=0, description="Total admissions predicted")
    baseline_admissions: int = Field(..., ge=0, description="Baseline admissions")
    surge_multiplier: float = Field(..., ge=1.0, description="Surge multiplier")
    surge_reasons: str = Field(..., description="Reasons for the surge")
    respiratory_admissions: int = Field(default=0, ge=0, description="Respiratory admissions")
    waterborne_admissions: int = Field(default=0, ge=0, description="Waterborne admissions")
    heat_related_admissions: int = Field(default=0, ge=0, description="Heat-related admissions")
    trauma_admissions: int = Field(default=0, ge=0, description="Trauma admissions")
    other_admissions: int = Field(default=0, ge=0, description="Other admissions")


class AlertLevel(str, Enum):
    """
    Alert severity levels based on BEE standards.
    """
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class EnergyAlert(BaseModel):
    """
    Energy consumption alert with baseline comparison.
    """
    alert_level: AlertLevel = Field(..., description="Alert severity level")
    current_energy_kwh: float = Field(..., description="Current energy consumption in kWh")
    baseline_energy_kwh: float = Field(..., description="Baseline energy consumption in kWh")
    percentage_above_baseline: float = Field(..., description="Percentage above baseline")
    threshold_exceeded: bool = Field(..., description="Whether threshold is exceeded")
    message: str = Field(..., description="Human-readable alert message")



class EmissionFactor(BaseModel):
    """
    Metadata about the emission factor used.
    """
    source: str = Field(..., description="Source of the factor (e.g., IEA, CEA)")
    region: str = Field(..., description="Region applicable (e.g., India, Global)")
    value: float = Field(..., description="Factor value in kgCO2/unit")
    unit: str = Field(..., description="Unit of the factor (e.g., kgCO2/kWh)")
    valid_from: str = Field(..., description="Validity start year/date")

class CalculationLog(BaseModel):
    """
    Audit log for a specific calculation.
    """
    formula: str = Field(..., description="The formula used")
    arithmetic: str = Field(..., description="The exact arithmetic string (e.g., '100 * 0.85')")
    result: float = Field(..., description="The result of the calculation")

class EmissionResult(BaseModel):
    """
    Final output for a single meter/record.
    """
    record_id: str = Field(..., description="Identifier for the input record")
    energy_consumption_kwh: float = Field(..., description="Estimated energy consumption in kWh")
    total_emissions_kg: float = Field(..., description="Total Carbon Emissions in kgCO2")
    total_emissions_tons: float = Field(..., description="Total Carbon Emissions in tCO2")
    scope: Literal["Scope 1", "Scope 2"] = Field(..., description="Emission Scope")
    factor_used: EmissionFactor
    energy_reasoning: Optional[str] = Field(None, description="LLM reasoning for energy estimation")
    calculation_log: CalculationLog


class HospitalReport(BaseModel):
    """
    Per-hospital energy and emissions report with baseline comparison.
    """
    hospital_id: str = Field(..., description="Hospital identifier")
    timestamp: str = Field(..., description="Forecast timestamp")
    surge_patients: int = Field(..., description="Number of surge patients")
    baseline_admissions: int = Field(..., description="Baseline patient admissions")
    total_admissions: int = Field(..., description="Total patient admissions")
    surge_reasons: str = Field(..., description="Reasons for the surge")
    current_energy_kwh: float = Field(..., description="Current energy consumption in kWh")
    baseline_energy_kwh: float = Field(..., description="Baseline energy consumption in kWh")
    energy_alert: EnergyAlert = Field(..., description="Energy alert with threshold status")
    emissions_kg: float = Field(..., description="Carbon emissions in kg")
    emissions_tons: float = Field(..., description="Carbon emissions in tons")
    solutions: str = Field(..., description="AI-generated targeted solutions for this hospital")
    emission_result: EmissionResult = Field(..., description="Detailed emission calculation")


class CarbonReport(BaseModel):
    """
    The complete report returned by the agent.
    """
    generated_at: datetime = Field(default_factory=datetime.now)
    total_surge_patients: int
    total_energy_kwh: float
    total_emissions_kg: float
    hospital_reports: List[HospitalReport] = Field(..., description="Per-hospital detailed reports")
    results: List[EmissionResult] = Field(..., description="Legacy emission results (for backward compatibility)")
    general_advisory: Optional[str] = Field(None, description="Overall AI-generated advisory across all hospitals")


# BEE Compliance and Carbon Credits Models

class BEECompliance(BaseModel):
    """BEE India compliance assessment"""
    epi_kwh_per_bed: float = Field(..., description="Energy Performance Index (kWh/bed/year)")
    current_star_rating: int = Field(..., ge=1, le=5, description="Current BEE star rating (1-5)")
    rating_label: str = Field(..., description="Rating label (e.g., 'Highly Efficient')")
    percentile: str = Field(..., description="Performance percentile")
    compliance_status: str = Field(..., description="COMPLIANT or NON_COMPLIANT")
    next_star_rating: int = Field(..., description="Next achievable star rating")
    improvement_needed_kwh: float = Field(..., description="Energy reduction needed for next star")
    improvement_percentage: float = Field(..., description="Percentage improvement needed")
    is_top_performer: bool = Field(..., description="Whether hospital is 4-5 star rated")


class EnergyMeasure(BaseModel):
    """Individual energy saving measure"""
    measure_id: str = Field(..., description="Unique measure identifier")
    name: str = Field(..., description="Measure name")
    category: str = Field(..., description="Category (HVAC, Lighting, etc.)")
    savings_kwh: float = Field(..., description="Annual energy savings in kWh")
    savings_percentage: float = Field(..., description="Percentage of total energy saved")
    cost_inr: float = Field(..., description="Implementation cost in INR")
    priority: str = Field(..., description="Priority level (HIGH, MEDIUM, LOW)")
    payback_months: Optional[float] = Field(None, description="Payback period in months")


class EnergySavingsPlan(BaseModel):
    """Comprehensive energy savings plan"""
    hospital_id: str = Field(..., description="Hospital identifier")
    current_energy_kwh: float = Field(..., description="Current annual energy consumption")
    alert_level: str = Field(..., description="Current alert level")
    num_beds: int = Field(..., description="Number of hospital beds")
    total_savings_kwh: float = Field(..., description="Total potential energy savings")
    savings_percentage: float = Field(..., description="Percentage of energy saved")
    new_energy_kwh: float = Field(..., description="Projected energy after savings")
    measures_applied: int = Field(..., description="Number of measures applied")
    measures: List[EnergyMeasure] = Field(..., description="List of energy saving measures")
    annual_cost_savings_inr: float = Field(..., description="Annual cost savings in INR")
    implementation_cost_inr: float = Field(..., description="Total implementation cost in INR")
    payback_period_months: float = Field(..., description="Overall payback period")
    roi_percentage: float = Field(..., description="Return on investment percentage")


class CarbonCreditDetails(BaseModel):
    """Carbon credit calculation details"""
    saved_energy_kwh: float = Field(..., description="Energy saved in kWh")
    saved_emissions_kg: float = Field(..., description="CO2 emissions avoided in kg")
    saved_emissions_tons: float = Field(..., description="CO2 emissions avoided in tons")
    carbon_credits_tons: float = Field(..., description="Carbon credits generated in tons")
    credit_value_usd: float = Field(..., description="Market value in USD")
    credit_value_inr: float = Field(..., description="Market value in INR")
    grid_emission_factor: float = Field(..., description="Grid emission factor used (kgCO2/kWh)")
    market_price_usd_per_ton: float = Field(..., description="Market price per ton CO2")


class NABHVerifiedCredit(BaseModel):
    """NABH-verified carbon credit with blockchain tokenization"""
    credit_id: str = Field(..., description="Unique credit identifier")
    hospital_id: str = Field(..., description="Hospital identifier")
    saved_energy_kwh: float = Field(..., description="Total energy saved")
    saved_emissions_tons: float = Field(..., description="Total CO2 emissions avoided")
    credit_value_usd: float = Field(..., description="Credit value in USD")
    credit_value_inr: float = Field(..., description="Credit value in INR")
    bee_star_improvement: Optional[int] = Field(None, description="Star rating improvement (e.g., 2→4)")
    nabh_verification_status: str = Field(default="PENDING", description="PENDING, VERIFIED, REJECTED")
    blockchain_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    issued_date: datetime = Field(default_factory=datetime.now, description="Credit issuance date")
    expiry_date: Optional[datetime] = Field(None, description="Credit expiry date")
    verification_documents: List[str] = Field(default_factory=list, description="Supporting documents")


class CarbonCreditReport(BaseModel):
    """Complete carbon credit generation report"""
    hospital_id: str = Field(..., description="Hospital identifier")
    generated_at: datetime = Field(default_factory=datetime.now)
    bee_compliance: BEECompliance = Field(..., description="BEE compliance assessment")
    energy_savings: EnergySavingsPlan = Field(..., description="Energy savings plan")
    carbon_credits: CarbonCreditDetails = Field(..., description="Carbon credit details")
    verified_credit: Optional[NABHVerifiedCredit] = Field(None, description="NABH-verified credit")
    recommended_measures: List[Dict] = Field(..., description="All recommended BEE measures")
