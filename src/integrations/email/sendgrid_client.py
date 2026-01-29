"""
Helm AI SendGrid Integration Client
This module provides integration with SendGrid for email marketing and transactional emails
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class SendGridClient:
    """SendGrid API client for email marketing"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SendGrid client
        
        Args:
            api_key: SendGrid API key
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SendGrid API key is required")
        
        self.base_url = "https://api.sendgrid.com/v3"
        
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
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to SendGrid API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"SendGrid API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # Email Sending
    def send_email(self, 
                   from_email: str,
                   to_emails: List[str],
                   subject: str,
                   content: str,
                   content_type: str = "text/plain",
                   cc_emails: List[str] = None,
                   bcc_emails: List[str] = None,
                   attachments: List[Dict[str, Any]] = None,
                   template_id: str = None,
                   template_data: Dict[str, Any] = None,
                   categories: List[str] = None,
                   custom_args: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Send email via SendGrid
        
        Args:
            from_email: Sender email address
            to_emails: List of recipient email addresses
            subject: Email subject
            content: Email content
            content_type: Content type (text/plain or text/html)
            cc_emails: List of CC recipients
            bcc_emails: List of BCC recipients
            attachments: List of file attachments
            template_id: SendGrid template ID
            template_data: Template substitution data
            categories: Email categories for tracking
            custom_args: Custom tracking arguments
            
        Returns:
            SendGrid API response
        """
        # Build personalizations
        personalizations = []
        
        # Split recipients into chunks of 1000 (SendGrid limit)
        chunk_size = 1000
        for i in range(0, len(to_emails), chunk_size):
            chunk = to_emails[i:i + chunk_size]
            personalization = {
                "to": [{"email": email} for email in chunk]
            }
            
            if cc_emails:
                personalization["cc"] = [{"email": email} for email in cc_emails]
            
            if bcc_emails:
                personalization["bcc"] = [{"email": email} for email in bcc_emails]
            
            if template_data:
                personalization["dynamic_template_data"] = template_data
            
            personalizations.append(personalization)
        
        # Build email data
        email_data = {
            "personalizations": personalizations,
            "from": {"email": from_email},
            "subject": subject
        }
        
        # Add content or template
        if template_id:
            email_data["template_id"] = template_id
        else:
            email_data["content"] = [
                {
                    "type": content_type,
                    "value": content
                }
            ]
        
        # Add optional fields
        if attachments:
            email_data["attachments"] = attachments
        
        if categories:
            email_data["categories"] = categories
        
        if custom_args:
            email_data["custom_args"] = custom_args
        
        # Add tracking settings
        email_data["tracking_settings"] = {
            "click_tracking": {"enable": True, "enable_text": True},
            "open_tracking": {"enable": True},
            "subscription_tracking": {"enable": False},
            "ganalytics": {"enable": True, "utm_source": "helm-ai", "utm_medium": "email"}
        }
        
        return self._make_request('POST', '/mail/send', json=email_data)
    
    # Contact Management
    def add_contact_to_list(self, email: str, list_id: str, fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add contact to specific list"""
        contact_data = {
            "contacts": [
                {
                    "email": email,
                    **(fields or {})
                }
            ],
            "list_ids": [list_id]
        }
        
        return self._make_request('PUT', '/marketing/contacts', json=contact_data)
    
    def create_contact_list(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new contact list"""
        data = {
            "name": name,
            "description": description
        }
        
        return self._make_request('POST', '/marketing/lists', json=data)
    
    def get_contact_lists(self) -> Dict[str, Any]:
        """Get all contact lists"""
        return self._make_request('GET', '/marketing/lists')
    
    def delete_contact_from_list(self, email: str, list_id: str) -> Dict[str, Any]:
        """Delete contact from list"""
        # First get contact ID
        contact_result = self.search_contacts(email)
        contacts = contact_result.get('result', [])
        
        if not contacts:
            raise ValueError(f"Contact {email} not found")
        
        contact_id = contacts[0]['id']
        
        return self._make_request('DELETE', f'/marketing/lists/{list_id}/contacts/{contact_id}')
    
    def search_contacts(self, email: str) -> Dict[str, Any]:
        """Search for contacts by email"""
        params = {'email': email}
        return self._make_request('GET', '/marketing/contacts/search', params=params)
    
    # Template Management
    def create_template(self, name: str, generation: str = "dynamic") -> Dict[str, Any]:
        """Create a new email template"""
        data = {
            "name": name,
            "generation": generation
        }
        
        return self._make_request('POST', '/templates', json=data)
    
    def get_templates(self) -> Dict[str, Any]:
        """Get all templates"""
        return self._make_request('GET', '/templates')
    
    def create_template_version(self, 
                               template_id: str,
                               name: str,
                               subject: str,
                               html_content: str,
                               plain_content: str = "",
                               active: bool = True) -> Dict[str, Any]:
        """Create a new version of a template"""
        data = {
            "template_id": template_id,
            "name": name,
            "subject": subject,
            "html_content": html_content,
            "plain_content": plain_content,
            "active": active
        }
        
        return self._make_request('POST', '/templates/versions', json=data)
    
    # Campaign Management
    def create_campaign(self, 
                       name: str,
                       subject: str,
                       sender_id: int,
                       list_ids: List[str],
                       categories: List[str] = None,
                       html_content: str = None,
                       plain_content: str = None,
                       template_id: str = None) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        data = {
            "name": name,
            "subject": subject,
            "sender_id": sender_id,
            "list_ids": list_ids,
            "categories": categories or []
        }
        
        if template_id:
            data["template_id"] = template_id
        else:
            if html_content:
                data["html_content"] = html_content
            if plain_content:
                data["plain_content"] = plain_content
        
        return self._make_request('POST', '/marketing/campaigns', json=data)
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send a marketing campaign"""
        return self._make_request('POST', f'/marketing/campaigns/{campaign_id}/schedules', json={"send_at": "now"})
    
    def schedule_campaign(self, campaign_id: str, send_at: str) -> Dict[str, Any]:
        """Schedule a marketing campaign"""
        return self._make_request('POST', f'/marketing/campaigns/{campaign_id}/schedules', json={"send_at": send_at})
    
    # Analytics and Reporting
    def get_email_stats(self, 
                       start_date: str = None,
                       end_date: str = None,
                       aggregated_by: str = "day") -> Dict[str, Any]:
        """Get email statistics"""
        params = {
            "aggregated_by": aggregated_by
        }
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._make_request('GET', '/stats', params=params)
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign-specific statistics"""
        return self._make_request('GET', f'/marketing/campaigns/{campaign_id}/stats')
    
    def get_bounce_reports(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get bounce reports"""
        params = {}
        if start_date:
            params["start_time"] = start_date
        if end_date:
            params["end_time"] = end_date
        
        return self._make_request('GET', '/suppression/bounces', params=params)
    
    def get_spam_reports(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get spam reports"""
        params = {}
        if start_date:
            params["start_time"] = start_date
        if end_date:
            params["end_time"] = end_date
        
        return self._make_request('GET', '/suppression/spam_reports', params=params)
    
    # Suppression Management
    def suppress_email(self, email: str) -> Dict[str, Any]:
        """Add email to suppression list"""
        data = {"recipient_emails": [email]}
        return self._make_request('POST', '/asm/suppressions/global', json=data)
    
    def unsuppress_email(self, email: str) -> Dict[str, Any]:
        """Remove email from suppression list"""
        return self._make_request('DELETE', f'/asm/suppressions/global/{email}')
    
    # Sender Management
    def get_senders(self) -> Dict[str, Any]:
        """Get all verified senders"""
        return self._make_request('GET', '/senders')
    
    def verify_sender(self, email: str, nickname: str, from_name: str, reply_to: str = None, address: str = None) -> Dict[str, Any]:
        """Verify a new sender"""
        data = {
            "nickname": nickname,
            "from_email": email,
            "from_name": from_name,
            "reply_to": reply_to or email,
            "address": address or "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105",
            "country": "United States"
        }
        
        return self._make_request('POST', '/senders', json=data)
    
    # Webhooks
    def create_webhook(self, 
                      name: str,
                      url: str,
                      events: List[str],
                      enabled: bool = True) -> Dict[str, Any]:
        """Create event webhook"""
        data = {
            "name": name,
            "url": url,
            "events": events,
            "enabled": enabled
        }
        
        return self._make_request('POST', '/user/webhooks', json=data)
    
    def get_webhooks(self) -> Dict[str, Any]:
        """Get all webhooks"""
        return self._make_request('GET', '/user/webhooks')
    
    def update_webhook(self, webhook_id: str, **kwargs) -> Dict[str, Any]:
        """Update webhook"""
        return self._make_request('PATCH', f'/user/webhooks/{webhook_id}', json=kwargs)


# Helm AI specific email operations
class HelmAIEmailMarketing:
    """Helm AI specific email marketing operations using SendGrid"""
    
    def __init__(self):
        self.sendgrid = SendGridClient()
        self.default_sender = "noreply@helm-ai.com"
        self.lists = {}
        self.templates = {}
        self._initialize_lists_and_templates()
    
    def _initialize_lists_and_templates(self):
        """Initialize default lists and templates"""
        try:
            # Get or create default lists
            lists_response = self.sendgrid.get_contact_lists()
            existing_lists = {lst['name']: lst['id'] for lst in lists_response.get('result', [])}
            
            default_lists = {
                'Newsletter Subscribers': 'newsletter_subscribers',
                'Trial Users': 'trial_users',
                'Free Users': 'free_users',
                'Pro Users': 'pro_users',
                'Business Users': 'business_users',
                'Enterprise Users': 'enterprise_users',
                'Inactive Users': 'inactive_users',
                'Churned Users': 'churned_users'
            }
            
            for list_name, list_key in default_lists.items():
                if list_name in existing_lists:
                    self.lists[list_key] = existing_lists[list_name]
                else:
                    new_list = self.sendgrid.create_contact_list(list_name, f"Auto-generated list for {list_name}")
                    self.lists[list_key] = new_list['id']
            
            # Get templates
            templates_response = self.sendgrid.get_templates()
            self.templates = {tmpl['name']: tmpl['id'] for tmpl in templates_response.get('templates', [])}
            
        except Exception as e:
            logger.error(f"Failed to initialize lists and templates: {e}")
    
    def send_welcome_email(self, email: str, first_name: str, plan: str = "free") -> Dict[str, Any]:
        """Send welcome email to new user"""
        template_data = {
            "first_name": first_name,
            "plan": plan.title(),
            "login_url": "https://helm-ai.com/login",
            "dashboard_url": "https://helm-ai.com/dashboard"
        }
        
        return self.sendgrid.send_email(
            from_email=self.default_sender,
            to_emails=[email],
            subject=f"Welcome to Helm AI, {first_name}!",
            content="",
            template_id=self.templates.get("Welcome Email"),
            template_data=template_data,
            categories=["welcome", "onboarding"],
            custom_args={"user_type": plan}
        )
    
    def send_trial_expiration_reminder(self, email: str, first_name: str, days_left: int) -> Dict[str, Any]:
        """Send trial expiration reminder"""
        template_data = {
            "first_name": first_name,
            "days_left": days_left,
            "upgrade_url": "https://helm-ai.com/pricing",
            "dashboard_url": "https://helm-ai.com/dashboard"
        }
        
        return self.sendgrid.send_email(
            from_email=self.default_sender,
            to_emails=[email],
            subject=f"Your Helm AI Trial Expires in {days_left} Days",
            content="",
            template_id=self.templates.get("Trial Expiration"),
            template_data=template_data,
            categories=["trial", "retention"],
            custom_args={"days_left": str(days_left)}
        )
    
    def send_newsletter(self, subject: str, content: str, segment: str = "all") -> Dict[str, Any]:
        """Send marketing newsletter"""
        # Determine recipient list based on segment
        if segment == "all":
            list_ids = [self.lists['newsletter_subscribers']]
        elif segment == "free":
            list_ids = [self.lists['free_users']]
        elif segment == "paid":
            list_ids = [
                self.lists['pro_users'],
                self.lists['business_users'],
                self.lists['enterprise_users']
            ]
        else:
            list_ids = [self.lists.get(segment, self.lists['newsletter_subscribers'])]
        
        # Create campaign
        campaign = self.sendgrid.create_campaign(
            name=f"Newsletter: {subject}",
            subject=subject,
            sender_id=1,  # You'll need to get the actual sender ID
            list_ids=list_ids,
            categories=["newsletter", "marketing"],
            html_content=content
        )
        
        # Send campaign
        return self.sendgrid.send_campaign(campaign['id'])
    
    def send_feature_announcement(self, feature_name: str, description: str, target_segment: str = "all") -> Dict[str, Any]:
        """Send feature announcement email"""
        template_data = {
            "feature_name": feature_name,
            "feature_description": description,
            "learn_more_url": f"https://helm-ai.com/features/{feature_name.lower().replace(' ', '-')}",
            "dashboard_url": "https://helm-ai.com/dashboard"
        }
        
        # Determine recipient list
        list_ids = [self.lists.get(target_segment, self.lists['newsletter_subscribers'])]
        
        return self.sendgrid.send_email(
            from_email=self.default_sender,
            to_emails=[],  # Will be populated by list
            subject=f"New Feature: {feature_name}",
            content="",
            template_id=self.templates.get("Feature Announcement"),
            template_data=template_data,
            categories=["feature", "announcement"],
            custom_args={"feature": feature_name}
        )
    
    def send_reactivation_campaign(self, email: str, first_name: str, last_login: str) -> Dict[str, Any]:
        """Send reactivation email to inactive users"""
        template_data = {
            "first_name": first_name,
            "last_login": last_login,
            "dashboard_url": "https://helm-ai.com/dashboard",
            "new_features_url": "https://helm-ai.com/features"
        }
        
        return self.sendgrid.send_email(
            from_email=self.default_sender,
            to_emails=[email],
            subject=f"We miss you at Helm AI, {first_name}!",
            content="",
            template_id=self.templates.get("Reactivation"),
            template_data=template_data,
            categories=["reactivation", "retention"],
            custom_args={"campaign": "reactivation"}
        )
    
    def send_billing_notification(self, email: str, first_name: str, amount: float, due_date: str) -> Dict[str, Any]:
        """Send billing notification"""
        template_data = {
            "first_name": first_name,
            "amount": f"${amount:.2f}",
            "due_date": due_date,
            "billing_url": "https://helm-ai.com/billing",
            "support_url": "https://helm-ai.com/support"
        }
        
        return self.sendgrid.send_email(
            from_email="billing@helm-ai.com",
            to_emails=[email],
            subject=f"Helm AI Invoice - ${amount:.2f} due {due_date}",
            content="",
            template_id=self.templates.get("Billing Notification"),
            template_data=template_data,
            categories=["billing", "notification"],
            custom_args={"amount": str(amount)}
        )
    
    def add_user_to_segment(self, email: str, segment: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add user to email segment"""
        list_id = self.lists.get(segment)
        if not list_id:
            raise ValueError(f"Segment '{segment}' not found")
        
        # Prepare contact fields
        fields = {
            "first_name": user_data.get('first_name', ''),
            "last_name": user_data.get('last_name', ''),
            "plan": user_data.get('plan', 'free'),
            "signup_date": user_data.get('signup_date', ''),
            "company": user_data.get('company', ''),
            "job_title": user_data.get('job_title', '')
        }
        
        return self.sendgrid.add_contact_to_list(email, list_id, fields)
    
    def move_user_between_segments(self, email: str, from_segment: str, to_segment: str) -> Dict[str, Any]:
        """Move user from one segment to another"""
        # Remove from old segment
        try:
            self.sendgrid.delete_contact_from_list(email, self.lists[from_segment])
        except Exception as e:
            logger.warning(f"Failed to remove user from {from_segment}: {e}")
        
        # Add to new segment
        return self.add_user_to_segment(email, to_segment)
    
    def get_email_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get comprehensive email analytics"""
        stats = self.sendgrid.get_email_stats(start_date, end_date)
        
        # Get additional metrics
        bounces = self.sendgrid.get_bounce_reports(start_date, end_date)
        spam_reports = self.sendgrid.get_spam_reports(start_date, end_date)
        
        return {
            "general_stats": stats,
            "bounces": bounces,
            "spam_reports": spam_reports,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
