"""
Helm AI Marketplace Ecosystem
Provides comprehensive marketplace for apps, integrations, and third-party services
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

class AppStatus(Enum):
    """App status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"

class AppCategory(Enum):
    """App category enumeration"""
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    COLLABORATION = "collaboration"
    COMMUNICATION = "communication"
    CRM = "crm"
    DEVELOPMENT = "development"
    FINANCE = "finance"
    HR = "hr"
    INTEGRATION = "integration"
    MARKETING = "marketing"
    PRODUCTIVITY = "productivity"
    PROJECT_MANAGEMENT = "project_management"
    SECURITY = "security"
    SUPPORT = "support"
    UTILITIES = "utilities"
    CUSTOM = "custom"

class PricingModel(Enum):
    """Pricing model enumeration"""
    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class IntegrationType(Enum):
    """Integration type enumeration"""
    API = "api"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    NATIVE = "native"
    PLUGIN = "plugin"
    CONNECTOR = "connector"
    CUSTOM = "custom"

@dataclass
class MarketplaceApp:
    """Marketplace app definition"""
    app_id: str
    name: str
    description: str
    short_description: str
    category: AppCategory
    developer_id: str
    developer_name: str
    version: str
    status: AppStatus
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    icon_url: str
    screenshots: List[str]
    tags: Set[str]
    pricing: Dict[str, Any]
    features: List[str]
    requirements: List[str]
    documentation_url: str
    support_url: str
    privacy_policy_url: str
    terms_of_service_url: str
    installation_count: int
    rating_average: float
    rating_count: int
    reviews_count: int
    downloads_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert app to dictionary"""
        return {
            'app_id': self.app_id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'category': self.category.value,
            'developer_id': self.developer_id,
            'developer_name': self.developer_name,
            'version': self.version,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'icon_url': self.icon_url,
            'screenshots': self.screenshots,
            'tags': list(self.tags),
            'pricing': self.pricing,
            'features': self.features,
            'requirements': self.requirements,
            'documentation_url': self.documentation_url,
            'support_url': self.support_url,
            'privacy_policy_url': self.privacy_policy_url,
            'terms_of_service_url': self.terms_of_service_url,
            'installation_count': self.installation_count,
            'rating_average': self.rating_average,
            'rating_count': self.rating_count,
            'reviews_count': self.reviews_count,
            'downloads_count': self.downloads_count,
            'metadata': self.metadata
        }

@dataclass
class AppInstallation:
    """App installation record"""
    installation_id: str
    app_id: str
    tenant_id: str
    user_id: str
    installed_at: datetime
    updated_at: datetime
    status: str
    configuration: Dict[str, Any]
    usage_metrics: Dict[str, Any]
    last_used: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert installation to dictionary"""
        return {
            'installation_id': self.installation_id,
            'app_id': self.app_id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'installed_at': self.installed_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'configuration': self.configuration,
            'usage_metrics': self.usage_metrics,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'metadata': self.metadata
        }

@dataclass
class AppReview:
    """App review record"""
    review_id: str
    app_id: str
    user_id: str
    tenant_id: str
    rating: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    helpful_count: int
    verified: bool
    response: Optional[str]
    response_date: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert review to dictionary"""
        return {
            'review_id': self.review_id,
            'app_id': self.app_id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'helpful_count': self.helpful_count,
            'verified': self.verified,
            'response': self.response,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'metadata': self.metadata
        }

@dataclass
class Integration:
    """Integration definition"""
    integration_id: str
    name: str
    description: str
    type: IntegrationType
    provider: str
    category: AppCategory
    status: str
    created_at: datetime
    updated_at: datetime
    configuration_schema: Dict[str, Any]
    authentication_config: Dict[str, Any]
    endpoints: Dict[str, Any]
    webhooks: Dict[str, Any]
    documentation_url: str
    support_url: str
    icon_url: str
    tags: Set[str]
    usage_count: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert integration to dictionary"""
        return {
            'integration_id': self.integration_id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'provider': self.provider,
            'category': self.category.value,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'configuration_schema': self.configuration_schema,
            'authentication_config': self.authentication_config,
            'endpoints': self.endpoints,
            'webhooks': self.webhooks,
            'documentation_url': self.documentation_url,
            'support_url': self.support_url,
            'icon_url': self.icon_url,
            'tags': list(self.tags),
            'usage_count': self.usage_count,
            'metadata': self.metadata
        }

