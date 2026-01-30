#!/usr/bin/env python3
"""
Stellar Logic AI - Simple System Monitor
Quick health check without hanging
"""

import requests
import json
import time
from datetime import datetime

def quick_health_check():
    """Perform quick health check"""
    servers = {
        'dashboard': 5000,
        'llm': 5001,
        'team_chat': 5002,
        'voice_chat': 5003,
        'video_chat': 5004,
        'friends_system': 5005,
        'analytics': 5006,
        'security': 5007
    }
    
    print(f"\n🔍 Stellar Logic AI - System Health Check")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    healthy_count = 0
    total_count = len(servers)
    
    for server_name, port in servers.items():
        try:
            response = requests.get(f"http://localhost:{port}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {server_name:<15} - Port {port:<5} - HEALTHY")
                healthy_count += 1
            else:
                print(f"❌ {server_name:<15} - Port {port:<5} - HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ {server_name:<15} - Port {port:<5} - TIMEOUT")
        except requests.exceptions.ConnectionError:
            print(f"🔌 {server_name:<15} - Port {port:<5} - OFFLINE")
        except Exception as e:
            print(f"❓ {server_name:<15} - Port {port:<5} - ERROR: {str(e)[:20]}...")
    
    # Check Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            print(f"✅ {'Ollama':<15} - Port 11434 - HEALTHY")
            healthy_count += 1
        else:
            print(f"❌ {'Ollama':<15} - Port 11434 - HTTP {response.status_code}")
    except:
        print(f"❌ {'Ollama':<15} - Port 11434 - OFFLINE")
    
    # Summary
    print("=" * 60)
    health_percentage = (healthy_count / (total_count + 1)) * 100
    print(f"📊 Overall Health: {health_percentage:.1f}% ({healthy_count}/{total_count + 1})")
    
    if health_percentage >= 90:
        print("🎉 SYSTEM IS READY FOR LAUNCH!")
    elif health_percentage >= 70:
        print("⚠️ System mostly operational - minor issues")
    else:
        print("❌ System has significant issues")
    
    return health_percentage

if __name__ == '__main__':
    quick_health_check()
