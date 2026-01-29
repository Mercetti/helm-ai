"""
Helm AI HubSpot Integration Client
This module provides integration with HubSpot CRM for customer management
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class HubSpotClient:
    """HubSpot API client for CRM integration"""
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize HubSpot client
        
        Args:
            api_key: HubSpot API key (legacy authentication)
            access_token: HubSpot access token (OAuth2)
        """
        self.api_key = api_key or os.getenv('HUBSPOT_API_KEY')
        self.access_token = access_token or os.getenv('HUBSPOT_ACCESS_TOKEN')
        self.base_url = "https://api.hubapi.com"
        
        if not self.api_key and not self.access_token:
            raise ValueError("Either API key or access token must be provided")
        
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
        
        # Setup authentication headers
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.params.update({'hapikey': self.api_key})
            self.session.headers.update({'Content-Type': 'application/json'})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to HubSpot API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # Contact Management
    def create_contact(self, email: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in HubSpot"""
        data = {
            "properties": {
                "email": email,
                **properties
            }
        }
        return self._make_request('POST', '/crm/v3/objects/contacts', json=data)
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID"""
        return self._make_request('GET', f'/crm/v3/objects/contacts/{contact_id}')
    
    def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search contacts by email or name"""
        data = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "CONTAINS_TOKEN",
                            "value": query
                        }
                    ]
                }
            ],
            "limit": limit
        }
        return self._make_request('POST', '/crm/v3/objects/contacts/search', json=data)
    
    def update_contact(self, contact_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact properties"""
        data = {"properties": properties}
        return self._make_request('PATCH', f'/crm/v3/objects/contacts/{contact_id}', json=data)
    
    def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        """Delete contact"""
        return self._make_request('DELETE', f'/crm/v3/objects/contacts/{contact_id}')
    
    # Company Management
    def create_company(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company in HubSpot"""
        data = {"properties": properties}
        return self._make_request('POST', '/crm/v3/objects/companies', json=data)
    
    def get_company(self, company_id: str) -> Dict[str, Any]:
        """Get company by ID"""
        return self._make_request('GET', f'/crm/v3/objects/companies/{company_id}')
    
    def update_company(self, company_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update company properties"""
        data = {"properties": properties}
        return self._make_request('PATCH', f'/crm/v3/objects/companies/{company_id}', json=data)
    
    # Deal Management
    def create_deal(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal in HubSpot"""
        data = {"properties": properties}
        return self._make_request('POST', '/crm/v3/objects/deals', json=data)
    
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Get deal by ID"""
        return self._make_request('GET', f'/crm/v3/objects/deals/{deal_id}')
    
    def update_deal(self, deal_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update deal properties"""
        data = {"properties": properties}
        return self._make_request('PATCH', f'/crm/v3/objects/deals/{deal_id}', json=data)
    
    # Association Management
    def associate_contact_company(self, contact_id: str, company_id: str) -> Dict[str, Any]:
        """Associate contact with company"""
        data = {
            "from": {"id": contact_id, "type": "contact"},
            "to": {"id": company_id, "type": "company"},
            "type": "contact_to_company"
        }
        return self._make_request('PUT', '/crm/v3/associations/contact/company/batch/create', json=data)
    
    def associate_deal_contact(self, deal_id: str, contact_id: str) -> Dict[str, Any]:
        """Associate deal with contact"""
        data = {
            "from": {"id": deal_id, "type": "deal"},
            "to": {"id": contact_id, "type": "contact"},
            "type": "deal_to_contact"
        }
        return self._make_request('PUT', '/crm/v3/associations/deal/contact/batch/create', json=data)
    
    # Pipeline Management
    def get_pipelines(self, object_type: str = "deals") -> Dict[str, Any]:
        """Get pipelines for specified object type"""
        return self._make_request('GET', f'/crm/v3/pipelines/{object_type}')
    
    def get_pipeline_stages(self, pipeline_id: str, object_type: str = "deals") -> Dict[str, Any]:
        """Get stages for a specific pipeline"""
        return self._make_request('GET', f'/crm/v3/pipelines/{object_type}/{pipeline_id}/stages')
    
    # Engagement Management
    def create_note(self, properties: Dict[str, Any], associations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a note engagement"""
        data = {
            "properties": properties,
            "associations": associations or []
        }
        return self._make_request('POST', '/crm/v3/objects/notes', json=data)
    
    def create_task(self, properties: Dict[str, Any], associations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a task engagement"""
        data = {
            "properties": properties,
            "associations": associations or []
        }
        return self._make_request('POST', '/crm/v3/objects/tasks', json=data)
    
    # Email Tracking
    def track_email_open(self, contact_id: str, email_id: str) -> Dict[str, Any]:
        """Track email open event"""
        properties = {
            "hs_timestamp": int(datetime.now().timestamp() * 1000),
            "hs_email_status": "OPENED",
            "hs_email_direction": "EMAIL",
            "hs_email_subject": "Helm AI Communication"
        }
        return self.create_note(properties, [
            {"to": {"id": contact_id, "type": "contact"}}
        ])
    
    def track_email_click(self, contact_id: str, email_id: str, url: str) -> Dict[str, Any]:
        """Track email click event"""
        properties = {
            "hs_timestamp": int(datetime.now().timestamp() * 1000),
            "hs_email_status": "CLICKED",
            "hs_email_direction": "EMAIL",
            "hs_email_subject": "Helm AI Communication",
            "hs_click_through_url": url
        }
        return self.create_note(properties, [
            {"to": {"id": contact_id, "type": "contact"}}
        ])
    
    # Webhooks
    def create_webhook(self, target_url: str, event_types: List[str], active: bool = True) -> Dict[str, Any]:
        """Create a webhook subscription"""
        data = {
            "targetUrl": target_url,
            "eventTypes": event_types,
            "active": active
        }
        return self._make_request('POST', '/webhooks/v3/subscriptions', json=data)
    
    def get_webhooks(self) -> Dict[str, Any]:
        """Get all webhook subscriptions"""
        return self._make_request('GET', '/webhooks/v3/subscriptions')
    
    def delete_webhook(self, subscription_id: str) -> Dict[str, Any]:
        """Delete webhook subscription"""
        return self._make_request('DELETE', f'/webhooks/v3/subscriptions/{subscription_id}')
    
    # Custom Objects
    def get_custom_objects(self) -> Dict[str, Any]:
        """Get all custom object definitions"""
        return self._make_request('GET', '/crm/v3/schemas')
    
    def create_custom_object_record(self, object_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom object record"""
        data = {"properties": properties}
        return self._make_request('POST', f'/crm/v3/objects/{object_type}', json=data)
    
    # Analytics and Reporting
    def get_contact_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get contact analytics for date range"""
        params = {
            "start": start_date,
            "end": end_date
        }
        return self._make_request('GET', '/analytics/v2/views/contact-creation', params=params)
    
    def get_deal_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get deal analytics for date range"""
        params = {
            "start": start_date,
            "end": end_date
        }
        return self._make_request('GET', '/analytics/v2/views/deal-forecast', params=params)


# Helm AI specific CRM operations
class HelmAICRM:
    """Helm AI specific CRM operations using HubSpot"""
    
    def __init__(self):
        self.hubspot = HubSpotClient()
    
    def create_customer_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive customer profile"""
        # Create contact
        contact_properties = {
            "firstname": user_data.get('first_name', ''),
            "lastname": user_data.get('last_name', ''),
            "phone": user_data.get('phone', ''),
            "company": user_data.get('company', ''),
            "jobtitle": user_data.get('job_title', ''),
            "helm_ai_plan": user_data.get('plan', 'free'),
            "helm_ai_signup_date": user_data.get('signup_date', ''),
            "helm_ai_last_login": user_data.get('last_login', ''),
            "helm_ai_usage_count": str(user_data.get('usage_count', 0)),
            "lifecyclestage": "customer"
        }
        
        contact = self.hubspot.create_contact(user_data['email'], contact_properties)
        
        # Create company if provided
        if user_data.get('company'):
            company_properties = {
                "name": user_data['company'],
                "industry": user_data.get('industry', ''),
                "size": user_data.get('company_size', ''),
                "website": user_data.get('website', ''),
                "helm_ai_account_type": user_data.get('account_type', 'individual')
            }
            
            company = self.hubspot.create_company(company_properties)
            
            # Associate contact with company
            self.hubspot.associate_contact_company(
                contact['id'], 
                company['id']
            )
        
        # Create initial deal for enterprise customers
        if user_data.get('plan') in ['enterprise', 'business']:
            deal_properties = {
                "dealname": f"New {user_data.get('plan', '').title()} Account - {user_data.get('company', 'Individual')}",
                "dealstage": "appointmentscheduled",
                "pipeline": "default",
                "amount": str(user_data.get('expected_revenue', 0)),
                "closedate": user_data.get('expected_close_date', ''),
                "helm_ai_plan": user_data.get('plan', ''),
                "helm_ai_user_count": str(user_data.get('user_count', 1))
            }
            
            deal = self.hubspot.create_deal(deal_properties)
            self.hubspot.associate_deal_contact(deal['id'], contact['id'])
        
        return contact
    
    def update_customer_activity(self, contact_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer activity and engagement"""
        properties = {
            "helm_ai_last_login": activity_data.get('last_login', ''),
            "helm_ai_usage_count": str(activity_data.get('usage_count', 0)),
            "helm_ai_last_feature_used": activity_data.get('last_feature', ''),
            "helm_ai_session_duration": str(activity_data.get('session_duration', 0)),
            "hs_lead_status": "OPEN"
        }
        
        return self.hubspot.update_contact(contact_id, properties)
    
    def create_support_ticket_note(self, contact_id: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a note for support ticket"""
        properties = {
            "hs_note_body": f"Support Ticket: {ticket_data.get('subject', '')}\n\n{ticket_data.get('description', '')}\n\nPriority: {ticket_data.get('priority', 'medium')}\nCategory: {ticket_data.get('category', 'general')}",
            "hs_timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        return self.hubspot.create_note(properties, [
            {"to": {"id": contact_id, "type": "contact"}}
        ])
    
    def track_conversion_event(self, contact_id: str, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track conversion events like trial signups, upgrades, etc."""
        properties = {
            "hs_note_body": f"Conversion Event: {event_type}\n\n{json.dumps(event_data, indent=2)}",
            "hs_timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        return self.hubspot.create_note(properties, [
            {"to": {"id": contact_id, "type": "contact"}}
        ])
