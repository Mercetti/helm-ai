"""
Helm AI API Rate Limiting
This module provides comprehensive rate limiting and throttling for API endpoints
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import time
import threading
import redis
from collections import defaultdict, deque
import hashlib
import ipaddress

logger = logging.getLogger(__name__)

class RateLimitException(Exception):
    """Rate limit exception"""
    def __init__(self, message: str, limit: int, window: int, context: Dict[str, Any] = None):
        super().__init__(message)
        self.limit = limit
        self.window = window
        self.context = context or {}

class RateLimitType(Enum):
    """Rate limit types"""
    IP_BASED = "ip_based"
    USER_BASED = "user_based"
    API_KEY_BASED = "api_key_based"
    ENDPOINT_BASED = "endpoint_based"
    GLOBAL = "global"

class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitRule:
    """Rate limit rule definition"""
    rule_id: str
    name: str
    limit_type: RateLimitType
    algorithm: RateLimitAlgorithm
    requests_per_window: int
    window_seconds: int
    burst_size: int = 0
    priority: int = 1
    enabled: bool = True
    endpoints: List[str] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    user_whitelist: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitViolation:
    """Rate limit violation record"""
    violation_id: str
    rule_id: str
    identifier: str  # IP, user ID, API key, etc.
    endpoint: str
    violation_time: datetime
    current_requests: int
    limit: int
    window_seconds: int
    action_taken: str = "blocked"
    metadata: Dict[str, Any] = field(default_factory=dict)

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
        
        if elapsed > 0:
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
    
    def get_available_tokens(self) -> int:
        """Get available tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)

class SlidingWindowCounter:
    """Sliding window rate limiter"""
    
    def __init__(self, window_seconds: int, max_requests: int):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        with self.lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_seconds:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_current_count(self) -> int:
        """Get current request count"""
        with self.lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_seconds:
                self.requests.popleft()
            
            return len(self.requests)

