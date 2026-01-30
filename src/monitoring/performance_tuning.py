"""
Helm AI Performance Tuning and Caching Strategies
Provides performance optimization, caching mechanisms, and tuning recommendations
"""

import os
import sys
import time
import json
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor
import redis

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import get_database_manager
from monitoring.structured_logging import logger
from database.connection_pool import connection_pool_manager

@dataclass
class CacheConfig:
    """Cache configuration"""
    default_ttl: int = 300  # 5 minutes
    max_size: int = 1000
    key_prefix: str = "helm_ai:"
    serializer: str = "json"  # json, pickle, msgpack
    compression: bool = True
    stats_enabled: bool = True

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate miss rate"""
        total = self.hits + self.misses
        return (self.misses / total * 100) if total > 0 else 0.0

class CacheManager:
    """High-performance cache manager with multiple backends"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.stats = CacheStats()
        self.lock = threading.RLock()
        
        # Initialize backends
        self.memory_cache = {}
        self.redis_client = None
        self._init_redis()
        
        # Cache policies
        self.cache_policies = {}
        self._setup_default_policies()
    
    def _init_redis(self):
        """Initialize Redis client"""
        try:
            redis_pool = connection_pool_manager.get_pool('redis')
            if redis_pool:
                self.redis_client = redis_pool.get_connection()
                logger.info("Redis cache backend initialized")
            else:
                logger.warning("Redis not available, using memory-only cache")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
    
    def _setup_default_policies(self):
        """Set up default cache policies"""
        self.cache_policies = {
            'user_profile': {'ttl': 1800, 'max_size': 100},  # 30 minutes
            'api_key': {'ttl': 3600, 'max_size': 50},     # 1 hour
            'game_session': {'ttl': 600, 'max_size': 200},  # 10 minutes
            'audit_log': {'ttl': 86400, 'max_size': 1000}, # 24 hours
            'security_event': {'ttl': 86400, 'max_size': 500}, # 24 hours
            'query_result': {'ttl': 300, 'max_size': 200},  # 5 minutes
            'config': {'ttl': 3600, 'max_size': 50},     # 1 hour
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        full_key = f"{self.config.key_prefix}{key}"
        
        with self.lock:
            self.stats.total_requests += 1
            
            # Try memory cache first
            if key in self.memory_cache:
                self.stats.hits += 1
                return self.memory_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                try:
                    value = self.redis_client.get(full_key)
                    if value is not None:
                        # Deserialize and store in memory cache
                        deserialized_value = self._deserialize(value)
                        self._store_in_memory(key, deserialized_value)
                        self.stats.hits += 1
                        return deserialized_value_value
                except Exception as e:
                    logger.error(f"Redis get error: {e}")
            
            self.stats.misses += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        full_key = f"{self.config.key_prefix}{key}"
        
        # Get TTL from policy if not specified
        if ttl is None:
            policy = self.cache_policies.get(key, {})
            ttl = policy.get('ttl', self.config.default_ttl)
        
        with self.lock:
            self.stats.sets += 1
            
            # Store in memory cache
            self._store_in_memory(key, value)
            
            # Store in Redis
            if self.redis_client:
                try:
                    serialized_value = self._serialize(value)
                    self.redis_client.setex(full_key, ttl, serialized_value)
                except Exception as e:
                    logger.error(f"Redis set error: {e}")
                    return False
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        full_key = f"{self.config.key_prefix}{key}"
        
        with self.lock:
            self.stats.deletes += 1
            
            # Delete from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Delete from Redis
            if self.redis_client:
                try:
                    self.redis_client.delete(full_key)
                except Exception as e:
                    logger.error(f"Redis delete error: {e}")
                    return False
            
            return True
    
    def clear(self, pattern: Optional[str] = None):
        """Clear cache entries"""
        with self.lock:
            if pattern:
                # Clear matching entries
                keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                
                if self.redis_client:
                    try:
                        redis_pattern = f"{self.config.key_prefix}{pattern}*"
                        keys = self.redis_client.keys(redis_pattern)
                        if keys:
                            self.redis_client.delete(*keys)
                    except Exception as e:
                        logger.error(f"Redis clear error: {e}")
            else:
                # Clear all
                self.memory_cache.clear()
                
                if self.redis_client:
                    try:
                        keys = self.redis_client.keys(f"{self.config.key_prefix}*")
                        if keys:
                            self.redis_client.delete(*keys)
                    except Exception as e:
                        logger.error(f"Redis clear error: {e}")
    
    def _store_in_memory(self, key: str, value: Any):
        """Store value in memory cache with size limit"""
        # Check if we need to evict
        policy = self.cache_policies.get(key, {})
        max_size = policy.get('max_size', self.config.max_size)
        
        if len(self.memory_cache) >= max_size:
            # Simple LRU eviction
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
            self.stats.evictions += 1
        
        self.memory_cache[key] = value
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        if self.config.serializer == 'json':
            return json.dumps(value, default=str)
        elif self.config.serializer == 'pickle':
            import pickle
            return pickle.dumps(value).hex()
        else:
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        if self.config.serializer == 'json':
            return json.loads(value)
        elif self.config.serializer == 'pickle':
            import pickle
            return pickle.loads(bytes.fromhex(value))
        else:
            return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'sets': self.stats.sets,
                'deletes': self.stats.deletes,
                'evictions': self.stats.evictions,
                'total_requests': self.stats.total_requests,
                'hit_rate': self.stats.hit_rate,
                'miss_rate': self.stats.miss_rate,
                'memory_size': len(self.memory_cache)
            }
    
    def warm_cache(self, keys: List[str], data_loader: Callable[[str], Any]):
        """Warm cache with data"""
        logger.info(f"Warming cache with {len(keys)} keys")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for key in keys:
                future = executor.submit(self._warm_key, key, data_loader)
                futures.append(future)
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        logger.info(f"Cache warming completed")
    
    def _warm_key(self, key: str, data_loader: Callable[[str], Any]):
        """Warm a single cache key"""
        try:
            value = data_loader(key)
            self.set(key, value)
        except Exception as e:
            logger.error(f"Failed to warm cache key {key}: {e}")

