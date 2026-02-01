#!/usr/bin/env python3
"""
Stellar Logic AI - Comprehensive Security Monitoring Dashboard
Real-time security monitoring dashboard with advanced metrics and visualization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import json
from collections import defaultdict, deque

class MetricType(Enum):
    """Types of security metrics"""
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    RESPONSE_TIME = "response_time"
    THREAT_LEVEL = "threat_level"
    SYSTEM_HEALTH = "system_health"
    NETWORK_TRAFFIC = "network_traffic"
    ANOMALY_SCORE = "anomaly_score"
    COMPLIANCE_SCORE = "compliance_score"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SecurityMetric:
    """Security metric data point"""
    metric_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    threshold: float
    status: str
    metadata: Dict[str, Any]

@dataclass
class SecurityAlert:
    """Security alert information"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    source: str
    affected_systems: List[str]
    metrics_impacted: List[str]
    resolution_status: str
    metadata: Dict[str, Any]

@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    position: Dict[str, int]
    size: Dict[str, int]
    data_source: str
    refresh_rate: int
    configuration: Dict[str, Any]

@dataclass
class DashboardProfile:
    """Dashboard monitoring profile"""
    dashboard_id: str
    widgets: Dict[str, DashboardWidget]
    metrics: deque
    alerts: deque
    system_status: Dict[str, Any]
    performance_metrics: Dict[str, float]
    last_updated: datetime
    total_metrics: int
    total_alerts: int

