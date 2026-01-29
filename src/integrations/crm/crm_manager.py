"""
Helm AI CRM Manager
This module provides a unified interface for CRM operations across multiple platforms
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .hubspot_client import HubSpotClient, HelmAICRM as HubSpotCRM
from .salesforce_client import SalesforceClient, HelmAISalesforce

logger = logging.getLogger(__name__)

class CRMProvider(Enum):
    """Supported CRM providers"""
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"

@dataclass
class CustomerProfile:
    """Customer profile data structure"""
    email: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    plan: str = "free"
    signup_date: Optional[str] = None
    last_login: Optional[str] = None
    usage_count: int = 0
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    expected_revenue: float = 0.0
    user_count: int = 1
    account_type: str = "individual"

@dataclass
class SupportTicket:
    """Support ticket data structure"""
    subject: str
    description: str
    priority: str = "medium"
    category: str = "general"
    feature: Optional[str] = None
    error_code: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class UsageMetrics:
    """Usage metrics data structure"""
    last_login: str
    usage_count: int
    last_feature: Optional[str] = None
    session_duration: int = 0
    api_calls: int = 0

class CRMManager:
    """Unified CRM manager supporting multiple providers"""
    
    def __init__(self, primary_provider: CRMProvider = CRMProvider.HUBSPOT):
        """
        Initialize CRM manager
        
        Args:
            primary_provider: Primary CRM provider to use
        """
        self.primary_provider = primary_provider
        self.providers = {}
        
        # Initialize primary provider
        self._initialize_provider(primary_provider)
        
        # Initialize secondary provider if configured
        if primary_provider == CRMProvider.HUBSPOT:
            if os.getenv('SALESFORCE_USERNAME'):
                self._initialize_provider(CRMProvider.SALESFORCE)
        else:
            if os.getenv('HUBSPOT_API_KEY') or os.getenv('HUBSPOT_ACCESS_TOKEN'):
                self._initialize_provider(CRMProvider.HUBSPOT)
    
    def _initialize_provider(self, provider: CRMProvider):
        """Initialize a specific CRM provider"""
        try:
            if provider == CRMProvider.HUBSPOT:
                self.providers[provider] = HubSpotCRM()
                logger.info("HubSpot CRM initialized successfully")
            elif provider == CRMProvider.SALESFORCE:
                self.providers[provider] = HelmAISalesforce()
                logger.info("Salesforce CRM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {provider.value}: {e}")
            raise
    
    def create_customer_profile(self, profile: CustomerProfile, provider: Optional[CRMProvider] = None) -> Dict[str, Any]:
        """
        Create customer profile in CRM
        
        Args:
            profile: Customer profile data
            provider: Specific provider to use (defaults to primary)
            
        Returns:
            Created customer record
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.HUBSPOT:
                user_data = {
                    'email': profile.email,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'company': profile.company,
                    'phone': profile.phone,
                    'job_title': profile.job_title,
                    'plan': profile.plan,
                    'signup_date': profile.signup_date,
                    'last_login': profile.last_login,
                    'usage_count': profile.usage_count,
                    'industry': profile.industry,
                    'company_size': profile.company_size,
                    'website': profile.website,
                    'expected_revenue': profile.expected_revenue,
                    'user_count': profile.user_count,
                    'account_type': profile.account_type
                }
                return crm_client.create_customer_profile(user_data)
            
            elif provider == CRMProvider.SALESFORCE:
                customer_data = {
                    'email': profile.email,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'company_name': profile.company,
                    'phone': profile.phone,
                    'job_title': profile.job_title,
                    'plan': profile.plan,
                    'last_login': profile.last_login,
                    'usage_count': profile.usage_count,
                    'industry': profile.industry,
                    'employee_count': int(profile.company_size or 0),
                    'website': profile.website,
                    'expected_revenue': profile.expected_revenue,
                    'user_count': profile.user_count,
                    'account_type': profile.account_type
                }
                return crm_client.create_enterprise_customer(customer_data)
                
        except Exception as e:
            logger.error(f"Failed to create customer profile in {provider.value}: {e}")
            raise
    
    def update_customer_activity(self, contact_id: str, metrics: UsageMetrics, provider: Optional[CRMProvider] = None) -> Dict[str, Any]:
        """
        Update customer activity metrics
        
        Args:
            contact_id: CRM contact ID
            metrics: Usage metrics
            provider: Specific provider to use
            
        Returns:
            Updated customer record
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.HUBSPOT:
                activity_data = {
                    'last_login': metrics.last_login,
                    'usage_count': metrics.usage_count,
                    'last_feature': metrics.last_feature,
                    'session_duration': metrics.session_duration
                }
                return crm_client.update_customer_activity(contact_id, activity_data)
            
            elif provider == CRMProvider.SALESFORCE:
                usage_data = {
                    'last_login': metrics.last_login,
                    'usage_count': metrics.usage_count,
                    'last_feature': metrics.last_feature,
                    'session_duration': metrics.session_duration,
                    'api_calls': metrics.api_calls
                }
                return crm_client.update_customer_usage(contact_id, usage_data)
                
        except Exception as e:
            logger.error(f"Failed to update customer activity in {provider.value}: {e}")
            raise
    
    def create_support_ticket(self, contact_id: str, ticket: SupportTicket, provider: Optional[CRMProvider] = None) -> Dict[str, Any]:
        """
        Create support ticket
        
        Args:
            contact_id: CRM contact ID
            ticket: Support ticket data
            provider: Specific provider to use
            
        Returns:
            Created support ticket
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.HUBSPOT:
                ticket_data = {
                    'subject': ticket.subject,
                    'description': ticket.description,
                    'priority': ticket.priority,
                    'category': ticket.category
                }
                return crm_client.create_support_ticket_note(contact_id, ticket_data)
            
            elif provider == CRMProvider.SALESFORCE:
                case_data = {
                    'subject': ticket.subject,
                    'description': ticket.description,
                    'priority': ticket.priority,
                    'category': ticket.category,
                    'feature': ticket.feature,
                    'error_code': ticket.error_code,
                    'user_id': ticket.user_id
                }
                return crm_client.create_support_case(contact_id, case_data)
                
        except Exception as e:
            logger.error(f"Failed to create support ticket in {provider.value}: {e}")
            raise
    
    def find_customer_by_email(self, email: str, provider: Optional[CRMProvider] = None) -> List[Dict[str, Any]]:
        """
        Find customer by email address
        
        Args:
            email: Email address to search
            provider: Specific provider to use
            
        Returns:
            List of matching customer records
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.HUBSPOT:
                result = crm_client.hubspot.search_contacts(email, limit=10)
                return result.get('results', [])
            
            elif provider == CRMProvider.SALESFORCE:
                return crm_client.salesforce.find_contact_by_email(email)
                
        except Exception as e:
            logger.error(f"Failed to find customer by email in {provider.value}: {e}")
            raise
    
    def track_conversion_event(self, contact_id: str, event_type: str, event_data: Dict[str, Any], provider: Optional[CRMProvider] = None) -> Dict[str, Any]:
        """
        Track conversion events
        
        Args:
            contact_id: CRM contact ID
            event_type: Type of conversion event
            event_data: Event-specific data
            provider: Specific provider to use
            
        Returns:
            Created event record
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.HUBSPOT:
                return crm_client.track_conversion_event(contact_id, event_type, event_data)
            
            elif provider == CRMProvider.SALESFORCE:
                # Create a task for conversion events
                task_data = {
                    'Subject': f"Conversion Event: {event_type}",
                    'Description': f"Event Data: {event_data}",
                    'Status': 'Completed',
                    'Priority': 'Normal',
                    'WhoId': contact_id
                }
                return crm_client.salesforce.create_task(task_data)
                
        except Exception as e:
            logger.error(f"Failed to track conversion event in {provider.value}: {e}")
            raise
    
    def sync_customer_data(self, source_provider: CRMProvider, target_provider: CRMProvider, contact_id: str) -> Dict[str, Any]:
        """
        Sync customer data between CRM providers
        
        Args:
            source_provider: Source CRM provider
            target_provider: Target CRM provider
            contact_id: Contact ID in source provider
            
        Returns:
            Sync result with new contact ID
        """
        source_client = self.providers.get(source_provider)
        target_client = self.providers.get(target_provider)
        
        if not source_client or not target_client:
            raise ValueError("Both CRM providers must be initialized")
        
        try:
            # Get customer data from source
            if source_provider == CRMProvider.HUBSPOT:
                contact = source_client.hubspot.get_contact(contact_id)
                properties = contact.get('properties', {})
                
                profile = CustomerProfile(
                    email=properties.get('email', ''),
                    first_name=properties.get('firstname', ''),
                    last_name=properties.get('lastname', ''),
                    company=properties.get('company'),
                    phone=properties.get('phone'),
                    job_title=properties.get('jobtitle'),
                    plan=properties.get('helm_ai_plan', 'free'),
                    usage_count=int(properties.get('helm_ai_usage_count', 0))
                )
            
            elif source_provider == CRMProvider.SALESFORCE:
                contact = source_client.salesforce.get_contact(contact_id)
                
                profile = CustomerProfile(
                    email=contact.get('Email', ''),
                    first_name=contact.get('FirstName', ''),
                    last_name=contact.get('LastName', ''),
                    company=contact.get('Account', {}).get('Name') if contact.get('Account') else None,
                    phone=contact.get('Phone'),
                    job_title=contact.get('Title'),
                    plan=contact.get('Helm_AI_Plan__c', 'free'),
                    usage_count=int(contact.get('Helm_AI_Usage_Count__c', 0))
                )
            
            # Create in target provider
            result = self.create_customer_profile(profile, target_provider)
            
            logger.info(f"Successfully synced customer from {source_provider.value} to {target_provider.value}")
            
            return {
                'source_contact_id': contact_id,
                'target_contact_id': result.get('id'),
                'target_provider': target_provider.value,
                'sync_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync customer data: {e}")
            raise
    
    def get_customer_health(self, contact_id: str, provider: Optional[CRMProvider] = None) -> Dict[str, Any]:
        """
        Get comprehensive customer health metrics
        
        Args:
            contact_id: CRM contact ID
            provider: Specific provider to use
            
        Returns:
            Customer health metrics
        """
        provider = provider or self.primary_provider
        crm_client = self.providers.get(provider)
        
        if not crm_client:
            raise ValueError(f"CRM provider {provider.value} not initialized")
        
        try:
            if provider == CRMProvider.SALESFORCE:
                # Get account ID from contact
                contact = crm_client.salesforce.get_contact(contact_id)
                account_id = contact.get('AccountId')
                
                if account_id:
                    return crm_client.salesforce.get_customer_health_metrics(account_id)
            
            # For HubSpot or if no account found, return basic contact info
            if provider == CRMProvider.HUBSPOT:
                contact = crm_client.hubspot.get_contact(contact_id)
                return {
                    'contact_id': contact_id,
                    'properties': contact.get('properties', {}),
                    'health_score': self._calculate_health_score(contact.get('properties', {}))
                }
            
            return {'contact_id': contact_id, 'health_score': 0}
            
        except Exception as e:
            logger.error(f"Failed to get customer health: {e}")
            raise
    
    def _calculate_health_score(self, properties: Dict[str, Any]) -> int:
        """Calculate simple health score based on customer properties"""
        score = 50  # Base score
        
        # Usage metrics
        usage_count = int(properties.get('helm_ai_usage_count', 0))
        if usage_count > 100:
            score += 20
        elif usage_count > 50:
            score += 10
        elif usage_count > 10:
            score += 5
        
        # Plan type
        plan = properties.get('helm_ai_plan', 'free')
        if plan in ['enterprise', 'business']:
            score += 15
        elif plan == 'pro':
            score += 10
        
        # Recent activity
        last_login = properties.get('helm_ai_last_login', '')
        if last_login:
            try:
                login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                days_since_login = (datetime.now() - login_date.replace(tzinfo=None)).days
                if days_since_login <= 7:
                    score += 15
                elif days_since_login <= 30:
                    score += 10
                elif days_since_login <= 90:
                    score += 5
            except:
                pass
        
        return min(100, max(0, score))


# Singleton instance for easy access
crm_manager = CRMManager()
