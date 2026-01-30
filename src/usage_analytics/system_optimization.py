"""
Usage Analytics and System Optimization Insights for Helm AI
============================================================

This module provides comprehensive usage analytics and system optimization capabilities:
- System usage tracking and analysis
- Performance monitoring and optimization
- Resource utilization analytics
- User behavior patterns
- System bottleneck identification
- Optimization recommendations
- Capacity planning insights
- Cost optimization analysis
"""

import asyncio
import json
import logging
import uuid
import psutil
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd

# Third-party imports
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import redis
import aiohttp

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager

logger = StructuredLogger("usage_analytics")

Base = declarative_base()


class MetricType(str, Enum):
    """Types of usage metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    API_CALLS = "api_calls"
    USER_SESSIONS = "user_sessions"
    DATABASE_QUERIES = "database_queries"
    CACHE_HITS = "cache_hits"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"


class OptimizationType(str, Enum):
    """Types of optimizations"""
    PERFORMANCE = "performance"
    COST = "cost"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    EFFICIENCY = "efficiency"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UsageMetric:
    """Usage metric data point"""
    id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    source: str  # service, component, or system name
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)


@dataclass
class SystemResource:
    """System resource information"""
    id: str
    name: str
    type: str  # server, database, cache, etc.
    cpu_cores: int
    memory_gb: float
    disk_gb: float
    network_mbps: float
    location: str
    cost_per_hour: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    id: str
    title: str
    description: str
    optimization_type: OptimizationType
    priority: str  # low, medium, high, critical
    estimated_savings: float  # cost or performance improvement
    implementation_effort: str  # low, medium, high
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UsagePattern:
    """Usage pattern analysis"""
    id: str
    pattern_type: str
    description: str
    confidence_score: float
    time_period: str
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class UsageMetrics(Base):
    """SQLAlchemy model for usage metrics"""
    __tablename__ = "usage_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(255))
    metadata = Column(JSONB)
    tags = Column(JSONB)


class SystemResources(Base):
    """SQLAlchemy model for system resources"""
    __tablename__ = "system_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    cpu_cores = Column(Integer)
    memory_gb = Column(Float)
    disk_gb = Column(Float)
    network_mbps = Column(Float)
    location = Column(String(255))
    cost_per_hour = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OptimizationRecommendations(Base):
    """SQLAlchemy model for optimization recommendations"""
    __tablename__ = "optimization_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(String(255), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    optimization_type = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False)
    estimated_savings = Column(Float)
    implementation_effort = Column(String(20))
    current_state = Column(JSONB)
    recommended_state = Column(JSONB)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    implemented_at = Column(DateTime)


class UsagePatterns(Base):
    """SQLAlchemy model for usage patterns"""
    __tablename__ = "usage_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_id = Column(String(255), nullable=False, unique=True, index=True)
    pattern_type = Column(String(100), nullable=False)
    description = Column(Text)
    confidence_score = Column(Float)
    time_period = Column(String(50))
    metrics = Column(JSONB)
    insights = Column(JSONB)
    recommendations = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class UsageAnalyticsEngine:
    """Usage Analytics and System Optimization Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Storage
        self.system_resources: Dict[str, SystemResource] = {}
        self.optimization_recommendations: Dict[str, OptimizationRecommendation] = {}
        self.usage_patterns: Dict[str, UsagePattern] = {}
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_interval = config.get('monitoring_interval', 60)  # seconds
        
        logger.info("Usage Analytics Engine initialized")
    
    async def record_usage_metric(self, metric: UsageMetric) -> bool:
        """Record a usage metric"""
        try:
            # Store in database
            metric_record = UsageMetrics(
                metric_id=metric.id,
                metric_type=metric.metric_type.value,
                value=metric.value,
                unit=metric.unit,
                timestamp=metric.timestamp,
                source=metric.source,
                metadata=metric.metadata,
                tags=list(metric.tags)
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(metric_record)
                session.commit()
            finally:
                session.close()
            
            # Cache in Redis for real-time access
            await self._cache_usage_metric(metric)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            logger.info("Usage metric recorded successfully", 
                       metric_id=metric.id, metric_type=metric.metric_type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to record usage metric", 
                        metric_id=metric.id, error=str(e))
            return False
    
    async def _cache_usage_metric(self, metric: UsageMetric):
        """Cache usage metric in Redis"""
        try:
            key = f"metric:{metric.metric_type.value}:{metric.source}"
            value = {
                "metric_id": metric.id,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat(),
                "source": metric.source,
                "metadata": metric.metadata
            }
            
            # Keep last 1000 metrics per type/source
            self.redis_client.lpush(key, json.dumps(value))
            self.redis_client.ltrim(key, 0, 999)
            self.redis_client.expire(key, 86400)  # 24 hours TTL
            
        except Exception as e:
            logger.error("Failed to cache usage metric", error=str(e))
    
    async def _check_metric_alerts(self, metric: UsageMetric):
        """Check if metric triggers any alerts"""
        try:
            # Define alert thresholds
            alert_thresholds = {
                MetricType.CPU_USAGE: {"warning": 70, "critical": 90},
                MetricType.MEMORY_USAGE: {"warning": 80, "critical": 95},
                MetricType.DISK_USAGE: {"warning": 80, "critical": 95},
                MetricType.ERROR_RATE: {"warning": 5, "critical": 10},
                MetricType.RESPONSE_TIME: {"warning": 1000, "critical": 5000}  # ms
            }
            
            if metric.metric_type in alert_thresholds:
                thresholds = alert_thresholds[metric.metric_type]
                
                if metric.value >= thresholds["critical"]:
                    await self._send_alert(metric, AlertSeverity.CRITICAL)
                elif metric.value >= thresholds["warning"]:
                    await self._send_alert(metric, AlertSeverity.MEDIUM)
            
        except Exception as e:
            logger.error("Failed to check metric alerts", error=str(e))
    
    async def _send_alert(self, metric: UsageMetric, severity: AlertSeverity):
        """Send alert for metric"""
        try:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "metric_type": metric.metric_type.value,
                "source": metric.source,
                "value": metric.value,
                "severity": severity.value,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"{metric.metric_type.value} for {metric.source} is {metric.value}{metric.unit}"
            }
            
            # Store alert in Redis for dashboard
            self.redis_client.lpush("alerts", json.dumps(alert))
            self.redis_client.ltrim("alerts", 0, 999)  # Keep last 1000 alerts
            
            logger.warning("Usage alert triggered", 
                         metric_type=metric.metric_type.value, 
                         source=metric.source, 
                         value=metric.value)
            
        except Exception as e:
            logger.error("Failed to send alert", error=str(e))
    
    async def start_monitoring(self):
        """Start background system monitoring"""
        try:
            self.monitoring_active = True
            
            # Start monitoring task
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("System monitoring started")
            
        except Exception as e:
            logger.error("Failed to start monitoring", error=str(e))
    
    async def stop_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring_active = False
        logger.info("System monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error("Monitoring loop error", error=str(e))
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            timestamp = datetime.utcnow()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = UsageMetric(
                id=str(uuid.uuid4()),
                metric_type=MetricType.CPU_USAGE,
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                source="system"
            )
            await self.record_usage_metric(cpu_metric)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_metric = UsageMetric(
                id=str(uuid.uuid4()),
                metric_type=MetricType.MEMORY_USAGE,
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                source="system",
                metadata={
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3)
                }
            )
            await self.record_usage_metric(memory_metric)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_metric = UsageMetric(
                id=str(uuid.uuid4()),
                metric_type=MetricType.DISK_USAGE,
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                source="system",
                metadata={
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3)
                }
            )
            await self.record_usage_metric(disk_metric)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_metric = UsageMetric(
                id=str(uuid.uuid4()),
                metric_type=MetricType.NETWORK_IO,
                value=network.bytes_sent + network.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                source="system",
                metadata={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            )
            await self.record_usage_metric(network_metric)
            
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
    
    async def get_usage_analytics(self, start_date: datetime, end_date: datetime,
                                 metric_types: Optional[List[MetricType]] = None,
                                 sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get usage analytics for a date range"""
        try:
            # Query usage metrics
            session = self.db_manager.get_session()
            try:
                query = session.query(UsageMetrics).filter(
                    UsageMetrics.timestamp >= start_date,
                    UsageMetrics.timestamp <= end_date
                )
                
                if metric_types:
                    query = query.filter(UsageMetrics.metric_type.in_([mt.value for mt in metric_types]))
                
                if sources:
                    query = query.filter(UsageMetrics.source.in_(sources))
                
                metrics_data = query.all()
            finally:
                session.close()
            
            if not metrics_data:
                return {"error": "No usage data found for the specified period"}
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "metric_id": m.metric_id,
                    "metric_type": m.metric_type,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp,
                    "source": m.source,
                    "metadata": m.metadata
                }
                for m in metrics_data
            ])
            
            # Calculate analytics
            analytics = {
                "summary": self._calculate_usage_summary(df),
                "trends": self._calculate_usage_trends(df),
                "by_type": self._calculate_usage_by_type(df),
                "by_source": self._calculate_usage_by_source(df),
                "anomalies": await self._detect_usage_anomalies(df),
                "patterns": await self._analyze_usage_patterns(df),
                "optimization_opportunities": await self._identify_optimization_opportunities(df)
            }
            
            logger.info("Usage analytics generated successfully", 
                       start_date=start_date.isoformat(), end_date=end_date.isoformat())
            
            return analytics
            
        except Exception as e:
            logger.error("Failed to get usage analytics", error=str(e))
            return {"error": str(e)}
    
    def _calculate_usage_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate usage summary statistics"""
        return {
            "total_metrics": len(df),
            "unique_sources": df['source'].nunique(),
            "metric_types": df['metric_type'].unique().tolist(),
            "date_range": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat()
            },
            "average_values": df.groupby('metric_type')['value'].mean().to_dict(),
            "peak_values": df.groupby('metric_type')['value'].max().to_dict(),
            "minimum_values": df.groupby('metric_type')['value'].min().to_dict()
        }
    
    def _calculate_usage_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate usage trends over time"""
        trends = {}
        
        for metric_type in df['metric_type'].unique():
            metric_df = df[df['metric_type'] == metric_type].copy()
            metric_df['hour'] = metric_df['timestamp'].dt.hour
            metric_df['date'] = metric_df['timestamp'].dt.date
            
            # Hourly trend
            hourly_trend = metric_df.groupby('hour')['value'].mean().reset_index()
            
            # Daily trend
            daily_trend = metric_df.groupby('date')['value'].mean().reset_index()
            
            trends[metric_type] = {
                "hourly_trend": hourly_trend.to_dict('records'),
                "daily_trend": daily_trend.to_dict('records')
            }
        
        return trends
    
    def _calculate_usage_by_type(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate usage breakdown by metric type"""
        by_type = df.groupby('metric_type').agg({
            'value': ['count', 'mean', 'std', 'min', 'max']
        }).reset_index()
        
        by_type.columns = ['metric_type', 'count', 'mean', 'std', 'min', 'max']
        
        return by_type.to_dict('records')
    
    def _calculate_usage_by_source(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate usage breakdown by source"""
        by_source = df.groupby('source').agg({
            'value': ['count', 'mean']
        }).reset_index()
        
        by_source.columns = ['source', 'count', 'mean']
        
        return by_source.to_dict('records')
    
    async def _detect_usage_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in usage patterns"""
        anomalies = []
        
        try:
            for metric_type in df['metric_type'].unique():
                metric_df = df[df['metric_type'] == metric_type].copy()
                
                if len(metric_df) < 10:  # Need enough data for anomaly detection
                    continue
                
                # Prepare data for anomaly detection
                X = metric_df[['value']].values
                
                # Use Isolation Forest for anomaly detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(X)
                
                # Find anomalies
                anomaly_indices = np.where(anomaly_labels == -1)[0]
                
                for idx in anomaly_indices:
                    anomaly_data = metric_df.iloc[idx]
                    anomalies.append({
                        "metric_type": metric_type,
                        "timestamp": anomaly_data['timestamp'].isoformat(),
                        "value": anomaly_data['value'],
                        "source": anomaly_data['source'],
                        "anomaly_score": iso_forest.decision_function(X)[idx][0],
                        "severity": "high" if abs(anomaly_data['value']) > metric_df['value'].std() * 2 else "medium"
                    })
            
        except Exception as e:
            logger.error("Failed to detect usage anomalies", error=str(e))
        
        return anomalies
    
    async def _analyze_usage_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze usage patterns"""
        patterns = []
        
        try:
            # Analyze peak usage times
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            for metric_type in df['metric_type'].unique():
                metric_df = df[df['metric_type'] == metric_type]
                
                # Peak hours
                hourly_avg = metric_df.groupby('hour')['value'].mean()
                peak_hours = hourly_avg.nlargest(3).index.tolist()
                
                # Peak days
                daily_avg = metric_df.groupby('day_of_week')['value'].mean()
                peak_days = daily_avg.nlargest(3).index.tolist()
                
                patterns.append({
                    "metric_type": metric_type,
                    "pattern_type": "peak_usage",
                    "description": f"Peak usage hours and days for {metric_type}",
                    "peak_hours": peak_hours,
                    "peak_days": peak_days,
                    "confidence_score": 0.8
                })
            
        except Exception as e:
            logger.error("Failed to analyze usage patterns", error=str(e))
        
        return patterns
    
    async def _identify_optimization_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        try:
            # Analyze each metric type for optimization opportunities
            for metric_type in df['metric_type'].unique():
                metric_df = df[df['metric_type'] == metric_type]
                
                avg_value = metric_df['value'].mean()
                max_value = metric_df['value'].max()
                
                # Identify optimization opportunities based on metric type
                if metric_type == MetricType.CPU_USAGE.value:
                    if avg_value > 70:
                        opportunities.append({
                            "type": "performance",
                            "description": f"High CPU usage ({avg_value:.1f}% avg)",
                            "recommendation": "Consider scaling up or optimizing CPU-intensive processes",
                            "potential_savings": "15-30% performance improvement"
                        })
                
                elif metric_type == MetricType.MEMORY_USAGE.value:
                    if avg_value > 80:
                        opportunities.append({
                            "type": "performance",
                            "description": f"High memory usage ({avg_value:.1f}% avg)",
                            "recommendation": "Consider memory optimization or scaling",
                            "potential_savings": "10-25% performance improvement"
                        })
                
                elif metric_type == MetricType.ERROR_RATE.value:
                    if avg_value > 5:
                        opportunities.append({
                            "type": "reliability",
                            "description": f"High error rate ({avg_value:.1f}% avg)",
                            "recommendation": "Investigate and fix root causes of errors",
                            "potential_savings": "20-50% reliability improvement"
                        })
                
                elif metric_type == MetricType.RESPONSE_TIME.value:
                    if avg_value > 1000:  # 1 second
                        opportunities.append({
                            "type": "performance",
                            "description": f"High response time ({avg_value:.1f}ms avg)",
                            "recommendation": "Optimize slow operations and implement caching",
                            "potential_savings": "30-60% response time improvement"
                        })
            
        except Exception as e:
            logger.error("Failed to identify optimization opportunities", error=str(e))
        
        return opportunities
    
    async def register_system_resource(self, resource: SystemResource) -> bool:
        """Register a system resource"""
        try:
            # Store in database
            resource_record = SystemResources(
                resource_id=resource.id,
                name=resource.name,
                type=resource.type,
                cpu_cores=resource.cpu_cores,
                memory_gb=resource.memory_gb,
                disk_gb=resource.disk_gb,
                network_mbps=resource.network_mbps,
                location=resource.location,
                cost_per_hour=resource.cost_per_hour
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(resource_record)
                session.commit()
            finally:
                session.close()
            
            # Store in memory
            self.system_resources[resource.id] = resource
            
            logger.info("System resource registered successfully", 
                       resource_id=resource.id, resource_type=resource.type)
            return True
            
        except Exception as e:
            logger.error("Failed to register system resource", 
                        resource_id=resource.id, error=str(e))
            return False
    
    async def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # Get recent usage data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            analytics = await self.get_usage_analytics(start_date, end_date)
            
            if "error" in analytics:
                return []
            
            # Generate recommendations based on analytics
            opportunities = analytics.get("optimization_opportunities", [])
            
            for opportunity in opportunities:
                recommendation = OptimizationRecommendation(
                    id=str(uuid.uuid4()),
                    title=f"{opportunity['type'].title()} Optimization",
                    description=opportunity['description'],
                    optimization_type=OptimizationType(opportunity['type']),
                    priority="high" if "high" in opportunity['description'].lower() else "medium",
                    estimated_savings=0.0,  # Would be calculated based on actual metrics
                    implementation_effort="medium",
                    current_state={"status": "current"},
                    recommended_state={"status": "optimized"}
                )
                
                # Store recommendation
                self.optimization_recommendations[recommendation.id] = recommendation
                
                recommendations.append({
                    "id": recommendation.id,
                    "title": recommendation.title,
                    "description": recommendation.description,
                    "type": recommendation.optimization_type.value,
                    "priority": recommendation.priority,
                    "recommendation": opportunity['recommendation'],
                    "potential_savings": opportunity['potential_savings']
                })
            
            logger.info("Optimization recommendations generated", 
                       count=len(recommendations))
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate optimization recommendations", error=str(e))
            return []
    
    async def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        try:
            # Get recent metrics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=1)
            
            session = self.db_manager.get_session()
            try:
                recent_metrics = session.query(UsageMetrics).filter(
                    UsageMetrics.timestamp >= start_date,
                    UsageMetrics.timestamp <= end_date
                ).all()
            finally:
                session.close()
            
            if not recent_metrics:
                return {"health_score": 0, "status": "no_data"}
            
            # Calculate health score based on different metrics
            health_scores = {}
            
            for metric in recent_metrics:
                metric_type = metric.metric_type
                
                if metric_type not in health_scores:
                    health_scores[metric_type] = []
                
                # Convert metric value to health score (0-100)
                if metric_type == MetricType.CPU_USAGE.value:
                    score = max(0, 100 - metric.value)  # Lower CPU is better
                elif metric_type == MetricType.MEMORY_USAGE.value:
                    score = max(0, 100 - metric.value)  # Lower memory is better
                elif metric_type == MetricType.ERROR_RATE.value:
                    score = max(0, 100 - metric.value * 10)  # Lower error rate is better
                elif metric_type == MetricType.RESPONSE_TIME.value:
                    score = max(0, 100 - (metric.value / 100))  # Lower response time is better
                else:
                    score = 80  # Default score for other metrics
                
                health_scores[metric_type].append(score)
            
            # Calculate overall health score
            overall_score = 0
            total_weight = 0
            
            for metric_type, scores in health_scores.items():
                avg_score = np.mean(scores)
                weight = 1.0  # Equal weight for all metrics
                
                overall_score += avg_score * weight
                total_weight += weight
            
            if total_weight > 0:
                overall_score = overall_score / total_weight
            
            # Determine status
            if overall_score >= 90:
                status = "excellent"
            elif overall_score >= 80:
                status = "good"
            elif overall_score >= 70:
                status = "fair"
            elif overall_score >= 60:
                status = "poor"
            else:
                status = "critical"
            
            return {
                "health_score": round(overall_score, 2),
                "status": status,
                "metric_scores": {k: round(np.mean(v), 2) for k, v in health_scores.items()},
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to calculate system health score", error=str(e))
            return {"health_score": 0, "status": "error"}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_resources": len(self.system_resources),
            "total_recommendations": len(self.optimization_recommendations),
            "monitoring_active": self.monitoring_active,
            "monitoring_interval": self.monitoring_interval,
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
USAGE_ANALYTICS_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "data_lake": {
        "s3_bucket": "helm-ai-data-lake"
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": 0
    },
    "monitoring_interval": 60  # seconds
}


# Initialize usage analytics engine
usage_analytics_engine = UsageAnalyticsEngine(USAGE_ANALYTICS_CONFIG)

# Export main components
__all__ = [
    'UsageAnalyticsEngine',
    'UsageMetric',
    'SystemResource',
    'OptimizationRecommendation',
    'UsagePattern',
    'MetricType',
    'OptimizationType',
    'AlertSeverity',
    'usage_analytics_engine'
]
