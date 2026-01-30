"""
Helm AI Performance Monitor
This module provides comprehensive performance monitoring and metrics collection
"""

import os
import json
import logging
import time
import threading
import psutil
import gc
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import redis
from functools import wraps

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from structured_logging import logger
from database.database_manager import get_database_manager

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class MetricUnit(Enum):
    """Metric units"""
    COUNT = "count"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    PERCENTAGE = "percentage"
    REQUESTS_PER_SECOND = "requests_per_second"

@dataclass
class MetricValue:
    """Metric value with timestamp"""
    timestamp: datetime
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class PerformanceMetric:
    """Performance metric definition"""
    name: str
    metric_type: MetricType
    unit: MetricUnit
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Metrics collection and aggregation"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Configuration
        self.use_redis = os.getenv('REDIS_URL') is not None
        self.retention_hours = int(os.getenv('METRICS_RETENTION_HOURS', '24'))
        
        # Initialize Redis if configured
        if self.use_redis:
            self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def register_metric(self, 
                       name: str,
                       metric_type: MetricType,
                       unit: MetricUnit,
                       description: str,
                       labels: Dict[str, str] = None) -> PerformanceMetric:
        """Register a new metric"""
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            unit=unit,
            description=description,
            labels=labels or {}
        )
        
        self.metrics[name] = metric
        logger.info(f"Registered metric: {name}")
        return metric
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment counter metric"""
        self.counters[name] += value
        
        if self.use_redis:
            key = f"counter:{name}"
            self.redis_client.incrbyfloat(key, value)
            self.redis_client.expire(key, self.retention_hours * 3600)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge metric"""
        self.gauges[name] = value
        
        if self.use_redis:
            key = f"gauge:{name}"
            self.redis_client.set(key, value)
            self.redis_client.expire(key, self.retention_hours * 3600)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record histogram metric"""
        self.histograms[name].append(value)
        
        if self.use_redis:
            key = f"histogram:{name}"
            self.redis_client.lpush(key, json.dumps({
                'value': value,
                'timestamp': datetime.now().isoformat()
            }))
            self.redis_client.ltrim(key, 0, 999)  # Keep last 1000 values
            self.redis_client.expire(key, self.retention_hours * 3600)
    
    def record_timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        """Record timer metric"""
        self.timers[name].append(duration_ms)
        
        if self.use_redis:
            key = f"timer:{name}"
            self.redis_client.lpush(key, json.dumps({
                'duration_ms': duration_ms,
                'timestamp': datetime.now().isoformat()
            }))
            self.redis_client.ltrim(key, 0, 999)
            self.redis_client.expire(key, self.retention_hours * 3600)
    
    def get_metric_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a metric"""
        metric = self.metrics.get(name)
        if not metric:
            return {}
        
        stats = {
            'name': name,
            'type': metric.metric_type.value,
            'unit': metric.unit.value,
            'description': metric.description,
            'labels': metric.labels
        }
        
        if metric.metric_type == MetricType.COUNTER:
            stats['value'] = self.counters.get(name, 0.0)
        
        elif metric.metric_type == MetricType.GAUGE:
            stats['value'] = self.gauges.get(name, 0.0)
        
        elif metric.metric_type == MetricType.HISTOGRAM:
            values = list(self.histograms.get(name, []))
            if values:
                stats.update({
                    'count': len(values),
                    'sum': sum(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'p95': self._percentile(values, 0.95),
                    'p99': self._percentile(values, 0.99)
                })
        
        elif metric.metric_type == MetricType.TIMER:
            durations = list(self.timers.get(name, []))
            if durations:
                stats.update({
                    'count': len(durations),
                    'sum_ms': sum(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'mean_ms': statistics.mean(durations),
                    'median_ms': statistics.median(durations),
                    'p95_ms': self._percentile(durations, 0.95),
                    'p99_ms': self._percentile(durations, 0.99)
                })
        
        return stats
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _start_cleanup_thread(self):
        """Start cleanup thread for old metrics"""
        def cleanup_old_metrics():
            while True:
                try:
                    # Clean up old histogram and timer values
                    cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
                    
                    # This is a simplified cleanup - in production you'd want more sophisticated cleanup
                    for name in list(self.histograms.keys()):
                        if len(self.histograms[name]) == 0:
                            del self.histograms[name]
                    
                    for name in list(self.timers.keys()):
                        if len(self.timers[name]) == 0:
                            del self.timers[name]
                    
                    # Sleep for 1 hour
                    threading.Event().wait(3600)
                    
                except Exception as e:
                    logger.error(f"Metrics cleanup error: {e}")
                    threading.Event().wait(300)  # Wait 5 minutes on error
        
        cleanup_thread = threading.Thread(target=cleanup_old_metrics, daemon=True)
        cleanup_thread.start()


class PerformanceMonitor:
    """Performance monitoring and profiling"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profilers: Dict[str, threading.Thread] = {}
        
        # System monitoring
        self.system_stats_enabled = os.getenv('ENABLE_SYSTEM_STATS', 'true').lower() == 'true'
        self.system_stats_interval = int(os.getenv('SYSTEM_STATS_INTERVAL', '60'))  # seconds
        
        # Initialize default metrics
        self._initialize_metrics()
        
        # Start system monitoring
        if self.system_stats_enabled:
            self._start_system_monitoring()
    
    def _initialize_metrics(self):
        """Initialize default performance metrics"""
        # API metrics
        self.metrics_collector.register_metric(
            "api_requests_total",
            MetricType.COUNTER,
            MetricUnit.COUNT,
            "Total API requests"
        )
        
        self.metrics_collector.register_metric(
            "api_request_duration_ms",
            MetricType.TIMER,
            MetricUnit.MILLISECONDS,
            "API request duration in milliseconds"
        )
        
        self.metrics_collector.register_metric(
            "api_errors_total",
            MetricType.COUNTER,
            MetricUnit.COUNT,
            "Total API errors"
        )
        
        # Database metrics
        self.metrics_collector.register_metric(
            "db_connections_active",
            MetricType.GAUGE,
            MetricUnit.COUNT,
            "Active database connections"
        )
        
        self.metrics_collector.register_metric(
            "db_query_duration_ms",
            MetricType.TIMER,
            MetricUnit.MILLISECONDS,
            "Database query duration in milliseconds"
        )
        
        # Cache metrics
        self.metrics_collector.register_metric(
            "cache_hits_total",
            MetricType.COUNTER,
            MetricUnit.COUNT,
            "Total cache hits"
        )
        
        self.metrics_collector.register_metric(
            "cache_misses_total",
            MetricType.COUNTER,
            MetricUnit.COUNT,
            "Total cache misses"
        )
        
        # System metrics
        self.metrics_collector.register_metric(
            "cpu_usage_percent",
            MetricType.GAUGE,
            MetricUnit.PERCENTAGE,
            "CPU usage percentage"
        )
        
        self.metrics_collector.register_metric(
            "memory_usage_bytes",
            MetricType.GAUGE,
            MetricUnit.BYTES,
            "Memory usage in bytes"
        )
        
        self.metrics_collector.register_metric(
            "disk_usage_percent",
            MetricType.GAUGE,
            MetricUnit.PERCENTAGE,
            "Disk usage percentage"
        )
    
    def _start_system_monitoring(self):
        """Start system resource monitoring"""
        def monitor_system():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.metrics_collector.set_gauge("cpu_usage_percent", cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.metrics_collector.set_gauge("memory_usage_bytes", memory.used)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.metrics_collector.set_gauge("disk_usage_percent", disk_percent)
                    
                    # Process-specific metrics
                    process = psutil.Process()
                    self.metrics_collector.set_gauge("process_cpu_percent", process.cpu_percent())
                    self.metrics_collector.set_gauge("process_memory_bytes", process.memory_info().rss)
                    
                    # GC metrics
                    gc_stats = gc.get_stats()
                    total_collected = sum(stat['collected'] for stat in gc_stats)
                    self.metrics_collector.set_gauge("gc_objects_collected", total_collected)
                    
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                
                threading.Event().wait(self.system_stats_interval)
        
        system_thread = threading.Thread(target=monitor_system, daemon=True)
        system_thread.start()
    
    def track_api_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Track API request metrics"""
        # Increment request counter
        self.metrics_collector.increment_counter("api_requests_total")
        
        # Record duration
        self.metrics_collector.record_timer("api_request_duration_ms", duration_ms)
        
        # Track errors
        if status_code >= 400:
            self.metrics_collector.increment_counter("api_errors_total")
    
    def track_database_query(self, query_type: str, table: str, duration_ms: float, rows_affected: int = None):
        """Track database query metrics"""
        # Record query duration
        metric_name = f"db_{query_type.lower()}_duration_ms"
        self.metrics_collector.record_timer(metric_name, duration_ms)
        
        # Track rows affected if provided
        if rows_affected is not None:
            self.metrics_collector.record_histogram(f"db_{query_type.lower()}_rows", rows_affected)
    
    def track_cache_operation(self, operation: str, hit: bool, key: str = None):
        """Track cache operation metrics"""
        if hit:
            self.metrics_collector.increment_counter("cache_hits_total")
        else:
            self.metrics_collector.increment_counter("cache_misses_total")
    
    def start_profiling(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """Start performance profiling"""
        profile_id = f"{name}_{int(time.time() * 1000)}"
        
        self.profiles[profile_id] = {
            'name': name,
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'metadata': metadata or {},
            'samples': []
        }
        
        return profile_id
    
    def end_profiling(self, profile_id: str) -> Dict[str, Any]:
        """End performance profiling and return results"""
        if profile_id not in self.profiles:
            return {}
        
        profile = self.profiles[profile_id]
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        profile.update({
            'end_time': end_time,
            'end_memory': end_memory,
            'duration_ms': (end_time - profile['start_time']) * 1000,
            'memory_delta_bytes': end_memory - profile['start_memory']
        })
        
        # Calculate statistics from samples
        if profile['samples']:
            durations = [sample['duration_ms'] for sample in profile['samples']]
            profile['stats'] = {
                'sample_count': len(durations),
                'avg_duration_ms': sum(durations) / len(durations),
                'min_duration_ms': min(durations),
                'max_duration_ms': max(durations)
            }
        
        return profile
    
    def add_profile_sample(self, profile_id: str, operation: str, duration_ms: float):
        """Add sample to profile"""
        if profile_id in self.profiles:
            self.profiles[profile_id]['samples'].append({
                'operation': operation,
                'duration_ms': duration_ms,
                'timestamp': time.time()
            })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'system_stats': {},
            'recent_profiles': []
        }
        
        # Get metric statistics
        for metric_name in self.metrics_collector.metrics.keys():
            summary['metrics'][metric_name] = self.metrics_collector.get_metric_stats(metric_name)
        
        # System statistics
        if self.system_stats_enabled:
            try:
                summary['system_stats'] = {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_total': psutil.disk_usage('/').total,
                    'disk_free': psutil.disk_usage('/').free,
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                }
            except Exception as e:
                logger.error(f"Failed to get system stats: {e}")
        
        # Recent profiles
        recent_profiles = sorted(
            [(pid, profile) for pid, profile in self.profiles.items()],
            key=lambda x: x[1].get('end_time', 0),
            reverse=True
        )[:10]
        
        summary['recent_profiles'] = [
            {
                'profile_id': pid,
                'name': profile['name'],
                'duration_ms': profile.get('duration_ms'),
                'memory_delta_bytes': profile.get('memory_delta_bytes'),
                'metadata': profile.get('metadata')
            }
            for pid, profile in recent_profiles
        ]
        
        return summary
    
    def cleanup_profiles(self, hours: int = 24):
        """Clean up old profiles"""
        cutoff_time = time.time() - (hours * 3600)
        
        profiles_to_remove = []
        for profile_id, profile in self.profiles.items():
            if profile.get('end_time', 0) < cutoff_time:
                profiles_to_remove.append(profile_id)
        
        for profile_id in profiles_to_remove:
            del self.profiles[profile_id]
        
        logger.info(f"Cleaned up {len(profiles_to_remove)} old profiles")


# Decorators for performance monitoring
def monitor_performance(metric_name: str = None, track_args: bool = False):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            
            except Exception as e:
                success = False
                raise
            
            finally:
                duration_ms = (time.time() - start_time) * 1000
                name = metric_name or f"{func.__module__}.{func.__name__}"
                
                # Record performance metric
                performance_monitor.metrics_collector.record_timer(f"{name}_duration_ms", duration_ms)
                
                # Track success/failure
                if success:
                    performance_monitor.metrics_collector.increment_counter(f"{name}_success_total")
                else:
                    performance_monitor.metrics_collector.increment_counter(f"{name}_error_total")
                
                # Log performance if slow
                if duration_ms > 1000:  # > 1 second
                    logger.warning(f"Slow function: {name} took {duration_ms:.2f}ms")
        
        return wrapper
    return decorator


def profile_function(name: str = None):
    """Decorator to profile function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profile_name = name or f"{func.__module__}.{func.__name__}"
            profile_id = performance_monitor.start_profiling(profile_name)
            
            try:
                return func(*args, **kwargs)
            finally:
                performance_monitor.end_profiling(profile_id)
        
        return wrapper
    return decorator


class PerformanceProfiler:
    """Context manager for performance profiling"""
    
    def __init__(self, name: str, metadata: Dict[str, Any] = None):
        self.name = name
        self.metadata = metadata or {}
        self.profile_id = None
    
    def __enter__(self):
        self.profile_id = performance_monitor.start_profiling(self.name, self.metadata)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        profile = performance_monitor.end_profiling(self.profile_id)
        
        # Log profile results
        logger.info(f"Profile completed: {self.name} - {profile.get('duration_ms', 0):.2f}ms")
        
        if exc_type:
            logger.error(f"Exception in profile {self.name}: {exc_type.__name__}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
