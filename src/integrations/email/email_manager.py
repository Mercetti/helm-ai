"""
Helm AI Email Manager
This module provides a unified interface for email marketing across multiple platforms
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from .sendgrid_client import SendGridClient, HelmAIEmailMarketing as SendGridMarketing
from .mailchimp_client import MailchimpClient, HelmAIMailchimp as MailchimpMarketing

logger = logging.getLogger(__name__)

class EmailProvider(Enum):
    """Supported email providers"""
    SENDGRID = "sendgrid"
    MAILCHIMP = "mailchimp"

@dataclass
class EmailMessage:
    """Email message data structure"""
    to_emails: List[str]
    subject: str
    content: str
    content_type: str = "text/html"
    from_email: str = "noreply@helm-ai.com"
    cc_emails: List[str] = None
    bcc_emails: List[str] = None
    attachments: List[Dict[str, Any]] = None
    categories: List[str] = None
    custom_args: Dict[str, str] = None

@dataclass
class EmailTemplate:
    """Email template data structure"""
    name: str
    subject: str
    html_content: str
    plain_content: str = ""
    variables: Dict[str, str] = None

@dataclass
class EmailCampaign:
    """Email campaign data structure"""
    name: str
    subject: str
    content: str
    target_segments: List[str]
    scheduled_time: Optional[str] = None
    template_id: Optional[str] = None

@dataclass
class EmailUser:
    """Email user data structure"""
    email: str
    first_name: str
    last_name: str
    plan: str = "free"
    company: str = ""
    job_title: str = ""
    signup_date: Optional[str] = None
    last_login: Optional[str] = None
    usage_count: int = 0
    tags: List[str] = None

class EmailManager:
    """Unified email manager supporting multiple providers"""
    
    def __init__(self, primary_provider: EmailProvider = EmailProvider.SENDGRID):
        """
        Initialize email manager
        
        Args:
            primary_provider: Primary email provider to use
        """
        self.primary_provider = primary_provider
        self.providers = {}
        
        # Initialize primary provider
        self._initialize_provider(primary_provider)
        
        # Initialize secondary provider if configured
        if primary_provider == EmailProvider.SENDGRID:
            if os.getenv('MAILCHIMP_API_KEY'):
                self._initialize_provider(EmailProvider.MAILCHIMP)
        else:
            if os.getenv('SENDGRID_API_KEY'):
                self._initialize_provider(EmailProvider.SENDGRID)
    
    def _initialize_provider(self, provider: EmailProvider):
        """Initialize a specific email provider"""
        try:
            if provider == EmailProvider.SENDGRID:
                self.providers[provider] = SendGridMarketing()
                logger.info("SendGrid email provider initialized successfully")
            elif provider == EmailProvider.MAILCHIMP:
                self.providers[provider] = MailchimpMarketing()
                logger.info("Mailchimp email provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {provider.value}: {e}")
            raise
    
    def send_email(self, message: EmailMessage, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send email message
        
        Args:
            message: Email message data
            provider: Specific provider to use (defaults to primary)
            
        Returns:
            Send result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.sendgrid.send_email(
                    from_email=message.from_email,
                    to_emails=message.to_emails,
                    subject=message.subject,
                    content=message.content,
                    content_type=message.content_type,
                    cc_emails=message.cc_emails,
                    bcc_emails=message.bcc_emails,
                    attachments=message.attachments,
                    categories=message.categories,
                    custom_args=message.custom_args
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                # Mailchimp doesn't have direct send API, create campaign instead
                campaign = email_client.send_newsletter_campaign(
                    subject=message.subject,
                    content=message.content,
                    target_lists=['newsletter']
                )
                return campaign
                
        except Exception as e:
            logger.error(f"Failed to send email via {provider.value}: {e}")
            raise
    
    def add_user_to_email_list(self, user: EmailUser, list_name: str, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Add user to email list
        
        Args:
            user: User data
            list_name: List/segment name
            provider: Specific provider to use
            
        Returns:
            Add result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.add_user_to_segment(
                    email=user.email,
                    segment=list_name,
                    user_data={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'plan': user.plan,
                        'company': user.company,
                        'job_title': user.job_title,
                        'signup_date': user.signup_date
                    }
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                return email_client.add_user_to_list(
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    list_key=list_name,
                    plan=user.plan,
                    company=user.company,
                    job_title=user.job_title,
                    tags=user.tags
                )
                
        except Exception as e:
            logger.error(f"Failed to add user to email list via {provider.value}: {e}")
            raise
    
    def send_welcome_email(self, user: EmailUser, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send welcome email to new user
        
        Args:
            user: User data
            provider: Specific provider to use
            
        Returns:
            Send result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.send_welcome_email(
                    email=user.email,
                    first_name=user.first_name,
                    plan=user.plan
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                return email_client.send_welcome_campaign(
                    email=user.email,
                    first_name=user.first_name,
                    plan=user.plan
                )
                
        except Exception as e:
            logger.error(f"Failed to send welcome email via {provider.value}: {e}")
            raise
    
    def send_newsletter(self, campaign: EmailCampaign, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send newsletter campaign
        
        Args:
            campaign: Campaign data
            provider: Specific provider to use
            
        Returns:
            Campaign result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.send_newsletter(
                    subject=campaign.subject,
                    content=campaign.content,
                    segment=campaign.target_segments[0] if campaign.target_segments else "all"
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                return email_client.send_newsletter_campaign(
                    subject=campaign.subject,
                    content=campaign.content,
                    target_lists=campaign.target_segments
                )
                
        except Exception as e:
            logger.error(f"Failed to send newsletter via {provider.value}: {e}")
            raise
    
    def send_trial_expiration_reminder(self, user: EmailUser, days_left: int, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send trial expiration reminder
        
        Args:
            user: User data
            days_left: Days until trial expires
            provider: Specific provider to use
            
        Returns:
            Send result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.send_trial_expiration_reminder(
                    email=user.email,
                    first_name=user.first_name,
                    days_left=days_left
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                # Create custom campaign for trial expiration
                subject = f"Your Helm AI Trial Expires in {days_left} Days"
                content = f"""
                <h1>Trial Expiration Reminder</h1>
                <p>Hi {user.first_name},</p>
                <p>Your Helm AI trial expires in {days_left} days.</p>
                <p><a href="https://helm-ai.com/pricing">Upgrade Now</a></p>
                """
                
                return email_client.send_newsletter_campaign(
                    subject=subject,
                    content=content,
                    target_lists=['trial_users']
                )
                
        except Exception as e:
            logger.error(f"Failed to send trial expiration reminder via {provider.value}: {e}")
            raise
    
    def send_feature_announcement(self, feature_name: str, description: str, target_segments: List[str], provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send feature announcement
        
        Args:
            feature_name: Name of the feature
            description: Feature description
            target_segments: Target user segments
            provider: Specific provider to use
            
        Returns:
            Send result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.send_feature_announcement(
                    feature_name=feature_name,
                    description=description,
                    target_segment=target_segments[0] if target_segments else "all"
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                subject = f"New Feature: {feature_name}"
                content = f"""
                <h1>Exciting New Feature!</h1>
                <p>We're excited to announce {feature_name}!</p>
                <p>{description}</p>
                <p><a href="https://helm-ai.com/features/{feature_name.lower().replace(' ', '-')}">Learn More</a></p>
                """
                
                return email_client.send_newsletter_campaign(
                    subject=subject,
                    content=content,
                    target_lists=target_segments
                )
                
        except Exception as e:
            logger.error(f"Failed to send feature announcement via {provider.value}: {e}")
            raise
    
    def send_reactivation_campaign(self, user: EmailUser, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Send reactivation campaign to inactive user
        
        Args:
            user: User data
            provider: Specific provider to use
            
        Returns:
            Send result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.send_reactivation_campaign(
                    email=user.email,
                    first_name=user.first_name,
                    last_login=user.last_login or ""
                )
            
            elif provider == EmailProvider.MAILCHIMP:
                subject = f"We miss you at Helm AI, {user.first_name}!"
                content = f"""
                <h1>We Miss You!</h1>
                <p>Hi {user.first_name},</p>
                <p>It's been a while since you've used Helm AI.</p>
                <p><a href="https://helm-ai.com/dashboard">Come Back and See What's New</a></p>
                """
                
                return email_client.send_newsletter_campaign(
                    subject=subject,
                    content=content,
                    target_lists=['inactive_users']
                )
                
        except Exception as e:
            logger.error(f"Failed to send reactivation campaign via {provider.value}: {e}")
            raise
    
    def get_email_analytics(self, start_date: str, end_date: str, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Get email analytics for date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            provider: Specific provider to use
            
        Returns:
            Analytics data
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.get_email_analytics(start_date, end_date)
            
            elif provider == EmailProvider.MAILCHIMP:
                # Get list growth history
                analytics = {}
                
                for list_key, list_id in email_client.lists.items():
                    growth = email_client.mailchimp.get_list_growth_history(list_id)
                    analytics[list_key] = growth
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get email analytics from {provider.value}: {e}")
            raise
    
    def sync_user_data(self, user: EmailUser, usage_metrics: Dict[str, Any], provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Sync user data with email provider
        
        Args:
            user: User data
            usage_metrics: Usage metrics
            provider: Specific provider to use
            
        Returns:
            Sync result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                # SendGrid doesn't have direct sync, would need to update contact fields
                return {"status": "synced", "provider": "sendgrid"}
            
            elif provider == EmailProvider.MAILCHIMP:
                return email_client.sync_user_data(
                    email=user.email,
                    plan=user.plan,
                    usage_metrics=usage_metrics,
                    list_key='newsletter'
                )
                
        except Exception as e:
            logger.error(f"Failed to sync user data with {provider.value}: {e}")
            raise
    
    def create_automation_workflow(self, workflow_name: str, trigger_type: str, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Create automation workflow
        
        Args:
            workflow_name: Name of the workflow
            trigger_type: Type of trigger (welcome, onboarding, etc.)
            provider: Specific provider to use
            
        Returns:
            Workflow result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                # SendGrid automation would be handled via Marketing Campaign API
                return {"status": "automation_created", "provider": "sendgrid", "workflow": workflow_name}
            
            elif provider == EmailProvider.MAILCHIMP:
                if trigger_type == "onboarding":
                    return email_client.create_onboarding_automation()
                else:
                    return {"status": "automation_created", "provider": "mailchimp", "workflow": workflow_name}
                
        except Exception as e:
            logger.error(f"Failed to create automation workflow with {provider.value}: {e}")
            raise
    
    def move_user_between_segments(self, email: str, from_segment: str, to_segment: str, provider: Optional[EmailProvider] = None) -> Dict[str, Any]:
        """
        Move user between email segments
        
        Args:
            email: User email
            from_segment: Source segment
            to_segment: Target segment
            provider: Specific provider to use
            
        Returns:
            Move result
        """
        provider = provider or self.primary_provider
        email_client = self.providers.get(provider)
        
        if not email_client:
            raise ValueError(f"Email provider {provider.value} not initialized")
        
        try:
            if provider == EmailProvider.SENDGRID:
                return email_client.move_user_between_segments(email, from_segment, to_segment)
            
            elif provider == EmailProvider.MAILCHIMP:
                # Remove from old segment and add to new
                list_id = email_client.lists.get('newsletter')
                if list_id:
                    # Get member info
                    member = email_client.mailchimp.get_member(list_id, email)
                    
                    # Update with new tags/segments
                    return email_client.mailchimp.update_member(
                        list_id=list_id,
                        email=email,
                        merge_fields={"SEGMENT": to_segment}
                    )
                
        except Exception as e:
            logger.error(f"Failed to move user between segments with {provider.value}: {e}")
            raise


# Singleton instance for easy access
email_manager = EmailManager()
