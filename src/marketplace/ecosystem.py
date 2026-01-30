"""
Marketplace Ecosystem for Helm AI
================================

This module provides comprehensive marketplace capabilities:
- App store and plugin marketplace
- Developer portal and SDK
- App submission and review process
- Monetization and revenue sharing
- App analytics and insights
- User reviews and ratings
- Integration management
- Marketplace governance
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
from collections import defaultdict

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("marketplace")


class AppStatus(str, Enum):
    """App status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


class AppCategory(str, Enum):
    """App categories"""
    ANALYTICS = "analytics"
    SECURITY = "security"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    AI_ML = "ai_ml"
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    DEVELOPMENT = "development"
    BUSINESS = "business"
    UTILITIES = "utilities"


class PricingModel(str, Enum):
    """Pricing models"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    FREEMIUM = "freemium"
    ENTERPRISE = "enterprise"


class ReviewStatus(str, Enum):
    """Review status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"


@dataclass
class MarketplaceApp:
    """Marketplace app definition"""
    id: str
    name: str
    description: str
    short_description: str
    category: AppCategory
    developer_id: str
    version: str
    status: AppStatus
    pricing_model: PricingModel
    price: float = 0.0
    currency: str = "USD"
    download_url: str
    documentation_url: str
    support_url: str
    privacy_policy_url: str
    terms_of_service_url: str
    screenshots: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    changelog: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppReview:
    """App review process"""
    id: str
    app_id: str
    reviewer_id: str
    status: ReviewStatus
    score: int = 0
    comments: str = ""
    checklist: Dict[str, bool] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None


