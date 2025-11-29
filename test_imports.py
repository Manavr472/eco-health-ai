
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Testing imports...")
    from api.main import app
    from sustainability.baseline import estimate_baseline_energy
    from sustainability.emissions import calculate_carbon
    from sustainability.energy import estimate_energy
    from sustainability.factors import FACTOR_DB
    from sustainability.llm import generate_hospital_advisory
    from sustainability.llm_energy import estimate_energy_smart
    from models.carbon_models import CarbonReport
    
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
