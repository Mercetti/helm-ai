#!/usr/bin/env python3
"""
Stellar Logic AI Configuration Manager
Centralized configuration management system
"""

import os
import json
import yaml
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_dir='./config'):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.config_dir / 'plugins').mkdir(exist_ok=True)
        (self.config_dir / 'gateway').mkdir(exist_ok=True)
        (self.config_dir / 'security').mkdir(exist_ok=True)
        (self.config_dir / 'monitoring').mkdir(exist_ok=True)
        (self.config_dir / 'deployment').mkdir(exist_ok=True)
        (self.config_dir / 'backups').mkdir(exist_ok=True)
        
        self.configs = {}
        self.watchers = {}
        self.lock = threading.Lock()
        
        # Load existing configurations
        self.load_all_configs()
        
        print(f"✅ Configuration Manager initialized: {self.config_dir}")
    
    def load_all_configs(self):
        """Load all configuration files"""
        config_files = {
            'plugins': self.config_dir / 'plugins',
            'gateway': self.config_dir / 'gateway',
            'security': self.config_dir / 'security',
            'monitoring': self.config_dir / 'monitoring',
            'deployment': self.config_dir / 'deployment'
        }
        
        for config_type, config_path in config_files.items():
            self.configs[config_type] = {}
            
            for config_file in config_path.glob('*.json'):
                config_name = config_file.stem
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self.configs[config_type][config_name] = json.load(f)
                        print(f"✅ Loaded {config_type}/{config_name} config")
                except Exception as e:
                    print(f"❌ Failed to load {config_type}/{config_name}: {e}")
    
    def get_config(self, config_type: str, config_name: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self.lock:
            if config_type in self.configs and config_name in self.configs[config_type]:
                return self.configs[config_type][config_name]
            return default
    
    def set_config(self, config_type: str, config_name: str, value: Any):
        """Set configuration value"""
        with self.lock:
            if config_type not in self.configs:
                self.configs[config_type] = {}
            
            self.configs[config_type][config_name] = value
            self.save_config(config_type, config_name)
    
    def save_config(self, config_type: str, config_name: str):
        """Save configuration to file"""
        if config_type not in self.configs or config_name not in self.configs[config_type]:
            return False
        
        config_path = self.config_dir / config_type / f"{config_name}.json"
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.configs[config_type][config_name], f, indent=2)
            
            # Create backup
            backup_path = self.config_dir / 'backups' / f"{config_name}_{int(time.time())}.json"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.configs[config_type][config_name], f, indent=2)
            
            print(f"✅ Saved {config_type}/{config_name} config")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {config_type}/{config_name}: {e}")
            return False
    
    def reload_config(self, config_type: str, config_name: str):
        """Reload configuration from file"""
        config_path = self.config_dir / config_type / f"{config_name}.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                with self.lock:
                    self.configs[config_type][config_name] = json.load(f)
            
            print(f"✅ Reloaded {config_type}/{config_name} config")
            return True
            
        except Exception as e:
            print(f"❌ Failed to reload {config_type}/{config_name}: {e}")
            return False
    
    def list_configs(self, config_type: str = None) -> Dict[str, list]:
        """List all configurations"""
        if config_type:
            if config_type in self.configs:
                return {config_type: list(self.configs[config_type].keys())}
            else:
                return {config_type: []}
        
        return {ct: list(configs.keys()) for ct, configs in self.configs.items()}
    
    def delete_config(self, config_type: str, config_name: str):
        """Delete configuration"""
        with self.lock:
            if config_type in self.configs and config_name in self.configs[config_type]:
                del self.configs[config_type][config_name]
                
                # Delete file
                config_path = self.config_dir / config_type / f"{config_name}.json"
                if config_path.exists():
                    config_path.unlink()
                
                print(f"✅ Deleted {config_type}/{config_name} config")
                return True
        
        return False

# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions
def get_config(config_type: str, config_name: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get_config(config_type, config_name, default)

def set_config(config_type: str, config_name: str, value: Any):
    """Set configuration value"""
    return config_manager.set_config(config_type, config_name, value)

def reload_config(config_type: str, config_name: str):
    """Reload configuration from file"""
    return config_manager.reload_config(config_type, config_name)

if __name__ == '__main__':
    print("🚀 STELLAR LOGIC AI CONFIGURATION MANAGER")
    print(f"📊 Configurations loaded: {config_manager.list_configs()}")
    print(f"📁 Config directory: {config_manager.config_dir}")