@dataclass
class UserReview:
    """User review and rating"""
    id: str
    app_id: str
    user_id: str
    rating: int  # 1-5 stars
    title: str
    content: str
    helpful_count: int = 0
    verified_purchase: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AppInstallation:
    """App installation record"""
    id: str
    app_id: str
    user_id: str
    tenant_id: str
    version: str
    status: str = "installed"
    installed_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AppUsage:
    """App usage analytics"""
    id: str
    app_id: str
    tenant_id: str
    date: datetime
    active_users: int = 0
    total_sessions: int = 0
    session_duration: float = 0.0
    api_calls: int = 0
    errors: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Developer:
    """Developer profile"""
    id: str
    name: str
    email: str
    company: str = ""
    website: str = ""
    description: str = ""
    verified: bool = False
    rating: float = 0.0
    total_apps: int = 0
    total_downloads: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueShare:
    """Revenue sharing configuration"""
    id: str
    app_id: str
    developer_id: str
    platform_percentage: float = 30.0  # Platform takes 30%
    developer_percentage: float = 70.0  # Developer gets 70%
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class MarketplaceManager:
    """Marketplace Ecosystem Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.apps: Dict[str, MarketplaceApp] = {}
        self.reviews: Dict[str, AppReview] = {}
        self.user_reviews: Dict[str, UserReview] = {}
        self.installations: Dict[str, AppInstallation] = {}
        self.usage: Dict[str, AppUsage] = {}
        self.developers: Dict[str, Developer] = {}
        self.revenue_shares: Dict[str, RevenueShare] = {}
        
        # Initialize marketplace
        self._initialize_marketplace()
        
        logger.info("Marketplace Manager initialized")
    
    def _initialize_marketplace(self):
        """Initialize marketplace with default settings"""
        # Create default developer (Helm AI)
        helm_developer = Developer(
            id=str(uuid.uuid4()),
            name="Helm AI",
            email="marketplace@helm-ai.com",
            company="Helm AI Inc.",
            website="https://helm-ai.com",
            description="Official Helm AI applications and integrations",
            verified=True
        )
        self.developers[helm_developer.id] = helm_developer
        
        # Create sample apps
        self._create_sample_apps(helm_developer.id)
        
        logger.info("Marketplace initialized with default content")
    
    def _create_sample_apps(self, developer_id: str):
        """Create sample marketplace apps"""
        sample_apps = [
            {
                "name": "Advanced Analytics Dashboard",
                "description": "Comprehensive analytics dashboard with real-time KPIs, custom reports, and AI-powered insights.",
                "short_description": "Advanced analytics with AI insights",
                "category": AppCategory.ANALYTICS,
                "pricing_model": PricingModel.FREEMIUM,
                "price": 0.0,
                "tags": ["analytics", "dashboard", "ai", "insights"],
                "requirements": ["Helm AI Core", "Python 3.8+"],
                "features": ["Real-time KPIs", "Custom reports", "AI insights", "Data visualization"]
            },
            {
                "name": "Security Threat Scanner",
                "description": "AI-powered security scanning with real-time threat detection, vulnerability assessment, and automated remediation.",
                "short_description": "AI-powered security scanning",
                "category": AppCategory.SECURITY,
                "pricing_model": PricingModel.SUBSCRIPTION,
                "price": 29.99,
                "tags": ["security", "scanning", "threats", "ai"],
                "requirements": ["Helm AI Security", "Admin access"],
                "features": ["Real-time scanning", "Threat detection", "Auto-remediation", "Compliance reports"]
            },
            {
                "name": "Slack Integration",
                "description": "Seamless Slack integration for notifications, alerts, and team collaboration within Helm AI.",
                "short_description": "Slack integration for teams",
                "category": AppCategory.INTEGRATION,
                "pricing_model": PricingModel.FREE,
                "price": 0.0,
                "tags": ["slack", "integration", "notifications", "collaboration"],
                "requirements": ["Slack workspace", "API access"],
                "features": ["Real-time notifications", "Alert routing", "Team collaboration", "Custom commands"]
            },
            {
                "name": "Workflow Automation",
                "description": "Intelligent workflow automation with AI-driven process optimization and custom automation rules.",
                "short_description": "AI-powered workflow automation",
                "category": AppCategory.AUTOMATION,
                "pricing_model": PricingModel.USAGE_BASED,
                "price": 0.01,
                "tags": ["automation", "workflows", "ai", "optimization"],
                "requirements": ["Helm AI Core", "Workflow engine"],
                "features": ["Process automation", "AI optimization", "Custom rules", "Performance tracking"]
            },
            {
                "name": "ML Model Manager",
                "description": "Advanced machine learning model management with version control, deployment, and monitoring.",
                "short_description": "ML model management platform",
                "category": AppCategory.AI_ML,
                "pricing_model": PricingModel.ENTERPRISE,
                "price": 199.99,
                "tags": ["machine learning", "models", "deployment", "monitoring"],
                "requirements": ["Helm AI ML", "GPU resources"],
                "features": ["Model versioning", "Auto-deployment", "Performance monitoring", "A/B testing"]
            }
        ]
        
        for app_data in sample_apps:
            app = MarketplaceApp(
                id=str(uuid.uuid4()),
                name=app_data["name"],
                description=app_data["description"],
                short_description=app_data["short_description"],
                category=app_data["category"],
                developer_id=developer_id,
                version="1.0.0",
                status=AppStatus.PUBLISHED,
                pricing_model=app_data["pricing_model"],
                price=app_data["price"],
                download_url=f"https://marketplace.helm-ai.com/download/{uuid.uuid4()}",
                documentation_url=f"https://docs.helm-ai.com/apps/{uuid.uuid4()}",
                support_url=f"https://support.helm-ai.com/apps/{uuid.uuid4()}",
                privacy_policy_url="https://helm-ai.com/privacy",
                terms_of_service_url="https://helm-ai.com/terms",
                screenshots=[f"https://screenshots.helm-ai.com/{uuid.uuid4()}/1.png",
                           f"https://screenshots.helm-ai.com/{uuid.uuid4()}/2.png"],
                tags=app_data["tags"],
                requirements=app_data["requirements"],
                features=app_data["features"],
                changelog=[
                    {"version": "1.0.0", "date": datetime.utcnow().isoformat(), "changes": ["Initial release"]},
                ],
                published_at=datetime.utcnow()
            )
            
            self.apps[app.id] = app
            
            # Create revenue share
            revenue_share = RevenueShare(
                id=str(uuid.uuid4()),
                app_id=app.id,
                developer_id=developer_id
            )
            self.revenue_shares[revenue_share.id] = revenue_share
        
        logger.info(f"Created {len(sample_apps)} sample marketplace apps")
    
    def create_developer(self, developer_data: Dict[str, Any]) -> Developer:
        """Create new developer profile"""
        try:
            developer = Developer(
                id=str(uuid.uuid4()),
                name=developer_data.get("name", ""),
                email=developer_data.get("email", ""),
                company=developer_data.get("company", ""),
                website=developer_data.get("website", ""),
                description=developer_data.get("description", "")
            )
            
            self.developers[developer.id] = developer
            
            logger.info(f"Developer created: {developer.id}")
            return developer
            
        except Exception as e:
            logger.error(f"Failed to create developer: {e}")
            raise
    
    def submit_app(self, developer_id: str, app_data: Dict[str, Any]) -> MarketplaceApp:
        """Submit new app to marketplace"""
        try:
            if developer_id not in self.developers:
                raise ValueError("Developer not found")
            
            app = MarketplaceApp(
                id=str(uuid.uuid4()),
                name=app_data.get("name", ""),
                description=app_data.get("description", ""),
                short_description=app_data.get("short_description", ""),
                category=AppCategory(app_data.get("category", "utilities")),
                developer_id=developer_id,
                version=app_data.get("version", "1.0.0"),
                status=AppStatus.SUBMITTED,
                pricing_model=PricingModel(app_data.get("pricing_model", "free")),
                price=app_data.get("price", 0.0),
                currency=app_data.get("currency", "USD"),
                download_url=app_data.get("download_url", ""),
                documentation_url=app_data.get("documentation_url", ""),
                support_url=app_data.get("support_url", ""),
                privacy_policy_url=app_data.get("privacy_policy_url", ""),
                terms_of_service_url=app_data.get("terms_of_service_url", ""),
                screenshots=app_data.get("screenshots", []),
                tags=app_data.get("tags", []),
                requirements=app_data.get("requirements", []),
                features=app_data.get("features", []),
                changelog=app_data.get("changelog", []),
                metadata=app_data.get("metadata", {})
            )
            
            self.apps[app.id] = app
            
            # Create revenue share
            revenue_share = RevenueShare(
                id=str(uuid.uuid4()),
                app_id=app.id,
                developer_id=developer_id
            )
            self.revenue_shares[revenue_share.id] = revenue_share
            
            # Start review process
            self._start_app_review(app.id)
            
            logger.info(f"App submitted: {app.id}")
            return app
            
        except Exception as e:
            logger.error(f"Failed to submit app: {e}")
            raise
    
    def _start_app_review(self, app_id: str):
        """Start app review process"""
        try:
            review = AppReview(
                id=str(uuid.uuid4()),
                app_id=app_id,
                reviewer_id="system",  # In real implementation, assign to actual reviewer
                status=ReviewStatus.PENDING,
                checklist={
                    "functionality": False,
                    "security": False,
                    "performance": False,
                    "documentation": False,
                    "user_experience": False,
                    "compliance": False
                }
            )
            
            self.reviews[review.id] = review
            
            # Update app status
            if app_id in self.apps:
                self.apps[app_id].status = AppStatus.UNDER_REVIEW
            
            logger.info(f"Review started for app: {app_id}")
            
        except Exception as e:
            logger.error(f"Failed to start app review: {e}")
            raise
    
    def approve_app(self, app_id: str, reviewer_id: str, comments: str = "") -> bool:
        """Approve app for marketplace"""
        try:
            # Find and update review
            review = next((r for r in self.reviews.values() if r.app_id == app_id), None)
            if not review:
                return False
            
            review.status = ReviewStatus.APPROVED
            review.reviewer_id = reviewer_id
            review.comments = comments
            review.completed_at = datetime.utcnow()
            
            # Update app status
            if app_id in self.apps:
                self.apps[app_id].status = AppStatus.APPROVED
                self.apps[app_id].updated_at = datetime.utcnow()
            
            logger.info(f"App approved: {app_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve app: {e}")
            return False
    
    def publish_app(self, app_id: str) -> bool:
        """Publish app to marketplace"""
        try:
            if app_id not in self.apps:
                return False
            
            app = self.apps[app_id]
            if app.status != AppStatus.APPROVED:
                return False
            
            app.status = AppStatus.PUBLISHED
            app.published_at = datetime.utcnow()
            app.updated_at = datetime.utcnow()
            
            logger.info(f"App published: {app_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish app: {e}")
            return False
    
    def install_app(self, app_id: str, user_id: str, tenant_id: str) -> AppInstallation:
        """Install app for user/tenant"""
        try:
            if app_id not in self.apps:
                raise ValueError("App not found")
            
            app = self.apps[app_id]
            if app.status != AppStatus.PUBLISHED:
                raise ValueError("App not available for installation")
            
            # Check if already installed
            existing_install = next((i for i in self.installations.values() 
                                   if i.app_id == app_id and i.tenant_id == tenant_id), None)
            if existing_install:
                return existing_install
            
            installation = AppInstallation(
                id=str(uuid.uuid4()),
                app_id=app_id,
                user_id=user_id,
                tenant_id=tenant_id,
                version=app.version
            )
            
            self.installations[installation.id] = installation
            
            # Update app download count
            # In real implementation, this would be tracked in the app record
            
            logger.info(f"App installed: {app_id} for tenant {tenant_id}")
            return installation
            
        except Exception as e:
            logger.error(f"Failed to install app: {e}")
            raise
    
    def add_user_review(self, app_id: str, user_id: str, rating: int, 
                       title: str, content: str, verified_purchase: bool = False) -> UserReview:
        """Add user review for app"""
        try:
            if app_id not in self.apps:
                raise ValueError("App not found")
            
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            
            # Check if user already reviewed
            existing_review = next((r for r in self.user_reviews.values() 
                                  if r.app_id == app_id and r.user_id == user_id), None)
            if existing_review:
                # Update existing review
                existing_review.rating = rating
                existing_review.title = title
                existing_review.content = content
                existing_review.verified_purchase = verified_purchase
                existing_review.updated_at = datetime.utcnow()
                return existing_review
            
            # Create new review
            review = UserReview(
                id=str(uuid.uuid4()),
                app_id=app_id,
                user_id=user_id,
                rating=rating,
                title=title,
                content=content,
                verified_purchase=verified_purchase
            )
            
            self.user_reviews[review.id] = review
            
            logger.info(f"User review added: {review.id}")
            return review
            
        except Exception as e:
            logger.error(f"Failed to add user review: {e}")
            raise
    
    def record_app_usage(self, app_id: str, tenant_id: str, date: datetime, 
                       active_users: int, total_sessions: int, session_duration: float,
                       api_calls: int, errors: int) -> AppUsage:
        """Record app usage analytics"""
        try:
            usage = AppUsage(
                id=str(uuid.uuid4()),
                app_id=app_id,
                tenant_id=tenant_id,
                date=date,
                active_users=active_users,
                total_sessions=total_sessions,
                session_duration=session_duration,
                api_calls=api_calls,
                errors=errors
            )
            
            self.usage[usage.id] = usage
            
            logger.info(f"App usage recorded: {app_id}")
            return usage
            
        except Exception as e:
            logger.error(f"Failed to record app usage: {e}")
            raise
    
    def get_marketplace_apps(self, category: Optional[AppCategory] = None,
                           pricing_model: Optional[PricingModel] = None,
                           tags: Optional[List[str]] = None,
                           sort_by: str = "created_at",
                           limit: int = 50) -> List[MarketplaceApp]:
        """Get marketplace apps with filters"""
        try:
            apps = list(self.apps.values())
            
            # Filter by status (only published apps)
            apps = [app for app in apps if app.status == AppStatus.PUBLISHED]
            
            # Filter by category
            if category:
                apps = [app for app in apps if app.category == category]
            
            # Filter by pricing model
            if pricing_model:
                apps = [app for app in apps if app.pricing_model == pricing_model]
            
            # Filter by tags
            if tags:
                apps = [app for app in apps if any(tag in app.tags for tag in tags)]
            
            # Sort apps
            if sort_by == "created_at":
                apps.sort(key=lambda x: x.created_at, reverse=True)
            elif sort_by == "name":
                apps.sort(key=lambda x: x.name.lower())
            elif sort_by == "price":
                apps.sort(key=lambda x: x.price)
            elif sort_by == "downloads":
                # In real implementation, sort by download count
                apps.sort(key=lambda x: x.created_at, reverse=True)
            
            # Limit results
            return apps[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get marketplace apps: {e}")
            return []
    
    def get_app_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed app information"""
        try:
            if app_id not in self.apps:
                return None
            
            app = self.apps[app_id]
            developer = self.developers.get(app.developer_id)
            
            # Get user reviews
            user_reviews = [r for r in self.user_reviews.values() if r.app_id == app_id]
            
            # Calculate average rating
            if user_reviews:
                avg_rating = sum(r.rating for r in user_reviews) / len(user_reviews)
                total_reviews = len(user_reviews)
            else:
                avg_rating = 0.0
                total_reviews = 0
            
            # Get installation count
            installation_count = len([i for i in self.installations.values() if i.app_id == app_id])
            
            return {
                "app": {
                    "id": app.id,
                    "name": app.name,
                    "description": app.description,
                    "short_description": app.short_description,
                    "category": app.category.value,
                    "version": app.version,
                    "pricing_model": app.pricing_model.value,
                    "price": app.price,
                    "currency": app.currency,
                    "screenshots": app.screenshots,
                    "tags": app.tags,
                    "requirements": app.requirements,
                    "features": app.features,
                    "changelog": app.changelog,
                    "download_url": app.download_url,
                    "documentation_url": app.documentation_url,
                    "support_url": app.support_url,
                    "privacy_policy_url": app.privacy_policy_url,
                    "terms_of_service_url": app.terms_of_service_url,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat(),
                    "published_at": app.published_at.isoformat() if app.published_at else None
                },
                "developer": {
                    "id": developer.id if developer else "",
                    "name": developer.name if developer else "",
                    "company": developer.company if developer else "",
                    "verified": developer.verified if developer else False,
                    "rating": developer.rating if developer else 0.0,
                    "total_apps": developer.total_apps if developer else 0,
                    "total_downloads": developer.total_downloads if developer else 0
                },
                "stats": {
                    "average_rating": avg_rating,
                    "total_reviews": total_reviews,
                    "installation_count": installation_count
                },
                "reviews": [
                    {
                        "id": review.id,
                        "rating": review.rating,
                        "title": review.title,
                        "content": review.content,
                        "verified_purchase": review.verified_purchase,
                        "created_at": review.created_at.isoformat()
                    }
                    for review in user_reviews[:10]  # Return latest 10 reviews
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get app details: {e}")
            return None
    
    def get_developer_apps(self, developer_id: str) -> List[MarketplaceApp]:
        """Get apps by developer"""
        try:
            return [app for app in self.apps.values() if app.developer_id == developer_id]
        except Exception as e:
            logger.error(f"Failed to get developer apps: {e}")
            return []
    
    def get_user_installations(self, user_id: str, tenant_id: str) -> List[AppInstallation]:
        """Get user's app installations"""
        try:
            return [inst for inst in self.installations.values() 
                   if inst.user_id == user_id and inst.tenant_id == tenant_id]
        except Exception as e:
            logger.error(f"Failed to get user installations: {e}")
            return []
    
    def get_app_analytics(self, app_id: str, start_date: datetime, 
                         end_date: datetime) -> Dict[str, Any]:
        """Get app analytics"""
        try:
            if app_id not in self.apps:
                return {"error": "App not found"}
            
            # Get usage data
            usage_data = [u for u in self.usage.values() 
                         if u.app_id == app_id and start_date <= u.date <= end_date]
            
            # Get installations
            installations = [i for i in self.installations.values() if i.app_id == app_id]
            
            # Get reviews
            reviews = [r for r in self.user_reviews.values() if r.app_id == app_id]
            
            # Calculate metrics
            total_active_users = sum(u.active_users for u in usage_data)
            total_sessions = sum(u.total_sessions for u in usage_data)
            avg_session_duration = sum(u.session_duration for u in usage_data) / len(usage_data) if usage_data else 0
            total_api_calls = sum(u.api_calls for u in usage_data)
            total_errors = sum(u.errors for u in usage_data)
            
            # Calculate revenue (simplified)
            app = self.apps[app_id]
            if app.pricing_model == PricingModel.ONE_TIME:
                total_revenue = len(installations) * app.price
            elif app.pricing_model == PricingModel.SUBSCRIPTION:
                total_revenue = len(installations) * app.price
            else:
                total_revenue = 0.0
            
            # Platform revenue share
            revenue_share = next((rs for rs in self.revenue_shares.values() 
                               if rs.app_id == app_id), None)
            
            if revenue_share:
                platform_revenue = total_revenue * (revenue_share.platform_percentage / 100)
                developer_revenue = total_revenue * (revenue_share.developer_percentage / 100)
            else:
                platform_revenue = 0.0
                developer_revenue = 0.0
            
            return {
                "app_id": app_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "usage_metrics": {
                    "total_active_users": total_active_users,
                    "total_sessions": total_sessions,
                    "average_session_duration": avg_session_duration,
                    "total_api_calls": total_api_calls,
                    "total_errors": total_errors,
                    "error_rate": (total_errors / total_api_calls * 100) if total_api_calls > 0 else 0
                },
                "installation_metrics": {
                    "total_installations": len(installations),
                    "active_installations": len([i for i in installations if i.status == "installed"])
                },
                "review_metrics": {
                    "total_reviews": len(reviews),
                    "average_rating": sum(r.rating for r in reviews) / len(reviews) if reviews else 0,
                    "verified_reviews": len([r for r in reviews if r.verified_purchase])
                },
                "revenue_metrics": {
                    "total_revenue": total_revenue,
                    "platform_revenue": platform_revenue,
                    "developer_revenue": developer_revenue
                },
                "daily_usage": [
                    {
                        "date": u.date.isoformat(),
                        "active_users": u.active_users,
                        "sessions": u.total_sessions,
                        "api_calls": u.api_calls,
                        "errors": u.errors
                    }
                    for u in usage_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get app analytics: {e}")
            return {"error": str(e)}
    
    def get_marketplace_dashboard(self) -> Dict[str, Any]:
        """Get marketplace dashboard data"""
        try:
            dashboard = {
                "overview": {},
                "popular_apps": [],
                "recent_submissions": [],
                "revenue_summary": {},
                "category_stats": {}
            }
            
            # Overview stats
            total_apps = len(self.apps)
            published_apps = len([a for a in self.apps.values() if a.status == AppStatus.PUBLISHED])
            total_developers = len(self.developers)
            total_installations = len(self.installations)
            total_reviews = len(self.user_reviews)
            
            dashboard["overview"] = {
                "total_apps": total_apps,
                "published_apps": published_apps,
                "total_developers": total_developers,
                "total_installations": total_installations,
                "total_reviews": total_reviews
            }
            
            # Popular apps (by installations)
            app_install_counts = defaultdict(int)
            for installation in self.installations.values():
                app_install_counts[installation.app_id] += 1
            
            popular_app_ids = sorted(app_install_counts.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
            
            dashboard["popular_apps"] = [
                {
                    "app_id": app_id,
                    "app_name": self.apps[app_id].name,
                    "installations": count,
                    "category": self.apps[app_id].category.value,
                    "rating": sum(r.rating for r in self.user_reviews.values() if r.app_id == app_id) / len([r for r in self.user_reviews.values() if r.app_id == app_id]) if [r for r in self.user_reviews.values() if r.app_id == app_id] else 0
                }
                for app_id, count in popular_app_ids
                if app_id in self.apps
            ]
            
            # Recent submissions
            recent_apps = sorted(self.apps.values(), key=lambda a: a.created_at, reverse=True)[:10]
            
            dashboard["recent_submissions"] = [
                {
                    "app_id": app.id,
                    "app_name": app.name,
                    "category": app.category.value,
                    "status": app.status.value,
                    "submitted_at": app.created_at.isoformat()
                }
                for app in recent_apps
            ]
            
            # Revenue summary
            total_revenue = 0.0
            platform_revenue = 0.0
            
            for app in self.apps.values():
                if app.status == AppStatus.PUBLISHED:
                    installations = len([i for i in self.installations.values() if i.app_id == app.id])
                    
                    if app.pricing_model == PricingModel.ONE_TIME:
                        app_revenue = installations * app.price
                    elif app.pricing_model == PricingModel.SUBSCRIPTION:
                        app_revenue = installations * app.price
                    else:
                        app_revenue = 0.0
                    
                    total_revenue += app_revenue
                    
                    # Calculate platform share
                    revenue_share = next((rs for rs in self.revenue_shares.values() 
                                       if rs.app_id == app.id), None)
                    if revenue_share:
                        platform_revenue += app_revenue * (revenue_share.platform_percentage / 100)
            
            dashboard["revenue_summary"] = {
                "total_revenue": total_revenue,
                "platform_revenue": platform_revenue,
                "developer_revenue": total_revenue - platform_revenue
            }
            
            # Category statistics
            category_stats = defaultdict(lambda: {"apps": 0, "installations": 0})
            
            for app in self.apps.values():
                if app.status == AppStatus.PUBLISHED:
                    category_stats[app.category.value]["apps"] += 1
                    category_stats[app.category.value]["installations"] += len([i for i in self.installations.values() if i.app_id == app.id])
            
            dashboard["category_stats"] = dict(category_stats)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get marketplace dashboard: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_apps": len(self.apps),
            "total_reviews": len(self.reviews),
            "total_user_reviews": len(self.user_reviews),
            "total_installations": len(self.installations),
            "total_usage_records": len(self.usage),
            "total_developers": len(self.developers),
            "total_revenue_shares": len(self.revenue_shares),
            "app_categories": [c.value for c in AppCategory],
            "pricing_models": [p.value for p in PricingModel],
            "app_statuses": [s.value for s in AppStatus],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
MARKETPLACE_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "marketplace": {
        "review_required": True,
        "auto_approve_verified": False,
        "platform_fee_percentage": 30.0,
        "max_app_size": 104857600,  # 100MB
        "supported_categories": ["analytics", "security", "integration", "automation", "ai_ml", "productivity", "communication", "development", "business", "utilities"]
    },
    "analytics": {
        "usage_tracking_enabled": True,
        "retention_days": 365
    }
}


# Initialize marketplace manager
marketplace_manager = MarketplaceManager(MARKETPLACE_CONFIG)

# Export main components
__all__ = [
    'MarketplaceManager',
    'MarketplaceApp',
    'AppReview',
    'UserReview',
    'AppInstallation',
    'AppUsage',
    'Developer',
    'RevenueShare',
    'AppStatus',
    'AppCategory',
    'PricingModel',
    'ReviewStatus',
    'marketplace_manager'
]
