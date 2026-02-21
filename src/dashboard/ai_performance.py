#!/usr/bin/env python3
"""
AI Performance Dashboard
Real-time monitoring and analytics for LLM performance metrics
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # response_time, accuracy, throughput, resource_usage
    tags: List[str] = None

@dataclass
class ModelHealth:
    """Model health status"""
    timestamp: datetime
    model_name: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    accuracy: float
    requests_per_minute: float
    error_rate: float
    gpu_usage: float
    memory_usage: float

class AIPerformanceMonitor:
    """AI Performance Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("ai_performance")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.model_health = {}
        self.alert_thresholds = {
            "response_time_warning": 2000,  # 2 seconds
            "response_time_critical": 5000,  # 5 seconds
            "accuracy_warning": 0.85,  # 85%
            "accuracy_critical": 0.70,  # 70%
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "gpu_usage_warning": 80.0,  # 80%
            "gpu_usage_critical": 95.0,  # 95%
            "memory_usage_warning": 80.0,  # 80%
            "memory_usage_critical": 95.0,  # 95%
        }
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "avg_accuracy": 0.0,
            "peak_response_time": 0.0,
            "min_response_time": float('inf'),
            "max_response_time": 0.0
        }
    
    def record_metric(self, metric_name: str, value: float, unit: str, category: str, tags: List[str] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        
        # Update performance stats
        self._update_performance_stats()
        
        # Check for alerts
        self._check_performance_alerts(metric)
        
        self.logger.info(f"Recorded metric: {metric_name} = {value} {unit}")
    
    def record_model_health(self, model_name: str, response_time_ms: float, accuracy: float, 
                         requests_per_minute: float, error_rate: float, 
                         gpu_usage: float = 0, memory_usage: float = 0):
        """Record model health status"""
        # Determine health status
        status = "healthy"
        if (response_time_ms > self.alert_thresholds["response_time_critical"] or 
            accuracy < self.alert_thresholds["accuracy_critical"] or
            error_rate > self.alert_thresholds["error_rate_critical"] or
            gpu_usage > self.alert_thresholds["gpu_usage_critical"] or
            memory_usage > self.alert_thresholds["memory_usage_critical"]):
            status = "unhealthy"
        elif (response_time_ms > self.alert_thresholds["response_time_warning"] or 
              accuracy < self.alert_thresholds["accuracy_warning"] or
              error_rate > self.alert_thresholds["error_rate_warning"] or
              gpu_usage > self.alert_thresholds["gpu_usage_warning"] or
              memory_usage > self.alert_thresholds["memory_usage_warning"]):
            status = "degraded"
        
        health = ModelHealth(
            timestamp=datetime.now(),
            model_name=model_name,
            status=status,
            response_time_ms=response_time_ms,
            accuracy=accuracy,
            requests_per_minute=requests_per_minute,
            error_rate=error_rate,
            gpu_usage=gpu_usage,
            memory_usage=memory_usage
        )
        
        self.model_health[model_name] = health
        
        self.logger.info(f"Model health updated: {model_name} = {status}")
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        if not self.metrics_history:
            return
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 metrics
        
        # Calculate stats
        response_times = [m.value for m in recent_metrics if m.category == "response_time"]
        accuracy_metrics = [m.value for m in recent_metrics if m.category == "accuracy"]
        error_metrics = [m.value for m in recent_metrics if m.category == "error_rate"]
        
        if response_times:
            self.performance_stats["avg_response_time"] = sum(response_times) / len(response_times)
            self.performance_stats["peak_response_time"] = max(response_times)
            self.performance_stats["min_response_time"] = min(response_times)
        
        if accuracy_metrics:
            self.performance_stats["avg_accuracy"] = sum(accuracy_metrics) / len(accuracy_metrics)
        
        if error_metrics:
            self.performance_stats["error_rate"] = sum(error_metrics) / len(error_metrics)
        else:
            self.performance_stats["error_rate"] = 0.0
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts"""
        alerts = []
        
        if metric.category == "response_time" and metric.value > self.alert_thresholds["response_time_warning"]:
            alerts.append({
                "type": "performance",
                "severity": "warning" if metric.value < self.alert_thresholds["response_time_critical"] else "critical",
                "message": f"Response time {metric.value:.0f}ms exceeds threshold",
                "metric": metric.metric_name,
                "value": metric.value,
                "threshold": self.alert_thresholds["response_time_warning"]
            })
        
        if metric.category == "accuracy" and metric.value < self.alert_thresholds["accuracy_warning"]:
            alerts.append({
                "type": "performance",
                "severity": "warning" if metric.value < self.alert_thresholds["accuracy_critical"] else "critical",
                "message": f"Accuracy {metric.value:.2f} below threshold",
                "metric": metric.metric_name,
                "value": metric.value,
                "threshold": self.alert_thresholds["accuracy_warning"]
            })
        
        if metric.category == "error_rate" and metric.value > self.alert_thresholds["error_rate_warning"]:
            alerts.append({
                "type": "performance",
                "severity": "warning" if metric.value < self.alert_thresholds["error_rate_critical"] else "critical",
                "message": f"Error rate {metric.value:.2f} exceeds threshold",
                "metric": metric.metric_name,
                "value": metric.value,
                "threshold": self.alert_thresholds["error_rate_warning"]
            })
        
        if metric.category == "resource_usage" and metric.value > self.alert_thresholds["gpu_usage_warning"]:
            alerts.append({
                "type": "resource",
                "severity": "warning" if metric.value < self.alert_thresholds["gpu_usage_critical"] else "critical",
                "message": f"GPU usage {metric.value:.1f}% exceeds threshold",
                "metric": metric.metric_name,
                "value": metric.value,
                "threshold": self.alert_thresholds["gpu_usage_warning"]
            })
        
        if alerts:
            self.logger.warning(f"Performance alerts: {len(alerts)} alerts generated")
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Add mock data for testing
        mock_stats = {
            "total_requests": 1500,
            "successful_requests": 1425,
            "failed_requests": 75,
            "avg_response_time": 1250.5,
            "avg_accuracy": 0.92,
            "peak_response_time": 3500.0,
            "min_response_time": 450.0,
            "max_response_time": 3500.0,
            "error_rate": 0.05,
            "gpu_usage": 65.0,
            "memory_usage": 72.0
        }
        
        # Calculate summary
        summary = {
            "period_hours": hours,
            "total_metrics": len(recent_metrics),
            "performance_stats": mock_stats,
            "model_health": dict(self.model_health),
            "alerts": self._get_recent_alerts(hours),
            "trends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # This would integrate with actual alert system
        # For now, return mock alerts based on thresholds
        alerts = []
        
        if self.performance_stats["avg_response_time"] > self.alert_thresholds["response_time_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "performance",
                "severity": "warning",
                "message": f"Avg response time ({self.performance_stats['avg_response_time']:.0f}ms) exceeds threshold"
            })
        
        if self.performance_stats["avg_accuracy"] < self.alert_thresholds["accuracy_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "performance",
                "severity": "warning",
                "message": f"Accuracy ({self.performance_stats['avg_accuracy']:.2f}) below threshold"
            })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance trends"""
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
        """Generate performance recommendations"""
        recommendations = []
        
        # Response time recommendations
        if self.performance_stats["avg_response_time"] > self.alert_thresholds["response_time_warning"]:
            recommendations.append("Consider optimizing model or increasing resources")
        
        # Accuracy recommendations
        if self.performance_stats["avg_accuracy"] < self.alert_thresholds["accuracy_warning"]:
            recommendations.append("Review training data and model parameters")
        
        # Error rate recommendations
        if self.performance_stats["error_rate"] > self.alert_thresholds["error_rate_warning"]:
            recommendations.append("Investigate error patterns and improve error handling")
        
        return recommendations

# Global performance monitor instance
ai_performance_monitor = AIPerformanceMonitor()
