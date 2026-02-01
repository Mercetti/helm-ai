"""
Helm AI Support System Integration Module
Integrates with Zendesk and Intercom for customer service
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class SupportTicket:
    """Support ticket data structure"""
    subject: str
    description: str
    user_email: str
    user_name: str
    priority: str = 'normal'  # low, normal, high, urgent
    status: str = 'new'  # new, open, pending, solved, closed
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

@dataclass
class SupportUser:
    """Support user data structure"""
    email: str
    name: str
    user_id: Optional[str] = None
    company: Optional[str] = None
    plan: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None

class ZendeskIntegration:
    """Zendesk Support Integration"""
    
    def __init__(self, subdomain: str = None, email: str = None, api_token: str = None):
        self.subdomain = subdomain or os.getenv('ZENDESK_SUBDOMAIN')
        self.email = email or os.getenv('ZENDESK_EMAIL')
        self.api_token = api_token or os.getenv('ZENDESK_API_TOKEN')
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"
        self.auth = (f"{self.email}/token", self.api_token)
        self.headers = {'Content-Type': 'application/json'}
    
    def create_or_update_user(self, user: SupportUser) -> Dict[str, Any]:
        """Create or update user in Zendesk"""
        try:
            # First try to find existing user
            existing_user = self._find_user_by_email(user.email)
            
            user_data = {
                'name': user.name,
                'email': user.email,
                'role': 'end-user'
            }
            
            if user.user_id:
                user_data['external_id'] = user.user_id
            
            if user.company:
                user_data['organization'] = {'name': user.company}
            
            if user.phone:
                user_data['phone'] = user.phone
            
            if user.timezone:
                user_data['time_zone'] = user.timezone
            
            if user.custom_attributes:
                user_data['user_fields'] = user.custom_attributes
            
            if existing_user:
                # Update existing user
                url = f"{self.base_url}/users/{existing_user['id']}.json"
                response = requests.put(url, auth=self.auth, headers=self.headers, 
                                      json={'user': user_data})
            else:
                # Create new user
                url = f"{self.base_url}/users.json"
                response = requests.post(url, auth=self.auth, headers=self.headers, 
                                        json={'user': user_data})
            
            response.raise_for_status()
            
            logger.info(f"{'Updated' if existing_user else 'Created'} Zendesk user: {user.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating/updating Zendesk user: {str(e)}")
            raise
    
    def create_ticket(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Create support ticket in Zendesk"""
        try:
            # Ensure user exists
            user = SupportUser(
                email=ticket.user_email,
                name=ticket.user_name
            )
            self.create_or_update_user(user)
            
            # Prepare ticket data
            ticket_data = {
                'ticket': {
                    'subject': ticket.subject,
                    'comment': {
                        'body': ticket.description
                    },
                    'priority': self._map_priority(ticket.priority),
                    'status': ticket.status,
                    'requester': {
                        'email': ticket.user_email,
                        'name': ticket.user_name
                    }
                }
            }
            
            # Add category if specified
            if ticket.category:
                ticket_data['ticket']['type'] = ticket.category
            
            # Add tags if specified
            if ticket.tags:
                ticket_data['ticket']['tags'] = ticket.tags
            
            # Add custom fields if specified
            if ticket.custom_fields:
                ticket_data['ticket']['custom_fields'] = [
                    {'id': field_id, 'value': value}
                    for field_id, value in ticket.custom_fields.items()
                ]
            
            url = f"{self.base_url}/tickets.json"
            response = requests.post(url, auth=self.auth, headers=self.headers, json=ticket_data)
            response.raise_for_status()
            
            logger.info(f"Created Zendesk ticket: {ticket.subject}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Zendesk ticket: {str(e)}")
            raise
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing ticket in Zendesk"""
        try:
            ticket_data = {'ticket': updates}
            
            url = f"{self.base_url}/tickets/{ticket_id}.json"
            response = requests.put(url, auth=self.auth, headers=self.headers, json=ticket_data)
            response.raise_for_status()
            
            logger.info(f"Updated Zendesk ticket: {ticket_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error updating Zendesk ticket: {str(e)}")
            raise
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get ticket details from Zendesk"""
        try:
            url = f"{self.base_url}/tickets/{ticket_id}.json"
            response = requests.get(url, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Zendesk ticket: {str(e)}")
            raise
    
    def _find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email in Zendesk"""
        try:
            url = f"{self.base_url}/users/search.json"
            params = {'query': f'email:{email}'}
            
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            response.raise_for_status()
            
            users = response.json().get('users', [])
            if users:
                return users[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding Zendesk user: {str(e)}")
            return None
    
    def _map_priority(self, priority: str) -> str:
        """Map priority levels to Zendesk priority"""
        priority_map = {
            'low': 'low',
            'normal': 'normal',
            'high': 'high',
            'urgent': 'urgent'
        }
        return priority_map.get(priority, 'normal')

class IntercomIntegration:
    """Intercom Support Integration"""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('INTERCOM_ACCESS_TOKEN')
        self.base_url = "https://api.intercom.io"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_or_update_user(self, user: SupportUser) -> Dict[str, Any]:
        """Create or update user in Intercom"""
        try:
            # Find existing user
            existing_user = self._find_user_by_email(user.email)
            
            user_data = {
                'email': user.email,
                'name': user.name,
                'role': 'user'
            }
            
            if user.user_id:
                user_data['user_id'] = user.user_id
            
            if user.company:
                user_data['companies'] = [{
                    'company_id': user.company.replace(' ', '_').lower(),
                    'name': user.company
                }]
            
            if user.phone:
                user_data['phone'] = user.phone
            
            if user.timezone:
                user_data['timezone'] = user.timezone
            
            if user.custom_attributes:
                user_data['custom_attributes'] = user.custom_attributes
            
            if existing_user:
                # Update existing user
                user_data['id'] = existing_user['id']
                url = f"{self.base_url}/contacts"
                response = requests.put(url, headers=self.headers, json=user_data)
            else:
                # Create new user
                url = f"{self.base_url}/contacts"
                response = requests.post(url, headers=self.headers, json=user_data)
            
            response.raise_for_status()
            
            logger.info(f"{'Updated' if existing_user else 'Created'} Intercom user: {user.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating/updating Intercom user: {str(e)}")
            raise
    
    def create_conversation(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Create conversation in Intercom"""
        try:
            # Ensure user exists
            user = SupportUser(
                email=ticket.user_email,
                name=ticket.user_name
            )
            user_result = self.create_or_update_user(user)
            user_id = user_result['id']
            
            # Prepare conversation data
            conversation_data = {
                'from': {
                    'type': 'user',
                    'id': user_id
                },
                'body': ticket.description,
                'subject': ticket.subject
            }
            
            # Add custom attributes if specified
            if ticket.custom_fields:
                conversation_data['custom_attributes'] = ticket.custom_fields
            
            # Add tags if specified
            if ticket.tags:
                conversation_data['tags'] = {
                    'tags': ticket.tags
                }
            
            url = f"{self.base_url}/conversations"
            response = requests.post(url, headers=self.headers, json=conversation_data)
            response.raise_for_status()
            
            logger.info(f"Created Intercom conversation: {ticket.subject}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Intercom conversation: {str(e)}")
            raise
    
    def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing conversation in Intercom"""
        try:
            url = f"{self.base_url}/conversations/{conversation_id}"
            response = requests.put(url, headers=self.headers, json=updates)
            response.raise_for_status()
            
            logger.info(f"Updated Intercom conversation: {conversation_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error updating Intercom conversation: {str(e)}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation details from Intercom"""
        try:
            url = f"{self.base_url}/conversations/{conversation_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Intercom conversation: {str(e)}")
            raise
    
    def _find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email in Intercom"""
        try:
            url = f"{self.base_url}/contacts/search"
            data = {
                'query': {
                    'field': 'email',
                    'operator': '=',
                    'value': email
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            contacts = response.json().get('data', [])
            if contacts:
                return contacts[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding Intercom user: {str(e)}")
            return None

class SupportManager:
    """Unified Support Manager"""
    
    def __init__(self):
        self.zendesk = ZendeskIntegration() if os.getenv('ZENDESK_SUBDOMAIN') else None
        self.intercom = IntercomIntegration() if os.getenv('INTERCOM_ACCESS_TOKEN') else None
        self.primary_service = os.getenv('PRIMARY_SUPPORT_SERVICE', 'zendesk')
    
    def create_support_ticket(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Create support ticket in primary service"""
        try:
            if self.primary_service == 'zendesk' and self.zendesk:
                return self.zendesk.create_ticket(ticket)
            elif self.primary_service == 'intercom' and self.intercom:
                return self.intercom.create_conversation(ticket)
            else:
                raise ValueError(f"Primary support service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error creating support ticket: {str(e)}")
            raise
    
    def update_support_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update support ticket in primary service"""
        try:
            if self.primary_service == 'zendesk' and self.zendesk:
                return self.zendesk.update_ticket(ticket_id, updates)
            elif self.primary_service == 'intercom' and self.intercom:
                return self.intercom.update_conversation(ticket_id, updates)
            else:
                raise ValueError(f"Primary support service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error updating support ticket: {str(e)}")
            raise
    
    def get_support_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get support ticket from primary service"""
        try:
            if self.primary_service == 'zendesk' and self.zendesk:
                return self.zendesk.get_ticket(ticket_id)
            elif self.primary_service == 'intercom' and self.intercom:
                return self.intercom.get_conversation(ticket_id)
            else:
                raise ValueError(f"Primary support service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error getting support ticket: {str(e)}")
            raise

