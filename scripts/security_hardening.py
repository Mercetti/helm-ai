#!/usr/bin/env python3
"""
Helm AI Security Hardening Script
Runs comprehensive security assessments, monitoring, and hardening procedures
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.security.security_hardening import run_security_audit, scan_vulnerabilities, get_security_report
from src.security.security_monitoring import start_security_monitoring, stop_security_monitoring, get_security_status
from src.security.compliance_monitoring import start_compliance_monitoring, assess_compliance, get_compliance_status
from src.security.incident_response import get_incident_status

def run_security_hardening():
    """Run comprehensive security hardening"""
    print("🔒 Starting Helm AI Security Hardening")
    print("=" * 50)
    
    # Start monitoring systems
    print("\n🚀 Starting security monitoring systems...")
    start_security_monitoring()
    start_compliance_monitoring()
    
    try:
        # 1. Run Security Audit
        print("\n📋 Running security audit...")
        audits = run_security_audit("comprehensive")
        print(f"✅ Security audit completed: {len(audits)} findings")
        
        # Show audit summary
        critical_audits = [a for a in audits if a.severity == 'critical']
        high_audits = [a for a in audits if a.severity == 'high']
        
        if critical_audits:
            print(f"⚠️  Critical issues: {len(critical_audits)}")
            for audit in critical_audits[:3]:
                print(f"   - {audit.title}")
        
        if high_audits:
            print(f"⚠️  High issues: {len(high_audits)}")
            for audit in high_audits[:3]:
                print(f"   - {audit.title}")
        
        # 2. Scan Vulnerabilities
        print("\n🔍 Scanning for vulnerabilities...")
        vulnerabilities = scan_vulnerabilities()
        print(f"✅ Vulnerability scan completed: {len(vulnerabilities)} vulnerabilities found")
        
        # Show vulnerability summary
        critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
        high_vulns = [v for v in vulnerabilities if v.severity == 'high']
        
        if critical_vulns:
            print(f"⚠️  Critical vulnerabilities: {len(critical_vulns)}")
            for vuln in critical_vulns[:3]:
                print(f"   - {vuln.title}")
        
        if high_vulns:
            print(f"⚠️  High vulnerabilities: {len(high_vulns)}")
            for vuln in high_vulns[:3]:
                print(f"   - {vuln.title}")
        
        # 3. Run Compliance Assessment
        print("\n📊 Running compliance assessments...")
        frameworks = ['GDPR', 'SOC2', 'HIPAA', 'ISO27001']
        compliance_results = {}
        
        for framework in frameworks:
            try:
                report = assess_compliance(framework, 30)
                compliance_results[framework] = {
                    'score': report.overall_score,
                    'requirements_met': report.requirements_met,
                    'requirements_total': report.requirements_total
                }
                print(f"✅ {framework}: {report.overall_score:.1f}% compliance")
            except Exception as e:
                print(f"❌ {framework}: Assessment failed - {e}")
                compliance_results[framework] = {'score': 0, 'requirements_met': 0, 'requirements_total': 0}
        
        # 4. Get Security Status
        print("\n📈 Getting security status...")
        security_status = get_security_status()
        compliance_status = get_compliance_status()
        incident_status = get_incident_status()
        
        # Generate comprehensive report
        print("\n📄 Generating security hardening report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'security_audit': {
                'total_findings': len(audits),
                'critical_issues': len(critical_audits),
                'high_issues': len(high_audits),
                'findings': [audit.to_dict() for audit in audits[:10]]  # Top 10 findings
            },
            'vulnerability_scan': {
                'total_vulnerabilities': len(vulnerabilities),
                'critical_vulnerabilities': len(critical_vulns),
                'high_vulnerabilities': len(high_vulns),
                'vulnerabilities': [vuln.to_dict() for vuln in vulnerabilities[:10]]  # Top 10 vulnerabilities
            },
            'compliance_assessment': compliance_results,
            'security_status': security_status,
            'compliance_status': compliance_status,
            'incident_status': incident_status,
            'recommendations': generate_recommendations(audits, vulnerabilities, compliance_results)
        }
        
        # Save report
        report_file = f"security_hardening_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Security hardening report saved to {report_file}")
        
        # Print summary
        print("\n🎯 Security Hardening Summary:")
        print(f"   Security Issues: {len(audits)} total ({len(critical_audits)} critical, {len(high_audits)} high)")
        print(f"   Vulnerabilities: {len(vulnerabilities)} total ({len(critical_vulns)} critical, {len(high_vulns)} high)")
        print(f"   Active Incidents: {incident_status.get('active_incidents', 0)}")
        
        avg_compliance = sum(r['score'] for r in compliance_results.values()) / len(compliance_results)
        print(f"   Average Compliance: {avg_compliance:.1f}%")
        
        # Show top recommendations
        recommendations = report['recommendations']
        if recommendations:
            print(f"\n📋 Top Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        print("\n✅ Security hardening completed successfully!")
        
        return report
        
    finally:
        # Stop monitoring systems
        print("\n🛑 Stopping security monitoring systems...")
        stop_security_monitoring()

def generate_recommendations(audits, vulnerabilities, compliance_results):
    """Generate security recommendations"""
    recommendations = []
    
    # Security audit recommendations
    critical_audits = [a for a in audits if a.severity == 'critical']
    high_audits = [a for a in audits if a.severity == 'high']
    
    if critical_audits:
        recommendations.append("URGENT: Address critical security audit findings immediately")
    
    if high_audits:
        recommendations.append(f"Address {len(high_audits)} high-priority security issues")
    
    # Vulnerability recommendations
    critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
    high_vulns = [v for v in vulnerabilities if v.severity == 'high']
    
    if critical_vulns:
        recommendations.append("URGENT: Patch critical vulnerabilities immediately")
    
    if high_vulns:
        recommendations.append(f"Patch {len(high_vulns)} high-severity vulnerabilities")
    
    # Compliance recommendations
    low_compliance = [f for f, r in compliance_results.items() if r['score'] < 80]
    if low_compliance:
        recommendations.append(f"Improve compliance for: {', '.join(low_compliance)}")
    
    # General recommendations
    if not critical_audits and not critical_vulns:
        recommendations.append("Security posture is good - continue monitoring")
    
    recommendations.extend([
        "Implement regular security scanning and monitoring",
        "Conduct quarterly security assessments",
        "Maintain up-to-date security policies and procedures",
        "Provide regular security training to staff"
    ])
    
    return recommendations

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Helm AI Security Hardening")
    parser.add_argument(
        '--audit-only',
        action='store_true',
        help='Run security audit only'
    )
    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='Run vulnerability scan only'
    )
    parser.add_argument(
        '--compliance-only',
        action='store_true',
        help='Run compliance assessment only'
    )
    
    args = parser.parse_args()
    
    if args.audit_only:
        print("🔒 Running Security Audit Only")
        audits = run_security_audit("comprehensive")
        print(f"✅ Security audit completed: {len(audits)} findings")
        
        critical_audits = [a for a in audits if a.severity == 'critical']
        high_audits = [a for a in audits if a.severity == 'high']
        
        print(f"Critical issues: {len(critical_audits)}")
        print(f"High issues: {len(high_audits)}")
        
    elif args.scan_only:
        print("🔍 Running Vulnerability Scan Only")
        vulnerabilities = scan_vulnerabilities()
        print(f"✅ Vulnerability scan completed: {len(vulnerabilities)} vulnerabilities found")
        
        critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
        high_vulns = [v for v in vulnerabilities if v.severity == 'high']
        
        print(f"Critical vulnerabilities: {len(critical_vulns)}")
        print(f"High vulnerabilities: {len(high_vulns)}")
        
    elif args.compliance_only:
        print("📊 Running Compliance Assessment Only")
        frameworks = ['GDPR', 'SOC2', 'HIPAA', 'ISO27001']
        
        for framework in frameworks:
            try:
                report = assess_compliance(framework, 30)
                print(f"✅ {framework}: {report.overall_score:.1f}% compliance")
            except Exception as e:
                print(f"❌ {framework}: Assessment failed - {e}")
    else:
        # Run full security hardening
        run_security_hardening()

if __name__ == "__main__":
    main()
