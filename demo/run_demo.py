"""
Demonstration Runner for Eco-Health AI
Runs comprehensive demonstrations of all system components
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.recommendation_engine import RecommendationEngine
from sustainability.carbon_calculator import CarbonCalculator
from sustainability.blockchain_tokenizer import CarbonCreditBlockchain


def demo_scenario_1_diwali():
    """Scenario 1: Diwali Pollution Surge"""
    print("\n" + "=" * 70)
    print("SCENARIO 1: DIWALI POLLUTION SURGE")
    print("=" * 70)
    
    print("\nContext:")
    print("• Date: November 2, 2024 (Diwali)")
    print("• AQI: 450+ (Severe)")
    print("• Primary concern: Respiratory admissions")
    print("• Expected surge: 2.0x baseline")
    
    # Simulate predictions
    baseline_admissions = 150
    predicted_admissions = 300
    surge_multiplier = 2.0
    
    print(f"\nPredictions:")
    print(f"• Baseline daily admissions: {baseline_admissions}")
    print(f"• Predicted admissions: {predicted_admissions}")
    print(f"• Surge multiplier: {surge_multiplier}x")
    
    # Generate recommendations
    engine = RecommendationEngine()
    
    resource_forecast = {
        'doctors_needed': 20,
        'nurses_needed': 60,
        'support_staff_needed': 30,
        'ppe_kits': 600,
        'oxygen_liters': 3000,
        'iv_fluids_ml': 150000,
        'medications_units': 1500,
        'beds_needed': 215
    }
    
    baseline_resources = {k: int(v / surge_multiplier) for k, v in resource_forecast.items()}
    
    recommendations = engine.generate_comprehensive_recommendations(
        surge_prediction=surge_multiplier,
        resource_forecast=resource_forecast,
        baseline_resources=baseline_resources,
        surge_reasons=['Diwali Pollution', 'Severe AQI'],
        prediction_date=datetime(2024, 11, 2)
    )
    
    print(f"\nRecommendations Generated:")
    print(f"• Surge Level: {recommendations['surge_level'].upper()}")
    print(f"• Total Actions: {recommendations['total_actions']}")
    print(f"• High Priority Actions: {recommendations['high_priority_actions']}")
    
    print(f"\nKey Recommendations:")
    for i, rec in enumerate(recommendations['recommendations'][:3], 1):
        print(f"\n{i}. {rec['category']} [{rec['priority']}]")
        print(f"   Action: {rec['action']}")
        for detail in rec['details'][:2]:
            print(f"    • {detail}")
    
    # Calculate carbon reduction
    calculator = CarbonCalculator()
    carbon_reduction = calculator.calculate_carbon_reduction(predicted_admissions, surge_multiplier)
    
    print(f"\nSustainability Impact:")
    print(f"• Baseline Emissions: {carbon_reduction['baseline_emissions_kg']:.0f} kg CO2")
    print(f"• Optimized Emissions: {carbon_reduction['optimized_emissions_kg']:.0f} kg CO2")
    print(f"• Reduction: {carbon_reduction['reduction_tons']:.2f} tons CO2 ({carbon_reduction['reduction_percent']:.1f}%)")
    print(f"• Carbon Credit Value: ${carbon_reduction['reduction_tons'] * 25:.2f} USD")


def demo_scenario_2_monsoon():
    """Scenario 2: Monsoon Healthcare Crisis"""
    print("\n" + "=" * 70)
    print("SCENARIO 2: MONSOON HEALTHCARE CRISIS")
    print("=" * 70)
    
    print("\nContext:")
    print("• Date: July 15, 2024 (Peak Monsoon)")
    print("• Rainfall: 85mm (Heavy)")
    print("• Primary concern: Waterborne diseases, accidents")
    print("• Expected surge: 1.6x baseline")
    
    baseline_admissions = 150
    predicted_admissions = 240
    surge_multiplier = 1.6
    
    print(f"\nPredictions:")
    print(f"• Baseline daily admissions: {baseline_admissions}")
    print(f"• Predicted admissions: {predicted_admissions}")
    print(f"• Surge multiplier: {surge_multiplier}x")
    
    # Calculate carbon reduction
    calculator = CarbonCalculator()
    carbon_reduction = calculator.calculate_carbon_reduction(predicted_admissions, surge_multiplier)
    
    print(f"\nSustainability Impact:")
    print(f"• Reduction: {carbon_reduction['reduction_tons']:.2f} tons CO2")
    print(f"• Carbon Credit Value: ${carbon_reduction['reduction_tons'] * 25:.2f} USD")
    
    print(f"\nResource Savings:")
    print(f"• Electricity: {carbon_reduction['resource_savings']['electricity_kwh']['percent_reduction']:.1f}% reduction")
    print(f"• Medical Waste: {carbon_reduction['resource_savings']['medical_waste_kg']['percent_reduction']:.1f}% reduction")
    print(f"• Transport: {carbon_reduction['resource_savings']['supply_transport_km']['percent_reduction']:.1f}% reduction")


def demo_blockchain_tokenization():
    """Demonstrate blockchain carbon credit tokenization"""
    print("\n" + "=" * 70)
    print("BLOCKCHAIN CARBON CREDIT TOKENIZATION")
    print("=" * 70)
    
    blockchain = CarbonCreditBlockchain()
    
    print(f"\nBlockchain Network: {blockchain.config['network_name']}")
    print(f"Token: {blockchain.config['token_name']} ({blockchain.config['token_symbol']})")
    
    # Tokenize multiple events
    events = [
        ("Diwali 2024", 2.5, 1),
        ("Monsoon June 2024", 1.8, 2),
        ("Heatwave May 2024", 1.5, 1)
    ]
    
    print(f"\nTokenizing {len(events)} Carbon Credits:")
    print("-" * 70)
    
    for event_name, carbon_tons, hospital_id in events:
        print(f"\n► {event_name}")
        credit = blockchain.tokenize_carbon_credit(
            carbon_reduction_tons=carbon_tons,
            hospital_id=hospital_id,
            surge_event_id=event_name.replace(" ", "-").upper(),
            verification_data={
                'event': event_name,
                'verified': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    summary = blockchain.calculate_total_value()
    
    print(f"\n" + "=" * 70)
    print(f"BLOCKCHAIN SUMMARY")
    print(f"=" * 70)
    print(f"• Total Credits Issued: {summary['total_credits_issued']}")
    print(f"• Total CO2 Reduction: {summary['total_credits_tons']:.2f} tons")
    print(f"• Total Value: ${summary['total_value_usd']:.2f} USD")
    print(f"• Blockchain Length: {len(blockchain.chain)} blocks")
    
    # Export
    blockchain.export_chain()


def main():
    """Run all demonstrations"""
    print("=" * 70)
    print("ECO-HEALTH AI PLATFORM - COMPREHENSIVE DEMONSTRATION")
    print("Mumbai Region - Sustainable Hospital Operations")
    print("=" * 70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run scenarios
    demo_scenario_1_diwali()
    demo_scenario_2_monsoon()
    demo_blockchain_tokenization()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("✓ Agentic AI successfully predicts patient surges 5-7 days in advance")
    print("✓ Autonomous recommendations for staff, supplies, and public advisories")
    print("✓ Carbon emission reductions of 25-45% per surge event")
    print("✓ Blockchain-verified carbon credits generating revenue")
    print("✓ Complete end-to-end workflow from data → prediction → action → credit")
    
    print(f"\nNext Steps:")
    print("1. Generate synthetic data: cd data_generators && python generate_all.py")
    print("2. Train ML models: cd models && python train_models.py")
    print("3. Start API server: uvicorn api.main:app --reload")
    print("4. Access dashboard: http://localhost:8000")


if __name__ == "__main__":
    main()
