import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env for API key
load_dotenv(".env.local")

class SurgePredictor:
    """
    Dynamic Surge Prediction Engine
    Calculates risk based on live environmental factors and uses Gemini for narrative.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('prediction_agent')
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.logger.info("Gemini AI initialized in SurgePredictor.")
        else:
            self.model = None
            self.logger.warning("GEMINI_API_KEY not found. AI narratives disabled.")
        
    def predict(self, date_str: str, aqi: float, weather: dict, events: list):
        """
        Calculate surge risk based on inputs and generate AI narrative
        """
        multiplier = 1.0
        risk_factors = []
        
        # 1. AQI Factor
        if aqi > 400:
            multiplier += 0.5
            risk_factors.append(f"Severe AQI ({aqi:.0f})")
        elif aqi > 300:
            multiplier += 0.2
            risk_factors.append(f"Very Poor AQI ({aqi:.0f})")
        elif aqi > 200:
            multiplier += 0.1
            risk_factors.append(f"Poor AQI ({aqi:.0f})")
            
        # 2. Weather Factor
        max_temp = weather.get('max_temp', 0)
        rainfall = weather.get('rainfall', 0)
        
        if rainfall > 50:
            multiplier += 0.3
            risk_factors.append(f"Heavy Rainfall ({rainfall:.1f}mm)")
        elif rainfall > 10:
            multiplier += 0.1
            
        if max_temp > 36:
            multiplier += 0.2
            risk_factors.append(f"Extreme Heat ({max_temp:.1f}C)")
            
        # 3. Event Factor
        for event in events:
            if event in ['Diwali', 'Ganesh Chaturthi']:
                multiplier += 0.3
                risk_factors.append(f"Major Festival ({event})")
            elif event == 'Monsoon Season':
                multiplier += 0.1
                
        # Determine Severity
        severity = 'none'
        if multiplier >= 2.0: severity = 'critical'
        elif multiplier >= 1.7: severity = 'major'
        elif multiplier >= 1.4: severity = 'moderate'
        elif multiplier >= 1.2: severity = 'minor'
            
        # 4. Generate Narrative with Gemini
        narrative = "Normal operations"
        if self.model and (multiplier > 1.1 or risk_factors):
            try:
                prompt = f"""
                Generate a very short (max 10 words) medical/environmental alert for a hospital in Mumbai on {date_str}.
                Risk Factors: {', '.join(risk_factors)}.
                Surge Multiplier: {multiplier}x.
                Output simple text like: "High respiratory load due to severe smog".
                """
                response = self.model.generate_content(prompt)
                narrative = response.text.strip()
            except Exception as e:
                self.logger.error(f"Gemini error: {e}")
                narrative = ", ".join(risk_factors) if risk_factors else "Elevated risk detected"

        return {
            'multiplier': round(multiplier, 2),
            'severity': severity,
            'risk_factors': risk_factors,
            'narrative': narrative
        }

# Singleton
surge_predictor = SurgePredictor()
