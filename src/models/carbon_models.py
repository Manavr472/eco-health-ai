from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class AlertLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class EnergyAlert(BaseModel):
    alert_level: AlertLevel
    current_energy_kwh: float
    baseline_energy_kwh: float
    percentage_above_baseline: float
    threshold_exceeded: bool
    message: str

class EmissionFactor(BaseModel):
    source: str
    region: str
    value: float
    unit: str
    valid_from: str

class CalculationLog(BaseModel):
    formula: str
    arithmetic: str
    result: float

class ForecastRecord(BaseModel):
    timestamp: datetime
    hospital_id: str
    predicted_admissions: int
    surge_multiplier: float
    contributing_factors: List[str]


class EmissionResult(BaseModel):
    record_id: str
    energy_consumption_kwh: float
    total_emissions_kg: float
    total_emissions_tons: float
    scope: str
    factor_used: EmissionFactor
    energy_reasoning: Optional[str] = None
    calculation_log: Optional[CalculationLog] = None


class EnergyMeasure(BaseModel):
    name: str
    category: str
    savings_percentage: float
    cost_inr_per_bed: float
    payback_months: float
    priority: str
    description: str

class BEECompliance(BaseModel):
    epi_score: float
    star_rating: int
    compliance_status: str
    improvement_gap: float
    max_star_rating: int = 5

class EnergySavingsPlan(BaseModel):
    recommended_measures: List[EnergyMeasure]
    total_potential_savings_kwh: float
    total_investment_inr: float
    roi_months: float
    savings_percentage: float

class CarbonCreditDetails(BaseModel):
    credits_generated: float
    market_value_usd: float
    credit_value_inr: float
    verification_status: str
    registry_id: Optional[str] = None

class NABHVerifiedCredit(BaseModel):
    verification_id: str
    verifier_name: str
    verification_date: datetime
    compliance_score: float
    digital_signature: str

class HospitalReport(BaseModel):
    hospital_id: str
    total_admissions: int
    energy_consumption_kwh: float
    carbon_emissions_kg: float
    alert_level: str
    advisory: str
    bee_compliance: Optional[BEECompliance] = None
    savings_plan: Optional[EnergySavingsPlan] = None
    carbon_credits: Optional[CarbonCreditDetails] = None
    # Department breakdown
    trauma_admissions: Optional[int] = 0
    respiratory_admissions: Optional[int] = 0
    waterborne_admissions: Optional[int] = 0
    other_admissions: Optional[int] = 0

class CarbonReport(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.now)
    total_surge_patients: int
    total_energy_kwh: float
    total_emissions_kg: float
    hospital_reports: List[HospitalReport] = Field(..., description="Per-hospital detailed reports")
    results: List[EmissionResult] = Field(..., description="Legacy emission results (for backward compatibility)")
    general_advisory: Optional[str] = Field(None, description="Overall AI-generated advisory across all hospitals")

class CarbonCreditReport(BaseModel):
    hospital_id: str
    generated_at: datetime
    bee_compliance: BEECompliance
    energy_savings: EnergySavingsPlan
    carbon_credits: CarbonCreditDetails
    nabh_verification: Optional[NABHVerifiedCredit] = None
