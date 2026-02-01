
"""
Plugin System Integration Tests
Tests all plugin integration and functionality
"""

import unittest
import json
import os
from datetime import datetime

class TestPluginIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Import plugin registry
        from plugin_registry import plugin_registry, analyze_threat, get_available_plugins
        
        self.plugin_registry = plugin_registry
        self.analyze_threat = analyze_threat
        self.get_available_plugins = get_available_plugins
    
    def test_plugin_registry_loading(self):
        """Test that plugin registry loads plugins correctly"""
        plugins = self.get_available_plugins()
        
        # Should have at least some plugins loaded
        self.assertGreater(len(plugins), 0)
        print(f"✅ Loaded {len(plugins)} plugins: {plugins}")
    
    def test_plugin_info_methods(self):
        """Test that all plugins have get_plugin_info method"""
        plugins = self.get_available_plugins()
        
        for plugin_name in plugins:
            info = self.plugin_registry.get_plugin_info(plugin_name)
            self.assertNotIn('error', info)
            self.assertIn('plugin_name', info)
            self.assertIn('version', info)
            print(f"✅ {plugin_name} plugin info method working")
    
    def test_threat_analysis_methods(self):
        """Test that all plugins have analyze_threat method"""
        plugins = self.get_available_plugins()
        
        test_threat = {
            'type': 'malware',
            'source': 'email',
            'content': 'Test malicious content'
        }
        
        for plugin_name in plugins:
            result = self.analyze_threat(plugin_name, test_threat)
            self.assertNotIn('error', result)
            self.assertIn('threat_id', result)
            print(f"✅ {plugin_name} threat analysis method working")
    
    def test_real_estate_plugin(self):
        """Test real estate plugin specific functionality"""
        if 'real_estate' in self.get_available_plugins():
            plugin = self.plugin_registry.get_plugin('real_estate')
            
            if hasattr(plugin, 'analyze_property_security'):
                test_property = {
                    'property_id': 'test_001',
                    'address': '123 Test St',
                    'property_type': 'residential',
                    'access_systems': ['keypad', 'camera']
                }
                
                result = plugin.analyze_property_security(test_property)
                self.assertNotIn('error', result)
                self.assertIn('security_score', result)
                print("✅ Real estate property security analysis working")
    
    def test_unicode_handling(self):
        """Test Unicode character handling in all plugins"""
        test_threat_unicode = {
            'type': 'suspicious',
            'source': 'web',
            'content': 'Test with Unicode: José García, 中文测试, العربية, 🏥⚕️💊'
        }
        
        plugins = self.get_available_plugins()
        for plugin_name in plugins:
            try:
                result = self.analyze_threat(plugin_name, test_threat_unicode)
                self.assertNotIn('error', result)
                print(f"✅ {plugin_name} Unicode handling working")
            except Exception as e:
                self.fail(f"Unicode handling failed in {plugin_name}: {e}")
    
    def test_error_handling(self):
        """Test error handling in plugins"""
        invalid_threat = {
            'type': None,  # Invalid type
            'source': None,
            'content': None
        }
        
        plugins = self.get_available_plugins()
        for plugin_name in plugins:
            result = self.analyze_threat(plugin_name, invalid_threat)
            # Should handle error gracefully
            self.assertIsNotNone(result)
            print(f"✅ {plugin_name} error handling working")

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
