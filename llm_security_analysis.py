#!/usr/bin/env python3
"""
LLM Security Integration Analysis
Analyzes current LLM integration with security systems and identifies needed updates
"""

import os
import sys
import re
from pathlib import Path

class LLMSecurityAnalyzer:
    def __init__(self):
        self.src_path = Path("src")
        self.security_path = self.src_path / "security"
        self.ai_path = self.src_path / "ai"
        self.findings = []
    
    def analyze_llm_security_integration(self):
        """Analyze LLM integration with security systems"""
        print("🔍 LLM SECURITY INTEGRATION ANALYSIS")
        print("=" * 60)
        
        # Check for LLM-specific security features
        self._check_prompt_injection_protection()
        self._check_content_filtering()
        self._check_output_validation()
        self._check_rate_limiting()
        self._check_access_control()
        self._check_audit_logging()
        self._check_data_privacy()
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _check_prompt_injection_protection(self):
        """Check for prompt injection protection"""
        print("\n🛡️ PROMPT INJECTION PROTECTION:")
        
        # Look for prompt injection patterns in security files
        injection_patterns = [
            r'prompt.*injection',
            r'input.*sanitization',
            r'llm.*security',
            r'model.*protection'
        ]
        
        found_patterns = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in injection_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_patterns.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_patterns:
            print("   ✅ Found prompt injection protection:")
            for file, pattern in found_patterns:
                print(f"      - {file}: {pattern}")
            self.findings.append("prompt_injection_protection")
        else:
            print("   ❌ No prompt injection protection found")
            self.findings.append("missing_prompt_injection_protection")
    
    def _check_content_filtering(self):
        """Check for content filtering capabilities"""
        print("\n🔍 CONTENT FILTERING:")
        
        # Look for content filtering patterns
        filter_patterns = [
            r'content.*filter',
            r'safe.*content',
            r'inappropriate.*content',
            r'moderation'
        ]
        
        found_filters = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in filter_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_filters.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_filters:
            print("   ✅ Found content filtering:")
            for file, pattern in found_filters:
                print(f"      - {file}: {pattern}")
            self.findings.append("content_filtering")
        else:
            print("   ❌ No content filtering found")
            self.findings.append("missing_content_filtering")
    
    def _check_output_validation(self):
        """Check for LLM output validation"""
        print("\n✅ OUTPUT VALIDATION:")
        
        # Look for output validation patterns
        validation_patterns = [
            r'output.*validation',
            r'response.*checking',
            r'llm.*output',
            r'generation.*control'
        ]
        
        found_validation = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in validation_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_validation.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_validation:
            print("   ✅ Found output validation:")
            for file, pattern in found_validation:
                print(f"      - {file}: {pattern}")
            self.findings.append("output_validation")
        else:
            print("   ❌ No output validation found")
            self.findings.append("missing_output_validation")
    
    def _check_rate_limiting(self):
        """Check for LLM rate limiting"""
        print("\n⏱️ RATE LIMITING:")
        
        # Look for rate limiting patterns
        rate_limit_patterns = [
            r'rate.*limit',
            r'throttling',
            r'api.*limit',
            r'request.*quota'
        ]
        
        found_rate_limits = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in rate_limit_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_rate_limits.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_rate_limits:
            print("   ✅ Found rate limiting:")
            for file, pattern in found_rate_limits:
                print(f"      - {file}: {pattern}")
            self.findings.append("rate_limiting")
        else:
            print("   ❌ No rate limiting found")
            self.findings.append("missing_rate_limiting")
    
    def _check_access_control(self):
        """Check for LLM access control"""
        print("\n🔐 ACCESS CONTROL:")
        
        # Look for access control patterns
        access_patterns = [
            r'access.*control',
            r'permission.*check',
            r'role.*based',
            r'authorization'
        ]
        
        found_access = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in access_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_access.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_access:
            print("   ✅ Found access control:")
            for file, pattern in found_access:
                print(f"      - {file}: {pattern}")
            self.findings.append("access_control")
        else:
            print("   ❌ No access control found")
            self.findings.append("missing_access_control")
    
    def _check_audit_logging(self):
        """Check for LLM audit logging"""
        print("\n📝 AUDIT LOGGING:")
        
        # Look for audit logging patterns
        audit_patterns = [
            r'audit.*log',
            r'llm.*audit',
            r'conversation.*log',
            r'interaction.*track'
        ]
        
        found_audit = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in audit_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_audit.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_audit:
            print("   ✅ Found audit logging:")
            for file, pattern in found_audit:
                print(f"      - {file}: {pattern}")
            self.findings.append("audit_logging")
        else:
            print("   ❌ No LLM-specific audit logging found")
            self.findings.append("missing_llm_audit_logging")
    
    def _check_data_privacy(self):
        """Check for data privacy protection"""
        print("\n🔒 DATA PRIVACY:")
        
        # Look for data privacy patterns
        privacy_patterns = [
            r'data.*privacy',
            r'pii.*protection',
            r'personal.*data',
            r'gdpr.*compliance'
        ]
        
        found_privacy = []
        for security_file in self.security_path.glob("*.py"):
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in privacy_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_privacy.append((security_file.name, pattern))
            except Exception as e:
                print(f"   Error reading {security_file}: {e}")
        
        if found_privacy:
            print("   ✅ Found data privacy protection:")
            for file, pattern in found_privacy:
                print(f"      - {file}: {pattern}")
            self.findings.append("data_privacy")
        else:
            print("   ❌ No LLM-specific data privacy found")
            self.findings.append("missing_llm_data_privacy")
    
    def _generate_recommendations(self):
        """Generate security recommendations"""
        print("\n🎯 SECURITY RECOMMENDATIONS:")
        print("=" * 60)
        
        recommendations = {
            "missing_prompt_injection_protection": [
                "Implement prompt injection detection",
                "Add input sanitization for LLM prompts",
                "Create malicious prompt pattern library",
                "Implement context-aware filtering"
            ],
            "missing_content_filtering": [
                "Add content moderation system",
                "Implement inappropriate content detection",
                "Create content classification system",
                "Add automated content blocking"
            ],
            "missing_output_validation": [
                "Implement LLM output validation",
                "Add response content checking",
                "Create output filtering system",
                "Implement response sanitization"
            ],
            "missing_rate_limiting": [
                "Add LLM-specific rate limiting",
                "Implement request throttling",
                "Create usage quota system",
                "Add burst protection"
            ],
            "missing_access_control": [
                "Implement LLM access control",
                "Add role-based permissions",
                "Create user authorization system",
                "Implement feature-level access"
            ],
            "missing_llm_audit_logging": [
                "Add LLM conversation logging",
                "Implement prompt/response tracking",
                "Create interaction audit system",
                "Add compliance reporting"
            ],
            "missing_llm_data_privacy": [
                "Add PII detection in prompts/responses",
                "Implement data anonymization",
                "Create privacy compliance system",
                "Add GDPR/CCPA compliance"
            ]
        }
        
        for finding in self.findings:
            if finding in recommendations:
                print(f"\n🔧 {finding.upper().replace('_', ' ')}:")
                for rec in recommendations[finding]:
                    print(f"   - {rec}")
        
        # Calculate security score
        total_checks = 7
        implemented_checks = total_checks - len([f for f in self.findings if f.startswith('missing_')])
        security_score = (implemented_checks / total_checks) * 100
        
        print(f"\n📊 LLM SECURITY SCORE: {security_score:.0f}/100")
        print(f"   Implemented: {implemented_checks}/{total_checks}")
        print(f"   Missing: {len(self.findings) - implemented_checks}/{total_checks}")

def main():
    analyzer = LLMSecurityAnalyzer()
    analyzer.analyze_llm_security_integration()

if __name__ == "__main__":
    main()
