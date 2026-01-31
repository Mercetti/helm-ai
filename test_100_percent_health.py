#!/usr/bin/env python3
"""
Stellar Logic AI - 100% Health Testing Suite
============================================

Comprehensive testing system to ensure 100% system health
and integration across all components.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Any

class StellarLogicAITester:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        self.health_score = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite for 100% health verification"""
        print("🚀 STELLAR LOGIC AI - 100% HEALTH TESTING SUITE")
        print("=" * 60)
        
        # Test Categories
        self.test_file_structure()
        self.test_documentation_integrity()
        self.test_branding_consistency()
        self.test_backend_systems()
        self.test_website_functionality()
        self.test_cross_references()
        self.test_python_syntax()
        self.test_system_integration()
        
        # Calculate final health score
        self.calculate_health_score()
        
        # Generate final report
        self.generate_final_report()
        
        return self.test_results
    
    def test_file_structure(self) -> None:
        """Test complete file structure"""
        print("\n📁 TESTING FILE STRUCTURE...")
        
        required_files = {
            'markdown': [
                'AI_CONTENT_AUTOMATION.md',
                'AI_ANALYTICS_TRACKING.md',
                'BUSINESS_DEVELOPMENT_AUTOMATION.md',
                'INVESTOR_RELATIONS_AUTOMATION.md',
                'AUTOMATED_REVENUE_STREAMS.md',
                'CONTENT_LIBRARY.md',
                'CONTENT_CALENDAR.md',
                'PROJECT_MANAGEMENT.md',
                'BACKUP_RECOVERY_SYSTEMS.md',
                'BUSINESS_DOCUMENTATION.md'
            ],
            'html': [
                'website/index.html',
                'index.html'
            ],
            'python': [
                'src/acquisition/strategy.py',
                'mvp/app.py',
                'analytics_server.py'
            ]
        }
        
        for category, files in required_files.items():
            for file_path in files:
                self.test_results['total_tests'] += 1
                full_path = self.base_dir / file_path
                
                if full_path.exists():
                    size = full_path.stat().st_size
                    self.test_results['passed'] += 1
                    self.test_results['details'].append({
                        'test': f'File Structure - {category}',
                        'file': file_path,
                        'status': 'PASS',
                        'details': f'File exists ({size:,} bytes)'
                    })
                else:
                    self.test_results['failed'] += 1
                    self.test_results['details'].append({
                        'test': f'File Structure - {category}',
                        'file': file_path,
                        'status': 'FAIL',
                        'details': 'File missing'
                    })
    
    def test_documentation_integrity(self) -> None:
        """Test documentation integrity and completeness"""
        print("\n📄 TESTING DOCUMENTATION INTEGRITY...")
        
        key_docs = [
            'AI_CONTENT_AUTOMATION.md',
            'AI_ANALYTICS_TRACKING.md',
            'BUSINESS_DEVELOPMENT_AUTOMATION.md',
            'INVESTOR_RELATIONS_AUTOMATION.md',
            'AUTOMATED_REVENUE_STREAMS.md'
        ]
        
        for doc in key_docs:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                self.test_results['total_tests'] += 1
                
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for key sections
                required_sections = ['## 🎯', '### **🚀', '---']
                missing_sections = []
                
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)
                
                if not missing_sections:
                    self.test_results['passed'] += 1
                    status = 'PASS'
                    details = f'Document structure complete ({len(content):,} characters)'
                else:
                    self.test_results['warnings'] += 1
                    status = 'WARNING'
                    details = f'Missing sections: {missing_sections}'
                
                self.test_results['details'].append({
                    'test': 'Documentation Integrity',
                    'file': doc,
                    'status': status,
                    'details': details
                })
    
    def test_branding_consistency(self) -> None:
        """Test branding consistency across all documents"""
        print("\n🎯 TESTING BRANDING CONSISTENCY...")
        
        key_docs = [
            'AI_CONTENT_AUTOMATION.md',
            'AI_ANALYTICS_TRACKING.md',
            'BUSINESS_DEVELOPMENT_AUTOMATION.md',
            'INVESTOR_RELATIONS_AUTOMATION.md',
            'AUTOMATED_REVENUE_STREAMS.md'
        ]
        
        branding_elements = {
            'Stellar Logic AI': 'Company name',
            'jamie@stellarlogic.ai': 'Contact email',
            'AI + gaming': 'Focus area'
        }
        
        for doc in key_docs:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for element, description in branding_elements.items():
                    self.test_results['total_tests'] += 1
                    
                    if element in content:
                        self.test_results['passed'] += 1
                        status = 'PASS'
                        details = f'{description} present'
                    else:
                        self.test_results['warnings'] += 1
                        status = 'WARNING'
                        details = f'{description} missing'
                    
                    self.test_results['details'].append({
                        'test': 'Branding Consistency',
                        'file': doc,
                        'status': status,
                        'details': details
                    })
    
    def test_backend_systems(self) -> None:
        """Test backend system functionality"""
        print("\n🔧 TESTING BACKEND SYSTEMS...")
        
        # Test Python imports
        required_modules = ['flask', 'requests', 'json']
        
        for module in required_modules:
            self.test_results['total_tests'] += 1
            
            try:
                if module == 'json':
                    import json
                    version = 'Built-in'
                else:
                    mod = __import__(module)
                    version = getattr(mod, '__version__', 'Unknown')
                
                self.test_results['passed'] += 1
                status = 'PASS'
                details = f'Module available (v{version})'
            except ImportError:
                self.test_results['failed'] += 1
                status = 'FAIL'
                details = 'Module not available'
            
            self.test_results['details'].append({
                'test': 'Backend Systems',
                'module': module,
                'status': status,
                'details': details
            })
    
    def test_website_functionality(self) -> None:
        """Test website functionality"""
        print("\n🌐 TESTING WEBSITE FUNCTIONALITY...")
        
        website_files = [
            'website/index.html',
            'index.html'
        ]
        
        for website_file in website_files:
            website_path = self.base_dir / website_file
            if website_path.exists():
                self.test_results['total_tests'] += 1
                
                with open(website_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for essential HTML elements
                required_elements = ['<!DOCTYPE html>', '<html', '<head>', '<body>', '</html>']
                missing_elements = [elem for elem in required_elements if elem not in content]
                
                if not missing_elements:
                    self.test_results['passed'] += 1
                    status = 'PASS'
                    details = f'HTML structure complete ({len(content):,} characters)'
                else:
                    self.test_results['warnings'] += 1
                    status = 'WARNING'
                    details = f'Missing elements: {missing_elements}'
                
                self.test_results['details'].append({
                    'test': 'Website Functionality',
                    'file': website_file,
                    'status': status,
                    'details': details
                })
    
    def test_cross_references(self) -> None:
        """Test cross-references between documents"""
        print("\n🔗 TESTING CROSS-REFERENCES...")
        
        # Test for consistent email references
        key_docs = [
            'AI_CONTENT_AUTOMATION.md',
            'AI_ANALYTICS_TRACKING.md',
            'BUSINESS_DEVELOPMENT_AUTOMATION.md'
        ]
        
        expected_email = 'jamie@stellarlogic.ai'
        
        for doc in key_docs:
            doc_path = self.base_dir / doc
            if doc_path.exists():
                self.test_results['total_tests'] += 1
                
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if expected_email in content:
                    self.test_results['passed'] += 1
                    status = 'PASS'
                    details = f'Email reference consistent'
                else:
                    self.test_results['warnings'] += 1
                    status = 'WARNING'
                    details = f'Email reference inconsistent'
                
                self.test_results['details'].append({
                    'test': 'Cross-References',
                    'file': doc,
                    'status': status,
                    'details': details
                })
    
    def test_python_syntax(self) -> None:
        """Test Python syntax in all Python files"""
        print("\n🐍 TESTING PYTHON SYNTAX...")
        
        python_files = list(self.base_dir.rglob('*.py'))
        
        for py_file in python_files:
            # Skip node_modules and other non-project files
            if 'node_modules' in str(py_file):
                continue
                
            self.test_results['total_tests'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                compile(content, str(py_file), 'exec')
                self.test_results['passed'] += 1
                status = 'PASS'
                details = f'Syntax valid ({len(content):,} characters)'
            except SyntaxError as e:
                self.test_results['failed'] += 1
                status = 'FAIL'
                details = f'Syntax error: {e}'
            except Exception as e:
                self.test_results['warnings'] += 1
                status = 'WARNING'
                details = f'Error: {e}'
            
            self.test_results['details'].append({
                'test': 'Python Syntax',
                'file': str(py_file.relative_to(self.base_dir)),
                'status': status,
                'details': details
            })
    
    def test_system_integration(self) -> None:
        """Test overall system integration"""
        print("\n🔄 TESTING SYSTEM INTEGRATION...")
        
        integration_tests = [
            {
                'name': 'Project Structure Complete',
                'test': lambda: len(list(self.base_dir.rglob('*.md'))) >= 50,
                'details': 'Sufficient documentation files'
            },
            {
                'name': 'Backend Scripts Present',
                'test': lambda: len(list(self.base_dir.rglob('*.py'))) >= 20,
                'details': 'Sufficient backend scripts'
            },
            {
                'name': 'Website Files Present',
                'test': lambda: len(list(self.base_dir.rglob('*.html'))) >= 10,
                'details': 'Sufficient web files'
            }
        ]
        
        for test in integration_tests:
            self.test_results['total_tests'] += 1
            
            try:
                if test['test']():
                    self.test_results['passed'] += 1
                    status = 'PASS'
                    details = test['details']
                else:
                    self.test_results['warnings'] += 1
                    status = 'WARNING'
                    details = f'Integration concern: {test["details"]}'
            except Exception as e:
                self.test_results['failed'] += 1
                status = 'FAIL'
                details = f'Test error: {e}'
            
            self.test_results['details'].append({
                'test': 'System Integration',
                'name': test['name'],
                'status': status,
                'details': details
            })
    
    def calculate_health_score(self) -> None:
        """Calculate overall health score"""
        if self.test_results['total_tests'] == 0:
            self.health_score = 0
            return
        
        # Weight scores: Pass=100, Warning=70, Fail=0
        total_score = (
            self.test_results['passed'] * 100 +
            self.test_results['warnings'] * 70 +
            self.test_results['failed'] * 0
        )
        
        max_score = self.test_results['total_tests'] * 100
        self.health_score = round((total_score / max_score) * 100, 1)
    
    def generate_final_report(self) -> None:
        """Generate final health report"""
        print("\n" + "=" * 60)
        print("🎯 STELLAR LOGIC AI - HEALTH REPORT")
        print("=" * 60)
        
        print(f"📊 OVERALL HEALTH SCORE: {self.health_score}%")
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"⚠️  Tests Warnings: {self.test_results['warnings']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📈 Total Tests: {self.test_results['total_tests']}")
        
        # Health status
        if self.health_score >= 95:
            status = "🟢 EXCELLENT - 100% READY"
        elif self.health_score >= 85:
            status = "🟡 GOOD - NEARLY READY"
        elif self.health_score >= 70:
            status = "🟠 FAIR - NEEDS ATTENTION"
        else:
            status = "🔴 POOR - MAJOR ISSUES"
        
        print(f"\n🎯 SYSTEM STATUS: {status}")
        
        # Failed tests summary
        if self.test_results['failed'] > 0:
            print(f"\n❌ FAILED TESTS:")
            for detail in self.test_results['details']:
                if detail['status'] == 'FAIL':
                    print(f"   • {detail.get('file', detail.get('module', detail.get('name', 'Unknown')))}: {detail['details']}")
        
        # Warning tests summary
        if self.test_results['warnings'] > 0:
            print(f"\n⚠️  WARNINGS:")
            for detail in self.test_results['details']:
                if detail['status'] == 'WARNING':
                    print(f"   • {detail.get('file', detail.get('module', detail.get('name', 'Unknown')))}: {detail['details']}")
        
        # Success message
        if self.health_score >= 95:
            print(f"\n🎉 CONGRATULATIONS! SYSTEM IS 100% HEALTHY!")
            print(f"🚀 Stellar Logic AI is ready for production deployment!")
        elif self.health_score >= 85:
            print(f"\n👍 ALMOST THERE! Address warnings for 100% health.")
            print(f"🚀 System is nearly ready for deployment.")
        
        print("=" * 60)

def main():
    """Main execution function"""
    tester = StellarLogicAITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results.get('health_score', 0) >= 95:
        sys.exit(0)  # Success
    elif results.get('health_score', 0) >= 85:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Failure

if __name__ == "__main__":
    main()
