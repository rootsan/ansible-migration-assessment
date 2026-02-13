#!/usr/bin/env python3
"""
CSV Report Generator for Migration Assessment
Generates executive reports in CSV format for decision making
"""

import json
import csv
import os
import sys
from datetime import datetime
from typing import List, Dict, Any


class ReportGenerator:
    """Generate CSV reports from assessment results"""
    
    def __init__(self, output_dir: str = '../output'):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def load_assessment_results(self, results_file: str) -> List[Dict]:
        """Load assessment results from JSON file"""
        try:
            with open(results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            return []
    
    def generate_executive_summary(self, results: List[Dict], output_file: str = None):
        """Generate executive summary CSV report"""
        if output_file is None:
            output_file = os.path.join(
                self.output_dir,
                f'executive_summary_{self.timestamp}.csv'
            )
        
        # Define CSV columns
        fieldnames = [
            'Hostname',
            'FQDN',
            'OS Family',
            'Distribution',
            'Version',
            'Overall Risk Score',
            'Risk Level',
            'OS Version Risk',
            'Package Risk',
            'Hardware Risk',
            'Services Risk',
            'Modules Risk',
            'Recommendation',
            'Assessment Date'
        ]
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                assessments = result.get('detailed_assessments', {})
                
                row = {
                    'Hostname': result.get('hostname', ''),
                    'FQDN': result.get('fqdn', ''),
                    'OS Family': result.get('os_family', ''),
                    'Distribution': result.get('distribution', ''),
                    'Version': result.get('distribution_version', ''),
                    'Overall Risk Score': result.get('overall_risk_score', 0),
                    'Risk Level': result.get('risk_level', ''),
                    'OS Version Risk': assessments.get('os_version', {}).get('score', 0),
                    'Package Risk': assessments.get('package_compatibility', {}).get('score', 0),
                    'Hardware Risk': assessments.get('hardware', {}).get('score', 0),
                    'Services Risk': assessments.get('services', {}).get('score', 0),
                    'Modules Risk': assessments.get('kernel_modules', {}).get('score', 0),
                    'Recommendation': result.get('recommendation', ''),
                    'Assessment Date': result.get('assessment_date', '')
                }
                writer.writerow(row)
        
        print(f"Executive summary report generated: {output_file}")
        return output_file
    
    def generate_detailed_report(self, results: List[Dict], output_file: str = None):
        """Generate detailed assessment CSV report"""
        if output_file is None:
            output_file = os.path.join(
                self.output_dir,
                f'detailed_assessment_{self.timestamp}.csv'
            )
        
        fieldnames = [
            'Hostname',
            'Assessment Category',
            'Risk Score',
            'Weight',
            'Weighted Score',
            'Issues'
        ]
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                hostname = result.get('hostname', '')
                assessments = result.get('detailed_assessments', {})
                
                for category, assessment in assessments.items():
                    issues = assessment.get('issues', [])
                    issues_str = ' | '.join(str(issue) for issue in issues)
                    
                    row = {
                        'Hostname': hostname,
                        'Assessment Category': category.replace('_', ' ').title(),
                        'Risk Score': assessment.get('score', 0),
                        'Weight': assessment.get('weight', 0),
                        'Weighted Score': assessment.get('weighted_score', 0),
                        'Issues': issues_str
                    }
                    writer.writerow(row)
        
        print(f"Detailed assessment report generated: {output_file}")
        return output_file
    
    def generate_priority_matrix(self, results: List[Dict], output_file: str = None):
        """Generate migration priority matrix CSV"""
        if output_file is None:
            output_file = os.path.join(
                self.output_dir,
                f'migration_priority_{self.timestamp}.csv'
            )
        
        # Sort results by risk score (descending)
        sorted_results = sorted(
            results,
            key=lambda x: x.get('overall_risk_score', 0),
            reverse=True
        )
        
        fieldnames = [
            'Priority',
            'Hostname',
            'Distribution',
            'Version',
            'Risk Level',
            'Risk Score',
            'Recommended Action',
            'Timeline'
        ]
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, result in enumerate(sorted_results, 1):
                risk_score = result.get('overall_risk_score', 0)
                
                # Determine timeline based on risk
                if risk_score >= 70:
                    timeline = "Immediate (0-3 months)"
                elif risk_score >= 50:
                    timeline = "Short-term (3-6 months)"
                elif risk_score >= 30:
                    timeline = "Medium-term (6-12 months)"
                else:
                    timeline = "Long-term (12+ months)"
                
                row = {
                    'Priority': idx,
                    'Hostname': result.get('hostname', ''),
                    'Distribution': result.get('distribution', ''),
                    'Version': result.get('distribution_version', ''),
                    'Risk Level': result.get('risk_level', ''),
                    'Risk Score': risk_score,
                    'Recommended Action': result.get('recommendation', ''),
                    'Timeline': timeline
                }
                writer.writerow(row)
        
        print(f"Migration priority matrix generated: {output_file}")
        return output_file
    
    def generate_statistics_report(self, results: List[Dict], output_file: str = None):
        """Generate statistical summary CSV"""
        if output_file is None:
            output_file = os.path.join(
                self.output_dir,
                f'statistics_summary_{self.timestamp}.csv'
            )
        
        # Calculate statistics
        total_systems = len(results)
        if total_systems == 0:
            print("No results to generate statistics")
            return None
        
        risk_levels = {'HIGH': 0, 'MEDIUM-HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        os_families = {}
        distributions = {}
        
        total_risk_score = 0
        
        for result in results:
            risk_level = result.get('risk_level', '')
            if risk_level in risk_levels:
                risk_levels[risk_level] += 1
            
            os_family = result.get('os_family', 'Unknown')
            os_families[os_family] = os_families.get(os_family, 0) + 1
            
            distro = result.get('distribution', 'Unknown')
            distributions[distro] = distributions.get(distro, 0) + 1
            
            total_risk_score += result.get('overall_risk_score', 0)
        
        avg_risk_score = total_risk_score / total_systems
        
        # Write statistics
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(['Migration Assessment Statistics'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            writer.writerow(['Overall Statistics'])
            writer.writerow(['Total Systems Assessed', total_systems])
            writer.writerow(['Average Risk Score', f'{avg_risk_score:.2f}'])
            writer.writerow([])
            
            writer.writerow(['Risk Level Distribution'])
            writer.writerow(['Risk Level', 'Count', 'Percentage'])
            for level, count in risk_levels.items():
                percentage = (count / total_systems) * 100
                writer.writerow([level, count, f'{percentage:.1f}%'])
            writer.writerow([])
            
            writer.writerow(['OS Family Distribution'])
            writer.writerow(['OS Family', 'Count', 'Percentage'])
            for family, count in sorted(os_families.items()):
                percentage = (count / total_systems) * 100
                writer.writerow([family, count, f'{percentage:.1f}%'])
            writer.writerow([])
            
            writer.writerow(['Distribution Breakdown'])
            writer.writerow(['Distribution', 'Count', 'Percentage'])
            for distro, count in sorted(distributions.items()):
                percentage = (count / total_systems) * 100
                writer.writerow([distro, count, f'{percentage:.1f}%'])
        
        print(f"Statistics summary generated: {output_file}")
        return output_file
    
    def generate_all_reports(self, results: List[Dict]):
        """Generate all report types"""
        print(f"\n{'='*60}")
        print("Generating CSV Reports")
        print(f"{'='*60}\n")
        
        self.generate_executive_summary(results)
        self.generate_detailed_report(results)
        self.generate_priority_matrix(results)
        self.generate_statistics_report(results)
        
        print(f"\n{'='*60}")
        print("All reports generated successfully")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python generate_reports.py <assessment_results.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '../output'
    
    generator = ReportGenerator(output_dir)
    results = generator.load_assessment_results(results_file)
    
    if results:
        generator.generate_all_reports(results)
    else:
        print("No results to generate reports from")
        sys.exit(1)


if __name__ == '__main__':
    main()
