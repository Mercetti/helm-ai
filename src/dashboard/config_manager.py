#!/usr/bin/env python3
"""
Configuration Management System - Clean Version
Environment-specific configuration management with encryption and validation
"""

import os
import sys
import time
import json
import logging
import threading
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigType(Enum):
    DATABASE = "database"
    SECURITY = "security"
    API = "api"
    MONITORING = "monitoring"
    LOGGING = "logging"
    CACHE = "cache"
    EMAIL = "email"
    STORAGE = "storage"

class ConfigStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    PENDING = "pending"

@dataclass
class Configuration:
    """Configuration data structure"""
    config_id: str
    name: str
    environment: Environment
    config_type: ConfigType
    key: str
    value: str
    is_encrypted: bool
    description: str
    validation_rules: List[str]
    default_value: str
    status: ConfigStatus
    created_at: datetime
    updated_at: datetime
    updated_by: str
    version: int

@dataclass
class ConfigTemplate:
    """Configuration template data structure"""
    template_id: str
    name: str
    description: str
    config_type: ConfigType
    environments: List[Environment]
    default_values: Dict[str, str]
    validation_rules: Dict[str, List[str]]
    required_fields: List[str]
    sensitive_fields: List[str]

@dataclass
class ConfigChange:
    """Configuration change data structure"""
    change_id: str
    config_id: str
    old_value: str
    new_value: str
    changed_by: str
    changed_at: datetime
    environment: Environment
    reason: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]

