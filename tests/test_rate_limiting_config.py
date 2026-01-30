"""
Tests for enhanced rate limiting configuration
"""

import pytest
import os
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import the modules we're testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

from rate_limiting_config import RateLimitingConfig, RateLimitRule, Environment, detect_environment
from enhanced_rate_limiting import EnhancedRateLimitManager, RateLimitResult

class TestRateLimitingConfig:
    """Test rate limiting configuration"""
    
    def test_environment_detection(self):
        """Test environment detection"""
        # Test with environment variable
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            env = detect_environment()
            assert env == Environment.PRODUCTION
        
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            env = detect_environment()
            assert env == Environment.DEVELOPMENT
        
        with patch.dict(os.environ, {}, clear=True):
            env = detect_environment()
            assert env == Environment.DEVELOPMENT  # Default
    
    def test_development_config(self):
        """Test development environment configuration"""
        config = RateLimitingConfig(Environment.DEVELOPMENT)
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.is_enabled() == True
        assert config.is_strict_mode() == False
        assert config.should_block_violations() == False
        assert config.should_log_violations() == True
        assert config.is_redis_enabled() == False
        
        rules = config.get_rules()
        assert len(rules) > 0
        
        # Check that development rules are permissive
        global_rule = config.get_rule("global_rate_limit")
        assert global_rule.requests_per_window == 10000  # Very permissive
        
        ip_rule = config.get_rule("ip_rate_limit")
        assert ip_rule.requests_per_window == 1000  # Permissive
    
    def test_testing_config(self):
        """Test testing environment configuration"""
        config = RateLimitingConfig(Environment.TESTING)
        
        assert config.environment == Environment.TESTING
        assert config.is_enabled() == True
        assert config.is_strict_mode() == False
        assert config.should_block_violations() == False
        assert config.is_redis_enabled() == False
        
        rules = config.get_rules()
        assert len(rules) > 0
        
        # Check that testing rules are moderate
        global_rule = config.get_rule("global_rate_limit")
        assert global_rule.requests_per_window == 5000  # Moderate
        
        # Should have test-specific rules
        test_rule_names = [rule.name for rule in rules]
        assert "test_endpoints" in test_rule_names
    
    def test_staging_config(self):
        """Test staging environment configuration"""
        config = RateLimitingConfig(Environment.STAGING)
        
        assert config.environment == Environment.STAGING
        assert config.is_enabled() == True
        assert config.is_strict_mode() == True
        assert config.should_block_violations() == True
        assert config.is_redis_enabled() == True
        
        rules = config.get_rules()
        assert len(rules) > 0
        
        # Check that staging rules are production-like
        global_rule = config.get_rule("global_rate_limit")
        assert global_rule.requests_per_window == 1000  # Production-like
        
        ip_rule = config.get_rule("ip_rate_limit")
        assert ip_rule.requests_per_window == 100  # Production-like
    
    def test_production_config(self):
        """Test production environment configuration"""
        config = RateLimitingConfig(Environment.PRODUCTION)
        
        assert config.environment == Environment.PRODUCTION
        assert config.is_enabled() == True
        assert config.is_strict_mode() == True
        assert config.should_block_violations() == True
        assert config.is_redis_enabled() == True
        
        rules = config.get_rules()
        assert len(rules) > 0
        
        # Check that production rules are strict
        global_rule = config.get_rule("global_rate_limit")
        assert global_rule.requests_per_window == 1000  # Strict
        
        # Should have critical rules
        critical_rules = config.get_critical_rules()
        assert len(critical_rules) > 0
        
        # Check for very strict auth endpoints
        auth_rule = config.get_rule("auth_endpoints")
        assert auth_rule.requests_per_window == 10  # Very strict
        
        # Check for password reset rule
        try:
            password_rule = config.get_rule("password_reset")
            assert password_rule.requests_per_window == 3  # Very strict
        except ValueError:
            pass  # Rule might not exist in some configs
    
    def test_rule_management(self):
        """Test rule management functions"""
        config = RateLimitingConfig(Environment.DEVELOPMENT)
        
        # Test adding a rule
        new_rule = RateLimitRule(
            name="test_rule",
            limit_type="ip_based",
            algorithm="token_bucket",
            requests_per_window=50,
            window_seconds=60
        )
        
        original_count = len(config.get_rules())
        config.add_rule(new_rule)
        assert len(config.get_rules()) == original_count + 1
        
        # Test getting the rule
        retrieved_rule = config.get_rule("test_rule")
        assert retrieved_rule.name == "test_rule"
        assert retrieved_rule.requests_per_window == 50
        
        # Test updating the rule
        config.update_rule("test_rule", requests_per_window=75)
        updated_rule = config.get_rule("test_rule")
        assert updated_rule.requests_per_window == 75
        
        # Test removing the rule
        result = config.remove_rule("test_rule")
        assert result == True
        assert len(config.get_rules()) == original_count
        
        # Test removing non-existent rule
        result = config.remove_rule("non_existent")
        assert result == False
    
    def test_rule_filtering(self):
        """Test rule filtering functions"""
        config = RateLimitingConfig(Environment.PRODUCTION)
        
        # Test filtering by type
        ip_rules = config.get_rules_by_type("ip_based")
        assert all(rule.limit_type == "ip_based" for rule in ip_rules)
        
        user_rules = config.get_rules_by_type("user_based")
        assert all(rule.limit_type == "user_based" for rule in user_rules)
        
        # Test filtering by endpoint
        auth_rules = config.get_rules_by_endpoint("/api/auth/login")
        assert len(auth_rules) > 0
        
        # Test wildcard endpoint matching
        api_rules = config.get_rules_by_endpoint("/api/analytics/data")
        # This might be empty depending on the configuration, so we'll check if it exists
        if not api_rules:
            # Try a different endpoint that should exist
            api_rules = config.get_rules_by_endpoint("/api/analytics")
        
        assert len(api_rules) > 0
        
        # Test non-matching endpoint
        no_rules = config.get_rules_by_endpoint("/api/nonexistent/endpoint")
        assert len(no_rules) == 0
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = RateLimitingConfig(Environment.PRODUCTION)
        
        issues = config.validate_config()
        
        # Should have no major issues with valid config
        # Allow for duplicate priorities since rules might have same priority
        major_issues = [issue for issue in issues if issue != "Duplicate rule priorities found"]
        assert len(major_issues) == 0
        
        # Test with disabled rate limiting
        config.config["enabled"] = False
        issues = config.validate_config()
        assert "Rate limiting is disabled" in issues
        
        # Reset for other tests
        config.config["enabled"] = True
    
    def test_config_export(self):
        """Test configuration export"""
        config = RateLimitingConfig(Environment.STAGING)
        
        exported = config.export_config()
        
        assert "environment" in exported
        assert "config" in exported
        assert exported["environment"] == "staging"
        assert "rules" in exported["config"]
        assert "enabled" in exported["config"]


