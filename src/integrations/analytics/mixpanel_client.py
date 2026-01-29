"""
Helm AI Mixpanel Integration
This module provides integration with Mixpanel for product analytics and user behavior tracking
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import time

logger = logging.getLogger(__name__)

class MixpanelClient:
    """Mixpanel API client for product analytics"""
    
    def __init__(self, token: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Mixpanel client
        
        Args:
            token: Mixpanel project token
            api_secret: Mixpanel API secret for data export
        """
        self.token = token or os.getenv('MIXPANEL_TOKEN')
        self.api_secret = api_secret or os.getenv('MIXPANEL_API_SECRET')
        
        if not self.token:
            raise ValueError("Mixpanel token is required")
        
        self.base_url = "https://api.mixpanel.com"
        self.import_url = "https://api.mixpanel.com/import"
        self.export_url = "https://data.mixpanel.com/api/2.0"
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Mixpanel API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Mixpanel API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # Event Tracking
    def track(self, 
              distinct_id: str,
              event_name: str,
              properties: Dict[str, Any] = None,
              time: int = None,
              ip: str = None,
              verbose: int = 0) -> Dict[str, Any]:
        """
        Track an event in Mixpanel
        
        Args:
            distinct_id: User identifier
            event_name: Name of the event
            properties: Event properties
            time: Event timestamp (Unix timestamp)
            ip: IP address for geolocation
            verbose: Verbose level
            
        Returns:
            Mixpanel API response
        """
        data = {
            "event": event_name,
            "properties": {
                "distinct_id": distinct_id,
                "token": self.token,
                **(properties or {})
            }
        }
        
        if time:
            data["properties"]["time"] = time
        
        if ip:
            data["properties"]["ip"] = ip
        
        if verbose:
            data["verbose"] = verbose
        
        return self._make_request('POST', '/track', json=[data])
    
    def track_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track multiple events in batch
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Mixpanel API response
        """
        # Add token to each event if not present
        for event in events:
            if 'properties' not in event:
                event['properties'] = {}
            event['properties']['token'] = self.token
        
        return self._make_request('POST', '/track', json=events)
    
    # User Profile Management
    def people_set(self, 
                   distinct_id: str,
                   properties: Dict[str, Any],
                   ip: str = None,
                   ignore_time: bool = False,
                   verbose: int = 0) -> Dict[str, Any]:
        """
        Set user profile properties
        
        Args:
            distinct_id: User identifier
            properties: User properties
            ip: IP address
            ignore_time: Whether to ignore timestamp
            verbose: Verbose level
            
        Returns:
            Mixpanel API response
        """
        data = {
            "$distinct_id": distinct_id,
            "$set": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if ignore_time:
            data["$ignore_time"] = True
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_set_once(self, 
                        distinct_id: str,
                        properties: Dict[str, Any],
                        ip: str = None,
                        verbose: int = 0) -> Dict[str, Any]:
        """Set user properties only if they don't exist"""
        data = {
            "$distinct_id": distinct_id,
            "$set_once": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_increment(self, 
                        distinct_id: str,
                        properties: Dict[str, Union[int, float]],
                        ip: str = None,
                        verbose: int = 0) -> Dict[str, Any]:
        """Increment numeric user properties"""
        data = {
            "$distinct_id": distinct_id,
            "$add": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_append(self, 
                     distinct_id: str,
                     properties: Dict[str, List[Any]],
                     ip: str = None,
                     verbose: int = 0) -> Dict[str, Any]:
        """Append values to list properties"""
        data = {
            "$distinct_id": distinct_id,
            "$append": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_union(self, 
                     distinct_id: str,
                     properties: Dict[str, List[Any]],
                     ip: str = None,
                     verbose: int = 0) -> Dict[str, Any]:
        """Union values with list properties"""
        data = {
            "$distinct_id": distinct_id,
            "$union": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_remove(self, 
                      distinct_id: str,
                      properties: Dict[str, Any],
                      ip: str = None,
                      verbose: int = 0) -> Dict[str, Any]:
        """Remove values from list properties"""
        data = {
            "$distinct_id": distinct_id,
            "$remove": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    def people_delete(self, 
                     distinct_id: str,
                     ip: str = None,
                     verbose: int = 0) -> Dict[str, Any]:
        """Delete user profile"""
        data = {
            "$distinct_id": distinct_id,
            "$delete": "",
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/engage', json=[data])
    
    # Group Analytics
    def group_set(self, 
                  group_key: str,
                  group_id: str,
                  properties: Dict[str, Any],
                  ip: str = None,
                  verbose: int = 0) -> Dict[str, Any]:
        """Set group properties"""
        data = {
            "$group_key": group_key,
            "$group_id": group_id,
            "$set": properties,
            "$token": self.token
        }
        
        if ip:
            data["$ip"] = ip
        
        if verbose:
            data["$verbose"] = verbose
        
        return self._make_request('POST', '/groups', json=[data])
    
    # Data Export
    def export_events(self, 
                     from_date: str,
                     to_date: str,
                     event: List[str] = None,
                     where: str = None,
                     bucket: str = None,
                     limit: int = None) -> List[Dict[str, Any]]:
        """
        Export raw event data
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            event: List of event names to filter
            where: SQL-like where clause
            bucket: Data bucket
            limit: Result limit
            
        Returns:
            List of event data
        """
        if not self.api_secret:
            raise ValueError("API secret is required for data export")
        
        params = {
            "from_date": from_date,
            "to_date": to_date
        }
        
        if event:
            params["event"] = json.dumps(event)
        
        if where:
            params["where"] = where
        
        if bucket:
            params["bucket"] = bucket
        
        if limit:
            params["limit"] = limit
        
        # Add API secret
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/export"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Mixpanel returns newline-delimited JSON
            events = []
            for line in response.text.strip().split('\n'):
                if line:
                    events.append(json.loads(line))
            
            return events
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to export events: {e}")
            raise
    
    def get_engagement(self, 
                      from_date: str,
                      to_date: str,
                      on: str = "user",
                      where: str = None) -> Dict[str, Any]:
        """Get engagement data"""
        if not self.api_secret:
            raise ValueError("API secret is required for engagement data")
        
        params = {
            "from_date": from_date,
            "to_date": to_date,
            "on": on
        }
        
        if where:
            params["where"] = where
        
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/engagement"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get engagement data: {e}")
            raise
    
    def get_funnel(self, 
                   events: List[str],
                   from_date: str,
                   to_date: str,
                   where: str = None) -> Dict[str, Any]:
        """Get funnel analysis"""
        if not self.api_secret:
            raise ValueError("API secret is required for funnel analysis")
        
        params = {
            "events": json.dumps(events),
            "from_date": from_date,
            "to_date": to_date
        }
        
        if where:
            params["where"] = where
        
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/funnel"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get funnel data: {e}")
            raise
    
    def get_retention(self, 
                     from_date: str,
                     to_date: str,
                     event: str,
                     born_event: str = None,
                     unit: str = "day",
                     n: int = None,
                     where: str = None) -> Dict[str, Any]:
        """Get retention analysis"""
        if not self.api_secret:
            raise ValueError("API secret is required for retention analysis")
        
        params = {
            "from_date": from_date,
            "to_date": to_date,
            "event": event,
            "unit": unit
        }
        
        if born_event:
            params["born_event"] = born_event
        
        if n:
            params["n"] = n
        
        if where:
            params["where"] = where
        
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/retention"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get retention data: {e}")
            raise
    
    def get_cohorts(self, 
                    from_date: str,
                    to_date: str,
                    on: str = "user",
                    unit: str = "day",
                    where: str = None) -> Dict[str, Any]:
        """Get cohort analysis"""
        if not self.api_secret:
            raise ValueError("API secret is required for cohort analysis")
        
        params = {
            "from_date": from_date,
            "to_date": to_date,
            "on": on,
            "unit": unit
        }
        
        if where:
            params["where"] = where
        
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/cohorts"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get cohort data: {e}")
            raise
    
    # Advanced Queries
    def query(self, 
              script: str,
              from_date: str,
              to_date: str) -> Dict[str, Any]:
        """Execute JQL query"""
        if not self.api_secret:
            raise ValueError("API secret is required for JQL queries")
        
        params = {
            "script": script,
            "from_date": from_date,
            "to_date": to_date
        }
        
        params["api_key"] = self.api_secret
        
        url = f"{self.export_url}/jql"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to execute JQL query: {e}")
            raise


# Helm AI specific Mixpanel operations
class HelmAIMixpanel:
    """Helm AI specific analytics operations using Mixpanel"""
    
    def __init__(self):
        self.mixpanel = MixpanelClient()
    
    def track_user_signup(self, 
                         user_id: str,
                         email: str,
                         plan: str,
                         signup_source: str = "web") -> Dict[str, Any]:
        """Track user signup event and create user profile"""
        # Track signup event
        event_properties = {
            "plan": plan,
            "signup_source": signup_source,
            "email_domain": email.split('@')[-1] if '@' in email else "unknown"
        }
        
        event_result = self.mixpanel.track(
            distinct_id=user_id,
            event_name="User Signed Up",
            properties=event_properties
        )
        
        # Create user profile
        user_properties = {
            "$email": email,
            "$name": email.split('@')[0] if '@' in email else user_id,
            "plan": plan,
            "signup_date": datetime.now().isoformat(),
            "signup_source": signup_source,
            "status": "active"
        }
        
        profile_result = self.mixpanel.people_set(
            distinct_id=user_id,
            properties=user_properties
        )
        
        return {
            "event": event_result,
            "profile": profile_result
        }
    
    def track_user_login(self, 
                        user_id: str,
                        login_method: str = "email",
                        success: bool = True) -> Dict[str, Any]:
        """Track user login event"""
        event_properties = {
            "login_method": login_method,
            "success": success
        }
        
        # Update last login in user profile
        if success:
            self.mixpanel.people_set(
                distinct_id=user_id,
                properties={"last_login": datetime.now().isoformat()}
            )
            
            # Increment login count
            self.mixpanel.people_increment(
                distinct_id=user_id,
                properties={"login_count": 1}
            )
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="User Logged In",
            properties=event_properties
        )
    
    def track_ai_model_interaction(self, 
                                  user_id: str,
                                  model_name: str,
                                  interaction_type: str,
                                  input_length: int,
                                  output_length: int,
                                  response_time: float,
                                  success: bool = True,
                                  error_message: str = None) -> Dict[str, Any]:
        """Track AI model interaction"""
        event_properties = {
            "model_name": model_name,
            "interaction_type": interaction_type,
            "input_length": input_length,
            "output_length": output_length,
            "total_tokens": input_length + output_length,
            "response_time_ms": int(response_time * 1000),
            "success": success
        }
        
        if error_message:
            event_properties["error_message"] = error_message
        
        # Update user profile with usage stats
        if success:
            self.mixpanel.people_increment(
                distinct_id=user_id,
                properties={
                    "total_interactions": 1,
                    "total_tokens": input_length + output_length
                }
            )
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="AI Model Interaction",
            properties=event_properties
        )
    
    def track_gaming_session(self, 
                           user_id: str,
                           game_title: str,
                           session_duration: int,
                           anti_cheat_detections: int = 0,
                           features_used: List[str] = None) -> Dict[str, Any]:
        """Track gaming session"""
        event_properties = {
            "game_title": game_title,
            "session_duration_seconds": session_duration,
            "anti_cheat_detections": anti_cheat_detections,
            "features_used": features_used or []
        }
        
        # Update user profile
        self.mixpanel.people_increment(
            distinct_id=user_id,
            properties={
                "total_sessions": 1,
                "total_gaming_time": session_duration
            }
        )
        
        # Add game to user's games list
        if game_title:
            self.mixpanel.people_union(
                distinct_id=user_id,
                properties={"games_played": [game_title]}
            )
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="Gaming Session",
            properties=event_properties
        )
    
    def track_subscription_change(self, 
                                  user_id: str,
                                  old_plan: str,
                                  new_plan: str,
                                  change_type: str) -> Dict[str, Any]:
        """Track subscription plan changes"""
        event_properties = {
            "old_plan": old_plan,
            "new_plan": new_plan,
            "change_type": change_type  # upgrade, downgrade, cancel
        }
        
        # Update user profile
        self.mixpanel.people_set(
            distinct_id=user_id,
            properties={
                "plan": new_plan,
                "plan_changed_date": datetime.now().isoformat()
            }
        )
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="Subscription Changed",
            properties=event_properties
        )
    
    def track_feature_adoption(self, 
                             user_id: str,
                             feature_name: str,
                             category: str = "general") -> Dict[str, Any]:
        """Track feature adoption"""
        event_properties = {
            "feature_name": feature_name,
            "category": category
        }
        
        # Add feature to user's adopted features
        self.mixpanel.people_union(
            distinct_id=user_id,
            properties={"features_used": [feature_name]}
        )
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="Feature Adopted",
            properties=event_properties
        )
    
    def track_user_engagement(self, 
                             user_id: str,
                             engagement_type: str,
                             duration: int = None,
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track user engagement metrics"""
        event_properties = {
            "engagement_type": engagement_type
        }
        
        if duration:
            event_properties["duration_seconds"] = duration
        
        if metadata:
            event_properties.update(metadata)
        
        return self.mixpanel.track(
            distinct_id=user_id,
            event_name="User Engagement",
            properties=event_properties
        )
    
    def get_user_lifecycle_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user lifecycle analytics"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            # Get engagement data
            engagement = self.mixpanel.get_engagement(
                from_date=start_date,
                to_date=end_date
            )
            
            # Get retention data
            retention = self.mixpanel.get_retention(
                from_date=start_date,
                to_date=end_date,
                event="User Logged In"
            )
            
            # Get cohort data
            cohorts = self.mixpanel.get_cohorts(
                from_date=start_date,
                to_date=end_date
            )
            
            return {
                "engagement": engagement,
                "retention": retention,
                "cohorts": cohorts,
                "period": f"Last {days} days"
            }
            
        except Exception as e:
            logger.error(f"Failed to get user lifecycle analytics: {e}")
            raise
    
    def get_product_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get product usage analytics"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            # Get AI model usage funnel
            model_funnel = self.mixpanel.get_funnel(
                events=["User Logged In", "AI Model Interaction", "Feature Adopted"],
                from_date=start_date,
                to_date=end_date
            )
            
            # Export raw events for detailed analysis
            ai_events = self.mixpanel.export_events(
                from_date=start_date,
                to_date=end_date,
                event=["AI Model Interaction"]
            )
            
            gaming_events = self.mixpanel.export_events(
                from_date=start_date,
                to_date=end_date,
                event=["Gaming Session"]
            )
            
            return {
                "model_funnel": model_funnel,
                "ai_events": ai_events[:1000],  # Limit to 1000 for performance
                "gaming_events": gaming_events[:1000],
                "period": f"Last {days} days"
            }
            
        except Exception as e:
            logger.error(f"Failed to get product usage analytics: {e}")
            raise
    
    def create_user_segments(self) -> Dict[str, Any]:
        """Create user segments based on behavior"""
        # This would typically be done in Mixpanel UI or via JQL
        # For now, return segment definitions
        
        segments = {
            "power_users": {
                "description": "Users with high engagement and feature adoption",
                "criteria": "total_interactions > 100 AND features_used.length > 5"
            },
            "new_users": {
                "description": "Users who signed up in the last 30 days",
                "criteria": "signup_date > 30 days ago"
            },
            "at_risk": {
                "description": "Users with declining engagement",
                "criteria": "last_login < 14 days ago AND total_interactions < 10"
            },
            "enterprise_users": {
                "description": "Users on enterprise plans",
                "criteria": "plan == 'enterprise'"
            }
        }
        
        return segments
    
    def export_user_data_for_compliance(self, user_id: str) -> Dict[str, Any]:
        """Export user data for GDPR/CCPA compliance"""
        try:
            # Get all events for this user
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            events = self.mixpanel.export_events(
                from_date=start_date,
                to_date=end_date,
                where=f'distinct_id == "{user_id}"'
            )
            
            return {
                "user_id": user_id,
                "events": events,
                "export_date": datetime.now().isoformat(),
                "total_events": len(events)
            }
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            raise