class RateLimitManager:
    """Comprehensive rate limiting management"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.violations: Dict[str, RateLimitViolation] = {}
        
        # Rate limiters storage
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindowCounter] = {}
        
        # Configuration
        self.use_redis = os.getenv('REDIS_URL') is not None
        self.default_window = int(os.getenv('RATE_LIMIT_DEFAULT_WINDOW', '60'))
        self.default_limit = int(os.getenv('RATE_LIMIT_DEFAULT_LIMIT', '100'))
        
        # Initialize Redis if configured
        if self.use_redis:
            self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        
        # Initialize default rules
        self._initialize_default_rules()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _initialize_default_rules(self):
        """Initialize default rate limiting rules"""
        
        # Global rate limit
        self.create_rule(
            name="global_rate_limit",
            limit_type=RateLimitType.GLOBAL,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            requests_per_window=1000,
            window_seconds=60,
            priority=1
        )
        
        # IP-based rate limit
        self.create_rule(
            name="ip_rate_limit",
            limit_type=RateLimitType.IP_BASED,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_window=100,
            window_seconds=60,
            burst_size=20,
            priority=2
        )
        
        # User-based rate limit
        self.create_rule(
            name="user_rate_limit",
            limit_type=RateLimitType.USER_BASED,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            requests_per_window=200,
            window_seconds=60,
            priority=2
        )
        
        # API key rate limit
        self.create_rule(
            name="api_key_rate_limit",
            limit_type=RateLimitType.API_KEY_BASED,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_window=500,
            window_seconds=60,
            burst_size=50,
            priority=2
        )
        
        # Strict rate limit for sensitive endpoints
        self.create_rule(
            name="sensitive_endpoints",
            limit_type=RateLimitType.ENDPOINT_BASED,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            requests_per_window=10,
            window_seconds=60,
            endpoints=["/auth/login", "/auth/register", "/api/keys"],
            priority=3
        )
        
        # AI model inference rate limit
        self.create_rule(
            name="ai_inference",
            limit_type=RateLimitType.USER_BASED,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            requests_per_window=50,
            window_seconds=60,
            endpoints=["/api/ai/infer", "/api/ai/chat"],
            priority=3
        )
    
    def create_rule(self, 
                   name: str,
                   limit_type: RateLimitType,
                   algorithm: RateLimitAlgorithm,
                   requests_per_window: int,
                   window_seconds: int,
                   burst_size: int = 0,
                   priority: int = 1,
                   endpoints: List[str] = None,
                   ip_whitelist: List[str] = None,
                   user_whitelist: List[str] = None) -> RateLimitRule:
        """Create rate limiting rule"""
        rule_id = f"rule_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        rule = RateLimitRule(
            rule_id=rule_id,
            name=name,
            limit_type=limit_type,
            algorithm=algorithm,
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
            burst_size=burst_size or requests_per_window // 4,
            priority=priority,
            endpoints=endpoints or [],
            ip_whitelist=ip_whitelist or [],
            user_whitelist=user_whitelist or []
        )
        
        self.rules[rule_id] = rule
        
        logger.info(f"Created rate limit rule: {name}")
        return rule
    
    def check_rate_limit(self, 
                        identifier: str,
                        endpoint: str = None,
                        ip_address: str = None,
                        user_id: str = None,
                        api_key: str = None) -> Tuple[bool, Optional[RateLimitRule]]:
        """Check if request is allowed based on rate limits"""
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.rules.values(), key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Check if rule applies to this endpoint
            if rule.endpoints and endpoint:
                if not any(endpoint.startswith(ep) for ep in rule.endpoints):
                    continue
            
            # Check whitelists
            if self._is_whitelisted(rule, ip_address, user_id, api_key):
                continue
            
            # Get appropriate identifier for rule type
            rule_identifier = self._get_identifier_for_rule(rule, identifier, ip_address, user_id, api_key)
            
            if not rule_identifier:
                continue
            
            # Check rate limit based on algorithm
            is_allowed = self._check_rule_limit(rule, rule_identifier)
            
            if not is_allowed:
                # Create violation record
                self._create_violation(rule, rule_identifier, endpoint)
                return False, rule
        
        return True, None
    
    def _is_whitelisted(self, 
                       rule: RateLimitRule,
                       ip_address: str = None,
                       user_id: str = None,
                       api_key: str = None) -> bool:
        """Check if identifier is whitelisted for rule"""
        if ip_address and any(self._ip_in_cidr(ip_address, cidr) for cidr in rule.ip_whitelist):
            return True
        
        if user_id and user_id in rule.user_whitelist:
            return True
        
        return False
    
    def _ip_in_cidr(self, ip: str, cidr: str) -> bool:
        """Check if IP is in CIDR range"""
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
        except ValueError:
            return False
    
    def _get_identifier_for_rule(self, 
                                 rule: RateLimitRule,
                                 identifier: str,
                                 ip_address: str = None,
                                 user_id: str = None,
                                 api_key: str = None) -> str:
        """Get appropriate identifier for rule type"""
        if rule.limit_type == RateLimitType.IP_BASED and ip_address:
            return f"ip:{ip_address}"
        elif rule.limit_type == RateLimitType.USER_BASED and user_id:
            return f"user:{user_id}"
        elif rule.limit_type == RateLimitType.API_KEY_BASED and api_key:
            return f"api_key:{api_key}"
        elif rule.limit_type == RateLimitType.ENDPOINT_BASED:
            return f"endpoint:{identifier}"
        elif rule.limit_type == RateLimitType.GLOBAL:
            return "global"
        
        return None
    
    def _check_rule_limit(self, rule: RateLimitRule, identifier: str) -> bool:
        """Check rate limit for specific rule and identifier"""
        key = f"{rule.rule_id}:{identifier}"
        
        if self.use_redis:
            return self._check_redis_limit(rule, key)
        else:
            return self._check_memory_limit(rule, key)
    
    def _check_memory_limit(self, rule: RateLimitRule, key: str) -> bool:
        """Check rate limit using in-memory storage"""
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            bucket = self.token_buckets.get(key)
            if not bucket:
                bucket = TokenBucket(rule.burst_size, rule.requests_per_window / rule.window_seconds)
                self.token_buckets[key] = bucket
            
            return bucket.consume()
        
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            window = self.sliding_windows.get(key)
            if not window:
                window = SlidingWindowCounter(rule.window_seconds, rule.requests_per_window)
                self.sliding_windows[key] = window
            
            return window.is_allowed()
        
        elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return self._check_fixed_window_memory(rule, key)
        
        return True
    
    def _check_redis_limit(self, rule: RateLimitRule, key: str) -> bool:
        """Check rate limit using Redis"""
        try:
            if rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                return self._check_sliding_window_redis(rule, key)
            elif rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                return self._check_token_bucket_redis(rule, key)
            else:
                return self._check_fixed_window_redis(rule, key)
        
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fall back to allowing request if Redis fails
            return True
    
    def _check_sliding_window_redis(self, rule: RateLimitRule, key: str) -> bool:
        """Check sliding window using Redis"""
        now = time.time()
        window_start = now - rule.window_seconds
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Get current count
        current_count = self.redis_client.zcard(key)
        
        if current_count < rule.requests_per_window:
            # Add current request
            self.redis_client.zadd(key, {str(now): now})
            # Set expiration
            self.redis_client.expire(key, rule.window_seconds)
            return True
        
        return False
    
    def _check_token_bucket_redis(self, rule: RateLimitRule, key: str) -> bool:
        """Check token bucket using Redis"""
        script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local current_tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        local elapsed = now - last_refill
        local new_tokens = math.min(capacity, current_tokens + elapsed * refill_rate)
        
        if new_tokens >= tokens then
            new_tokens = new_tokens - tokens
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return 1
        else
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return 0
        end
        """
        
        try:
            result = self.redis_client.eval(
                script,
                1,
                key,
                rule.burst_size,
                rule.requests_per_window / rule.window_seconds,
                1,  # tokens to consume
                time.time()
            )
            return result == 1
        except Exception as e:
            logger.error(f"Redis token bucket script failed: {e}")
            return True
    
    def _check_fixed_window_memory(self, rule: RateLimitRule, key: str) -> bool:
        """Check fixed window using in-memory storage"""
        current_time = int(time.time() // rule.window_seconds)
        window_key = f"{key}:{current_time}"
        
        if window_key not in self.sliding_windows:
            self.sliding_windows[window_key] = SlidingWindowCounter(rule.window_seconds, rule.requests_per_window)
        
        return self.sliding_windows[window_key].is_allowed()
    
    def _check_fixed_window_redis(self, rule: RateLimitRule, key: str) -> bool:
        """Check fixed window using Redis"""
        current_time = int(time.time() // rule.window_seconds)
        window_key = f"{key}:{current_time}"
        
        try:
            current_count = self.redis_client.incr(window_key)
            if current_count == 1:
                self.redis_client.expire(window_key, rule.window_seconds)
            
            return current_count <= rule.requests_per_window
        except Exception as e:
            logger.error(f"Redis fixed window check failed: {e}")
            return True
    
    def _create_violation(self, rule: RateLimitRule, identifier: str, endpoint: str = None):
        """Create rate limit violation record"""
        violation_id = f"violation_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(identifier.encode()).hexdigest()[:8]}"
        
        # Get current request count
        current_requests = self._get_current_request_count(rule, identifier)
        
        violation = RateLimitViolation(
            violation_id=violation_id,
            rule_id=rule.rule_id,
            identifier=identifier,
            endpoint=endpoint or "unknown",
            violation_time=datetime.now(),
            current_requests=current_requests,
            limit=rule.requests_per_window,
            window_seconds=rule.window_seconds
        )
        
        self.violations[violation_id] = violation
        
        logger.warning(f"Rate limit violation: {rule.name} - {identifier} ({current_requests}/{rule.requests_per_window})")
    
    def _get_current_request_count(self, rule: RateLimitRule, identifier: str) -> int:
        """Get current request count for rule and identifier"""
        key = f"{rule.rule_id}:{identifier}"
        
        if self.use_redis:
            try:
                if rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                    return self.redis_client.zcard(key)
                else:
                    return int(self.redis_client.get(key) or 0)
            except:
                return 0
        else:
            if rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                window = self.sliding_windows.get(key)
                return window.get_current_count() if window else 0
            else:
                return 0
    
    def get_rate_limit_status(self, 
                             identifier: str,
                             endpoint: str = None,
                             ip_address: str = None,
                             user_id: str = None,
                             api_key: str = None) -> Dict[str, Any]:
        """Get current rate limit status"""
        status = {
            "allowed": True,
            "limits": [],
            "violations": []
        }
        
        for rule in sorted(self.rules.values(), key=lambda x: x.priority, reverse=True):
            if not rule.enabled:
                continue
            
            # Check if rule applies
            if rule.endpoints and endpoint:
                if not any(endpoint.startswith(ep) for ep in rule.endpoints):
                    continue
            
            # Check whitelists
            if self._is_whitelisted(rule, ip_address, user_id, api_key):
                continue
            
            rule_identifier = self._get_identifier_for_rule(rule, identifier, ip_address, user_id, api_key)
            if not rule_identifier:
                continue
            
            current_requests = self._get_current_request_count(rule, rule_identifier)
            remaining_requests = max(0, rule.requests_per_window - current_requests)
            
            limit_info = {
                "rule_name": rule.name,
                "rule_type": rule.limit_type.value,
                "algorithm": rule.algorithm.value,
                "requests_per_window": rule.requests_per_window,
                "window_seconds": rule.window_seconds,
                "current_requests": current_requests,
                "remaining_requests": remaining_requests,
                "reset_time": datetime.now() + timedelta(seconds=rule.window_seconds)
            }
            
            status["limits"].append(limit_info)
            
            # Check if this would be a violation
            if current_requests >= rule.requests_per_window:
                status["allowed"] = False
                status["violations"].append({
                    "rule_name": rule.name,
                    "limit": rule.requests_per_window,
                    "current": current_requests,
                    "window_seconds": rule.window_seconds
                })
        
        return status
    
    def get_violations(self, 
                      rule_id: str = None,
                      identifier: str = None,
                      hours: int = 24) -> List[RateLimitViolation]:
        """Get rate limit violations"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        violations = []
        for violation in self.violations.values():
            if violation.violation_time < cutoff_time:
                continue
            
            if rule_id and violation.rule_id != rule_id:
                continue
            
            if identifier and violation.identifier != identifier:
                continue
            
            violations.append(violation)
        
        # Sort by violation time (most recent first)
        violations.sort(key=lambda x: x.violation_time, reverse=True)
        
        return violations
    
    def clear_violations(self, rule_id: str = None, identifier: str = None) -> int:
        """Clear rate limit violations"""
        violations_to_remove = []
        
        for violation_id, violation in self.violations.items():
            if rule_id and violation.rule_id != rule_id:
                continue
            
            if identifier and violation.identifier != identifier:
                continue
            
            violations_to_remove.append(violation_id)
        
        for violation_id in violations_to_remove:
            del self.violations[violation_id]
        
        return len(violations_to_remove)
    
    def _start_cleanup_thread(self):
        """Start cleanup thread for expired data"""
        def cleanup_expired_data():
            while True:
                try:
                    # Clean up old token buckets and sliding windows
                    current_time = time.time()
                    
                    # Clean up token buckets (remove those not used for 1 hour)
                    expired_buckets = []
                    for key, bucket in self.token_buckets.items():
                        if current_time - bucket.last_refill > 3600:
                            expired_buckets.append(key)
                    
                    for key in expired_buckets:
                        del self.token_buckets[key]
                    
                    # Clean up sliding windows (remove those not used for 1 hour)
                    expired_windows = []
                    for key, window in self.sliding_windows.items():
                        if not window.requests or current_time - window.requests[-1] > 3600:
                            expired_windows.append(key)
                    
                    for key in expired_windows:
                        del self.sliding_windows[key]
                    
                    # Clean up old violations (older than 7 days)
                    cutoff_time = datetime.now() - timedelta(days=7)
                    expired_violations = [
                        vid for vid, violation in self.violations.items()
                        if violation.violation_time < cutoff_time
                    ]
                    
                    for vid in expired_violations:
                        del self.violations[vid]
                    
                    if expired_buckets or expired_windows or expired_violations:
                        logger.info(f"Cleaned up {len(expired_buckets)} buckets, {len(expired_windows)} windows, {len(expired_violations)} violations")
                    
                    # Sleep for 1 hour
                    threading.Event().wait(3600)
                    
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
                    threading.Event().wait(300)  # Wait 5 minutes on error
        
        cleanup_thread = threading.Thread(target=cleanup_expired_data, daemon=True)
        cleanup_thread.start()
    
    def get_rate_limit_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        total_violations = len(self.violations)
        recent_violations = len([v for v in self.violations.values() 
                                if v.violation_time > datetime.now() - timedelta(hours=24)])
        
        violations_by_rule = defaultdict(int)
        for violation in self.violations.values():
            rule = self.rules.get(violation.rule_id)
            if rule:
                violations_by_rule[rule.name] += 1
        
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "total_violations": total_violations,
            "recent_violations_24h": recent_violations,
            "violations_by_rule": dict(violations_by_rule),
            "active_buckets": len(self.token_buckets),
            "active_windows": len(self.sliding_windows),
            "use_redis": self.use_redis
        }


# Global instance
rate_limit_manager = RateLimitManager()
