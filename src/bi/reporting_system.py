"""
Helm AI Business Intelligence Reporting System
Provides comprehensive BI reporting with dashboards, analytics, and insights
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from decimal import Decimal

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class ReportType(Enum):
    """Report type enumeration"""
    DASHBOARD = "dashboard"
    ANALYTICS = "analytics"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class VisualizationType(Enum):
    """Visualization type enumeration"""
    TABLE = "table"
    CHART = "chart"
    GRAPH = "graph"
    GAUGE = "gauge"
    MAP = "map"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SCATTER = "scatter"
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    AREA = "area"

class DataSourceType(Enum):
    """Data source type enumeration"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CACHE = "cache"
    EXTERNAL = "external"

class ScheduleType(Enum):
    """Schedule type enumeration"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"

@dataclass
class DataSource:
    """Data source definition"""
    source_id: str
    name: str
    description: str
    source_type: DataSourceType
    connection_config: Dict[str, Any]
    credentials_encrypted: str
    schema: Dict[str, Any]
    is_active: bool
    last_refresh: Optional[datetime]
    refresh_interval: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert data source to dictionary"""
        return {
            'source_id': self.source_id,
            'name': self.name,
            'description': self.description,
            'source_type': self.source_type.value,
            'connection_config': self.connection_config,
            'credentials_encrypted': self.credentials_encrypted,
            'schema': self.schema,
            'is_active': self.is_active,
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'refresh_interval': self.refresh_interval,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class Report:
    """Report definition"""
    report_id: str
    name: str
    description: str
    report_type: ReportType
    owner_id: str
    tenant_id: str
    data_sources: List[str]
    visualizations: List[Dict[str, Any]]
    filters: Dict[str, Any]
    parameters: Dict[str, Any]
    schedule: Optional[Dict[str, Any]]
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime]
    run_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'report_id': self.report_id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type.value,
            'owner_id': self.owner_id,
            'tenant_id': self.tenant_id,
            'data_sources': self.data_sources,
            'visualizations': self.visualizations,
            'filters': self.filters,
            'parameters': self.parameters,
            'schedule': self.schedule,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count,
            'metadata': self.metadata
        }

@dataclass
class Dashboard:
    """Dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    owner_id: str
    tenant_id: str
    reports: List[str]
    layout: Dict[str, Any]
    theme: Dict[str, Any]
    filters: Dict[str, Any]
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_viewed: Optional[datetime]
    view_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard to dictionary"""
        return {
            'dashboard_id': self.dashboard_id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'tenant_id': self.tenant_id,
            'reports': self.reports,
            'layout': self.layout,
            'theme': self.theme,
            'filters': self.filters,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'view_count': self.view_count,
            'metadata': self.metadata
        }

