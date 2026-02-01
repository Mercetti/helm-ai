# Helm AI - Performance Monitoring & Metrics
"""
Comprehensive performance monitoring with Prometheus metrics,
custom performance tracking, and real-time analytics.
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timezone, timedelta
from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    CollectorRegistry, generate_latest
)
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from src.logging_config.logger import get_performance_logger, log_performance
from src.common.exceptions import SystemException

perf_logger = get_performance_logger()

class MetricsCollector:
    """Custom Prometheus metrics collector for Helm AI"""

    def __init__(self):
        self.system_metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used_mb": 0.0,
            "disk_usage_percent": 0.0,
            "network_connections": 0
        }
        self._last_collection = datetime.now(timezone.utc)

    def collect(self):
        """Collect system metrics for Prometheus"""
        try:
            # CPU metrics
            yield GaugeMetricFamily(
                'helm_ai_cpu_percent',
                'CPU usage percentage',
                value=psutil.cpu_percent(interval=1)
            )

            # Memory metrics
            memory = psutil.virtual_memory()
            yield GaugeMetricFamily(
                'helm_ai_memory_percent',
                'Memory usage percentage',
                value=memory.percent
            )
            yield GaugeMetricFamily(
                'helm_ai_memory_used_bytes',
                'Memory used in bytes',
                value=memory.used
            )

            # Disk metrics
            disk = psutil.disk_usage('/')
            yield GaugeMetricFamily(
                'helm_ai_disk_usage_percent',
                'Disk usage percentage',
                value=disk.percent
            )

            # Network connections
            net_connections = len(psutil.net_connections())
            yield GaugeMetricFamily(
                'helm_ai_network_connections',
                'Number of network connections',
                value=net_connections
            )

            # Process metrics
            process = psutil.Process()
            yield GaugeMetricFamily(
                'helm_ai_process_cpu_percent',
                'Process CPU usage percentage',
                value=process.cpu_percent()
            )
            yield GaugeMetricFamily(
                'helm_ai_process_memory_mb',
                'Process memory usage in MB',
                value=process.memory_info().rss / 1024 / 1024
            )
            yield GaugeMetricFamily(
                'helm_ai_process_threads',
                'Number of process threads',
                value=process.num_threads()
            )

        except Exception as e:
            perf_logger.error(f"Error collecting system metrics: {e}")

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()

        # Request metrics
        self.request_count = Counter(
            'helm_ai_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'helm_ai_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            registry=self.registry
        )

        self.request_size = Summary(
            'helm_ai_http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint'],
            registry=self.registry
        )

        self.response_size = Summary(
            'helm_ai_http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        # Database metrics
        self.db_query_count = Counter(
            'helm_ai_db_queries_total',
            'Total database queries',
            ['operation', 'table'],
            registry=self.registry
        )

        self.db_query_duration = Histogram(
            'helm_ai_db_query_duration_seconds',
            'Database query duration',
            ['operation', 'table'],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
            registry=self.registry
        )

        self.db_connection_pool_size = Gauge(
            'helm_ai_db_connection_pool_size',
            'Database connection pool size',
            registry=self.registry
        )

        self.db_connection_pool_active = Gauge(
            'helm_ai_db_connection_pool_active',
            'Active database connections',
            registry=self.registry
        )

        # Cache metrics
        self.cache_hits = Counter(
            'helm_ai_cache_hits_total',
            'Cache hits',
            ['cache_name'],
            registry=self.registry
        )

        self.cache_misses = Counter(
            'helm_ai_cache_misses_total',
            'Cache misses',
            ['cache_name'],
            registry=self.registry
        )

        self.cache_hit_ratio = Gauge(
            'helm_ai_cache_hit_ratio',
            'Cache hit ratio (0.0-1.0)',
            ['cache_name'],
            registry=self.registry
        )

        # AI/ML metrics
        self.ai_inference_count = Counter(
            'helm_ai_inference_requests_total',
            'Total AI inference requests',
            ['model', 'task'],
            registry=self.registry
        )

        self.ai_inference_duration = Histogram(
            'helm_ai_inference_duration_seconds',
            'AI inference duration',
            ['model', 'task'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
            registry=self.registry
        )

        self.ai_model_accuracy = Gauge(
            'helm_ai_model_accuracy',
            'AI model accuracy (0.0-1.0)',
            ['model'],
            registry=self.registry
        )

        # Business metrics
        self.business_metric = Gauge(
            'helm_ai_business_metric',
            'Business performance metrics',
            ['metric_name'],
            registry=self.registry
        )

        # Error metrics
        self.error_count = Counter(
            'helm_ai_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'helm_ai_rate_limit_hits_total',
            'Rate limit hits',
            ['limit_type'],
            registry=self.registry
        )

        # Custom metrics storage
        self.custom_metrics: Dict[str, Any] = {}

        # System metrics collector
        self.system_collector = MetricsCollector()
        self.registry.register(self.system_collector)

        # Performance tracking
        self.operation_times: Dict[str, List[float]] = {}
        self._monitoring_thread = None
        self._stop_monitoring = False

    def start_monitoring(self, interval: int = 60):
        """Start background performance monitoring"""
        if self._monitoring_thread is None:
            self._monitoring_thread = threading.Thread(
                target=self._monitor_performance,
                args=(interval,),
                daemon=True
            )
            self._monitoring_thread.start()

    def stop_monitoring(self):
        """Stop background performance monitoring"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)

    def _monitor_performance(self, interval: int):
        """Background performance monitoring"""
        while not self._stop_monitoring:
            try:
                self._collect_performance_metrics()
                time.sleep(interval)
            except Exception as e:
                perf_logger.error(f"Performance monitoring error: {e}")
                time.sleep(interval)

    def _collect_performance_metrics(self):
        """Collect and log performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024

            # Log performance snapshot
            log_performance(
                operation="system_performance_snapshot",
                duration_ms=0,  # Not applicable
                component="system",
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb
            )

            # Update business metrics if available
            self._update_business_metrics()

        except Exception as e:
            perf_logger.error(f"Error collecting performance metrics: {e}")

    def _update_business_metrics(self):
        """Update business-related metrics"""
        # This would be extended with actual business logic
        pass

    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Track HTTP request metrics"""
        self.request_count.labels(method, endpoint, str(status_code)).inc()
        self.request_duration.labels(method, endpoint).observe(duration)

        if request_size > 0:
            self.request_size.labels(method, endpoint).observe(request_size)

        if response_size > 0:
            self.response_size.labels(method, endpoint, str(status_code)).observe(response_size)

    def track_database_query(
        self,
        operation: str,
        table: str,
        duration: float
    ):
        """Track database query metrics"""
        self.db_query_count.labels(operation, table).inc()
        self.db_query_duration.labels(operation, table).observe(duration)

    def track_cache_operation(
        self,
        cache_name: str,
        hit: bool
    ):
        """Track cache operation metrics"""
        if hit:
            self.cache_hits.labels(cache_name).inc()
        else:
            self.cache_misses.labels(cache_name).inc()

        # Update hit ratio
        total_requests = self.cache_hits.labels(cache_name)._value.get() + \
                        self.cache_misses.labels(cache_name)._value.get()
        if total_requests > 0:
            hit_ratio = self.cache_hits.labels(cache_name)._value.get() / total_requests
            self.cache_hit_ratio.labels(cache_name).set(hit_ratio)

    def track_ai_inference(
        self,
        model: str,
        task: str,
        duration: float
    ):
        """Track AI inference metrics"""
        self.ai_inference_count.labels(model, task).inc()
        self.ai_inference_duration.labels(model, task).observe(duration)

    def track_error(
        self,
        error_type: str,
        component: str
    ):
        """Track error metrics"""
        self.error_count.labels(error_type, component).inc()

    def track_rate_limit_hit(self, limit_type: str = "default"):
        """Track rate limit hits"""
        self.rate_limit_hits.labels(limit_type).inc()

    def set_business_metric(self, metric_name: str, value: float):
        """Set business metric value"""
        self.business_metric.labels(metric_name).set(value)

    def set_ai_model_accuracy(self, model: str, accuracy: float):
        """Set AI model accuracy"""
        self.ai_model_accuracy.labels(model).set(accuracy)

    def update_connection_pool_metrics(self, pool_size: int, active_connections: int):
        """Update database connection pool metrics"""
        self.db_connection_pool_size.set(pool_size)
        self.db_connection_pool_active.set(active_connections)

    def time_operation(self, operation_name: str) -> Callable:
        """Decorator to time operation execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    # Log performance
                    log_performance(
                        operation=f"{operation_name}.{func.__name__}",
                        duration_ms=duration * 1000,
                        component=operation_name
                    )

                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    log_performance(
                        operation=f"{operation_name}.{func.__name__}_error",
                        duration_ms=duration * 1000,
                        component=operation_name,
                        error=str(e)
                    )
                    raise
            return wrapper
        return decorator

    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format"""
        return generate_latest(self.registry).decode('utf-8')

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "process_cpu_percent": psutil.Process().cpu_percent(),
                "process_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "process_threads": psutil.Process().num_threads()
            }
        except Exception as e:
            perf_logger.error(f"Error getting system metrics: {e}")
            return {}

    def get_metrics_json(self) -> Dict[str, Any]:
        """Get metrics as JSON"""
        # This is a simplified version - in production you'd parse the Prometheus output
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": self.system_collector.system_metrics,
            "custom_metrics": self.custom_metrics
        }

# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def init_performance_monitor(registry: Optional[CollectorRegistry] = None) -> PerformanceMonitor:
    """Initialize global performance monitor"""
    global _performance_monitor
    _performance_monitor = PerformanceMonitor(registry)
    return _performance_monitor

# Convenience functions for easy access
def track_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track HTTP request"""
    get_performance_monitor().track_request(method, endpoint, status_code, duration)

def track_database_query(operation: str, table: str, duration: float):
    """Track database query"""
    get_performance_monitor().track_database_query(operation, table, duration)

def track_cache_operation(cache_name: str, hit: bool):
    """Track cache operation"""
    get_performance_monitor().track_cache_operation(cache_name, hit)

def track_ai_inference(model: str, task: str, duration: float):
    """Track AI inference"""
    get_performance_monitor().track_ai_inference(model, task, duration)

def track_error(error_type: str, component: str):
    """Track error"""
    get_performance_monitor().track_error(error_type, component)

# Initialize on import
try:
    _performance_monitor = PerformanceMonitor()
except Exception as e:
    perf_logger.error(f"Failed to initialize performance monitor: {e}")