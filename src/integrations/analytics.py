"""
Helm AI Analytics Integration Module
Integrates with Google Analytics and Mixpanel for business intelligence
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class UserProperties:
    """User properties for analytics"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    company: Optional[str] = None
    plan: Optional[str] = None
    signup_date: Optional[datetime] = None
    last_active: Optional[datetime] = None
    custom_properties: Optional[Dict[str, Any]] = None

class GoogleAnalyticsIntegration:
    """Google Analytics 4 Integration"""
    
    def __init__(self, measurement_id: str = None, api_secret: str = None):
        self.measurement_id = measurement_id or os.getenv('GA_MEASUREMENT_ID')
        self.api_secret = api_secret or os.getenv('GA_API_SECRET')
        self.base_url = f"https://www.google-analytics.com/mp/collect"
    
    def track_event(self, event: AnalyticsEvent, client_id: str) -> Dict[str, Any]:
        """Track event in Google Analytics"""
        try:
            # Prepare event data
            event_data = {
                'client_id': client_id,
                'events': [
                    {
                        'name': event.event_name,
                        'params': event.properties or {}
                    }
                ]
            }
            
            # Add user_id if available
            if event.user_id:
                event_data['user_id'] = event.user_id
            
            # Add timestamp
            if event.timestamp:
                event_data['timestamp_micros'] = int(event.timestamp.timestamp() * 1000000)
            
            # Make request
            params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret
            }
            
            response = requests.post(self.base_url, params=params, json=event_data)
            response.raise_for_status()
            
            logger.info(f"Tracked GA event: {event.event_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error tracking GA event: {str(e)}")
            raise
    
    def set_user_properties(self, user_properties: UserProperties, client_id: str) -> Dict[str, Any]:
        """Set user properties in Google Analytics"""
        try:
            # Prepare user properties data
            user_data = {
                'client_id': client_id,
                'user_properties': {}
            }
            
            # Add user_id if available
            if user_properties.user_id:
                user_data['user_id'] = user_properties.user_id
            
            # Add standard properties
            if user_properties.email:
                user_data['user_properties']['email'] = {'value': user_properties.email}
            
            if user_properties.name:
                user_data['user_properties']['name'] = {'value': user_properties.name}
            
            if user_properties.company:
                user_data['user_properties']['company'] = {'value': user_properties.company}
            
            if user_properties.plan:
                user_data['user_properties']['plan'] = {'value': user_properties.plan}
            
            if user_properties.signup_date:
                user_data['user_properties']['signup_date'] = {'value': user_properties.signup_date.isoformat()}
            
            if user_properties.last_active:
                user_data['user_properties']['last_active'] = {'value': user_properties.last_active.isoformat()}
            
            # Add custom properties
            if user_properties.custom_properties:
                for key, value in user_properties.custom_properties.items():
                    user_data['user_properties'][key] = {'value': str(value)}
            
            # Make request
            params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret
            }
            
            response = requests.post(self.base_url, params=params, json=user_data)
            response.raise_for_status()
            
            logger.info(f"Set GA user properties for: {user_properties.user_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error setting GA user properties: {str(e)}")
            raise
    
    def generate_client_id(self, user_data: Dict[str, Any]) -> str:
        """Generate consistent client ID for user"""
        # Create hash from user email or ID
        identifier = user_data.get('email') or user_data.get('id') or str(uuid.uuid4())
        return hashlib.md5(identifier.encode()).hexdigest()[:32]

