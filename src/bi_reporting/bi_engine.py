"""
Business Intelligence Reporting System for Helm AI
==================================================

This module provides comprehensive business intelligence and reporting capabilities:
- Interactive dashboard with real-time metrics
- Custom report generation and scheduling
- Data visualization and charting
- Executive summary reports
- Financial analytics and forecasting
- Performance benchmarking
- Automated report distribution
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import io
import base64

# Third-party imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import redis
from jinja2 import Template
import weasyprint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import schedule
import time

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager
from src.analytics.dashboard import AnalyticsEngine
from src.billing.subscription_manager import SubscriptionManager

logger = StructuredLogger("bi_reporting")

Base = declarative_base()


class ReportType(str, Enum):
    """Types of BI reports"""
    DASHBOARD = "dashboard"
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    USAGE = "usage"
    CUSTOM = "custom"


class ChartType(str, Enum):
    """Types of charts and visualizations"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    KPI = "kpi"


class ExportFormat(str, Enum):
    """Export formats for reports"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


@dataclass
class ReportMetric:
    """Report metric definition"""
    id: str
    name: str
    description: str
    query: str
    chart_type: ChartType
    target_value: Optional[float] = None
    unit: str = ""
    format: str = "{:.2f}"
    color_scheme: List[str] = field(default_factory=lambda: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])


@dataclass
class ReportFilter:
    """Report filter definition"""
    id: str
    name: str
    field: str
    type: str  # date, select, multiselect, text, number
    options: List[Any] = field(default_factory=list)
    default_value: Any = None
    required: bool = False


@dataclass
class ReportSchedule:
    """Report scheduling configuration"""
    id: str
    name: str
    frequency: str  # daily, weekly, monthly, quarterly
    recipients: List[str]
    format: ExportFormat
    enabled: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None


@dataclass
class BIReport:
    """Business Intelligence Report"""
    id: str
    name: str
    description: str
    type: ReportType
    metrics: List[ReportMetric]
    filters: List[ReportFilter] = field(default_factory=list)
    schedules: List[ReportSchedule] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_public: bool = False
    tags: Set[str] = field(default_factory=set)


class BIReportMetadata(Base):
    """SQLAlchemy model for BI report metadata"""
    __tablename__ = "bi_report_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    tags = Column(JSONB)
    config = Column(JSONB)


class ReportExecution(Base):
    """SQLAlchemy model for report execution history"""
    __tablename__ = "report_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(255), nullable=False, index=True)
    executed_by = Column(String(255))
    executed_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(JSONB)
    status = Column(String(50), default="pending")
    duration_seconds = Column(Integer)
    file_path = Column(String(1000))
    file_size = Column(Integer)
    error_message = Column(Text)


class BIReportingEngine:
    """Business Intelligence Reporting Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        self.analytics_engine = AnalyticsEngine(config.get('analytics', {}))
        self.subscription_manager = SubscriptionManager(config.get('billing', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Email configuration
        self.email_config = config.get('email', {})
        
        # Report storage
        self.reports: Dict[str, BIReport] = {}
        
        # Template engine
        self.template_env = self._initialize_templates()
        
        logger.info("BI Reporting Engine initialized")
    
    def _initialize_templates(self):
        """Initialize Jinja2 templates"""
        import jinja2
        
        template_loader = jinja2.FileSystemLoader(
            searchpath=[Path(__file__).parent / "templates"]
        )
        template_env = jinja2.Environment(loader=template_loader)
        
        # Add custom filters
        template_env.filters['currency'] = self._format_currency
        template_env.filters['percentage'] = self._format_percentage
        template_env.filters['number'] = self._format_number
        
        return template_env
    
    def _format_currency(self, value, currency='USD'):
        """Format currency values"""
        if value is None:
            return '$0.00'
        return f'{currency}{value:,.2f}'
    
    def _format_percentage(self, value, decimals=1):
        """Format percentage values"""
        if value is None:
            return '0%'
        return f'{value:.{decimals}f}%'
    
    def _format_number(self, value, decimals=0):
        """Format numbers with thousands separators"""
        if value is None:
            return '0'
        return f'{value:,.{decimals}f}'
    
    async def create_report(self, report: BIReport) -> bool:
        """Create a new BI report"""
        try:
            # Validate report configuration
            if not await self._validate_report(report):
                logger.error("Report validation failed", report_id=report.id)
                return False
            
            # Store report
            self.reports[report.id] = report
            
            # Save metadata to database
            metadata = BIReportMetadata(
                report_id=report.id,
                name=report.name,
                type=report.type.value,
                created_by=report.created_by,
                is_public=report.is_public,
                tags=list(report.tags),
                config={
                    "metrics": [
                        {
                            "id": m.id,
                            "name": m.name,
                            "query": m.query,
                            "chart_type": m.chart_type.value,
                            "target_value": m.target_value,
                            "unit": m.unit,
                            "format": m.format,
                            "color_scheme": m.color_scheme
                        } for m in report.metrics
                    ],
                    "filters": [
                        {
                            "id": f.id,
                            "name": f.name,
                            "field": f.field,
                            "type": f.type,
                            "options": f.options,
                            "default_value": f.default_value,
                            "required": f.required
                        } for f in report.filters
                    ]
                }
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(metadata)
                session.commit()
            finally:
                session.close()
            
            logger.info("BI report created successfully", 
                       report_id=report.id, report_type=report.type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create BI report", 
                        report_id=report.id, error=str(e))
            return False
    
    async def _validate_report(self, report: BIReport) -> bool:
        """Validate report configuration"""
        try:
            # Validate metrics
            for metric in report.metrics:
                # Test query execution
                test_data = await self.data_lake.query_data(metric.query)
                if test_data.empty:
                    logger.warning("Metric query returned no data", 
                                 metric_id=metric.id, report_id=report.id)
            
            # Validate filters
            for filter_def in report.filters:
                if filter_def.type == "select" and not filter_def.options:
                    logger.error("Select filter requires options", 
                                filter_id=filter_def.id, report_id=report.id)
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Report validation failed", 
                        report_id=report.id, error=str(e))
            return False
    
    async def generate_report(self, report_id: str, parameters: Optional[Dict[str, Any]] = None,
                            export_format: ExportFormat = ExportFormat.HTML) -> Dict[str, Any]:
        """Generate a BI report"""
        if report_id not in self.reports:
            raise ValueError(f"Report {report_id} not found")
        
        report = self.reports[report_id]
        parameters = parameters or {}
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution = ReportExecution(
            report_id=report_id,
            executed_by=parameters.get('user_id', 'system'),
            parameters=parameters,
            status="running"
        )
        
        session = self.db_manager.get_session()
        try:
            session.add(execution)
            session.commit()
        finally:
            session.close()
        
        start_time = datetime.utcnow()
        
        try:
            logger.info("Generating BI report", 
                       report_id=report_id, execution_id=execution_id)
            
            # Generate report data
            report_data = await self._generate_report_data(report, parameters)
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(report, report_data)
            
            # Create report content
            if export_format == ExportFormat.HTML:
                content = await self._generate_html_report(report, report_data, visualizations)
            elif export_format == ExportFormat.PDF:
                content = await self._generate_pdf_report(report, report_data, visualizations)
            elif export_format == ExportFormat.EXCEL:
                content = await self._generate_excel_report(report, report_data)
            elif export_format == ExportFormat.CSV:
                content = await self._generate_csv_report(report, report_data)
            elif export_format == ExportFormat.JSON:
                content = await self._generate_json_report(report, report_data, visualizations)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            # Save report file
            file_path = await self._save_report_file(report_id, execution_id, content, export_format)
            
            # Update execution record
            duration = (datetime.utcnow() - start_time).total_seconds()
            session = self.db_manager.get_session()
            try:
                execution.status = "completed"
                execution.duration_seconds = int(duration)
                execution.file_path = file_path
                execution.file_size = len(content) if isinstance(content, bytes) else len(content.encode())
                session.commit()
            finally:
                session.close()
            
            logger.info("BI report generated successfully", 
                       report_id=report_id, execution_id=execution_id, 
                       duration=duration, format=export_format.value)
            
            return {
                "execution_id": execution_id,
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "format": export_format.value,
                "duration": duration,
                "metrics_count": len(report_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Update execution record with error
            session = self.db_manager.get_session()
            try:
                execution.status = "failed"
                execution.duration_seconds = int((datetime.utcnow() - start_time).total_seconds())
                execution.error_message = str(e)
                session.commit()
            finally:
                session.close()
            
            logger.error("BI report generation failed", 
                        report_id=report_id, execution_id=execution_id, error=str(e))
            raise
    
    async def _generate_report_data(self, report: BIReport, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for all report metrics"""
        report_data = {}
        
        for metric in report.metrics:
            try:
                # Apply filters to query
                query = self._apply_filters_to_query(metric.query, report.filters, parameters)
                
                # Execute query
                data = await self.data_lake.query_data(query)
                
                # Calculate additional metrics
                if metric.target_value:
                    current_value = self._extract_metric_value(data, metric)
                    achievement_rate = (current_value / metric.target_value) * 100 if metric.target_value else 0
                    data['achievement_rate'] = achievement_rate
                    data['target_value'] = metric.target_value
                
                report_data[metric.id] = {
                    "data": data,
                    "metric": metric,
                    "current_value": self._extract_metric_value(data, metric),
                    "trend": self._calculate_trend(data, metric)
                }
                
            except Exception as e:
                logger.error("Failed to generate metric data", 
                            metric_id=metric.id, report_id=report.id, error=str(e))
                report_data[metric.id] = {
                    "data": pd.DataFrame(),
                    "metric": metric,
                    "error": str(e)
                }
        
        return report_data
    
    def _apply_filters_to_query(self, query: str, filters: List[ReportFilter], 
                               parameters: Dict[str, Any]) -> str:
        """Apply filter parameters to SQL query"""
        filtered_query = query
        
        for filter_def in filters:
            filter_value = parameters.get(filter_def.id, filter_def.default_value)
            if filter_value is not None:
                if filter_def.type == "date":
                    if isinstance(filter_value, dict):
                        if "start" in filter_value:
                            filtered_query += f" AND {filter_def.field} >= '{filter_value['start']}'"
                        if "end" in filter_value:
                            filtered_query += f" AND {filter_def.field} <= '{filter_value['end']}'"
                    else:
                        filtered_query += f" AND {filter_def.field} = '{filter_value}'"
                
                elif filter_def.type == "select":
                    filtered_query += f" AND {filter_def.field} = '{filter_value}'"
                
                elif filter_def.type == "multiselect":
                    if isinstance(filter_value, list):
                        values = "', '".join(filter_value)
                        filtered_query += f" AND {filter_def.field} IN ('{values}')"
                
                elif filter_def.type == "text":
                    filtered_query += f" AND {filter_def.field} ILIKE '%{filter_value}%'"
                
                elif filter_def.type == "number":
                    if isinstance(filter_value, dict):
                        if "min" in filter_value:
                            filtered_query += f" AND {filter_def.field} >= {filter_value['min']}"
                        if "max" in filter_value:
                            filtered_query += f" AND {filter_def.field} <= {filter_value['max']}"
                    else:
                        filtered_query += f" AND {filter_def.field} = {filter_value}"
        
        return filtered_query
    
    def _extract_metric_value(self, data: pd.DataFrame, metric: ReportMetric) -> float:
        """Extract the primary value from metric data"""
        if data.empty:
            return 0.0
        
        try:
            # Try to get the most recent value
            if 'date' in data.columns or 'timestamp' in data.columns:
                date_col = 'date' if 'date' in data.columns else 'timestamp'
                data = data.sort_values(date_col, ascending=False)
            
            # Get the first numeric column value
            for col in data.columns:
                if data[col].dtype in ['int64', 'float64']:
                    return float(data[col].iloc[0])
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_trend(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Calculate trend direction"""
        try:
            if len(data) < 2:
                return "stable"
            
            # Get numeric column
            numeric_col = None
            for col in data.columns:
                if data[col].dtype in ['int64', 'float64']:
                    numeric_col = col
                    break
            
            if not numeric_col:
                return "stable"
            
            # Calculate trend
            values = data[numeric_col].values
            if len(values) >= 2:
                recent_avg = np.mean(values[-min(7, len(values)):])  # Last 7 values
                previous_avg = np.mean(values[-min(14, len(values)):-7]) if len(values) > 7 else np.mean(values[:-7])
                
                if recent_avg > previous_avg * 1.05:
                    return "up"
                elif recent_avg < previous_avg * 0.95:
                    return "down"
            
            return "stable"
            
        except Exception:
            return "stable"
    
    async def _generate_visualizations(self, report: BIReport, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate chart visualizations"""
        visualizations = {}
        
        for metric_id, metric_data in report_data.items():
            if "error" in metric_data:
                continue
            
            metric = metric_data["metric"]
            data = metric_data["data"]
            
            if data.empty:
                continue
            
            try:
                chart_html = self._create_chart(data, metric)
                visualizations[metric_id] = chart_html
                
            except Exception as e:
                logger.error("Failed to generate chart", 
                            metric_id=metric_id, error=str(e))
        
        return visualizations
    
    def _create_chart(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Create a chart based on metric type"""
        if metric.chart_type == ChartType.LINE:
            return self._create_line_chart(data, metric)
        elif metric.chart_type == ChartType.BAR:
            return self._create_bar_chart(data, metric)
        elif metric.chart_type == ChartType.PIE:
            return self._create_pie_chart(data, metric)
        elif metric.chart_type == ChartType.KPI:
            return self._create_kpi_card(data, metric)
        else:
            return self._create_line_chart(data, metric)
    
    def _create_line_chart(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Create line chart"""
        # Find date and value columns
        date_col = None
        value_col = None
        
        for col in data.columns:
            if col.lower() in ['date', 'timestamp', 'time']:
                date_col = col
            elif data[col].dtype in ['int64', 'float64']:
                value_col = col
        
        if not date_col or not value_col:
            return "<div>No data available for chart</div>"
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data[date_col],
            y=data[value_col],
            mode='lines+markers',
            name=metric.name,
            line=dict(color=metric.color_scheme[0] if metric.color_scheme else '#1f77b4')
        ))
        
        fig.update_layout(
            title=metric.name,
            xaxis_title=date_col,
            yaxis_title=value_col,
            template="plotly_white"
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=f"chart_{metric.id}")
    
    def _create_bar_chart(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Create bar chart"""
        # Find categorical and value columns
        cat_col = None
        value_col = None
        
        for col in data.columns:
            if data[col].dtype == 'object':
                cat_col = col
            elif data[col].dtype in ['int64', 'float64']:
                value_col = col
        
        if not cat_col or not value_col:
            return "<div>No data available for chart</div>"
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data[cat_col],
            y=data[value_col],
            name=metric.name,
            marker_color=metric.color_scheme[0] if metric.color_scheme else '#1f77b4'
        ))
        
        fig.update_layout(
            title=metric.name,
            xaxis_title=cat_col,
            yaxis_title=value_col,
            template="plotly_white"
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=f"chart_{metric.id}")
    
    def _create_pie_chart(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Create pie chart"""
        # Find categorical and value columns
        cat_col = None
        value_col = None
        
        for col in data.columns:
            if data[col].dtype == 'object':
                cat_col = col
            elif data[col].dtype in ['int64', 'float64']:
                value_col = col
        
        if not cat_col or not value_col:
            return "<div>No data available for chart</div>"
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=data[cat_col],
            values=data[value_col],
            name=metric.name
        ))
        
        fig.update_layout(title=metric.name, template="plotly_white")
        
        return fig.to_html(include_plotlyjs='cdn', div_id=f"chart_{metric.id}")
    
    def _create_kpi_card(self, data: pd.DataFrame, metric: ReportMetric) -> str:
        """Create KPI card"""
        value = self._extract_metric_value(data, metric)
        trend = self._calculate_trend(data, metric)
        
        trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
        trend_color = "green" if trend == "up" else "red" if trend == "down" else "gray"
        
        html = f"""
        <div class="kpi-card" style="
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            text-align: center;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h3 style="margin: 0 0 10px 0; color: #333;">{metric.name}</h3>
            <div style="font-size: 2em; font-weight: bold; color: #1f77b4;">
                {metric.format.format(value)}{metric.unit}
            </div>
            <div style="color: {trend_color}; font-size: 1.2em; margin-top: 10px;">
                {trend_icon} {trend.title()}
            </div>
            {f'<div style="color: #666; font-size: 0.9em; margin-top: 5px;">Target: {metric.format.format(metric.target_value)}{metric.unit}</div>' if metric.target_value else ''}
        </div>
        """
        
        return html
    
    async def _generate_html_report(self, report: BIReport, report_data: Dict[str, Any], 
                                   visualizations: Dict[str, str]) -> str:
        """Generate HTML report"""
        # Simple HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.name}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .metric {{ margin: 20px 0; }}
                .kpi-card {{ display: inline-block; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.name}</h1>
                <p>{report.description}</p>
                <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        for metric_id, metric_data in report_data.items():
            metric = metric_data["metric"]
            visualization = visualizations.get(metric_id, "")
            
            html += f"""
            <div class="metric">
                <h2>{metric.name}</h2>
                <p>{metric.description}</p>
                {visualization}
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def _generate_pdf_report(self, report: BIReport, report_data: Dict[str, Any], 
                                  visualizations: Dict[str, str]) -> bytes:
        """Generate PDF report"""
        # Generate HTML first
        html_content = await self._generate_html_report(report, report_data, visualizations)
        
        # Convert to PDF
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        return pdf_bytes
    
    async def _generate_excel_report(self, report: BIReport, report_data: Dict[str, Any]) -> bytes:
        """Generate Excel report"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Create summary sheet
            summary_data = []
            for metric_id, metric_data in report_data.items():
                metric = metric_data["metric"]
                current_value = metric_data.get("current_value", 0)
                trend = metric_data.get("trend", "stable")
                
                summary_data.append({
                    "Metric": metric.name,
                    "Current Value": current_value,
                    "Unit": metric.unit,
                    "Target": metric.target_value or "",
                    "Trend": trend,
                    "Status": "Error" if "error" in metric_data else "Success"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create data sheets for each metric
            for metric_id, metric_data in report_data.items():
                if "error" not in metric_data:
                    data = metric_data["data"]
                    metric = metric_data["metric"]
                    
                    # Clean sheet name
                    sheet_name = metric.name[:31]  # Excel limit
                    sheet_name = ''.join(c for c in sheet_name if c.isalnum() or c in (' ', '_', '-'))
                    
                    data.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return output.getvalue()
    
    async def _generate_csv_report(self, report: BIReport, report_data: Dict[str, Any]) -> str:
        """Generate CSV report"""
        # Combine all metric data
        combined_data = []
        
        for metric_id, metric_data in report_data.items():
            if "error" not in metric_data:
                data = metric_data["data"].copy()
                data['metric_name'] = metric_data["metric"].name
                data['metric_id'] = metric_id
                combined_data.append(data)
        
        if combined_data:
            result_df = pd.concat(combined_data, ignore_index=True)
            return result_df.to_csv(index=False)
        else:
            return "No data available"
    
    async def _generate_json_report(self, report: BIReport, report_data: Dict[str, Any], 
                                   visualizations: Dict[str, str]) -> str:
        """Generate JSON report"""
        json_data = {
            "report": {
                "id": report.id,
                "name": report.name,
                "description": report.description,
                "type": report.type.value,
                "generated_at": datetime.utcnow().isoformat()
            },
            "metrics": []
        }
        
        for metric_id, metric_data in report_data.items():
            metric_info = {
                "id": metric_id,
                "name": metric_data["metric"].name,
                "description": metric_data["metric"].description,
                "current_value": metric_data.get("current_value"),
                "trend": metric_data.get("trend"),
                "data": metric_data["data"].to_dict('records') if not metric_data["data"].empty else [],
                "visualization": visualizations.get(metric_id, ""),
                "error": metric_data.get("error")
            }
            json_data["metrics"].append(metric_info)
        
        return json.dumps(json_data, indent=2, default=str)
    
    async def _save_report_file(self, report_id: str, execution_id: str, 
                              content: Union[str, bytes], export_format: ExportFormat) -> str:
        """Save report file to storage"""
        # Create reports directory
        reports_dir = Path("reports") / report_id
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{execution_id}_{timestamp}.{export_format.value}"
        file_path = reports_dir / filename
        
        # Save file
        if isinstance(content, bytes):
            with open(file_path, 'wb') as f:
                f.write(content)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return str(file_path)
    
    def get_bi_metrics(self) -> Dict[str, Any]:
        """Get BI system metrics"""
        return {
            "total_reports": len(self.reports),
            "active_reports": len([r for r in self.reports.values() if any(s.enabled for s in r.schedules)]),
            "total_executions": self._get_execution_count(),
            "cache_hit_rate": self.redis_client.info().get('keyspace_hits', 0) / max(1, self.redis_client.info().get('keyspace_misses', 1)),
            "system_uptime": datetime.utcnow().isoformat()
        }
    
    def _get_execution_count(self) -> int:
        """Get total execution count"""
        session = self.db_manager.get_session()
        try:
            return session.query(ReportExecution).count()
        finally:
            session.close()


# Configuration
BI_CONFIG = {
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
    "email": {
        "smtp_host": os.getenv("SMTP_HOST"),
        "smtp_port": int(os.getenv("SMTP_PORT", 587)),
        "username": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("FROM_EMAIL", "noreply@helm-ai.com")
    }
}


# Initialize BI reporting engine
bi_reporting_engine = BIReportingEngine(BI_CONFIG)

# Export main components
__all__ = [
    'BIReportingEngine',
    'BIReport',
    'ReportMetric',
    'ReportFilter',
    'ReportSchedule',
    'ReportType',
    'ChartType',
    'ExportFormat',
    'bi_reporting_engine'
]
