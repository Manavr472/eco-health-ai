"""
Resource Recommendation Agent (Cost-Free)
Pure clinical focus on resource allocation - zero cost consideration
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STAFF_RATIOS, SUPPLIES_PER_PATIENT


class ResourceRecommendationAgent:
    """
    Resource allocation agent focused purely on patient care needs
    No cost tracking - only clinical requirements
    """
    
    def __init__(self):
        self.lead_times = {
            'doctors': 0,  # Available immediately (on-call)
            'nurses': 0,
            'support_staff': 1,  # 1 day notice
            'ppe_kits': 2,  # 2 days delivery
            'oxygen_liters': 1,
            'iv_fluids_ml': 2,
            'medications_units': 3,
            'bed_linens': 1
        }
        
        self.inventory_buffer = 0.15  # 15% safety buffer
        
        # Setup Resource Agent Logger
        self.logger = logging.getLogger('resource_agent')
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if they exist
        if not self.logger.handlers:
            # File Handler
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'resource_agent.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
            self.logger.addHandler(file_handler)
    
    def log_thought(self, message: str):
        """Log the agent's reasoning process"""
        self.logger.info(f"[THOUGHT] {message}")
        
    def log_action(self, message: str):
        """Log the agent's decisions/actions"""
        self.logger.info(f"[ACTION] {message}")
    
    def calculate_resource_priority(self, resource_type: str, current_stock: int, 
                                   required: int, days_until_surge: int) -> float:
        """
        Calculate priority score based on patient impact
        Score: 0 (low) to 100 (critical)
        """
        # Base priority on shortage severity
        shortage_ratio = max(0, (required - current_stock) / required) if required > 0 else 0
        
        # Adjust for lead time urgency
        lead_time = self.lead_times.get(resource_type, 0)
        time_urgency = 1.0 if days_until_surge <= lead_time else max(0, 1 - (days_until_surge - lead_time) / 7)
        
        # Clinical criticality based on patient impact
        clinical_criticality = {
            'doctors': 1.0,          # Critical for patient care
            'nurses': 1.0,           # Critical for patient monitoring
            'oxygen_liters': 0.95,   # Life-saving
            'medications_units': 0.9, # Essential treatments
            'ppe_kits': 0.85,        # Infection control
            'iv_fluids_ml': 0.85,    # Critical supplies
            'beds_needed': 0.8,      # Patient capacity
            'support_staff': 0.75,   # Operational support
            'bed_linens': 0.6        # Important but not critical
        }.get(resource_type, 0.5)
        
        priority = 100 * shortage_ratio * time_urgency * clinical_criticality
        
        return min(100, priority)
    
    def calculate_staff_needs(self, required_staff: Dict[str, int],
                             available_staff: Dict[str, int]) -> Dict:
        """Calculate staff deployment needs"""
        allocation = {}
        
        for staff_type in ['doctors', 'nurses', 'support_staff']:
            required = required_staff.get(staff_type, 0)
            available = available_staff.get(staff_type, 0)
            shortage = max(0, required - available)
            
            allocation[staff_type] = {
                'required': required,
                'available': available,
                'to_deploy': shortage,
                'coverage': ((available + shortage) / required * 100) if required > 0 else 100
            }
        
        return allocation
    
    def calculate_supply_needs(self, required_supplies: Dict[str, int],
                              current_inventory: Dict[str, int],
                              days_until_surge: int) -> List[Dict]:
        """Calculate supply procurement needs"""
        procurement_plan = []
        
        for supply_type, required in required_supplies.items():
            current = current_inventory.get(supply_type, 0)
            
            # Calculate shortage with safety buffer
            shortage = max(0, int(required * (1 + self.inventory_buffer) - current))
            
            if shortage == 0:
                continue
            
            # Calculate priority
            priority = self.calculate_resource_priority(
                supply_type, current, required, days_until_surge
            )
            
            # Lead time check
            lead_time = self.lead_times[supply_type]
            delivery_possible = days_until_surge > lead_time
            
            procurement_plan.append({
                'supply': supply_type,
                'required': required,
                'current_stock': current,
                'to_order': shortage,
                'priority': priority,
                'lead_time_days': lead_time,
                'order_immediately': priority > 80 or not delivery_possible,
                'delivery_possible': delivery_possible
            })
        
        # Sort by priority
        procurement_plan.sort(key=lambda x: x['priority'], reverse=True)
        
        return procurement_plan
    
    def generate_multi_hospital_recommendations(self, hospitals_data: List[Dict]) -> Dict:
        """Generate recommendations for multiple hospitals with resource pooling"""
        total_requirements = {}
        total_available = {}
        
        hospitals_with_surplus = {}
        hospitals_with_shortage = {}
        
        # Analyze each hospital
        for hospital in hospitals_data:
            h_id = hospital['hospital_id']
            required = hospital['required_resources']
            available = hospital['available_resources']
            
            for resource_type in required.keys():
                req = required.get(resource_type, 0)
                avail = available.get(resource_type, 0)
                
                total_requirements[resource_type] = total_requirements.get(resource_type, 0) + req
                total_available[resource_type] = total_available.get(resource_type, 0) + avail
                
                if avail > req:
                    surplus = avail - req
                    if h_id not in hospitals_with_surplus:
                        hospitals_with_surplus[h_id] = {}
                    hospitals_with_surplus[h_id][resource_type] = surplus
                elif req > avail:
                    shortage = req - avail
                    if h_id not in hospitals_with_shortage:
                        hospitals_with_shortage[h_id] = {}
                    hospitals_with_shortage[h_id][resource_type] = shortage
        
        # Generate resource pooling recommendations
        pooling_recommendations = []
        
        for resource_type in total_requirements.keys():
            surplus_hospitals = [(h_id, surplus.get(resource_type, 0)) 
                                for h_id, surplus in hospitals_with_surplus.items() 
                                if resource_type in surplus]
            
            shortage_hospitals = [(h_id, shortage.get(resource_type, 0)) 
                                 for h_id, shortage in hospitals_with_shortage.items() 
                                 if resource_type in shortage]
            
            if surplus_hospitals and shortage_hospitals:
                transferable = min(sum(s for _, s in surplus_hospitals), 
                                 sum(s for _, s in shortage_hospitals))
                
                pooling_recommendations.append({
                    'resource': resource_type,
                    'total_surplus': sum(s for _, s in surplus_hospitals),
                    'total_shortage': sum(s for _, s in shortage_hospitals),
                    'can_transfer': transferable,
                    'surplus_hospitals': surplus_hospitals,
                    'shortage_hospitals': shortage_hospitals,
                    'recommendation': f'Transfer {transferable} units from surplus to shortage hospitals'
                })
        
        # Calculate network-level procurement needs
        network_procurement = {}
        for resource_type in total_requirements.keys():
            network_shortage = max(0, total_requirements[resource_type] - total_available[resource_type])
            if network_shortage > 0:
                network_procurement[resource_type] = network_shortage
        
        return {
            'total_requirements': total_requirements,
            'total_available': total_available,
            'network_procurement_needed': network_procurement,
            'pooling_opportunities': pooling_recommendations,
            'hospitals_with_surplus': hospitals_with_surplus,
            'hospitals_with_shortage': hospitals_with_shortage
        }
    
    def generate_comprehensive_resource_plan(self, 
                                            surge_prediction: Dict,
                                            current_resources: Dict,
                                            days_until_surge: int) -> Dict:
        """Generate complete resource allocation plan"""
        self.log_thought(f"Analyzing resource needs for surge date: {surge_prediction.get('date')} (in {days_until_surge} days)")
        
        required = surge_prediction['resource_forecast']
        available = current_resources
        
        self.log_thought(f"Current Resources: {available}")
        self.log_thought(f"Forecasted Needs: {required}")
        
        # Staff needs
        staff_plan = self.calculate_staff_needs(
            required_staff={
                'doctors': required.get('doctors_needed', 0),
                'nurses': required.get('nurses_needed', 0),
                'support_staff': required.get('support_staff_needed', 0)
            },
            available_staff={
                'doctors': available.get('doctors', 0),
                'nurses': available.get('nurses', 0),
                'support_staff': available.get('support_staff', 0)
            }
        )
        
        for staff, details in staff_plan.items():
            if details['to_deploy'] > 0:
                self.log_action(f"Staff Shortage Detected: Need {details['to_deploy']} more {staff} (Coverage: {details['coverage']:.1f}%)")
        
        # Supply needs
        supply_plan = self.calculate_supply_needs(
            required_supplies={
                'ppe_kits': required.get('ppe_kits', 0),
                'oxygen_liters': required.get('oxygen_liters', 0),
                'iv_fluids_ml': required.get('iv_fluids_ml', 0),
                'medications_units': required.get('medications_units', 0),
                'bed_linens': required.get('bed_linens', 0)
            },
            current_inventory={
                'ppe_kits': available.get('ppe_kits', 0),
                'oxygen_liters': available.get('oxygen_liters', 0),
                'iv_fluids_ml': available.get('iv_fluids_ml', 0),
                'medications_units': available.get('medications_units', 0),
                'bed_linens': available.get('bed_linens', 0)
            },
            days_until_surge=days_until_surge
        )
        
        for item in supply_plan:
            if item['to_order'] > 0:
                self.log_action(f"Supply Shortage: Order {item['to_order']} {item['supply']} (Priority: {item['priority']:.1f})")
        
        # Generate action timeline
        timeline = self._generate_action_timeline(staff_plan, supply_plan, days_until_surge)
        
        # Calculate readiness
        readiness = self._calculate_readiness_score(staff_plan, supply_plan)
        
        return {
            'surge_date': surge_prediction.get('date'),
            'days_until_surge': days_until_surge,
            'staff_allocation': staff_plan,
            'supply_procurement': supply_plan,
            'action_timeline': timeline,
            'readiness_score': readiness
        }
    
    def _generate_action_timeline(self, staff_plan: Dict, supply_plan: List[Dict], 
                                  days_until_surge: int) -> List[Dict]:
        """Generate day-by-day action timeline"""
        timeline = []
        current_date = datetime.now()
        
        # Add supply orders based on lead time
        for item in supply_plan:
            order_date = current_date + timedelta(days=max(0, days_until_surge - item['lead_time_days'] - 1))
            
            timeline.append({
                'date': order_date.strftime('%Y-%m-%d'),
                'days_from_now': (order_date - current_date).days,
                'action': f"Order {item['supply'].replace('_', ' ')}",
                'quantity': item['to_order'],
                'priority': 'URGENT' if item['priority'] > 80 else 'NORMAL',
                'category': 'Supply Procurement'
            })
        
        # Add staff deployment
        staff_deploy_date = current_date + timedelta(days=max(0, days_until_surge - 2))
        for staff_type, details in staff_plan.items():
            if details['to_deploy'] > 0:
                timeline.append({
                    'date': staff_deploy_date.strftime('%Y-%m-%d'),
                    'days_from_now': (staff_deploy_date - current_date).days,
                    'action': f"Deploy {staff_type.replace('_', ' ')}",
                    'quantity': details['to_deploy'],
                    'priority': 'HIGH',
                    'category': 'Staff Deployment'
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x['days_from_now'])
        
        return timeline
    
    def _calculate_readiness_score(self, staff_plan: Dict, supply_plan: List[Dict]) -> float:
        """Calculate overall readiness score (0-100)"""
        # Staff readiness
        staff_scores = [details['coverage'] for details in staff_plan.values()]
        avg_staff_readiness = np.mean(staff_scores) if staff_scores else 100
        
        # Supply readiness
        supply_scores = []
        for item in supply_plan:
            coverage = ((item['current_stock'] + item['to_order']) / item['required'] * 100) if item['required'] > 0 else 100
            supply_scores.append(min(100, coverage))
        
        avg_supply_readiness = np.mean(supply_scores) if supply_scores else 100
        
        # Weighted average
        overall_readiness = (avg_staff_readiness * 0.6 + avg_supply_readiness * 0.4)
        
        return round(overall_readiness, 1)


if __name__ == "__main__":
    # Demo
    print("=" * 70)
    print("RESOURCE RECOMMENDATION AGENT - CLINICAL FOCUS ONLY")
    print("=" * 70)
    
    agent = ResourceRecommendationAgent()
    
    surge_prediction = {
        'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'predicted_admissions': 300,
        'resource_forecast': {
            'doctors_needed': 20,
            'nurses_needed': 60,
            'support_staff_needed': 30,
            'ppe_kits': 600,
            'oxygen_liters': 3000,
            'iv_fluids_ml': 150000,
            'medications_units': 1500,
            'bed_linens': 600
        }
    }
    
    current_resources = {
        'doctors': 12, 'nurses': 35, 'support_staff': 18,
        'ppe_kits': 200, 'oxygen_liters': 1000,
        'iv_fluids_ml': 50000, 'medications_units': 500,
        'bed_linens': 300
    }
    
    plan = agent.generate_comprehensive_resource_plan(
        surge_prediction=surge_prediction,
        current_resources=current_resources,
        days_until_surge=5
    )
    
    print(f"\nSurge Date: {plan['surge_date']}")
    print(f"Readiness Score: {plan['readiness_score']}/100")
    
    print(f"\n{'─' * 70}")
    print("STAFF NEEDS")
    print(f"{'─' * 70}")
    for staff_type, details in plan['staff_allocation'].items():
        print(f"{staff_type:15} → Need {details['to_deploy']:2} more ({details['coverage']:.0f}% coverage)")
    
    print(f"\n{'─' * 70}")
    print("SUPPLY NEEDS (Top 5)")
    print(f"{'─' * 70}")
    for item in plan['supply_procurement'][:5]:
        print(f"{item['supply']:20} → Order {item['to_order']:,} units (Priority: {item['priority']:.0f})")
