"""
Helm AI Salesforce Integration Client
This module provides integration with Salesforce CRM for enterprise customer management
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

class SalesforceClient:
    """Salesforce API client for CRM integration"""
    
    def __init__(self, 
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 security_token: Optional[str] = None,
                 consumer_key: Optional[str] = None,
                 consumer_secret: Optional[str] = None,
                 sandbox: bool = False):
        """
        Initialize Salesforce client
        
        Args:
            username: Salesforce username
            password: Salesforce password
            security_token: Salesforce security token
            consumer_key: Connected app consumer key (OAuth2)
            consumer_secret: Connected app consumer secret (OAuth2)
            sandbox: Whether to use sandbox environment
        """
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.consumer_key = consumer_key or os.getenv('SALESFORCE_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('SALESFORCE_CONSUMER_SECRET')
        
        if sandbox:
            self.base_url = "https://test.salesforce.com"
        else:
            self.base_url = "https://login.salesforce.com"
        
        self.access_token = None
        self.instance_url = None
        
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
        
        # Authenticate
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Salesforce and get access token"""
        if self.consumer_key and self.consumer_secret:
            # OAuth2 authentication
            data = {
                'grant_type': 'password',
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'username': self.username,
                'password': f"{self.password}{self.security_token}"
            }
        else:
            # Username/password authentication
            data = {
                'grant_type': 'password',
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'username': self.username,
                'password': f"{self.password}{self.security_token}"
            }
        
        try:
            response = self.session.post(f"{self.base_url}/services/oauth2/token", data=data)
            response.raise_for_status()
            auth_data = response.json()
            
            self.access_token = auth_data['access_token']
            self.instance_url = auth_data['instance_url']
            
            # Setup authenticated session headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Salesforce authentication failed: {e}")
            raise
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Salesforce API"""
        url = f"{self.instance_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle token expiration
            if response.status_code == 401:
                logger.info("Access token expired, re-authenticating...")
                self.authenticate()
                response = self.session.request(method, url, **kwargs)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Salesforce API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # SOQL Queries
    def query(self, soql_query: str) -> Dict[str, Any]:
        """Execute SOQL query"""
        params = {'q': soql_query}
        return self._make_request('GET', '/services/data/v56.0/query/', params=params)
    
    def query_all(self, soql_query: str) -> List[Dict[str, Any]]:
        """Execute SOQL query and get all results (handles pagination)"""
        all_records = []
        query_url = f"/services/data/v56.0/query/?q={soql_query}"
        
        while query_url:
            result = self._make_request('GET', query_url)
            all_records.extend(result.get('records', []))
            
            if not result.get('done'):
                query_url = result.get('nextRecordsUrl')
            else:
                query_url = None
        
        return all_records
    
    # Contact Management
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Contact/', json=contact_data)
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/Contact/{contact_id}')
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact"""
        return self._make_request('PATCH', f'/services/data/v56.0/sobjects/Contact/{contact_id}', json=contact_data)
    
    def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        """Delete contact"""
        return self._make_request('DELETE', f'/services/data/v56.0/sobjects/Contact/{contact_id}')
    
    def find_contact_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Find contacts by email"""
        soql = f"SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact WHERE Email = '{email}'"
        result = self.query(soql)
        return result.get('records', [])
    
    # Account Management
    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new account"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Account/', json=account_data)
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get account by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/Account/{account_id}')
    
    def update_account(self, account_id: str, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update account"""
        return self._make_request('PATCH', f'/services/data/v56.0/sobjects/Account/{account_id}', json=account_data)
    
    def find_account_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find accounts by name"""
        soql = f"SELECT Id, Name, Type, Industry, AnnualRevenue FROM Account WHERE Name LIKE '%{name}%'"
        result = self.query(soql)
        return result.get('records', [])
    
    # Opportunity Management
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new opportunity"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Opportunity/', json=opportunity_data)
    
    def get_opportunity(self, opportunity_id: str) -> Dict[str, Any]:
        """Get opportunity by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/Opportunity/{opportunity_id}')
    
    def update_opportunity(self, opportunity_id: str, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update opportunity"""
        return self._make_request('PATCH', f'/services/data/v56.0/sobjects/Opportunity/{opportunity_id}', json=opportunity_data)
    
    # Lead Management
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Lead/', json=lead_data)
    
    def convert_lead(self, lead_id: str, converted_status: str, account_id: str = None, contact_id: str = None) -> Dict[str, Any]:
        """Convert lead to account/contact"""
        data = {
            'leadId': lead_id,
            'convertedStatus': converted_status
        }
        if account_id:
            data['accountId'] = account_id
        if contact_id:
            data['contactId'] = contact_id
        
        return self._make_request('POST', '/services/data/v56.0/sobjects/Lead/{lead_id}', json=data)
    
    # Case Management
    def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new case"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Case/', json=case_data)
    
    def get_case(self, case_id: str) -> Dict[str, Any]:
        """Get case by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/Case/{case_id}')
    
    def update_case(self, case_id: str, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update case"""
        return self._make_request('PATCH', f'/services/data/v56.0/sobjects/Case/{case_id}', json=case_data)
    
    # Task Management
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        return self._make_request('POST', '/services/data/v56.0/sobjects/Task/', json=task_data)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/Task/{task_id}')
    
    # Custom Objects
    def create_custom_object(self, object_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom object record"""
        return self._make_request('POST', f'/services/data/v56.0/sobjects/{object_name}/', json=record_data)
    
    def get_custom_object(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get custom object record by ID"""
        return self._make_request('GET', f'/services/data/v56.0/sobjects/{object_name}/{record_id}')
    
    # Bulk Operations
    def create_job(self, operation: str, object_name: str, content_type: str = 'JSON') -> Dict[str, Any]:
        """Create bulk API job"""
        data = {
            'operation': operation,
            'object': object_name,
            'contentType': content_type
        }
        return self._make_request('POST', '/services/data/v56.0/jobs/ingest/', json=data)
    
    def upload_job_data(self, job_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload data to bulk job"""
        return self._make_request('PUT', f'/services/data/v56.0/jobs/ingest/{job_id}/batches/', json=data)
    
    def close_job(self, job_id: str) -> Dict[str, Any]:
        """Close bulk job and start processing"""
        data = {'state': 'UploadComplete'}
        return self._make_request('PATCH', f'/services/data/v56.0/jobs/ingest/{job_id}', json=data)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get bulk job status"""
        return self._make_request('GET', f'/services/data/v56.0/jobs/ingest/{job_id}')
    
    # Streaming API
    def create_push_topic(self, topic_name: str, soql_query: str) -> Dict[str, Any]:
        """Create streaming API push topic"""
        data = {
            'Name': topic_name,
            'Query': soql_query,
            'ApiVersion': 56.0
        }
        return self._make_request('POST', '/services/data/v56.0/sobjects/PushTopic/', json=data)
    
    def subscribe_to_topic(self, topic_name: str, replay_id: int = -2) -> str:
        """Subscribe to streaming topic (returns channel URL)"""
        channel_url = f"{self.instance_url}/cometd/56.0/channel/{topic_name}"
        return channel_url


# Helm AI specific Salesforce operations
class HelmAISalesforce:
    """Helm AI specific CRM operations using Salesforce"""
    
    def __init__(self):
        self.salesforce = SalesforceClient()
    
    def create_enterprise_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive enterprise customer profile"""
        # Create account
        account_data = {
            'Name': customer_data.get('company_name', ''),
            'Type': customer_data.get('account_type', 'Prospect'),
            'Industry': customer_data.get('industry', ''),
            'AnnualRevenue': customer_data.get('annual_revenue', 0),
            'NumberOfEmployees': customer_data.get('employee_count', 0),
            'Website': customer_data.get('website', ''),
            'Phone': customer_data.get('phone', ''),
            'BillingCity': customer_data.get('billing_city', ''),
            'BillingState': customer_data.get('billing_state', ''),
            'BillingCountry': customer_data.get('billing_country', ''),
            'Helm_AI_Plan__c': customer_data.get('plan', 'enterprise'),
            'Helm_AI_User_Count__c': customer_data.get('user_count', 0),
            'Helm_AI_Start_Date__c': customer_data.get('start_date', datetime.now().isoformat()),
            'Helm_AI_Technical_Contact__c': customer_data.get('technical_contact', '')
        }
        
        account = self.salesforce.create_account(account_data)
        account_id = account['id']
        
        # Create primary contact
        contact_data = {
            'FirstName': customer_data.get('first_name', ''),
            'LastName': customer_data.get('last_name', ''),
            'Email': customer_data.get('email', ''),
            'Phone': customer_data.get('phone', ''),
            'Title': customer_data.get('job_title', ''),
            'AccountId': account_id,
            'Helm_AI_Role__c': customer_data.get('role', 'Primary Contact'),
            'Helm_AI_Last_Login__c': customer_data.get('last_login', ''),
            'Helm_AI_Usage_Count__c': customer_data.get('usage_count', 0)
        }
        
        contact = self.salesforce.create_contact(contact_data)
        
        # Create opportunity
        opportunity_data = {
            'Name': f"Helm AI {customer_data.get('plan', '').title()} - {customer_data.get('company_name', '')}",
            'AccountId': account_id,
            'StageName': 'Prospecting',
            'CloseDate': customer_data.get('expected_close_date', datetime.now().strftime('%Y-%m-%d')),
            'Amount': customer_data.get('expected_revenue', 0),
            'Type': 'New Business',
            'LeadSource': 'Web',
            'Helm_AI_Plan__c': customer_data.get('plan', 'enterprise'),
            'Helm_AI_Contract_Term__c': customer_data.get('contract_term', '12'),
            'Probability': 25
        }
        
        opportunity = self.salesforce.create_opportunity(opportunity_data)
        
        # Create initial task for sales team
        task_data = {
            'Subject': f"New Enterprise Account Setup - {customer_data.get('company_name', '')}",
            'Description': f"New enterprise customer signed up for {customer_data.get('plan', '')} plan. Contact: {customer_data.get('email', '')}",
            'Status': 'Not Started',
            'Priority': 'High',
            'WhatId': account_id,
            'WhoId': contact['id'],
            'ActivityDate': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.salesforce.create_task(task_data)
        
        return {
            'account': account,
            'contact': contact,
            'opportunity': opportunity
        }
    
    def update_customer_usage(self, contact_id: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer usage metrics"""
        update_data = {
            'Helm_AI_Last_Login__c': usage_data.get('last_login', ''),
            'Helm_AI_Usage_Count__c': usage_data.get('usage_count', 0),
            'Helm_AI_Last_Feature_Used__c': usage_data.get('last_feature', ''),
            'Helm_AI_Session_Duration__c': usage_data.get('session_duration', 0),
            'Helm_AI_API_Calls__c': usage_data.get('api_calls', 0)
        }
        
        return self.salesforce.update_contact(contact_id, update_data)
    
    def create_support_case(self, contact_id: str, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create support case"""
        case_record = {
            'ContactId': contact_id,
            'Subject': case_data.get('subject', ''),
            'Description': case_data.get('description', ''),
            'Origin': case_data.get('origin', 'Web'),
            'Priority': case_data.get('priority', 'Medium'),
            'Status': 'New',
            'Type': case_data.get('category', 'Problem'),
            'Helm_AI_Feature__c': case_data.get('feature', ''),
            'Helm_AI_Error_Code__c': case_data.get('error_code', ''),
            'Helm_AI_User_ID__c': case_data.get('user_id', '')
        }
        
        return self.salesforce.create_case(case_record)
    
    def track_renewal_opportunity(self, account_id: str, renewal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create renewal opportunity"""
        opportunity_data = {
            'Name': f"Renewal - {renewal_data.get('company_name', '')}",
            'AccountId': account_id,
            'StageName': 'Qualification',
            'CloseDate': renewal_data.get('renewal_date', datetime.now().strftime('%Y-%m-%d')),
            'Amount': renewal_data.get('renewal_amount', 0),
            'Type': 'Existing Business',
            'LeadSource': 'Renewal',
            'Helm_AI_Plan__c': renewal_data.get('plan', 'enterprise'),
            'Helm_AI_Current_Term__c': renewal_data.get('current_term', '12'),
            'Helm_AI_Renewal_Term__c': renewal_data.get('renewal_term', '12'),
            'Probability': 70
        }
        
        return self.salesforce.create_opportunity(opportunity_data)
    
    def bulk_update_usage_metrics(self, usage_records: List[Dict[str, Any]]) -> str:
        """Bulk update usage metrics for multiple customers"""
        # Create bulk job
        job = self.salesforce.create_job('update', 'Contact')
        job_id = job['id']
        
        # Upload data
        self.salesforce.upload_job_data(job_id, usage_records)
        
        # Close job
        self.salesforce.close_job(job_id)
        
        return job_id
    
    def get_customer_health_metrics(self, account_id: str) -> Dict[str, Any]:
        """Get comprehensive customer health metrics"""
        soql = f"""
        SELECT 
            Id, Name, Type, AnnualRevenue, Helm_AI_Plan__c, Helm_AI_User_Count__c,
            (SELECT Id, Subject, Status, CreatedDate FROM Cases WHERE CreatedDate = LAST_N_DAYS:30),
            (SELECT Id, Subject, Status, ActivityDate FROM Tasks WHERE ActivityDate = LAST_N_DAYS:30),
            (SELECT Id, Name, StageName, Amount, CloseDate FROM Opportunities WHERE CloseDate = LAST_N_DAYS:365)
        FROM Account 
        WHERE Id = '{account_id}'
        """
        
        result = self.salesforce.query(soql)
        return result.get('records', [{}])[0]
