"""
Resource Recommendation Service
Calculates medical supply requirements based on surge predictions
Uses NESCO logic without modifying surge_predictor
"""

import os
import json
import logging
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from src.services.resource_mappings import (
    HOSPITAL_NAME_MAPPING,
    HOSPITAL_TYPES,
    SUPPLY_REQUIREMENTS,
    SAFETY_BUFFERS
)

# Load environment
load_dotenv(".env.local")

logger = logging.getLogger('resource_service')


class ResourceService:
    """Service for calculating hospital resource requirements"""
    
    def __init__(self, inventory_file="data/hospital_inventory.json"):
        """Initialize resource service"""
        self.inventory_data = self._load_inventory(inventory_file)
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro-latest')
            logger.info("Gemini AI initialized for resource recommendations")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not found. Using basic calculations only.")
    
    def _load_inventory(self, filepath):
        """Load hospital inventory from JSON file"""
        abs_path = os.path.abspath(filepath)
        logger.info(f"Loading inventory from: {abs_path}")
        
        if not os.path.exists(filepath):
            logger.warning(f"Inventory file not found: {filepath} (Abs: {abs_path})")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                inventory_array = json.load(f)
            
            # Simple direct mapping - inventory already uses hospital_id
            inventory_dict = {}
            for hospital in inventory_array:
                hospital_id = hospital.get('hospital_id')
                
                if hospital_id:
                    inventory_dict[hospital_id] = {
                        'name': HOSPITAL_NAME_MAPPING.get(hospital_id, hospital_id),
                        'type': HOSPITAL_TYPES.get(hospital_id, 'Unknown'),
                        'inventory': {
                            'Oxygen Cylinders': hospital.get('Oxygen_cylinders', 0),
                            'Ventilators': hospital.get('Ventilators', 0),
                            'Oxygen Masks': hospital.get('Oxygen_masks', 0),
                            'Humidifiers': hospital.get('Humidifiers', 0),
                            'Trauma Stretchers': hospital.get('Trauma_stretchers', 0),
                            'IV Stand Kits': hospital.get('IV_stand_kits', 0),
                            'Defibrillators': hospital.get('Defibrillators', 0),
                            'Gloves/PPE': hospital.get('Gloves_aprons_PPE', 0),
                            'Cooling Pads': hospital.get('Cooling_pads_ice_packs', 0),
                            'Thermometers': hospital.get('Thermometers', 0)
                        }
                    }
                    logger.info(f"Loaded: {hospital_id} ({inventory_dict[hospital_id]['name']})")
                else:
                    logger.warning(f"Skipping entry without hospital_id: {hospital}")
            
            logger.info(f"Loaded inventory for {len(inventory_dict)} hospitals")
            logger.info(f"Hospital IDs: {sorted(inventory_dict.keys())}")
            return inventory_dict
            
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            return {}
    
    def get_latest_surge_data(self, surge_csv="data/continuous_surge_predictions.csv"):
        """Get latest surge predictions from CSV"""
        try:
            df = pd.read_csv(surge_csv)
            
            # Get only the most recent predictions (days_ahead=0, i.e., today)
            latest = df[df['days_ahead'] == 0].copy()
            
            # Group by hospital and sum admission types
            surge_by_hospital = {}
            for hospital_id in latest['hospital_id'].unique():
                hospital_data = latest[latest['hospital_id'] == hospital_id].iloc[0]
                
                surge_by_hospital[hospital_id] = {
                    'respiratory': int(hospital_data.get('respiratory_admissions', 0)),
                    'waterborne': int(hospital_data.get('waterborne_admissions', 0)),
                    'heat_related': int(hospital_data.get('heat_related_admissions', 0)),
                    'trauma': int(hospital_data.get('trauma_admissions', 0)),
                    'other': int(hospital_data.get('other_admissions', 0))
                }
            
            logger.info(f"Loaded surge data for {len(surge_by_hospital)} hospitals")
            return surge_by_hospital
            
        except Exception as e:
            logger.error(f"Error loading surge data: {e}")
            return {}
    
    def calculate_supply_needs(self, hospital_id, admissions):
        """Calculate supply requirements for a hospital"""
        supplies_status = []
        
        hospital_info = self.inventory_data.get(hospital_id, {})
        hospital_type = hospital_info.get('type', 'Private')
        safety_buffer = 1 + SAFETY_BUFFERS.get(hospital_type, 0.2)
        current_inventory = hospital_info.get('inventory', {})
        
        logger.info(f"[RESOURCE CALC] Hospital: {hospital_id} ({hospital_type})")
        logger.info(f"[ADMISSIONS] Respiratory: {admissions.get('respiratory', 0)}, "
                   f"Waterborne: {admissions.get('waterborne', 0)}, "
                   f"Heat: {admissions.get('heat_related', 0)}, "
                   f"Trauma: {admissions.get('trauma', 0)}, "
                   f"Other: {admissions.get('other', 0)}")
        logger.info(f"[SAFETY BUFFER] {int((safety_buffer - 1) * 100)}% ({hospital_type})")
        
        for supply_name, requirements in SUPPLY_REQUIREMENTS.items():
            # Calculate base need
            base_need = sum(
                admissions.get(category, 0) * requirements.get(category, 0)
                for category in ['respiratory', 'waterborne', 'heat_related', 'trauma', 'other']
            )
            
            # Apply safety buffer
            projected_need = int(base_need * safety_buffer)
            
            # Get current stock
            current_stock = current_inventory.get(supply_name, 0)
            
            # Determine status
            stock_percentage = (current_stock / projected_need * 100) if projected_need > 0 else 100
            
            if stock_percentage < 50:
                status = "CRITICAL"
                action = "ORDER_IMMEDIATELY"
            elif stock_percentage < 80:
                status = "LOW"
                action = "ORDER_IMMEDIATELY"
            else:
                status = "OK"
                action = "None"
            
            # Calculate order quantity
            quantity_to_order = max(0, projected_need - current_stock)
            
            logger.info(f"[{supply_name}] Stock: {current_stock}, Need: {projected_need}, "
                       f"Status: {status}, Order: {quantity_to_order}")
            
            supplies_status.append({
                "item_name": supply_name,
                "current_stock": current_stock,
                "projected_need": projected_need,
                "stock_percentage": round(stock_percentage, 1),
                "status": status,
                "action_required": action,
                "quantity_to_order": quantity_to_order
            })
        
        return supplies_status
    


    def generate_public_advisory(self, hospital_name, admissions, surge_multiplier):
        """Generate public health advisory using Gemini"""
        if not self.model:
            return {
                "level": "MODERATE",
                "message": "Standard health precautions advised.",
                "actions": ["Wear masks in crowded areas", "Stay hydrated"]
            }
            
        try:
            prompt = f"""
            Generate a concise public health advisory for {hospital_name}.
            Context:
            - Predicted Admissions: {sum(admissions.values())}
            - Surge Multiplier: {surge_multiplier}x
            - Disease Breakdown: {json.dumps(admissions)}
            
            Output JSON only:
            {{
                "level": "LOW/MODERATE/HIGH/CRITICAL",
                "message": "One sentence summary",
                "actions": ["Action 1", "Action 2", "Action 3"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            
        except Exception as e:
            logger.error(f"Gemini advisory error: {e}")
            return {
                "level": "MODERATE",
                "message": "Follow standard health guidelines.",
                "actions": ["Monitor local health updates", "Maintain hygiene"]
            }

    def calculate_staff_requirements(self, hospital_id, admissions):
        """Calculate staff requirements using Gemini based on predicted admissions"""
        total_patients = sum(admissions.values())
        
        if not self.model:
            # Fallback logic based on standard ratios
            doctors_needed = max(int(total_patients / 15), 5)
            nurses_needed = max(int(total_patients / 5), 15)
            support_needed = max(int(total_patients / 10), 8)
            
            return {
                "doctors": {"required": doctors_needed, "status": "CALCULATED"},
                "nurses": {"required": nurses_needed, "status": "CALCULATED"},
                "support": {"required": support_needed, "status": "CALCULATED"}
            }
            
        try:
            prompt = f"""
            You are a healthcare resource planning expert. Calculate optimal staff requirements for {hospital_id}.
            
            Predicted Patient Load:
            - Total Patients: {total_patients}
            - Respiratory Cases: {admissions.get('respiratory', 0)}
            - Waterborne Cases: {admissions.get('waterborne', 0)}
            - Heat-related Cases: {admissions.get('heat', 0)}
            - Trauma Cases: {admissions.get('trauma', 0)}
            - Other Cases: {admissions.get('other', 0)}
            
            Apply standard healthcare staffing ratios:
            - Doctors: 1 doctor per 15-20 patients (ICU cases need 1:5)
            - Nurses: 1 nurse per 5-6 patients (ICU cases need 1:2)
            - Support Staff: 1 support per 10-12 patients
            
            Consider disease severity:
            - Respiratory and Trauma cases often need ICU care (higher staff ratios)
            - Waterborne and Heat cases typically need general ward care
            
            Return ONLY valid JSON in this exact format:
            {{
                "doctors": {{"required": <number>, "status": "CALCULATED"}},
                "nurses": {{"required": <number>, "status": "CALCULATED"}},
                "support": {{"required": <number>, "status": "CALCULATED"}}
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up response
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            result = json.loads(result_text)
            
            logger.info(f"Gemini staff calculation for {hospital_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini staffing error: {e}")
            # Fallback calculation
            doctors_needed = max(int(total_patients / 15), 5)
            nurses_needed = max(int(total_patients / 5), 15)
            support_needed = max(int(total_patients / 10), 8)
            
            return {
                "doctors": {"required": doctors_needed, "status": "FALLBACK"},
                "nurses": {"required": nurses_needed, "status": "FALLBACK"},
                "support": {"required": support_needed, "status": "FALLBACK"}
            }

    def get_recommendations(self, hospital_id=None):
        """Get resource recommendations for hospital(s)"""
        logger.info("="*80)
        logger.info(f"[RESOURCE SERVICE] Getting recommendations for: {hospital_id or 'ALL HOSPITALS'}")
        
        surge_data = self.get_latest_surge_data()
        
        if not surge_data:
            logger.error("[ERROR] No surge data available")
            return {"error": "No surge data available"}
        
        results = []
        
        # Single hospital or all hospitals
        hospitals_to_process = [hospital_id] if hospital_id else surge_data.keys()
        
        for hid in hospitals_to_process:
            if hid not in surge_data:
                logger.warning(f"[SKIP] Hospital {hid} not found in surge data")
                continue
            
            hospital_info = self.inventory_data.get(hid, {})
            admissions = surge_data.get(hid, {})
            
            # 1. Supply Recommendations
            supplies_status = self.calculate_supply_needs(hid, admissions)
            
            # 2. Staff Requirements (Gemini-based only)
            staff_reqs = self.calculate_staff_requirements(hid, admissions)
            
            # 3. Public Advisory
            surge_multiplier = 1.2 # Placeholder, ideally get from surge data
            advisory = self.generate_public_advisory(hospital_info.get('name', hid), admissions, surge_multiplier)
            
            # Count critical/low items
            critical_count = sum(1 for s in supplies_status if s['status'] == 'CRITICAL')
            low_count = sum(1 for s in supplies_status if s['status'] == 'LOW')
            
            logger.info(f"[SUMMARY] {hid}: {critical_count} CRITICAL, {low_count} LOW")
            
            result = {
                "hospital_id": hid,
                "hospital_name": hospital_info.get('name', HOSPITAL_NAME_MAPPING.get(hid, hid)),
                "hospital_type": hospital_info.get('type', 'Unknown'),
                "admissions": admissions,
                "supplies_status": supplies_status,
                "staff_requirements": staff_reqs,
                "public_advisory": advisory,
                "summary": {
                    "total_items": len(supplies_status),
                    "critical_items": critical_count,
                    "low_items": low_count,
                    "ok_items": len(supplies_status) - critical_count - low_count
                }
            }
            
            results.append(result)
        
        logger.info("="*80)
        return results if not hospital_id else (results[0] if results else {})


# Singleton instance
resource_service = ResourceService()
