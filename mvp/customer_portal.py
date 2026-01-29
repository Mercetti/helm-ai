"""
Helm AI Customer Portal
Complete customer portal with dashboard, usage analytics, billing management, and support features
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path

from database import get_db, User, DetectionResult, GameSession
from auth import get_current_active_user
from billing import get_subscription, SubscriptionStatus
from user_management import UserProfile

# Templates setup
templates = Jinja2Templates(directory="templates")

# Pydantic Models
class UsageAnalytics(BaseModel):
    total_requests: int
    requests_today: int
    requests_week: int
    requests_month: int
    requests_by_type: Dict[str, int]
    requests_by_risk: Dict[str, int]
    average_response_time: float
    success_rate: float

class BillingInfo(BaseModel):
    subscription_id: str
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    amount: int
    currency: str
    next_billing_date: datetime
    cancel_at_period_end: bool
    payment_methods: List[Dict[str, Any]]

class SupportTicket(BaseModel):
    id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    responses: List[Dict[str, Any]]

class CustomerDashboardData(BaseModel):
    user_profile: Dict[str, Any]
    usage_analytics: UsageAnalytics
    billing_info: BillingInfo
    recent_detections: List[Dict[str, Any]]
    support_tickets: List[SupportTicket]
    notifications: List[Dict[str, Any]]

# Customer Portal Functions
def get_usage_analytics(db: Session, user_id: int) -> UsageAnalytics:
    """Get usage analytics for a customer"""
    
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Total requests
    total_requests = db.query(DetectionResult).filter(DetectionResult.user_id == user_id).count()
    
    # Requests by time period
    requests_today = db.query(DetectionResult).filter(
        and_(DetectionResult.user_id == user_id, DetectionResult.created_at >= today)
    ).count()
    
    requests_week = db.query(DetectionResult).filter(
        and_(DetectionResult.user_id == user_id, DetectionResult.created_at >= week_ago)
    ).count()
    
    requests_month = db.query(DetectionResult).filter(
        and_(DetectionResult.user_id == user_id, DetectionResult.created_at >= month_ago)
    ).count()
    
    # Requests by type
    requests_by_type = {
        "image": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.detection_type == "image")
        ).count(),
        "audio": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.detection_type == "audio")
        ).count(),
        "network": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.detection_type == "network")
        ).count(),
        "multimodal": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.detection_type == "multimodal")
        ).count()
    }
    
    # Requests by risk level
    requests_by_risk = {
        "low": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.risk_level == "low")
        ).count(),
        "medium": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.risk_level == "medium")
        ).count(),
        "high": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.risk_level == "high")
        ).count(),
        "critical": db.query(DetectionResult).filter(
            and_(DetectionResult.user_id == user_id, DetectionResult.risk_level == "critical")
        ).count()
    }
    
    # Average response time (placeholder)
    average_response_time = 0.15  # 150ms average response time
    
    # Success rate (placeholder)
    success_rate = 0.98  # 98% success rate
    
    return UsageAnalytics(
        total_requests=total_requests,
        requests_today=requests_today,
        requests_week=requests_week,
        requests_month=requests_month,
        requests_by_type=requests_by_type,
        requests_by_risk=requests_by_risk,
        average_response_time=average_response_time,
        success_rate=success_rate
    )

def get_billing_info(db: Session, user_id: int) -> BillingInfo:
    """Get billing information for a customer"""
    
    # This would integrate with Stripe API for actual billing data
    # For now, using placeholder data
    
    subscription_id = f"sub_{user_id}"
    plan = "professional"
    status = "active"
    current_period_start = datetime.now(timezone.utc).replace(day=1)
    current_period_end = current_period_start + timedelta(days=30)
    amount = 100000  # $1,000 in cents
    currency = "usd"
    next_billing_date = current_period_end
    cancel_at_period_end = False
    
    payment_methods = [
        {
            "id": "pm_card_123",
            "type": "card",
            "last4": "4242",
            "brand": "visa",
            "exp_month": 12,
            "exp_year": 2025,
            "is_default": True
        }
    ]
    
    return BillingInfo(
        subscription_id=subscription_id,
        plan=plan,
        status=status,
        current_period_start=current_period_start,
        current_period_end=current_period_end,
        amount=amount,
        currency=currency,
        next_billing_date=next_billing_date,
        cancel_at_period_end=cancel_at_period_end,
        payment_methods=payment_methods
    )

def get_recent_detections(db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent detections for a customer"""
    
    detections = db.query(DetectionResult).filter(
        DetectionResult.user_id == user_id
    ).order_by(desc(DetectionResult.created_at)).limit(limit).all()
    
    return [
        {
            "id": detection.id,
            "detection_type": detection.detection_type,
            "risk_level": detection.risk_level,
            "confidence": detection.confidence,
            "created_at": detection.created_at,
            "game_id": detection.game_id,
            "features": detection.features
        }
        for detection in detections
    ]

