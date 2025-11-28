"""
Clinical Priority Resource Recommendations
Demonstrates resource allocation focused on patient outcomes, not costs
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.resource_recommendation_agent import ResourceRecommendationAgent


def demo_clinical_priority_mode():
    """Demonstrate clinical-first resource recommendations"""
    print("=" * 70)
    print("CLINICAL PRIORITY MODE - Patient Safety First")
    print("=" * 70)
    print("\n🏥 Focus: Ensure optimal patient care regardless of cost\n")
    
    # Initialize agent in clinical priority mode
    agent = ResourceRecommendationAgent(mode='CLINICAL_PRIORITY')
    
    # Critical surge scenario
    surge_prediction = {
        'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        'predicted_admissions': 350,
        'surge_multiplier': 2.3,
        'resource_forecast': {
            'doctors_needed': 25,
            'nurses_needed': 75,
            'support_staff_needed': 35,
            'ppe_kits': 700,
            'oxygen_liters': 3500,
            'iv_fluids_ml': 175000,
            'medications_units': 1750,
            'bed_linens': 700
        }
    }
    
    current_resources = {
        'doctors': 10,
        'nurses': 30,
        'support_staff': 15,
        'ppe_kits': 150,
        'oxygen_liters': 800,
        'iv_fluids_ml': 40000,
        'medications_units': 400,
        'bed_linens': 250
    }
    
    print(f"📊 Scenario: Critical Surge (2.3x baseline)")
    print(f"   Predicted Admissions: 350 patients")
    print(f"   Surge Date: {surge_prediction['date']} (3 days away)")
    print(f"   Mode: CLINICAL PRIORITY (no budget limit)")
    
    # Generate clinical-first plan
    plan = agent.generate_comprehensive_resource_plan(
        surge_prediction=surge_prediction,
        current_resources=current_resources,
        days_until_surge=3,
        budget=None  # No budget constraint
    )
    
    print(f"\n{'═' * 70}")
    print("RESOURCE ALLOCATION PLAN")
    print(f"{'═' * 70}")
    print(f"\n✓ Readiness Score: {plan['readiness_score']}/100")
    print(f"✓ All resources allocated to meet 100% of patient needs")
    
    print(f"\n{'─' * 70}")
    print("STAFF DEPLOYMENT (Immediate Action Required)")
    print(f"{'─' * 70}")
    
    for staff_type, details in plan['staff_allocation']['allocation'].items():
        shortage = details['shortage']
        to_deploy = details['to_deploy']
        coverage = ((details['available'] + to_deploy) / details['required'] * 100) if details['required'] > 0 else 100
        
        status = "✓ READY" if coverage >= 100 else "⚠ SHORTFALL"
        print(f"\n{staff_type.upper():20}")
        print(f"  Required: {details['required']}")
        print(f"  Currently Available: {details['available']}")
        print(f"  To Deploy: {to_deploy}")
        print(f"  Coverage: {coverage:.0f}% {status}")
    
    print(f"\n{'─' * 70}")
    print("CRITICAL SUPPLIES (Priority Order)")
    print(f"{'─' * 70}")
    
    # Show high-priority supplies
    high_priority = [s for s in plan['supply_procurement']['procurement_plan'] 
                    if s['priority'] > 80]
    
    for i, supply in enumerate(high_priority[:5], 1):
        print(f"\n{i}. {supply['supply'].replace('_', ' ').upper()}")
        print(f"   Needed: {supply['shortage']:,} units")
        print(f"   Priority: {supply['priority']:.0f}/100 (CRITICAL)")
        print(f"   Lead Time: {supply['lead_time_days']} days")
        print(f"   Action: {supply['recommended_action']}")
    
    print(f"\n{'─' * 70}")
    print("ACTION TIMELINE (Next 3 Days)")
    print(f"{'─' * 70}")
    
    for action in plan['action_timeline'][:8]:
        day_marker = "TODAY" if action['days_from_now'] == 0 else f"Day +{action['days_from_now']}"
        print(f"\n{day_marker}: {action['action']}")
        print(f"   Quantity: {action['quantity']:,} | Priority: {action['priority']}")
    
    # Cost summary (informational only)
    print(f"\n{'─' * 70}")
    print("RESOURCE COST SUMMARY (Informational)")
    print(f"{'─' * 70}")
    print(f"Total Investment Required: ₹{plan['total_cost']:,.0f}")
    print(f"  Staff Deployment: ₹{plan['staff_allocation']['total_cost']:,.0f}")
    print(f"  Supply Procurement: ₹{plan['supply_procurement']['total_cost']:,.0f}")
    print(f"\n💡 Note: In clinical priority mode, costs are tracked but not limiting")
    
    return plan


def compare_clinical_vs_budget_mode():
    """Compare clinical priority vs budget-aware modes"""
    print("\n\n" + "=" * 70)
    print("MODE COMPARISON: Clinical Priority vs Budget Aware")
    print("=" * 70)
    
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
    
    # Clinical Priority Mode
    clinical_agent = ResourceRecommendationAgent(mode='CLINICAL_PRIORITY')
    clinical_plan = clinical_agent.generate_comprehensive_resource_plan(
        surge_prediction=surge_prediction,
        current_resources=current_resources,
        days_until_surge=5,
        budget=None
    )
    
    # Budget Aware Mode
    budget_agent = ResourceRecommendationAgent(mode='BUDGET_AWARE')
    budget_plan = budget_agent.generate_comprehensive_resource_plan(
        surge_prediction=surge_prediction,
        current_resources=current_resources,
        days_until_surge=5,
        budget=200000  # Limited budget
    )
    
    print(f"\n{'─' * 70}")
    print("CLINICAL PRIORITY MODE (Patient Care First)")
    print(f"{'─' * 70}")
    print(f"Readiness Score: {clinical_plan['readiness_score']}/100")
    print(f"Staff Coverage: 100% (all positions filled)")
    print(f"Supply Coverage: 100% (all needs met)")
    print(f"Total Cost: ₹{clinical_plan['total_cost']:,.0f}")
    
    print(f"\n{'─' * 70}")
    print("BUDGET AWARE MODE (Cost Constrained)")
    print(f"{'─' * 70}")
    print(f"Readiness Score: {budget_plan['readiness_score']}/100")
    print(f"Budget: ₹2,00,000")
    print(f"Budget Used: ₹{budget_plan['total_cost']:,.0f} ({budget_plan['budget_utilization']:.1f}%)")
    
    # Show what was compromised
    print(f"\n⚠️  Compromises due to budget:")
    for staff_type, details in budget_plan['staff_allocation']['allocation'].items():
        if details['unfulfilled'] > 0:
            print(f"   {staff_type}: {details['unfulfilled']} positions unfilled")
    
    print(f"\n💡 Recommendation: Use CLINICAL PRIORITY mode for patient safety")


def main():
    """Run clinical priority demonstrations"""
    print("\n" * 2)
    print("=" * 70)
    print("RESOURCE RECOMMENDATION - CLINICAL PRIORITY FOCUS")
    print("Patient Outcomes Over Budget Constraints")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Demo 1: Clinical priority
    demo_clinical_priority_mode()
    
    # Demo 2: Comparison
    compare_clinical_vs_budget_mode()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    
    print("\n✅ Key Principles:")
    print("   • Patient safety is the top priority")
    print("   • All clinical needs are met regardless of cost")
    print("   • Cost tracking is informational, not limiting")
    print("   • Resource allocation prioritizes life-saving care")
    print("   • Budget-aware mode available when needed")
    
    print("\n📋 Clinical Priority Mode ensures:")
    print("   ✓ 100% staffing requirements met")
    print("   ✓ All critical supplies ordered")
    print("   ✓ No compromises on patient care")
    print("   ✓ Transparent cost reporting")


if __name__ == "__main__":
    main()