class ConfigurationManager:
    """Configuration Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger("configuration_manager")
        self.configurations = {}
        self.config_templates = {}
        self.config_changes = deque(maxlen=1000)
        self.encryption_key = os.getenv('CONFIG_ENCRYPTION_KEY', 'default-key-change-in-production')
        self.validation_rules = {}
        self.approval_required = True
        
        # Initialize with sample configurations and templates
        self._initialize_config_templates()
        self._initialize_configurations()
        self._initialize_config_changes()
        self._initialize_validation_rules()
    
    def _initialize_config_templates(self):
        """Initialize with sample configuration templates"""
        templates = [
            {
                "template_id": "database_template_001",
                "name": "Database Configuration Template",
                "description": "Database connection and performance settings",
                "config_type": ConfigType.DATABASE,
                "environments": [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION],
                "default_values": {
                    "db_host": "localhost",
                    "db_port": "5432",
                    "db_name": "stellarlogic",
                    "db_username": "stellarlogic_user",
                    "db_password": "",
                    "db_ssl_mode": "require",
                    "db_pool_size": "20",
                    "db_timeout": "30",
                    "db_max_connections": "100"
                },
                "validation_rules": {
                    "db_port": ["required", "integer", "min:1", "max:65535"],
                    "db_pool_size": ["required", "integer", "min:1", "max:100"],
                    "db_timeout": ["required", "integer", "min:1", "max:300"],
                    "db_max_connections": ["required", "integer", "min:1", "max:1000"],
                    "db_ssl_mode": ["required", "in:disable,prefer,require,verify-ca,verify-full"]
                },
                "required_fields": ["db_host", "db_port", "db_name", "db_username"],
                "sensitive_fields": ["db_password"]
            },
            {
                "template_id": "security_template_002",
                "name": "Security Configuration Template",
                "description": "Security and authentication settings",
                "config_type": ConfigType.SECURITY,
                "environments": [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION],
                "default_values": {
                    "jwt_secret": "",
                    "jwt_expiry": "3600",
                    "session_timeout": "1800",
                    "max_login_attempts": "5",
                    "lockout_duration": "900",
                    "password_min_length": "8",
                    "password_require_special": "true",
                    "mfa_required": "false",
                    "api_rate_limit": "1000",
                    "cors_origins": "[]"
                },
                "validation_rules": {
                    "jwt_expiry": ["required", "integer", "min:300", "max:86400"],
                    "session_timeout": ["required", "integer", "min:300", "max:7200"],
                    "max_login_attempts": ["required", "integer", "min:3", "max:10"],
                    "lockout_duration": ["required", "integer", "min:300", "max:3600"],
                    "password_min_length": ["required", "integer", "min:6", "max:128"],
                    "api_rate_limit": ["required", "integer", "min:100", "max:10000"]
                },
                "required_fields": ["jwt_secret", "jwt_expiry", "session_timeout"],
                "sensitive_fields": ["jwt_secret"]
            },
            {
                "template_id": "api_template_003",
                "name": "API Configuration Template",
                "description": "API server and endpoint settings",
                "config_type": ConfigType.API,
                "environments": [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION],
                "default_values": {
                    "api_host": "0.0.0.0",
                    "api_port": "8000",
                    "api_workers": "4",
                    "api_debug": "false",
                    "api_log_level": "INFO",
                    "api_cors_enabled": "true",
                    "api_rate_limit": "1000",
                    "api_timeout": "30",
                    "api_max_request_size": "10485760",
                    "api_trusted_proxies": "[]"
                },
                "validation_rules": {
                    "api_port": ["required", "integer", "min:1", "max:65535"],
                    "api_workers": ["required", "integer", "min:1", "max:32"],
                    "api_rate_limit": ["required", "integer", "min:100", "max:10000"],
                    "api_timeout": ["required", "integer", "min:5", "max:300"],
                    "api_max_request_size": ["required", "integer", "min:1024", "max:104857600"],
                    "api_log_level": ["required", "in:DEBUG,INFO,WARNING,ERROR,CRITICAL"]
                },
                "required_fields": ["api_host", "api_port", "api_workers"],
                "sensitive_fields": []
            },
            {
                "template_id": "monitoring_template_004",
                "name": "Monitoring Configuration Template",
                "description": "Monitoring and alerting settings",
                "config_type": ConfigType.MONITORING,
                "environments": [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION],
                "default_values": {
                    "monitoring_enabled": "true",
                    "metrics_port": "9090",
                    "health_check_interval": "30",
                    "alert_webhook_url": "",
                    "alert_email_recipients": "[]",
                    "alert_slack_webhook": "",
                    "performance_threshold_cpu": "80",
                    "performance_threshold_memory": "85",
                    "performance_threshold_disk": "90",
                    "log_retention_days": "30"
                },
                "validation_rules": {
                    "metrics_port": ["required", "integer", "min:1", "max:65535"],
                    "health_check_interval": ["required", "integer", "min:10", "max:300"],
                    "performance_threshold_cpu": ["required", "integer", "min:50", "max:95"],
                    "performance_threshold_memory": ["required", "integer", "min:50", "max:95"],
                    "performance_threshold_disk": ["required", "integer", "min:50", "max:95"],
                    "log_retention_days": ["required", "integer", "min:1", "max:365"]
                },
                "required_fields": ["monitoring_enabled", "metrics_port", "health_check_interval"],
                "sensitive_fields": ["alert_webhook_url", "alert_slack_webhook"]
            }
        ]
        
        for template_data in templates:
            template = ConfigTemplate(**template_data)
            self.config_templates[template.template_id] = template
        
        self.logger.info(f"Initialized {len(templates)} configuration templates")
    
    def _initialize_configurations(self):
        """Initialize with sample configurations"""
        configurations = [
            {
                "config_id": "db_prod_host_001",
                "name": "Production Database Host",
                "environment": Environment.PRODUCTION,
                "config_type": ConfigType.DATABASE,
                "key": "db_host",
                "value": "db.stellarlogica.ai",
                "is_encrypted": False,
                "description": "Production database hostname",
                "validation_rules": ["required", "hostname"],
                "default_value": "localhost",
                "status": ConfigStatus.ACTIVE,
                "created_at": datetime.now() - timedelta(days=365),
                "updated_at": datetime.now() - timedelta(days=30),
                "updated_by": "admin",
                "version": 1
            },
            {
                "config_id": "db_prod_password_002",
                "name": "Production Database Password",
                "environment": Environment.PRODUCTION,
                "config_type": ConfigType.DATABASE,
                "key": "db_password",
                "value": "encrypted:U2FsdGVkX1+encrypted_password_hash",
                "is_encrypted": True,
                "description": "Production database password (encrypted)",
                "validation_rules": ["required", "min_length:16"],
                "default_value": "",
                "status": ConfigStatus.ACTIVE,
                "created_at": datetime.now() - timedelta(days=365),
                "updated_at": datetime.now() - timedelta(days=7),
                "updated_by": "admin",
                "version": 3
            },
            {
                "config_id": "security_jwt_secret_003",
                "name": "JWT Secret Key",
                "environment": Environment.PRODUCTION,
                "config_type": ConfigType.SECURITY,
                "key": "jwt_secret",
                "value": "encrypted:U2FsdGVkX1+jwt_secret_key_hash",
                "is_encrypted": True,
                "description": "JWT signing secret (encrypted)",
                "validation_rules": ["required", "min_length:32"],
                "default_value": "",
                "status": ConfigStatus.ACTIVE,
                "created_at": datetime.now() - timedelta(days=365),
                "updated_at": datetime.now() - timedelta(days=90),
                "updated_by": "security_admin",
                "version": 2
            },
            {
                "config_id": "api_prod_port_004",
                "name": "Production API Port",
                "environment": Environment.PRODUCTION,
                "config_type": ConfigType.API,
                "key": "api_port",
                "value": "8000",
                "is_encrypted": False,
                "description": "Production API server port",
                "validation_rules": ["required", "integer", "min:1", "max:65535"],
                "default_value": "8000",
                "status": ConfigStatus.ACTIVE,
                "created_at": datetime.now() - timedelta(days=365),
                "updated_at": datetime.now() - timedelta(days=180),
                "updated_by": "admin",
                "version": 1
            },
            {
                "config_id": "monitoring_enabled_005",
                "name": "Monitoring Enabled",
                "environment": Environment.PRODUCTION,
                "config_type": ConfigType.MONITORING,
                "key": "monitoring_enabled",
                "value": "true",
                "is_encrypted": False,
                "description": "Enable/disable monitoring system",
                "validation_rules": ["required", "boolean"],
                "default_value": "true",
                "status": ConfigStatus.ACTIVE,
                "created_at": datetime.now() - timedelta(days=365),
                "updated_at": datetime.now() - timedelta(days=60),
                "updated_by": "ops_admin",
                "version": 1
            }
        ]
        
        for config_data in configurations:
            config = Configuration(**config_data)
            self.configurations[config.config_id] = config
        
        self.logger.info(f"Initialized {len(configurations)} configurations")
    
    def _initialize_config_changes(self):
        """Initialize with sample configuration changes"""
        changes = [
            {
                "change_id": "change_001",
                "config_id": "db_prod_password_002",
                "old_value": "encrypted:U2FsdGVkX1+old_password_hash",
                "new_value": "encrypted:U2FsdGVkX1+new_password_hash",
                "changed_by": "admin",
                "changed_at": datetime.now() - timedelta(days=7),
                "environment": Environment.PRODUCTION,
                "reason": "Regular password rotation",
                "approved_by": "security_admin",
                "approved_at": datetime.now() - timedelta(days=7, hours=1)
            },
            {
                "change_id": "change_002",
                "config_id": "security_jwt_secret_003",
                "old_value": "encrypted:U2FsdGVkX1+old_jwt_secret",
                "new_value": "encrypted:U2FsdGVkX1+new_jwt_secret",
                "changed_by": "security_admin",
                "changed_at": datetime.now() - timedelta(days=90),
                "environment": Environment.PRODUCTION,
                "reason": "JWT secret rotation for security",
                "approved_by": "cto",
                "approved_at": datetime.now() - timedelta(days=90, hours=2)
            },
            {
                "change_id": "change_003",
                "config_id": "api_prod_port_004",
                "old_value": "8000",
                "new_value": "8443",
                "changed_by": "ops_admin",
                "changed_at": datetime.now() - timedelta(days=180),
                "environment": Environment.PRODUCTION,
                "reason": "Port change to avoid conflicts",
                "approved_by": "admin",
                "approved_at": datetime.now() - timedelta(days=180, hours=3)
            }
        ]
        
        for change_data in changes:
            change = ConfigChange(**change_data)
            self.config_changes.append(change)
        
        self.logger.info(f"Initialized {len(changes)} configuration changes")
    
    def _initialize_validation_rules(self):
        """Initialize validation rules"""
        self.validation_rules = {
            "required": lambda value: value is not None and str(value).strip() != "",
            "integer": lambda value: str(value).isdigit() if str(value).isdigit() else False,
            "float": lambda value: self._is_float(value),
            "boolean": lambda value: str(value).lower() in ["true", "false", "1", "0"],
            "email": lambda value: "@" in str(value) and "." in str(value).split("@")[1],
            "url": lambda value: str(value).startswith(("http://", "https://")),
            "hostname": lambda value: self._is_valid_hostname(str(value)),
            "ip_address": lambda value: self._is_valid_ip(str(value)),
            "min_length": lambda value, min_len: len(str(value)) >= min_len,
            "max_length": lambda value, max_len: len(str(value)) <= max_len,
            "min": lambda value, min_val: float(str(value)) >= min_val,
            "max": lambda value, max_val: float(str(value)) <= max_val,
            "in": lambda value, options: str(value) in [opt.strip() for opt in options.split(",")]
        }
        
        self.logger.info("Initialized validation rules")
    
    def get_configuration(self, environment: str, config_type: str = None, key: str = None) -> Dict[str, Any]:
        """Get configuration by environment and type"""
        try:
            env = Environment(environment)
            
            configs = list(self.configurations.values())
            configs = [c for c in configs if c.environment == env]
            
            if config_type:
                configs = [c for c in configs if c.config_type.value == config_type]
            
            if key:
                configs = [c for c in configs if c.key == key]
            
            # Decrypt encrypted values
            result_configs = []
            for config in configs:
                config_dict = asdict(config)
                if config.is_encrypted:
                    config_dict["value"] = self._decrypt_value(config.value)
                result_configs.append(config_dict)
            
            return {
                "environment": environment,
                "config_type": config_type,
                "key": key,
                "configurations": result_configs,
                "total_count": len(result_configs)
            }
            
        except Exception as e:
            self.logger.error(f"Get configuration error: {e}")
            return {"error": "Failed to get configuration"}
    
    def set_configuration(self, environment: str, config_type: str, key: str, value: str, 
                          description: str = "", is_encrypted: bool = False, updated_by: str = "system") -> Dict[str, Any]:
        """Set configuration value"""
        try:
            env = Environment(environment)
            ct = ConfigType(config_type)
            
            # Validate configuration
            validation_result = self._validate_configuration(key, value, ct)
            if not validation_result["valid"]:
                return {"success": False, "error": f"Validation failed: {validation_result['error']}"}
            
            # Check if configuration exists
            existing_config = None
            for config in self.configurations.values():
                if config.environment == env and config.config_type == ct and config.key == key:
                    existing_config = config
                    break
            
            # Encrypt value if needed
            final_value = self._encrypt_value(value) if is_encrypted else value
            
            if existing_config:
                # Update existing configuration
                old_value = existing_config.value
                existing_config.value = final_value
                existing_config.is_encrypted = is_encrypted
                existing_config.description = description or existing_config.description
                existing_config.updated_at = datetime.now()
                existing_config.updated_by = updated_by
                existing_config.version += 1
                
                # Record change
                change_id = f"change_{int(time.time())}"
                change = ConfigChange(
                    change_id=change_id,
                    config_id=existing_config.config_id,
                    old_value=old_value,
                    new_value=final_value,
                    changed_by=updated_by,
                    changed_at=datetime.now(),
                    environment=env,
                    reason="Configuration update",
                    approved_by=None,
                    approved_at=None
                )
                self.config_changes.append(change)
                
                return {
                    "success": True,
                    "config_id": existing_config.config_id,
                    "action": "updated",
                    "version": existing_config.version,
                    "change_id": change_id
                }
            else:
                # Create new configuration
                config_id = f"config_{int(time.time())}"
                config = Configuration(
                    config_id=config_id,
                    name=f"{key.title()} Configuration",
                    environment=env,
                    config_type=ct,
                    key=key,
                    value=final_value,
                    is_encrypted=is_encrypted,
                    description=description,
                    validation_rules=[],
                    default_value="",
                    status=ConfigStatus.ACTIVE,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    updated_by=updated_by,
                    version=1
                )
                
                self.configurations[config_id] = config
                
                return {
                    "success": True,
                    "config_id": config_id,
                    "action": "created",
                    "version": 1
                }
                
        except Exception as e:
            self.logger.error(f"Set configuration error: {e}")
            return {"success": False, "error": "Failed to set configuration"}
    
    def get_config_template(self, template_id: str = None) -> Dict[str, Any]:
        """Get configuration template"""
        if template_id:
            template = self.config_templates.get(template_id)
            if template:
                return asdict(template)
            else:
                return {"error": "Template not found"}
        
        return {
            "total_templates": len(self.config_templates),
            "templates": [asdict(template) for template in self.config_templates.values()]
        }
    
    def apply_template(self, template_id: str, environment: str, values: Dict[str, str], 
                       updated_by: str = "system") -> Dict[str, Any]:
        """Apply configuration template"""
        try:
            template = self.config_templates.get(template_id)
            if not template:
                return {"success": False, "error": "Template not found"}
            
            env = Environment(environment)
            
            # Validate environment
            if env not in template.environments:
                return {"success": False, "error": f"Template not available for environment: {environment}"}
            
            # Merge default values with provided values
            final_values = template.default_values.copy()
            final_values.update(values)
            
            # Apply configurations
            results = []
            errors = []
            
            for key, value in final_values.items():
                is_encrypted = key in template.sensitive_fields
                description = f"Configuration from template: {template.name}"
                
                result = self.set_configuration(
                    environment=environment,
                    config_type=template.config_type.value,
                    key=key,
                    value=value,
                    description=description,
                    is_encrypted=is_encrypted,
                    updated_by=updated_by
                )
                
                if result["success"]:
                    results.append({
                        "key": key,
                        "config_id": result.get("config_id"),
                        "action": result.get("action"),
                        "version": result.get("version")
                    })
                else:
                    errors.append({"key": key, "error": result.get("error")})
            
            return {
                "success": len(errors) == 0,
                "template_id": template_id,
                "environment": environment,
                "applied_count": len(results),
                "results": results,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"Apply template error: {e}")
            return {"success": False, "error": "Failed to apply template"}
    
    def get_config_changes(self, environment: str = None, config_id: str = None, 
                           days: int = 30) -> Dict[str, Any]:
        """Get configuration changes"""
        try:
            changes = list(self.config_changes)
            
            if environment:
                env = Environment(environment)
                changes = [c for c in changes if c.environment == env]
            
            if config_id:
                changes = [c for c in changes if c.config_id == config_id]
            
            # Filter by time period
            cutoff_date = datetime.now() - timedelta(days=days)
            changes = [c for c in changes if c.changed_at >= cutoff_date]
            
            # Sort by date (newest first)
            changes.sort(key=lambda x: x.changed_at, reverse=True)
            
            return {
                "total_changes": len(changes),
                "environment": environment,
                "config_id": config_id,
                "period_days": days,
                "changes": [asdict(change) for change in changes]
            }
            
        except Exception as e:
            self.logger.error(f"Get config changes error: {e}")
            return {"error": "Failed to get configuration changes"}
    
    def validate_all_configurations(self, environment: str) -> Dict[str, Any]:
        """Validate all configurations for an environment"""
        try:
            env = Environment(environment)
            
            configs = [c for c in self.configurations.values() if c.environment == env]
            
            validation_results = []
            errors = []
            
            for config in configs:
                validation_result = self._validate_configuration(config.key, config.value, config.config_type)
                
                if validation_result["valid"]:
                    validation_results.append({
                        "config_id": config.config_id,
                        "key": config.key,
                        "status": "valid"
                    })
                else:
                    errors.append({
                        "config_id": config.config_id,
                        "key": config.key,
                        "error": validation_result["error"]
                    })
            
            return {
                "environment": environment,
                "total_configurations": len(configs),
                "valid_configurations": len(validation_results),
                "invalid_configurations": len(errors),
                "validation_results": validation_results,
                "errors": errors,
                "overall_status": "valid" if len(errors) == 0 else "invalid"
            }
            
        except Exception as e:
            self.logger.error(f"Validate all configurations error: {e}")
            return {"error": "Failed to validate configurations"}
    
    def _validate_configuration(self, key: str, value: str, config_type: ConfigType) -> Dict[str, Any]:
        """Validate single configuration"""
        try:
            # Get validation rules from template
            rules = []
            for template in self.config_templates.values():
                if template.config_type == config_type and key in template.validation_rules:
                    rules = template.validation_rules[key]
                    break
            
            if not rules:
                return {"valid": True, "message": "No validation rules found"}
            
            # Apply validation rules
            for rule in rules:
                if rule.startswith("min_length:"):
                    min_len = int(rule.split(":")[1])
                    if not self.validation_rules["min_length"](value, min_len):
                        return {"valid": False, "error": f"Value too short (minimum {min_len} characters)"}
                elif rule.startswith("max_length:"):
                    max_len = int(rule.split(":")[1])
                    if not self.validation_rules["max_length"](value, max_len):
                        return {"valid": False, "error": f"Value too long (maximum {max_len} characters)"}
                elif rule.startswith("min:"):
                    min_val = float(rule.split(":")[1])
                    if not self.validation_rules["min"](value, min_val):
                        return {"valid": False, "error": f"Value too small (minimum {min_val})"}
                elif rule.startswith("max:"):
                    max_val = float(rule.split(":")[1])
                    if not self.validation_rules["max"](value, max_val):
                        return {"valid": False, "error": f"Value too large (maximum {max_val})"}
                elif rule.startswith("in:"):
                    options = rule.split(":")[1]
                    if not self.validation_rules["in"](value, options):
                        return {"valid": False, "error": f"Value not in allowed options: {options}"}
                elif rule in self.validation_rules:
                    if not self.validation_rules[rule](value):
                        return {"valid": False, "error": f"Validation failed for rule: {rule}"}
            
            return {"valid": True, "message": "Validation passed"}
            
        except Exception as e:
            self.logger.error(f"Validate configuration error: {e}")
            return {"valid": False, "error": "Validation error"}
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt sensitive value"""
        try:
            import hashlib
            import base64
            
            # Simple encryption for demo (use proper encryption in production)
            key = self.encryption_key.encode()
            value_bytes = value.encode()
            
            # Create hash and encode
            encrypted = hashlib.sha256(key + value_bytes).hexdigest()
            return f"encrypted:{encrypted}"
            
        except Exception as e:
            self.logger.error(f"Encrypt value error: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive value"""
        try:
            if not encrypted_value.startswith("encrypted:"):
                return encrypted_value
            
            # For demo, return placeholder (use proper decryption in production)
            return "[ENCRYPTED_VALUE]"
            
        except Exception as e:
            self.logger.error(f"Decrypt value error: {e}")
            return encrypted_value
    
    def _is_float(self, value) -> bool:
        """Check if value is a valid float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if hostname is valid"""
        import re
        if len(hostname) > 253:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        allowed = re.compile(r"^[a-zA-Z0-9-]{1,63}$")
        return all(allowed.match(x) for x in hostname.split("."))
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

# Global configuration manager instance
configuration_manager = ConfigurationManager()