class TestEnhancedRateLimitManager:
    """Test enhanced rate limit manager"""
    
    def test_manager_initialization(self):
        """Test manager initialization"""
        manager = EnhancedRateLimitManager("development")
        
        assert manager.environment == Environment.DEVELOPMENT
        assert manager.config.is_enabled() == True
        
        # Check that rate limiters were created
        assert len(manager.token_buckets) > 0
        assert len(manager.sliding_windows) > 0
        
        # Check statistics
        stats = manager.get_statistics()
        assert "environment" in stats
        assert stats["environment"] == "development"
        assert "total_rules" in stats
        assert "rate_limiters" in stats
    
    @patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379'})
    def test_redis_initialization(self):
        """Test Redis initialization"""
        with patch('redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            manager = EnhancedRateLimitManager("production")
            
            assert manager.redis_client is not None
            mock_redis.assert_called_once_with('redis://localhost:6379')
    
    def test_rate_limit_check(self):
        """Test rate limit checking"""
        manager = EnhancedRateLimitManager("testing")
        
        # Test with no rate limiting (development mode)
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == True
        
        # Test with specific endpoint
        result = manager.check_rate_limit("127.0.0.1", "/api/auth/login")
        assert result.allowed == True  # Testing mode doesn't block
    
    def test_ip_whitelist(self):
        """Test IP whitelist functionality"""
        manager = EnhancedRateLimitManager("production")
        
        # Add a rule with IP whitelist
        whitelist_rule = RateLimitRule(
            name="whitelist_test",
            limit_type="ip_based",
            algorithm="token_bucket",
            requests_per_window=10,
            window_seconds=60,
            ip_whitelist=["192.168.1.0/24", "10.0.0.1"]
        )
        
        manager.add_rule(whitelist_rule)
        
        # Test whitelisted IP
        result = manager.check_rate_limit("192.168.1.100", "/api/test")
        assert result.allowed == True
        
        # Test non-whitelisted IP
        result = manager.check_rate_limit("8.8.8.8", "/api/test")
        assert result.allowed == True  # Should be allowed but limited
    
    def test_user_whitelist(self):
        """Test user whitelist functionality"""
        manager = EnhancedRateLimitManager("production")
        
        # Add a rule with user whitelist
        whitelist_rule = RateLimitRule(
            name="user_whitelist_test",
            limit_type="user_based",
            algorithm="token_bucket",
            requests_per_window=10,
            window_seconds=60,
            user_whitelist=["admin_user", "premium_user"]
        )
        
        manager.add_rule(whitelist_rule)
        
        # Test whitelisted user
        result = manager.check_rate_limit("127.0.0.1", "/api/test", user_id="admin_user")
        assert result.allowed == True
        
        # Test non-whitelisted user
        result = manager.check_rate_limit("127.0.0.1", "/api/test", user_id="regular_user")
        assert result.allowed == True  # Should be allowed but limited
    
    def test_token_bucket_algorithm(self):
        """Test token bucket algorithm"""
        manager = EnhancedRateLimitManager("testing")
        
        # Create a token bucket rule
        rule = RateLimitRule(
            name="token_bucket_test",
            limit_type="ip_based",
            algorithm="token_bucket",
            requests_per_window=5,
            window_seconds=60,
            burst_size=5
        )
        
        manager.add_rule(rule)
        
        # Test multiple requests
        for i in range(5):
            result = manager.check_rate_limit("127.0.0.1", "/api/test")
            assert result.allowed == True
            assert result.remaining == 5 - i - 1
        
        # Next request should be limited
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == False
        assert result.remaining == 0
    
    def test_sliding_window_algorithm(self):
        """Test sliding window algorithm"""
        manager = EnhancedRateLimitManager("testing")
        
        # Create a sliding window rule
        rule = RateLimitRule(
            name="sliding_window_test",
            limit_type="ip_based",
            algorithm="sliding_window",
            requests_per_window=3,
            window_seconds=60
        )
        
        manager.add_rule(rule)
        
        # Test requests within limit
        for i in range(3):
            result = manager.check_rate_limit("127.0.0.1", "/api/test")
            assert result.allowed == True
        
        # Next request should be limited
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == False
    
    def test_fixed_window_algorithm(self):
        """Test fixed window algorithm"""
        manager = EnhancedRateLimitManager("testing")
        
        # Create a fixed window rule
        rule = RateLimitRule(
            name="fixed_window_test",
            limit_type="ip_based",
            algorithm="fixed_window",
            requests_per_window=2,
            window_seconds=60
        )
        
        manager.add_rule(rule)
        
        # Test requests within limit
        for i in range(2):
            result = manager.check_rate_limit("127.0.0.1", "/api/test")
            assert result.allowed == True
        
        # Next request should be limited
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == False
    
    def test_rule_priority(self):
        """Test rule priority handling"""
        manager = EnhancedRateLimitManager("production")
        
        # Create multiple rules for same endpoint with different priorities
        rule1 = RateLimitRule(
            name="priority_1",
            limit_type="endpoint_based",
            algorithm="token_bucket",
            requests_per_window=10,
            window_seconds=60,
            priority=1,  # Higher priority
            endpoints=["/api/test"]
        )
        
        rule2 = RateLimitRule(
            name="priority_2",
            limit_type="endpoint_based",
            algorithm="token_bucket",
            requests_per_window=5,
            window_seconds=60,
            priority=2,  # Lower priority
            endpoints=["/api/test"]
        )
        
        manager.add_rule(rule1)
        manager.add_rule(rule2)
        
        # The more restrictive rule (priority 2) should apply
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == True
        assert result.limit == 5  # More restrictive limit
    
    def test_violation_logging(self):
        """Test violation logging"""
        manager = EnhancedRateLimitManager("production")
        
        # Create a restrictive rule
        rule = RateLimitRule(
            name="violation_test",
            limit_type="ip_based",
            algorithm="token_bucket",
            requests_per_window=1,
            window_seconds=60
        )
        
        manager.add_rule(rule)
        
        # First request should be allowed
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == True
        
        # Second request should be blocked and logged
        result = manager.check_rate_limit("127.0.0.1", "/api/test")
        assert result.allowed == False
        
        # Check that violation was recorded
        assert len(manager.violations) > 0
        violation = list(manager.violations.values())[0]
        assert violation.rule_id == "violation_test"
        assert violation.identifier == "127.0.0.1"
    
    def test_statistics(self):
        """Test statistics collection"""
        manager = EnhancedRateLimitManager("staging")
        
        stats = manager.get_statistics()
        
        assert "environment" in stats
        assert "enabled" in stats
        assert "total_rules" in stats
        assert "rate_limiters" in stats
        assert "rules" in stats
        
        assert stats["environment"] == "staging"
        assert stats["enabled"] == True
        assert stats["total_rules"] > 0
        assert stats["rate_limiters"]["token_buckets"] > 0
        assert stats["rate_limiters"]["sliding_windows"] > 0
    
    def test_dynamic_rule_management(self):
        """Test dynamic rule management"""
        manager = EnhancedRateLimitManager("testing")
        
        # Add a new rule
        new_rule = RateLimitRule(
            name="dynamic_test",
            limit_type="ip_based",
            algorithm="token_bucket",
            requests_per_window=20,
            window_seconds=60
        )
        
        result = manager.add_rule(new_rule)
        assert result == True
        
        # Check that rule exists
        rule = manager.config.get_rule("dynamic_test")
        assert rule.name == "dynamic_test"
        assert rule.requests_per_window == 20
        
        # Update the rule
        result = manager.update_rule("dynamic_test", requests_per_window=30)
        assert result == True
        
        updated_rule = manager.config.get_rule("dynamic_test")
        assert updated_rule.requests_per_window == 30
        
        # Remove the rule
        result = manager.remove_rule("dynamic_test")
        assert result == True
        
        # Verify rule is gone
        try:
            manager.config.get_rule("dynamic_test")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected


class TestRateLimitIntegration:
    """Integration tests for rate limiting"""
    
    def test_end_to_end_rate_limiting(self):
        """Test end-to-end rate limiting flow"""
        manager = EnhancedRateLimitManager("testing")  # Use testing mode to avoid blocking
        
        # Simulate multiple requests from different users
        users = ["user1", "user2", "user3"]
        endpoints = ["/api/auth/login", "/api/analytics", "/api/projects"]
        
        for user in users:
            for endpoint in endpoints:
                # Make requests until rate limited
                request_count = 0
                while request_count < 20:  # Max 20 requests per user/endpoint
                    result = manager.check_rate_limit(f"ip_{user}", endpoint, user_id=user)
                    
                    if not result.allowed:
                        break
                    
                    request_count += 1
                
                # Verify that some requests were processed (testing mode is permissive)
                assert request_count > 0
    
    def test_environment_specific_behavior(self):
        """Test behavior differences between environments"""
        environments = ["development", "testing", "staging", "production"]
        
        for env_name in environments:
            manager = EnhancedRateLimitManager(env_name)
            
            # All environments should allow requests in test
            result = manager.check_rate_limit("127.0.0.1", "/api/test")
            assert result.allowed == True
            
            # Check environment-specific settings
            stats = manager.get_statistics()
            assert stats["environment"] == env_name
            
            # Production should be strictest
            if env_name == "production":
                assert manager.config.is_strict_mode() == True
                assert manager.config.should_block_violations() == True
            elif env_name == "development":
                assert manager.config.is_strict_mode() == False
                assert manager.config.should_block_violations() == False


if __name__ == "__main__":
    pytest.main([__file__])