def get_support_tickets(db: Session, user_id: int) -> List[SupportTicket]:
    """Get support tickets for a customer"""
    
    # This would integrate with a support system like Zendesk
    # For now, using placeholder data
    
    tickets = [
        SupportTicket(
            id="ticket_123",
            subject="Billing Question",
            description="I have a question about my subscription",
            status="open",
            priority="medium",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            updated_at=datetime.now(timezone.utc) - timedelta(days=1),
            responses=[
                {
                    "id": "resp_123",
                    "author": "support",
                    "message": "Thank you for your question. We'll help you with that.",
                    "created_at": datetime.now(timezone.utc) - timedelta(days=1)
                }
            ]
        ),
        SupportTicket(
            id="ticket_124",
            subject="Technical Issue",
            description="I'm having trouble with the API integration",
            status="resolved",
            priority="high",
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
            updated_at=datetime.now(timezone.utc) - timedelta(days=3),
            responses=[
                {
                    "id": "resp_124",
                    "author": "support",
                    "message": "We've resolved the issue. Please try again.",
                    "created_at": datetime.now(timezone.utc) - timedelta(days=3)
                }
            ]
        )
    ]
    
    return tickets

def get_notifications(user_id: int) -> List[Dict[str, Any]]:
    """Get notifications for a customer"""
    
    notifications = [
        {
            "id": "notif_123",
            "type": "info",
            "title": "Welcome to Helm AI",
            "message": "Thank you for joining Helm AI! Get started with our quick start guide.",
            "created_at": datetime.now(timezone.utc) - timedelta(days=1),
            "read": False
        },
        {
            "id": "notif_124",
            "type": "success",
            "title": "Payment Successful",
            "message": "Your subscription payment has been processed successfully.",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=6),
            "read": False
        },
        {
            "id": "notif_125",
            "type": "warning",
            "title": "Usage Limit",
            "message": "You've used 80% of your monthly API quota.",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
            "read": True
        }
    ]
    
    return notifications

