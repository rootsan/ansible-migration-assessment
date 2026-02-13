#!/usr/bin/env python3
"""
Master Migration Assessment Orchestrator
Coordinates assessment and report generation
"""

import sys
import os
import json

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from assess_migration import MigrationAssessment
from generate_reports import ReportGenerator


def main():
    """Main orchestration function"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Migration Assessment Tool - Legacy to RHEL 8/9             ║
    ║   Evaluación de Viabilidad de Migración                      ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Get data directory
    data_dir = sys.argv[1] if len(sys.argv) > 1 else '../output'
    
    if not os.path.exists(data_dir):
        print(f"Creating output directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Step 1: Run assessment
    print("\n[Step 1/3] Running Migration Risk Assessment...")
    print("-" * 60)
    
    assessment = MigrationAssessment(data_dir)
    assessment.run_assessment()
    
    if not assessment.assessment_results:
        print("\nError: No assessment results generated")
        print("Please run the Ansible playbook first to gather system information")
        sys.exit(1)
    
    # Step 2: Save assessment results
    print("\n[Step 2/3] Saving Assessment Results...")
    print("-" * 60)
    
    results_file = os.path.join(data_dir, 'assessment_results.json')
    with open(results_file, 'w') as f:
        json.dump(assessment.assessment_results, f, indent=2)
    print(f"Results saved to: {results_file}")
    
    # Step 3: Generate CSV reports
    print("\n[Step 3/3] Generating CSV Reports...")
    print("-" * 60)
    
    generator = ReportGenerator(data_dir)
    generator.generate_all_reports(assessment.assessment_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("ASSESSMENT SUMMARY")
    print("=" * 60)
    
    total_systems = len(assessment.assessment_results)
    high_risk = sum(1 for r in assessment.assessment_results if r['risk_level'] == 'HIGH')
    medium_high = sum(1 for r in assessment.assessment_results if r['risk_level'] == 'MEDIUM-HIGH')
    medium = sum(1 for r in assessment.assessment_results if r['risk_level'] == 'MEDIUM')
    low = sum(1 for r in assessment.assessment_results if r['risk_level'] == 'LOW')
    
    print(f"\nTotal Systems Assessed: {total_systems}")
    print(f"  - HIGH Risk:        {high_risk}")
    print(f"  - MEDIUM-HIGH Risk: {medium_high}")
    print(f"  - MEDIUM Risk:      {medium}")
    print(f"  - LOW Risk:         {low}")
    
    avg_score = sum(r['overall_risk_score'] for r in assessment.assessment_results) / total_systems
    print(f"\nAverage Risk Score: {avg_score:.2f}/100")
    
    print("\nNext Steps:")
    print("1. Review the generated CSV reports in the output directory")
    print("2. Prioritize systems based on the migration_priority_*.csv file")
    print("3. Plan migration timeline based on risk levels")
    print("4. Review detailed assessments for specific concerns")
    
    print("\n" + "=" * 60)
    print("Assessment Complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
