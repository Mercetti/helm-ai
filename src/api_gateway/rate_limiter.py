# Helm AI - Distributed Rate Limiter
"""
Redis-backed distributed rate limiter for API gateway.
Supports multiple algorithms and scales across multiple instances.
"""

import time
import math
from typing import Tuple, Dict, Any, Optional
from redis import Redis
from redis.exceptions import RedisError

from src.common.exceptions import RateLimitException, ExternalServiceException
from src.logging_config.logger import get_logger

logger = get_logger(__name__)

class RateLimitAlgorithm:
    """Rate limiting algorithms"""

    @staticmethod
    def fixed_window(
        redis: Redis,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Fixed window rate limiting algorithm.

        Args:
            redis: Redis client
            key: Rate limit key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, metadata)
        """
        current_window = int(time.time() / window_seconds)
        window_key = f"rate_limit:fw:{key}:{current_window}"

        try:
            # Get current count
            current_count = redis.get(window_key)
            current_count = int(current_count) if current_count else 0

            # Check if limit exceeded
            if current_count >= limit:
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_at": (current_window + 1) * window_seconds,
                    "reset_in": ((current_window + 1) * window_seconds) - int(time.time())
                }

            # Increment counter
            new_count = redis.incr(window_key)

            # Set expiration if this is the first request in window
            if new_count == 1:
                redis.expire(window_key, window_seconds * 2)  # Extra time for cleanup

            return True, {
                "limit": limit,
                "remaining": max(0, limit - new_count),
                "reset_at": (current_window + 1) * window_seconds,
                "reset_in": ((current_window + 1) * window_seconds) - int(time.time())
            }

        except RedisError as e:
            logger.error(f"Redis error in fixed window rate limiting: {e}")
            # Allow request on Redis failure to avoid blocking legitimate traffic
            return True, {"limit": limit, "remaining": limit, "error": "redis_unavailable"}

    @staticmethod
    def sliding_window(
        redis: Redis,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Sliding window rate limiting algorithm.

        Args:
            redis: Redis client
            key: Rate limit key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, metadata)
        """
        now = time.time()
        window_start = now - window_seconds

        try:
            # Remove old entries
            redis.zremrangebyscore(f"rate_limit:sw:{key}", 0, window_start)

            # Count requests in current window
            request_count = redis.zcard(f"rate_limit:sw:{key}")

            if request_count >= limit:
                # Get next reset time
                oldest_timestamp = redis.zrange(f"rate_limit:sw:{key}", 0, 0, withscores=True)
                reset_at = oldest_timestamp[0][1] + window_seconds if oldest_timestamp else now + window_seconds

                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset_at": reset_at,
                    "reset_in": max(0, reset_at - now)
                }

            # Add current request
            redis.zadd(f"rate_limit:sw:{key}", {str(now): now})

            # Set expiration for cleanup
            redis.expire(f"rate_limit:sw:{key}", window_seconds * 2)

            return True, {
                "limit": limit,
                "remaining": max(0, limit - request_count - 1),
                "reset_at": now + window_seconds,
                "reset_in": window_seconds
            }

        except RedisError as e:
            logger.error(f"Redis error in sliding window rate limiting: {e}")
            return True, {"limit": limit, "remaining": limit, "error": "redis_unavailable"}

    @staticmethod
    def token_bucket(
        redis: Redis,
        key: str,
        capacity: int,
        refill_rate: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Token bucket rate limiting algorithm.

        Args:
            redis: Redis client
            key: Rate limit key
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second

        Returns:
            (is_allowed, metadata)
        """
        now = time.time()
        bucket_key = f"rate_limit:tb:{key}"

        try:
            # Get current bucket state
            bucket_data = redis.hgetall(bucket_key)

            if not bucket_data:
                # Initialize new bucket
                tokens = capacity - 1  # Consume one token
                last_refill = now
                redis.hset(bucket_key, mapping={
                    "tokens": tokens,
                    "last_refill": last_refill
                })
                redis.expire(bucket_key, int(capacity / refill_rate) * 2)

                return True, {
                    "limit": capacity,
                    "remaining": tokens,
                    "reset_at": now + (capacity / refill_rate),
                    "reset_in": capacity / refill_rate
                }

            # Parse existing bucket
            current_tokens = float(bucket_data.get(b"tokens", capacity))
            last_refill = float(bucket_data.get(b"last_refill", now))

            # Calculate tokens to add since last refill
            time_passed = now - last_refill
            tokens_to_add = time_passed * refill_rate
            new_tokens = min(capacity, current_tokens + tokens_to_add)

            if new_tokens < 1:
                # No tokens available
                reset_in = (1 - new_tokens) / refill_rate
                return False, {
                    "limit": capacity,
                    "remaining": 0,
                    "reset_at": now + reset_in,
                    "reset_in": reset_in
                }

            # Consume token
            new_tokens -= 1

            # Update bucket
            redis.hset(bucket_key, mapping={
                "tokens": new_tokens,
                "last_refill": now
            })

            return True, {
                "limit": capacity,
                "remaining": math.floor(new_tokens),
                "reset_at": now + ((capacity - new_tokens) / refill_rate),
                "reset_in": (capacity - new_tokens) / refill_rate
            }

        except RedisError as e:
            logger.error(f"Redis error in token bucket rate limiting: {e}")
            return True, {"limit": capacity, "remaining": capacity, "error": "redis_unavailable"}

class DistributedRateLimiter:
    """Redis-backed distributed rate limiter"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.logger = get_logger(__name__)

    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        algorithm: str = "sliding_window"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Rate limit key (e.g., user_id, IP address)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            algorithm: Rate limiting algorithm ('fixed_window', 'sliding_window', 'token_bucket')

        Returns:
            (is_allowed, metadata)

        Raises:
            RateLimitException: If rate limit is exceeded
            ExternalServiceException: If Redis is unavailable
        """
        try:
            if algorithm == "fixed_window":
                allowed, metadata = RateLimitAlgorithm.fixed_window(
                    self.redis, key, limit, window_seconds
                )
            elif algorithm == "sliding_window":
                allowed, metadata = RateLimitAlgorithm.sliding_window(
                    self.redis, key, limit, window_seconds
                )
            elif algorithm == "token_bucket":
                # For token bucket, treat limit as capacity and calculate refill rate
                refill_rate = limit / window_seconds
                allowed, metadata = RateLimitAlgorithm.token_bucket(
                    self.redis, key, limit, refill_rate
                )
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

            # Log rate limit events
            if not allowed:
                self.logger.warning(
                    f"Rate limit exceeded for key: {key}",
                    extra={
                        "rate_limit_key": key,
                        "limit": limit,
                        "window_seconds": window_seconds,
                        "algorithm": algorithm,
                        "metadata": metadata
                    }
                )
            elif metadata.get("remaining", limit) < limit * 0.1:  # Log when approaching limit
                self.logger.info(
                    f"Rate limit approaching for key: {key}",
                    extra={
                        "rate_limit_key": key,
                        "remaining": metadata.get("remaining", 0),
                        "limit": limit
                    }
                )

            return allowed, metadata

        except RedisError as e:
            self.logger.error(f"Redis connection error in rate limiter: {e}")
            raise ExternalServiceException(
                "Rate limiting service unavailable",
                service_name="redis",
                service_error=str(e)
            )

    def get_usage(
        self,
        key: str,
        algorithm: str = "sliding_window",
        window_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Get current rate limit usage for a key.

        Args:
            key: Rate limit key
            algorithm: Algorithm used
            window_seconds: Time window

        Returns:
            Usage statistics
        """
        try:
            if algorithm == "fixed_window":
                current_window = int(time.time() / window_seconds)
                window_key = f"rate_limit:fw:{key}:{current_window}"
                count = self.redis.get(window_key)
                current_count = int(count) if count else 0
                return {"current": current_count, "window": current_window}

            elif algorithm == "sliding_window":
                window_key = f"rate_limit:sw:{key}"
                count = self.redis.zcard(window_key)
                return {"current": count, "window_start": time.time() - window_seconds}

            elif algorithm == "token_bucket":
                bucket_key = f"rate_limit:tb:{key}"
                bucket_data = self.redis.hgetall(bucket_key)
                if bucket_data:
                    tokens = float(bucket_data.get(b"tokens", 0))
                    return {"current_tokens": tokens}
                return {"current_tokens": 0}

            return {}

        except RedisError as e:
            self.logger.error(f"Error getting rate limit usage: {e}")
            return {"error": "redis_unavailable"}

    def reset_limit(self, key: str, algorithm: str = "sliding_window") -> bool:
        """
        Reset rate limit for a key.

        Args:
            key: Rate limit key
            algorithm: Algorithm used

        Returns:
            True if reset successful
        """
        try:
            if algorithm == "fixed_window":
                # Clear all windows for this key
                pattern = f"rate_limit:fw:{key}:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            elif algorithm == "sliding_window":
                self.redis.delete(f"rate_limit:sw:{key}")
            elif algorithm == "token_bucket":
                self.redis.delete(f"rate_limit:tb:{key}")

            self.logger.info(f"Rate limit reset for key: {key}")
            return True

        except RedisError as e:
            self.logger.error(f"Error resetting rate limit: {e}")
            return False

    def get_all_limits(self, pattern: str = "*") -> Dict[str, Any]:
        """
        Get all rate limit keys matching pattern.

        Args:
            pattern: Redis key pattern

        Returns:
            Dictionary of keys and their usage
        """
        try:
            keys = self.redis.keys(f"rate_limit:*:{pattern}")
            result = {}

            for key in keys:
                key_str = key.decode('utf-8')
                # Extract the actual key part
                parts = key_str.split(':')
                if len(parts) >= 3:
                    actual_key = ':'.join(parts[2:])
                    result[actual_key] = self.get_usage(actual_key)

            return result

        except RedisError as e:
            self.logger.error(f"Error getting all limits: {e}")
            return {"error": "redis_unavailable"}

# Global rate limiter instance
_rate_limiter: Optional[DistributedRateLimiter] = None

def get_rate_limiter(redis_client: Optional[Redis] = None) -> DistributedRateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        if redis_client is None:
            raise ValueError("Redis client required for rate limiter initialization")
        _rate_limiter = DistributedRateLimiter(redis_client)
    return _rate_limiter

def init_rate_limiter(redis_client: Redis) -> DistributedRateLimiter:
    """Initialize global rate limiter"""
    global _rate_limiter
    _rate_limiter = DistributedRateLimiter(redis_client)
    return _rate_limiter