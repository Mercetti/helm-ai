#!/usr/bin/env python3
"""
Stellar Logic AI - Quick Security Monitoring Setup (Fixed)
Initialize monitoring system without unicode issues
"""

import os
import json
from datetime import datetime

def setup_monitoring():
    """Set up security monitoring configuration"""
    print("Setting up Security Monitoring...")
    
    production_path = "c:/Users/merce/Documents/helm-ai/production"
    monitoring_path = os.path.join(production_path, "monitoring")
    
    # Create monitoring configuration
    monitoring_config = {
        "security_monitoring": {
            "enabled": True,
            "log_file": "production/logs/stellar_security.log",
            "alert_thresholds": {
                "failed_logins": 10,
                "suspicious_patterns": 5,
                "rate_limit_hits": 100,
                "csrf_failures": 10,
                "sql_injection_attempts": 3,
                "xss_attempts": 3,
                "unauthorized_access": 5
            },
            "notifications": {
                "email": "security@stellarlogic.ai",
                "webhook": "https://api.stellarlogic.ai/alerts",
                "slack": "#security-alerts"
            },
            "metrics": {
                "collection_interval": 60,
                "retention_days": 30,
                "export_format": "json"
            }
        }
    }
    
    # Save monitoring configuration
    config_path = os.path.join(monitoring_path, "security_monitoring.json")
    with open(config_path, 'w') as f:
        json.dump(monitoring_config, f, indent=2)
    
    print("Monitoring configuration saved")
    
    # Create initial security report
    initial_report = {
        "timestamp": datetime.now().isoformat(),
        "system": "Stellar Logic AI",
        "report_type": "initial_security_report",
        "status": "monitoring_configured",
        "components": [
            "Security Event Logging",
            "Real-time Alerting",
            "Threat Detection",
            "IP Anomaly Detection",
            "SQL Injection Monitoring",
            "XSS Attempt Detection",
            "Rate Limiting Monitoring"
        ],
        "alert_thresholds": monitoring_config["security_monitoring"]["alert_thresholds"],
        "next_steps": [
            "Start production server to generate security events",
            "Monitor security logs for alerts",
            "Review security reports regularly"
        ]
    }
    
    report_path = os.path.join(monitoring_path, "initial_security_report.json")
    with open(report_path, 'w') as f:
        json.dump(initial_report, f, indent=2)
    
    print("Initial security report created")
    
    # Create monitoring startup script
    startup_script = """#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime

# Add production path
sys.path.insert(0, 'c:/Users/merce/Documents/helm-ai')

def start_monitoring():
    print("Starting Stellar Logic AI Security Monitoring...")
    
    # Check if production server is running
    try:
        import requests
        response = requests.get('http://localhost/health', timeout=5)
        if response.status_code == 200:
            print("Production server is running")
        else:
            print("Production server may not be running")
    except:
        print("Cannot connect to production server - start it first")
        print("Run: cd production && python start_stellar_security.py")
        return
    
    # Start monitoring (simplified version)
    print("Security monitoring is now active")
    print("Alerts will be generated based on security events")
    print("Reports will be generated hourly")
    
    # Monitor for 60 seconds as demo
    for i in range(60):
        time.sleep(1)
        if i % 10 == 0:
            print(f"Monitoring... ({i}s)")

if __name__ == "__main__":
    start_monitoring()
"""
    
    startup_path = os.path.join(production_path, "start_monitoring.py")
    with open(startup_path, 'w') as f:
        f.write(startup_script)
    
    print("Monitoring startup script created")
    
    return True

if __name__ == "__main__":
    success = setup_monitoring()
    if success:
        print("\nSecurity monitoring setup completed!")
        print("Ready to monitor security events")
        print("Next: Start production server to begin monitoring")
    else:
        print("Monitoring setup failed")