# Predefined ticket templates
SUPPORT_TEMPLATES = {
    'technical_issue': {
        'subject': 'Technical Issue - {issue_type}',
        'description': '''
        User is experiencing a technical issue with Helm AI.
        
        Issue Type: {issue_type}
        User Plan: {user_plan}
        Error Details: {error_details}
        
        Steps to reproduce:
        {reproduction_steps}
        
        Expected behavior:
        {expected_behavior}
        
        Actual behavior:
        {actual_behavior}
        '''
    },
    'billing_question': {
        'subject': 'Billing Question - {question_type}',
        'description': '''
        User has a billing-related question.
        
        Question Type: {question_type}
        User Plan: {user_plan}
        Subscription ID: {subscription_id}
        
        Question Details:
        {question_details}
        
        Additional Information:
        {additional_info}
        '''
    },
    'feature_request': {
        'subject': 'Feature Request - {feature_name}',
        'description': '''
        User would like to request a new feature.
        
        Feature Name: {feature_name}
        User Plan: {user_plan}
        Use Case: {use_case}
        
        Feature Description:
        {feature_description}
        
        Business Impact:
        {business_impact}
        
        Priority: {priority}
        '''
    }
}

# Integration functions for Helm AI
def create_technical_support_ticket(user_data: Dict[str, Any], issue_data: Dict[str, Any]) -> Optional[str]:
    """Create technical support ticket"""
    try:
        support_manager = SupportManager()
        
        template = SUPPORT_TEMPLATES['technical_issue']
        
        ticket = SupportTicket(
            subject=template['subject'].format(issue_type=issue_data.get('issue_type', 'General')),
            description=template['description'].format(
                issue_type=issue_data.get('issue_type', 'General'),
                user_plan=user_data.get('plan', 'free'),
                error_details=issue_data.get('error_details', 'Not provided'),
                reproduction_steps=issue_data.get('reproduction_steps', 'Not provided'),
                expected_behavior=issue_data.get('expected_behavior', 'Not provided'),
                actual_behavior=issue_data.get('actual_behavior', 'Not provided')
            ),
            user_email=user_data['email'],
            user_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            priority=issue_data.get('priority', 'normal'),
            category='incident',
            tags=['technical', 'helm_ai', issue_data.get('issue_type', 'general')],
            custom_fields={
                'helm_ai_user_id': user_data.get('id'),
                'helm_ai_plan': user_data.get('plan', 'free'),
                'error_code': issue_data.get('error_code'),
                'browser': issue_data.get('browser'),
                'os': issue_data.get('os')
            }
        )
        
        result = support_manager.create_support_ticket(ticket)
        ticket_id = result.get('id') or result.get('ticket', {}).get('id')
        
        logger.info(f"Created technical support ticket {ticket_id} for user {user_data['email']}")
        return ticket_id
        
    except Exception as e:
        logger.error(f"Failed to create technical support ticket: {str(e)}")
        return None

