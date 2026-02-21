#!/usr/bin/env python3
"""
Database Performance Monitoring
Real-time monitoring and analytics for database performance, query optimization, and connection pool management
"""

import os
import sys
import time
import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class DatabaseMetric:
    """Database performance metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # queries, connections, performance, health
    database_name: str
    query_type: str = None
    tags: List[str] = None

@dataclass
class QueryPerformance:
    """Query performance data structure"""
    timestamp: datetime
    query_hash: str
    query_type: str  # SELECT, INSERT, UPDATE, DELETE
    execution_time_ms: float
    rows_affected: int
    table_name: str
    index_used: str = None
    slow_query: bool = False
    error_occurred: bool = False
    error_message: str = None

@dataclass
class ConnectionPoolMetrics:
    """Connection pool metrics data structure"""
    timestamp: datetime
    total_connections: int
    active_connections: int
    idle_connections: int
    pool_size: int
    max_pool_size: int
    connection_wait_time_ms: float
    connection_timeout_count: int
    database_name: str

class DatabasePerformanceMonitor:
    """Database Performance Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("database_performance")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.query_performance = {}
        self.connection_pools = {}
        self.alert_thresholds = {
            "query_time_warning": 1000,     # 1 second
            "query_time_critical": 5000,    # 5 seconds
            "connection_pool_warning": 80,     # 80% usage
            "connection_pool_critical": 95,    # 95% usage
            "slow_query_threshold": 2000,    # 2 seconds
            "error_rate_warning": 0.05,      # 5%
            "error_rate_critical": 0.10,     # 10%
        }
        self.performance_stats = {
            "total_queries": 0,
            "slow_queries": 0,
            "failed_queries": 0,
            "avg_query_time": 0,
            "total_connections": 0,
            "active_connections": 0,
            "connection_pool_usage": 0,
            "database_size_mb": 0,
            "index_usage_ratio": 0,
            "cache_hit_ratio": 0
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds
    
    def start_monitoring(self):
        """Start database performance monitoring"""
        if self.monitoring_active:
            self.logger.warning("Database performance monitoring is already running")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Database performance monitoring started")
    
    def stop_monitoring(self):
        """Stop database performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("Database performance monitoring stopped")
    
    def record_query_performance(self, query_hash: str, query_type: str, execution_time_ms: float, 
                            rows_affected: int, table_name: str, index_used: str = None,
                            error_occurred: bool = False, error_message: str = None):
        """Record query performance data"""
        query_perf = QueryPerformance(
            timestamp=datetime.now(),
            query_hash=query_hash,
            query_type=query_type,
            execution_time_ms=execution_time_ms,
            rows_affected=rows_affected,
            table_name=table_name,
            index_used=index_used,
            slow_query=execution_time_ms > self.alert_thresholds["slow_query_threshold"],
            error_occurred=error_occurred,
            error_message=error_message
        )
        
        self.query_performance[query_hash] = query_perf
        
        # Update performance stats
        self.performance_stats["total_queries"] += 1
        if query_perf.slow_query:
            self.performance_stats["slow_queries"] += 1
        if error_occurred:
            self.performance_stats["failed_queries"] += 1
        
        self._update_avg_query_time()
        
        self.logger.info(f"Recorded query performance: {query_type} in {execution_time_ms:.2f}ms")
    
    def record_connection_pool_metrics(self, database_name: str, total_connections: int, 
                                 active_connections: int, idle_connections: int, 
                                 pool_size: int, max_pool_size: int, 
                                 connection_wait_time_ms: float, connection_timeout_count: int):
        """Record connection pool metrics"""
        pool_metrics = ConnectionPoolMetrics(
            timestamp=datetime.now(),
            total_connections=total_connections,
            active_connections=active_connections,
            idle_connections=idle_connections,
            pool_size=pool_size,
            max_pool_size=max_pool_size,
            connection_wait_time_ms=connection_wait_time_ms,
            connection_timeout_count=connection_timeout_count,
            database_name=database_name
        )
        
        self.connection_pools[database_name] = pool_metrics
        
        # Update performance stats
        self.performance_stats["total_connections"] = total_connections
        self.performance_stats["active_connections"] = active_connections
        self.performance_stats["connection_pool_usage"] = (pool_size / max_pool_size) * 100
        
        self.logger.info(f"Recorded connection pool metrics for {database_name}: {active_connections}/{total_connections} active")
    
    def record_database_metric(self, metric_name: str, value: float, unit: str, category: str, 
                           database_name: str, query_type: str = None, tags: List[str] = None):
        """Record a database performance metric"""
        metric = DatabaseMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            database_name=database_name,
            query_type=query_type,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        self.logger.info(f"Recorded database metric: {metric_name} = {value} {unit}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect database performance metrics
                self._collect_database_metrics()
                self._collect_connection_pool_metrics()
                self._collect_query_performance_metrics()
                
                # Update performance stats
                self._update_performance_stats()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in database monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_database_metrics(self):
        """Collect database performance metrics"""
        try:
            # Mock database metrics collection
            # In production, this would connect to actual databases
            metrics = {
                "database_size_mb": 1024.5,
                "index_usage_ratio": 0.75,
                "cache_hit_ratio": 0.85,
                "table_lock_wait_time": 15.2,
                "deadlock_count": 2,
                "checkpoint_write_time": 45.8,
                "log_write_time": 12.3
            }
            
            for metric_name, value in metrics.items():
                self.record_database_metric(
                    metric_name=metric_name,
                    value=value,
                    unit="MB" if "size" in metric_name else "ms" if "time" in metric_name else "count" if "count" in metric_name else "ratio",
                    category="performance",
                    database_name="stellar_logic_ai"
                )
                
        except Exception as e:
            self.logger.error(f"Error collecting database metrics: {e}")
    
    def _collect_connection_pool_metrics(self):
        """Collect connection pool metrics"""
        try:
            # Mock connection pool metrics
            pools = {
                "main_db": {
                    "total_connections": 50,
                    "active_connections": 35,
                    "idle_connections": 15,
                    "pool_size": 50,
                    "max_pool_size": 100,
                    "connection_wait_time_ms": 25.5,
                    "connection_timeout_count": 3
                },
                "analytics_db": {
                    "total_connections": 25,
                    "active_connections": 18,
                    "idle_connections": 7,
                    "pool_size": 25,
                    "max_pool_size": 50,
                    "connection_wait_time_ms": 15.2,
                    "connection_timeout_count": 1
                }
            }
            
            for db_name, pool_data in pools.items():
                self.record_connection_pool_metrics(
                    database_name=db_name,
                    **pool_data
                )
                
        except Exception as e:
            self.logger.error(f"Error collecting connection pool metrics: {e}")
    
    def _collect_query_performance_metrics(self):
        """Collect query performance metrics"""
        try:
            # Mock query performance metrics
            queries = [
                {
                    "query_hash": "SELECT_users_001",
                    "query_type": "SELECT",
                    "execution_time_ms": 125.5,
                    "rows_affected": 0,
                    "table_name": "users",
                    "index_used": "idx_users_email",
                    "slow_query": False,
                    "error_occurred": False
                },
                {
                    "query_hash": "UPDATE_sessions_002",
                    "query_type": "UPDATE",
                    "execution_time_ms": 2500.0,
                    "rows_affected": 1,
                    "table_name": "user_sessions",
                    "index_used": "idx_sessions_user_id",
                    "slow_query": True,
                    "error_occurred": False
                },
                {
                    "query_hash": "INSERT_analytics_003",
                    "query_type": "INSERT",
                    "execution_time_ms": 450.0,
                    "rows_affected": 1,
                    "table_name": "user_analytics",
                    "index_used": None,
                    "slow_query": False,
                    "error_occurred": False
                }
            ]
            
            for query_data in queries:
                # Remove slow_query from kwargs as it's calculated in the method
                query_kwargs = {k: v for k, v in query_data.items() if k != 'slow_query'}
                self.record_query_performance(**query_kwargs)
                
        except Exception as e:
            self.logger.error(f"Error collecting query performance metrics: {e}")
    
    def _update_avg_query_time(self):
        """Update average query time"""
        if self.query_performance:
            query_times = [q.execution_time_ms for q in self.query_performance.values()]
            if query_times:
                self.performance_stats["avg_query_time"] = sum(query_times) / len(query_times)
    
    def _update_performance_stats(self):
        """Update overall performance statistics"""
        # Calculate error rate
        if self.performance_stats["total_queries"] > 0:
            error_rate = self.performance_stats["failed_queries"] / self.performance_stats["total_queries"]
            self.performance_stats["error_rate"] = error_rate
        
        # Calculate slow query rate
        if self.performance_stats["total_queries"] > 0:
            slow_query_rate = self.performance_stats["slow_queries"] / self.performance_stats["total_queries"]
            self.performance_stats["slow_query_rate"] = slow_query_rate
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get database performance summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Calculate summary
        summary = {
            "period_hours": hours,
            "total_metrics": len(recent_metrics),
            "performance_stats": self.performance_stats,
            "query_performance": dict(self.query_performance),
            "connection_pools": dict(self.connection_pools),
            "alerts": self._get_recent_alerts(hours),
            "rends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent database performance alerts"""
        alerts = []
        
        # Check slow query alerts
        if self.performance_stats["slow_queries"] > 0:
            slow_query_rate = self.performance_stats.get("slow_query_rate", 0)
            if slow_query_rate > 0.05:  # 5% slow queries
                alerts.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "performance",
                    "severity": "warning",
                    "message": f"Slow query rate ({slow_query_rate:.1%}) exceeds threshold"
                })
        
        # Check connection pool alerts
        if self.performance_stats["connection_pool_usage"] > self.alert_thresholds["connection_pool_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "connections",
                "severity": "warning",
                "message": f"Connection pool usage ({self.performance_stats['connection_pool_usage']:.1f}%) exceeds threshold"
            })
        
        # Check error rate alerts
        error_rate = self.performance_stats.get("error_rate", 0)
        if error_rate > self.alert_thresholds["error_rate_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "errors",
                "severity": "critical" if error_rate > self.alert_thresholds["error_rate_critical"] else "warning",
                "message": f"Database error rate ({error_rate:.1%}) exceeds threshold"
            })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[DatabaseMetric]) -> Dict[str, Any]:
        """Calculate database performance trends"""
        if len(metrics) < 10:
            return {}
        
        # Group metrics by category
        categories = defaultdict(list)
        for metric in metrics:
            categories[metric.category].append(metric)
        
        trends = {}
        for category, category_metrics in categories.items():
            if len(category_metrics) >= 2:
                recent_values = [m.value for m in category_metrics[-10:]]
                older_values = [m.value for m in category_metrics[-20:-10]]
                
                if recent_values and older_values:
                    recent_avg = sum(recent_values) / len(recent_values)
                    older_avg = sum(older_values) / len(older_values)
                    
                    trend = "improving" if recent_avg < older_avg else "degrading" if recent_avg > older_avg else "stable"
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
                    
                    trends[category] = {
                        "trend": trend,
                        "change_percent": change_percent,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg
                    }
        
        return trends
    
    def _generate_recommendations(self) -> List[str]:
        """Generate database performance recommendations"""
        recommendations = []
        
        # Query performance recommendations
        if self.performance_stats["avg_query_time"] > self.alert_thresholds["query_time_warning"]:
            recommendations.append("Optimize slow queries and add appropriate indexes")
        
        if self.performance_stats.get("slow_query_rate", 0) > 0.05:
            recommendations.append("Review and optimize slow queries")
        
        # Connection pool recommendations
        if self.performance_stats["connection_pool_usage"] > self.alert_thresholds["connection_pool_warning"]:
            recommendations.append("Increase connection pool size or optimize connection usage")
        
        # Error rate recommendations
        error_rate = self.performance_stats.get("error_rate", 0)
        if error_rate > self.alert_thresholds["error_rate_warning"]:
            recommendations.append("Investigate and fix database errors")
        
        # Database size recommendations
        if self.performance_stats["database_size_mb"] > 5000:  # 5GB
            recommendations.append("Consider database archiving or cleanup")
        
        return recommendations

# Global database performance monitor instance
database_performance_monitor = DatabasePerformanceMonitor()
