"""
Helm AI Analytics Manager
This module provides a unified interface for analytics tracking across multiple platforms
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from .google_analytics import GoogleAnalyticsClient, HelmAIAnalytics as GoogleAnalytics
from .mixpanel_client import MixpanelClient, HelmAIMixpanel as MixpanelAnalytics

logger = logging.getLogger(__name__)

class AnalyticsProvider(Enum):
    """Supported analytics providers"""
    GOOGLE_ANALYTICS = "google_analytics"
    MIXPANEL = "mixpanel"

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_name: str
    user_id: str
    client_id: str
    properties: Dict[str, Any] = None
    user_properties: Dict[str, Any] = None
    timestamp: Optional[datetime] = None

@dataclass
class UserProperties:
    """User properties data structure"""
    user_id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    plan: str = "free"
    signup_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    company: str = ""
    job_title: str = ""
    custom_properties: Dict[str, Any] = None

@dataclass
class FunnelStep:
    """Funnel step data structure"""
    event_name: str
    description: str
    required: bool = True

class AnalyticsManager:
    """Unified analytics manager supporting multiple providers"""
    
    def __init__(self, primary_provider: AnalyticsProvider = AnalyticsProvider.MIXPANEL):
        """
        Initialize analytics manager
        
        Args:
            primary_provider: Primary analytics provider to use
        """
        self.primary_provider = primary_provider
        self.providers = {}
        
        # Initialize primary provider
        self._initialize_provider(primary_provider)
        
        # Initialize secondary provider if configured
        if primary_provider == AnalyticsProvider.MIXPANEL:
            if os.getenv('GA4_MEASUREMENT_ID') and os.getenv('GA4_API_SECRET'):
                self._initialize_provider(AnalyticsProvider.GOOGLE_ANALYTICS)
        else:
            if os.getenv('MIXPANEL_TOKEN'):
                self._initialize_provider(AnalyticsProvider.MIXPANEL)
    
    def _initialize_provider(self, provider: AnalyticsProvider):
        """Initialize a specific analytics provider"""
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                self.providers[provider] = GoogleAnalytics()
                logger.info("Google Analytics provider initialized successfully")
            elif provider == AnalyticsProvider.MIXPANEL:
                self.providers[provider] = MixpanelAnalytics()
                logger.info("Mixpanel provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {provider.value}: {e}")
            raise
    
    def track_event(self, event: AnalyticsEvent, provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track analytics event
        
        Args:
            event: Event data
            provider: Specific provider to use (defaults to primary)
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_event(
                    client_id=event.client_id,
                    event_name=event.event_name,
                    event_parameters=event.properties,
                    user_properties=event.user_properties,
                    user_id=event.user_id,
                    timestamp_micros=int(event.timestamp.timestamp() * 1000000) if event.timestamp else None
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.mixpanel.track(
                    distinct_id=event.user_id,
                    event_name=event.event_name,
                    properties=event.properties
                )
                
        except Exception as e:
            logger.error(f"Failed to track event via {provider.value}: {e}")
            raise
    
    def track_user_signup(self, 
                         user_properties: UserProperties,
                         signup_source: str = "web",
                         provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track user signup event
        
        Args:
            user_properties: User data
            signup_source: Signup source
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_user_signup(
                    client_id=user_properties.user_id,
                    user_id=user_properties.user_id,
                    method=signup_source,
                    plan=user_properties.plan,
                    user_properties={
                        "user_type": user_properties.plan,
                        "signup_source": signup_source
                    }
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_user_signup(
                    user_id=user_properties.user_id,
                    email=user_properties.email,
                    plan=user_properties.plan,
                    signup_source=signup_source
                )
                
        except Exception as e:
            logger.error(f"Failed to track user signup via {provider.value}: {e}")
            raise
    
    def track_user_login(self, 
                        user_id: str,
                        client_id: str,
                        login_method: str = "email",
                        success: bool = True,
                        provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track user login event
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            login_method: Login method
            success: Whether login was successful
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_user_login(
                    client_id=client_id,
                    user_id=user_id,
                    method=login_method,
                    user_properties={"login_method": login_method}
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_user_login(
                    user_id=user_id,
                    login_method=login_method,
                    success=success
                )
                
        except Exception as e:
            logger.error(f"Failed to track user login via {provider.value}: {e}")
            raise
    
    def track_ai_model_usage(self, 
                            user_id: str,
                            client_id: str,
                            model_name: str,
                            input_tokens: int,
                            output_tokens: int,
                            processing_time: float,
                            success: bool = True,
                            error_message: str = None,
                            provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track AI model usage
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            model_name: Name of the AI model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            processing_time: Processing time in seconds
            success: Whether the request was successful
            error_message: Error message if failed
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_ai_model_usage(
                    client_id=client_id,
                    user_id=user_id,
                    model_name=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    processing_time=processing_time,
                    user_properties={"model_usage": "active"}
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_ai_model_interaction(
                    user_id=user_id,
                    model_name=model_name,
                    interaction_type="inference",
                    input_length=input_tokens,
                    output_length=output_tokens,
                    response_time=processing_time,
                    success=success,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Failed to track AI model usage via {provider.value}: {e}")
            raise
    
    def track_gaming_session(self, 
                           user_id: str,
                           client_id: str,
                           game_title: str,
                           session_duration: int,
                           anti_cheat_detections: int = 0,
                           features_used: List[str] = None,
                           provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track gaming session
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            game_title: Title of the game
            session_duration: Session duration in seconds
            anti_cheat_detections: Number of anti-cheat detections
            features_used: List of features used
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_gaming_session(
                    client_id=client_id,
                    user_id=user_id,
                    game_title=game_title,
                    session_duration=session_duration,
                    anti_cheat_detections=anti_cheat_detections,
                    user_properties={"gaming_active": "true"}
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_gaming_session(
                    user_id=user_id,
                    game_title=game_title,
                    session_duration=session_duration,
                    anti_cheat_detections=anti_cheat_detections,
                    features_used=features_used
                )
                
        except Exception as e:
            logger.error(f"Failed to track gaming session via {provider.value}: {e}")
            raise
    
    def track_subscription_change(self, 
                                  user_id: str,
                                  client_id: str,
                                  old_plan: str,
                                  new_plan: str,
                                  change_type: str,
                                  value: float = 0.0,
                                  provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track subscription change
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            old_plan: Previous plan
            new_plan: New plan
            change_type: Type of change (upgrade, downgrade, cancel)
            value: Monetary value
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                if change_type == "cancel":
                    return analytics_client.ga.track_event(
                        client_id=client_id,
                        user_id=user_id,
                        event_name="subscription_cancelled",
                        event_parameters={
                            "old_plan": old_plan,
                            "change_type": change_type
                        }
                    )
                else:
                    return analytics_client.ga.track_subscription(
                        client_id=client_id,
                        user_id=user_id,
                        plan=new_plan,
                        value=value
                    )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_subscription_change(
                    user_id=user_id,
                    old_plan=old_plan,
                    new_plan=new_plan,
                    change_type=change_type
                )
                
        except Exception as e:
            logger.error(f"Failed to track subscription change via {provider.value}: {e}")
            raise
    
    def track_feature_adoption(self, 
                             user_id: str,
                             client_id: str,
                             feature_name: str,
                             category: str = "general",
                             provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track feature adoption
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            feature_name: Name of the feature
            category: Feature category
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_event(
                    client_id=client_id,
                    user_id=user_id,
                    event_name="feature_adoption",
                    event_parameters={
                        "feature_name": feature_name,
                        "category": category
                    }
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.track_feature_adoption(
                    user_id=user_id,
                    feature_name=feature_name,
                    category=category
                )
                
        except Exception as e:
            logger.error(f"Failed to track feature adoption via {provider.value}: {e}")
            raise
    
    def get_user_analytics(self, 
                          user_id: str,
                          days: int = 30,
                          provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Get analytics data for specific user
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            provider: Specific provider to use
            
        Returns:
            User analytics data
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.export_user_data_for_compliance(user_id)
            
            elif provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                # GA4 doesn't have direct user export, would need to use Data API
                return {
                    "user_id": user_id,
                    "provider": "google_analytics",
                    "message": "User-level analytics require Data API setup",
                    "period": f"Last {days} days"
                }
                
        except Exception as e:
            logger.error(f"Failed to get user analytics from {provider.value}: {e}")
            raise
    
    def get_product_analytics(self, 
                             days: int = 30,
                             provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Get product-level analytics
        
        Args:
            days: Number of days to look back
            provider: Specific provider to use
            
        Returns:
            Product analytics data
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.get_comprehensive_analytics(days)
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.get_product_usage_analytics(days)
                
        except Exception as e:
            logger.error(f"Failed to get product analytics from {provider.value}: {e}")
            raise
    
    def create_funnel_analysis(self, 
                              funnel_steps: List[FunnelStep],
                              days: int = 30,
                              provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Create funnel analysis
        
        Args:
            funnel_steps: List of funnel steps
            days: Number of days to analyze
            provider: Specific provider to use
            
        Returns:
            Funnel analysis data
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.MIXPANEL:
                event_names = [step.event_name for step in funnel_steps]
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                return analytics_client.mixpanel.get_funnel(
                    events=event_names,
                    from_date=start_date,
                    to_date=end_date
                )
            
            elif provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                # GA4 funnel analysis would be done through exploration reports
                return {
                    "provider": "google_analytics",
                    "message": "Funnel analysis requires GA4 Exploration setup",
                    "funnel_steps": [step.event_name for step in funnel_steps],
                    "period": f"Last {days} days"
                }
                
        except Exception as e:
            logger.error(f"Failed to create funnel analysis with {provider.value}: {e}")
            raise
    
    def track_page_view(self, 
                       user_id: str,
                       client_id: str,
                       page_location: str,
                       page_title: str = None,
                       provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Track page view
        
        Args:
            user_id: User identifier
            client_id: Client identifier (for GA4)
            page_location: Page URL
            page_title: Page title
            provider: Specific provider to use
            
        Returns:
            Track result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                return analytics_client.ga.track_page_view(
                    client_id=client_id,
                    page_location=page_location,
                    page_title=page_title,
                    user_id=user_id
                )
            
            elif provider == AnalyticsProvider.MIXPANEL:
                return analytics_client.mixpanel.track(
                    distinct_id=user_id,
                    event_name="Page View",
                    properties={
                        "page_location": page_location,
                        "page_title": page_title
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to track page view via {provider.value}: {e}")
            raise
    
    def update_user_properties(self, 
                              user_properties: UserProperties,
                              provider: Optional[AnalyticsProvider] = None) -> Dict[str, Any]:
        """
        Update user properties
        
        Args:
            user_properties: User properties data
            provider: Specific provider to use
            
        Returns:
            Update result
        """
        provider = provider or self.primary_provider
        analytics_client = self.providers.get(provider)
        
        if not analytics_client:
            raise ValueError(f"Analytics provider {provider.value} not initialized")
        
        try:
            if provider == AnalyticsProvider.MIXPANEL:
                properties = {
                    "$email": user_properties.email,
                    "$name": f"{user_properties.first_name} {user_properties.last_name}".strip(),
                    "plan": user_properties.plan,
                    "company": user_properties.company,
                    "job_title": user_properties.job_title
                }
                
                if user_properties.signup_date:
                    properties["signup_date"] = user_properties.signup_date.isoformat()
                
                if user_properties.last_login:
                    properties["last_login"] = user_properties.last_login.isoformat()
                
                if user_properties.custom_properties:
                    properties.update(user_properties.custom_properties)
                
                return analytics_client.mixpanel.people_set(
                    distinct_id=user_properties.user_id,
                    properties=properties
                )
            
            elif provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                # GA4 user properties are sent with events
                return {
                    "provider": "google_analytics",
                    "message": "User properties updated with next event",
                    "user_id": user_properties.user_id
                }
                
        except Exception as e:
            logger.error(f"Failed to update user properties via {provider.value}: {e}")
            raise
    
    def sync_data_between_providers(self, 
                                  user_id: str,
                                  event_data: List[Dict[str, Any]],
                                  source_provider: AnalyticsProvider,
                                  target_provider: AnalyticsProvider) -> Dict[str, Any]:
        """
        Sync analytics data between providers
        
        Args:
            user_id: User identifier
            event_data: Event data to sync
            source_provider: Source analytics provider
            target_provider: Target analytics provider
            
        Returns:
            Sync result
        """
        try:
            synced_events = []
            
            for event in event_data:
                analytics_event = AnalyticsEvent(
                    event_name=event.get('event_name', 'unknown'),
                    user_id=user_id,
                    client_id=user_id,  # Use user_id as client_id for GA4
                    properties=event.get('properties', {}),
                    user_properties=event.get('user_properties', {})
                )
                
                result = self.track_event(analytics_event, target_provider)
                synced_events.append(result)
            
            return {
                "source_provider": source_provider.value,
                "target_provider": target_provider.value,
                "user_id": user_id,
                "synced_events": len(synced_events),
                "results": synced_events
            }
            
        except Exception as e:
            logger.error(f"Failed to sync data between providers: {e}")
            raise


# Singleton instance for easy access
analytics_manager = AnalyticsManager()
