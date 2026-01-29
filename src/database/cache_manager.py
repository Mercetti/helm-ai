"""
Helm AI Cache Manager
This module provides multi-level caching strategies and cache management
"""

import os
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import redis
import threading
from collections import OrderedDict
import weakref

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheLevel(Enum):
    """Cache levels"""
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"

class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    avg_access_time: float = 0.0

class MemoryCache:
    """In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        self.lock = threading.RLock()
        
        # Background cleanup thread
        self._start_cleanup_thread()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        start_time = time.time()
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if entry.ttl_seconds and (datetime.now() - entry.created_at).total_seconds() > entry.ttl_seconds:
                    del self.cache[key]
                    self.stats.misses += 1
                    return None
                
                # Update access info
                entry.accessed_at = datetime.now()
                entry.access_count += 1
                
                # Move to end (LRU)
                self.cache.move_to_end(key)
                
                self.stats.hits += 1
                self._update_access_time(time.time() - start_time)
                return entry.value
            else:
                self.stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache"""
        with self.lock:
            # Calculate size
            try:
                size_bytes = len(json.dumps(value).encode('utf-8'))
            except:
                size_bytes = len(str(value))
            
            # Check memory limits
            if size_bytes > self.max_memory_bytes:
                logger.warning(f"Value too large for cache: {size_bytes} bytes")
                return False
            
            # Evict if necessary
            while (len(self.cache) >= self.max_size or 
                   self._get_total_size() + size_bytes > self.max_memory_bytes):
                if not self._evict_lru():
                    break
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl_seconds=ttl_seconds,
                size_bytes=size_bytes,
                tags=tags or []
            )
            
            self.cache[key] = entry
            self.cache.move_to_end(key)
            self.stats.sets += 1
            self._update_stats()
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats.deletes += 1
                self._update_stats()
                return True
            return False
    
    def clear(self, tags: List[str] = None):
        """Clear cache entries"""
        with self.lock:
            if tags:
                # Clear entries with specific tags
                keys_to_delete = [key for key, entry in self.cache.items()
                                if any(tag in entry.tags for tag in tags)]
                for key in keys_to_delete:
                    del self.cache[key]
            else:
                # Clear all entries
                self.cache.clear()
            
            self._update_stats()
    
    def _evict_lru(self) -> bool:
        """Evict least recently used entry"""
        if self.cache:
            key, entry = self.cache.popitem(last=False)
            self.stats.evictions += 1
            self._update_stats()
            return True
        return False
    
    def _get_total_size(self) -> int:
        """Get total cache size in bytes"""
        return sum(entry.size_bytes for entry in self.cache.values())
    
    def _update_stats(self):
        """Update cache statistics"""
        self.stats.entry_count = len(self.cache)
        self.stats.size_bytes = self._get_total_size()
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = (self.stats.hits / total_requests * 100) if total_requests > 0 else 0
    
    def _update_access_time(self, access_time: float):
        """Update average access time"""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.avg_access_time = (
                (self.stats.avg_access_time * (total_requests - 1) + access_time) / total_requests
            )
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_expired():
            while True:
                try:
                    self._cleanup_expired_entries()
                    threading.Event().wait(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                    threading.Event().wait(60)
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired_entries(self):
        """Clean up expired entries"""
        with self.lock:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.ttl_seconds and (current_time - entry.created_at).total_seconds() > entry.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                self.stats.evictions += 1
            
            if expired_keys:
                self._update_stats()
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


class RedisCache:
    """Redis-based distributed cache"""
    
    def __init__(self, redis_url: str = None, key_prefix: str = "helm_ai:"):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.key_prefix = key_prefix
        self.stats = CacheStats()
        
        try:
            self.client = redis.from_url(self.redis_url)
            self.client.ping()  # Test connection
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def _make_key(self, key: str) -> str:
        """Create Redis key with prefix"""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.client:
            return None
        
        start_time = time.time()
        
        try:
            redis_key = self._make_key(key)
            data = self.client.get(redis_key)
            
            if data:
                value = json.loads(data.decode('utf-8'))
                self.stats.hits += 1
                self._update_access_time(time.time() - start_time)
                return value
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in Redis cache"""
        if not self.client:
            return False
        
        try:
            redis_key = self._make_key(key)
            serialized_data = json.dumps(value).encode('utf-8')
            
            if ttl_seconds:
                result = self.client.setex(redis_key, ttl_seconds, serialized_data)
            else:
                result = self.client.set(redis_key, serialized_data)
            
            if result:
                self.stats.sets += 1
                
                # Store tags in separate set for tag-based invalidation
                if tags:
                    for tag in tags:
                        self.client.sadd(f"{self.key_prefix}tag:{tag}", redis_key)
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self.client:
            return False
        
        try:
            redis_key = self._make_key(key)
            result = self.client.delete(redis_key)
            
            if result:
                self.stats.deletes += 1
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self, tags: List[str] = None):
        """Clear cache entries"""
        if not self.client:
            return
        
        try:
            if tags:
                # Clear entries with specific tags
                for tag in tags:
                    tag_key = f"{self.key_prefix}tag:{tag}"
                    keys = self.client.smembers(tag_key)
                    if keys:
                        self.client.delete(*keys)
                    self.client.delete(tag_key)
            else:
                # Clear all entries with prefix
                pattern = f"{self.key_prefix}*"
                keys = self.client.keys(pattern)
                if keys:
                    self.client.delete(*keys)
            
            logger.info(f"Cleared Redis cache entries for tags: {tags}")
            
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def get_stats(self) -> CacheStats:
        """Get Redis cache statistics"""
        if not self.client:
            return self.stats
        
        try:
            info = self.client.info()
            self.stats.entry_count = info.get('db0', {}).get('keys', 0)
            self.stats.size_bytes = info.get('used_memory', 0)
            
            total_requests = self.stats.hits + self.stats.misses
            self.stats.hit_rate = (self.stats.hits / total_requests * 100) if total_requests > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
        
        return self.stats
    
    def _update_access_time(self, access_time: float):
        """Update average access time"""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.avg_access_time = (
                (self.stats.avg_access_time * (total_requests - 1) + access_time) / total_requests
            )


class CacheManager:
    """Multi-level cache manager"""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 memory_cache_mb: int = 100,
                 redis_url: str = None,
                 cache_strategy: CacheStrategy = CacheStrategy.LRU):
        
        self.cache_strategy = cache_strategy
        
        # Initialize cache levels
        self.memory_cache = MemoryCache(memory_cache_size, memory_cache_mb)
        self.redis_cache = RedisCache(redis_url) if redis_url or os.getenv('REDIS_URL') else None
        
        # Global statistics
        self.global_stats = CacheStats()
        
        logger.info(f"Cache manager initialized with strategy: {cache_strategy.value}")
    
    def get(self, key: str, use_memory: bool = True, use_redis: bool = True) -> Optional[Any]:
        """Get value from cache hierarchy"""
        start_time = time.time()
        
        # Try memory cache first
        if use_memory:
            value = self.memory_cache.get(key)
            if value is not None:
                self.global_stats.hits += 1
                self._update_global_access_time(time.time() - start_time)
                return value
        
        # Try Redis cache
        if use_redis and self.redis_cache:
            value = self.redis_cache.get(key)
            if value is not None:
                # Store in memory cache for faster access
                self.memory_cache.set(key, value)
                self.global_stats.hits += 1
                self._update_global_access_time(time.time() - start_time)
                return value
        
        # Cache miss
        self.global_stats.misses += 1
        self._update_global_access_time(time.time() - start_time)
        return None
    
    def set(self, 
            key: str, 
            value: Any, 
            ttl_seconds: Optional[int] = None,
            tags: List[str] = None,
            use_memory: bool = True,
            use_redis: bool = True) -> bool:
        """Set value in cache hierarchy"""
        success = True
        
        # Set in memory cache
        if use_memory:
            success &= self.memory_cache.set(key, value, ttl_seconds, tags)
        
        # Set in Redis cache
        if use_redis and self.redis_cache:
            success &= self.redis_cache.set(key, value, ttl_seconds, tags)
        
        if success:
            self.global_stats.sets += 1
        
        return success
    
    def delete(self, key: str, use_memory: bool = True, use_redis: bool = True) -> bool:
        """Delete key from cache hierarchy"""
        success = True
        
        # Delete from memory cache
        if use_memory:
            success &= self.memory_cache.delete(key)
        
        # Delete from Redis cache
        if use_redis and self.redis_cache:
            success &= self.redis_cache.delete(key)
        
        if success:
            self.global_stats.deletes += 1
        
        return success
    
    def clear(self, tags: List[str] = None, use_memory: bool = True, use_redis: bool = True):
        """Clear cache entries"""
        if use_memory:
            self.memory_cache.clear(tags)
        
        if use_redis and self.redis_cache:
            self.redis_cache.clear(tags)
        
        logger.info(f"Cleared cache entries for tags: {tags}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'global': {
                'hits': self.global_stats.hits,
                'misses': self.global_stats.misses,
                'sets': self.global_stats.sets,
                'deletes': self.global_stats.deletes,
                'hit_rate': self.global_stats.hit_rate,
                'avg_access_time': self.global_stats.avg_access_time
            },
            'memory': {
                'hits': self.memory_cache.stats.hits,
                'misses': self.memory_cache.stats.misses,
                'sets': self.memory_cache.stats.sets,
                'deletes': self.memory_cache.stats.deletes,
                'evictions': self.memory_cache.stats.evictions,
                'entry_count': self.memory_cache.stats.entry_count,
                'size_bytes': self.memory_cache.stats.size_bytes,
                'hit_rate': self.memory_cache.stats.hit_rate,
                'avg_access_time': self.memory_cache.stats.avg_access_time
            }
        }
        
        if self.redis_cache:
            redis_stats = self.redis_cache.get_stats()
            stats['redis'] = {
                'hits': redis_stats.hits,
                'misses': redis_stats.misses,
                'sets': redis_stats.sets,
                'deletes': redis_stats.deletes,
                'entry_count': redis_stats.entry_count,
                'size_bytes': redis_stats.size_bytes,
                'hit_rate': redis_stats.hit_rate,
                'avg_access_time': redis_stats.avg_access_time
            }
        
        return stats
    
    def _update_global_access_time(self, access_time: float):
        """Update global average access time"""
        total_requests = self.global_stats.hits + self.global_stats.misses
        if total_requests > 0:
            self.global_stats.avg_access_time = (
                (self.global_stats.avg_access_time * (total_requests - 1) + access_time) / total_requests
            )


# Decorators for caching
def cache_result(ttl_seconds: int = 3600, 
                key_func: Callable = None,
                tags: List[str] = None,
                use_memory: bool = True,
                use_redis: bool = True):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, use_memory, use_redis)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl_seconds, tags, use_memory, use_redis)
            
            return result
        
        return wrapper
    return decorator


def cache_query(ttl_seconds: int = 3600,
               table_name: str = None,
               use_memory: bool = True,
               use_redis: bool = True):
    """Decorator to cache database query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key based on query parameters
            query_hash = hashlib.sha256(str(args).encode()).hexdigest()
            cache_key = f"query:{table_name or func.__name__}:{query_hash}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, use_memory, use_redis)
            if cached_result is not None:
                return cached_result
            
            # Execute query and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl_seconds, ['query'], use_memory, use_redis)
            
            return result
        
        return wrapper
    return decorator


class CacheWarmer:
    """Cache warming utility"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def warm_cache(self, warmup_functions: List[Callable]):
        """Warm cache with predefined data"""
        logger.info("Starting cache warming...")
        
        for func in warmup_functions:
            try:
                start_time = time.time()
                func()
                duration = time.time() - start_time
                logger.info(f"Cache warming function {func.__name__} completed in {duration:.2f}s")
            except Exception as e:
                logger.error(f"Cache warming function {func.__name__} failed: {e}")
        
        logger.info("Cache warming completed")
    
    def warm_common_queries(self):
        """Warm cache with common queries"""
        # This would be implemented with actual common queries
        pass


# Global cache manager instance
cache_manager = CacheManager()
