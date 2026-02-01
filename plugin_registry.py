
"""
Stellar Logic AI Plugin Registry
Centralized plugin management system
"""

import os
import json
import importlib.util
from datetime import datetime

class PluginRegistry:
    def __init__(self):
        self.plugins = {}
        self.plugin_configs = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Load all available plugins"""
        plugin_files = {
            'healthcare': 'healthcare_ai_security_plugin.py',
            'financial': 'financial_ai_security_plugin.py',
            'manufacturing': 'manufacturing_ai_security_plugin.py',
            'automotive': 'automotive_transportation_plugin.py',
            'real_estate': 'real_estate_plugin.py',
            'government': 'government_defense_plugin.py',
            'education': 'education_plugin.py',
            'ecommerce': 'ecommerce_plugin.py',
            'cybersecurity': 'cybersecurity_ai_security_plugin.py',
            'gaming': 'gaming_ai_security_plugin.py',
            'mobile': 'mobile_ai_security_plugin.py',
            'iot': 'iot_ai_security_plugin.py',
            'blockchain': 'blockchain_ai_security_plugin.py'
        }
        
        for plugin_name, plugin_file in plugin_files.items():
            if os.path.exists(plugin_file):
                try:
                    # Load plugin module
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Instantiate plugin class
                    if hasattr(module, 'SecurityPlugin'):
                        plugin_instance = module.SecurityPlugin()
                        self.plugins[plugin_name] = plugin_instance
                        print(f"✅ Loaded plugin: {plugin_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to load {plugin_name}: {e}")
            else:
                print(f"⚠️  Plugin file not found: {plugin_file}")
    
    def get_plugin(self, plugin_name):
        """Get a specific plugin instance"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self):
        """List all loaded plugins"""
        return list(self.plugins.keys())
    
    def analyze_threat_with_plugin(self, plugin_name, threat_data):
        """Analyze threat using specific plugin"""
        plugin = self.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'analyze_threat'):
            return plugin.analyze_threat(threat_data)
        else:
            return {'error': f'Plugin {plugin_name} not available or missing analyze_threat method'}
    
    def get_plugin_info(self, plugin_name):
        """Get plugin information"""
        plugin = self.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'get_plugin_info'):
            return plugin.get_plugin_info()
        else:
            return {'error': f'Plugin {plugin_name} not available or missing get_plugin_info method'}
    
    def get_all_plugins_info(self):
        """Get information for all plugins"""
        plugins_info = {}
        for plugin_name in self.list_plugins():
            plugins_info[plugin_name] = self.get_plugin_info(plugin_name)
        return plugins_info

# Global plugin registry instance
plugin_registry = PluginRegistry()

# Convenience functions
def analyze_threat(plugin_name, threat_data):
    """Analyze threat using specified plugin"""
    return plugin_registry.analyze_threat_with_plugin(plugin_name, threat_data)

def get_available_plugins():
    """Get list of available plugins"""
    return plugin_registry.list_plugins()

def get_plugin_info(plugin_name):
    """Get information about a plugin"""
    return plugin_registry.get_plugin_info(plugin_name)
