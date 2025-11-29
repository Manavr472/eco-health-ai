import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict

# Load environment variables
load_dotenv()

# Configure Perplexity API
API_KEY = os.getenv("PERPLEXITY_API_KEY")
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")


def generate_hospital_advisory(hospital_data: dict) -> str:
    """
    Generate targeted, actionable solutions for a specific hospital.
    
    Args:
        hospital_data: Dictionary containing hospital-specific metrics
    
    Returns:
        Concise, actionable solutions (3-5 bullet points)
    """
    if not API_KEY or not client:
        # Fallback advisory
        if hospital_data['alert_level'] == 'CRITICAL':
            return f"""**Immediate Actions Required for {hospital_data['hospital_id']}:**
- Activate emergency energy management protocols
- Optimize HVAC settings for {hospital_data['surge_reasons']} patient load
- Deploy energy-efficient temporary equipment
- Implement load shedding for non-critical areas
- Monitor real-time energy consumption hourly"""
        elif hospital_data['alert_level'] == 'WARNING':
            return f"""**Recommended Actions for {hospital_data['hospital_id']}:**
- Review and optimize HVAC schedules
- Implement energy-efficient protocols for {hospital_data['surge_reasons']} cases
- Audit lighting and equipment usage
- Consider renewable energy backup activation"""
        else:
            return f"""**Maintain Current Performance:**
- Continue current energy management practices
- Monitor for any changes in patient load"""

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an energy efficiency expert for hospitals in India, following BEE standards."
            },
            {
                "role": "user",
                "content": f"""
Hospital: {hospital_data['hospital_id']}
Alert Level: {hospital_data['alert_level']}
Surge Reason: {hospital_data['surge_reasons']}
Current Energy: {hospital_data['current_energy_kwh']:.0f} kWh
Baseline Energy: {hospital_data['baseline_energy_kwh']:.0f} kWh
Percentage Above Baseline: {hospital_data['percentage_above_baseline']:.1f}%
Surge Patients: {hospital_data['surge_patients']}

Generate 3-5 SPECIFIC, ACTIONABLE solutions for THIS hospital to reduce energy consumption.
Focus on immediate actions for {hospital_data['alert_level']} alert level and {hospital_data['surge_reasons']}.
Format as concise bullet points. Be direct and actionable.
"""
            }
        ]
        
        response = client.chat.completions.create(
            model="sonar",
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"**Error generating advisory:** {str(e)}"


def generate_general_advisory(summary: Dict) -> str:
    """
    Generate overall advisory for the entire healthcare system.
    """
    if not API_KEY or not client:
        return "AI Advisory unavailable: PERPLEXITY_API_KEY not found in environment variables."

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an expert Sustainability Consultant for Hospitals in Mumbai, India."
            },
            {
                "role": "user",
                "content": f"""
Analyze the following Carbon Emission Report for Mumbai hospitals:

DATA SUMMARY:
- Total Surge Patients: {summary.get('total_patients')}
- Total Energy Added: {summary.get('total_energy')} kWh
- Total Carbon Emissions: {summary.get('total_emissions')} kgCO2
- Surge Reasons: {summary.get('surge_reasons')}

TASK:
Provide 3-4 specific, system-wide recommendations based on BEE and ECBC standards.
Focus on the specific surge reasons mentioned.
Keep the response concise (under 150 words) and bulleted.
"""
            }
        ]
        
        response = client.chat.completions.create(
            model="sonar",
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AI Advisory generation failed: {str(e)}"
