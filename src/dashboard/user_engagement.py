#!/usr/bin/env python3
"""
User Engagement Analytics Dashboard
Real-time monitoring and analytics for user behavior, feature adoption, and engagement metrics
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
class EngagementMetric:
    """User engagement metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # sessions, features, devices, geography, behavior
    tags: List[str] = None

@dataclass
class UserBehavior:
    """User behavior data structure"""
    timestamp: datetime
    user_id: str
    session_id: str
    page_views: int
    session_duration: float
    bounce_rate: float
    pages_per_session: float
    exit_page: str
    entry_page: str
    device_type: str
    browser: str
    location: str

@dataclass
class FeatureUsage:
    """Feature usage data structure"""
    timestamp: datetime
    feature_name: str
    active_users: int
    total_users: int
    usage_frequency: float
    average_session_time: float
    adoption_rate: float
    satisfaction_score: float

class UserEngagementMonitor:
    """User Engagement Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("user_engagement")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.user_behavior = {}
        self.feature_usage = {}
        self.geographic_data = defaultdict(int)
        self.device_data = defaultdict(int)
        self.alert_thresholds = {
            "bounce_rate_warning": 0.40,      # 40%
            "bounce_rate_critical": 0.60,     # 60%
            "session_duration_warning": 30,    # 30 seconds
            "session_duration_critical": 10,   # 10 seconds
            "adoption_rate_warning": 0.20,     # 20%
            "adoption_rate_critical": 0.10,    # 10%
            "satisfaction_warning": 3.5,       # 3.5/5 rating
            "satisfaction_critical": 2.5,     # 2.5/5 rating
        }
        self.engagement_stats = {
            "total_sessions": 0,
            "total_page_views": 0,
            "avg_session_duration": 0,
            "bounce_rate": 0,
            "pages_per_session": 0,
            "active_users": 0,
            "new_users": 0,
            "returning_users": 0,
            "feature_adoption_rate": 0,
            "user_satisfaction": 0
        }
    
    def record_metric(self, metric_name: str, value: float, unit: str, category: str, tags: List[str] = None):
        """Record an engagement metric"""
        metric = EngagementMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        self.logger.info(f"Recorded engagement metric: {metric_name} = {value} {unit}")
    
    def record_user_behavior(self, user_id: str, session_id: str, page_views: int, 
                          session_duration: float, bounce_rate: float, pages_per_session: float,
                          exit_page: str, entry_page: str, device_type: str, 
                          browser: str, location: str):
        """Record user behavior data"""
        behavior = UserBehavior(
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            page_views=page_views,
            session_duration=session_duration,
            bounce_rate=bounce_rate,
            pages_per_session=pages_per_session,
            exit_page=exit_page,
            entry_page=entry_page,
            device_type=device_type,
            browser=browser,
            location=location
        )
        
        self.user_behavior[user_id] = behavior
        self.geographic_data[location] += 1
        
        # Update engagement stats
        self.engagement_stats["total_sessions"] += 1
        self.engagement_stats["total_page_views"] += page_views
        self.engagement_stats["avg_session_duration"] = self._calculate_avg_session_duration()
        self.engagement_stats["bounce_rate"] = self._calculate_avg_bounce_rate()
        self.engagement_stats["pages_per_session"] = self._calculate_avg_pages_per_session()
        
        self.logger.info(f"Recorded user behavior for user {user_id}: {page_views} pages in {session_duration:.1f}s")
    
    def record_feature_usage(self, feature_name: str, active_users: int, total_users: int, 
                        usage_frequency: float, average_session_time: float, 
                        adoption_rate: float, satisfaction_score: float):
        """Record feature usage data"""
        usage = FeatureUsage(
            timestamp=datetime.now(),
            feature_name=feature_name,
            active_users=active_users,
            total_users=total_users,
            usage_frequency=usage_frequency,
            average_session_time=average_session_time,
            adoption_rate=adoption_rate,
            satisfaction_score=satisfaction_score
        )
        
        self.feature_usage[feature_name] = usage
        
        # Update engagement stats
        self.engagement_stats["feature_adoption_rate"] = self._calculate_avg_adoption_rate()
        self.engagement_stats["user_satisfaction"] = self._calculate_avg_satisfaction()
        
        self.logger.info(f"Recorded feature usage: {feature_name} - {adoption_rate:.1%} adoption")
    
    def record_device_data(self, device_type: str, user_count: int, session_count: int):
        """Record device usage data"""
        self.device_data[device_type] = user_count
        self.logger.info(f"Recorded device data: {device_type} - {user_count} users, {session_count} sessions")
    
    def get_engagement_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get engagement summary for specified time period"""
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
            "engagement_stats": self.engagement_stats,
            "user_behavior": dict(self.user_behavior),
            "feature_usage": dict(self.feature_usage),
            "geographic_data": dict(self.geographic_data),
            "device_data": dict(self.device_data),
            "alerts": self._get_recent_alerts(hours),
            "rends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _calculate_avg_session_duration(self) -> float:
        """Calculate average session duration"""
        if not self.user_behavior:
            return 0.0
        
        durations = [b.session_duration for b in self.user_behavior.values()]
        return sum(durations) / len(durations) if durations else 0.0
    
    def _calculate_avg_bounce_rate(self) -> float:
        """Calculate average bounce rate"""
        if not self.user_behavior:
            return 0.0
        
        bounce_rates = [b.bounce_rate for b in self.user_behavior.values()]
        return sum(bounce_rates) / len(bounce_rates) if bounce_rates else 0.0
    
    def _calculate_avg_pages_per_session(self) -> float:
        """Calculate average pages per session"""
        if not self.user_behavior:
            return 0.0
        
        pages_per_session = [b.pages_per_session for b in self.user_behavior.values()]
        return sum(pages_per_session) / len(pages_per_session) if pages_per_session else 0.0
    
    def _calculate_avg_adoption_rate(self) -> float:
        """Calculate average feature adoption rate"""
        if not self.feature_usage:
            return 0.0
        
        adoption_rates = [f.adoption_rate for f in self.feature_usage.values()]
        return sum(adoption_rates) / len(adoption_rates) if adoption_rates else 0.0
    
    def _calculate_avg_satisfaction(self) -> float:
        """Calculate average user satisfaction"""
        if not self.feature_usage:
            return 0.0
        
        satisfaction_scores = [f.satisfaction_score for f in self.feature_usage.values()]
        return sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.0
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent engagement alerts"""
        alerts = []
        
        # Check bounce rate alerts
        if self.engagement_stats["bounce_rate"] > self.alert_thresholds["bounce_rate_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "critical",
                "message": f"Bounce rate ({self.engagement_stats['bounce_rate']:.1%}) exceeds critical threshold ({self.alert_thresholds['bounce_rate_critical']:.1%})"
            })
        elif self.engagement_stats["bounce_rate"] > self.alert_thresholds["bounce_rate_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "warning",
                "message": f"Bounce rate ({self.engagement_stats['bounce_rate']:.1%}) exceeds warning threshold ({self.alert_thresholds['bounce_rate_warning']:.1%})"
            })
        
        # Check session duration alerts
        if self.engagement_stats["avg_session_duration"] < self.alert_thresholds["session_duration_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "critical",
                "message": f"Average session duration ({self.engagement_stats['avg_session_duration']:.1f}s) is below critical threshold ({self.alert_thresholds['session_duration']}s)"
            })
        elif self.engagement_stats["avg_session_duration"] < self.alert_thresholds["session_duration_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "warning",
                "message": f"Average session duration ({self.engagement_stats['avg_session_duration']:.1f}s) is below warning threshold ({self.alert_thresholds['session_duration']}s)"
            })
        
        # Check adoption rate alerts
        if self.engagement_stats["feature_adoption_rate"] < self.alert_thresholds["adoption_rate_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "critical",
                "message": f"Feature adoption rate ({self.engagement_stats['feature_adoption_rate']:.1%}) is below critical threshold ({self.alert_thresholds['adoption_rate_critical']:.1%})"
            })
        elif self.engagement_stats["feature_adoption_rate"] < self.alert_thresholds["adoption_rate_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "engagement",
                "severity": "warning",
                "message": f"Feature adoption rate ({self.engagement_stats['feature_adoption_rate']:.1%}) is below warning threshold ({self.alert_thresholds['adoption_rate_warning']:.1%})"
            })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[EngagementMetric]) -> Dict[str, Any]:
        """Calculate engagement trends"""
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
                    
                    trend = "increasing" if recent_avg > older_avg else "decreasing" if recent_avg < older_avg else "stable"
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
                    
                    trends[category] = {
                        "trend": trend,
                        "change_percent": change_percent,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg
                    }
        
        return trends
    
    def _generate_recommendations(self) -> List[str]:
        """Generate engagement recommendations"""
        recommendations = []
        
        # Bounce rate recommendations
        if self.engagement_stats["bounce_rate"] > self.alert_thresholds["bounce_rate_warning"]:
            recommendations.append("Improve onboarding and user experience to reduce bounce rate")
        
        # Session duration recommendations
        if self.engagement_stats["avg_session_duration"] < self.alert_thresholds["session_duration_warning"]:
            recommendations.append("Enhance content and features to increase session duration")
        
        # Feature adoption recommendations
        if self.engagement_stats["feature_adoption_rate"] < self.alert_thresholds["adoption_rate_warning"]:
            recommendations.append("Improve feature discoverability and user education")
        
        # Satisfaction recommendations
        if self.engagement_stats["user_satisfaction"] < self.alert_thresholds["satisfaction_warning"]:
            recommendations.append("Address user feedback and improve product experience")
        
        return recommendations

# Global user engagement monitor instance
user_engagement_monitor = UserEngagementMonitor()