class SecurityMonitoringDashboard:
    """Comprehensive security monitoring dashboard system"""
    
    def __init__(self):
        self.profiles = {}
        self.metrics = {}
        self.alerts = {}
        self.widgets = {}
        
        # Dashboard configuration
        self.dashboard_config = {
            'refresh_interval': 5,  # seconds
            'max_metrics_per_widget': 100,
            'alert_retention_period': 24,  # hours
            'metric_retention_period': 7,  # days
            'auto_refresh': True,
            'theme': 'dark',
            'layout': 'grid'
        }
        
        # Metric thresholds
        self.metric_thresholds = {
            MetricType.DETECTION_RATE: {'warning': 0.8, 'critical': 0.6},
            MetricType.FALSE_POSITIVE_RATE: {'warning': 0.1, 'critical': 0.2},
            MetricType.RESPONSE_TIME: {'warning': 1000, 'critical': 5000},  # milliseconds
            MetricType.THREAT_LEVEL: {'warning': 0.7, 'critical': 0.9},
            MetricType.SYSTEM_HEALTH: {'warning': 0.8, 'critical': 0.6},
            MetricType.NETWORK_TRAFFIC: {'warning': 1000, 'critical': 5000},  # MB/s
            MetricType.ANOMALY_SCORE: {'warning': 0.7, 'critical': 0.9},
            MetricType.COMPLIANCE_SCORE: {'warning': 0.8, 'critical': 0.6}
        }
        
        # Performance metrics
        self.total_metrics = 0
        self.total_alerts = 0
        self.active_dashboards = 0
        
        # Initialize default widgets
        self._initialize_default_widgets()
        
    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets"""
        self.widgets = {
            'detection_rate_widget': DashboardWidget(
                widget_id='detection_rate_widget',
                widget_type='line_chart',
                title='Detection Rate Over Time',
                position={'x': 0, 'y': 0},
                size={'width': 6, 'height': 4},
                data_source='detection_rate_metrics',
                refresh_rate=5,
                configuration={
                    'y_axis_min': 0,
                    'y_axis_max': 1,
                    'show_grid': True,
                    'show_legend': True
                }
            ),
            'threat_level_widget': DashboardWidget(
                widget_id='threat_level_widget',
                widget_type='gauge',
                title='Current Threat Level',
                position={'x': 6, 'y': 0},
                size={'width': 3, 'height': 4},
                data_source='threat_level_metrics',
                refresh_rate=2,
                configuration={
                    'min_value': 0,
                    'max_value': 1,
                    'color_zones': [
                        {'min': 0, 'max': 0.3, 'color': 'green'},
                        {'min': 0.3, 'max': 0.7, 'color': 'yellow'},
                        {'min': 0.7, 'max': 1, 'color': 'red'}
                    ]
                }
            ),
            'system_health_widget': DashboardWidget(
                widget_id='system_health_widget',
                widget_type='status_panel',
                title='System Health Status',
                position={'x': 9, 'y': 0},
                size={'width': 3, 'height': 4},
                data_source='system_health_metrics',
                refresh_rate=10,
                configuration={
                    'show_details': True,
                    'alert_threshold': 0.8
                }
            ),
            'alerts_widget': DashboardWidget(
                widget_id='alerts_widget',
                widget_type='alert_list',
                title='Recent Security Alerts',
                position={'x': 0, 'y': 4},
                size={'width': 12, 'height': 6},
                data_source='security_alerts',
                refresh_rate=3,
                configuration={
                    'max_alerts': 20,
                    'group_by_severity': True,
                    'auto_refresh': True
                }
            ),
            'network_traffic_widget': DashboardWidget(
                widget_id='network_traffic_widget',
                widget_type='area_chart',
                title='Network Traffic Analysis',
                position={'x': 0, 'y': 10},
                size={'width': 8, 'height': 4},
                data_source='network_traffic_metrics',
                refresh_rate=5,
                configuration={
                    'show_trend': True,
                    'show_peaks': True,
                    'time_window': 3600  # 1 hour
                }
            ),
            'anomaly_detection_widget': DashboardWidget(
                widget_id='anomaly_detection_widget',
                widget_type='heatmap',
                title='Anomaly Detection Heatmap',
                position={'x': 8, 'y': 10},
                size={'width': 4, 'height': 4},
                data_source='anomaly_metrics',
                refresh_rate=10,
                configuration={
                    'color_scale': 'viridis',
                    'show_values': False,
                    'interpolate': True
                }
            ),
            'compliance_widget': DashboardWidget(
                widget_id='compliance_widget',
                widget_type='progress_bar',
                title='Compliance Status',
                position={'x': 0, 'y': 14},
                size={'width': 6, 'height': 2},
                data_source='compliance_metrics',
                refresh_rate=60,
                configuration={
                    'show_percentage': True,
                    'color_by_status': True
                }
            ),
            'performance_widget': DashboardWidget(
                widget_id='performance_widget',
                widget_type='metric_cards',
                title='Performance Metrics',
                position={'x': 6, 'y': 14},
                size={'width': 6, 'height': 2},
                data_source='performance_metrics',
                refresh_rate=5,
                configuration={
                    'card_layout': 'horizontal',
                    'show_trends': True
                }
            )
        }
    
    def create_profile(self, dashboard_id: str) -> DashboardProfile:
        """Create dashboard monitoring profile"""
        profile = DashboardProfile(
            dashboard_id=dashboard_id,
            widgets=self.widgets.copy(),
            metrics=deque(maxlen=10000),
            alerts=deque(maxlen=1000),
            system_status={
                'overall_health': 1.0,
                'active_threats': 0,
                'system_load': 0.0,
                'response_time': 0.0
            },
            performance_metrics={
                'avg_detection_rate': 0.0,
                'avg_response_time': 0.0,
                'false_positive_rate': 0.0,
                'uptime_percentage': 100.0
            },
            last_updated=datetime.now(),
            total_metrics=0,
            total_alerts=0
        )
        
        self.profiles[dashboard_id] = profile
        self.active_dashboards += 1
        return profile
    
    def add_metric(self, dashboard_id: str, metric: SecurityMetric) -> List[SecurityAlert]:
        """Add security metric and generate alerts if needed"""
        profile = self.profiles.get(dashboard_id)
        if not profile:
            profile = self.create_profile(dashboard_id)
        
        # Add metric to profile
        profile.metrics.append(metric)
        profile.total_metrics = len(profile.metrics)
        profile.last_updated = datetime.now()
        
        # Update global metrics
        self.metrics[metric.metric_id] = metric
        self.total_metrics = len(self.metrics)
        
        # Check for alerts
        alerts = self._check_metric_alerts(profile, metric)
        
        # Store alerts
        for alert in alerts:
            profile.alerts.append(alert)
            profile.total_alerts = len(profile.alerts)
            self.alerts[alert.alert_id] = alert
            self.total_alerts = len(self.alerts)
        
        # Update performance metrics
        self._update_performance_metrics(profile, metric)
        
        return alerts
    
    def add_alert(self, dashboard_id: str, alert: SecurityAlert) -> None:
        """Add security alert to dashboard"""
        profile = self.profiles.get(dashboard_id)
        if not profile:
            profile = self.create_profile(dashboard_id)
        
        # Add alert to profile
        profile.alerts.append(alert)
        profile.total_alerts = len(profile.alerts)
        profile.last_updated = datetime.now()
        
        # Update global alerts
        self.alerts[alert.alert_id] = alert
        self.total_alerts = len(self.alerts)
        
        # Update system status
        self._update_system_status(profile, alert)
    
    def _check_metric_alerts(self, profile: DashboardProfile, metric: SecurityMetric) -> List[SecurityAlert]:
        """Check if metric triggers any alerts"""
        alerts = []
        
        # Get threshold for metric type
        thresholds = self.metric_thresholds.get(metric.metric_type, {})
        
        # Check warning threshold
        if 'warning' in thresholds and metric.value <= thresholds['warning']:
            alert = SecurityAlert(
                alert_id=f"warning_{metric.metric_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                severity=AlertSeverity.WARNING,
                title=f"Warning: {metric.metric_type.value} Below Threshold",
                description=f"{metric.metric_type.value} is {metric.value:.3f}, below warning threshold of {thresholds['warning']}",
                timestamp=datetime.now(),
                source=metric.metadata.get('source', 'Unknown'),
                affected_systems=metric.metadata.get('systems', []),
                metrics_impacted=[metric.metric_id],
                resolution_status='open',
                metadata={'threshold_type': 'warning', 'threshold_value': thresholds['warning']}
            )
            alerts.append(alert)
        
        # Check critical threshold
        if 'critical' in thresholds and metric.value <= thresholds['critical']:
            alert = SecurityAlert(
                alert_id=f"critical_{metric.metric_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                severity=AlertSeverity.CRITICAL,
                title=f"Critical: {metric.metric_type.value} Below Threshold",
                description=f"{metric.metric_type.value} is {metric.value:.3f}, below critical threshold of {thresholds['critical']}",
                timestamp=datetime.now(),
                source=metric.metadata.get('source', 'Unknown'),
                affected_systems=metric.metadata.get('systems', []),
                metrics_impacted=[metric.metric_id],
                resolution_status='open',
                metadata={'threshold_type': 'critical', 'threshold_value': thresholds['critical']}
            )
            alerts.append(alert)
        
        return alerts
    
    def _update_performance_metrics(self, profile: DashboardProfile, metric: SecurityMetric) -> None:
        """Update performance metrics based on new metric"""
        # Update detection rate
        if metric.metric_type == MetricType.DETECTION_RATE:
            recent_metrics = [m for m in profile.metrics if m.metric_type == MetricType.DETECTION_RATE][-100:]
            if recent_metrics:
                profile.performance_metrics['avg_detection_rate'] = sum(m.value for m in recent_metrics) / len(recent_metrics)
        
        # Update response time
        if metric.metric_type == MetricType.RESPONSE_TIME:
            recent_metrics = [m for m in profile.metrics if m.metric_type == MetricType.RESPONSE_TIME][-100:]
            if recent_metrics:
                profile.performance_metrics['avg_response_time'] = sum(m.value for m in recent_metrics) / len(recent_metrics)
        
        # Update false positive rate
        if metric.metric_type == MetricType.FALSE_POSITIVE_RATE:
            recent_metrics = [m for m in profile.metrics if m.metric_type == MetricType.FALSE_POSITIVE_RATE][-100:]
            if recent_metrics:
                profile.performance_metrics['false_positive_rate'] = sum(m.value for m in recent_metrics) / len(recent_metrics)
    
    def _update_system_status(self, profile: DashboardProfile, alert: SecurityAlert) -> None:
        """Update system status based on alert"""
        # Update active threats
        if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
            profile.system_status['active_threats'] += 1
        
        # Update overall health
        if alert.severity == AlertSeverity.CRITICAL:
            profile.system_status['overall_health'] *= 0.9
        elif alert.severity == AlertSeverity.ERROR:
            profile.system_status['overall_health'] *= 0.95
        elif alert.severity == AlertSeverity.WARNING:
            profile.system_status['overall_health'] *= 0.98
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get complete dashboard data"""
        profile = self.profiles.get(dashboard_id)
        if not profile:
            return {'error': 'Dashboard not found'}
        
        # Generate widget data
        widget_data = {}
        for widget_id, widget in profile.widgets.items():
            widget_data[widget_id] = self._generate_widget_data(profile, widget)
        
        return {
            'dashboard_id': dashboard_id,
            'widgets': widget_data,
            'system_status': profile.system_status,
            'performance_metrics': profile.performance_metrics,
            'recent_alerts': list(profile.alerts)[-20:],
            'summary': self._generate_dashboard_summary(profile),
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _generate_widget_data(self, profile: DashboardProfile, widget: DashboardWidget) -> Dict[str, Any]:
        """Generate data for specific widget"""
        # Filter metrics based on widget data source
        if widget.data_source == 'detection_rate_metrics':
            metrics = [m for m in profile.metrics if m.metric_type == MetricType.DETECTION_RATE][-widget.configuration.get('max_points', 100):]
            return {
                'type': 'line_chart',
                'data': {
                    'labels': [m.timestamp.strftime('%H:%M') for m in metrics],
                    'values': [m.value for m in metrics]
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'threat_level_metrics':
            recent_metrics = [m for m in profile.metrics if m.metric_type == MetricType.THREAT_LEVEL][-10:]
            current_value = recent_metrics[-1].value if recent_metrics else 0.0
            return {
                'type': 'gauge',
                'data': {
                    'current_value': current_value,
                    'trend': 'up' if len(recent_metrics) >= 2 and recent_metrics[-1].value > recent_metrics[-2].value else 'down'
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'system_health_metrics':
            return {
                'type': 'status_panel',
                'data': {
                    'overall_health': profile.system_status['overall_health'],
                    'active_threats': profile.system_status['active_threats'],
                    'system_load': profile.system_status['system_load'],
                    'response_time': profile.system_status['response_time']
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'security_alerts':
            recent_alerts = list(profile.alerts)[-widget.configuration.get('max_alerts', 20):]
            return {
                'type': 'alert_list',
                'data': {
                    'alerts': [
                        {
                            'id': alert.alert_id,
                            'severity': alert.severity.value,
                            'title': alert.title,
                            'description': alert.description,
                            'timestamp': alert.timestamp.isoformat(),
                            'source': alert.source,
                            'status': alert.resolution_status
                        }
                        for alert in recent_alerts
                    ]
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'network_traffic_metrics':
            metrics = [m for m in profile.metrics if m.metric_type == MetricType.NETWORK_TRAFFIC][-100:]
            return {
                'type': 'area_chart',
                'data': {
                    'labels': [m.timestamp.strftime('%H:%M') for m in metrics],
                    'values': [m.value for m in metrics]
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'anomaly_metrics':
            # Generate heatmap data
            anomaly_metrics = [m for m in profile.metrics if m.metric_type == MetricType.ANOMALY_SCORE][-50:]
            heatmap_data = []
            for i, metric in enumerate(anomaly_metrics):
                heatmap_data.append({
                    'x': i % 10,
                    'y': i // 10,
                    'value': metric.value
                })
            
            return {
                'type': 'heatmap',
                'data': {
                    'heatmap': heatmap_data
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'compliance_metrics':
            compliance_metrics = [m for m in profile.metrics if m.metric_type == MetricType.COMPLIANCE_SCORE][-10:]
            current_compliance = compliance_metrics[-1].value if compliance_metrics else 1.0
            return {
                'type': 'progress_bar',
                'data': {
                    'current_value': current_compliance,
                    'target_value': 1.0,
                    'percentage': current_compliance * 100
                },
                'configuration': widget.configuration
            }
        
        elif widget.data_source == 'performance_metrics':
            return {
                'type': 'metric_cards',
                'data': {
                    'cards': [
                        {'title': 'Detection Rate', 'value': f"{profile.performance_metrics['avg_detection_rate']:.2%}", 'trend': 'up'},
                        {'title': 'Response Time', 'value': f"{profile.performance_metrics['avg_response_time']:.0f}ms", 'trend': 'down'},
                        {'title': 'False Positive Rate', 'value': f"{profile.performance_metrics['false_positive_rate']:.2%}", 'trend': 'down'},
                        {'title': 'Uptime', 'value': f"{profile.performance_metrics['uptime_percentage']:.1f}%", 'trend': 'stable'}
                    ]
                },
                'configuration': widget.configuration
            }
        
        return {'type': 'unknown', 'data': {}, 'configuration': widget.configuration}
    
    def _generate_dashboard_summary(self, profile: DashboardProfile) -> Dict[str, Any]:
        """Generate dashboard summary"""
        recent_alerts = list(profile.alerts)[-100:]
        
        # Count alerts by severity
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert.severity.value] += 1
        
        # Calculate metrics summary
        recent_metrics = list(profile.metrics)[-1000:]
        metrics_summary = {}
        for metric_type in MetricType:
            type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            if type_metrics:
                metrics_summary[metric_type.value] = {
                    'current': type_metrics[-1].value,
                    'average': sum(m.value for m in type_metrics) / len(type_metrics),
                    'trend': 'up' if len(type_metrics) >= 2 and type_metrics[-1].value > type_metrics[-2].value else 'down'
                }
        
        return {
            'total_alerts': len(recent_alerts),
            'alert_severity_distribution': dict(severity_counts),
            'metrics_summary': metrics_summary,
            'system_health': profile.system_status['overall_health'],
            'active_threats': profile.system_status['active_threats']
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'total_dashboards': self.active_dashboards,
            'total_metrics': self.total_metrics,
            'total_alerts': self.total_alerts,
            'active_widgets': len(self.widgets),
            'dashboard_config': self.dashboard_config,
            'metric_thresholds': {k.value: v for k, v in self.metric_thresholds.items()}
        }

# Test the security monitoring dashboard
def test_security_monitoring_dashboard():
    """Test the security monitoring dashboard"""
    print("📊 Testing Security Monitoring Dashboard")
    print("=" * 50)
    
    dashboard = SecurityMonitoringDashboard()
    
    # Create test dashboard
    print("\n🖥️ Creating Test Dashboard...")
    
    dashboard_id = "main_security_dashboard"
    profile = dashboard.create_profile(dashboard_id)
    
    # Simulate security metrics
    print("\n📈 Simulating Security Metrics...")
    
    # Detection rate metrics
    for i in range(100):
        timestamp = datetime.now() - timedelta(minutes=i*5)
        
        # Simulate detection rate with some variation
        base_rate = 0.95
        variation = random.uniform(-0.1, 0.1)
        detection_rate = max(0.0, min(1.0, base_rate + variation))
        
        metric = SecurityMetric(
            metric_id=f"detection_rate_{i}",
            metric_type=MetricType.DETECTION_RATE,
            value=detection_rate,
            timestamp=timestamp,
            threshold=0.8,
            status='good' if detection_rate >= 0.8 else 'warning',
            metadata={'source': 'behavioral_analysis', 'systems': ['gaming', 'cybersecurity']}
        )
        
        alerts = dashboard.add_metric(dashboard_id, metric)
        
        if i % 20 == 0 and alerts:
            print(f"   Metric {i}: {len(alerts)} alerts generated")
    
    # Threat level metrics
    for i in range(50):
        timestamp = datetime.now() - timedelta(minutes=i*10)
        
        # Simulate threat level with occasional spikes
        base_threat = 0.3
        if i % 10 == 0:  # Occasional threat spikes
            base_threat = random.uniform(0.7, 0.9)
        
        threat_level = base_threat + random.uniform(-0.1, 0.1)
        threat_level = max(0.0, min(1.0, threat_level))
        
        metric = SecurityMetric(
            metric_id=f"threat_level_{i}",
            metric_type=MetricType.THREAT_LEVEL,
            value=threat_level,
            timestamp=timestamp,
            threshold=0.7,
            status='critical' if threat_level >= 0.9 else 'warning' if threat_level >= 0.7 else 'good',
            metadata={'source': 'threat_intelligence', 'systems': ['all']}
        )
        
        alerts = dashboard.add_metric(dashboard_id, metric)
        
        if alerts:
            print(f"   Threat Level {i}: {len(alerts)} alerts generated")
    
    # System health metrics
    for i in range(30):
        timestamp = datetime.now() - timedelta(minutes=i*15)
        
        # Simulate system health with occasional degradation
        base_health = 0.95
        if i % 8 == 0:  # Occasional health issues
            base_health = random.uniform(0.6, 0.8)
        
        system_health = base_health + random.uniform(-0.05, 0.05)
        system_health = max(0.0, min(1.0, system_health))
        
        metric = SecurityMetric(
            metric_id=f"system_health_{i}",
            metric_type=MetricType.SYSTEM_HEALTH,
            value=system_health,
            timestamp=timestamp,
            threshold=0.8,
            status='good' if system_health >= 0.8 else 'warning' if system_health >= 0.6 else 'critical',
            metadata={'source': 'system_monitoring', 'systems': ['infrastructure']}
        )
        
        alerts = dashboard.add_metric(dashboard_id, metric)
        
        if alerts:
            print(f"   System Health {i}: {len(alerts)} alerts generated")
    
    # Network traffic metrics
    for i in range(40):
        timestamp = datetime.now() - timedelta(minutes=i*3)
        
        # Simulate network traffic with peaks
        base_traffic = 500
        if i % 5 == 0:  # Traffic spikes
            base_traffic = random.uniform(2000, 4000)
        
        network_traffic = base_traffic + random.uniform(-100, 100)
        
        metric = SecurityMetric(
            metric_id=f"network_traffic_{i}",
            metric_type=MetricType.NETWORK_TRAFFIC,
            value=network_traffic,
            timestamp=timestamp,
            threshold=1000,
            status='good' if network_traffic <= 1000 else 'warning' if network_traffic <= 5000 else 'critical',
            metadata={'source': 'network_monitoring', 'systems': ['network']}
        )
        
        alerts = dashboard.add_metric(dashboard_id, metric)
        
        if i % 10 == 0 and alerts:
            print(f"   Network Traffic {i}: {len(alerts)} alerts generated")
    
    # Simulate some manual alerts
    print("\n🚨 Simulating Security Alerts...")
    
    alert_types = [
        {
            'severity': AlertSeverity.CRITICAL,
            'title': 'Critical Security Breach Detected',
            'description': 'Unauthorized access attempt detected in production environment',
            'source': 'intrusion_detection',
            'systems': ['production', 'database']
        },
        {
            'severity': AlertSeverity.WARNING,
            'title': 'Unusual Login Pattern',
            'description': 'Multiple failed login attempts from unusual location',
            'source': 'authentication',
            'systems': ['auth_service']
        },
        {
            'severity': AlertSeverity.ERROR,
            'title': 'System Performance Degradation',
            'description': 'Response times exceeding acceptable thresholds',
            'source': 'performance_monitoring',
            'systems': ['api_gateway', 'database']
        },
        {
            'severity': AlertSeverity.INFO,
            'title': 'Scheduled Security Update',
            'description': 'Security patches will be applied during maintenance window',
            'source': 'patch_management',
            'systems': ['all']
        }
    ]
    
    for i, alert_data in enumerate(alert_types):
        alert = SecurityAlert(
            alert_id=f"manual_alert_{i}",
            severity=alert_data['severity'],
            title=alert_data['title'],
            description=alert_data['description'],
            timestamp=datetime.now() - timedelta(hours=i*2),
            source=alert_data['source'],
            affected_systems=alert_data['systems'],
            metrics_impacted=[],
            resolution_status='open' if i < 2 else 'resolved',
            metadata={'priority': 'high' if i < 2 else 'medium'}
        )
        
        dashboard.add_alert(dashboard_id, alert)
        print(f"   Alert {i}: {alert.title}")
    
    # Generate dashboard report
    print("\n📋 Generating Dashboard Report...")
    
    dashboard_data = dashboard.get_dashboard_data(dashboard_id)
    
    print("\n📄 DASHBOARD SUMMARY:")
    summary = dashboard_data['summary']
    print(f"   Total Alerts: {summary['total_alerts']}")
    print(f"   Alert Severity Distribution: {summary['alert_severity_distribution']}")
    print(f"   System Health: {summary['system_health']:.3f}")
    print(f"   Active Threats: {summary['active_threats']}")
    
    print("\n📊 PERFORMANCE METRICS:")
    performance = dashboard_data['performance_metrics']
    print(f"   Detection Rate: {performance['avg_detection_rate']:.2%}")
    print(f"   Response Time: {performance['avg_response_time']:.0f}ms")
    print(f"   False Positive Rate: {performance['false_positive_rate']:.2%}")
    print(f"   Uptime: {performance['uptime_percentage']:.1f}%")
    
    print("\n🎯 METRICS SUMMARY:")
    for metric_name, metric_data in summary['metrics_summary'].items():
        print(f"   {metric_name}:")
        print(f"     Current: {metric_data['current']:.3f}")
        print(f"     Average: {metric_data['average']:.3f}")
        print(f"     Trend: {metric_data['trend']}")
    
    print("\n🖥️ WIDGETS STATUS:")
    for widget_id, widget_data in dashboard_data['widgets'].items():
        widget = profile.widgets[widget_id]
        print(f"   {widget.title}: {widget_data['type']} widget - Active")
    
    print("\n📈 RECENT ALERTS:")
    recent_alerts = dashboard_data['recent_alerts'][:5]
    for alert in recent_alerts:
        if isinstance(alert, SecurityAlert):
            print(f"   [{alert.severity.value.upper()}] {alert.title}")
            print(f"     {alert.description}")
            print(f"     Source: {alert.source}, Status: {alert.resolution_status}")
        else:
            print(f"   [{alert['severity'].upper()}] {alert['title']}")
            print(f"     {alert['description']}")
            print(f"     Source: {alert['source']}, Status: {alert['status']}")
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = dashboard.get_system_performance()
    print(f"   Total Dashboards: {performance['total_dashboards']}")
    print(f"   Total Metrics: {performance['total_metrics']}")
    print(f"   Total Alerts: {performance['total_alerts']}")
    print(f"   Active Widgets: {performance['active_widgets']}")
    print(f"   Refresh Interval: {performance['dashboard_config']['refresh_interval']}s")
    
    return dashboard

if __name__ == "__main__":
    test_security_monitoring_dashboard()
