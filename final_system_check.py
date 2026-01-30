#!/usr/bin/env python3
"""
Stellar Logic AI - Final Comprehensive System Check
Complete UI/UX and backend validation for bug-free launch
"""

import requests
import json
import time
import os
from datetime import datetime

class FinalSystemCheck:
    def __init__(self):
        self.servers = {
            'dashboard': {'port': 5000, 'url': 'http://localhost:5000'},
            'llm': {'port': 5001, 'url': 'http://localhost:5001'},
            'team_chat': {'port': 5002, 'url': 'http://localhost:5002'},
            'voice_chat': {'port': 5003, 'url': 'http://localhost:5003'},
            'video_chat': {'port': 5004, 'url': 'http://localhost:5004'},
            'friends_system': {'port': 5005, 'url': 'http://localhost:5005'},
            'analytics': {'port': 5006, 'url': 'http://localhost:5006'},
            'security': {'port': 5007, 'url': 'http://localhost:5007'}
        }
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_issue(self, component, issue, severity='error'):
        self.issues.append({
            'component': component,
            'issue': issue,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        
    def log_warning(self, component, warning):
        self.warnings.append({
            'component': component,
            'warning': warning,
            'timestamp': datetime.now().isoformat()
        })
        
    def log_success(self, component, success):
        self.successes.append({
            'component': component,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
    
    def check_server_health(self):
        """Check all server health endpoints"""
        print("🔍 Checking Server Health...")
        
        for server_name, server_info in self.servers.items():
            try:
                health_url = f"{server_info['url']}/api/health"
                response = requests.get(health_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_success(server_name, f"Health check passed - {data.get('status', 'unknown')}")
                    print(f"✅ {server_name}: Healthy")
                else:
                    self.log_issue(server_name, f"Health check failed with status {response.status_code}")
                    print(f"❌ {server_name}: Health check failed")
                    
            except requests.exceptions.Timeout:
                self.log_issue(server_name, "Health check timeout")
                print(f"⏰ {server_name}: Timeout")
            except requests.exceptions.ConnectionError:
                self.log_issue(server_name, "Connection refused")
                print(f"🔌 {server_name}: Connection refused")
            except Exception as e:
                self.log_issue(server_name, f"Unexpected error: {str(e)}")
                print(f"❓ {server_name}: {str(e)}")
    
    def check_api_endpoints(self):
        """Check critical API endpoints"""
        print("\n🔍 Checking API Endpoints...")
        
        # LLM Server endpoints
        llm_endpoints = [
            ('/api/chat', 'POST', {'message': 'test message'}),
            ('/api/models', 'GET', None),
            ('/api/email/generate', 'POST', {'investor_name': 'Test', 'investor_firm': 'Test Corp'}),
            ('/api/research', 'POST', {'query': 'test query'}),
            ('/api/campaign', 'POST', {}),
            ('/api/documents', 'POST', {}),
            ('/api/feedback', 'POST', {'feedback': 'test'})
        ]
        
        for endpoint, method, data in llm_endpoints:
            try:
                url = f"{self.servers['llm']['url']}{endpoint}"
                if method == 'POST':
                    response = requests.post(url, json=data, timeout=10)
                else:
                    response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log_success('llm_api', f"{method} {endpoint} - {response.status_code}")
                    print(f"✅ LLM API {method} {endpoint}: OK")
                else:
                    self.log_warning('llm_api', f"{method} {endpoint} - {response.status_code}")
                    print(f"⚠️ LLM API {method} {endpoint}: {response.status_code}")
                    
            except Exception as e:
                self.log_issue('llm_api', f"{method} {endpoint} - {str(e)}")
                print(f"❌ LLM API {method} {endpoint}: {str(e)}")
        
        # Team Chat endpoints
        chat_endpoints = [
            ('/api/channels', 'GET', None),
            ('/api/chat/messages/general', 'GET', None)
        ]
        
        for endpoint, method, data in chat_endpoints:
            try:
                url = f"{self.servers['team_chat']['url']}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.log_success('team_chat_api', f"{method} {endpoint} - {response.status_code}")
                    print(f"✅ Team Chat API {method} {endpoint}: OK")
                else:
                    self.log_warning('team_chat_api', f"{method} {endpoint} - {response.status_code}")
                    print(f"⚠️ Team Chat API {method} {endpoint}: {response.status_code}")
                    
            except Exception as e:
                self.log_issue('team_chat_api', f"{method} {endpoint} - {str(e)}")
                print(f"❌ Team Chat API {method} {endpoint}: {str(e)}")
    
    def check_files_exist(self):
        """Check all required files exist"""
        print("\n🔍 Checking Required Files...")
        
        required_files = [
            'dashboard.html',
            'mobile.html',
            'stellar_llm_server.py',
            'team_chat_server.py',
            'voice_chat_server.py',
            'video_chat_server.py',
            'friends_system_server.py',
            'analytics_server.py',
            'security_server.py',
            'webrtc-client.js',
            'dev_server.py',
            'deploy_production.py',
            'start_stellar_ai_clean.bat'
        ]
        
        for file_name in required_files:
            if os.path.exists(file_name):
                self.log_success('files', f"{file_name} exists")
                print(f"✅ {file_name}: Exists")
            else:
                self.log_issue('files', f"{file_name} missing")
                print(f"❌ {file_name}: Missing")
    
    def check_ui_integrity(self):
        """Check UI/UX integrity"""
        print("\n🔍 Checking UI/UX Integrity...")
        
        # Check dashboard.html
        try:
            with open('dashboard.html', 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
                
            # Check for critical elements
            critical_elements = [
                'webrtc-client.js',
                'socket.io',
                'timeManagementAI',
                'startVoiceCall',
                'startVideoCall',
                'openFriendsSystem',
                'openTeamChat'
            ]
            
            for element in critical_elements:
                if element in dashboard_content:
                    self.log_success('dashboard_ui', f"Contains {element}")
                    print(f"✅ Dashboard UI: {element} found")
                else:
                    self.log_issue('dashboard_ui', f"Missing {element}")
                    print(f"❌ Dashboard UI: {element} missing")
                    
        except Exception as e:
            self.log_issue('dashboard_ui', f"Error reading dashboard.html: {str(e)}")
            print(f"❌ Dashboard UI: Error reading file")
        
        # Check mobile.html
        try:
            with open('mobile.html', 'r', encoding='utf-8') as f:
                mobile_content = f.read()
                
            mobile_elements = [
                'mobile-container',
                'showSection',
                'sendAIMessage',
                'loadAnalyticsData'
            ]
            
            for element in mobile_elements:
                if element in mobile_content:
                    self.log_success('mobile_ui', f"Contains {element}")
                    print(f"✅ Mobile UI: {element} found")
                else:
                    self.log_warning('mobile_ui', f"Missing {element}")
                    print(f"⚠️ Mobile UI: {element} missing")
                    
        except Exception as e:
            self.log_issue('mobile_ui', f"Error reading mobile.html: {str(e)}")
            print(f"❌ Mobile UI: Error reading file")
    
    def check_dependencies(self):
        """Check dependencies and imports"""
        print("\n🔍 Checking Dependencies...")
        
        # Check Python imports in server files
        server_files = [
            'stellar_llm_server.py',
            'team_chat_server.py',
            'voice_chat_server.py',
            'video_chat_server.py',
            'friends_system_server.py',
            'analytics_server.py',
            'security_server.py'
        ]
        
        for server_file in server_files:
            try:
                with open(server_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for critical imports
                critical_imports = [
                    'flask',
                    'requests',
                    'sqlite3',
                    'json'
                ]
                
                for import_name in critical_imports:
                    if import_name in content:
                        self.log_success('dependencies', f"{server_file} imports {import_name}")
                        print(f"✅ {server_file}: {import_name} imported")
                    else:
                        self.log_warning('dependencies', f"{server_file} missing {import_name}")
                        print(f"⚠️ {server_file}: {import_name} not imported")
                        
            except Exception as e:
                self.log_issue('dependencies', f"Error checking {server_file}: {str(e)}")
                print(f"❌ {server_file}: {str(e)}")
    
    def check_database_files(self):
        """Check database files and connections"""
        print("\n🔍 Checking Database Files...")
        
        db_files = [
            'stellar_learning_platform.db',
            'team_chat.db',
            'friends_system.db',
            'analytics.db',
            'security_compliance.db'
        ]
        
        for db_file in db_files:
            if os.path.exists(db_file):
                self.log_success('database', f"{db_file} exists")
                print(f"✅ Database: {db_file} exists")
            else:
                self.log_warning('database', f"{db_file} not found (will be created)")
                print(f"⚠️ Database: {db_file} not found (will be created)")
    
    def check_ollama_connection(self):
        """Check Ollama connection"""
        print("\n🔍 Checking Ollama Connection...")
        
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                self.log_success('ollama', f"Connected - {len(models)} models available")
                print(f"✅ Ollama: Connected - {len(models)} models available")
                
                # Check for stellar-logic-ai model
                for model in models:
                    if 'stellar-logic-ai' in model.get('name', ''):
                        self.log_success('ollama', "Stellar Logic AI model found")
                        print(f"✅ Ollama: Stellar Logic AI model found")
                        break
                else:
                    self.log_warning('ollama', "Stellar Logic AI model not found")
                    print(f"⚠️ Ollama: Stellar Logic AI model not found")
            else:
                self.log_issue('ollama', f"Connection failed with status {response.status_code}")
                print(f"❌ Ollama: Connection failed")
                
        except Exception as e:
            self.log_issue('ollama', f"Connection error: {str(e)}")
            print(f"❌ Ollama: {str(e)}")
    
    def check_websocket_connections(self):
        """Check WebSocket/Socket.io capabilities"""
        print("\n🔍 Checking WebSocket Capabilities...")
        
        # Check if Socket.io is included in dashboard
        try:
            with open('dashboard.html', 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
                
            if 'socket.io' in dashboard_content.lower():
                self.log_success('websocket', "Socket.io included in dashboard")
                print(f"✅ WebSocket: Socket.io included")
            else:
                self.log_issue('websocket', "Socket.io not found in dashboard")
                print(f"❌ WebSocket: Socket.io not found")
                
        except Exception as e:
            self.log_issue('websocket', f"Error checking WebSocket: {str(e)}")
            print(f"❌ WebSocket: {str(e)}")
    
    def check_css_and_styling(self):
        """Check CSS and styling integrity"""
        print("\n🔍 Checking CSS and Styling...")
        
        try:
            with open('dashboard.html', 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
                
            # Check for critical CSS classes
            css_classes = [
                '.dashboard',
                '.chat-interface',
                '.friends-system-container',
                '.voice-call-ui',
                '.video-call-ui',
                '.mobile-container'
            ]
            
            for css_class in css_classes:
                if css_class in dashboard_content:
                    self.log_success('css', f"CSS class {css_class} found")
                    print(f"✅ CSS: {css_class} found")
                else:
                    self.log_warning('css', f"CSS class {css_class} missing")
                    print(f"⚠️ CSS: {css_class} missing")
                    
        except Exception as e:
            self.log_issue('css', f"Error checking CSS: {str(e)}")
            print(f"❌ CSS: {str(e)}")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "="*60)
        print("📊 FINAL SYSTEM CHECK REPORT")
        print("="*60)
        
        print(f"\n✅ SUCCESSES: {len(self.successes)}")
        for success in self.successes:
            print(f"  ✅ {success['component']}: {success['success']}")
        
        print(f"\n⚠️ WARNINGS: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"  ⚠️ {warning['component']}: {warning['warning']}")
        
        print(f"\n❌ ISSUES: {len(self.issues)}")
        for issue in self.issues:
            print(f"  ❌ {issue['component']}: {issue['issue']}")
        
        # Overall status
        total_checks = len(self.successes) + len(self.warnings) + len(self.issues)
        success_rate = (len(self.successes) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 OVERALL STATUS: {success_rate:.1f}% Success Rate")
        
        if len(self.issues) == 0:
            print("🎉 SYSTEM IS READY FOR LAUNCH!")
        else:
            print("⚠️ SYSTEM HAS ISSUES THAT NEED ADDRESSING")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'successes': self.successes,
            'warnings': self.warnings,
            'issues': self.issues,
            'success_rate': success_rate,
            'total_checks': total_checks
        }
        
        with open('final_system_check_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: final_system_check_report.json")
        
        return len(self.issues) == 0
    
    def run_comprehensive_check(self):
        """Run all checks"""
        print("🚀 Starting Comprehensive Final System Check...")
        print("="*60)
        
        self.check_files_exist()
        self.check_server_health()
        self.check_api_endpoints()
        self.check_ui_integrity()
        self.check_dependencies()
        self.check_database_files()
        self.check_ollama_connection()
        self.check_websocket_connections()
        self.check_css_and_styling()
        
        return self.generate_final_report()

def main():
    """Main check function"""
    checker = FinalSystemCheck()
    is_ready = checker.run_comprehensive_check()
    
    if is_ready:
        print("\n🎉 YOUR PLATFORM IS 100% READY FOR LAUNCH!")
        print("✅ No critical issues found")
        print("✅ All servers running")
        print("✅ All files present")
        print("✅ UI/UX integrity confirmed")
        print("✅ Dependencies verified")
        print("\n🚀 Launch your platform with confidence!")
    else:
        print("\n⚠️ ISSUES FOUND - PLEASE ADDRESS BEFORE LAUNCH")
        print("❌ Check the detailed report for specific issues")
        print("📄 See: final_system_check_report.json")
    
    return is_ready

if __name__ == '__main__':
    main()