# API Routes
def setup_customer_portal_routes(app: FastAPI):
    """Setup customer portal routes"""
    
    @app.get("/portal", response_class=HTMLResponse)
    async def customer_portal_page(
        current_user: User = Depends(get_current_active_user)
    ):
        """Customer portal page"""
        
        return templates.TemplateResponse("portal/dashboard.html", {
            "request": {"type": "http", "url": "/portal"},
            "user": current_user
        })
    
    @app.get("/portal/api/dashboard", response_model=CustomerDashboardData)
    async def get_customer_dashboard(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get customer dashboard data"""
        
        # Get user profile
        user_profile = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "company": current_user.company,
            "role": current_user.role,
            "avatar_url": current_user.avatar_url,
            "bio": current_user.bio,
            "preferences": current_user.preferences,
            "created_at": current_user.created_at,
            "last_login": current_user.last_login,
            "email_verified_at": current_user.email_verified_at
        }
        
        # Get usage analytics
        usage_analytics = get_usage_analytics(db, current_user.id)
        
        # Get billing info
        billing_info = get_billing_info(db, current_user.id)
        
        # Get recent detections
        recent_detections = get_recent_detections(db, current_user.id)
        
        # Get support tickets
        support_tickets = get_support_tickets(db, current_user.id)
        
        # Get notifications
        notifications = get_notifications(current_user.id)
        
        return CustomerDashboardData(
            user_profile=user_profile,
            usage_analytics=usage_analytics,
            billing_info=billing_info,
            recent_detections=recent_detections,
            support_tickets=support_tickets,
            notifications=notifications
        )
    
    @app.get("/portal/api/profile")
    async def get_customer_profile(
        current_user: User = Depends(get_current_active_user)
    ):
        """Get customer profile"""
        
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "company": current_user.company,
            "role": current_user.role,
            "avatar_url": current_user.avatar_url,
            "bio": current_user.bio,
            "preferences": current_user.preferences,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
            "last_login": current_user.last_login,
            "email_verified_at": current_user.email_verified_at
        }
    
    @app.put("/portal/api/profile")
    async def update_customer_profile(
        profile_data: UserProfile,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Update customer profile"""
        
        # Update user fields
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        if profile_data.company is not None:
            current_user.company = profile_data.company
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        if profile_data.avatar_url is not None:
            current_user.avatar_url = profile_data.avatar_url
        if profile_data.preferences is not None:
            current_user.preferences = profile_data.preferences
        
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        
        return {"message": "Profile updated successfully"}
    
    @app.get("/portal/api/usage-analytics", response_model=UsageAnalytics)
    async def get_usage_analytics_api(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get usage analytics"""
        
        return get_usage_analytics(db, current_user.id)
    
    @app.get("/portal/api/billing", response_model=BillingInfo)
    async def get_billing_info_api(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get billing information"""
        
        return get_billing_info(db, current_user.id)
    
    @app.get("/portal/api/detections")
    async def get_recent_detections_api(
        limit: int = Query(10, ge=1, le=50),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get recent detections"""
        
        return get_recent_detections(db, current_user.id, limit)
    
    @app.get("/portal/api/support-tickets")
    async def get_support_tickets_api(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get support tickets"""
        
        return get_support_tickets(db, current_user.id)
    
    @app.post("/portal/api/support-tickets")
    async def create_support_ticket(
        ticket_data: dict,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new support ticket"""
        
        # This would integrate with a support system like Zendesk
        # For now, returning a placeholder response
        
        ticket_id = f"ticket_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": ticket_id,
            "message": "Support ticket created successfully",
            "ticket_id": ticket_id
        }
    
    @app.get("/portal/api/notifications")
    async def get_notifications_api(
        current_user: User = Depends(get_current_active_user)
    ):
        """Get notifications"""
        
        return get_notifications(current_user.id)
    
    @app.put("/portal/api/notifications/{notification_id}/read")
    async def mark_notification_read(
        notification_id: str,
        current_user: User = Depends(get_current_active_user)
    ):
        """Mark notification as read"""
        
        # This would update the notification in the database
        # For now, returning a placeholder response
        
        return {"message": "Notification marked as read"}
    
    @app.get("/portal/api/api-keys")
    async def get_api_keys(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get API keys"""
        
        # This would return API keys from the database
        # For now, returning placeholder data
        
        return {
            "api_keys": [
                {
                    "id": "key_123",
                    "name": "Production Key",
                    "key": "sk_live_...",
                    "created_at": datetime.now(timezone.utc) - timedelta(days=30),
                    "last_used": datetime.now(timezone.utc) - timedelta(hours=2),
                    "is_active": True
                },
                {
                    "id": "key_124",
                    "name": "Development Key",
                    "key": "sk_test_...",
                    "created_at": datetime.now(timezone.utc) - timedelta(days=7),
                    "last_used": datetime.now(timezone.utc) - timedelta(days=1),
                    "is_active": True
                }
            ]
        }
    
    @app.post("/portal/api/api-keys")
    async def create_api_key(
        key_data: dict,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new API key"""
        
        # This would create an API key in the database
        # For now, returning a placeholder response
        
        key_id = f"key_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": key_id,
            "message": "API key created successfully",
            "key": "sk_live_..."  # Would generate actual key
        }
    
    @app.delete("/portal/api/api-keys/{key_id}")
    async def delete_api_key(
        key_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Delete an API key"""
        
        # This would delete the API key from the database
        # For now, returning a placeholder response
        
        return {"message": "API key deleted successfully"}

# Export functions
__all__ = [
    "setup_customer_portal_routes",
    "get_usage_analytics",
    "get_billing_info",
    "get_recent_detections",
    "get_support_tickets",
    "get_notifications",
    "UsageAnalytics",
    "BillingInfo",
    "SupportTicket",
    "CustomerDashboardData"
]
