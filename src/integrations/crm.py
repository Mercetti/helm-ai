"""
Stellar Logic AI CRM Integration Module
Integrates with HubSpot and Salesforce for customer management
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class CRMContact:
    """CRM Contact data structure"""
    email: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    lead_source: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None

@dataclass
class CRMDeal:
    """CRM Deal data structure"""
    contact_id: str
    deal_name: str
    amount: Optional[float] = None
    deal_stage: Optional[str] = None
    close_date: Optional[datetime] = None
    probability: Optional[int] = None
    custom_properties: Optional[Dict[str, Any]] = None

class HubSpotIntegration:
    """HubSpot CRM Integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('HUBSPOT_API_KEY')
        self.base_url = "https://api.hubapi.com/crm/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_contact(self, contact: CRMContact) -> Dict[str, Any]:
        """Create a new contact in HubSpot"""
        try:
            url = f"{self.base_url}/objects/contacts"
            
            properties = {
                'email': contact.email,
                'firstname': contact.first_name,
                'lastname': contact.last_name,
                'company': contact.company or '',
                'phone': contact.phone or '',
                'website': contact.website or '',
                'lifecyclestage': contact.lifecycle_stage or 'lead',
                'hs_lead_status': contact.lead_source or 'NEW'
            }
            
            # Add custom properties
            if contact.custom_properties:
                properties.update(contact.custom_properties)
            
            payload = {
                'properties': properties
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Created HubSpot contact: {contact.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating HubSpot contact: {str(e)}")
            raise
    
    def update_contact(self, contact_id: str, contact: CRMContact) -> Dict[str, Any]:
        """Update an existing contact in HubSpot"""
        try:
            url = f"{self.base_url}/objects/contacts/{contact_id}"
            
            properties = {
                'firstname': contact.first_name,
                'lastname': contact.last_name,
                'company': contact.company or '',
                'phone': contact.phone or '',
                'website': contact.website or ''
            }
            
            if contact.lifecycle_stage:
                properties['lifecyclestage'] = contact.lifecycle_stage
            
            if contact.custom_properties:
                properties.update(contact.custom_properties)
            
            payload = {
                'properties': properties
            }
            
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Updated HubSpot contact: {contact_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error updating HubSpot contact: {str(e)}")
            raise
    
    def create_deal(self, deal: CRMDeal) -> Dict[str, Any]:
        """Create a new deal in HubSpot"""
        try:
            url = f"{self.base_url}/objects/deals"
            
            properties = {
                'dealname': deal.deal_name,
                'dealstage': deal.deal_stage or 'appointmentscheduled',
                'pipeline': 'default'
            }
            
            if deal.amount:
                properties['amount'] = str(deal.amount)
            
            if deal.close_date:
                properties['closedate'] = int(deal.close_date.timestamp() * 1000)
            
            if deal.probability:
                properties['hs_probability'] = str(deal.probability)
            
            if deal.custom_properties:
                properties.update(deal.custom_properties)
            
            payload = {
                'properties': properties,
                'associations': [
                    {
                        'to': {'id': deal.contact_id},
                        'types': [{'category': 'HUBSPOT_DEFINED', 'typeId': 4}]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Created HubSpot deal: {deal.deal_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating HubSpot deal: {str(e)}")
            raise
    
    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email from HubSpot"""
        try:
            url = f"{self.base_url}/objects/contacts/search"
            
            payload = {
                'filterGroups': [
                    {
                        'filters': [
                            {
                                'propertyName': 'email',
                                'operator': 'EQ',
                                'value': email
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                return data['results'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting HubSpot contact: {str(e)}")
            raise

class SalesforceIntegration:
    """Salesforce CRM Integration"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 username: str = None, password: str = None, security_token: str = None):
        self.client_id = client_id or os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SALESFORCE_CLIENT_SECRET')
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.access_token = None
        self.instance_url = None
    
    def authenticate(self) -> bool:
        """Authenticate with Salesforce"""
        try:
            url = "https://login.salesforce.com/services/oauth2/token"
            
            data = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': f"{self.password}{self.security_token}"
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data['access_token']
            self.instance_url = auth_data['instance_url']
            
            logger.info("Successfully authenticated with Salesforce")
            return True
            
        except Exception as e:
            logger.error(f"Salesforce authentication failed: {str(e)}")
            return False
    
    def create_contact(self, contact: CRMContact) -> Dict[str, Any]:
        """Create a new contact in Salesforce"""
        try:
            if not self.access_token:
                self.authenticate()
            
            url = f"{self.instance_url}/services/data/v52.0/sobjects/Contact/"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'Email': contact.email,
                'FirstName': contact.first_name,
                'LastName': contact.last_name,
                'Phone': contact.phone or '',
                'Website': contact.website or ''
            }
            
            if contact.company:
                # First create or find account
                account_id = self._get_or_create_account(contact.company)
                if account_id:
                    data['AccountId'] = account_id
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Created Salesforce contact: {contact.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Salesforce contact: {str(e)}")
            raise
    
    def create_opportunity(self, deal: CRMDeal) -> Dict[str, Any]:
        """Create a new opportunity in Salesforce"""
        try:
            if not self.access_token:
                self.authenticate()
            
            url = f"{self.instance_url}/services/data/v52.0/sobjects/Opportunity/"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'Name': deal.deal_name,
                'StageName': deal.deal_stage or 'Prospecting',
                'CloseDate': deal.close_date.strftime('%Y-%m-%d') if deal.close_date else datetime.now().strftime('%Y-%m-%d')
            }
            
            if deal.amount:
                data['Amount'] = deal.amount
            
            if deal.probability:
                data['Probability'] = deal.probability
            
            # Associate with contact
            if deal.contact_id:
                data['Primary_Contact__c'] = deal.contact_id
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Created Salesforce opportunity: {deal.deal_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Salesforce opportunity: {str(e)}")
            raise
    
    def _get_or_create_account(self, company_name: str) -> Optional[str]:
        """Get or create an account in Salesforce"""
        try:
            # Search for existing account
            url = f"{self.instance_url}/services/data/v52.0/query/?q=SELECT+Id+FROM+Account+WHERE+Name+=+'{company_name}'"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('records'):
                return data['records'][0]['Id']
            
            # Create new account
            url = f"{self.instance_url}/services/data/v52.0/sobjects/Account/"
            
            headers['Content-Type'] = 'application/json'
            
            account_data = {
                'Name': company_name
            }
            
            response = requests.post(url, headers=headers, json=account_data)
            response.raise_for_status()
            
            return response.json()['id']
            
        except Exception as e:
            logger.error(f"Error getting/creating Salesforce account: {str(e)}")
            return None

class CRMManager:
    """Unified CRM Manager"""
    
    def __init__(self):
        self.hubspot = HubSpotIntegration() if os.getenv('HUBSPOT_API_KEY') else None
        self.salesforce = SalesforceIntegration() if os.getenv('SALESFORCE_CLIENT_ID') else None
        self.primary_crm = os.getenv('PRIMARY_CRM', 'hubspot')
    
    def sync_contact(self, contact: CRMContact) -> Dict[str, Any]:
        """Sync contact to primary CRM"""
        try:
            if self.primary_crm == 'hubspot' and self.hubspot:
                return self.hubspot.create_contact(contact)
            elif self.primary_crm == 'salesforce' and self.salesforce:
                return self.salesforce.create_contact(contact)
            else:
                raise ValueError(f"Primary CRM '{self.primary_crm}' not configured")
                
        except Exception as e:
            logger.error(f"Error syncing contact: {str(e)}")
            raise
    
    def sync_deal(self, deal: CRMDeal) -> Dict[str, Any]:
        """Sync deal to primary CRM"""
        try:
            if self.primary_crm == 'hubspot' and self.hubspot:
                return self.hubspot.create_deal(deal)
            elif self.primary_crm == 'salesforce' and self.salesforce:
                return self.salesforce.create_opportunity(deal)
            else:
                raise ValueError(f"Primary CRM '{self.primary_crm}' not configured")
                
        except Exception as e:
            logger.error(f"Error syncing deal: {str(e)}")
            raise
    
    def get_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact from primary CRM"""
        try:
            if self.primary_crm == 'hubspot' and self.hubspot:
                return self.hubspot.get_contact_by_email(email)
            elif self.primary_crm == 'salesforce' and self.salesforce:
                # Implement Salesforce contact lookup
                return None
            else:
                raise ValueError(f"Primary CRM '{self.primary_crm}' not configured")
                
        except Exception as e:
            logger.error(f"Error getting contact: {str(e)}")
            return None

# Usage example and integration with Helm AI
def sync_user_to_crm(user_data: Dict[str, Any]) -> bool:
    """Sync Helm AI user to CRM"""
    try:
        crm_manager = CRMManager()
        
        contact = CRMContact(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            company=user_data.get('company'),
            phone=user_data.get('phone'),
            website=user_data.get('website'),
            lifecycle_stage='customer',
            lead_source='stellar_logic_ai_signup',
            custom_properties={
                'stellar_logic_ai_user_id': user_data['id'],
                'stellar_logic_ai_plan': user_data.get('plan', 'free'),
                'stellar_logic_ai_signup_date': user_data['created_at']
            }
        )
        
        result = crm_manager.sync_contact(contact)
        logger.info(f"Successfully synced user {user_data['email']} to CRM")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync user to CRM: {str(e)}")
        return False

def sync_subscription_to_crm(subscription_data: Dict[str, Any]) -> bool:
    """Sync Helm AI subscription to CRM"""
    try:
        crm_manager = CRMManager()
        
        # Get contact first
        contact = crm_manager.get_contact(subscription_data['user_email'])
        if not contact:
            logger.error(f"Contact not found for user {subscription_data['user_email']}")
            return False
        
        contact_id = contact['id']
        
        deal = CRMDeal(
            contact_id=contact_id,
            deal_name=f"Stellar Logic AI Subscription - {subscription_data['plan'].upper()}",
            amount=subscription_data['amount'],
            deal_stage='closedwon',
            close_date=datetime.now(),
            probability=100,
            custom_properties={
                'stellar_logic_ai_subscription_id': subscription_data['id'],
                'stellar_logic_ai_plan': subscription_data['plan'],
                'stellar_logic_ai_billing_cycle': subscription_data['billing_cycle']
            }
        )
        
        result = crm_manager.sync_deal(deal)
        logger.info(f"Successfully synced subscription {subscription_data['id']} to CRM")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync subscription to CRM: {str(e)}")
        return False