class MixpanelIntegration:
    """Mixpanel Analytics Integration"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('MIXPANEL_TOKEN')
        self.base_url = "https://api.mixpanel.com"
    
    def track_event(self, event: AnalyticsEvent) -> Dict[str, Any]:
        """Track event in Mixpanel"""
        try:
            # Prepare event data
            event_data = {
                'event': event.event_name,
                'properties': {
                    'token': self.token,
                    'time': int(event.timestamp.timestamp()) if event.timestamp else int(datetime.now().timestamp()),
                    'distinct_id': event.user_id or event.session_id or 'anonymous',
                    'ip': event.ip_address,
                    '$user_agent': event.user_agent
                }
            }
            
            # Add custom properties
            if event.properties:
                event_data['properties'].update(event.properties)
            
            # Make request
            url = f"{self.base_url}/track"
            response = requests.post(url, json=[event_data])
            response.raise_for_status()
            
            logger.info(f"Tracked Mixpanel event: {event.event_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error tracking Mixpanel event: {str(e)}")
            raise
    
    def set_user_properties(self, user_properties: UserProperties) -> Dict[str, Any]:
        """Set user properties in Mixpanel"""
        try:
            # Prepare user properties data
            user_data = {
                '$token': self.token,
                '$distinct_id': user_properties.user_id,
                '$set': {}
            }
            
            # Add standard properties
            if user_properties.email:
                user_data['$set']['$email'] = user_properties.email
            
            if user_properties.name:
                user_data['$set']['$name'] = user_properties.name
            
            if user_properties.company:
                user_data['$set']['$company'] = user_properties.company
            
            if user_properties.plan:
                user_data['$set']['plan'] = user_properties.plan
            
            if user_properties.signup_date:
                user_data['$set']['$created'] = user_properties.signup_date.isoformat()
            
            if user_properties.last_active:
                user_data['$set']['$last_seen'] = user_properties.last_active.isoformat()
            
            # Add custom properties
            if user_properties.custom_properties:
                user_data['$set'].update(user_properties.custom_properties)
            
            # Make request
            url = f"{self.base_url}/engage"
            response = requests.post(url, json=[user_data])
            response.raise_for_status()
            
            logger.info(f"Set Mixpanel user properties for: {user_properties.user_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error setting Mixpanel user properties: {str(e)}")
            raise
    
    def create_alias(self, original_id: str, new_id: str) -> Dict[str, Any]:
        """Create alias for user identity merge"""
        try:
            alias_data = {
                'event': '$create_alias',
                'properties': {
                    'token': self.token,
                    'distinct_id': original_id,
                    'alias': new_id
                }
            }
            
            url = f"{self.base_url}/track"
            response = requests.post(url, json=[alias_data])
            response.raise_for_status()
            
            logger.info(f"Created Mixpanel alias: {original_id} -> {new_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Mixpanel alias: {str(e)}")
            raise

class AnalyticsManager:
    """Unified Analytics Manager"""
    
    def __init__(self):
        self.google_analytics = GoogleAnalyticsIntegration() if os.getenv('GA_MEASUREMENT_ID') else None
        self.mixpanel = MixpanelIntegration() if os.getenv('MIXPANEL_TOKEN') else None
        self.primary_service = os.getenv('PRIMARY_ANALYTICS_SERVICE', 'google_analytics')
    
    def track_event(self, event: AnalyticsEvent, client_id: str = None) -> bool:
        """Track event to primary analytics service"""
        try:
            success = True
            
            if self.primary_service == 'google_analytics' and self.google_analytics:
                if not client_id:
                    client_id = self.google_analytics.generate_client_id({'id': event.user_id})
                self.google_analytics.track_event(event, client_id)
            elif self.primary_service == 'mixpanel' and self.mixpanel:
                self.mixpanel.track_event(event)
            else:
                logger.warning(f"Primary analytics service '{self.primary_service}' not configured")
                success = False
            
            # Track to secondary service if configured
            if self.primary_service == 'google_analytics' and self.mixpanel:
                try:
                    self.mixpanel.track_event(event)
                except Exception as e:
                    logger.error(f"Failed to track to secondary service: {str(e)}")
            elif self.primary_service == 'mixpanel' and self.google_analytics:
                try:
                    if not client_id:
                        client_id = self.google_analytics.generate_client_id({'id': event.user_id})
                    self.google_analytics.track_event(event, client_id)
                except Exception as e:
                    logger.error(f"Failed to track to secondary service: {str(e)}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return False
    
    def set_user_properties(self, user_properties: UserProperties, client_id: str = None) -> bool:
        """Set user properties in primary analytics service"""
        try:
            success = True
            
            if self.primary_service == 'google_analytics' and self.google_analytics:
                if not client_id:
                    client_id = self.google_analytics.generate_client_id({'id': user_properties.user_id})
                self.google_analytics.set_user_properties(user_properties, client_id)
            elif self.primary_service == 'mixpanel' and self.mixpanel:
                self.mixpanel.set_user_properties(user_properties)
            else:
                logger.warning(f"Primary analytics service '{self.primary_service}' not configured")
                success = False
            
            # Set in secondary service if configured
            if self.primary_service == 'google_analytics' and self.mixpanel:
                try:
                    self.mixpanel.set_user_properties(user_properties)
                except Exception as e:
                    logger.error(f"Failed to set user properties in secondary service: {str(e)}")
            elif self.primary_service == 'mixpanel' and self.google_analytics:
                try:
                    if not client_id:
                        client_id = self.google_analytics.generate_client_id({'id': user_properties.user_id})
                    self.google_analytics.set_user_properties(user_properties, client_id)
                except Exception as e:
                    logger.error(f"Failed to set user properties in secondary service: {str(e)}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting user properties: {str(e)}")
            return False

# Predefined event types
ANALYTICS_EVENTS = {
    'user_signup': 'User Signup',
    'user_login': 'User Login',
    'user_logout': 'User Logout',
    'detection_started': 'Detection Started',
    'detection_completed': 'Detection Completed',
    'detection_failed': 'Detection Failed',
    'subscription_created': 'Subscription Created',
    'subscription_cancelled': 'Subscription Cancelled',
    'payment_successful': 'Payment Successful',
    'payment_failed': 'Payment Failed',
    'api_request': 'API Request',
    'dashboard_view': 'Dashboard View',
    'feature_used': 'Feature Used'
}

# Integration functions for Helm AI
def track_user_signup(user_data: Dict[str, Any]) -> bool:
    """Track user signup event"""
    try:
        analytics_manager = AnalyticsManager()
        
        event = AnalyticsEvent(
            event_name=ANALYTICS_EVENTS['user_signup'],
            user_id=user_data['id'],
            properties={
                'email': user_data['email'],
                'plan': user_data.get('plan', 'free'),
                'company': user_data.get('company'),
                'signup_source': user_data.get('source', 'direct')
            },
            timestamp=datetime.now()
        )
        
        # Set user properties
        user_properties = UserProperties(
            user_id=user_data['id'],
            email=user_data['email'],
            name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            company=user_data.get('company'),
            plan=user_data.get('plan', 'free'),
            signup_date=datetime.now(),
            custom_properties={
                'signup_source': user_data.get('source', 'direct'),
                'referral_code': user_data.get('referral_code')
            }
        )
        
        # Track event and set properties
        analytics_manager.track_event(event)
        analytics_manager.set_user_properties(user_properties)
        
        logger.info(f"Tracked signup event for user {user_data['id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to track user signup: {str(e)}")
        return False

def track_detection_event(user_id: str, detection_data: Dict[str, Any]) -> bool:
    """Track detection event"""
    try:
        analytics_manager = AnalyticsManager()
        
        event_name = ANALYTICS_EVENTS['detection_completed'] if detection_data.get('success') else ANALYTICS_EVENTS['detection_failed']
        
        event = AnalyticsEvent(
            event_name=event_name,
            user_id=user_id,
            properties={
                'detection_type': detection_data.get('type'),
                'game_type': detection_data.get('game_type'),
                'confidence_score': detection_data.get('confidence_score'),
                'processing_time': detection_data.get('processing_time'),
                'file_size': detection_data.get('file_size'),
                'success': detection_data.get('success', False)
            },
            timestamp=datetime.now()
        )
        
        analytics_manager.track_event(event)
        logger.info(f"Tracked detection event for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to track detection event: {str(e)}")
        return False

def track_subscription_event(user_id: str, subscription_data: Dict[str, Any]) -> bool:
    """Track subscription event"""
    try:
        analytics_manager = AnalyticsManager()
        
        event_name = ANALYTICS_EVENTS['subscription_created'] if subscription_data.get('action') == 'created' else ANALYTICS_EVENTS['subscription_cancelled']
        
        event = AnalyticsEvent(
            event_name=event_name,
            user_id=user_id,
            properties={
                'plan': subscription_data.get('plan'),
                'amount': subscription_data.get('amount'),
                'billing_cycle': subscription_data.get('billing_cycle'),
                'payment_method': subscription_data.get('payment_method')
            },
            timestamp=datetime.now()
        )
        
        analytics_manager.track_event(event)
        logger.info(f"Tracked subscription event for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to track subscription event: {str(e)}")
        return False

def track_api_request(user_id: str, request_data: Dict[str, Any]) -> bool:
    """Track API request event"""
    try:
        analytics_manager = AnalyticsManager()
        
        event = AnalyticsEvent(
            event_name=ANALYTICS_EVENTS['api_request'],
            user_id=user_id,
            properties={
                'endpoint': request_data.get('endpoint'),
                'method': request_data.get('method'),
                'status_code': request_data.get('status_code'),
                'response_time': request_data.get('response_time'),
                'user_agent': request_data.get('user_agent')
            },
            timestamp=datetime.now()
        )
        
        analytics_manager.track_event(event)
        logger.info(f"Tracked API request for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to track API request: {str(e)}")
        return False

def update_user_analytics(user_id: str, user_data: Dict[str, Any]) -> bool:
    """Update user analytics properties"""
    try:
        analytics_manager = AnalyticsManager()
        
        user_properties = UserProperties(
            user_id=user_id,
            email=user_data.get('email'),
            name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            company=user_data.get('company'),
            plan=user_data.get('plan'),
            last_active=datetime.now(),
            custom_properties={
                'total_detections': user_data.get('total_detections', 0),
                'last_detection_date': user_data.get('last_detection_date'),
                'api_calls_this_month': user_data.get('api_calls_this_month', 0),
                'subscription_status': user_data.get('subscription_status', 'active')
            }
        )
        
        analytics_manager.set_user_properties(user_properties)
        logger.info(f"Updated analytics for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update user analytics: {str(e)}")
        return False
