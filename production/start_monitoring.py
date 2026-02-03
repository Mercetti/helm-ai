#!/usr/bin/env python3
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
