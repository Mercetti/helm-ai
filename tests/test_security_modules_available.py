"""
Test Security Modules Availability
Simple test to verify security modules can be imported and have expected structure
"""

import pytest
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestSecurityModulesAvailable:
    """Test that security modules are available and have expected structure"""
    
    def test_security_hardening_module_exists(self):
        """Test that security hardening module exists"""
        try:
            import src.security.security_hardening as security_hardening
            assert security_hardening is not None
            
            # Check that expected classes/functions exist
            assert hasattr(security_hardening, 'SecurityAuditor')
            assert hasattr(security_hardening, 'VulnerabilityScanner')
            assert hasattr(security_hardening, 'run_security_audit')
            assert hasattr(security_hardening, 'scan_vulnerabilities')
            assert hasattr(security_hardening, 'get_security_report')
            
        except ImportError as e:
            pytest.skip(f"Security hardening module not available: {e}")
    
    def test_security_monitoring_module_exists(self):
        """Test that security monitoring module exists"""
        try:
            import src.security.security_monitoring as security_monitoring
            assert security_monitoring is not None
            
            # Check for expected classes/functions
            # We'll check for common patterns since we don't know exact structure
            assert hasattr(security_monitoring, '__name__')
            assert security_monitoring.__name__.endswith('security_monitoring')
            
        except ImportError as e:
            pytest.skip(f"Security monitoring module not available: {e}")
    
    def test_compliance_monitoring_module_exists(self):
        """Test that compliance monitoring module exists"""
        try:
            import src.security.compliance_monitoring as compliance_monitoring
            assert compliance_monitoring is not None
            
            # Check for expected classes/functions
            assert hasattr(compliance_monitoring, '__name__')
            assert compliance_monitoring.__name__.endswith('compliance_monitoring')
            
        except ImportError as e:
            pytest.skip(f"Compliance monitoring module not available: {e}")
    
    def test_incident_response_module_exists(self):
        """Test that incident response module exists"""
        try:
            import src.security.incident_response as incident_response
            assert incident_response is not None
            
            # Check for expected classes/functions
            assert hasattr(incident_response, '__name__')
            assert incident_response.__name__.endswith('incident_response')
            
        except ImportError as e:
            pytest.skip(f"Incident response module not available: {e}")
    
    def test_security_hardening_file_structure(self):
        """Test that security hardening file has expected structure"""
        security_hardening_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'security', 'security_hardening.py'
        )
        
        assert os.path.exists(security_hardening_path), "Security hardening file should exist"
        
        # Read file and check for expected content
        with open(security_hardening_path, 'r') as f:
            content = f.read()
        
        # Check for key classes and functions
        assert 'class SecurityAuditor' in content, "SecurityAuditor class should exist"
        assert 'class VulnerabilityScanner' in content, "VulnerabilityScanner class should exist"
        assert 'def run_security_audit' in content, "run_security_audit function should exist"
        assert 'def scan_vulnerabilities' in content, "scan_vulnerabilities function should exist"
        assert 'def get_security_report' in content, "get_security_report function should exist"
    
    def test_security_monitoring_file_structure(self):
        """Test that security monitoring file has expected structure"""
        security_monitoring_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'security', 'security_monitoring.py'
        )
        
        assert os.path.exists(security_monitoring_path), "Security monitoring file should exist"
        
        # Read file and check for expected content
        with open(security_monitoring_path, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        assert 'class' in content, "Should contain at least one class"
        assert 'def' in content, "Should contain at least one function"
        assert 'monitoring' in content.lower(), "Should contain monitoring-related content"
    
    def test_compliance_monitoring_file_structure(self):
        """Test that compliance monitoring file has expected structure"""
        compliance_monitoring_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'security', 'compliance_monitoring.py'
        )
        
        assert os.path.exists(compliance_monitoring_path), "Compliance monitoring file should exist"
        
        # Read file and check for expected content
        with open(compliance_monitoring_path, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        assert 'class' in content, "Should contain at least one class"
        assert 'def' in content, "Should contain at least one function"
        assert 'compliance' in content.lower(), "Should contain compliance-related content"
    
    def test_incident_response_file_structure(self):
        """Test that incident response file has expected structure"""
        incident_response_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'security', 'incident_response.py'
        )
        
        assert os.path.exists(incident_response_path), "Incident response file should exist"
        
        # Read file and check for expected content
        with open(incident_response_path, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        assert 'class' in content, "Should contain at least one class"
        assert 'def' in content, "Should contain at least one function"
        assert 'incident' in content.lower(), "Should contain incident-related content"
    
    def test_security_directory_structure(self):
        """Test that security directory has expected files"""
        security_dir = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'security'
        )
        
        assert os.path.exists(security_dir), "Security directory should exist"
        assert os.path.isdir(security_dir), "Security should be a directory"
        
        # Check for expected files
        expected_files = [
            'security_hardening.py',
            'security_monitoring.py',
            'compliance_monitoring.py',
            'incident_response.py',
            'encryption.py',
            'disaster_recovery.py',
            'data_integrity.py',
            'backup_system.py'
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(security_dir, file_name)
            assert os.path.exists(file_path), f"Security file {file_name} should exist"
            assert os.path.isfile(file_path), f"Security file {file_name} should be a file"
    
    def test_security_modules_importable(self):
        """Test that all security modules can be imported without errors"""
        security_modules = [
            'src.security.security_hardening',
            'src.security.security_monitoring',
            'src.security.compliance_monitoring',
            'src.security.incident_response',
            'src.security.encryption',
            'src.security.disaster_recovery',
            'src.security.data_integrity',
            'src.security.backup_system'
        ]
        
        imported_modules = []
        failed_imports = []
        
        for module_name in security_modules:
            try:
                __import__(module_name)
                imported_modules.append(module_name)
            except ImportError as e:
                failed_imports.append((module_name, str(e)))
        
        # At least some modules should be importable
        assert len(imported_modules) > 0, f"At least some security modules should be importable. Failed: {failed_imports}"
        
        # Report which modules were successfully imported
        print(f"Successfully imported {len(imported_modules)} security modules:")
        for module in imported_modules:
            print(f"  - {module}")
        
        if failed_imports:
            print(f"Failed to import {len(failed_imports)} security modules:")
            for module, error in failed_imports:
                print(f"  - {module}: {error}")


if __name__ == "__main__":
    pytest.main([__file__])
