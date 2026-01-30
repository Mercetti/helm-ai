"""
Enhanced Rate Limiting Manager for Helm AI
Environment-aware rate limiting with dynamic configuration
"""

import os
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import redis
import hashlib
import ipaddress
from dataclasses import dataclass, field

# Import our configuration
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from rate_limiting_config import RateLimitingConfig, RateLimitRule, Environment, detect_environment

logger = logging.getLogger(__name__)

class EnhancedRateLimitManager:
    """Enhanced rate limiting manager with environment-aware configuration"""
    
    def __init__(self, environment: str = None):
        """Initialize enhanced rate limit manager"""
        # Detect or set environment
        if environment:
            self.environment = Environment(environment.lower())
        else:
            self.environment = detect_environment()
        
        # Load configuration
        self.config = RateLimitingConfig(self.environment)
        
        # Validate configuration
        issues = self.config.validate_config()
        if issues:
            logger.warning(f"Rate limiting configuration issues: {issues}")
        
        # Storage for rate limiters
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindowCounter] = {}
        self.fixed_windows: Dict[str, FixedWindowCounter] = {}
        
        # Violations tracking
        self.violations: Dict[str, RateLimitViolation] = {}
        
        # Redis setup
        self.redis_client = None
        if self.config.is_redis_enabled():
            try:
                redis_url = os.getenv('REDIS_URL')
                if redis_url:
                    self.redis_client = redis.from_url(redis_url)
                    self.redis_client.ping()  # Test connection
                    logger.info("Redis connected for rate limiting")
                else:
                    logger.warning("REDIS_URL not set, using in-memory rate limiting")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        
        # Initialize default rules
        self._initialize_rules()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"Enhanced rate limiting initialized for {self.environment.value} environment")
    
    def _initialize_rules(self):
        """Initialize rate limiting rules from configuration"""
        rules = self.config.get_rules()
        
        for rule in rules:
            if rule.enabled:
                self._create_rate_limiter(rule)
                logger.debug(f"Initialized rate limit rule: {rule.name}")
    
    def _create_rate_limiter(self, rule: RateLimitRule):
        """Create appropriate rate limiter for a rule"""
        if rule.algorithm == "token_bucket":
            refill_rate = rule.requests_per_window / rule.window_seconds
            bucket = TokenBucket(rule.requests_per_window, refill_rate)
            self.token_buckets[rule.name] = bucket
        elif rule.algorithm == "sliding_window":
            window = SlidingWindowCounter(rule.requests_per_window, rule.window_seconds)
            self.sliding_windows[rule.name] = window
        elif rule.algorithm == "fixed_window":
            window = FixedWindowCounter(rule.requests_per_window, rule.window_seconds)
            self.fixed_windows[rule.name] = window
        else:
            logger.warning(f"Unsupported algorithm: {rule.algorithm} for rule: {rule.name}")
    
    def check_rate_limit(self, identifier: str, endpoint: str = None, 
                        user_id: str = None, api_key: str = None) -> RateLimitResult:
        """Check rate limit for a request"""
        if not self.config.is_enabled():
            return RateLimitResult(allowed=True, limit=0, remaining=0, reset_time=0)
        
        # Get applicable rules
        applicable_rules = self._get_applicable_rules(identifier, endpoint, user_id, api_key)
        
        if not applicable_rules:
            return RateLimitResult(allowed=True, limit=0, remaining=0, reset_time=0)
        
        # Check each rule (most restrictive wins)
        most_restrictive_result = None
        for rule in applicable_rules:
            result = self._check_rule(rule, identifier, endpoint, user_id, api_key)
            
            if not result.allowed:
                # Log violation
                self._log_violation(rule, identifier, endpoint, result)
                
                # Block if configured to do so
                if self.config.should_block_violations():
                    return result
            
            # Track most restrictive result
            if most_restrictive_result is None or result.remaining < most_restrictive_result.remaining:
                most_restrictive_result = result
        
        return most_restrictive_result or RateLimitResult(allowed=True, limit=0, remaining=0, reset_time=0)
    
    def _get_applicable_rules(self, identifier: str, endpoint: str = None, 
                           user_id: str = None, api_key: str = None) -> List[RateLimitRule]:
        """Get rules that apply to this request"""
        applicable_rules = []
        rules = self.config.get_rules()
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            # Check if rule applies based on type
            applies = False
            
            if rule.limit_type == "global":
                applies = True
            elif rule.limit_type == "ip_based" and identifier:
                applies = self._check_ip_whitelist(rule, identifier)
            elif rule.limit_type == "user_based" and user_id:
                applies = self._check_user_whitelist(rule, user_id)
            elif rule.limit_type == "api_key_based" and api_key:
                applies = True  # API keys are always checked
            elif rule.limit_type == "endpoint_based" and endpoint:
                applies = self._check_endpoint_match(rule, endpoint)
            
            if applies:
                applicable_rules.append(rule)
        
        # Sort by priority (lower number = higher priority)
        applicable_rules.sort(key=lambda r: r.priority)
        return applicable_rules
    
    def _check_rule(self, rule: RateLimitRule, identifier: str, endpoint: str = None,
                   user_id: str = None, api_key: str = None) -> RateLimitResult:
        """Check a specific rate limit rule"""
        # Create cache key
        cache_key = self._create_cache_key(rule, identifier, endpoint, user_id, api_key)
        
        # Check based on algorithm
        if rule.algorithm == "token_bucket":
            return self._check_token_bucket(rule, cache_key)
        elif rule.algorithm == "sliding_window":
            return self._check_sliding_window(rule, cache_key)
        elif rule.algorithm == "fixed_window":
            return self._check_fixed_window(rule, cache_key)
        else:
            logger.warning(f"Unknown algorithm: {rule.algorithm}")
            return RateLimitResult(allowed=True, limit=0, remaining=0, reset_time=0)
    
    def _check_token_bucket(self, rule: RateLimitRule, cache_key: str) -> RateLimitResult:
        """Check token bucket rate limit"""
        bucket = self.token_buckets.get(rule.name)
        if not bucket:
            bucket = TokenBucket(rule.requests_per_window, rule.requests_per_window / rule.window_seconds)
            self.token_buckets[rule.name] = bucket
        
        # Try to consume token
        if bucket.consume():
            remaining = int(bucket.tokens)
            return RateLimitResult(
                allowed=True,
                limit=rule.requests_per_window,
                remaining=remaining,
                reset_time=int(time.time() + (rule.requests_per_window - remaining) / bucket.refill_rate)
            )
        else:
            reset_time = int(time.time() + 1.0 / bucket.refill_rate)
            return RateLimitResult(
                allowed=False,
                limit=rule.requests_per_window,
                remaining=0,
                reset_time=reset_time
            )
    
    def _check_sliding_window(self, rule: RateLimitRule, cache_key: str) -> RateLimitResult:
        """Check sliding window rate limit"""
        window = self.sliding_windows.get(rule.name)
        if not window:
            window = SlidingWindowCounter(rule.requests_per_window, rule.window_seconds)
            self.sliding_windows[rule.name] = window
        
        if self.redis_client:
            return self._check_sliding_window_redis(rule, cache_key)
        else:
            return self._check_sliding_window_memory(rule, cache_key, window)
    
    def _check_sliding_window_memory(self, rule: RateLimitRule, cache_key: str, 
                                   window: 'SlidingWindowCounter') -> RateLimitResult:
        """Check sliding window in memory"""
        current_count = window.add_request()
        
        if current_count <= rule.requests_per_window:
            remaining = rule.requests_per_window - current_count
            return RateLimitResult(
                allowed=True,
                limit=rule.requests_per_window,
                remaining=remaining,
                reset_time=int(time.time() + rule.window_seconds)
            )
        else:
            return RateLimitResult(
                allowed=False,
                limit=rule.requests_per_window,
                remaining=0,
                reset_time=int(time.time() + rule.window_seconds)
            )
    
    def _check_sliding_window_redis(self, rule: RateLimitRule, cache_key: str) -> RateLimitResult:
        """Check sliding window using Redis"""
        try:
            pipe = self.redis_client.pipeline()
            now = time.time()
            window_start = now - rule.window_seconds
            
            # Remove old entries
            pipe.zremrangebyscore(cache_key, 0, window_start)
            
            # Count current entries
            pipe.zcard(cache_key)
            
            # Add current request
            pipe.zadd(cache_key, {str(now): now})
            
            # Set expiration
            pipe.expire(cache_key, rule.window_seconds + 10)
            
            results = pipe.execute()
            current_count = results[1]
            
            if current_count <= rule.requests_per_window:
                remaining = rule.requests_per_window - current_count
                return RateLimitResult(
                    allowed=True,
                    limit=rule.requests_per_window,
                    remaining=remaining,
                    reset_time=int(now + rule.window_seconds)
                )
            else:
                return RateLimitResult(
                    allowed=False,
                    limit=rule.requests_per_window,
                    remaining=0,
                    reset_time=int(now + rule.window_seconds)
                )
        except Exception as e:
            logger.error(f"Redis sliding window check failed: {e}")
            # Fallback to memory
            return self._check_sliding_window_memory(rule, cache_key, 
                                                SlidingWindowCounter(rule.requests_per_window, rule.window_seconds))
    
    def _check_fixed_window(self, rule: RateLimitRule, cache_key: str) -> RateLimitResult:
        """Check fixed window rate limit"""
        window = self.fixed_windows.get(rule.name)
        if not window:
            window = FixedWindowCounter(rule.requests_per_window, rule.window_seconds)
            self.fixed_windows[rule.name] = window
        
        current_count = window.add_request()
        
        if current_count <= rule.requests_per_window:
            remaining = rule.requests_per_window - current_count
            return RateLimitResult(
                allowed=True,
                limit=rule.requests_per_window,
                remaining=remaining,
                reset_time=window.reset_time
            )
        else:
            return RateLimitResult(
                allowed=False,
                limit=rule.requests_per_window,
                remaining=0,
                reset_time=window.reset_time
            )
    
    def _create_cache_key(self, rule: RateLimitRule, identifier: str, endpoint: str = None,
                        user_id: str = None, api_key: str = None) -> str:
        """Create cache key for rate limiting"""
        key_parts = [f"rate_limit:{rule.name}"]
        
        if rule.limit_type == "ip_based" and identifier:
            key_parts.append(f"ip:{identifier}")
        elif rule.limit_type == "user_based" and user_id:
            key_parts.append(f"user:{user_id}")
        elif rule.limit_type == "api_key_based" and api_key:
            key_parts.append(f"api_key:{hashlib.md5(api_key.encode()).hexdigest()}")
        elif rule.limit_type == "endpoint_based" and endpoint:
            key_parts.append(f"endpoint:{endpoint}")
        elif rule.limit_type == "global":
            key_parts.append("global")
        
        return ":".join(key_parts)
    
    def _check_ip_whitelist(self, rule: RateLimitRule, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        if not rule.ip_whitelist:
            return True
        
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            for whitelisted_ip in rule.ip_whitelist:
                if "/" in whitelisted_ip:
                    # CIDR notation
                    if ip_obj in ipaddress.ip_network(whitelisted_ip):
                        return True
                else:
                    # Exact match
                    if str(ip_obj) == whitelisted_ip:
                        return True
        except ValueError:
            pass  # Invalid IP
        
        return False
    
    def _check_user_whitelist(self, rule: RateLimitRule, user_id: str) -> bool:
        """Check if user is whitelisted"""
        if not rule.user_whitelist:
            return True
        
        return user_id in rule.user_whitelist
    
    def _check_endpoint_match(self, rule: RateLimitRule, endpoint: str) -> bool:
        """Check if endpoint matches rule"""
        if not rule.endpoints:
            return False
        
        for rule_endpoint in rule.endpoints:
            if rule_endpoint.endswith("/*"):
                # Wildcard match
                if endpoint.startswith(rule_endpoint[:-1]):
                    return True
            else:
                # Exact match
                if endpoint == rule_endpoint:
                    return True
        
        return False
    
    def _log_violation(self, rule: RateLimitRule, identifier: str, endpoint: str, 
                      result: 'RateLimitResult'):
        """Log rate limit violation"""
        if not self.config.should_log_violations():
            return
        
        violation = RateLimitViolation(
            violation_id=f"violation_{int(time.time())}_{hash(identifier) % 10000}",
            rule_id=rule.name,
            identifier=identifier,
            endpoint=endpoint or "unknown",
            violation_time=datetime.now(),
            current_requests=result.limit - result.remaining,
            limit=result.limit,
            window_seconds=rule.window_seconds,
            action_taken="blocked" if self.config.should_block_violations() else "logged",
            metadata={
                "environment": self.environment.value,
                "algorithm": rule.algorithm,
                "priority": rule.priority
            }
        )
        
        self.violations[violation.violation_id] = violation
        
        logger.warning(
            f"Rate limit violation: {rule.name} - {identifier} - {endpoint} - "
            f"{violation.current_requests}/{violation.limit} requests"
        )
    
    def _start_cleanup_thread(self):
        """Start cleanup thread for old rate limit data"""
        def cleanup():
            while True:
                try:
                    time.sleep(self.config.get_cleanup_interval())
                    self._cleanup_old_data()
                except Exception as e:
                    logger.error(f"Rate limiting cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_data(self):
        """Clean up old rate limiting data"""
        now = time.time()
        cutoff = now - self.config.get_cleanup_interval() * 2
        
        # Clean up in-memory data
        for cache_key, window in list(self.sliding_windows.items()):
            window.cleanup(cutoff)
        
        for cache_key, window in list(self.fixed_windows.items()):
            window.cleanup(cutoff)
        
        # Clean up old violations
        old_violations = [
            vid for vid, violation in self.violations.items()
            if (now - violation.violation_time.timestamp()) > self.config.get_cleanup_interval() * 2
        ]
        
        for vid in old_violations:
            del self.violations[vid]
        
        if old_violations:
            logger.debug(f"Cleaned up {len(old_violations)} old violations")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        stats = {
            "environment": self.environment.value,
            "enabled": self.config.is_enabled(),
            "strict_mode": self.config.is_strict_mode(),
            "redis_enabled": self.config.is_redis_enabled(),
            "total_rules": len(self.config.get_rules()),
            "active_violations": len(self.violations),
            "rate_limiters": {
                "token_buckets": len(self.token_buckets),
                "sliding_windows": len(self.sliding_windows),
                "fixed_windows": len(self.fixed_windows)
            }
        }
        
        # Add rule-specific stats
        rule_stats = {}
        for rule in self.config.get_rules():
            rule_stats[rule.name] = {
                "type": rule.limit_type,
                "algorithm": rule.algorithm,
                "limit": rule.requests_per_window,
                "window": rule.window_seconds,
                "priority": rule.priority,
                "enabled": rule.enabled
            }
        
        stats["rules"] = rule_stats
        return stats
    
    def add_rule(self, rule: RateLimitRule) -> bool:
        """Add a new rate limit rule"""
        try:
            self.config.add_rule(rule)
            self._create_rate_limiter(rule)
            logger.info(f"Added rate limit rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add rule {rule.name}: {e}")
            return False
    
    def remove_rule(self, name: str) -> bool:
        """Remove a rate limit rule"""
        try:
            if self.config.remove_rule(name):
                # Clean up rate limiters
                self.token_buckets.pop(name, None)
                self.sliding_windows.pop(name, None)
                self.fixed_windows.pop(name, None)
                logger.info(f"Removed rate limit rule: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove rule {name}: {e}")
            return False
    
    def update_rule(self, name: str, **kwargs) -> bool:
        """Update a rate limit rule"""
        try:
            if self.config.update_rule(name, **kwargs):
                # Recreate rate limiter with new settings
                rule = self.config.get_rule(name)
                self._create_rate_limiter(rule)
                logger.info(f"Updated rate limit rule: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update rule {name}: {e}")
            return False


# Supporting classes
@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    limit: int
    remaining: int
    reset_time: int
    retry_after: int = 0
    
    def __post_init__(self):
        if not self.allowed and self.retry_after == 0:
            self.retry_after = max(1, self.reset_time - int(time.time()))

@dataclass
class RateLimitViolation:
    """Rate limit violation record"""
    violation_id: str
    rule_id: str
    identifier: str
    endpoint: str
    violation_time: datetime
    current_requests: int
    limit: int
    window_seconds: int
    action_taken: str = "blocked"
    metadata: Dict[str, Any] = None

class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        if tokens_to_add > 0:
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now

class SlidingWindowCounter:
    """Sliding window counter"""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()
    
    def add_request(self) -> int:
        """Add a request to the window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Remove old requests
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            # Add current request
            self.requests.append(now)
            
            return len(self.requests)
    
    def cleanup(self, cutoff_time: float):
        """Clean up old requests"""
        with self.lock:
            while self.requests and self.requests[0] < cutoff_time:
                self.requests.popleft()

class FixedWindowCounter:
    """Fixed window counter"""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.count = 0
        self.window_start = time.time()
        self.lock = threading.Lock()
    
    def add_request(self) -> int:
        """Add a request to the window"""
        with self.lock:
            now = time.time()
            
            # Reset window if expired
            if now - self.window_start >= self.window_seconds:
                self.count = 0
                self.window_start = now
            
            self.count += 1
            return self.count
    
    @property
    def reset_time(self) -> int:
        """Get window reset time"""
        return int(self.window_start + self.window_seconds)
    
    def cleanup(self, cutoff_time: float):
        """Clean up if window is expired"""
        with self.lock:
            if cutoff_time > self.window_start + self.window_seconds:
                self.count = 0
                self.window_start = time.time()


# Factory function
def create_enhanced_rate_limit_manager(environment: str = None) -> EnhancedRateLimitManager:
    """Create enhanced rate limit manager for specified environment"""
    return EnhancedRateLimitManager(environment)