class MarketplaceManager:
    """Marketplace management system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.apps: Dict[str, MarketplaceApp] = {}
        self.app_installations: Dict[str, AppInstallation] = {}
        self.app_reviews: Dict[str, AppReview] = {}
        self.integrations: Dict[str, Integration] = {}
        self.developer_apps: Dict[str, Set[str]] = defaultdict(set)  # developer_id -> app_ids
        self.tenant_installations: Dict[str, Set[str]] = defaultdict(set)  # tenant_id -> installation_ids
        self.lock = threading.Lock()
        
        # Configuration
        self.max_app_screenshots = int(os.getenv('MAX_APP_SCREENSHOTS', '10'))
        self.review_approval_required = os.getenv('REVIEW_APPROVAL_REQUIRED', 'true').lower() == 'true'
        self.app_review_queue = deque()
        
        # Initialize default integrations
        self._initialize_default_integrations()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_integrations(self) -> None:
        """Initialize default integrations"""
        # Slack Integration
        slack_integration = Integration(
            integration_id="slack",
            name="Slack Integration",
            description="Connect Helm AI with Slack for notifications and commands",
            type=IntegrationType.API,
            provider="Slack",
            category=AppCategory.COMMUNICATION,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            configuration_schema={
                "workspace_id": {"type": "string", "required": True},
                "bot_token": {"type": "string", "required": True},
                "channels": {"type": "array", "required": False},
                "notifications": {"type": "object", "required": False}
            },
            authentication_config={
                "type": "oauth2",
                "scopes": ["channels:read", "chat:write", "users:read"],
                "auth_url": "https://slack.com/oauth/v2/authorize"
            },
            endpoints={
                "api_base": "https://slack.com/api/",
                "auth": "https://slack.com/api/auth.test",
                "channels": "https://slack.com/api/conversations.list",
                "messages": "https://slack.com/api/chat.postMessage"
            },
            webhooks={
                "events": "https://hooks.slack.com/services",
                "interactive": "https://hooks.slack.com/interactive"
            },
            documentation_url="https://api.slack.com/",
            support_url="https://slack.com/help",
            icon_url="/assets/integrations/slack.png",
            tags={"communication", "messaging", "team"},
            usage_count=0,
            metadata={}
        )
        
        # Salesforce Integration
        salesforce_integration = Integration(
            integration_id="salesforce",
            name="Salesforce Integration",
            description="Connect Helm AI with Salesforce for CRM automation",
            type=IntegrationType.API,
            provider="Salesforce",
            category=AppCategory.CRM,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            configuration_schema={
                "instance_url": {"type": "string", "required": True},
                "client_id": {"type": "string", "required": True},
                "client_secret": {"type": "string", "required": True},
                "username": {"type": "string", "required": True},
                "security_token": {"type": "string", "required": True}
            },
            authentication_config={
                "type": "oauth2",
                "scopes": ["api", "refresh_token", "offline_access"],
                "auth_url": "https://login.salesforce.com/services/oauth2/authorize"
            },
            endpoints={
                "api_base": "{instance_url}/services/data/v53.0/",
                "auth": "{instance_url}/services/oauth2/authorize",
                "objects": "{instance_url}/services/data/v53.0/sobjects/",
                "query": "{instance_url}/services/data/v53.0/query/"
            },
            webhooks={},
            documentation_url="https://developer.salesforce.com/docs",
            support_url="https://help.salesforce.com/",
            icon_url="/assets/integrations/salesforce.png",
            tags={"crm", "sales", "automation"},
            usage_count=0,
            metadata={}
        )
        
        # Google Analytics Integration
        ga_integration = Integration(
            integration_id="google_analytics",
            name="Google Analytics Integration",
            description="Connect Helm AI with Google Analytics for web analytics",
            type=IntegrationType.API,
            provider="Google",
            category=AppCategory.ANALYTICS,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            configuration_schema={
                "property_id": {"type": "string", "required": True},
                "service_account_key": {"type": "string", "required": True},
                "view_id": {"type": "string", "required": False}
            },
            authentication_config={
                "type": "service_account",
                "scopes": ["https://www.googleapis.com/auth/analytics.readonly"]
            },
            endpoints={
                "api_base": "https://analyticsreporting.googleapis.com/v4/",
                "reports": "https://analyticsreporting.googleapis.com/v4/reports",
                "metadata": "https://analyticsadmin.googleapis.com/v1alpha/"
            },
            webhooks={},
            documentation_url="https://developers.google.com/analytics/",
            support_url="https://support.google.com/analytics/",
            icon_url="/assets/integrations/google_analytics.png",
            tags={"analytics", "web", "metrics"},
            usage_count=0,
            metadata={}
        )
        
        # Add integrations to registry
        self.integrations[slack_integration.integration_id] = slack_integration
        self.integrations[salesforce_integration.integration_id] = salesforce_integration
        self.integrations[ga_integration.integration_id] = ga_integration
        
        logger.info(f"Initialized {len(self.integrations)} default integrations")
    
    def submit_app(self, developer_id: str, name: str, description: str, short_description: str,
                   category: AppCategory, version: str, icon_url: str, screenshots: List[str],
                   tags: Set[str], pricing: Dict[str, Any], features: List[str],
                   requirements: List[str], documentation_url: str, support_url: str,
                   privacy_policy_url: str, terms_of_service_url: str,
                   metadata: Optional[Dict[str, Any]] = None) -> MarketplaceApp:
        """Submit new app to marketplace"""
        app_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Validate screenshots
        if len(screenshots) > self.max_app_screenshots:
            raise ValueError(f"Maximum {self.max_app_screenshots} screenshots allowed")
        
        # Create app
        app = MarketplaceApp(
            app_id=app_id,
            name=name,
            description=description,
            short_description=short_description,
            category=category,
            developer_id=developer_id,
            developer_name="",  # Will be set from developer profile
            version=version,
            status=AppStatus.DRAFT,
            created_at=now,
            updated_at=now,
            published_at=None,
            icon_url=icon_url,
            screenshots=screenshots,
            tags=tags,
            pricing=pricing,
            features=features,
            requirements=requirements,
            documentation_url=documentation_url,
            support_url=support_url,
            privacy_policy_url=privacy_policy_url,
            terms_of_service_url=terms_of_service_url,
            installation_count=0,
            rating_average=0.0,
            rating_count=0,
            reviews_count=0,
            downloads_count=0,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.apps[app_id] = app
            self.developer_apps[developer_id].add(app_id)
        
        logger.info(f"Submitted app {app_id} ({name}) by developer {developer_id}")
        
        return app
    
    def submit_for_review(self, app_id: str) -> bool:
        """Submit app for review"""
        with self.lock:
            if app_id not in self.apps:
                return False
            
            app = self.apps[app_id]
            
            if app.status != AppStatus.DRAFT:
                return False
            
            app.status = AppStatus.PENDING_REVIEW
            app.updated_at = datetime.utcnow()
            
            # Add to review queue
            self.app_review_queue.append(app_id)
            
            logger.info(f"Submitted app {app_id} for review")
            
            return True
    
    def approve_app(self, app_id: str, reviewer_id: str) -> bool:
        """Approve app for publication"""
        with self.lock:
            if app_id not in self.apps:
                return False
            
            app = self.apps[app_id]
            
            if app.status != AppStatus.PENDING_REVIEW:
                return False
            
            app.status = AppStatus.APPROVED
            app.updated_at = datetime.utcnow()
            
            # Add review metadata
            app.metadata['review_approved_by'] = reviewer_id
            app.metadata['review_approved_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Approved app {app_id} by reviewer {reviewer_id}")
            
            return True
    
    def publish_app(self, app_id: str) -> bool:
        """Publish app to marketplace"""
        with self.lock:
            if app_id not in self.apps:
                return False
            
            app = self.apps[app_id]
            
            if app.status != AppStatus.APPROVED:
                return False
            
            app.status = AppStatus.PUBLISHED
            app.published_at = datetime.utcnow()
            app.updated_at = datetime.utcnow()
            
            logger.info(f"Published app {app_id} to marketplace")
            
            return True
    
    def reject_app(self, app_id: str, reason: str, reviewer_id: str) -> bool:
        """Reject app"""
        with self.lock:
            if app_id not in self.apps:
                return False
            
            app = self.apps[app_id]
            
            if app.status != AppStatus.PENDING_REVIEW:
                return False
            
            app.status = AppStatus.REJECTED
            app.updated_at = datetime.utcnow()
            
            # Add rejection metadata
            app.metadata['rejection_reason'] = reason
            app.metadata['rejection_by'] = reviewer_id
            app.metadata['rejection_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Rejected app {app_id}: {reason}")
            
            return True
    
    def install_app(self, app_id: str, tenant_id: str, user_id: str,
                   configuration: Optional[Dict[str, Any]] = None) -> AppInstallation:
        """Install app for tenant"""
        with self.lock:
            if app_id not in self.apps:
                raise ValueError(f"App {app_id} not found")
            
            app = self.apps[app_id]
            
            if app.status != AppStatus.PUBLISHED:
                raise ValueError(f"App {app_id} is not published")
            
            # Check if already installed
            existing_installation = next(
                (inst for inst in self.app_installations.values()
                 if inst.app_id == app_id and inst.tenant_id == tenant_id),
                None
            )
            
            if existing_installation:
                raise ValueError(f"App {app_id} already installed for tenant {tenant_id}")
            
            installation_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            installation = AppInstallation(
                installation_id=installation_id,
                app_id=app_id,
                tenant_id=tenant_id,
                user_id=user_id,
                installed_at=now,
                updated_at=now,
                status="active",
                configuration=configuration or {},
                usage_metrics={},
                last_used=now,
                metadata={}
            )
            
            self.app_installations[installation_id] = installation
            self.tenant_installations[tenant_id].add(installation_id)
            
            # Update app installation count
            app.installation_count += 1
            app.updated_at = now
            
            logger.info(f"Installed app {app_id} for tenant {tenant_id}")
            
            return installation
    
    def uninstall_app(self, installation_id: str) -> bool:
        """Uninstall app"""
        with self.lock:
            if installation_id not in self.app_installations:
                return False
            
            installation = self.app_installations[installation_id]
            app = self.apps.get(installation.app_id)
            
            # Update installation status
            installation.status = "uninstalled"
            installation.updated_at = datetime.utcnow()
            
            # Remove from tenant installations
            if installation.tenant_id in self.tenant_installations:
                self.tenant_installations[installation.tenant_id].discard(installation_id)
            
            # Update app installation count
            if app and app.installation_count > 0:
                app.installation_count -= 1
                app.updated_at = datetime.utcnow()
            
            logger.info(f"Uninstalled app {installation.app_id} (installation {installation_id})")
            
            return True
    
    def add_app_review(self, app_id: str, user_id: str, tenant_id: str, rating: int,
                      title: str, content: str, verified: bool = False) -> AppReview:
        """Add app review"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        with self.lock:
            if app_id not in self.apps:
                raise ValueError(f"App {app_id} not found")
            
            app = self.apps[app_id]
            
            review_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            review = AppReview(
                review_id=review_id,
                app_id=app_id,
                user_id=user_id,
                tenant_id=tenant_id,
                rating=rating,
                title=title,
                content=content,
                created_at=now,
                updated_at=now,
                helpful_count=0,
                verified=verified,
                response=None,
                response_date=None,
                metadata={}
            )
            
            self.app_reviews[review_id] = review
            
            # Update app rating
            self._update_app_rating(app_id)
            
            logger.info(f"Added review {review_id} for app {app_id}")
            
            return review
    
    def _update_app_rating(self, app_id: str) -> None:
        """Update app rating based on reviews"""
        if app_id not in self.apps:
            return
        
        app = self.apps[app_id]
        
        # Calculate average rating
        app_reviews = [r for r in self.app_reviews.values() if r.app_id == app_id]
        
        if app_reviews:
            total_rating = sum(r.rating for r in app_reviews)
            app.rating_average = round(total_rating / len(app_reviews), 2)
            app.rating_count = len(app_reviews)
            app.reviews_count = len(app_reviews)
        else:
            app.rating_average = 0.0
            app.rating_count = 0
            app.reviews_count = 0
        
        app.updated_at = datetime.utcnow()
    
    def get_apps_by_category(self, category: AppCategory, status: Optional[AppStatus] = None,
                           limit: Optional[int] = None, offset: Optional[int] = None) -> List[MarketplaceApp]:
        """Get apps by category"""
        with self.lock:
            apps = [app for app in self.apps.values() if app.category == category]
            
            if status:
                apps = [app for app in apps if app.status == status]
            
            # Sort by rating and downloads
            apps.sort(key=lambda x: (x.rating_average, x.downloads_count), reverse=True)
            
            # Apply pagination
            if offset:
                apps = apps[offset:]
            
            if limit:
                apps = apps[:limit]
            
            return apps
    
    def get_tenant_installations(self, tenant_id: str) -> List[AppInstallation]:
        """Get all installations for a tenant"""
        with self.lock:
            installation_ids = self.tenant_installations.get(tenant_id, set())
            return [self.app_installations[inst_id] for inst_id in installation_ids if inst_id in self.app_installations]
    
    def search_apps(self, query: str, category: Optional[AppCategory] = None,
                    tags: Optional[Set[str]] = None, limit: Optional[int] = None) -> List[MarketplaceApp]:
        """Search apps"""
        with self.lock:
            apps = list(self.apps.values())
            
            # Filter by status
            apps = [app for app in apps if app.status == AppStatus.PUBLISHED]
            
            # Filter by category
            if category:
                apps = [app for app in apps if app.category == category]
            
            # Filter by tags
            if tags:
                apps = [app for app in apps if tags.intersection(app.tags)]
            
            # Filter by query
            if query:
                query_lower = query.lower()
                apps = [app for app in apps if 
                        query_lower in app.name.lower() or 
                        query_lower in app.description.lower() or
                        query_lower in app.short_description.lower()]
            
            # Sort by relevance (rating, downloads, name match)
            apps.sort(key=lambda x: (
                x.rating_average,
                x.downloads_count,
                query_lower in x.name.lower() if query else False
            ), reverse=True)
            
            if limit:
                apps = apps[:limit]
            
            return apps
    
    def get_app_analytics(self, app_id: str) -> Dict[str, Any]:
        """Get app analytics"""
        with self.lock:
            if app_id not in self.apps:
                return {}
            
            app = self.apps[app_id]
            
            # Get installations
            installations = [inst for inst in self.app_installations.values() if inst.app_id == app_id]
            
            # Get reviews
            reviews = [review for review in self.app_reviews.values() if review.app_id == app_id]
            
            # Calculate metrics
            total_usage = sum(inst.usage_metrics.get('api_calls', 0) for inst in installations)
            active_installations = len([inst for inst in installations if inst.status == 'active'])
            
            return {
                'app_id': app_id,
                'name': app.name,
                'total_installations': len(installations),
                'active_installations': active_installations,
                'total_downloads': app.downloads_count,
                'total_usage': total_usage,
                'average_rating': app.rating_average,
                'total_reviews': len(reviews),
                'verified_reviews': len([r for r in reviews if r.verified]),
                'category': app.category.value,
                'pricing_model': app.pricing.get('model', 'unknown'),
                'created_at': app.created_at.isoformat(),
                'published_at': app.published_at.isoformat() if app.published_at else None
            }
    
    def get_marketplace_metrics(self) -> Dict[str, Any]:
        """Get marketplace metrics"""
        with self.lock:
            total_apps = len(self.apps)
            published_apps = len([app for app in self.apps.values() if app.status == AppStatus.PUBLISHED])
            pending_review = len([app for app in self.apps.values() if app.status == AppStatus.PENDING_REVIEW])
            
            # Category distribution
            category_distribution = defaultdict(int)
            for app in self.apps.values():
                category_distribution[app.category.value] += 1
            
            # Developer distribution
            developer_distribution = defaultdict(int)
            for developer_id, app_ids in self.developer_apps.items():
                developer_distribution[developer_id] = len(app_ids)
            
            # Installation metrics
            total_installations = len(self.app_installations)
            active_installations = len([inst for inst in self.app_installations.values() if inst.status == 'active'])
            
            # Review metrics
            total_reviews = len(self.app_reviews)
            average_rating = 0.0
            if total_reviews > 0:
                average_rating = sum(review.rating for review in self.app_reviews.values()) / total_reviews
            
            # Integration metrics
            total_integrations = len(self.integrations)
            active_integrations = len([integ for integ in self.integrations.values() if integ.status == 'active'])
            
            return {
                'total_apps': total_apps,
                'published_apps': published_apps,
                'pending_review': pending_review,
                'category_distribution': dict(category_distribution),
                'developer_distribution': dict(developer_distribution),
                'total_installations': total_installations,
                'active_installations': active_installations,
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 2),
                'total_integrations': total_integrations,
                'active_integrations': active_integrations,
                'review_queue_length': len(self.app_review_queue)
            }
    
    def _start_background_tasks(self) -> None:
        """Start background marketplace tasks"""
        # Start review processing thread
        review_thread = threading.Thread(target=self._process_reviews, daemon=True)
        review_thread.start()
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _process_reviews(self) -> None:
        """Process app review queue"""
        while True:
            try:
                if self.app_review_queue:
                    app_id = self.app_review_queue.popleft()
                    
                    # Auto-approve if not requiring approval
                    if not self.review_approval_required:
                        self.approve_app(app_id, "system_auto_approve")
                
                # Check every 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Review processing failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _collect_metrics(self) -> None:
        """Collect marketplace metrics"""
        while True:
            try:
                # Collect metrics every hour
                time.sleep(3600)
                
                metrics = self.get_marketplace_metrics()
                logger.info(f"Marketplace metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

# Global marketplace manager instance
marketplace_manager = MarketplaceManager()

# Export main components
__all__ = [
    'MarketplaceManager',
    'MarketplaceApp',
    'AppInstallation',
    'AppReview',
    'Integration',
    'AppStatus',
    'AppCategory',
    'PricingModel',
    'IntegrationType',
    'marketplace_manager'
]
