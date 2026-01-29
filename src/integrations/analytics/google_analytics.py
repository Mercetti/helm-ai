"""
Helm AI Google Analytics Integration
This module provides integration with Google Analytics 4 for business intelligence
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class GoogleAnalyticsClient:
    """Google Analytics 4 API client"""
    
    def __init__(self, 
                 measurement_id: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 service_account_key: Optional[str] = None):
        """
        Initialize Google Analytics client
        
        Args:
            measurement_id: GA4 Measurement ID
            api_secret: GA4 API Secret for data collection
            service_account_key: Path to service account key file for Data API
        """
        self.measurement_id = measurement_id or os.getenv('GA4_MEASUREMENT_ID')
        self.api_secret = api_secret or os.getenv('GA4_API_SECRET')
        self.service_account_key = service_account_key or os.getenv('GA4_SERVICE_ACCOUNT_KEY')
        
        if not self.measurement_id or not self.api_secret:
            raise ValueError("GA4 Measurement ID and API Secret are required")
        
        self.base_url = "https://www.google-analytics.com/mp/collect"
        self.data_api_url = "https://analyticsdata.googleapis.com/v1beta"
        
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
        
        # Setup authentication for Data API
        self.access_token = None
        if self.service_account_key:
            self._authenticate_service_account()
    
    def _authenticate_service_account(self):
        """Authenticate using service account for Data API access"""
        try:
            # Load service account key
            with open(self.service_account_key, 'r') as f:
                service_account = json.load(f)
            
            # Get access token
            auth_url = "https://oauth2.googleapis.com/token"
            data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': self._generate_jwt(service_account)
            }
            
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data['access_token']
            
        except Exception as e:
            logger.error(f"Failed to authenticate service account: {e}")
            raise
    
    def _generate_jwt(self, service_account: Dict[str, Any]) -> str:
        """Generate JWT for service account authentication"""
        import jwt
        import time
        
        now = int(time.time())
        exp = now + 3600  # 1 hour expiration
        
        payload = {
            'iss': service_account['client_email'],
            'scope': 'https://www.googleapis.com/auth/analytics.readonly',
            'aud': 'https://oauth2.googleapis.com/token',
            'exp': exp,
            'iat': now
        }
        
        # Load private key
        private_key = service_account['private_key']
        
        return jwt.encode(payload, private_key, algorithm='RS256')
    
    # Event Tracking
    def track_event(self, 
                   client_id: str,
                   event_name: str,
                   event_parameters: Dict[str, Any] = None,
                   user_properties: Dict[str, Any] = None,
                   user_id: str = None,
                   timestamp_micros: int = None) -> Dict[str, Any]:
        """
        Track custom event in GA4
        
        Args:
            client_id: Client identifier
            event_name: Name of the event
            event_parameters: Event parameters
            user_properties: User properties
            user_id: User identifier
            timestamp_micros: Event timestamp in microseconds
            
        Returns:
            GA4 API response
        """
        data = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_name,
                    "parameters": event_parameters or {}
                }
            ]
        }
        
        if user_id:
            data["user_id"] = user_id
        
        if user_properties:
            data["user_properties"] = {
                key: {"value": str(value)} for key, value in user_properties.items()
            }
        
        if timestamp_micros:
            data["events"][0]["timestamp_micros"] = timestamp_micros
        
        url = f"{self.base_url}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to track event: {e}")
            raise
    
    def track_page_view(self, 
                       client_id: str,
                       page_location: str,
                       page_title: str = None,
                       user_id: str = None,
                       user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track page view event"""
        event_parameters = {
            "page_location": page_location,
            "page_referrer": "https://helm-ai.com"
        }
        
        if page_title:
            event_parameters["page_title"] = page_title
        
        return self.track_event(
            client_id=client_id,
            event_name="page_view",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_user_signup(self, 
                         client_id: str,
                         user_id: str,
                         method: str = "email",
                         plan: str = "free",
                         user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track user signup event"""
        event_parameters = {
            "method": method,
            "plan": plan
        }
        
        return self.track_event(
            client_id=client_id,
            event_name="sign_up",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_user_login(self, 
                        client_id: str,
                        user_id: str,
                        method: str = "email",
                        user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track user login event"""
        event_parameters = {
            "method": method
        }
        
        return self.track_event(
            client_id=client_id,
            event_name="login",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_ai_model_usage(self, 
                            client_id: str,
                            user_id: str,
                            model_name: str,
                            input_tokens: int,
                            output_tokens: int,
                            processing_time: float,
                            user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track AI model usage event"""
        event_parameters = {
            "model_name": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "processing_time_ms": int(processing_time * 1000),
            "tokens_per_second": int((input_tokens + output_tokens) / processing_time) if processing_time > 0 else 0
        }
        
        return self.track_event(
            client_id=client_id,
            event_name="ai_model_usage",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_gaming_session(self, 
                           client_id: str,
                           user_id: str,
                           game_title: str,
                           session_duration: int,
                           anti_cheat_detections: int = 0,
                           user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track gaming session event"""
        event_parameters = {
            "game_title": game_title,
            "session_duration_seconds": session_duration,
            "anti_cheat_detections": anti_cheat_detections
        }
        
        return self.track_event(
            client_id=client_id,
            event_name="gaming_session",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_purchase(self, 
                      client_id: str,
                      user_id: str,
                      transaction_id: str,
                      value: float,
                      currency: str = "USD",
                      items: List[Dict[str, Any]] = None,
                      user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track purchase event"""
        event_parameters = {
            "transaction_id": transaction_id,
            "value": value,
            "currency": currency
        }
        
        if items:
            event_parameters["items"] = items
        
        return self.track_event(
            client_id=client_id,
            event_name="purchase",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    def track_subscription(self, 
                          client_id: str,
                          user_id: str,
                          plan: str,
                          value: float,
                          currency: str = "USD",
                          user_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track subscription event"""
        event_parameters = {
            "plan": plan,
            "value": value,
            "currency": currency
        }
        
        return self.track_event(
            client_id=client_id,
            event_name="subscription",
            event_parameters=event_parameters,
            user_id=user_id,
            user_properties=user_properties
        )
    
    # Data API (Analytics Data)
    def run_report(self, 
                   property_id: str,
                   dimensions: List[Dict[str, str]],
                   metrics: List[Dict[str, str]],
                   date_ranges: List[Dict[str, str]] = None,
                   dimension_filters: List[Dict[str, Any]] = None,
                   metric_filters: List[Dict[str, Any]] = None,
                   order_bys: List[Dict[str, Any]] = None,
                   limit: int = 10000) -> Dict[str, Any]:
        """
        Run a report using GA4 Data API
        
        Args:
            property_id: GA4 Property ID
            dimensions: List of dimensions
            metrics: List of metrics
            date_ranges: List of date ranges
            dimension_filters: Dimension filters
            metric_filters: Metric filters
            order_bys: Order by specifications
            limit: Result limit
            
        Returns:
            Report data
        """
        if not self.access_token:
            raise ValueError("Service account authentication required for Data API")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "dimensions": dimensions,
            "metrics": metrics,
            "limit": limit
        }
        
        if date_ranges:
            data["dateRanges"] = date_ranges
        else:
            # Default to last 30 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            data["dateRanges"] = [{"startDate": start_date, "endDate": end_date}]
        
        if dimension_filters:
            data["dimensionFilter"] = {"andGroup": {"expressions": dimension_filters}}
        
        if metric_filters:
            data["metricFilter"] = {"andGroup": {"expressions": metric_filters}}
        
        if order_bys:
            data["orderBys"] = order_bys
        
        url = f"{self.data_api_url}/properties/{property_id}:runReport"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to run report: {e}")
            raise
    
    def get_user_acquisition_report(self, property_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user acquisition report"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        dimensions = [
            {"name": "sessionSource"},
            {"name": "sessionMedium"},
            {"name": "sessionCampaign"}
        ]
        
        metrics = [
            {"name": "activeUsers"},
            {"name": "sessions"},
            {"name": "newUsers"}
        ]
        
        date_ranges = [{"startDate": start_date, "endDate": end_date}]
        
        return self.run_report(
            property_id=property_id,
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=date_ranges
        )
    
    def get_engagement_report(self, property_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user engagement report"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        dimensions = [
            {"name": "date"},
            {"name": "pageTitle"}
        ]
        
        metrics = [
            {"name": "activeUsers"},
            {"name": "screenPageViews"},
            {"name": "engagementDuration"},
            {"name": "engagedSessions"}
        ]
        
        date_ranges = [{"startDate": start_date, "endDate": end_date}]
        
        return self.run_report(
            property_id=property_id,
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=date_ranges
        )
    
    def get_conversion_report(self, property_id: str, days: int = 30) -> Dict[str, Any]:
        """Get conversion report"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        dimensions = [
            {"name": "eventName"},
            {"name": "date"}
        ]
        
        metrics = [
            {"name": "eventCount"},
            {"name": "conversions"}
        ]
        
        date_ranges = [{"startDate": start_date, "endDate": end_date}]
        
        # Filter for conversion events
        dimension_filters = [
            {
                "fieldName": "eventName",
                "stringFilter": {
                    "matchType": "CONTAINS",
                    "value": "purchase"
                }
            }
        ]
        
        return self.run_report(
            property_id=property_id,
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=date_ranges,
            dimension_filters=dimension_filters
        )
    
    def get_realtime_data(self, property_id: str) -> Dict[str, Any]:
        """Get realtime user data"""
        if not self.access_token:
            raise ValueError("Service account authentication required for Data API")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        dimensions = [
            {"name": "country"},
            {"name": "city"},
            {"name": "pageTitle"}
        ]
        
        metrics = [
            {"name": "activeUsers"}
        ]
        
        data = {
            "dimensions": dimensions,
            "metrics": metrics
        }
        
        url = f"{self.data_api_url}/properties/{property_id}:runRealtimeReport"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get realtime data: {e}")
            raise
    
    def create_audience(self, 
                       property_id: str,
                       display_name: str,
                       description: str,
                       filter_clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create custom audience"""
        if not self.access_token:
            raise ValueError("Service account authentication required for Data API")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "displayName": display_name,
            "description": description,
            "filterClauses": filter_clauses
        }
        
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/audiences"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create audience: {e}")
            raise


# Helm AI specific analytics operations
class HelmAIAnalytics:
    """Helm AI specific analytics operations using Google Analytics"""
    
    def __init__(self):
        self.ga = GoogleAnalyticsClient()
        self.property_id = os.getenv('GA4_PROPERTY_ID')
    
    def track_user_journey(self, 
                          client_id: str,
                          user_id: str,
                          events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track complete user journey with multiple events"""
        results = []
        
        for event in events:
            try:
                result = self.ga.track_event(
                    client_id=client_id,
                    user_id=user_id,
                    event_name=event['name'],
                    event_parameters=event.get('parameters', {}),
                    user_properties=event.get('user_properties', {})
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to track event {event['name']}: {e}")
                results.append({"error": str(e)})
        
        return results
    
    def track_ai_model_performance(self, 
                                  model_name: str,
                                  performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Track AI model performance metrics"""
        # Use a system client_id for model performance tracking
        client_id = f"model_{model_name}"
        
        event_parameters = {
            "model_name": model_name,
            "avg_response_time_ms": performance_metrics.get('avg_response_time', 0),
            "success_rate": performance_metrics.get('success_rate', 0),
            "error_rate": performance_metrics.get('error_rate', 0),
            "total_requests": performance_metrics.get('total_requests', 0),
            "cache_hit_rate": performance_metrics.get('cache_hit_rate', 0)
        }
        
        return self.ga.track_event(
            client_id=client_id,
            event_name="model_performance",
            event_parameters=event_parameters
        )
    
    def track_business_metrics(self, 
                              metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Track business-level metrics"""
        client_id = "business_metrics"
        
        event_parameters = {
            "daily_active_users": metrics.get('daily_active_users', 0),
            "monthly_active_users": metrics.get('monthly_active_users', 0),
            "new_signups": metrics.get('new_signups', 0),
            "revenue": metrics.get('revenue', 0),
            "conversion_rate": metrics.get('conversion_rate', 0),
            "churn_rate": metrics.get('churn_rate', 0)
        }
        
        return self.ga.track_event(
            client_id=client_id,
            event_name="business_metrics",
            event_parameters=event_parameters
        )
    
    def get_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        if not self.property_id:
            raise ValueError("GA4 Property ID is required")
        
        try:
            # Get user acquisition data
            acquisition = self.ga.get_user_acquisition_report(self.property_id, days)
            
            # Get engagement data
            engagement = self.ga.get_engagement_report(self.property_id, days)
            
            # Get conversion data
            conversions = self.ga.get_conversion_report(self.property_id, days)
            
            # Get realtime data
            realtime = self.ga.get_realtime_data(self.property_id)
            
            return {
                "acquisition": acquisition,
                "engagement": engagement,
                "conversions": conversions,
                "realtime": realtime,
                "period": f"Last {days} days"
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive analytics: {e}")
            raise
    
    def create_user_segments(self) -> Dict[str, Any]:
        """Create predefined user segments"""
        if not self.property_id:
            raise ValueError("GA4 Property ID is required")
        
        segments = {}
        
        try:
            # Power users segment
            power_users_filter = [
                {
                    "dimensionFilter": {
                        "fieldName": "sessionCount",
                        "numericFilter": {
                            "operation": "GREATER_THAN",
                            "value": {"int64Value": "10"}
                        }
                    }
                }
            ]
            
            segments['power_users'] = self.ga.create_audience(
                property_id=self.property_id,
                display_name="Power Users",
                description="Users with more than 10 sessions",
                filter_clauses=power_users_filter
            )
            
            # High value customers segment
            high_value_filter = [
                {
                    "dimensionFilter": {
                        "fieldName": "totalRevenue",
                        "numericFilter": {
                            "operation": "GREATER_THAN",
                            "value": {"doubleValue": "100.0"}
                        }
                    }
                }
            ]
            
            segments['high_value'] = self.ga.create_audience(
                property_id=self.property_id,
                display_name="High Value Customers",
                description="Customers with revenue > $100",
                filter_clauses=high_value_filter
            )
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to create user segments: {e}")
            raise
    
    def export_analytics_to_bigquery(self, 
                                   project_id: str,
                                   dataset_id: str,
                                   table_id: str) -> Dict[str, Any]:
        """Export analytics data to BigQuery"""
        # This would require additional setup with Google Cloud
        # For now, return a placeholder
        return {
            "status": "not_implemented",
            "message": "BigQuery export requires additional Google Cloud setup",
            "project_id": project_id,
            "dataset_id": dataset_id,
            "table_id": table_id
        }
