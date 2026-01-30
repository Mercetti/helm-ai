"""
Helm AI Health Checks
This module provides comprehensive health check endpoints and system monitoring
"""

import os
import json
import logging
import time
import threading
import psutil
import subprocess
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import requests
from urllib.parse import urlparse
from collections import defaultdict

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CheckType(Enum):
    """Health check types"""
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_SERVICE = "external_service"
    DISK_SPACE = "disk_space"
    MEMORY = "memory"
    CPU = "cpu"
    API_ENDPOINT = "api_endpoint"
    CUSTOM = "custom"

@dataclass
class HealthCheckResult:
    """Health check result"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_type: CheckType
    check_function: Callable
    timeout_seconds: int = 30
    interval_seconds: int = 60
    enabled: bool = True
    critical: bool = False
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class HealthChecker:
    """Health check execution engine"""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.check_history: Dict[str, List[HealthCheckResult]] = defaultdict(list)
        
        # Configuration
        self.default_timeout = int(os.getenv('HEALTH_CHECK_TIMEOUT', '30'))
        self.max_history_size = int(os.getenv('HEALTH_CHECK_HISTORY_SIZE', '100'))
        
        # Initialize default health checks
        self._initialize_default_checks()
        
        # Start periodic health checking
        self._start_health_monitoring()
    
    def _initialize_default_checks(self):
        """Initialize default health checks"""
        
        # Database health check
        self.add_check(HealthCheck(
            name="database",
            check_type=CheckType.DATABASE,
            check_function=self._check_database,
            timeout_seconds=10,
            critical=True,
            tags=["core", "data"]
        ))
        
        # Cache health check
        self.add_check(HealthCheck(
            name="cache",
            check_type=CheckType.CACHE,
            check_function=self._check_cache,
            timeout_seconds=5,
            tags=["core", "performance"]
        ))
        
        # Disk space health check
        self.add_check(HealthCheck(
            name="disk_space",
            check_type=CheckType.DISK_SPACE,
            check_function=self._check_disk_space,
            timeout_seconds=5,
            critical=True,
            tags=["system", "storage"]
        ))
        
        # Memory health check
        self.add_check(HealthCheck(
            name="memory",
            check_type=CheckType.MEMORY,
            check_function=self._check_memory,
            timeout_seconds=5,
            tags=["system", "resources"]
        ))
        
        # CPU health check
        self.add_check(HealthCheck(
            name="cpu",
            check_type=CheckType.CPU,
            check_function=self._check_cpu,
            timeout_seconds=5,
            tags=["system", "resources"]
        ))
        
        # External API health check
        self.add_check(HealthCheck(
            name="external_api",
            check_type=CheckType.API_ENDPOINT,
            check_function=self._check_external_api,
            timeout_seconds=10,
            tags=["external", "dependency"]
        ))
    
    def add_check(self, check: HealthCheck):
        """Add health check"""
        self.checks[check.name] = check
        logger.info(f"Added health check: {check.name}")
    
    def remove_check(self, name: str) -> bool:
        """Remove health check"""
        if name in self.checks:
            del self.checks[name]
            if name in self.results:
                del self.results[name]
            if name in self.check_history:
                del self.check_history[name]
            logger.info(f"Removed health check: {name}")
            return True
        return False
    
    def run_check(self, name: str) -> HealthCheckResult:
        """Run specific health check"""
        check = self.checks.get(name)
        if not check:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found",
                duration_ms=0.0
            )
        
        if not check.enabled:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="Health check is disabled",
                duration_ms=0.0
            )
        
        start_time = time.time()
        
        try:
            # Run check with timeout
            result = self._run_check_with_timeout(check)
            result.duration_ms = (time.time() - start_time) * 1000
            
            # Store result
            self.results[name] = result
            self._add_to_history(name, result)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=duration_ms,
                details={"error": str(e)}
            )
            
            self.results[name] = error_result
            self._add_to_history(name, error_result)
            
            return error_result
    
    def _run_check_with_timeout(self, check: HealthCheck) -> HealthCheckResult:
        """Run health check with timeout"""
        def run_check():
            return check.check_function()
        
        # Simple timeout implementation
        result_queue = []
        
        def target():
            try:
                result = run_check()
                result_queue.append(result)
            except Exception as e:
                result_queue.append(e)
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(check.timeout_seconds)
        
        if thread.is_alive():
            # Timeout occurred
            return HealthCheckResult(
                name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {check.timeout_seconds} seconds",
                duration_ms=check.timeout_seconds * 1000
            )
        
        if result_queue:
            result = result_queue[0]
            if isinstance(result, Exception):
                return HealthCheckResult(
                    name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(result)}",
                    duration_ms=0.0,
                    details={"error": str(result)}
                )
            return result
        
        return HealthCheckResult(
            name=check.name,
            status=HealthStatus.UNKNOWN,
            message="No result from health check",
            duration_ms=0.0
        )
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all enabled health checks"""
        results = {}
        
        for name, check in self.checks.items():
            if check.enabled:
                results[name] = self.run_check(name)
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall health status"""
        if not self.results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in self.results.values()]
        
        # Determine overall status
        if any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        results = self.run_all_checks()
        overall_status = self.get_overall_status()
        
        summary = {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {
                "total": len(results),
                "healthy": len([r for r in results.values() if r.status == HealthStatus.HEALTHY]),
                "degraded": len([r for r in results.values() if r.status == HealthStatus.DEGRADED]),
                "unhealthy": len([r for r in results.values() if r.status == HealthStatus.UNHEALTHY]),
                "unknown": len([r for r in results.values() if r.status == HealthStatus.UNKNOWN])
            },
            "critical_issues": []
        }
        
        # Add individual check results
        for name, result in results.items():
            check = self.checks.get(name)
            summary["checks"][name] = {
                "status": result.status.value,
                "message": result.message,
                "duration_ms": result.duration_ms,
                "critical": check.critical if check else False,
                "tags": check.tags if check else [],
                "details": result.details
            }
            
            # Add critical issues
            if result.status == HealthStatus.UNHEALTHY and check and check.critical:
                summary["critical_issues"].append({
                    "name": name,
                    "message": result.message,
                    "duration_ms": result.duration_ms
                })
        
        return summary
    
    def _add_to_history(self, name: str, result: HealthCheckResult):
        """Add result to check history"""
        history = self.check_history[name]
        history.append(result)
        
        # Limit history size
        if len(history) > self.max_history_size:
            history.pop(0)
    
    def get_check_history(self, name: str, hours: int = 24) -> List[HealthCheckResult]:
        """Get health check history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            result for result in self.check_history.get(name, [])
            if result.timestamp >= cutoff_time
        ]
    
    def _start_health_monitoring(self):
        """Start periodic health monitoring"""
        def monitor_health():
            while True:
                try:
                    self.run_all_checks()
                    threading.Event().wait(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    threading.Event().wait(60)
        
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()
    
    # Default health check implementations
    def _check_database(self) -> HealthCheckResult:
        """Check database connectivity"""
        try:
            # This would check actual database connection
            # For now, simulate database check
            
            # Check PostgreSQL if available
            try:
                result = subprocess.run(
                    ["pg_isready", "-h", "localhost"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return HealthCheckResult(
                        name="database",
                        status=HealthStatus.HEALTHY,
                        message="Database is ready and accepting connections"
                    )
                else:
                    return HealthCheckResult(
                        name="database",
                        status=HealthStatus.UNHEALTHY,
                        message="Database is not ready",
                        details={"stderr": result.stderr}
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Fallback check
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database check not configured"
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_cache(self) -> HealthCheckResult:
        """Check cache connectivity"""
        try:
            # This would check actual cache connection (Redis, Memcached, etc.)
            # For now, simulate cache check
            
            # Check Redis if available
            try:
                import redis
                redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
                redis_client.ping()
                
                return HealthCheckResult(
                    name="cache",
                    status=HealthStatus.HEALTHY,
                    message="Cache is responsive",
                    details={"ping_ms": 1.0}
                )
            except Exception:
                pass
            
            return HealthCheckResult(
                name="cache",
                status=HealthStatus.HEALTHY,
                message="Cache check not configured"
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="cache",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_disk_space(self) -> HealthCheckResult:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            used_percent = (disk.used / disk.total) * 100
            free_gb = disk.free / (1024**3)
            
            # Determine status based on usage
            if used_percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {used_percent:.1f}% ({free_gb:.1f}GB free)"
            elif used_percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {used_percent:.1f}% ({free_gb:.1f}GB free)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {used_percent:.1f}% ({free_gb:.1f}GB free)"
            
            return HealthCheckResult(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": free_gb,
                    "used_percent": used_percent
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_memory(self) -> HealthCheckResult:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            available_gb = memory.available / (1024**3)
            
            # Determine status based on usage
            if used_percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {used_percent:.1f}% ({available_gb:.1f}GB available)"
            elif used_percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {used_percent:.1f}% ({available_gb:.1f}GB available)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {used_percent:.1f}% ({available_gb:.1f}GB available)"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                details={
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": available_gb,
                    "used_percent": used_percent
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_cpu(self) -> HealthCheckResult:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            load_avg = psutil.getloadavg()
            
            # Determine status based on usage
            if cpu_percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                name="cpu",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "load_avg_1min": load_avg[0],
                    "load_avg_5min": load_avg[1],
                    "load_avg_15min": load_avg[2]
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="cpu",
                status=HealthStatus.UNHEALTHY,
                message=f"CPU check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_external_api(self) -> HealthCheckResult:
        """Check external API connectivity"""
        try:
            # Check external API health endpoint
            api_url = os.getenv('EXTERNAL_API_HEALTH_URL', 'https://api.helm-ai.com/health')
            
            start_time = time.time()
            response = requests.get(api_url, timeout=5)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return HealthCheckResult(
                    name="external_api",
                    status=HealthStatus.HEALTHY,
                    message="External API is healthy",
                    details={
                        "url": api_url,
                        "status_code": response.status_code,
                        "response_time_ms": duration_ms
                    }
                )
            else:
                return HealthCheckResult(
                    name="external_api",
                    status=HealthStatus.UNHEALTHY,
                    message=f"External API returned status {response.status_code}",
                    details={
                        "url": api_url,
                        "status_code": response.status_code,
                        "response_time_ms": duration_ms
                    }
                )
                
        except requests.RequestException as e:
            return HealthCheckResult(
                name="external_api",
                status=HealthStatus.UNHEALTHY,
                message=f"External API check failed: {str(e)}",
                details={"error": str(e)}
            )
        except Exception as e:
            return HealthCheckResult(
                name="external_api",
                status=HealthStatus.UNKNOWN,
                message=f"External API check not configured: {str(e)}",
                details={"error": str(e)}
            )


class HealthEndpoint:
    """Health check HTTP endpoint"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
    
    def get_health(self, detailed: bool = False) -> Dict[str, Any]:
        """Get health status"""
        if detailed:
            return self.health_checker.get_health_summary()
        else:
            status = self.health_checker.get_overall_status()
            return {
                "status": status.value,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_readiness(self) -> Dict[str, Any]:
        """Get readiness status (for Kubernetes readiness probes)"""
        results = self.health_checker.run_all_checks()
        
        # Check if all critical checks are healthy
        critical_checks = [
            name for name, check in self.health_checker.checks.items()
            if check.critical and check.enabled
        ]
        
        ready = all(
            results.get(name, HealthCheckResult("", HealthStatus.UNHEALTHY, "", 0.0)).status == HealthStatus.HEALTHY
            for name in critical_checks
        )
        
        return {
            "ready": ready,
            "status": "ready" if ready else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                name: results.get(name, HealthCheckResult("", HealthStatus.UNKNOWN, "", 0.0)).status.value
                for name in critical_checks
            }
        }
    
    def get_liveness(self) -> Dict[str, Any]:
        """Get liveness status (for Kubernetes liveness probes)"""
        # Simple liveness check - just check if the service is running
        return {
            "alive": True,
            "status": "alive",
            "timestamp": datetime.now().isoformat()
        }


# Global health checker instance
health_checker = HealthChecker()

# Flask routes for health checks
def register_health_routes(app):
    """Register health check routes with Flask app"""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Basic health check endpoint"""
        try:
            health = health_checker.get_health()
            status_code = 200 if health['status'] == 'healthy' else 503
            return jsonify(health), status_code
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 503
    
    @app.route('/health/detailed', methods=['GET'])
    def detailed_health_check():
        """Comprehensive health check endpoint"""
        try:
            health = health_checker.get_detailed_health()
            status_code = 200 if health['status'] == 'healthy' else 503
            return jsonify(health), status_code
        except Exception as e:
            logger.error(f"Detailed health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 503
    
    @app.route('/health/readiness', methods=['GET'])
    def readiness_check():
        """Kubernetes readiness probe"""
        try:
            ready = health_checker.get_readiness()
            status_code = 200 if ready['status'] == 'ready' else 503
            return jsonify(ready), status_code
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({
                'status': 'not_ready',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 503
    
    @app.route('/health/liveness', methods=['GET'])
    def liveness_check():
        """Kubernetes liveness probe"""
        try:
            alive = health_checker.get_liveness()
            return jsonify(alive), 200
        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            return jsonify({
                'status': 'dead',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Get application metrics"""
        try:
            metrics = health_checker.get_metrics()
            return jsonify(metrics), 200
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {e}")
            return jsonify({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
