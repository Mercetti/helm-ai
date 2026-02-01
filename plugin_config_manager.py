#!/usr/bin/env python3
"""
Plugin Configuration Manager
Centralized configuration management for all Helm AI plugins
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PluginConfig:
    """Plugin configuration data class"""
    name: str
    port: int
    enabled: bool
    host: str = "localhost"
    debug: bool = False
    environment: str = "production"

class PluginConfigurationManager:
    """Manages configuration for all plugins"""
    
    def __init__(self, env_file: str = ".env.plugins"):
        self.env_file = env_file
        self.configs = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Load configurations from environment file"""
        # Default configurations
        self.configs = {
            'helm-api': PluginConfig(
                name='Core API Server',
                port=int(os.getenv('API_PORT', 5001)),
                enabled=True,
                host=os.getenv('API_HOST', 'localhost'),
                debug=os.getenv('API_DEBUG', 'false').lower() == 'true',
                environment=os.getenv('API_ENVIRONMENT', 'production')
            ),
            'healthcare-plugin': PluginConfig(
                name='Healthcare Plugin',
                port=int(os.getenv('HEALTHCARE_PLUGIN_PORT', 5002)),
                enabled=os.getenv('HEALTHCARE_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'government-defense-plugin': PluginConfig(
                name='Government & Defense Plugin',
                port=int(os.getenv('GOVERNMENT_DEFENSE_PLUGIN_PORT', 5005)),
                enabled=os.getenv('GOVERNMENT_DEFENSE_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'automotive-transportation-plugin': PluginConfig(
                name='Automotive & Transportation Plugin',
                port=int(os.getenv('AUTOMOTIVE_TRANSPORTATION_PLUGIN_PORT', 5006)),
                enabled=os.getenv('AUTOMOTIVE_TRANSPORTATION_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'real-estate-plugin': PluginConfig(
                name='Real Estate & Property Plugin',
                port=int(os.getenv('REAL_ESTATE_PLUGIN_PORT', 5007)),
                enabled=os.getenv('REAL_ESTATE_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'financial-plugin': PluginConfig(
                name='Financial Services Plugin',
                port=int(os.getenv('FINANCIAL_PLUGIN_PORT', 5008)),
                enabled=os.getenv('FINANCIAL_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'manufacturing-plugin': PluginConfig(
                name='Manufacturing & IoT Plugin',
                port=int(os.getenv('MANUFACTURING_PLUGIN_PORT', 5009)),
                enabled=os.getenv('MANUFACTURING_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'education-plugin': PluginConfig(
                name='Education & Academic Plugin',
                port=int(os.getenv('EDUCATION_PLUGIN_PORT', 5010)),
                enabled=os.getenv('EDUCATION_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'ecommerce-plugin': PluginConfig(
                name='E-Commerce Plugin',
                port=int(os.getenv('ECOMMERCE_PLUGIN_PORT', 5011)),
                enabled=os.getenv('ECOMMERCE_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'media-entertainment-plugin': PluginConfig(
                name='Media & Entertainment Plugin',
                port=int(os.getenv('MEDIA_ENTERTAINMENT_PLUGIN_PORT', 5012)),
                enabled=os.getenv('MEDIA_ENTERTAINMENT_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'pharmaceutical-plugin': PluginConfig(
                name='Pharmaceutical & Research Plugin',
                port=int(os.getenv('PHARMACEUTICAL_PLUGIN_PORT', 5013)),
                enabled=os.getenv('PHARMACEUTICAL_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'enterprise-plugin': PluginConfig(
                name='Enterprise Solutions Plugin',
                port=int(os.getenv('ENTERPRISE_PLUGIN_PORT', 5014)),
                enabled=os.getenv('ENTERPRISE_PLUGIN_ENABLED', 'true').lower() == 'true'
            ),
            'gaming-plugin': PluginConfig(
                name='Enhanced Gaming Plugin',
                port=int(os.getenv('GAMING_PLUGIN_PORT', 5015)),
                enabled=os.getenv('GAMING_PLUGIN_ENABLED', 'true').lower() == 'true'
            )
        }
    
    def get_plugin_config(self, plugin_id: str) -> Optional[PluginConfig]:
        """Get configuration for a specific plugin"""
        return self.configs.get(plugin_id)
    
    def get_all_configs(self) -> Dict[str, PluginConfig]:
        """Get all plugin configurations"""
        return self.configs
    
    def get_enabled_plugins(self) -> Dict[str, PluginConfig]:
        """Get only enabled plugins"""
        return {k: v for k, v in self.configs.items() if v.enabled}
    
    def get_plugin_url(self, plugin_id: str) -> Optional[str]:
        """Get full URL for a plugin"""
        config = self.get_plugin_config(plugin_id)
        if config:
            return f"http://{config.host}:{config.port}"
        return None
    
    def update_plugin_config(self, plugin_id: str, **kwargs) -> bool:
        """Update configuration for a specific plugin"""
        if plugin_id not in self.configs:
            return False
        
        config = self.configs[plugin_id]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return True
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        return self.update_plugin_config(plugin_id, enabled=True)
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        return self.update_plugin_config(plugin_id, enabled=False)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'url': os.getenv('DATABASE_URL', 'postgresql://helm_user:helm_password@localhost:5432/helm_ai'),
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', 5432)),
            'name': os.getenv('DATABASE_NAME', 'helm_ai'),
            'user': os.getenv('DATABASE_USER', 'helm_user'),
            'password': os.getenv('DATABASE_PASSWORD', 'helm_password')
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0))
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here'),
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here'),
            'encryption_key': os.getenv('ENCRYPTION_KEY', 'your-encryption-key-here'),
            'enable_rate_limiting': os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            'rate_limit_requests': int(os.getenv('RATE_LIMIT_REQUESTS', 100)),
            'rate_limit_window': int(os.getenv('RATE_LIMIT_WINDOW', 60))
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', 'json'),
            'file': os.getenv('LOG_FILE', 'logs/helm_ai.log'),
            'max_size': os.getenv('LOG_MAX_SIZE', '10MB'),
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', 5))
        }
    
    def save_config_to_file(self, filename: str = 'plugin_config.json'):
        """Save current configuration to file"""
        config_data = {}
        
        for plugin_id, config in self.configs.items():
            config_data[plugin_id] = {
                'name': config.name,
                'port': config.port,
                'enabled': config.enabled,
                'host': config.host,
                'debug': config.debug,
                'environment': config.environment
            }
        
        try:
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"Configuration saved to: {filename}")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_config_from_file(self, filename: str = 'plugin_config.json'):
        """Load configuration from file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            for plugin_id, data in config_data.items():
                if plugin_id in self.configs:
                    self.update_plugin_config(plugin_id, **data)
            
            print(f"Configuration loaded from: {filename}")
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def print_config_summary(self):
        """Print configuration summary"""
        print("Plugin Configuration Summary")
        print("=" * 50)
        
        enabled_count = 0
        disabled_count = 0
        
        for plugin_id, config in self.configs.items():
            status = "✅ Enabled" if config.enabled else "❌ Disabled"
            print(f"{config.name} (Port {config.port}): {status}")
            
            if config.enabled:
                enabled_count += 1
            else:
                disabled_count += 1
        
        print()
        print(f"Total Plugins: {len(self.configs)}")
        print(f"Enabled: {enabled_count}")
        print(f"Disabled: {disabled_count}")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration"""
        issues = []
        warnings = []
        
        # Check for port conflicts
        port_usage = {}
        for plugin_id, config in self.configs.items():
            if config.enabled:
                if config.port in port_usage:
                    issues.append(f"Port conflict: {config.name} and {port_usage[config.port]} both use port {config.port}")
                else:
                    port_usage[config.port] = config.name
        
        # Check for required environment variables
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        for var in required_vars:
            if not os.getenv(var):
                warnings.append(f"Missing environment variable: {var}")
        
        # Check for reasonable port ranges
        for plugin_id, config in self.configs.items():
            if config.port < 1024:
                warnings.append(f"{config.name} uses privileged port {config.port}")
            elif config.port > 65535:
                issues.append(f"{config.name} uses invalid port {config.port}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

# Global configuration manager instance
config_manager = PluginConfigurationManager()

def main():
    """Main function for testing"""
    print("Plugin Configuration Manager")
    print("=" * 50)
    
    # Print configuration summary
    config_manager.print_config_summary()
    
    # Validate configuration
    validation = config_manager.validate_config()
    print(f"\nConfiguration Valid: {'✅ Yes' if validation['valid'] else '❌ No'}")
    
    if validation['issues']:
        print("\nIssues:")
        for issue in validation['issues']:
            print(f"  ❌ {issue}")
    
    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  ⚠️ {warning}")
    
    # Save configuration
    config_manager.save_config_to_file()

if __name__ == "__main__":
    main()
