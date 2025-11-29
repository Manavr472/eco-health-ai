import csv
import json
import argparse
import os
import google.generativeai as genai
import config
from hospital_mapping import HOSPITAL_NAME_MAPPING, HOSPITAL_TYPES

class ResourcingAgent:
    def __init__(self, inventory_file, api_key=None, model_name=None):
        self.inventory_data = self._load_inventory(inventory_file)
        self.surge_data = []
        
        # Use config defaults if not provided
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _load_inventory(self, filepath):
        """Load inventory from Hsupply.json (array format) and convert to dict by hospital ID"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Inventory file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            inventory_array = json.load(f)
        
        # Convert array to dictionary keyed by hospital ID
        inventory_dict = {}
        for hospital in inventory_array:
            hospital_name = hospital.get('hospital_name')
            # Find matching hospital ID from mapping
            hospital_id = None
            for hid, hname in HOSPITAL_NAME_MAPPING.items():
                if hname == hospital_name:
                    hospital_id = hid
                    break
            
            if hospital_id:
                inventory_dict[hospital_id] = {
                    'name': hospital_name,
                    'type': HOSPITAL_TYPES.get(hospital_id, 'Unknown'),
                    'inventory': {
                        'Oxygen Cylinders': hospital.get('Oxygen_cylinders', 0),
                        'Ventilators': hospital.get('Ventilators', 0),
                        'Oxygen Masks': hospital.get('Oxygen_masks', 0),
                        'Humidifiers': hospital.get('Humidifiers', 0),
                        'Trauma Stretchers': hospital.get('Trauma_stretchers', 0),
                        'IV Stand Kits': hospital.get('IV_stand_kits', 0),
                        'Defibrillators': hospital.get('Defibrillators', 0),
                        'Gloves/Aprons/PPE': hospital.get('Gloves_aprons_PPE', 0),
                        'Cooling Pads/Ice Packs': hospital.get('Cooling_pads_ice_packs', 0),
                        'Thermometers': hospital.get('Thermometers', 0)
                    }
                }
        
        return inventory_dict


    def load_surge_data(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Surge data file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            self.surge_data = list(reader)

    def calculate_requirements_for_hospital(self, hospital_id):
        hospital_info = self.inventory_data.get(hospital_id)
        if not hospital_info:
            return {"status": "error", "message": f"Hospital ID {hospital_id} not found in inventory."}

        # Filter surge data for this hospital
        hospital_surge = [case for case in self.surge_data if case.get('hospital_id') == hospital_id]
        if not hospital_surge:
             return {"status": "warning", "message": f"No surge data found for hospital {hospital_id}"}

        # Update field names for category-based data
        surge_summary = "\n".join([f"- {case.get('admission_category', case.get('case_type'))}: {case.get('predicted_admissions', case.get('predicted_cases'))} admissions" for case in hospital_surge])
        inventory_summary = json.dumps(hospital_info['inventory'], indent=2)
        
        prompt = f"""
        Act as a medical resourcing expert for {hospital_info['name']} ({hospital_info['type']} Hospital) in Mumbai.
        
        **CRITICAL: Calculate ONLY for the 10 supplies in the inventory dataset**
        
        **Available Supplies:**
        {inventory_summary}
        
        **Per-Patient Supply Requirements by Admission Category:**
        
        1. **Oxygen Cylinders**: Airborne(0.3), Waterborne(0.05), Heat-related(0.2), Trauma(0.3), Other(0.25)
        2. **Ventilators**: Airborne(0.1), Waterborne(0.02), Heat-related(0.05), Trauma(0.15), Other(0.08)
        3. **Oxygen Masks**: Airborne(2), Waterborne(0.5), Heat-related(1.5), Trauma(2), Other(1.5)
        4. **Humidifiers**: Airborne(0.3), Waterborne(0.05), Heat-related(0.1), Trauma(0.2), Other(0.15)
        5. **Trauma Stretchers**: Airborne(0.1), Waterborne(0.05), Heat-related(0.2), Trauma(1.0), Other(0.15)
        6. **IV Stand Kits**: Airborne(0.6), Waterborne(0.8), Heat-related(0.9), Trauma(0.95), Other(0.7)
        7. **Defibrillators**: Airborne(0.02), Waterborne(0.01), Heat-related(0.05), Trauma(0.08), Other(0.15)
        8. **Gloves/Aprons/PPE**: Airborne(25), Waterborne(20), Heat-related(12), Trauma(30), Other(15)
        9. **Cooling Pads/Ice Packs**: Airborne(2), Waterborne(1), Heat-related(15), Trauma(3), Other(2)
        10. **Thermometers**: Airborne(0.5), Waterborne(0.3), Heat-related(0.6), Trauma(0.4), Other(0.4)
        
        **Safety Buffer:** {hospital_info['type']} hospital = {'30%' if hospital_info['type'] == 'Municipal' else '20%'}
        
        **Formula:**
        For each supply: Base Need = Sum(Category Admissions × Per-Patient Rate)
        Final Need = Base Need × (1 + Safety Buffer)
        Order = max(0, Final Need - Current Stock)
        
        **Status:** CRITICAL(<50%), LOW(50-80%), OK(>80%)
        
        **Admissions:**
        {surge_summary}
        
        **Task:** Calculate for ALL 10 supplies. Return JSON:
        {{
            "hospital_id": "{hospital_id}",
            "hospital_name": "{hospital_info['name']}",
            "hospital_type": "{hospital_info['type']}",
            "safety_buffer_applied": "{'30%' if hospital_info['type'] == 'Municipal' else '20%'}",
            "supplies_status": [
                {{
                    "item_name": "Supply name",
                    "current_stock": <number>,
                    "projected_need": <number>,
                    "calculation_note": "Formula",
                    "status": "OK/LOW/CRITICAL",
                    "action_required": "None/ORDER_IMMEDIATELY",
                    "quantity_to_order": <number>
                }}
            ]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except Exception as e:
            print(f"Error calling LLM for {hospital_id}: {e}")
            return {"status": "error", "message": str(e)}

    def generate_report(self, output_file, target_hospital_id=None):
        report = {"reports": []}
        
        if target_hospital_id:
            result = self.calculate_requirements_for_hospital(target_hospital_id)
            report["reports"].append(result)
        else:
            # Run for all hospitals in inventory
            for hospital_id in self.inventory_data.keys():
                print(f"Processing {hospital_id}...")
                result = self.calculate_requirements_for_hospital(hospital_id)
                report["reports"].append(result)

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"Report generated: {output_file}")
        return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resourcing Agent")
    parser.add_argument("--surge_data", default=config.DEFAULT_SURGE_DATA, help="Path to surge prediction CSV")
    parser.add_argument("--inventory", default=config.DEFAULT_INVENTORY, help="Path to current inventory JSON")
    parser.add_argument("--output", default=config.DEFAULT_OUTPUT, help="Path to output JSON report")
    parser.add_argument("--api_key", help="Google Gemini API Key (defaults to config.py)")
    parser.add_argument("--model_name", help="Gemini model name (defaults to config.py)")
    parser.add_argument("--hospital_id", help="Specific Hospital ID to process (optional)")

    args = parser.parse_args()

    agent = ResourcingAgent(args.inventory, args.api_key, args.model_name)
    agent.load_surge_data(args.surge_data)
    agent.generate_report(args.output, args.hospital_id)