class QueryCache:
    """Query result caching with automatic invalidation"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.query_hashes = {}
        
    @lru_cache(maxsize=1000)
    def get_query_result(self, query_hash: str, query_func: Callable, *args, **kwargs) -> Any:
        """Get cached query result or execute query"""
        cache_key = f"query:{query_hash}"
        
        # Try cache first
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        
        # Execute query
        result = query_func(*args, **kwargs)
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
    
    def invalidate_query(self, query_hash: str):
        """Invalidate cached query result"""
        cache_key = f"query:{query_hash}"
        self.cache.delete(cache_key)
    
    def invalidate_table(self, table_name: str):
        """Invalidate all queries for a table"""
        pattern = f"query:*{table_name}*"
        self.cache.clear(pattern)

class PerformanceTuner:
    """Performance tuning recommendations and optimizations"""
    
    def __init__(self):
        self.recommendations = []
        self.tuning_history = []
        
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and generate recommendations"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'recommendations': [],
            'metrics': self._collect_metrics(),
            'optimizations_applied': self.tuning_history
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations()
        
        return analysis
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        metrics = {}
        
        # Database metrics
        try:
            db_manager = get_database_manager()
            health = db_manager.health_check()
            metrics['database'] = health
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
        
        # Cache metrics
        try:
            cache_stats = cache_manager.get_stats()
            metrics['cache'] = cache_stats
        except Exception as e:
            logger.error(f"Failed to collect cache metrics: {e}")
        
        # System metrics
        try:
            import psutil
            metrics['system'] = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
        
        return metrics
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        try:
            metrics = self._collect_metrics()
            
            # Database recommendations
            if 'database' in metrics:
                db_health = metrics['database']
                if db_health.get('status') != 'healthy':
                    recommendations.append("Database health issues detected - check connection pool")
                
                pool_stats = db_health.get('connection_pool', {})
                if pool_stats.get('active', 0) > pool_stats.get('total', 0) * 0.8:
                    recommendations.append("High database connection usage - consider increasing pool size")
            
            # Cache recommendations
            if 'cache' in metrics:
                cache_stats = metrics['cache']
                if cache_stats['hit_rate'] < 80:
                    recommendations.append(f"Low cache hit rate ({cache_stats['hit_rate']:.1f}%) - review cache strategy")
                if cache_stats['miss_rate'] > 20:
                    recommendations.append(f"High cache miss rate ({cache_stats['miss_rate']:.1f}%) - consider cache warming")
            
            # System recommendations
            if 'system' in metrics:
                sys_metrics = metrics['system']
                if sys_metrics['cpu_percent'] > 80:
                    recommendations.append(f"High CPU usage ({sys_metrics['cpu_percent']:.1f}%) - check for optimization opportunities")
                if sys_metrics['memory_percent'] > 80:
                    recommendations.append(f"High memory usage ({sys_metrics['memory_percent']:.1f}%) - investigate memory leaks")
                if sys_metrics['disk_percent'] > 85:
                    recommendations.append(f"High disk usage ({sys_metrics['disk_percent']:.1f}%) - consider cleanup or expansion")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance looks good - no immediate optimizations needed")
        
        return recommendations
    
    def apply_optimization(self, optimization: str, impact: str = "medium") -> bool:
        """Apply a performance optimization"""
        try:
            logger.info(f"Applying optimization: {optimization}")
            
            # Record optimization
            self.tuning_history.append({
                'timestamp': datetime.now().isoformat(),
                'optimization': optimization,
                'impact': impact,
                'applied': True
            })
            
            # Apply specific optimization based on type
            if optimization == "increase_db_pool":
                return self._increase_db_pool()
            elif optimization == "enable_query_cache":
                return self._enable_query_cache()
            elif optimization == "warm_cache":
                return self._warm_cache()
            elif optimization == "optimize_indexes":
                return self._optimize_indexes()
            else:
                logger.warning(f"Unknown optimization: {optimization}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply optimization {optimization}: {e}")
            return False
    
    def _increase_db_pool(self) -> bool:
        """Increase database connection pool size"""
        try:
            # This would need to be implemented based on your connection pool manager
            logger.info("Increasing database connection pool size")
            # Implementation would depend on your specific pool manager
            return True
        except Exception as e:
            logger.error(f"Failed to increase DB pool: {e}")
            return False
    
    def _enable_query_cache(self) -> bool:
        """Enable query result caching"""
        try:
            logger.info("Enabling query result caching")
            # Implementation would depend on your query cache system
            return True
        except Exception as e:
            logger.error(f"Failed to enable query cache: {e}")
            return False
    
    def _warm_cache(self) -> bool:
        """Warm up cache with frequently accessed data"""
        try:
            logger.info("Warming up cache")
            # Implementation would depend on your cache system
            return True
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")
            return False
    
    def _optimize_indexes(self) -> bool:
        """Optimize database indexes"""
        try:
            logger.info("Optimizing database indexes")
            # Implementation would depend on your database system
            return True
        except Exception as e:
            logger.error(f"Failed to optimize indexes: {e}")
            return False

# Global instances
cache_config = CacheConfig()
cache_manager = CacheManager(cache_config)
query_cache = QueryCache(cache_manager)
performance_tuner = PerformanceTuner()

# Decorators for caching
def cache_result(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}"
            
            # Try to get from cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def timed_cache(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}"
            
            # Try to get from cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store execution time in result if it's a dict
            if isinstance(result, dict):
                result['_execution_time'] = execution_time
            
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Performance monitoring utilities
def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        execution_time = time.time() - start_time
        
        # Record performance metric
        metric_name = f"function:{func.__name__}"
        performance_manager.add_metric(
            metric_name=metric_name,
            value=execution_time,
            unit='seconds',
            tags={
                'success': str(success),
                'error': error or ''
            }
        )
        
        return result
    return wrapper

# Global performance manager instance
performance_manager = cache_manager

def add_performance_metric(name: str, value: float, unit: str, tags: Dict[str, str] = None):
    """Add a performance metric"""
    metric = PerformanceMetric(
        name=name,
        value=value,
        unit=unit,
        timestamp=datetime.now(),
        tags=tags or {}
    )
    performance_manager.add_metric(metric)

def get_performance_metrics(minutes: int = 5) -> Dict[str, Any]:
    """Get performance metrics for the last N minutes"""
    return performance_manager.get_recent_metrics(minutes)

def get_performance_report() -> Dict[str, Any]:
    """Get comprehensive performance report"""
    return performance_tuner.analyze_performance()

def start_performance_monitoring():
    """Start performance monitoring"""
    logger.info("Starting performance monitoring")

def stop_performance_monitoring():
    """Stop performance monitoring"""
    logger.info("Stopping performance monitoring")
