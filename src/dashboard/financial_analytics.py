#!/usr/bin/env python3
"""
Financial Analytics Dashboard
Real-time monitoring and analytics for business metrics and financial KPIs
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
class FinancialMetric:
    """Financial metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # revenue, users, acquisition, costs, engagement
    tags: List[str] = None

@dataclass
class UserMetrics:
    """User metrics data structure"""
    timestamp: datetime
    active_users: int
    new_signups: int
    churn_rate: float
    retention_rate: float
    avg_session_duration: float
    conversion_rate: float
    monthly_recurring_revenue: float
    customer_lifetime_value: float

@dataclass
class RevenueMetrics:
    """Revenue metrics data structure"""
    timestamp: datetime
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    total_revenue: float
    revenue_growth_rate: float
    average_revenue_per_user: float
    revenue_by_plan: Dict[str, float]
    revenue_by_region: Dict[str, float]

class FinancialAnalyticsMonitor:
    """Financial Analytics Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("financial_analytics")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.user_metrics = {}
        self.revenue_metrics = {}
        self.alert_thresholds = {
            "mrr_warning": 10000,      # $10,000
            "mrr_critical": 5000,       # $5,000
            "churn_rate_warning": 0.05,   # 5%
            "churn_rate_critical": 0.10,   # 10%
            "retention_rate_warning": 0.80, # 80%
            "retention_rate_critical": 0.70, # 70%
            "conversion_rate_warning": 0.02, # 2%
            "conversion_rate_critical": 0.01, # 1%
            "acquisition_cost_warning": 100,  # $100 per user
            "acquisition_cost_critical": 200, # $200 per user
        }
        self.financial_stats = {
            "total_revenue": 0,
            "total_users": 0,
            "total_customers": 0,
            "avg_revenue_per_user": 0,
            "churn_rate": 0,
            "retention_rate": 100,
            "conversion_rate": 0,
            "mrr_growth_rate": 0,
            "last_updated": datetime.now()
        }
    
    def record_metric(self, metric_name: str, value: float, unit: str, category: str, tags: List[str] = None):
        """Record a financial metric"""
        metric = FinancialMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        self.logger.info(f"Recorded financial metric: {metric_name} = {value} {unit}")
    
    def record_user_metrics(self, active_users: int, new_signups: int, churn_rate: float, 
                          retention_rate: float, avg_session_duration: float, conversion_rate: float,
                          monthly_recurring_revenue: float, customer_lifetime_value: float):
        """Record user metrics"""
        metrics = UserMetrics(
            timestamp=datetime.now(),
            active_users=active_users,
            new_signups=new_signups,
            churn_rate=churn_rate,
            retention_rate=retention_rate,
            avg_session_duration=avg_session_duration,
            conversion_rate=conversion_rate,
            monthly_recurring_revenue=monthly_recurring_revenue,
            customer_lifetime_value=customer_lifetime_value
        )
        
        self.user_metrics = metrics
        self.financial_stats.update({
            "total_users": active_users,
            "churn_rate": churn_rate,
            "retention_rate": retention_rate,
            "conversion_rate": conversion_rate,
            "avg_revenue_per_user": monthly_recurring_revenue,
            "last_updated": datetime.now()
        })
        
        self.logger.info(f"Recorded user metrics: {active_users} active, {new_signups} new signups")
    
    def record_revenue_metrics(self, mrr: float, arr: float, total_revenue: float, 
                           revenue_growth_rate: float, average_revenue_per_user: float,
                           revenue_by_plan: Dict[str, float] = None, revenue_by_region: Dict[str, float] = None):
        """Record revenue metrics"""
        metrics = RevenueMetrics(
            timestamp=datetime.now(),
            mrr=mrr,
            arr=arr,
            total_revenue=total_revenue,
            revenue_growth_rate=revenue_growth_rate,
            average_revenue_per_user=average_revenue_per_user,
            revenue_by_plan=revenue_by_plan or {},
            revenue_by_region=revenue_by_region or {}
        )
        
        self.revenue_metrics = metrics
        self.financial_stats.update({
            "mrr": mrr,
            "arr": arr,
            "total_revenue": total_revenue,
            "revenue_growth_rate": revenue_growth_rate,
            "avg_revenue_per_user": average_revenue_per_user,
            "last_updated": datetime.now()
        })
        
        self.logger.info(f"Recorded revenue metrics: MRR=${mrr}, ARR=${arr}")
    
    def get_financial_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get financial summary for specified time period"""
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
            "user_metrics": asdict(self.user_metrics) if self.user_metrics else None,
            "revenue_metrics": asdict(self.revenue_metrics) if self.revenue_metrics else None,
            "financial_stats": self.financial_stats,
            "alerts": self._get_recent_alerts(hours),
            "rends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent financial alerts"""
        alerts = []
        
        # Check MRR alerts
        if self.financial_stats.get("mrr", 0) < self.alert_thresholds["mrr_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "revenue",
                "severity": "critical",
                "message": f"MRR (${self.financial_stats['mrr']}) is below critical threshold (${self.alert_thresholds['mrr_critical']})"
            })
        elif self.financial_stats.get("mrr", 0) < self.alert_thresholds["mrr_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "revenue",
                "severity": "warning",
                "message": f"MRR (${self.financial_stats['mrr']}) is below warning threshold (${self.alert_thresholds['mrr_warning']})"
            })
        
        # Check churn rate alerts
        if self.financial_stats.get("churn_rate", 0) > self.alert_thresholds["churn_rate_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "retention",
                "severity": "critical",
                "message": f"Churn rate ({self.financial_stats['churn_rate']:.1%}) exceeds critical threshold ({self.alert_thresholds['churn_rate_critical']:.1%})"
            })
        elif self.financial_stats.get("churn_rate", 0) > self.alert_thresholds["churn_rate_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "retention",
                "severity": "warning",
                "message": f"Churn rate ({self.financial_stats['churn_rate']:.1%}) exceeds warning threshold ({self.alert_thresholds['churn_rate_warning']:.1%})"
            })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[FinancialMetric]) -> Dict[str, Any]:
        """Calculate financial trends"""
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
        """Generate financial recommendations"""
        recommendations = []
        
        # Revenue recommendations
        if self.financial_stats.get("mrr", 0) < self.alert_thresholds["mrr_warning"]:
            recommendations.append("Focus on customer retention and upselling to increase MRR")
        
        if self.financial_stats.get("revenue_growth_rate", 0) < 0:
            recommendations.append("Investigate revenue decline and adjust pricing strategy")
        
        # User retention recommendations
        if self.financial_stats.get("churn_rate", 0) > self.alert_thresholds["churn_rate_warning"]:
            recommendations.append("Implement customer success programs and improve onboarding")
        
        if self.financial_stats.get("retention_rate", 100) < self.alert_thresholds["retention_rate_warning"]:
            recommendations.append("Enhance product features and customer support")
        
        # Conversion recommendations
        if self.financial_stats.get("conversion_rate", 0) < self.alert_thresholds["conversion_rate_warning"]:
            recommendations.append("Optimize conversion funnel and marketing strategies")
        
        return recommendations

# Global financial analytics monitor instance
financial_analytics_monitor = FinancialAnalyticsMonitor()
