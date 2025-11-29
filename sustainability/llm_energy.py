import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from typing import Dict, Tuple

load_dotenv()

# Configure Perplexity API
API_KEY = os.getenv("PERPLEXITY_API_KEY")
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

def estimate_energy_with_llm(forecast_data: Dict) -> Dict:
    """
    Uses LLM to estimate energy consumption based on forecasting data.
    Returns: {
        "total_energy_kwh": float,
        "breakdown": {...},
        "reasoning": str
    }
    """
    if not API_KEY or not client:
        raise Exception("PERPLEXITY_API_KEY not configured")

    prompt = f"""
You are an expert in Hospital Energy Management. Estimate the TOTAL energy consumption for the following patient surge scenario.

INPUT DATA:
- Baseline Admissions: {forecast_data.get('baseline_admissions', 0)}
- Respiratory Admissions: {forecast_data.get('respiratory_admissions', 0)}
- Waterborne Admissions: {forecast_data.get('waterborne_admissions', 0)}
- Heat-Related Admissions: {forecast_data.get('heat_related_admissions', 0)}
- Trauma Admissions: {forecast_data.get('trauma_admissions', 0)}
- Other Admissions: {forecast_data.get('other_admissions', 0)}
- Duration: 7 days

ENERGY FACTORS (use these as guidelines):
- Respiratory: ~10 kWh/patient/day (ventilators, oxygen, isolation HVAC)
- Trauma: ~18 kWh/patient/day (ORs, ICU, imaging equipment)
- Heat-related: ~14 kWh/patient/day (intensive cooling)
- Waterborne: ~6 kWh/patient/day (standard ward equipment)
- Other: ~7 kWh/patient/day (general ward)
- Baseline: ~7 kWh/patient/day

TASK:
Calculate the TOTAL energy consumption in kWh for this 7-day period.

Return ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{
  "total_energy_kwh": <number>,
  "breakdown": {{
    "baseline": <number>,
    "respiratory": <number>,
    "trauma": <number>,
    "heat_related": <number>,
    "waterborne": <number>,
    "other": <number>
  }},
  "reasoning": "<brief 1-sentence explanation>"
}}
"""
    
    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse JSON from LLM response
    content = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    result = json.loads(content)
    return result

def estimate_energy_deterministic(forecast_data: Dict) -> Dict:
    """
    Deterministic fallback energy estimation.
    """
    baseline = forecast_data.get('baseline_admissions', 0) * 7 * 7
    respiratory = forecast_data.get('respiratory_admissions', 0) * 10 * 7
    waterborne = forecast_data.get('waterborne_admissions', 0) * 6 * 7
    heat_related = forecast_data.get('heat_related_admissions', 0) * 14 * 7
    trauma = forecast_data.get('trauma_admissions', 0) * 18 * 7
    other = forecast_data.get('other_admissions', 0) * 7 * 7
    
    total = baseline + respiratory + waterborne + heat_related + trauma + other
    
    return {
        "total_energy_kwh": total,
        "breakdown": {
            "baseline": baseline,
            "respiratory": respiratory,
            "trauma": trauma,
            "heat_related": heat_related,
            "waterborne": waterborne,
            "other": other
        },
        "reasoning": "Deterministic calculation using standard energy factors"
    }

def estimate_energy_smart(forecast_data: Dict) -> Tuple[float, str]:
    """
    Hybrid approach: Try LLM first, fallback to deterministic.
    Returns: (total_energy_kwh, reasoning)
    """
    try:
        llm_result = estimate_energy_with_llm(forecast_data)
        return llm_result["total_energy_kwh"], llm_result["reasoning"]
    except Exception as e:
        print(f"LLM estimation failed: {e}, using deterministic fallback")
        det_result = estimate_energy_deterministic(forecast_data)
        return det_result["total_energy_kwh"], det_result["reasoning"]