def create_billing_support_ticket(user_data: Dict[str, Any], billing_data: Dict[str, Any]) -> Optional[str]:
    """Create billing support ticket"""
    try:
        support_manager = SupportManager()
        
        template = SUPPORT_TEMPLATES['billing_question']
        
        ticket = SupportTicket(
            subject=template['subject'].format(question_type=billing_data.get('question_type', 'General')),
            description=template['description'].format(
                question_type=billing_data.get('question_type', 'General'),
                user_plan=user_data.get('plan', 'free'),
                subscription_id=billing_data.get('subscription_id', 'Not provided'),
                question_details=billing_data.get('question_details', 'Not provided'),
                additional_info=billing_data.get('additional_info', 'Not provided')
            ),
            user_email=user_data['email'],
            user_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            priority=billing_data.get('priority', 'normal'),
            category='question',
            tags=['billing', 'helm_ai', billing_data.get('question_type', 'general')],
            custom_fields={
                'helm_ai_user_id': user_data.get('id'),
                'helm_ai_plan': user_data.get('plan', 'free'),
                'subscription_id': billing_data.get('subscription_id'),
                'invoice_id': billing_data.get('invoice_id'),
                'payment_method': billing_data.get('payment_method')
            }
        )
        
        result = support_manager.create_support_ticket(ticket)
        ticket_id = result.get('id') or result.get('ticket', {}).get('id')
        
        logger.info(f"Created billing support ticket {ticket_id} for user {user_data['email']}")
        return ticket_id
        
    except Exception as e:
        logger.error(f"Failed to create billing support ticket: {str(e)}")
        return None

