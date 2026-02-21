#!/usr/bin/env python3
"""
Historical Data Analysis System
Trending, analytics, and historical reporting for all dashboards
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class HistoricalDataPoint:
    """Historical data point structure"""
    timestamp: datetime
    metric_name: str
    value: float
    category: str
    source: str
    metadata: Dict[str, Any] = None

@dataclass
class TrendAnalysis:
    """Trend analysis data structure"""
    metric_name: str
    category: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1 scale
    change_percent: float
    confidence: float  # 0-1 scale
    period_days: int
    start_value: float
    end_value: float
    volatility: float
    seasonality_detected: bool

@dataclass
class AnomalyDetection:
    """Anomaly detection data structure"""
    timestamp: datetime
    metric_name: str
    category: str
    anomaly_type: str  # spike, drop, outlier, pattern_break
    severity: str  # low, medium, high, critical
    expected_value: float
    actual_value: float
    deviation_percent: float
    confidence: float

class HistoricalDataAnalyzer:
    """Historical Data Analysis System"""
    
    def __init__(self):
        self.logger = logging.getLogger("historical_data_analyzer")
        self.historical_data = defaultdict(list)  # category -> list of HistoricalDataPoint
        self.trend_cache = {}
        self.anomaly_cache = {}
        self.analysis_window_days = 30  # Default analysis window
        self.min_data_points = 10  # Minimum data points for analysis
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection
        self.trend_analysis_active = False
        self.analysis_thread = None
        self.analysis_interval = 3600  # 1 hour
        self.max_data_points_per_metric = 10000  # Maximum data points to keep per metric
        
        # Initialize with sample historical data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample historical data for testing"""
        import random
        
        # Generate sample data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        categories = {
            "ai_performance": ["response_time", "accuracy", "gpu_usage", "memory_usage"],
            "system_health": ["cpu_usage", "memory_usage", "disk_usage", "network_throughput"],
            "financial_analytics": ["mrr", "arr", "active_users", "revenue_growth"],
            "user_engagement": ["active_users", "bounce_rate", "session_duration", "feature_adoption"]
        }
        
        current_date = start_date
        while current_date <= end_date:
            for category, metrics in categories.items():
                for metric in metrics:
                    # Generate realistic sample data with trends and variations
                    base_value = self._get_base_value(metric)
                    
                    # Add trend
                    days_from_start = (current_date - start_date).days
                    trend_factor = 1.0 + (days_from_start * 0.01)  # 1% daily growth trend
                    
                    # Add daily variation
                    daily_variation = random.uniform(0.9, 1.1)
                    
                    # Add weekly pattern
                    weekday = current_date.weekday()
                    weekly_factor = 1.0
                    if weekday >= 5:  # Weekend
                        weekly_factor = 0.8 if metric in ["active_users", "bounce_rate"] else 1.2
                    
                    value = base_value * trend_factor * daily_variation * weekly_factor
                    
                    # Add some random noise
                    noise = random.uniform(-0.05, 0.05)
                    value = value * (1 + noise)
                    
                    data_point = HistoricalDataPoint(
                        timestamp=current_date,
                        metric_name=metric,
                        value=value,
                        category=category,
                        source="historical_sample",
                        metadata={
                            "day_of_week": weekday,
                            "is_weekend": weekday >= 5,
                            "days_from_start": days_from_start
                        }
                    )
                    
                    self.historical_data[category].append(data_point)
            
            current_date += timedelta(hours=6)  # Data every 6 hours
        
        self.logger.info(f"Initialized {sum(len(data) for data in self.historical_data.values())} historical data points")
    
    def _get_base_value(self, metric: str) -> float:
        """Get base value for a metric"""
        base_values = {
            "response_time": 1500.0,
            "accuracy": 0.92,
            "gpu_usage": 65.0,
            "memory_usage": 70.0,
            "cpu_usage": 45.0,
            "disk_usage": 60.0,
            "network_throughput": 1000000.0,
            "mrr": 15000.0,
            "arr": 180000.0,
            "active_users": 1200.0,
            "revenue_growth": 0.15,
            "bounce_rate": 0.35,
            "session_duration": 180.0,
            "feature_adoption": 0.75
        }
        return base_values.get(metric, 100.0)
    
    def add_data_point(self, metric_name: str, value: float, category: str, source: str, metadata: Dict[str, Any] = None):
        """Add a new data point to historical data"""
        data_point = HistoricalDataPoint(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            category=category,
            source=source,
            metadata=metadata or {}
        )
        
        self.historical_data[category].append(data_point)
        
        # Limit data points per metric
        if len(self.historical_data[category]) > self.max_data_points_per_metric:
            self.historical_data[category] = self.historical_data[category][-self.max_data_points_per_metric:]
        
        # Clear cache for affected metric
        cache_key = f"{category}_{metric_name}"
        if cache_key in self.trend_cache:
            del self.trend_cache[cache_key]
        if cache_key in self.anomaly_cache:
            del self.anomaly_cache[cache_key]
        
        self.logger.debug(f"Added historical data point: {category}.{metric_name} = {value}")
    
    def start_analysis(self):
        """Start historical data analysis"""
        if self.trend_analysis_active:
            self.logger.warning("Historical data analysis is already running")
            return
        
        self.trend_analysis_active = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        self.logger.info("Historical data analysis started")
    
    def stop_analysis(self):
        """Stop historical data analysis"""
        self.trend_analysis_active = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=10)
        self.logger.info("Historical data analysis stopped")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        while self.trend_analysis_active:
            try:
                # Perform trend analysis for all categories
                self._perform_trend_analysis()
                
                # Perform anomaly detection
                self._perform_anomaly_detection()
                
                # Clean up old cache entries
                self._cleanup_cache()
                
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in historical analysis loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _perform_trend_analysis(self):
        """Perform trend analysis for all metrics"""
        for category, data_points in self.historical_data.items():
            # Group by metric name
            metrics_data = defaultdict(list)
            for point in data_points:
                metrics_data[point.metric_name].append(point)
            
            for metric_name, points in metrics_data.items():
                if len(points) >= self.min_data_points:
                    cache_key = f"{category}_{metric_name}"
                    trend = self._calculate_trend(points)
                    self.trend_cache[cache_key] = trend
    
    def _calculate_trend(self, data_points: List[HistoricalDataPoint]) -> TrendAnalysis:
        """Calculate trend for a set of data points"""
        if len(data_points) < self.min_data_points:
            return None
        
        # Sort by timestamp
        sorted_points = sorted(data_points, key=lambda x: x.timestamp)
        values = [point.value for point in sorted_points]
        
        # Calculate linear regression
        n = len(values)
        x_values = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate trend direction
        if abs(slope) < 0.01:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        # Calculate trend strength (R-squared)
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        y_pred = [slope * x + (sum_y - slope * sum_x) / n for x in x_values]
        ss_res = sum((y - y_pred_i) ** 2 for y, y_pred_i in zip(values, y_pred))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        trend_strength = max(0, min(1, r_squared))
        
        # Calculate change percentage
        start_value = values[0]
        end_value = values[-1]
        change_percent = ((end_value - start_value) / start_value) * 100 if start_value != 0 else 0
        
        # Calculate volatility (standard deviation)
        volatility = statistics.stdev(values) if len(values) > 1 else 0
        
        # Calculate confidence based on data quality
        confidence = min(1.0, len(values) / 100) * trend_strength
        
        # Detect seasonality (simple weekly pattern detection)
        seasonality_detected = self._detect_seasonality(sorted_points)
        
        # Calculate period in days
        period_days = (sorted_points[-1].timestamp - sorted_points[0].timestamp).days
        
        return TrendAnalysis(
            metric_name=sorted_points[0].metric_name,
            category=sorted_points[0].category,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            change_percent=change_percent,
            confidence=confidence,
            period_days=period_days,
            start_value=start_value,
            end_value=end_value,
            volatility=volatility,
            seasonality_detected=seasonality_detected
        )
    
    def _detect_seasonality(self, data_points: List[HistoricalDataPoint]) -> bool:
        """Detect weekly seasonality in data"""
        if len(data_points) < 14:  # Need at least 2 weeks of data
            return False
        
        # Group by day of week
        weekday_values = defaultdict(list)
        for point in data_points:
            weekday = point.timestamp.weekday()
            weekday_values[weekday].append(point.value)
        
        # Calculate average for each weekday
        weekday_averages = {}
        for weekday, values in weekday_values.items():
            weekday_averages[weekday] = statistics.mean(values)
        
        # Check if there's a pattern (weekend vs weekday difference)
        weekday_avg = statistics.mean([weekday_averages[i] for i in range(5)])  # Mon-Fri
        weekend_avg = statistics.mean([weekday_averages[i] for i in range(5, 7)])  # Sat-Sun
        
        # If weekend and weekday averages differ by more than 20%, consider it seasonal
        if weekday_avg > 0:
            difference = abs(weekend_avg - weekday_avg) / weekday_avg
            return difference > 0.2
        
        return False
    
    def _perform_anomaly_detection(self):
        """Perform anomaly detection for all metrics"""
        for category, data_points in self.historical_data.items():
            # Group by metric name
            metrics_data = defaultdict(list)
            for point in data_points:
                metrics_data[point.metric_name].append(point)
            
            for metric_name, points in metrics_data.items():
                if len(points) >= self.min_data_points:
                    cache_key = f"{category}_{metric_name}"
                    anomalies = self._detect_anomalies(points)
                    self.anomaly_cache[cache_key] = anomalies
    
    def _detect_anomalies(self, data_points: List[HistoricalDataPoint]) -> List[AnomalyDetection]:
        """Detect anomalies in data points"""
        if len(data_points) < self.min_data_points:
            return []
        
        anomalies = []
        values = [point.value for point in data_points]
        
        # Calculate statistics
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_dev == 0:
            return anomalies
        
        # Detect outliers using standard deviation
        for i, point in enumerate(data_points):
            z_score = abs((point.value - mean) / std_dev)
            
            if z_score > self.anomaly_threshold:
                # Determine anomaly type
                if point.value > mean:
                    anomaly_type = "spike"
                else:
                    anomaly_type = "drop"
                
                # Determine severity
                if z_score > 4:
                    severity = "critical"
                elif z_score > 3:
                    severity = "high"
                elif z_score > 2.5:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Calculate deviation percentage
                deviation_percent = abs((point.value - mean) / mean) * 100 if mean != 0 else 0
                
                anomaly = AnomalyDetection(
                    timestamp=point.timestamp,
                    metric_name=point.metric_name,
                    category=point.category,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    expected_value=mean,
                    actual_value=point.value,
                    deviation_percent=deviation_percent,
                    confidence=min(1.0, z_score / 4)  # Normalize to 0-1
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        current_time = datetime.now()
        cache_ttl = timedelta(hours=24)
        
        # Clean trend cache
        expired_trends = []
        for key, trend in self.trend_cache.items():
            # Check if trend is older than TTL
            if hasattr(trend, 'timestamp'):
                if current_time - trend.timestamp > cache_ttl:
                    expired_trends.append(key)
        
        for key in expired_trends:
            del self.trend_cache[key]
        
        # Clean anomaly cache
        expired_anomalies = []
        for key, anomalies in self.anomaly_cache.items():
            # Remove anomalies older than TTL
            recent_anomalies = [a for a in anomalies if current_time - a.timestamp < cache_ttl]
            if recent_anomalies:
                self.anomaly_cache[key] = recent_anomalies
            else:
                expired_anomalies.append(key)
        
        for key in expired_anomalies:
            del self.anomaly_cache[key]
    
    def get_trend_analysis(self, category: str = None, metric_name: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get trend analysis for specified category and metric"""
        trends = []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for cache_key, trend in self.trend_cache.items():
            if category and not cache_key.startswith(f"{category}_"):
                continue
            
            if metric_name and not cache_key.endswith(f"_{metric_name}"):
                continue
            
            # Check if trend is within the requested time period
            if hasattr(trend, 'timestamp') and trend.timestamp < cutoff_date:
                continue
            
            trends.append(asdict(trend))
        
        return trends
    
    def get_anomaly_detection(self, category: str = None, metric_name: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get anomaly detection results for specified category and metric"""
        anomalies = []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for cache_key, anomaly_list in self.anomaly_cache.items():
            if category and not cache_key.startswith(f"{category}_"):
                continue
            
            if metric_name and not cache_key.endswith(f"_{metric_name}"):
                continue
            
            # Filter anomalies by time period
            recent_anomalies = [
                asdict(a) for a in anomaly_list 
                if a.timestamp >= cutoff_date
            ]
            
            anomalies.extend(recent_anomalies)
        
        # Sort by timestamp (newest first)
        anomalies.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return anomalies
    
    def get_historical_summary(self, category: str = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive historical summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        summary = {
            "period_days": days,
            "categories": {},
            "total_data_points": 0,
            "trends": [],
            "anomalies": [],
            "data_quality": {
                "completeness": 0,
                "consistency": 0,
                "timeliness": 0
            }
        }
        
        # Process each category
        for cat_name, data_points in self.historical_data.items():
            if category and cat_name != category:
                continue
            
            # Filter by time period
            recent_points = [p for p in data_points if p.timestamp >= cutoff_date]
            
            if not recent_points:
                continue
            
            # Calculate category statistics
            category_summary = {
                "data_points": len(recent_points),
                "metrics": list(set(p.metric_name for p in recent_points)),
                "date_range": {
                    "start": min(p.timestamp for p in recent_points).isoformat(),
                    "end": max(p.timestamp for p in recent_points).isoformat()
                },
                "value_ranges": {}
            }
            
            # Calculate value ranges for each metric
            metrics_data = defaultdict(list)
            for point in recent_points:
                metrics_data[point.metric_name].append(point.value)
            
            for metric, values in metrics_data.items():
                category_summary["value_ranges"][metric] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                }
            
            summary["categories"][cat_name] = category_summary
            summary["total_data_points"] += len(recent_points)
        
        # Add trends and anomalies
        summary["trends"] = self.get_trend_analysis(category=category, days=days)
        summary["anomalies"] = self.get_anomaly_detection(category=category, days=days)
        
        # Calculate data quality metrics
        if summary["total_data_points"] > 0:
            expected_points = days * 4  # Assuming 4 data points per day
            summary["data_quality"]["completeness"] = min(1.0, summary["total_data_points"] / expected_points)
            summary["data_quality"]["consistency"] = 0.95  # Mock value
            summary["data_quality"]["timeliness"] = 0.98  # Mock value
        
        return summary

# Global historical data analyzer instance
historical_data_analyzer = HistoricalDataAnalyzer()
