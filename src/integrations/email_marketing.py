"""
Helm AI Email Marketing Integration Module
Integrates with SendGrid and Mailchimp for email campaigns
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
class EmailContact:
    """Email marketing contact data structure"""
    email: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

@dataclass
class EmailCampaign:
    """Email campaign data structure"""
    name: str
    subject: str
    content: str
    list_id: str
    send_time: Optional[datetime] = None
    template_id: Optional[str] = None
    segment_id: Optional[str] = None

class SendGridIntegration:
    """SendGrid Email Marketing Integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self.base_url = "https://api.sendgrid.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def add_contact(self, contact: EmailContact, list_ids: List[str] = None) -> Dict[str, Any]:
        """Add contact to SendGrid"""
        try:
            url = f"{self.base_url}/marketing/contacts"
            
            # Prepare contact data
            contact_data = {
                'contacts': [
                    {
                        'email': contact.email,
                        'first_name': contact.first_name,
                        'last_name': contact.last_name,
                        'custom_fields': {}
                    }
                ]
            }
            
            # Add custom fields
            if contact.custom_fields:
                contact_data['contacts'][0]['custom_fields'].update(contact.custom_fields)
            
            # Add list IDs
            if list_ids:
                contact_data['list_ids'] = list_ids
            
            response = requests.put(url, headers=self.headers, json=contact_data)
            response.raise_for_status()
            
            logger.info(f"Added SendGrid contact: {contact.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error adding SendGrid contact: {str(e)}")
            raise
    
    def create_campaign(self, campaign: EmailCampaign) -> Dict[str, Any]:
        """Create email campaign in SendGrid"""
        try:
            url = f"{self.base_url}/marketing/campaigns"
            
            campaign_data = {
                'name': campaign.name,
                'subject': campaign.subject,
                'html_content': campaign.content,
                'list_ids': [campaign.list_id],
                'sender_id': self._get_default_sender_id()
            }
            
            if campaign.send_time:
                campaign_data['send_at'] = int(campaign.send_time.timestamp())
            
            if campaign.template_id:
                campaign_data['template_id'] = campaign.template_id
            
            if campaign.segment_id:
                campaign_data['segment_ids'] = [campaign.segment_id]
            
            response = requests.post(url, headers=self.headers, json=campaign_data)
            response.raise_for_status()
            
            logger.info(f"Created SendGrid campaign: {campaign.name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating SendGrid campaign: {str(e)}")
            raise
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send email campaign"""
        try:
            url = f"{self.base_url}/marketing/campaigns/{campaign_id}/schedules/now"
            
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Sent SendGrid campaign: {campaign_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending SendGrid campaign: {str(e)}")
            raise
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            url = f"{self.base_url}/marketing/campaigns/{campaign_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting SendGrid campaign stats: {str(e)}")
            raise
    
    def _get_default_sender_id(self) -> str:
        """Get default sender ID"""
        try:
            url = f"{self.base_url}/marketing/senders"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            senders = response.json().get('results', [])
            if senders:
                return senders[0]['id']
            
            raise ValueError("No sender found in SendGrid")
            
        except Exception as e:
            logger.error(f"Error getting SendGrid sender ID: {str(e)}")
            raise

class MailchimpIntegration:
    """Mailchimp Email Marketing Integration"""
    
    def __init__(self, api_key: str = None, server_prefix: str = None):
        self.api_key = api_key or os.getenv('MAILCHIMP_API_KEY')
        self.server_prefix = server_prefix or os.getenv('MAILCHIMP_SERVER_PREFIX')
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def add_contact(self, contact: EmailContact, list_id: str) -> Dict[str, Any]:
        """Add contact to Mailchimp list"""
        try:
            url = f"{self.base_url}/lists/{list_id}/members"
            
            member_data = {
                'email_address': contact.email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': contact.first_name,
                    'LNAME': contact.last_name
                }
            }
            
            if contact.company:
                member_data['merge_fields']['COMPANY'] = contact.company
            
            if contact.phone:
                member_data['merge_fields']['PHONE'] = contact.phone
            
            if contact.tags:
                member_data['tags'] = contact.tags
            
            response = requests.post(url, headers=self.headers, json=member_data)
            response.raise_for_status()
            
            logger.info(f"Added Mailchimp contact: {contact.email}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error adding Mailchimp contact: {str(e)}")
            raise
    
    def create_campaign(self, campaign: EmailCampaign, list_id: str) -> Dict[str, Any]:
        """Create email campaign in Mailchimp"""
        try:
            url = f"{self.base_url}/campaigns"
            
            campaign_data = {
                'type': 'regular',
                'recipients': {
                    'list_id': list_id
                },
                'settings': {
                    'subject_line': campaign.subject,
                    'from_name': 'Helm AI',
                    'reply_to': 'support@helm-ai.com',
                    'title': campaign.name
                }
            }
            
            if campaign.template_id:
                campaign_data['template']['id'] = int(campaign.template_id)
            
            response = requests.post(url, headers=self.headers, json=campaign_data)
            response.raise_for_status()
            
            campaign_result = response.json()
            
            # Set content
            if campaign.content:
                self._set_campaign_content(campaign_result['id'], campaign.content)
            
            logger.info(f"Created Mailchimp campaign: {campaign.name}")
            return campaign_result
            
        except Exception as e:
            logger.error(f"Error creating Mailchimp campaign: {str(e)}")
            raise
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send email campaign"""
        try:
            url = f"{self.base_url}/campaigns/{campaign_id}/actions/send"
            
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Sent Mailchimp campaign: {campaign_id}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending Mailchimp campaign: {str(e)}")
            raise
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            url = f"{self.base_url}/reports/{campaign_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Mailchimp campaign stats: {str(e)}")
            raise
    
    def _set_campaign_content(self, campaign_id: str, content: str) -> Dict[str, Any]:
        """Set campaign content"""
        try:
            url = f"{self.base_url}/campaigns/{campaign_id}/content"
            
            content_data = {
                'html': content
            }
            
            response = requests.put(url, headers=self.headers, json=content_data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error setting Mailchimp campaign content: {str(e)}")
            raise

class EmailMarketingManager:
    """Unified Email Marketing Manager"""
    
    def __init__(self):
        self.sendgrid = SendGridIntegration() if os.getenv('SENDGRID_API_KEY') else None
        self.mailchimp = MailchimpIntegration() if os.getenv('MAILCHIMP_API_KEY') else None
        self.primary_service = os.getenv('PRIMARY_EMAIL_SERVICE', 'sendgrid')
    
    def add_contact(self, contact: EmailContact, list_id: str = None, list_ids: List[str] = None) -> Dict[str, Any]:
        """Add contact to primary email service"""
        try:
            if self.primary_service == 'sendgrid' and self.sendgrid:
                return self.sendgrid.add_contact(contact, list_ids)
            elif self.primary_service == 'mailchimp' and self.mailchimp:
                if not list_id:
                    raise ValueError("List ID required for Mailchimp")
                return self.mailchimp.add_contact(contact, list_id)
            else:
                raise ValueError(f"Primary email service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error adding contact to email service: {str(e)}")
            raise
    
    def create_campaign(self, campaign: EmailCampaign, list_id: str = None) -> Dict[str, Any]:
        """Create campaign in primary email service"""
        try:
            if self.primary_service == 'sendgrid' and self.sendgrid:
                return self.sendgrid.create_campaign(campaign)
            elif self.primary_service == 'mailchimp' and self.mailchimp:
                if not list_id:
                    raise ValueError("List ID required for Mailchimp")
                return self.mailchimp.create_campaign(campaign, list_id)
            else:
                raise ValueError(f"Primary email service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send campaign via primary email service"""
        try:
            if self.primary_service == 'sendgrid' and self.sendgrid:
                return self.sendgrid.send_campaign(campaign_id)
            elif self.primary_service == 'mailchimp' and self.mailchimp:
                return self.mailchimp.send_campaign(campaign_id)
            else:
                raise ValueError(f"Primary email service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error sending campaign: {str(e)}")
            raise
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics from primary email service"""
        try:
            if self.primary_service == 'sendgrid' and self.sendgrid:
                return self.sendgrid.get_campaign_stats(campaign_id)
            elif self.primary_service == 'mailchimp' and self.mailchimp:
                return self.mailchimp.get_campaign_stats(campaign_id)
            else:
                raise ValueError(f"Primary email service '{self.primary_service}' not configured")
                
        except Exception as e:
            logger.error(f"Error getting campaign stats: {str(e)}")
            raise

# Predefined email templates
EMAIL_TEMPLATES = {
    'welcome': {
        'subject': 'Welcome to Helm AI - Your Anti-Cheat Journey Begins!',
        'content': '''
        <html>
        <body>
            <h1>Welcome to Helm AI! 🎯</h1>
            <p>Thank you for joining Helm AI, the most advanced anti-cheat detection system.</p>
            <p>What's next?</p>
            <ul>
                <li>Complete your profile setup</li>
                <li>Explore our detection features</li>
                <li>Check out our documentation</li>
            </ul>
            <p>Get started now: <a href="https://helm-ai.com/dashboard">Dashboard</a></p>
            <p>Best regards,<br>The Helm AI Team</p>
        </body>
        </html>
        '''
    },
    'trial_ending': {
        'subject': 'Your Helm AI Trial is Ending Soon',
        'content': '''
        <html>
        <body>
            <h1>Trial Ending Soon ⏰</h1>
            <p>Your Helm AI trial will end in 3 days.</p>
            <p>Upgrade now to continue enjoying:</p>
            <ul>
                <li>Advanced AI detection</li>
                <li>Real-time monitoring</li>
                <li>Priority support</li>
            </ul>
            <p>Upgrade now: <a href="https://helm-ai.com/billing">Upgrade</a></p>
            <p>Best regards,<br>The Helm AI Team</p>
        </body>
        </html>
        '''
    },
    'payment_failed': {
        'subject': 'Payment Failed - Action Required',
        'content': '''
        <html>
        <body>
            <h1>Payment Failed 💳</h1>
            <p>We were unable to process your recent payment.</p>
            <p>Please update your payment method to avoid service interruption.</p>
            <p>Update payment: <a href="https://helm-ai.com/billing">Update Payment</a></p>
            <p>If you believe this is an error, please contact our support team.</p>
            <p>Best regards,<br>The Helm AI Team</p>
        </body>
        </html>
        '''
    }
}

# Integration functions for Helm AI
def add_user_to_email_list(user_data: Dict[str, Any]) -> bool:
    """Add Helm AI user to email marketing list"""
    try:
        email_manager = EmailMarketingManager()
        
        contact = EmailContact(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            company=user_data.get('company'),
            phone=user_data.get('phone'),
            tags=['helm_ai_users', user_data.get('plan', 'free')],
            custom_fields={
                'helm_ai_user_id': user_data['id'],
                'helm_ai_plan': user_data.get('plan', 'free'),
                'helm_ai_signup_date': user_data['created_at']
            }
        )
        
        list_id = os.getenv('HELM_AI_EMAIL_LIST_ID')
        list_ids = os.getenv('HELM_AI_EMAIL_LIST_IDS', '').split(',') if os.getenv('HELM_AI_EMAIL_LIST_IDS') else None
        
        result = email_manager.add_contact(contact, list_id, list_ids)
        logger.info(f"Added user {user_data['email']} to email list")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add user to email list: {str(e)}")
        return False

def send_welcome_email(user_email: str, user_name: str = None) -> bool:
    """Send welcome email to new user"""
    try:
        email_manager = EmailMarketingManager()
        
        template = EMAIL_TEMPLATES['welcome']
        campaign = EmailCampaign(
            name=f"Welcome - {user_email}",
            subject=template['subject'].replace('Welcome', f'Welcome {user_name or ""}'),
            content=template['content'],
            list_id=os.getenv('HELM_AI_EMAIL_LIST_ID')
        )
        
        # Create campaign
        campaign_result = email_manager.create_campaign(campaign)
        campaign_id = campaign_result['id']
        
        # Send campaign
        email_manager.send_campaign(campaign_id)
        
        logger.info(f"Sent welcome email to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False

def send_trial_ending_email(user_email: str, days_remaining: int = 3) -> bool:
    """Send trial ending reminder email"""
    try:
        email_manager = EmailMarketingManager()
        
        template = EMAIL_TEMPLATES['trial_ending']
        campaign = EmailCampaign(
            name=f"Trial Ending - {user_email}",
            subject=template['subject'],
            content=template['content'].replace('3 days', f'{days_remaining} days'),
            list_id=os.getenv('HELM_AI_EMAIL_LIST_ID')
        )
        
        # Create campaign
        campaign_result = email_manager.create_campaign(campaign)
        campaign_id = campaign_result['id']
        
        # Send campaign
        email_manager.send_campaign(campaign_id)
        
        logger.info(f"Sent trial ending email to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send trial ending email: {str(e)}")
        return False

def send_payment_failed_email(user_email: str) -> bool:
    """Send payment failed notification"""
    try:
        email_manager = EmailMarketingManager()
        
        template = EMAIL_TEMPLATES['payment_failed']
        campaign = EmailCampaign(
            name=f"Payment Failed - {user_email}",
            subject=template['subject'],
            content=template['content'],
            list_id=os.getenv('HELM_AI_EMAIL_LIST_ID')
        )
        
        # Create campaign
        campaign_result = email_manager.create_campaign(campaign)
        campaign_id = campaign_result['id']
        
        # Send campaign
        email_manager.send_campaign(campaign_id)
        
        logger.info(f"Sent payment failed email to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment failed email: {str(e)}")
        return False
