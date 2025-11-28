"""
Enhanced demonstration with Resource Recommendation Agent
Shows intelligent resource optimization with budget constraints
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.resource_recommendation_agent import ResourceRecommendationAgent


def demo_resource_agent_single_hospital():
    """Demonstrate resource agent for single hospital surge"""
    print("\n" + "=" * 70)
    print("RESOURCE RECOMMENDATION AGENT - SINGLE HOSPITAL OPTIMIZATION")
    print("=" * 70)
    
    agent = ResourceRecommendationAgent()
    
    # Diwali surge scenario
    surge_prediction = {
        'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'predicted_admissions': 300,
        'surge_multiplier': 2.0,
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
        'doctors': 12,
        'nurses': 35,
        'support_staff': 18,
        'ppe_kits': 200,
        'oxygen_liters': 1000,
        'iv_fluids_ml': 50000,
        'medications_units': 500,
        'bed_linens': 300
    }
    
    print(f"\nScenario: Diwali Pollution Surge")
    print(f"Predicted Admissions: {surge_prediction['predicted_admissions']}")
    print(f"Surge Date: {surge_prediction['date']} (5 days away)")
    print(f"Budget: ₹5,00,000")
    
    # Generate optimized plan
    plan = agent.generate_comprehensive_resource_plan(
        surge_prediction=surge_prediction,
        current_resources=current_resources,
        days_until_surge=5,
        budget=500000
    )
    
    print(f"\n{'═' * 70}")
    print(f"OPTIMIZATION RESULTS")
    print(f"{'═' * 70}")
    print(f"✓ Readiness Score: {plan['readiness_score']}/100")
    print(f"✓ Total Cost: ₹{plan['total_cost']:,.0f}")
    print(f"✓ Budget Utilization: {plan['budget_utilization']:.1f}%")
    print(f"✓ Budget Remaining: ₹{500000 - plan['total_cost']:,.0f}")
    
    print(f"\n{'─' * 70}")
    print("TOP PRIORITY ITEMS (Timeline)")
    print(f"{'─' * 70}")
    
    urgent_actions = [a for a in plan['action_timeline'] if a.get('priority') in ['URGENT', 'HIGH']]
    for i, action in enumerate(urgent_actions[:5], 1):
        print(f"\n{i}. Day {action['days_from_now']}: {action['date']}")
        print(f"   [{action['priority']}] {action['action']}")
        print(f"   Quantity: {action['quantity']:,} units | Cost: ₹{action['cost']:,}")
    
    print(f"\n{'─' * 70}")
    print("STAFF DEPLOYMENT SUMMARY")
    print(f"{'─' * 70}")
    
    for staff_type, details in plan['staff_allocation']['allocation'].items():
        coverage = ((details['available'] + details['to_deploy']) / details['required'] * 100) if details['required'] > 0 else 100
        print(f"{staff_type.capitalize():15} → {details['available'] + details['to_deploy']}/{details['required']} ({coverage:.0f}% coverage)")
    
    return plan


def demo_resource_agent_multi_hospital():
    """Demonstrate multi-hospital resource pooling"""
    print("\n" + "=" * 70)
    print("RESOURCE RECOMMENDATION AGENT - MULTI-HOSPITAL POOLING")
    print("=" * 70)
    
    agent = ResourceRecommendationAgent()
    
    # Multiple hospitals with different surge levels
    hospitals_data = [
        {
            'hospital_id': 1,
            'name': 'Hospital A (Critical Surge)',
            'required_resources': {
                'doctors': 25, 'nurses': 75, 'ppe_kits': 800,
                'oxygen_liters': 4000, 'medications_units': 2000
            },
            'available_resources': {
                'doctors': 10, 'nurses': 30, 'ppe_kits': 200,
                'oxygen_liters': 1000, 'medications_units': 500
            }
        },
        {
            'hospital_id': 2,
            'name': 'Hospital B (Normal Operations)',
            'required_resources': {
                'doctors': 10, 'nurses': 30, 'ppe_kits': 200,
                'oxygen_liters': 1000, 'medications_units': 500
            },
            'available_resources': {
                'doctors': 15, 'nurses': 45, 'ppe_kits': 600,
                'oxygen_liters': 2500, 'medications_units': 1200
            }
        },
        {
            'hospital_id': 3,
            'name': 'Hospital C (Minor Surge)',
            'required_resources': {
                'doctors': 15, 'nurses': 45, 'ppe_kits': 400,
                'oxygen_liters': 2000, 'medications_units': 1000
            },
            'available_resources': {
                'doctors': 12, 'nurses': 35, 'ppe_kits': 300,
                'oxygen_liters': 1500, 'medications_units': 700
            }
        }
    ]
    
    print(f"\nAnalyzing {len(hospitals_data)} hospitals in Mumbai network...")
    
    network_analysis = agent.generate_multi_hospital_recommendations(hospitals_data)
    
    print(f"\n{'═' * 70}")
    print(f"NETWORK-WIDE ANALYSIS")
    print(f"{'═' * 70}")
    
    print(f"\nTotal Network Requirements:")
    for resource, amount in list(network_analysis['total_requirements'].items())[:5]:
        required = network_analysis['total_requirements'][resource]
        available = network_analysis['total_available'][resource]
        gap = required - available
        print(f"  {resource:20} : Need {required:,} | Have {available:,} | Gap {gap:,}")
    
    print(f"\n{'─' * 70}")
    print(f"RESOURCE POOLING OPPORTUNITIES")
    print(f"{'─' * 70}")
    
    if network_analysis['pooling_opportunities']:
        print(f"\nFound {len(network_analysis['pooling_opportunities'])} pooling opportunities!")
        print(f"💰 Estimated Savings: ₹{network_analysis['cost_savings_from_pooling']:,.0f}")
        
        for i, opportunity in enumerate(network_analysis['pooling_opportunities'][:3], 1):
            print(f"\n{i}. {opportunity['resource'].upper()}")
            print(f"   Surplus: {opportunity['total_surplus']:,} units")
            print(f"   Shortage: {opportunity['total_shortage']:,} units")
            print(f"   Can transfer: {min(opportunity['total_surplus'], opportunity['total_shortage']):,} units")
            
            if opportunity['surplus_hospitals']:
                surplus_h = opportunity['surplus_hospitals'][0]
                shortage_h = opportunity['shortage_hospitals'][0]
                print(f"   → Transfer from Hospital {surplus_h[0]} to Hospital {shortage_h[0]}")
    
    print(f"\n{'─' * 70}")
    print(f"NETWORK PROCUREMENT NEEDED")
    print(f"{'─' * 70}")
    
    if network_analysis['network_procurement_needed']:
        total_procurement_cost = 0
        for resource, amount in list(network_analysis['network_procurement_needed'].items())[:5]:
            if resource in agent.supply_costs:
                cost = amount * agent.supply_costs[resource]
                total_procurement_cost += cost
                print(f"  {resource:20} : {amount:,} units @ ₹{cost:,.0f}")
        
        print(f"\n  Total Network Procurement Cost: ₹{total_procurement_cost:,.0f}")
        print(f"  After Resource Pooling Savings: ₹{total_procurement_cost - network_analysis['cost_savings_from_pooling']:,.0f}")
    
    return network_analysis


def demo_budget_constraint_scenarios():
    """Compare different budget scenarios"""
    print("\n" + "=" * 70)
    print("BUDGET CONSTRAINT ANALYSIS")
    print("=" * 70)
    
    agent = ResourceRecommendationAgent()
    
    surge_prediction = {
        'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'predicted_admissions': 300,
        'surge_multiplier': 2.0,
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
    
    budgets = {
        'Limited': 200000,
        'Moderate': 500000,
        'Unlimited': None
    }
    
    print(f"\nComparing resource allocation under different budgets...\n")
    
    for scenario, budget in budgets.items():
        plan = agent.generate_comprehensive_resource_plan(
            surge_prediction=surge_prediction,
            current_resources=current_resources,
            days_until_surge=5,
            budget=budget
        )
        
        budget_str = f"₹{budget:,}" if budget else "Unlimited"
        print(f"{scenario} Budget ({budget_str}):")
        print(f"  Readiness Score: {plan['readiness_score']}/100")
        print(f"  Total Cost: ₹{plan['total_cost']:,.0f}")
        
        if budget:
            print(f"  Budget Utilization: {plan['budget_utilization']:.1f}%")
        print()


def main():
    """Run all resource agent demonstrations"""
    print("=" * 70)
    print("ECO-HEALTH AI - RESOURCE RECOMMENDATION AGENT DEMONSTRATIONS")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Demo 1: Single hospital optimization
    demo_resource_agent_single_hospital()
    
    # Demo 2: Multi-hospital pooling
    demo_resource_agent_multi_hospital()
    
    # Demo 3: Budget constraints
    demo_budget_constraint_scenarios()
    
    print("\n" + "=" * 70)
    print("RESOURCE AGENT DEMONSTRATIONS COMPLETE")
    print("=" * 70)
    
    print("\nKey Features Demonstrated:")
    print("✓ Constraint-based resource optimization")
    print("✓ Budget-aware allocation (₹2L to ₹5L scenarios)")
    print("✓ Priority scoring for procurement decisions")
    print("✓ Lead time consideration in action timeline")
    print("✓ Multi-hospital resource pooling (up to 40% cost savings)")
    print("✓ Automated readiness scoring")
    print("✓ Day-by-day action plans")


if __name__ == "__main__":
    main()
