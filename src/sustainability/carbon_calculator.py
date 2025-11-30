"""
Carbon Calculator
Calculates carbon emissions for baseline vs optimized hospital operations
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import (
    CARBON_EMISSIONS, RESOURCE_CONSUMPTION,
    OPTIMIZATION_BENEFITS, NUM_HOSPITALS
)


class CarbonCalculator:
    """Calculate carbon emissions and sustainability metrics"""
    
    def __init__(self):
        self.emission_factors = CARBON_EMISSIONS
        self.consumption_rates = RESOURCE_CONSUMPTION
        self.optimization = OPTIMIZATION_BENEFITS
    
    def calculate_baseline_emissions(self, admissions, surge_multiplier=1.0):
        """
        Calculate baseline (chaotic) carbon emissions
        In chaos scenario, hospital over-provisions and wastes resources
        """
        
        # In chaotic scenario, hospital guesstimates needs
        # Apply inefficiency factor based on surge
        if surge_multiplier > 1.5:
            inefficiency = 1.6  # 60% waste in crisis
        elif surge_multiplier > 1.2:
            inefficiency = 1.4  # 40% waste in moderate surge
        else:
            inefficiency = 1.2  # 20% baseline inefficiency
        
        # Calculate resource consumption (with waste)
        electricity_kwh = admissions * self.consumption_rates['electricity_kwh_per_patient'] * inefficiency
        water_liters = admissions * self.consumption_rates['water_liters_per_patient'] * inefficiency
        medical_waste_kg = admissions * self.consumption_rates['medical_waste_kg_per_patient'] * inefficiency
        
        # Staff commuting (chaos = staff called in urgently, more trips)
        staff_count = int(admissions * 0.4)  # Rough staff ratio
        staff_commute_km = staff_count * self.consumption_rates['avg_staff_commute_km'] * (1.5 if surge_multiplier > 1.3 else 1.0)
        
        # Supply transport (chaos = emergency orders, multiple small shipments)
        supply_trips = int(admissions / 20) * (2 if surge_multiplier > 1.3 else 1)  # More trips in chaos
        supply_transport_km = supply_trips * self.consumption_rates['avg_supply_distance_km']
        
        # Calculate emissions
        emissions = {
            'electricity': electricity_kwh * self.emission_factors['electricity_kwh'],
            'water': water_liters * self.emission_factors['water_liter'],
            'medical_waste': medical_waste_kg * self.emission_factors['medical_waste_kg'],
            'staff_commute': staff_commute_km * self.emission_factors['staff_commute_km'],
            'supply_transport': supply_transport_km * self.emission_factors['supply_transport_km']
        }
        
        total_emissions = sum(emissions.values())
        
        return {
            'total_kg_co2': total_emissions,
            'breakdown': emissions,
            'inefficiency_factor': inefficiency,
            'resource_consumption': {
                'electricity_kwh': electricity_kwh,
                'water_liters': water_liters,
                'medical_waste_kg': medical_waste_kg,
                'staff_commute_km': staff_commute_km,
                'supply_transport_km': supply_transport_km
            }
        }
    
    def calculate_optimized_emissions(self, admissions, surge_multiplier=1.0):
        """
        Calculate optimized carbon emissions with AI predictions
        AI enables precise resource allocation, reducing waste
        """
        
        # With AI optimization, minimal waste
        efficiency_improvement = 1.0  # No waste
        
        # Calculate precise resource consumption
        electricity_kwh = admissions * self.consumption_rates['electricity_kwh_per_patient']
        water_liters = admissions * self.consumption_rates['water_liters_per_patient']
        medical_waste_kg = admissions * self.consumption_rates['medical_waste_kg_per_patient']
        
        # Apply optimization benefits
        electricity_kwh *= (1 - self.optimization['energy_reduction'])
        medical_waste_kg *= (1 - self.optimization['supply_waste_reduction'])
        
        # Optimized staff deployment (pre-scheduled, efficient commuting)
        staff_count = int(admissions * 0.4)
        staff_commute_km = staff_count * self.consumption_rates['avg_staff_commute_km']
        staff_commute_km *= (1 - self.optimization['staff_efficiency'])
        
        # Optimized supply chain (bulk pre-orders, consolidated shipments)
        supply_trips = int(admissions / 50)  # Bulk orders
        supply_transport_km = supply_trips * self.consumption_rates['avg_supply_distance_km']
        supply_transport_km *= (1 - self.optimization['transport_optimization'])
        
        # Calculate emissions
        emissions = {
            'electricity': electricity_kwh * self.emission_factors['electricity_kwh'],
            'water': water_liters * self.emission_factors['water_liter'],
            'medical_waste': medical_waste_kg * self.emission_factors['medical_waste_kg'],
            'staff_commute': staff_commute_km * self.emission_factors['staff_commute_km'],
            'supply_transport': supply_transport_km * self.emission_factors['supply_transport_km']
        }
        
        total_emissions = sum(emissions.values())
        
        return {
            'total_kg_co2': total_emissions,
            'breakdown': emissions,
            'efficiency_factor': 1.0,
            'resource_consumption': {
                'electricity_kwh': electricity_kwh,
                'water_liters': water_liters,
                'medical_waste_kg': medical_waste_kg,
                'staff_commute_km': staff_commute_km,
                'supply_transport_km': supply_transport_km
            }
        }
    
    def calculate_carbon_reduction(self, admissions, surge_multiplier=1.0):
        """Calculate carbon reduction from baseline to optimized"""
        
        baseline = self.calculate_baseline_emissions(admissions, surge_multiplier)
        optimized = self.calculate_optimized_emissions(admissions, surge_multiplier)
        
        reduction_kg = baseline['total_kg_co2'] - optimized['total_kg_co2']
        reduction_tons = reduction_kg / 1000
        reduction_percent = (reduction_kg / baseline['total_kg_co2']) * 100
        
        return {
            'baseline_emissions_kg': baseline['total_kg_co2'],
            'optimized_emissions_kg': optimized['total_kg_co2'],
            'reduction_kg': reduction_kg,
            'reduction_tons': reduction_tons,
            'reduction_percent': reduction_percent,
            'baseline_breakdown': baseline['breakdown'],
            'optimized_breakdown': optimized['breakdown'],
            'resource_savings': self._calculate_resource_savings(
                baseline['resource_consumption'],
                optimized['resource_consumption']
            )
        }
    
    def _calculate_resource_savings(self, baseline_resources, optimized_resources):
        """Calculate actual resource savings"""
        savings = {}
        for resource, baseline_value in baseline_resources.items():
            optimized_value = optimized_resources[resource]
            savings[resource] = {
                'baseline': baseline_value,
                'optimized': optimized_value,
                'saved': baseline_value - optimized_value,
                'percent_reduction': ((baseline_value - optimized_value) / baseline_value * 100) if baseline_value > 0 else 0
            }
        return savings
    
    def calculate_surge_event_carbon_credits(self, patient_df, event_dates):
        """Calculate carbon credits for a specific surge event"""
        
        # Filter data for event dates
        event_data = patient_df[
            (patient_df['date'] >= event_dates['start']) &
            (patient_df['date'] <= event_dates['end'])
        ]
        
        if event_data.empty:
            return None
        
        total_reduction = 0
        daily_reductions = []
        
        for _, day_data in event_data.iterrows():
            admissions = day_data['total_admissions']
            surge_mult = day_data['surge_multiplier']
            
            reduction = self.calculate_carbon_reduction(admissions, surge_mult)
            total_reduction += reduction['reduction_kg']
            
            daily_reductions.append({
                'date': day_data['date'],
                'admissions': admissions,
                'surge_multiplier': surge_mult,
                'reduction_kg': reduction['reduction_kg']
            })
        
        return {
            'event_period': event_dates,
            'total_reduction_kg': total_reduction,
            'total_reduction_tons': total_reduction / 1000,
            'total_admissions': event_data['total_admissions'].sum(),
            'avg_surge_multiplier': event_data['surge_multiplier'].mean(),
            'daily_reductions': daily_reductions
        }


if __name__ == "__main__":
    calculator = CarbonCalculator()
    
    print("=" * 70)
    print("CARBON EMISSION CALCULATOR DEMO")
    print("=" * 70)
    
    # Example: Compare baseline vs optimized for a surge event
    admissions = 300  # Surge scenario
    surge_multiplier = 2.0
    
    print(f"\nScenario: {admissions} patients, {surge_multiplier}x surge")
    print("-" * 70)
    
    baseline = calculator.calculate_baseline_emissions(admissions, surge_multiplier)
    print(f"\nBaseline (Chaotic) Emissions:")
    print(f"  Total: {baseline['total_kg_co2']:.2f} kg CO2 ({baseline['total_kg_co2']/1000:.3f} tons)")
    print(f"  Inefficiency factor: {baseline['inefficiency_factor']}x")
    print(f"  Breakdown:")
    for source, emission in baseline['breakdown'].items():
        print(f"    • {source}: {emission:.2f} kg CO2")
    
    optimized = calculator.calculate_optimized_emissions(admissions, surge_multiplier)
    print(f"\nOptimized (AI-Predicted) Emissions:")
    print(f"  Total: {optimized['total_kg_co2']:.2f} kg CO2 ({optimized['total_kg_co2']/1000:.3f} tons)")
    print(f"  Breakdown:")
    for source, emission in optimized['breakdown'].items():
        print(f"    • {source}: {emission:.2f} kg CO2")
    
    reduction = calculator.calculate_carbon_reduction(admissions, surge_multiplier)
    print(f"\n" + "=" * 70)
    print(f"CARBON REDUCTION ACHIEVED")
    print(f"=" * 70)
    print(f"Reduction: {reduction['reduction_kg']:.2f} kg CO2 ({reduction['reduction_tons']:.3f} tons)")
    print(f"Percentage: {reduction['reduction_percent']:.1f}%")
    
    print(f"\nResource Savings:")
    for resource, data in reduction['resource_savings'].items():
        if data['saved'] > 0:
            print(f"  • {resource}: {data['saved']:.1f} units ({data['percent_reduction']:.1f}% reduction)")
