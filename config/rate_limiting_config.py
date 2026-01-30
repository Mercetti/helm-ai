"""
Rate Limiting Configuration for Helm AI
Environment-specific rate limiting configurations
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    name: str
    limit_type: str  # ip_based, user_based, api_key_based, endpoint_based, global
    algorithm: str  # token_bucket, sliding_window, fixed_window, leaky_bucket
    requests_per_window: int
    window_seconds: int
    burst_size: int = 0
    priority: int = 1
    enabled: bool = True
    endpoints: List[str] = None
    ip_whitelist: List[str] = None
    user_whitelist: List[str] = None
    metadata: Dict[str, Any] = None

class RateLimitingConfig:
    """Rate limiting configuration manager"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.config = self._get_environment_config()
    
    def _get_environment_config(self) -> Dict[str, Any]:
        """Get configuration based on environment"""
        
        if self.environment == Environment.DEVELOPMENT:
            return self._development_config()
        elif self.environment == Environment.TESTING:
            return self._testing_config()
        elif self.environment == Environment.STAGING:
            return self._staging_config()
        elif self.environment == Environment.PRODUCTION:
            return self._production_config()
        else:
            return self._development_config()
    
    def _development_config(self) -> Dict[str, Any]:
        """Development environment configuration"""
        return {
            "enabled": True,
            "strict_mode": False,  # More lenient for development
            "log_violations": True,
            "block_violations": False,  # Don't block in development
            "redis_enabled": False,  # Use in-memory for development
            "cleanup_interval": 300,  # 5 minutes
            "default_window": 60,
            "default_limit": 1000,
            "rules": [
                # Global limits - very permissive
                RateLimitRule(
                    name="global_rate_limit",
                    limit_type="global",
                    algorithm="sliding_window",
                    requests_per_window=10000,
                    window_seconds=60,
                    priority=1,
                    metadata={"environment": "development"}
                ),
                
                # IP-based limits - permissive
                RateLimitRule(
                    name="ip_rate_limit",
                    limit_type="ip_based",
                    algorithm="token_bucket",
                    requests_per_window=1000,
                    window_seconds=60,
                    burst_size=200,
                    priority=2,
                    metadata={"environment": "development"}
                ),
                
                # User-based limits - permissive
                RateLimitRule(
                    name="user_rate_limit",
                    limit_type="user_based",
                    algorithm="sliding_window",
                    requests_per_window=2000,
                    window_seconds=60,
                    priority=3,
                    metadata={"environment": "development"}
                ),
                
                # API key limits - permissive
                RateLimitRule(
                    name="api_key_rate_limit",
                    limit_type="api_key_based",
                    algorithm="token_bucket",
                    requests_per_window=5000,
                    window_seconds=60,
                    burst_size=500,
                    priority=4,
                    metadata={"environment": "development"}
                ),
                
                # Endpoint-specific limits - very permissive
                RateLimitRule(
                    name="auth_endpoints",
                    limit_type="endpoint_based",
                    algorithm="fixed_window",
                    requests_per_window=100,
                    window_seconds=60,
                    endpoints=["/api/auth/login", "/api/auth/register", "/api/auth/refresh"],
                    priority=5,
                    metadata={"environment": "development", "category": "authentication"}
                ),
                
                RateLimitRule(
                    name="api_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=2000,
                    window_seconds=60,
                    endpoints=["/api/analytics", "/api/projects", "/api/reports"],
                    priority=6,
                    metadata={"environment": "development", "category": "data"}
                ),
                
                RateLimitRule(
                    name="upload_endpoints",
                    limit_type="endpoint_based",
                    algorithm="token_bucket",
                    requests_per_window=50,
                    window_seconds=60,
                    burst_size=10,
                    endpoints=["/api/files/upload", "/api/import/data"],
                    priority=7,
                    metadata={"environment": "development", "category": "upload"}
                )
            ]
        }
    
    def _testing_config(self) -> Dict[str, Any]:
        """Testing environment configuration"""
        return {
            "enabled": True,
            "strict_mode": False,
            "log_violations": True,
            "block_violations": False,
            "redis_enabled": False,
            "cleanup_interval": 60,  # 1 minute for testing
            "default_window": 60,
            "default_limit": 500,
            "rules": [
                # Global limits - moderate for testing
                RateLimitRule(
                    name="global_rate_limit",
                    limit_type="global",
                    algorithm="sliding_window",
                    requests_per_window=5000,
                    window_seconds=60,
                    priority=1,
                    metadata={"environment": "testing"}
                ),
                
                # IP-based limits - moderate
                RateLimitRule(
                    name="ip_rate_limit",
                    limit_type="ip_based",
                    algorithm="token_bucket",
                    requests_per_window=500,
                    window_seconds=60,
                    burst_size=100,
                    priority=2,
                    metadata={"environment": "testing"}
                ),
                
                # User-based limits - moderate
                RateLimitRule(
                    name="user_rate_limit",
                    limit_type="user_based",
                    algorithm="sliding_window",
                    requests_per_window=1000,
                    window_seconds=60,
                    priority=3,
                    metadata={"environment": "testing"}
                ),
                
                # API key limits - moderate
                RateLimitRule(
                    name="api_key_rate_limit",
                    limit_type="api_key_based",
                    algorithm="token_bucket",
                    requests_per_window=2000,
                    window_seconds=60,
                    burst_size=200,
                    priority=4,
                    metadata={"environment": "testing"}
                ),
                
                # Endpoint-specific limits - testing focused
                RateLimitRule(
                    name="auth_endpoints",
                    limit_type="endpoint_based",
                    algorithm="fixed_window",
                    requests_per_window=50,
                    window_seconds=60,
                    endpoints=["/api/auth/login", "/api/auth/register", "/api/auth/refresh"],
                    priority=5,
                    metadata={"environment": "testing", "category": "authentication"}
                ),
                
                RateLimitRule(
                    name="test_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=1000,
                    window_seconds=60,
                    endpoints=["/api/test/*", "/api/debug/*"],
                    priority=6,
                    metadata={"environment": "testing", "category": "testing"}
                )
            ]
        }
    
    def _staging_config(self) -> Dict[str, Any]:
        """Staging environment configuration"""
        return {
            "enabled": True,
            "strict_mode": True,
            "log_violations": True,
            "block_violations": True,
            "redis_enabled": True,
            "cleanup_interval": 600,  # 10 minutes
            "default_window": 60,
            "default_limit": 100,
            "rules": [
                # Global limits - production-like
                RateLimitRule(
                    name="global_rate_limit",
                    limit_type="global",
                    algorithm="sliding_window",
                    requests_per_window=1000,
                    window_seconds=60,
                    priority=1,
                    metadata={"environment": "staging"}
                ),
                
                # IP-based limits - production-like
                RateLimitRule(
                    name="ip_rate_limit",
                    limit_type="ip_based",
                    algorithm="token_bucket",
                    requests_per_window=100,
                    window_seconds=60,
                    burst_size=20,
                    priority=2,
                    metadata={"environment": "staging"}
                ),
                
                # User-based limits - production-like
                RateLimitRule(
                    name="user_rate_limit",
                    limit_type="user_based",
                    algorithm="sliding_window",
                    requests_per_window=200,
                    window_seconds=60,
                    priority=3,
                    metadata={"environment": "staging"}
                ),
                
                # API key limits - production-like
                RateLimitRule(
                    name="api_key_rate_limit",
                    limit_type="api_key_based",
                    algorithm="token_bucket",
                    requests_per_window=500,
                    window_seconds=60,
                    burst_size=50,
                    priority=4,
                    metadata={"environment": "staging"}
                ),
                
                # Endpoint-specific limits - production-like
                RateLimitRule(
                    name="auth_endpoints",
                    limit_type="endpoint_based",
                    algorithm="fixed_window",
                    requests_per_window=20,
                    window_seconds=60,
                    endpoints=["/api/auth/login", "/api/auth/register", "/api/auth/refresh"],
                    priority=5,
                    metadata={"environment": "staging", "category": "authentication"}
                ),
                
                RateLimitRule(
                    name="api_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=200,
                    window_seconds=60,
                    endpoints=["/api/analytics", "/api/projects", "/api/reports"],
                    priority=6,
                    metadata={"environment": "staging", "category": "data"}
                ),
                
                RateLimitRule(
                    name="upload_endpoints",
                    limit_type="endpoint_based",
                    algorithm="token_bucket",
                    requests_per_window=10,
                    window_seconds=60,
                    burst_size=5,
                    endpoints=["/api/files/upload", "/api/import/data"],
                    priority=7,
                    metadata={"environment": "staging", "category": "upload"}
                ),
                
                RateLimitRule(
                    name="export_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=5,
                    window_seconds=300,  # 5 minutes
                    endpoints=["/api/export/*", "/api/reports/generate"],
                    priority=8,
                    metadata={"environment": "staging", "category": "export"}
                )
            ]
        }
    
    def _production_config(self) -> Dict[str, Any]:
        """Production environment configuration"""
        return {
            "enabled": True,
            "strict_mode": True,
            "log_violations": True,
            "block_violations": True,
            "redis_enabled": True,
            "cleanup_interval": 900,  # 15 minutes
            "default_window": 60,
            "default_limit": 100,
            "rules": [
                # Global limits - strict
                RateLimitRule(
                    name="global_rate_limit",
                    limit_type="global",
                    algorithm="sliding_window",
                    requests_per_window=1000,
                    window_seconds=60,
                    priority=1,
                    metadata={"environment": "production"}
                ),
                
                # IP-based limits - strict
                RateLimitRule(
                    name="ip_rate_limit",
                    limit_type="ip_based",
                    algorithm="token_bucket",
                    requests_per_window=100,
                    window_seconds=60,
                    burst_size=20,
                    priority=2,
                    metadata={"environment": "production"}
                ),
                
                # User-based limits - strict
                RateLimitRule(
                    name="user_rate_limit",
                    limit_type="user_based",
                    algorithm="sliding_window",
                    requests_per_window=200,
                    window_seconds=60,
                    priority=3,
                    metadata={"environment": "production"}
                ),
                
                # API key limits - strict
                RateLimitRule(
                    name="api_key_rate_limit",
                    limit_type="api_key_based",
                    algorithm="token_bucket",
                    requests_per_window=500,
                    window_seconds=60,
                    burst_size=50,
                    priority=4,
                    metadata={"environment": "production"}
                ),
                
                # Critical endpoints - very strict
                RateLimitRule(
                    name="auth_endpoints",
                    limit_type="endpoint_based",
                    algorithm="fixed_window",
                    requests_per_window=10,
                    window_seconds=60,
                    endpoints=["/api/auth/login", "/api/auth/register", "/api/auth/refresh"],
                    priority=5,
                    metadata={"environment": "production", "category": "authentication", "critical": True}
                ),
                
                RateLimitRule(
                    name="password_reset",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=3,
                    window_seconds=300,  # 5 minutes
                    endpoints=["/api/auth/password/reset", "/api/auth/forgot-password"],
                    priority=5,
                    metadata={"environment": "production", "category": "security", "critical": True}
                ),
                
                # API endpoints - moderate
                RateLimitRule(
                    name="api_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=200,
                    window_seconds=60,
                    endpoints=["/api/analytics", "/api/projects", "/api/reports"],
                    priority=6,
                    metadata={"environment": "production", "category": "data"}
                ),
                
                # Upload endpoints - strict
                RateLimitRule(
                    name="upload_endpoints",
                    limit_type="endpoint_based",
                    algorithm="token_bucket",
                    requests_per_window=10,
                    window_seconds=60,
                    burst_size=5,
                    endpoints=["/api/files/upload", "/api/import/data"],
                    priority=7,
                    metadata={"environment": "production", "category": "upload"}
                ),
                
                # Export endpoints - very strict
                RateLimitRule(
                    name="export_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=3,
                    window_seconds=300,  # 5 minutes
                    endpoints=["/api/export/*", "/api/reports/generate"],
                    priority=8,
                    metadata={"environment": "production", "category": "export"}
                ),
                
                # Admin endpoints - very strict
                RateLimitRule(
                    name="admin_endpoints",
                    limit_type="endpoint_based",
                    algorithm="sliding_window",
                    requests_per_window=50,
                    window_seconds=60,
                    endpoints=["/api/admin/*"],
                    priority=9,
                    metadata={"environment": "production", "category": "admin"}
                ),
                
                # Webhook endpoints - moderate
                RateLimitRule(
                    name="webhook_endpoints",
                    limit_type="endpoint_based",
                    algorithm="token_bucket",
                    requests_per_window=1000,
                    window_seconds=60,
                    burst_size=200,
                    endpoints=["/api/webhooks/*"],
                    priority=10,
                    metadata={"environment": "production", "category": "webhooks"}
                )
            ]
        }
    
    def get_rules(self) -> List[RateLimitRule]:
        """Get all rate limit rules for current environment"""
        return self.config.get("rules", [])
    
    def get_rule(self, name: str) -> RateLimitRule:
        """Get specific rule by name"""
        for rule in self.get_rules():
            if rule.name == name:
                return rule
        raise ValueError(f"Rule '{name}' not found")
    
    def is_enabled(self) -> bool:
        """Check if rate limiting is enabled"""
        return self.config.get("enabled", True)
    
    def is_strict_mode(self) -> bool:
        """Check if strict mode is enabled"""
        return self.config.get("strict_mode", True)
    
    def should_block_violations(self) -> bool:
        """Check if violations should be blocked"""
        return self.config.get("block_violations", True)
    
    def should_log_violations(self) -> bool:
        """Check if violations should be logged"""
        return self.config.get("log_violations", True)
    
    def is_redis_enabled(self) -> bool:
        """Check if Redis is enabled for rate limiting"""
        return self.config.get("redis_enabled", True)
    
    def get_cleanup_interval(self) -> int:
        """Get cleanup interval in seconds"""
        return self.config.get("cleanup_interval", 600)
    
    def get_default_window(self) -> int:
        """Get default window in seconds"""
        return self.config.get("default_window", 60)
    
    def get_default_limit(self) -> int:
        """Get default limit"""
        return self.config.get("default_limit", 100)
    
    def add_rule(self, rule: RateLimitRule) -> None:
        """Add a new rule to the configuration"""
        self.config["rules"].append(rule)
    
    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name"""
        rules = self.config.get("rules", [])
        original_length = len(rules)
        self.config["rules"] = [rule for rule in rules if rule.name != name]
        return len(self.config["rules"]) < original_length
    
    def update_rule(self, name: str, **kwargs) -> bool:
        """Update a rule by name"""
        for rule in self.config.get("rules", []):
            if rule.name == name:
                for key, value in kwargs.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                return True
        return False
    
    def get_rules_by_type(self, limit_type: str) -> List[RateLimitRule]:
        """Get rules by limit type"""
        return [rule for rule in self.get_rules() if rule.limit_type == limit_type]
    
    def get_rules_by_endpoint(self, endpoint: str) -> List[RateLimitRule]:
        """Get rules that apply to a specific endpoint"""
        applicable_rules = []
        for rule in self.get_rules():
            if rule.endpoints:
                for rule_endpoint in rule.endpoints:
                    if rule_endpoint.endswith("/*"):
                        # Wildcard endpoint
                        if endpoint.startswith(rule_endpoint[:-1]):
                            applicable_rules.append(rule)
                            break
                    else:
                        # Exact match
                        if endpoint == rule_endpoint:
                            applicable_rules.append(rule)
                            break
        return applicable_rules
    
    def get_critical_rules(self) -> List[RateLimitRule]:
        """Get critical rules (those marked as critical)"""
        return [rule for rule in self.get_rules() 
                if rule.metadata and rule.metadata.get("critical", False)]
    
    def export_config(self) -> Dict[str, Any]:
        """Export the entire configuration"""
        return {
            "environment": self.environment.value,
            "config": self.config
        }
    
    def validate_config(self) -> List[str]:
        """Validate the configuration and return any issues"""
        issues = []
        
        # Check if rate limiting is enabled
        if not self.is_enabled():
            issues.append("Rate limiting is disabled")
        
        # Check if there are any rules
        rules = self.get_rules()
        if not rules:
            issues.append("No rate limit rules defined")
        
        # Check rule priorities
        priorities = [rule.priority for rule in rules]
        if len(set(priorities)) != len(priorities):
            issues.append("Duplicate rule priorities found")
        
        # Check for invalid algorithms
        valid_algorithms = ["token_bucket", "sliding_window", "fixed_window", "leaky_bucket"]
        for rule in rules:
            if rule.algorithm not in valid_algorithms:
                issues.append(f"Invalid algorithm '{rule.algorithm}' in rule '{rule.name}'")
        
        # Check for invalid limit types
        valid_limit_types = ["ip_based", "user_based", "api_key_based", "endpoint_based", "global"]
        for rule in rules:
            if rule.limit_type not in valid_limit_types:
                issues.append(f"Invalid limit type '{rule.limit_type}' in rule '{rule.name}'")
        
        # Check window and limit values
        for rule in rules:
            if rule.requests_per_window <= 0:
                issues.append(f"Invalid requests_per_window '{rule.requests_per_window}' in rule '{rule.name}'")
            if rule.window_seconds <= 0:
                issues.append(f"Invalid window_seconds '{rule.window_seconds}' in rule '{rule.name}'")
            if rule.burst_size < 0:
                issues.append(f"Invalid burst_size '{rule.burst_size}' in rule '{rule.name}'")
        
        return issues

# Environment detection helper
def detect_environment() -> Environment:
    """Detect the current environment"""
    env = os.getenv('ENVIRONMENT', os.getenv('FLASK_ENV', 'development')).lower()
    
    if env in ['prod', 'production']:
        return Environment.PRODUCTION
    elif env in ['staging', 'stage']:
        return Environment.STAGING
    elif env in ['test', 'testing']:
        return Environment.TESTING
    else:
        return Environment.DEVELOPMENT

# Configuration factory
def create_rate_limit_config(environment: str = None) -> RateLimitingConfig:
    """Create rate limiting configuration for the specified environment"""
    if environment is None:
        environment = detect_environment().value
    
    env_enum = Environment(environment.lower())
    return RateLimitingConfig(env_enum)

# Default configuration getter
def get_rate_limit_config() -> RateLimitingConfig:
    """Get the rate limiting configuration for the current environment"""
    return create_rate_limit_config()
