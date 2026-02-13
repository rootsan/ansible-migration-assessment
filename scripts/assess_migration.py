#!/usr/bin/env python3
"""
Migration Risk Assessment Script
Analyzes system information and calculates migration risk scores
"""

import json
import os
import sys
from typing import Dict, List, Any
from datetime import datetime


class MigrationAssessment:
    """Main class for assessing migration risk"""
    
    # Risk weights
    WEIGHTS = {
        'os_version': 30,
        'package_compatibility': 25,
        'hardware': 20,
        'services': 15,
        'kernel_modules': 10
    }
    
    # Known problematic packages
    PROBLEMATIC_PACKAGES = [
        'python2', 'python-', 'python2.7',
        'mysql-server-5.5', 'mysql-server-5.6',
        'postgresql-9', 'php5', 'php-5',
        'openssl-1.0', 'iptables'
    ]
    
    # Known problematic services
    PROBLEMATIC_SERVICES = [
        'network.service',  # Deprecated in favor of NetworkManager
        'iptables.service',  # Replaced by firewalld/nftables
    ]
    
    def __init__(self, data_dir: str = '../output'):
        self.data_dir = data_dir
        self.systems = []
        self.assessment_results = []
    
    def load_system_data(self):
        """Load all system information JSON files"""
        if not os.path.exists(self.data_dir):
            print(f"Error: Data directory {self.data_dir} does not exist")
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('_system_info.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        self.systems.append(data)
                        print(f"Loaded: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def normalize_os_family(self, os_family: str, distribution: str) -> str:
        """Normalize OS family naming"""
        if os_family in ['RedHat', 'Fedora']:
            return 'RedHat'
        elif os_family in ['Debian', 'Ubuntu']:
            return 'Debian'
        return os_family
    
    def normalize_package_name(self, package_line: str, os_family: str) -> Dict[str, str]:
        """Normalize package information across different OS families"""
        if os_family == 'RedHat':
            # Format: name|version|release|arch
            parts = package_line.split('|')
            if len(parts) >= 3:
                return {
                    'name': parts[0],
                    'version': f"{parts[1]}-{parts[2]}",
                    'arch': parts[3] if len(parts) > 3 else 'unknown'
                }
        elif os_family == 'Debian':
            # Format: name|version|arch
            parts = package_line.split('|')
            if len(parts) >= 2:
                return {
                    'name': parts[0],
                    'version': parts[1],
                    'arch': parts[2] if len(parts) > 2 else 'unknown'
                }
        return {'name': package_line, 'version': 'unknown', 'arch': 'unknown'}
    
    def assess_os_version_risk(self, system: Dict) -> Dict[str, Any]:
        """Assess risk based on OS version"""
        distribution = system.get('distribution', '')
        version = system.get('distribution_version', '')
        major_version = system.get('distribution_major_version', '')
        
        risk_score = 0
        issues = []
        
        # CentOS 7 or older - High risk
        if distribution == 'CentOS' and major_version in ['6', '7']:
            risk_score = 90
            issues.append(f"CentOS {major_version} is EOL or near EOL - High migration priority")
        # Ubuntu old versions
        elif distribution == 'Ubuntu' and major_version in ['14', '16', '18']:
            risk_score = 80
            issues.append(f"Ubuntu {version} is EOL or near EOL")
        # RHEL 6 or 7
        elif distribution in ['RedHat', 'Red Hat Enterprise Linux'] and major_version in ['6', '7']:
            risk_score = 70
            issues.append(f"RHEL {major_version} migration recommended")
        # Debian old versions
        elif distribution == 'Debian' and int(major_version) < 10:
            risk_score = 75
            issues.append(f"Debian {major_version} is outdated")
        else:
            risk_score = 20
            issues.append("OS version is relatively current")
        
        return {
            'score': risk_score,
            'weight': self.WEIGHTS['os_version'],
            'weighted_score': (risk_score * self.WEIGHTS['os_version']) / 100,
            'issues': issues
        }
    
    def assess_package_compatibility(self, system: Dict) -> Dict[str, Any]:
        """Assess package compatibility risks"""
        packages = system.get('packages', [])
        os_family = self.normalize_os_family(
            system.get('os_family', ''),
            system.get('distribution', '')
        )
        
        risk_score = 0
        issues = []
        problematic_found = []
        
        for pkg_line in packages:
            pkg = self.normalize_package_name(pkg_line, os_family)
            pkg_name = pkg['name'].lower()
            
            for problematic in self.PROBLEMATIC_PACKAGES:
                if problematic in pkg_name:
                    problematic_found.append(f"{pkg['name']} ({pkg['version']})")
        
        if problematic_found:
            risk_score = min(100, 40 + len(problematic_found) * 10)
            issues.append(f"Found {len(problematic_found)} potentially problematic packages")
            issues.extend(problematic_found[:5])  # Show first 5
        else:
            risk_score = 20
            issues.append("No major package compatibility concerns detected")
        
        return {
            'score': risk_score,
            'weight': self.WEIGHTS['package_compatibility'],
            'weighted_score': (risk_score * self.WEIGHTS['package_compatibility']) / 100,
            'issues': issues
        }
    
    def assess_hardware_risk(self, system: Dict) -> Dict[str, Any]:
        """Assess hardware-related risks"""
        memory_mb = int(system.get('memtotal_mb', 0))
        processor_cores = int(system.get('processor_cores', 1))
        
        risk_score = 0
        issues = []
        
        # Memory assessment
        if memory_mb < 2048:
            risk_score += 40
            issues.append(f"Low memory: {memory_mb}MB (minimum 2GB recommended for RHEL 8/9)")
        elif memory_mb < 4096:
            risk_score += 20
            issues.append(f"Moderate memory: {memory_mb}MB (4GB+ recommended)")
        else:
            issues.append(f"Adequate memory: {memory_mb}MB")
        
        # CPU assessment
        if processor_cores < 2:
            risk_score += 20
            issues.append(f"Limited CPU cores: {processor_cores} (2+ recommended)")
        else:
            issues.append(f"Adequate CPU cores: {processor_cores}")
        
        risk_score = min(100, risk_score)
        if risk_score < 30:
            risk_score = 15
        
        return {
            'score': risk_score,
            'weight': self.WEIGHTS['hardware'],
            'weighted_score': (risk_score * self.WEIGHTS['hardware']) / 100,
            'issues': issues
        }
    
    def assess_services_risk(self, system: Dict) -> Dict[str, Any]:
        """Assess services compatibility risks"""
        services = system.get('enabled_services', [])
        
        risk_score = 0
        issues = []
        problematic_found = []
        
        for service in services:
            for problematic in self.PROBLEMATIC_SERVICES:
                if problematic in service:
                    problematic_found.append(service)
        
        if problematic_found:
            risk_score = min(100, 50 + len(problematic_found) * 15)
            issues.append(f"Found {len(problematic_found)} services requiring attention")
            issues.extend(problematic_found)
        else:
            risk_score = 15
            issues.append("No critical service compatibility issues detected")
        
        return {
            'score': risk_score,
            'weight': self.WEIGHTS['services'],
            'weighted_score': (risk_score * self.WEIGHTS['services']) / 100,
            'issues': issues
        }
    
    def assess_kernel_modules_risk(self, system: Dict) -> Dict[str, Any]:
        """Assess kernel modules compatibility"""
        modules = system.get('kernel_modules', [])
        
        # Simple heuristic: more modules might mean more complexity
        module_count = len(modules)
        
        if module_count > 100:
            risk_score = 40
            issues = [f"High number of kernel modules loaded: {module_count}"]
        elif module_count > 50:
            risk_score = 25
            issues = [f"Moderate number of kernel modules: {module_count}"]
        else:
            risk_score = 10
            issues = [f"Standard kernel module count: {module_count}"]
        
        return {
            'score': risk_score,
            'weight': self.WEIGHTS['kernel_modules'],
            'weighted_score': (risk_score * self.WEIGHTS['kernel_modules']) / 100,
            'issues': issues
        }
    
    def calculate_overall_risk(self, assessments: Dict) -> Dict[str, Any]:
        """Calculate overall risk score"""
        total_weighted_score = sum(
            assessment['weighted_score']
            for assessment in assessments.values()
        )
        
        # Classify risk level
        if total_weighted_score >= 70:
            risk_level = "HIGH"
            recommendation = "Immediate migration planning required"
        elif total_weighted_score >= 50:
            risk_level = "MEDIUM-HIGH"
            recommendation = "Migration should be planned within 6 months"
        elif total_weighted_score >= 30:
            risk_level = "MEDIUM"
            recommendation = "Migration can be scheduled in 6-12 months"
        else:
            risk_level = "LOW"
            recommendation = "System is relatively stable, plan migration at convenience"
        
        return {
            'overall_score': round(total_weighted_score, 2),
            'risk_level': risk_level,
            'recommendation': recommendation
        }
    
    def assess_system(self, system: Dict) -> Dict[str, Any]:
        """Perform complete assessment on a system"""
        hostname = system.get('hostname', 'unknown')
        print(f"\nAssessing: {hostname}")
        
        assessments = {
            'os_version': self.assess_os_version_risk(system),
            'package_compatibility': self.assess_package_compatibility(system),
            'hardware': self.assess_hardware_risk(system),
            'services': self.assess_services_risk(system),
            'kernel_modules': self.assess_kernel_modules_risk(system)
        }
        
        overall = self.calculate_overall_risk(assessments)
        
        result = {
            'hostname': hostname,
            'fqdn': system.get('fqdn', hostname),
            'os_family': self.normalize_os_family(
                system.get('os_family', ''),
                system.get('distribution', '')
            ),
            'distribution': system.get('distribution', ''),
            'distribution_version': system.get('distribution_version', ''),
            'assessment_date': datetime.now().isoformat(),
            'overall_risk_score': overall['overall_score'],
            'risk_level': overall['risk_level'],
            'recommendation': overall['recommendation'],
            'detailed_assessments': assessments
        }
        
        return result
    
    def run_assessment(self):
        """Run assessment on all loaded systems"""
        self.load_system_data()
        
        if not self.systems:
            print("No system data found to assess")
            return
        
        print(f"\n{'='*60}")
        print(f"Starting Migration Risk Assessment")
        print(f"Systems to assess: {len(self.systems)}")
        print(f"{'='*60}")
        
        for system in self.systems:
            result = self.assess_system(system)
            self.assessment_results.append(result)
        
        print(f"\n{'='*60}")
        print("Assessment Complete")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    data_dir = sys.argv[1] if len(sys.argv) > 1 else '../output'
    
    assessment = MigrationAssessment(data_dir)
    assessment.run_assessment()
    
    # Return results for use by report generator
    return assessment.assessment_results


if __name__ == '__main__':
    main()