def create_feature_request_ticket(user_data: Dict[str, Any], feature_data: Dict[str, Any]) -> Optional[str]:
    """Create feature request ticket"""
    try:
        support_manager = SupportManager()
        
        template = SUPPORT_TEMPLATES['feature_request']
        
        ticket = SupportTicket(
            subject=template['subject'].format(feature_name=feature_data.get('feature_name', 'New Feature')),
            description=template['description'].format(
                feature_name=feature_data.get('feature_name', 'New Feature'),
                user_plan=user_data.get('plan', 'free'),
                use_case=feature_data.get('use_case', 'Not provided'),
                feature_description=feature_data.get('feature_description', 'Not provided'),
                business_impact=feature_data.get('business_impact', 'Not provided'),
                priority=feature_data.get('priority', 'normal')
            ),
            user_email=user_data['email'],
            user_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            priority=feature_data.get('priority', 'normal'),
            category='task',
            tags=['feature_request', 'helm_ai', feature_data.get('category', 'general')],
            custom_fields={
                'helm_ai_user_id': user_data.get('id'),
                'helm_ai_plan': user_data.get('plan', 'free'),
                'feature_category': feature_data.get('category'),
                'estimated_value': feature_data.get('estimated_value'),
                'target_users': feature_data.get('target_users')
            }
        )
        
        result = support_manager.create_support_ticket(ticket)
        ticket_id = result.get('id') or result.get('ticket', {}).get('id')
        
        logger.info(f"Created feature request ticket {ticket_id} for user {user_data['email']}")
        return ticket_id
        
    except Exception as e:
        logger.error(f"Failed to create feature request ticket: {str(e)}")
        return None

def sync_user_to_support_system(user_data: Dict[str, Any]) -> bool:
    """Sync user to support system"""
    try:
        support_manager = SupportManager()
        
        user = SupportUser(
            email=user_data['email'],
            name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            user_id=user_data.get('id'),
            company=user_data.get('company'),
            plan=user_data.get('plan', 'free'),
            phone=user_data.get('phone'),
            timezone=user_data.get('timezone'),
            custom_attributes={
                'helm_ai_user_id': user_data.get('id'),
                'helm_ai_plan': user_data.get('plan', 'free'),
                'helm_ai_signup_date': user_data.get('created_at'),
                'total_detections': user_data.get('total_detections', 0),
                'last_active': user_data.get('last_active')
            }
        )
        
        if support_manager.primary_service == 'zendesk' and support_manager.zendesk:
            support_manager.zendesk.create_or_update_user(user)
        elif support_manager.primary_service == 'intercom' and support_manager.intercom:
            support_manager.intercom.create_or_update_user(user)
        
        logger.info(f"Synced user {user_data['email']} to support system")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync user to support system: {str(e)}")
        return False
