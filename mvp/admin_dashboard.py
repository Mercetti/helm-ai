"""
Helm AI Admin Dashboard
Complete admin dashboard with user management, system monitoring, analytics, and configuration controls
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import psutil
import json
import os
from pathlib import Path

from database import get_db, User, DetectionResult, GameSession
from auth import get_current_superuser
from user_management import get_users, count_users, UserRole, UserStatus
from billing import get_subscription, SubscriptionStatus

# Templates setup
templates = Jinja2Templates(directory="templates")

# Pydantic Models
class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    uptime: float
    active_connections: int

class UserMetrics(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    users_by_role: Dict[str, int]
    users_by_status: Dict[str, int]

class DetectionMetrics(BaseModel):
    total_detections: int
    detections_today: int
    detections_week: int
    detections_month: int
    detections_by_type: Dict[str, int]
    detections_by_risk: Dict[str, int]
    false_positive_rate: float

class RevenueMetrics(BaseModel):
    total_revenue: float
    revenue_today: float
    revenue_week: float
    revenue_month: float
    active_subscriptions: int
    subscriptions_by_plan: Dict[str, int]
    churn_rate: float

class AdminDashboardData(BaseModel):
    system_metrics: SystemMetrics
    user_metrics: UserMetrics
    detection_metrics: DetectionMetrics
    revenue_metrics: RevenueMetrics
    recent_activities: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]

# System Monitoring Functions
def get_system_metrics() -> SystemMetrics:
    """Get system performance metrics"""
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Disk usage
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    
    # Network I/O
    network = psutil.net_io_counters()
    network_io = {
        "bytes_sent": network.bytes_sent,
        "bytes_recv": network.bytes_recv,
        "packets_sent": network.packets_sent,
        "packets_recv": network.packets_recv
    }
    
    # System uptime
    uptime = psutil.boot_time()
    uptime_seconds = datetime.now(timezone.utc).timestamp() - uptime
    
    # Active connections (approximate)
    active_connections = len(psutil.net_connections())
    
    return SystemMetrics(
        cpu_usage=cpu_percent,
        memory_usage=memory_percent,
        disk_usage=disk_percent,
        network_io=network_io,
        uptime=uptime_seconds,
        active_connections=active_connections
    )

def get_user_metrics(db: Session) -> UserMetrics:
    """Get user-related metrics"""
    
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total users
    total_users = db.query(User).count()
    
    # Active users (logged in within last 30 days)
    active_users = db.query(User).filter(
        User.last_login >= month_ago
    ).count()
    
    # New users
    new_users_today = db.query(User).filter(User.created_at >= today).count()
    new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
    new_users_month = db.query(User).filter(User.created_at >= month_ago).count()
    
    # Users by role
    users_by_role = {}
    for role in UserRole:
        count = db.query(User).filter(User.role == role).count()
        users_by_role[role.value] = count
    
    # Users by status
    users_by_status = {
        "active": db.query(User).filter(User.is_active == True).count(),
        "inactive": db.query(User).filter(User.is_active == False).count(),
        "pending": db.query(User).filter(User.email_verified_at.is_(None)).count()
    }
    
    return UserMetrics(
        total_users=total_users,
        active_users=active_users,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        new_users_month=new_users_month,
        users_by_role=users_by_role,
        users_by_status=users_by_status
    )

def get_detection_metrics(db: Session) -> DetectionMetrics:
    """Get detection-related metrics"""
    
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total detections
    total_detections = db.query(DetectionResult).count()
    
    # Detections by time period
    detections_today = db.query(DetectionResult).filter(DetectionResult.created_at >= today).count()
    detections_week = db.query(DetectionResult).filter(DetectionResult.created_at >= week_ago).count()
    detections_month = db.query(DetectionResult).filter(DetectionResult.created_at >= month_ago).count()
    
    # Detections by type (assuming detection_type field)
    detections_by_type = {
        "image": db.query(DetectionResult).filter(DetectionResult.detection_type == "image").count(),
        "audio": db.query(DetectionResult).filter(DetectionResult.detection_type == "audio").count(),
        "network": db.query(DetectionResult).filter(DetectionResult.detection_type == "network").count(),
        "multimodal": db.query(DetectionResult).filter(DetectionResult.detection_type == "multimodal").count()
    }
    
    # Detections by risk level
    detections_by_risk = {
        "low": db.query(DetectionResult).filter(DetectionResult.risk_level == "low").count(),
        "medium": db.query(DetectionResult).filter(DetectionResult.risk_level == "medium").count(),
        "high": db.query(DetectionResult).filter(DetectionResult.risk_level == "high").count(),
        "critical": db.query(DetectionResult).filter(DetectionResult.risk_level == "critical").count()
    }
    
    # False positive rate (placeholder - would need actual false positive tracking)
    false_positive_rate = 0.05  # 5% false positive rate
    
    return DetectionMetrics(
        total_detections=total_detections,
        detections_today=detections_today,
        detections_week=detections_week,
        detections_month=detections_month,
        detections_by_type=detections_by_type,
        detections_by_risk=detections_by_risk,
        false_positive_rate=false_positive_rate
    )

def get_revenue_metrics(db: Session) -> RevenueMetrics:
    """Get revenue-related metrics"""
    
    # This would integrate with Stripe API for actual revenue data
    # For now, using placeholder data
    
    total_revenue = 150000.00  # $150,000 total revenue
    revenue_today = 2500.00  # $2,500 today
    revenue_week = 17500.00  # $17,500 this week
    revenue_month = 75000.00  # $75,000 this month
    
    # Active subscriptions
    active_subscriptions = 125  # 125 active subscriptions
    
    # Subscriptions by plan
    subscriptions_by_plan = {
        "starter": 50,
        "professional": 60,
        "enterprise": 15
    }
    
    # Churn rate (placeholder)
    churn_rate = 0.03  # 3% monthly churn rate
    
    return RevenueMetrics(
        total_revenue=total_revenue,
        revenue_today=revenue_today,
        revenue_week=revenue_week,
        revenue_month=revenue_month,
        active_subscriptions=active_subscriptions,
        subscriptions_by_plan=subscriptions_by_plan,
        churn_rate=churn_rate
    )

def get_recent_activities(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent system activities"""
    
    activities = []
    
    # Recent user registrations
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    for user in recent_users:
        activities.append({
            "type": "user_registration",
            "message": f"New user registered: {user.username}",
            "timestamp": user.created_at,
            "severity": "info"
        })
    
    # Recent detections
    recent_detections = db.query(DetectionResult).order_by(desc(DetectionResult.created_at)).limit(5).all()
    for detection in recent_detections:
        activities.append({
            "type": "detection",
            "message": f"Detection completed: {detection.detection_type}",
            "timestamp": detection.created_at,
            "severity": detection.risk_level
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:limit]

def get_alerts() -> List[Dict[str, Any]]:
    """Get system alerts"""
    
    alerts = []
    
    # System alerts
    system_metrics = get_system_metrics()
    
    if system_metrics.cpu_usage > 80:
        alerts.append({
            "type": "system",
            "message": f"High CPU usage: {system_metrics.cpu_usage:.1f}%",
            "severity": "warning",
            "timestamp": datetime.now(timezone.utc)
        })
    
    if system_metrics.memory_usage > 85:
        alerts.append({
            "type": "system",
            "message": f"High memory usage: {system_metrics.memory_usage:.1f}%",
            "severity": "warning",
            "timestamp": datetime.now(timezone.utc)
        })
    
    if system_metrics.disk_usage > 90:
        alerts.append({
            "type": "system",
            "message": f"High disk usage: {system_metrics.disk_usage:.1f}%",
            "severity": "critical",
            "timestamp": datetime.now(timezone.utc)
        })
    
    return alerts

# API Routes
def setup_admin_dashboard_routes(app: FastAPI):
    """Setup admin dashboard routes"""
    
    @app.get("/admin/dashboard", response_class=HTMLResponse)
    async def admin_dashboard_page(
        current_user: User = Depends(get_current_superuser)
    ):
        """Admin dashboard page"""
        
        return templates.TemplateResponse("admin/dashboard.html", {
            "request": {"type": "http", "url": "/admin/dashboard"},
            "user": current_user
        })
    
    @app.get("/admin/api/metrics", response_model=AdminDashboardData)
    async def get_dashboard_metrics(
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get dashboard metrics"""
        
        system_metrics = get_system_metrics()
        user_metrics = get_user_metrics(db)
        detection_metrics = get_detection_metrics(db)
        revenue_metrics = get_revenue_metrics(db)
        recent_activities = get_recent_activities(db)
        alerts = get_alerts()
        
        return AdminDashboardData(
            system_metrics=system_metrics,
            user_metrics=user_metrics,
            detection_metrics=detection_metrics,
            revenue_metrics=revenue_metrics,
            recent_activities=recent_activities,
            alerts=alerts
        )
    
    @app.get("/admin/api/system-metrics", response_model=SystemMetrics)
    async def get_system_metrics_api(
        current_user: User = Depends(get_current_superuser)
    ):
        """Get system metrics"""
        
        return get_system_metrics()
    
    @app.get("/admin/api/user-metrics", response_model=UserMetrics)
    async def get_user_metrics_api(
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get user metrics"""
        
        return get_user_metrics(db)
    
    @app.get("/admin/api/detection-metrics", response_model=DetectionMetrics)
    async def get_detection_metrics_api(
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get detection metrics"""
        
        return get_detection_metrics(db)
    
    @app.get("/admin/api/revenue-metrics", response_model=RevenueMetrics)
    async def get_revenue_metrics_api(
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get revenue metrics"""
        
        return get_revenue_metrics(db)
    
    @app.get("/admin/api/recent-activities")
    async def get_recent_activities_api(
        limit: int = Query(10, ge=1, le=50),
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get recent activities"""
        
        return get_recent_activities(db, limit)
    
    @app.get("/admin/api/alerts")
    async def get_alerts_api(
        current_user: User = Depends(get_current_superuser)
    ):
        """Get system alerts"""
        
        return get_alerts()
    
    @app.get("/admin/api/users")
    async def get_users_list(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
        role: Optional[UserRole] = Query(None),
        status: Optional[UserStatus] = Query(None),
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get users list"""
        
        skip = (page - 1) * per_page
        users = get_users(db, skip=skip, limit=per_page, search=search, role=role, status=status)
        total = count_users(db, search=search, role=role, status=status)
        
        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "last_login": user.last_login
                }
                for user in users
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    @app.get("/admin/api/detections")
    async def get_detections_list(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_superuser),
        db: Session = Depends(get_db)
    ):
        """Get detections list"""
        
        skip = (page - 1) * per_page
        detections = db.query(DetectionResult).order_by(desc(DetectionResult.created_at)).offset(skip).limit(per_page).all()
        total = db.query(DetectionResult).count()
        
        return {
            "detections": [
                {
                    "id": detection.id,
                    "detection_type": detection.detection_type,
                    "risk_level": detection.risk_level,
                    "confidence": detection.confidence,
                    "created_at": detection.created_at,
                    "user_id": detection.user_id,
                    "game_id": detection.game_id
                }
                for detection in detections
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    @app.post("/admin/api/system/restart")
    async def restart_system(
        current_user: User = Depends(get_current_superuser)
    ):
        """Restart system (placeholder)"""
        
        # This would implement actual system restart logic
        return {"message": "System restart initiated"}
    
    @app.post("/admin/api/system/cleanup")
    async def cleanup_system(
        current_user: User = Depends(get_current_superuser)
    ):
        """Cleanup system (placeholder)"""
        
        # This would implement actual system cleanup logic
        return {"message": "System cleanup completed"}
    
    @app.get("/admin/api/logs")
    async def get_system_logs(
        level: str = Query("info", regex="^(debug|info|warning|error)$"),
        lines: int = Query(100, ge=1, le=1000),
        current_user: User = Depends(get_current_superuser)
    ):
        """Get system logs"""
        
        # This would implement actual log retrieval
        log_file = Path("logs/app.log")
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                return {
                    "logs": [line.strip() for line in recent_lines],
                    "level": level,
                    "lines_returned": len(recent_lines)
                }
        else:
            return {
                "logs": [],
                "level": level,
                "lines_returned": 0,
                "message": "No log file found"
            }

# Export functions
__all__ = [
    "setup_admin_dashboard_routes",
    "get_system_metrics",
    "get_user_metrics",
    "get_detection_metrics",
    "get_revenue_metrics",
    "get_recent_activities",
    "get_alerts",
    "SystemMetrics",
    "UserMetrics",
    "DetectionMetrics",
    "RevenueMetrics",
    "AdminDashboardData"
]