@dataclass
class ReportExecution:
    """Report execution record"""
    execution_id: str
    report_id: str
    user_id: str
    tenant_id: str
    parameters: Dict[str, Any]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    results: Dict[str, Any]
    error_message: Optional[str]
    cache_hit: bool
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary"""
        return {
            'execution_id': self.execution_id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'parameters': self.parameters,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time': self.execution_time,
            'results': self.results,
            'error_message': self.error_message,
            'cache_hit': self.cache_hit,
            'metadata': self.metadata
        }

class BIReportingSystem:
    """Business Intelligence reporting system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.data_sources: Dict[str, DataSource] = {}
        self.reports: Dict[str, Report] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.executions: Dict[str, ReportExecution] = {}
        self.report_cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.cache_ttl = int(os.getenv('BI_CACHE_TTL', '300'))  # 5 minutes
        self.max_execution_time = int(os.getenv('BI_MAX_EXECUTION_TIME', '300'))  # 5 minutes
        self.max_cache_size = int(os.getenv('BI_MAX_CACHE_SIZE', '1000'))
        
        # Initialize default data sources
        self._initialize_default_data_sources()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_data_sources(self) -> None:
        """Initialize default data sources"""
        # Main Database Source
        main_db_source = DataSource(
            source_id="main_database",
            name="Main Database",
            description="Primary application database",
            source_type=DataSourceType.DATABASE,
            connection_config={
                "host": "localhost",
                "port": 5432,
                "database": "helm_ai",
                "ssl": True
            },
            credentials_encrypted=self.encryption_manager.encrypt("username:password"),
            schema={
                "tables": {
                    "users": {"columns": ["id", "name", "email", "created_at"]},
                    "subscriptions": {"columns": ["id", "user_id", "plan", "status", "created_at"]},
                    "events": {"columns": ["id", "user_id", "event_type", "timestamp", "data"]}
                }
            },
            is_active=True,
            last_refresh=None,
            refresh_interval=3600,  # 1 hour
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Analytics Database Source
        analytics_db_source = DataSource(
            source_id="analytics_database",
            name="Analytics Database",
            description="Analytics and reporting database",
            source_type=DataSourceType.DATABASE,
            connection_config={
                "host": "analytics.helm-ai.com",
                "port": 5432,
                "database": "analytics",
                "ssl": True
            },
            credentials_encrypted=self.encryption_manager.encrypt("analytics_user:analytics_pass"),
            schema={
                "tables": {
                    "user_metrics": {"columns": ["user_id", "metric_name", "value", "date"]},
                    "revenue": {"columns": ["date", "amount", "currency", "source"]},
                    "usage_stats": {"columns": ["date", "active_users", "api_calls", "storage_gb"]}
                }
            },
            is_active=True,
            last_refresh=None,
            refresh_interval=1800,  # 30 minutes
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # API Data Source
        api_source = DataSource(
            source_id="external_api",
            name="External API",
            description="External API data source",
            source_type=DataSourceType.API,
            connection_config={
                "base_url": "https://api.external.com/v1",
                "timeout": 30,
                "retry_count": 3
            },
            credentials_encrypted=self.encryption_manager.encrypt("api_key:secret"),
            schema={
                "endpoints": {
                    "/users": {"fields": ["id", "name", "email", "status"]},
                    "/analytics": {"fields": ["metric", "value", "timestamp"]}
                }
            },
            is_active=True,
            last_refresh=None,
            refresh_interval=900,  # 15 minutes
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Add data sources
        self.data_sources[main_db_source.source_id] = main_db_source
        self.data_sources[analytics_db_source.source_id] = analytics_db_source
        self.data_sources[api_source.source_id] = api_source
        
        logger.info(f"Initialized {len(self.data_sources)} default data sources")
    
    def create_data_source(self, name: str, description: str, source_type: DataSourceType,
                          connection_config: Dict[str, Any], credentials: str,
                          schema: Dict[str, Any], refresh_interval: int = 3600) -> DataSource:
        """Create new data source"""
        source_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        data_source = DataSource(
            source_id=source_id,
            name=name,
            description=description,
            source_type=source_type,
            connection_config=connection_config,
            credentials_encrypted=self.encryption_manager.encrypt(credentials),
            schema=schema,
            is_active=True,
            last_refresh=None,
            refresh_interval=refresh_interval,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        
        with self.lock:
            self.data_sources[source_id] = data_source
        
        logger.info(f"Created data source {source_id} ({name})")
        
        return data_source
    
    def create_report(self, name: str, description: str, report_type: ReportType,
                     owner_id: str, tenant_id: str, data_sources: List[str],
                     visualizations: List[Dict[str, Any]], filters: Dict[str, Any],
                     parameters: Dict[str, Any], schedule: Optional[Dict[str, Any]] = None,
                     is_public: bool = False) -> Report:
        """Create new report"""
        # Validate data sources
        for source_id in data_sources:
            if source_id not in self.data_sources:
                raise ValueError(f"Data source {source_id} not found")
        
        report_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        report = Report(
            report_id=report_id,
            name=name,
            description=description,
            report_type=report_type,
            owner_id=owner_id,
            tenant_id=tenant_id,
            data_sources=data_sources,
            visualizations=visualizations,
            filters=filters,
            parameters=parameters,
            schedule=schedule,
            is_public=is_public,
            is_active=True,
            created_at=now,
            updated_at=now,
            last_run=None,
            run_count=0,
            metadata={}
        )
        
        with self.lock:
            self.reports[report_id] = report
        
        logger.info(f"Created report {report_id} ({name})")
        
        return report
    
    def create_dashboard(self, name: str, description: str, owner_id: str, tenant_id: str,
                       reports: List[str], layout: Dict[str, Any], theme: Dict[str, Any],
                       filters: Dict[str, Any], is_public: bool = False) -> Dashboard:
        """Create new dashboard"""
        # Validate reports
        for report_id in reports:
            if report_id not in self.reports:
                raise ValueError(f"Report {report_id} not found")
        
        dashboard_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            owner_id=owner_id,
            tenant_id=tenant_id,
            reports=reports,
            layout=layout,
            theme=theme,
            filters=filters,
            is_public=is_public,
            is_active=True,
            created_at=now,
            updated_at=now,
            last_viewed=None,
            view_count=0,
            metadata={}
        )
        
        with self.lock:
            self.dashboards[dashboard_id] = dashboard
        
        logger.info(f"Created dashboard {dashboard_id} ({name})")
        
        return dashboard
    
    def execute_report(self, report_id: str, user_id: str, tenant_id: str,
                      parameters: Optional[Dict[str, Any]] = None) -> ReportExecution:
        """Execute report"""
        with self.lock:
            if report_id not in self.reports:
                raise ValueError(f"Report {report_id} not found")
            
            report = self.reports[report_id]
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Merge parameters
        exec_params = report.parameters.copy()
        if parameters:
            exec_params.update(parameters)
        
        # Check cache
        cache_key = f"{report_id}:{hash(json.dumps(exec_params, sort_keys=True))}"
        cache_result = self._get_from_cache(cache_key)
        
        if cache_result:
            execution = ReportExecution(
                execution_id=execution_id,
                report_id=report_id,
                user_id=user_id,
                tenant_id=tenant_id,
                parameters=exec_params,
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                execution_time=0.1,
                results=cache_result,
                error_message=None,
                cache_hit=True,
                metadata={}
            )
            
            with self.lock:
                self.executions[execution_id] = execution
            
            return execution
        
        # Execute report
        execution = ReportExecution(
            execution_id=execution_id,
            report_id=report_id,
            user_id=user_id,
            tenant_id=tenant_id,
            parameters=exec_params,
            status="running",
            started_at=datetime.utcnow(),
            completed_at=None,
            execution_time=None,
            results={},
            error_message=None,
            cache_hit=False,
            metadata={}
        )
        
        with self.lock:
            self.executions[execution_id] = execution
        
        try:
            # Simulate report execution
            results = self._execute_report_logic(report, exec_params)
            
            execution_time = time.time() - start_time
            
            # Update execution
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.execution_time = execution_time
            execution.results = results
            
            # Cache results
            self._add_to_cache(cache_key, results)
            
            # Update report metrics
            with self.lock:
                report.last_run = datetime.utcnow()
                report.run_count += 1
                report.updated_at = datetime.utcnow()
            
            logger.info(f"Executed report {report_id} in {execution_time:.2f}s")
            
            return execution
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.execution_time = time.time() - start_time
            execution.error_message = str(e)
            
            logger.error(f"Failed to execute report {report_id}: {e}")
            
            return execution
    
    def _execute_report_logic(self, report: Report, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report logic (simulated)"""
        results = {
            'report_id': report.report_id,
            'report_name': report.name,
            'generated_at': datetime.utcnow().isoformat(),
            'parameters': parameters,
            'visualizations': []
        }
        
        # Generate data for each visualization
        for viz in report.visualizations:
            viz_type = viz.get('type', 'table')
            viz_id = viz.get('id', f'viz_{len(results["visualizations"])}')
            
            if viz_type == VisualizationType.TABLE.value:
                viz_data = self._generate_table_data(viz, parameters)
            elif viz_type == VisualizationType.CHART.value:
                viz_data = self._generate_chart_data(viz, parameters)
            elif viz_type == VisualizationType.GAUGE.value:
                viz_data = self._generate_gauge_data(viz, parameters)
            elif viz_type == VisualizationType.PIE.value:
                viz_data = self._generate_pie_data(viz, parameters)
            else:
                viz_data = self._generate_default_data(viz, parameters)
            
            results['visualizations'].append({
                'id': viz_id,
                'type': viz_type,
                'title': viz.get('title', 'Visualization'),
                'data': viz_data,
                'config': viz.get('config', {})
            })
        
        return results
    
    def _generate_table_data(self, viz: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate table data"""
        return {
            'columns': ['ID', 'Name', 'Value', 'Date'],
            'rows': [
                {'ID': 1, 'Name': 'Item 1', 'Value': 100, 'Date': '2024-01-01'},
                {'ID': 2, 'Name': 'Item 2', 'Value': 200, 'Date': '2024-01-02'},
                {'ID': 3, 'Name': 'Item 3', 'Value': 150, 'Date': '2024-01-03'}
            ],
            'total_rows': 3
        }
    
    def _generate_chart_data(self, viz: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data"""
        return {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': [1000, 1200, 1100, 1300, 1500, 1400],
                    'backgroundColor': '#007bff',
                    'borderColor': '#007bff'
                },
                {
                    'label': 'Costs',
                    'data': [800, 900, 850, 950, 1000, 950],
                    'backgroundColor': '#dc3545',
                    'borderColor': '#dc3545'
                }
            ]
        }
    
    def _generate_gauge_data(self, viz: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate gauge data"""
        return {
            'value': 75,
            'min': 0,
            'max': 100,
            'thresholds': [
                {'value': 50, 'color': '#28a745'},
                {'value': 80, 'color': '#ffc107'},
                {'value': 100, 'color': '#dc3545'}
            ],
            'unit': '%'
        }
    
    def _generate_pie_data(self, viz: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pie chart data"""
        return {
            'labels': ['Product A', 'Product B', 'Product C', 'Product D'],
            'datasets': [{
                'data': [30, 25, 20, 25],
                'backgroundColor': ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }]
        }
    
    def _generate_default_data(self, viz: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default visualization data"""
        return {
            'message': 'Default visualization data',
            'config': viz.get('config', {})
        }
    
    def get_dashboard_data(self, dashboard_id: str, user_id: str, tenant_id: str,
                          filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get dashboard data"""
        with self.lock:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
        
        # Update view count
        dashboard.last_viewed = datetime.utcnow()
        dashboard.view_count += 1
        dashboard.updated_at = datetime.utcnow()
        
        # Execute all reports in dashboard
        dashboard_data = {
            'dashboard_id': dashboard_id,
            'dashboard_name': dashboard.name,
            'layout': dashboard.layout,
            'theme': dashboard.theme,
            'reports': []
        }
        
        for report_id in dashboard.reports:
            try:
                execution = self.execute_report(report_id, user_id, tenant_id, filters)
                dashboard_data['reports'].append({
                    'report_id': report_id,
                    'execution': execution.to_dict()
                })
            except Exception as e:
                logger.error(f"Failed to execute report {report_id} for dashboard {dashboard_id}: {e}")
                dashboard_data['reports'].append({
                    'report_id': report_id,
                    'error': str(e)
                })
        
        return dashboard_data
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache"""
        with self.lock:
            if cache_key in self.report_cache:
                cached_item = self.report_cache[cache_key]
                
                # Check TTL
                if datetime.utcnow() - cached_item['timestamp'] < timedelta(seconds=self.cache_ttl):
                    return cached_item['data']
                else:
                    # Remove expired cache item
                    del self.report_cache[cache_key]
        
        return None
    
    def _add_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Add data to cache"""
        with self.lock:
            # Check cache size limit
            if len(self.report_cache) >= self.max_cache_size:
                # Remove oldest item
                oldest_key = min(self.report_cache.keys(), 
                               key=lambda k: self.report_cache[k]['timestamp'])
                del self.report_cache[oldest_key]
            
            self.report_cache[cache_key] = {
                'data': data,
                'timestamp': datetime.utcnow()
            }
    
    def get_bi_metrics(self) -> Dict[str, Any]:
        """Get BI system metrics"""
        with self.lock:
            total_data_sources = len(self.data_sources)
            active_data_sources = len([ds for ds in self.data_sources.values() if ds.is_active])
            
            total_reports = len(self.reports)
            active_reports = len([r for r in self.reports.values() if r.is_active])
            public_reports = len([r for r in self.reports.values() if r.is_public])
            
            total_dashboards = len(self.dashboards)
            active_dashboards = len([d for d in self.dashboards.values() if d.is_active])
            public_dashboards = len([d for d in self.dashboards.values() if d.is_public])
            
            # Execution metrics
            total_executions = len(self.executions)
            successful_executions = len([e for e in self.executions.values() if e.status == 'completed'])
            failed_executions = len([e for e in self.executions.values() if e.status == 'failed'])
            
            # Cache metrics
            cache_size = len(self.report_cache)
            cache_hit_rate = 0.0
            if total_executions > 0:
                cache_hits = len([e for e in self.executions.values() if e.cache_hit])
                cache_hit_rate = (cache_hits / total_executions) * 100
            
            # Report type distribution
            report_type_distribution = defaultdict(int)
            for report in self.reports.values():
                report_type_distribution[report.report_type.value] += 1
            
            return {
                'data_sources': {
                    'total': total_data_sources,
                    'active': active_data_sources,
                    'inactive': total_data_sources - active_data_sources
                },
                'reports': {
                    'total': total_reports,
                    'active': active_reports,
                    'public': public_reports,
                    'private': total_reports - public_reports,
                    'type_distribution': dict(report_type_distribution)
                },
                'dashboards': {
                    'total': total_dashboards,
                    'active': active_dashboards,
                    'public': public_dashboards,
                    'private': total_dashboards - public_dashboards
                },
                'executions': {
                    'total': total_executions,
                    'successful': successful_executions,
                    'failed': failed_executions,
                    'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0
                },
                'cache': {
                    'size': cache_size,
                    'max_size': self.max_cache_size,
                    'hit_rate': round(cache_hit_rate, 2),
                    'ttl_seconds': self.cache_ttl
                }
            }
    
    def _start_background_tasks(self) -> None:
        """Start background BI tasks"""
        # Start data source refresh thread
        refresh_thread = threading.Thread(target=self._refresh_data_sources, daemon=True)
        refresh_thread.start()
        
        # Start cache cleanup thread
        cache_thread = threading.Thread(target=self._cleanup_cache, daemon=True)
        cache_thread.start()
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _refresh_data_sources(self) -> None:
        """Refresh data sources"""
        while True:
            try:
                now = datetime.utcnow()
                
                with self.lock:
                    for source in self.data_sources.values():
                        if source.is_active:
                            # Check if refresh is needed
                            if (source.last_refresh is None or 
                                (now - source.last_refresh).total_seconds() >= source.refresh_interval):
                                
                                # Simulate data refresh
                                source.last_refresh = now
                                source.updated_at = now
                                
                                logger.info(f"Refreshed data source {source.source_id}")
                
                # Check every minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Data source refresh failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache items"""
        while True:
            try:
                # Run cleanup every 5 minutes
                time.sleep(300)  # 5 minutes
                
                now = datetime.utcnow()
                expired_keys = []
                
                with self.lock:
                    for cache_key, cached_item in self.report_cache.items():
                        if now - cached_item['timestamp'] > timedelta(seconds=self.cache_ttl):
                            expired_keys.append(cache_key)
                    
                    for key in expired_keys:
                        del self.report_cache[key]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
                
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _collect_metrics(self) -> None:
        """Collect BI metrics"""
        while True:
            try:
                # Collect metrics every hour
                time.sleep(3600)  # 1 hour
                
                metrics = self.get_bi_metrics()
                logger.info(f"BI metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(1800)  # Wait 30 minutes before retrying

# Global BI reporting system instance
bi_reporting_system = BIReportingSystem()

# Export main components
__all__ = [
    'BIReportingSystem',
    'DataSource',
    'Report',
    'Dashboard',
    'ReportExecution',
    'ReportType',
    'VisualizationType',
    'DataSourceType',
    'ScheduleType',
    'bi_reporting_system'
]
