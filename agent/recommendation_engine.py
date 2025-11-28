"""
Recommendation Engine for Eco-Health AI
Generates actionable recommendations for hospital operations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RECOMMENDATION_THRESHOLDS, SURGE_FACTORS


class RecommendationEngine:
    """Generate actionable recommendations based on predictions"""
    
    def __init__(self):
        self.thresholds = RECOMMENDATION_THRESHOLDS
    
    def _classify_surge_level(self, surge_multiplier):
        """Classify surge severity level"""
        if surge_multiplier >= self.thresholds['critical_surge']:
            return 'critical'
        elif surge_multiplier >= self.thresholds['major_surge']:
            return 'major'
        elif surge_multiplier >= self.thresholds['moderate_surge']:
            return 'moderate'
        elif surge_multiplier >= self.thresholds['minor_surge']:
            return 'minor'
        else:
            return 'normal'
    
    def generate_staff_deployment(self, resource_forecast, surge_level):
        """Generate staff deployment recommendations"""
        recommendations = []
        
        doctors = resource_forecast['doctors_needed']
        nurses = resource_forecast['nurses_needed']
        support = resource_forecast['support_staff_needed']
        
        if surge_level in ['critical', 'major']:
            recommendations.append({
                'category': 'Staff Deployment - URGENT',
                'priority': 'HIGH',
                'action': 'Activate Emergency Staffing Protocol',
                'details': [
                    f'Deploy {doctors} doctors (call in off-duty staff)',
                    f'Deploy {nurses} nurses (activate on-call roster)',
                    f'Deploy {support} support staff',
                    'Cancel all non-emergency leaves',
                    'Consider requesting staff from neighboring facilities'
                ]
            })
        elif surge_level == 'moderate':
            recommendations.append({
                'category': 'Staff Deployment',
                'priority': 'MEDIUM',
                'action': 'Increase Staff Allocation',
                'details': [
                    f'Schedule {doctors} doctors for extended shifts',
                    f'Assign {nurses} nurses to surge wards',
                    f'Add {support} support staff',
                    'Alert on-call staff for potential activation'
                ]
            })
        elif surge_level == 'minor':
            recommendations.append({
                'category': 'Staff Deployment',
                'priority': 'LOW',
                'action': 'Optimize Staff Scheduling',
                'details': [
                    f'Ensure {doctors} doctors available',
                    f'Pre-schedule {nurses} nurses',
                    'Monitor staffing levels closely'
                ]
            })
        
        return recommendations
    
    def generate_supply_orders(self, resource_forecast, baseline_resources, surge_level):
        """Generate supply pre-ordering recommendations"""
        recommendations = []
        
        # Calculate additional supplies needed
        additional_ppe = resource_forecast['ppe_kits'] - baseline_resources['ppe_kits']
        additional_oxygen = resource_forecast['oxygen_liters'] - baseline_resources['oxygen_liters']
        additional_iv = resource_forecast['iv_fluids_ml'] - baseline_resources['iv_fluids_ml']
        additional_meds = resource_forecast['medications_units'] - baseline_resources['medications_units']
        
        if surge_level in ['critical', 'major', 'moderate']:
            priority = 'HIGH' if surge_level in ['critical', 'major'] else 'MEDIUM'
            
            supply_orders = []
            if additional_ppe > 0:
                supply_orders.append(f'PPE Kits: Order {additional_ppe} units immediately')
            if additional_oxygen > 0:
                supply_orders.append(f'Medical Oxygen: Order {additional_oxygen} liters')
            if additional_iv > 0:
                supply_orders.append(f'IV Fluids: Order {additional_iv / 1000:.1f} liters')
            if additional_meds > 0:
                supply_orders.append(f'Emergency Medications: Order {additional_meds} units')
            
            # Add buffer stock (20% extra for critical, 10% for others)
            buffer_pct = 20 if surge_level == 'critical' else 10
            supply_orders.append(f'Include {buffer_pct}% buffer stock for all items')
            
            recommendations.append({
                'category': 'Supply Pre-ordering',
                'priority': priority,
                'action': 'Execute Emergency Procurement',
                'details': supply_orders
            })
        
        return recommendations
    
    def generate_public_advisory(self, surge_reasons, surge_level, predicted_date):
        """Generate public health advisory"""
        recommendations = []
        
        if surge_level in ['critical', 'major']:
            advisory_type = 'URGENT PUBLIC HEALTH ADVISORY'
            priority = 'HIGH'
        elif surge_level == 'moderate':
            advisory_type = 'Public Health Advisory'
            priority = 'MEDIUM'
        else:
            return []  # No advisory for minor surges
        
        # Generate advisory based on surge reasons
        advisory_points = []
        
        if 'Severe AQI' in surge_reasons or 'Very Poor AQI' in surge_reasons:
            advisory_points.extend([
                'Air quality alert: Minimize outdoor activities',
                'Use N95 masks when going outside',
                'Keep windows closed; use air purifiers',
                'Vulnerable groups (children, elderly) stay indoors'
            ])
        
        if 'Heavy Rainfall' in surge_reasons:
            advisory_points.extend([
                'Avoid waterlogged areas to prevent waterborne diseases',
                'Boil drinking water before consumption',
                'Stay indoors during heavy rainfall',
                'Report any flooding or drainage issues'
            ])
        
        if 'Extreme Heat' in surge_reasons:
            advisory_points.extend([
                'Stay hydrated: Drink plenty of water',
                'Avoid outdoor activities during peak hours (12 PM - 4 PM)',
                'Use cooling measures and stay in shade',
                'Watch for heat exhaustion symptoms'
            ])
        
        if 'Diwali Pollution' in surge_reasons or 'Festival Crowd' in surge_reasons:
            advisory_points.extend([
                'Exercise caution during festival celebrations',
                'Use protective gear (masks, safety equipment)',
                'Keep emergency contacts ready',
                'Avoid overcrowded areas if possible'
            ])
        
        # Hospital capacity management
        advisory_points.extend([
            f'Expected surge starting {predicted_date.strftime("%B %d")}',
            'Visit hospital only for emergencies',
            'Use telemedicine for non-urgent consultations',
            'Keep emergency medications stocked at home'
        ])
        
        recommendations.append({
            'category': advisory_type,
            'priority': priority,
            'action': 'Issue Public Health Advisory',
            'details': advisory_points,
            'distribution_channels': [
                'Social media (Twitter, Facebook, Instagram)',
                'Local news channels and radio',
                'Municipal corporation website',
                'SMS alerts to registered citizens',
                'Community health workers'
            ]
        })
        
        return recommendations
    
    def generate_bed_management(self, resource_forecast, surge_level):
        """Generate bed and facility management recommendations"""
        recommendations = []
        
        beds_needed = resource_forecast['beds_needed']
        
        if surge_level == 'critical':
            recommendations.append({
                'category': 'Facility Management - CRITICAL',
                'priority': 'HIGH',
                'action': 'Activate Emergency Bed Expansion',
                'details': [
                    f'Prepare {beds_needed} beds total',
                    'Convert general wards to surge capacity',
                    'Set up temporary treatment areas',
                    'Expedite patient discharges where safe',
                    'Coordinate with nearby hospitals for overflow',
                    'Consider setting up field hospitals if needed'
                ]
            })
        elif surge_level == 'major':
            recommendations.append({
                'category': 'Facility Management',
                'priority': 'HIGH',
                'action': 'Expand Bed Capacity',
                'details': [
                    f'Ensure {beds_needed} beds available',
                    'Add beds to existing wards',
                    'Defer elective procedures',
                    'Accelerate discharge planning'
                ]
            })
        
        return recommendations
    
    def generate_comprehensive_recommendations(self, surge_prediction, resource_forecast,
                                               baseline_resources, surge_reasons,
                                               prediction_date):
        """Generate comprehensive set of recommendations"""
        
        surge_multiplier = surge_prediction
        surge_level = self._classify_surge_level(surge_multiplier)
        
        all_recommendations = []
        
        # Skip if no surge expected
        if surge_level == 'normal':
            return {
                'surge_level': 'normal',
                'message': 'No surge expected. Normal operations recommended.',
                'recommendations': []
            }
        
        # Generate all recommendation types
        all_recommendations.extend(
            self.generate_staff_deployment(resource_forecast, surge_level)
        )
        all_recommendations.extend(
            self.generate_supply_orders(resource_forecast, baseline_resources, surge_level)
        )
        all_recommendations.extend(
            self.generate_public_advisory(surge_reasons, surge_level, prediction_date)
        )
        all_recommendations.extend(
            self.generate_bed_management(resource_forecast, surge_level)
        )
        
        return {
            'surge_level': surge_level,
            'surge_multiplier': surge_multiplier,
            'prediction_date': prediction_date,
            'recommendations': all_recommendations,
            'total_actions': len(all_recommendations),
            'high_priority_actions': len([r for r in all_recommendations if r['priority'] == 'HIGH'])
        }


if __name__ == "__main__":
    # Example usage
    engine = RecommendationEngine()
    
    # Simulated forecast
    resource_forecast = {
        'doctors_needed': 25,
        'nurses_needed': 75,
        'support_staff_needed': 40,
        'ppe_kits': 600,
        'oxygen_liters': 3000,
        'iv_fluids_ml': 150000,
        'medications_units': 1500,
        'beds_needed': 215
    }
    
    baseline_resources = {
        'doctors_needed': 10,
        'nurses_needed': 30,
        'support_staff_needed': 15,
        'ppe_kits': 300,
        'oxygen_liters': 1500,
        'iv_fluids_ml': 75000,
        'medications_units': 750,
        'beds_needed': 107
    }
    
    surge_reasons = ['Diwali Pollution', 'Severe AQI']
    prediction_date = datetime.now() + timedelta(days=3)
    
    result = engine.generate_comprehensive_recommendations(
        surge_prediction=2.0,
        resource_forecast=resource_forecast,
        baseline_resources=baseline_resources,
        surge_reasons=surge_reasons,
        prediction_date=prediction_date
    )
    
    print("=" * 70)
    print("RECOMMENDATION ENGINE OUTPUT")
    print("=" * 70)
    print(f"\nSurge Level: {result['surge_level'].upper()}")
    print(f"Surge Multiplier: {result['surge_multiplier']}x")
    print(f"Total Actions: {result['total_actions']}")
    print(f"High Priority Actions: {result['high_priority_actions']}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. {rec['category']} [{rec['priority']} PRIORITY]")
        print(f"   Action: {rec['action']}")
        print(f"   Details:")
        for detail in rec['details']:
            print(f"     • {detail}")
