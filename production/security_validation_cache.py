#!/usr/bin/env python3
"""
Stellar Logic AI - Security Validation Caching System
Advanced caching layer for security validations to improve performance
"""

import os
import sys
import json
import time
import logging
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import pickle
import sqlite3

@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    ttl: int  # Time to live in seconds

@dataclass
class CacheStats:
    """Cache statistics data structure"""
    cache_type: str
    total_entries: int
    hit_count: int
    miss_count: int
    hit_rate: float
    memory_usage: int
    eviction_count: int
    last_cleanup: datetime

class SecurityValidationCache:
    """Security validation caching system for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.production_path, "logs/security_cache.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Cache stores
        self.memory_cache = MemoryCacheStore()
        self.redis_cache = RedisCacheStore()
        self.file_cache = FileCacheStore(self.production_path)
        self.database_cache = DatabaseCacheStore(self.production_path)
        
        # Cache managers
        self.cache_managers = {
            "authentication": AuthenticationCacheManager(),
            "authorization": AuthorizationCacheManager(),
            "rate_limiting": RateLimitingCacheManager(),
            "csrf_protection": CSRFProtectionCacheManager(),
            "input_validation": InputValidationCacheManager(),
            "threat_detection": ThreatDetectionCacheManager(),
            "security_headers": SecurityHeadersCacheManager(),
            "compliance_checks": ComplianceCacheManager()
        }
        
        # Cache statistics
        self.cache_stats = defaultdict(lambda: {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage": 0
        })
        
        # Load configuration
        self.load_configuration()
        
        # Initialize cache cleanup
        self.start_cache_cleanup()
        
        self.logger.info("Security Validation Cache initialized")
    
    def load_configuration(self):
        """Load cache configuration"""
        config_file = os.path.join(self.production_path, "config/security_cache_config.json")
        
        default_config = {
            "security_cache": {
                "enabled": True,
                "default_ttl": 300,  # 5 minutes
                "max_memory_size": 100 * 1024 * 1024,  # 100MB
                "cleanup_interval": 60,  # 1 minute
                "cache_stores": {
                    "memory": {"enabled": True, "max_size": 1000},
                    "redis": {"enabled": False, "host": "localhost", "port": 6379},
                    "file": {"enabled": True, "directory": "cache"},
                    "database": {"enabled": True, "table": "security_cache"}
                },
                "cache_managers": {
                    "authentication": {"enabled": True, "ttl": 1800},     # 30 minutes
                    "authorization": {"enabled": True, "ttl": 600},       # 10 minutes
                    "rate_limiting": {"enabled": True, "ttl": 60},        # 1 minute
                    "csrf_protection": {"enabled": True, "ttl": 3600},    # 1 hour
                    "input_validation": {"enabled": True, "ttl": 300},    # 5 minutes
                    "threat_detection": {"enabled": True, "ttl": 1800},    # 30 minutes
                    "security_headers": {"enabled": True, "ttl": 86400},   # 24 hours
                    "compliance_checks": {"enabled": True, "ttl": 3600}    # 1 hour
                },
                "performance": {
                    "max_cache_size": 10000,
                    "eviction_policy": "LRU",
                    "compression_enabled": True,
                    "serialization_format": "pickle"
                }
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                # Save default configuration
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.logger.info("Created default security cache configuration")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = default_config
    
    def get_cached_result(self, cache_type: str, key: str, validation_func: callable, *args, **kwargs) -> Any:
        """Get cached result or compute and cache it"""
        if not self.config["security_cache"]["enabled"]:
            return validation_func(*args, **kwargs)
        
        if not self.config["security_cache"]["cache_managers"][cache_type]["enabled"]:
            return validation_func(*args, **kwargs)
        
        # Generate cache key
        cache_key = self.generate_cache_key(cache_type, key, args, kwargs)
        
        # Try to get from cache
        cached_result = self.get_from_cache(cache_key)
        
        if cached_result is not None:
            self.cache_stats[cache_type]["hits"] += 1
            self.logger.debug(f"Cache hit for {cache_type}: {cache_key}")
            return cached_result
        
        # Cache miss - compute result
        self.cache_stats[cache_type]["misses"] += 1
        self.logger.debug(f"Cache miss for {cache_type}: {cache_key}")
        
        result = validation_func(*args, **kwargs)
        
        # Cache the result
        ttl = self.config["security_cache"]["cache_managers"][cache_type]["ttl"]
        self.set_cache(cache_key, result, ttl)
        
        return result
    
    def generate_cache_key(self, cache_type: str, key: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key"""
        # Create a hash of the parameters
        key_data = {
            "cache_type": cache_type,
            "key": key,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        hash_key = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"{cache_type}:{hash_key[:16]}"
    
    def get_from_cache(self, cache_key: str) -> Any:
        """Get value from cache (try multiple stores)"""
        # Try memory cache first (fastest)
        if self.config["security_cache"]["cache_stores"]["memory"]["enabled"]:
            value = self.memory_cache.get(cache_key)
            if value is not None:
                return value
        
        # Try file cache
        if self.config["security_cache"]["cache_stores"]["file"]["enabled"]:
            value = self.file_cache.get(cache_key)
            if value is not None:
                # Store in memory cache for faster access next time
                self.memory_cache.set(cache_key, value, 300)
                return value
        
        # Try database cache
        if self.config["security_cache"]["cache_stores"]["database"]["enabled"]:
            value = self.database_cache.get(cache_key)
            if value is not None:
                # Store in memory and file cache
                self.memory_cache.set(cache_key, value, 300)
                self.file_cache.set(cache_key, value, 300)
                return value
        
        return None
    
    def set_cache(self, cache_key: str, value: Any, ttl: int):
        """Set value in cache stores"""
        # Set in memory cache
        if self.config["security_cache"]["cache_stores"]["memory"]["enabled"]:
            self.memory_cache.set(cache_key, value, ttl)
        
        # Set in file cache
        if self.config["security_cache"]["cache_stores"]["file"]["enabled"]:
            self.file_cache.set(cache_key, value, ttl)
        
        # Set in database cache
        if self.config["security_cache"]["cache_stores"]["database"]["enabled"]:
            self.database_cache.set(cache_key, value, ttl)
    
    def invalidate_cache(self, cache_type: str = None, pattern: str = None):
        """Invalidate cache entries"""
        if cache_type:
            # Invalidate specific cache type
            if pattern:
                # Invalidate by pattern
                self.memory_cache.invalidate_pattern(f"{cache_type}:*")
                self.file_cache.invalidate_pattern(f"{cache_type}:*")
                self.database_cache.invalidate_pattern(f"{cache_type}:*")
            else:
                # Invalidate all of this type
                self.memory_cache.invalidate_type(cache_type)
                self.file_cache.invalidate_type(cache_type)
                self.database_cache.invalidate_type(cache_type)
        else:
            # Invalidate all cache
            self.memory_cache.clear()
            self.file_cache.clear()
            self.database_cache.clear()
        
        self.logger.info(f"Cache invalidated: {cache_type or 'all'}")
    
    def start_cache_cleanup(self):
        """Start background cache cleanup"""
        def cleanup():
            while True:
                try:
                    # Clean expired entries
                    self.memory_cache.cleanup()
                    self.file_cache.cleanup()
                    self.database_cache.cleanup()
                    
                    # Update statistics
                    self.update_cache_statistics()
                    
                    time.sleep(self.config["security_cache"]["cleanup_interval"])
                    
                except Exception as e:
                    self.logger.error(f"Error in cache cleanup: {str(e)}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
        
        self.logger.info("Cache cleanup thread started")
    
    def update_cache_statistics(self):
        """Update cache statistics"""
        for cache_type in self.cache_managers.keys():
            stats = self.cache_stats[cache_type]
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            # Update memory usage
            stats["memory_usage"] = self.memory_cache.get_memory_usage()
            
            self.logger.debug(f"Cache stats for {cache_type}: Hit rate {hit_rate:.2f}%, "
                           f"Memory usage {stats['memory_usage']} bytes")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        overall_stats = {
            "total_hits": sum(stats["hits"] for stats in self.cache_stats.values()),
            "total_misses": sum(stats["misses"] for stats in self.cache_stats.values()),
            "total_evictions": sum(stats["evictions"] for stats in self.cache_stats.values()),
            "total_memory_usage": sum(stats["memory_usage"] for stats in self.cache_stats.values())
        }
        
        # Calculate overall hit rate
        total_requests = overall_stats["total_hits"] + overall_stats["total_misses"]
        overall_stats["hit_rate"] = (overall_stats["total_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "overall": overall_stats,
            "by_cache_type": dict(self.cache_stats),
            "cache_stores": {
                "memory": self.memory_cache.get_stats(),
                "file": self.file_cache.get_stats(),
                "database": self.database_cache.get_stats()
            },
            "performance_metrics": self.get_performance_metrics()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        return {
            "average_response_time": self.measure_cache_performance(),
            "cache_efficiency": self.calculate_cache_efficiency(),
            "memory_utilization": self.calculate_memory_utilization(),
            "eviction_rate": self.calculate_eviction_rate()
        }
    
    def measure_cache_performance(self) -> float:
        """Measure average cache response time"""
        start_time = time.time()
        
        # Perform cache operations
        test_key = "performance_test"
        test_value = {"test": "data"}
        
        # Set operation
        self.set_cache(test_key, test_value, 60)
        
        # Get operation
        self.get_from_cache(test_key)
        
        # Delete operation
        self.memory_cache.delete(test_key)
        
        return (time.time() - start_time) * 1000  # Return in milliseconds
    
    def calculate_cache_efficiency(self) -> float:
        """Calculate cache efficiency"""
        total_requests = sum(stats["hits"] + stats["misses"] for stats in self.cache_stats.values())
        total_hits = sum(stats["hits"] for stats in self.cache_stats.values())
        
        return (total_hits / total_requests * 100) if total_requests > 0 else 0
    
    def calculate_memory_utilization(self) -> float:
        """Calculate memory utilization percentage"""
        max_memory = self.config["security_cache"]["max_memory_size"]
        used_memory = sum(stats["memory_usage"] for stats in self.cache_stats.values())
        
        return (used_memory / max_memory * 100) if max_memory > 0 else 0
    
    def calculate_eviction_rate(self) -> float:
        """Calculate eviction rate"""
        total_evictions = sum(stats["evictions"] for stats in self.cache_stats.values())
        total_entries = sum(self.memory_cache.get_size() for _ in self.cache_stats.keys())
        
        return (total_evictions / total_entries * 100) if total_entries > 0 else 0

# Cache Store Implementations
class MemoryCacheStore:
    """In-memory cache store"""
    
    def __init__(self):
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Any:
        """Get value from memory cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if datetime.now() > entry.expires_at:
                    del self.cache[key]
                    return None
                
                # Update access info
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Move to end of access order (LRU)
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.value
            
            return None
    
    def set(self, key: str, value: Any, ttl: int):
        """Set value in memory cache"""
        with self.lock:
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=ttl),
                access_count=1,
                last_accessed=datetime.now(),
                ttl=ttl
            )
            
            self.cache[key] = entry
            
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            # Evict if necessary (simple LRU)
            if len(self.cache) > 1000:  # Max size
                self.evict_lru()
    
    def delete(self, key: str):
        """Delete key from memory cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
    
    def clear(self):
        """Clear memory cache"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def cleanup(self):
        """Clean up expired entries"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if datetime.now() > entry.expires_at:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
    
    def evict_lru(self):
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    def get_memory_usage(self) -> int:
        """Get memory usage in bytes"""
        return len(pickle.dumps(self.cache))
    
    def get_size(self) -> int:
        """Get cache size"""
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "type": "memory",
            "size": len(self.cache),
            "memory_usage": self.get_memory_usage()
        }
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate entries matching pattern"""
        with self.lock:
            keys_to_remove = []
            for key in self.cache.keys():
                if pattern.replace("*", "") in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
    
    def invalidate_type(self, cache_type: str):
        """Invalidate all entries of a specific type"""
        self.invalidate_pattern(f"{cache_type}:*")

class FileCacheStore:
    """File-based cache store"""
    
    def __init__(self, production_path: str):
        self.cache_dir = os.path.join(production_path, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Any:
        """Get value from file cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    entry_data = pickle.load(f)
                
                # Check if expired
                if datetime.now() > entry_data['expires_at']:
                    os.remove(cache_file)
                    return None
                
                return entry_data['value']
            
        except Exception as e:
            logging.error(f"Error reading from file cache: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int):
        """Set value in file cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            
            entry_data = {
                'key': key,
                'value': value,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl),
                'ttl': ttl
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(entry_data, f)
                
        except Exception as e:
            logging.error(f"Error writing to file cache: {str(e)}")
    
    def clear(self):
        """Clear file cache"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            logging.error(f"Error clearing file cache: {str(e)}")
    
    def cleanup(self):
        """Clean up expired entries"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(cache_file, 'rb') as f:
                            entry_data = pickle.load(f)
                        
                        if datetime.now() > entry_data['expires_at']:
                            os.remove(cache_file)
                    except:
                        # Remove corrupted files
                        os.remove(cache_file)
                        
        except Exception as e:
            logging.error(f"Error in file cache cleanup: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.cache')]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in cache_files)
            
            return {
                "type": "file",
                "size": len(cache_files),
                "disk_usage": total_size
            }
        except Exception as e:
            logging.error(f"Error getting file cache stats: {str(e)}")
            return {"type": "file", "size": 0, "disk_usage": 0}
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate entries matching pattern"""
        try:
            pattern_prefix = pattern.replace("*", "")
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache') and pattern_prefix in filename:
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            logging.error(f"Error invalidating file cache pattern: {str(e)}")
    
    def invalidate_type(self, cache_type: str):
        """Invalidate all entries of a specific type"""
        self.invalidate_pattern(f"{cache_type}:*")

class DatabaseCacheStore:
    """Database-based cache store"""
    
    def __init__(self, production_path: str):
        self.db_path = os.path.join(production_path, "cache", "security_cache.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS security_cache (
                        key TEXT PRIMARY KEY,
                        value BLOB,
                        created_at TIMESTAMP,
                        expires_at TIMESTAMP,
                        ttl INTEGER
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"Error initializing database cache: {str(e)}")
    
    def get(self, key: str) -> Any:
        """Get value from database cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT value, expires_at FROM security_cache WHERE key = ?',
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    value_blob, expires_at = row
                    
                    # Check if expired
                    if datetime.now() > datetime.fromisoformat(expires_at):
                        conn.execute('DELETE FROM security_cache WHERE key = ?', (key,))
                        conn.commit()
                        return None
                    
                    return pickle.loads(value_blob)
                    
        except Exception as e:
            logging.error(f"Error reading from database cache: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int):
        """Set value in database cache"""
        try:
            value_blob = pickle.dumps(value)
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO security_cache (key, value, created_at, expires_at, ttl)
                    VALUES (?, ?, ?, ?, ?)
                ''', (key, value_blob, datetime.now(), expires_at, ttl))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error writing to database cache: {str(e)}")
    
    def clear(self):
        """Clear database cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM security_cache')
                conn.commit()
        except Exception as e:
            logging.error(f"Error clearing database cache: {str(e)}")
    
    def cleanup(self):
        """Clean up expired entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM security_cache WHERE expires_at < ?', (datetime.now(),))
                conn.commit()
        except Exception as e:
            logging.error(f"Error in database cache cleanup: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM security_cache')
                size = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT SUM(LENGTH(value)) FROM security_cache')
                total_size = cursor.fetchone()[0] or 0
                
                return {
                    "type": "database",
                    "size": size,
                    "disk_usage": total_size
                }
        except Exception as e:
            logging.error(f"Error getting database cache stats: {str(e)}")
            return {"type": "database", "size": 0, "disk_usage": 0}
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate entries matching pattern"""
        try:
            pattern_like = pattern.replace("*", "%")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM security_cache WHERE key LIKE ?', (pattern_like,))
                conn.commit()
        except Exception as e:
            logging.error(f"Error invalidating database cache pattern: {str(e)}")
    
    def invalidate_type(self, cache_type: str):
        """Invalidate all entries of a specific type"""
        self.invalidate_pattern(f"{cache_type}:*")

class RedisCacheStore:
    """Redis-based cache store (placeholder)"""
    
    def __init__(self):
        self.enabled = False
        logging.info("Redis cache store not configured - using fallback stores")
    
    def get(self, key: str) -> Any:
        return None
    
    def set(self, key: str, value: Any, ttl: int):
        pass
    
    def clear(self):
        pass
    
    def cleanup(self):
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        return {"type": "redis", "size": 0, "memory_usage": 0}

# Cache Manager Implementations
class AuthenticationCacheManager:
    """Authentication cache manager"""
    
    def get_cache_key(self, user_id: str, token: str) -> str:
        """Generate authentication cache key"""
        return f"auth:{user_id}:{hashlib.md5(token.encode()).hexdigest()[:8]}"

class AuthorizationCacheManager:
    """Authorization cache manager"""
    
    def get_cache_key(self, user_id: str, resource: str, action: str) -> str:
        """Generate authorization cache key"""
        return f"authz:{user_id}:{hashlib.md5(f"{resource}:{action}".encode()).hexdigest()[:8]}"

class RateLimitingCacheManager:
    """Rate limiting cache manager"""
    
    def get_cache_key(self, identifier: str, window: str) -> str:
        """Generate rate limiting cache key"""
        return f"rate:{identifier}:{window}"

class CSRFProtectionCacheManager:
    """CSRF protection cache manager"""
    
    def get_cache_key(self, session_id: str, token: str) -> str:
        """Generate CSRF cache key"""
        return f"csrf:{session_id}:{hashlib.md5(token.encode()).hexdigest()[:8]}"

class InputValidationCacheManager:
    """Input validation cache manager"""
    
    def get_cache_key(self, input_hash: str, validation_type: str) -> str:
        """Generate input validation cache key"""
        return f"validation:{validation_type}:{input_hash[:16]}"

class ThreatDetectionCacheManager:
    """Threat detection cache manager"""
    
    def get_cache_key(self, ip_address: str, threat_type: str) -> str:
        """Generate threat detection cache key"""
        return f"threat:{threat_type}:{ip_address}"

class SecurityHeadersCacheManager:
    """Security headers cache manager"""
    
    def get_cache_key(self, endpoint: str, user_agent: str) -> str:
        """Generate security headers cache key"""
        return f"headers:{endpoint}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"

class ComplianceCacheManager:
    """Compliance cache manager"""
    
    def get_cache_key(self, compliance_type: str, entity_id: str) -> str:
        """Generate compliance cache key"""
        return f"compliance:{compliance_type}:{entity_id}"

def main():
    """Main function to test security validation caching"""
    cache = SecurityValidationCache()
    
    print("💾 STELLAR LOGIC AI - SECURITY VALIDATION CACHING")
    print("=" * 60)
    
    # Test authentication caching
    print("\n🔐 Testing Authentication Caching...")
    
    def mock_auth_check(user_id: str, token: str):
        """Mock authentication check"""
        time.sleep(0.1)  # Simulate slow operation
        return {"user_id": user_id, "valid": token == "valid_token"}
    
    # First call (cache miss)
    start_time = time.time()
    result1 = cache.get_cached_result("authentication", "user123", mock_auth_check, "user123", "valid_token")
    first_call_time = (time.time() - start_time) * 1000
    
    # Second call (cache hit)
    start_time = time.time()
    result2 = cache.get_cached_result("authentication", "user123", mock_auth_check, "user123", "valid_token")
    second_call_time = (time.time() - start_time) * 1000
    
    print(f"   First call (cache miss): {first_call_time:.2f}ms")
    print(f"   Second call (cache hit): {second_call_time:.2f}ms")
    print(f"   Performance improvement: {((first_call_time - second_call_time) / first_call_time * 100):.1f}%")
    print(f"   Results match: {result1 == result2}")
    
    # Test authorization caching
    print("\n🛡️ Testing Authorization Caching...")
    
    def mock_authz_check(user_id: str, resource: str, action: str):
        """Mock authorization check"""
        time.sleep(0.05)  # Simulate operation
        return {"allowed": action in ["read", "write"]}
    
    # Test multiple calls
    for i in range(3):
        result = cache.get_cached_result("authorization", "user123", mock_authz_check, "user123", "/api/data", "read")
        print(f"   Authorization check {i+1}: {result['allowed']}")
    
    # Test rate limiting caching
    print("\n⏱️ Testing Rate Limiting Caching...")
    
    def mock_rate_check(ip: str, window: str):
        """Mock rate limiting check"""
        time.sleep(0.02)  # Simulate operation
        return {"allowed": True, "remaining": 100}
    
    # Test rate limiting
    for i in range(3):
        result = cache.get_cached_result("rate_limiting", "192.168.1.1", mock_rate_check, "192.168.1.1", "1m")
        print(f"   Rate limit check {i+1}: {result['allowed']}, remaining: {result['remaining']}")
    
    # Display cache statistics
    stats = cache.get_cache_statistics()
    print(f"\n📊 Cache Statistics:")
    print(f"   Total hits: {stats['overall']['total_hits']}")
    print(f"   Total misses: {stats['overall']['total_misses']}")
    print(f"   Hit rate: {stats['overall']['hit_rate']:.2f}%")
    print(f"   Total memory usage: {stats['overall']['total_memory_usage']} bytes")
    
    print(f"\n📈 Cache Store Statistics:")
    for store_name, store_stats in stats['cache_stores'].items():
        print(f"   {store_name.capitalize()}: {store_stats['size']} entries, "
              f"{store_stats.get('memory_usage', store_stats.get('disk_usage', 0))} bytes")
    
    print(f"\n🔍 Performance Metrics:")
    perf_metrics = stats['performance_metrics']
    print(f"   Average response time: {perf_metrics['average_response_time']:.2f}ms")
    print(f"   Cache efficiency: {perf_metrics['cache_efficiency']:.2f}%")
    print(f"   Memory utilization: {perf_metrics['memory_utilization']:.2f}%")
    
    print(f"\n🎯 Security Validation Caching is operational!")

if __name__ == "__main__":
    main()
