"""
Helm AI Mailchimp Integration Client
This module provides integration with Mailchimp for email marketing automation
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib

logger = logging.getLogger(__name__)

class MailchimpClient:
    """Mailchimp API client for email marketing"""
    
    def __init__(self, api_key: Optional[str] = None, server_prefix: Optional[str] = None):
        """
        Initialize Mailchimp client
        
        Args:
            api_key: Mailchimp API key
            server_prefix: Mailchimp server prefix (e.g., 'us1', 'us2')
        """
        self.api_key = api_key or os.getenv('MAILCHIMP_API_KEY')
        if not self.api_key:
            raise ValueError("Mailchimp API key is required")
        
        # Extract server prefix from API key if not provided
        if not server_prefix:
            self.server_prefix = self.api_key.split('-')[-1]
        else:
            self.server_prefix = server_prefix
        
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        
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
        auth_string = f"anystring:{self.api_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = __import__('base64').b64encode(auth_bytes).decode('ascii')
        
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Mailchimp API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Mailchimp API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # List Management
    def get_lists(self) -> Dict[str, Any]:
        """Get all mailing lists"""
        return self._make_request('GET', '/lists')
    
    def create_list(self, 
                   name: str,
                   company: str,
                   address1: str,
                   city: str,
                   state: str,
                   zip: str,
                   country: str,
                   phone: str = "",
                   permission_reminder: str = "You are receiving this email because you opted in at our website.",
                   email_type_option: bool = True,
                   campaign_defaults: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new mailing list"""
        if not campaign_defaults:
            campaign_defaults = {
                "from_name": "Helm AI",
                "from_email": "noreply@helm-ai.com",
                "subject": "Helm AI Newsletter",
                "language": "en"
            }
        
        data = {
            "name": name,
            "contact": {
                "company": company,
                "address1": address1,
                "city": city,
                "state": state,
                "zip": zip,
                "country": country,
                "phone": phone
            },
            "permission_reminder": permission_reminder,
            "email_type_option": email_type_option,
            "campaign_defaults": campaign_defaults
        }
        
        return self._make_request('POST', '/lists', json=data)
    
    def get_list_details(self, list_id: str) -> Dict[str, Any]:
        """Get details of a specific list"""
        return self._make_request('GET', f'/lists/{list_id}')
    
    # Member Management
    def add_member(self, 
                   list_id: str,
                   email: str,
                   status: str = "subscribed",
                   merge_fields: Dict[str, Any] = None,
                   tags: List[str] = None,
                   language: str = "en") -> Dict[str, Any]:
        """
        Add member to list
        
        Args:
            list_id: List ID
            email: Member email
            status: Subscription status (subscribed, unsubscribed, cleaned, pending)
            merge_fields: Custom merge fields
            tags: List of tags to apply
            language: Member language preference
        """
        # Generate subscriber hash for email
        subscriber_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        
        data = {
            "email_address": email,
            "status": status,
            "language": language,
            "merge_fields": merge_fields or {},
            "tags": tags or []
        }
        
        return self._make_request('PUT', f'/lists/{list_id}/members/{subscriber_hash}', json=data)
    
    def get_member(self, list_id: str, email: str) -> Dict[str, Any]:
        """Get member by email"""
        subscriber_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        return self._make_request('GET', f'/lists/{list_id}/members/{subscriber_hash}')
    
    def update_member(self, 
                     list_id: str,
                     email: str,
                     merge_fields: Dict[str, Any] = None,
                     status: str = None,
                     tags: List[str] = None) -> Dict[str, Any]:
        """Update member information"""
        subscriber_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        
        data = {}
        if merge_fields:
            data["merge_fields"] = merge_fields
        if status:
            data["status"] = status
        if tags:
            data["tags"] = tags
        
        return self._make_request('PATCH', f'/lists/{list_id}/members/{subscriber_hash}', json=data)
    
    def remove_member(self, list_id: str, email: str) -> Dict[str, Any]:
        """Remove member from list"""
        subscriber_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        return self._make_request('DELETE', f'/lists/{list_id}/members/{subscriber_hash}')
    
    def get_members(self, 
                   list_id: str,
                   status: str = None,
                   count: int = 100,
                   offset: int = 0) -> Dict[str, Any]:
        """Get members from list"""
        params = {
            "count": count,
            "offset": offset
        }
        
        if status:
            params["status"] = status
        
        return self._make_request('GET', f'/lists/{list_id}/members', params=params)
    
    def batch_subscribe(self, list_id: str, members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch subscribe members to list"""
        data = {
            "members": members,
            "update_existing": True
        }
        
        return self._make_request('POST', f'/lists/{list_id}', json=data)
    
    # Campaign Management
    def get_campaigns(self, status: str = None, count: int = 100) -> Dict[str, Any]:
        """Get all campaigns"""
        params = {"count": count}
        
        if status:
            params["status"] = status
        
        return self._make_request('GET', '/campaigns', params=params)
    
    def create_campaign(self, 
                       type: str = "regular",
                       recipients: Dict[str, Any] = None,
                       settings: Dict[str, Any] = None,
                       tracking: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new campaign"""
        data = {
            "type": type,
            "recipients": recipients or {},
            "settings": settings or {},
            "tracking": tracking or {
                "opens": True,
                "clicks": True,
                "text_clicks": True,
                "goal_tracking": True,
                "ecomm360": False
            }
        }
        
        return self._make_request('POST', '/campaigns', json=data)
    
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details"""
        return self._make_request('GET', f'/campaigns/{campaign_id}')
    
    def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send campaign"""
        return self._make_request('POST', f'/campaigns/{campaign_id}/actions/send')
    
    def schedule_campaign(self, campaign_id: str, schedule_time: str) -> Dict[str, Any]:
        """Schedule campaign for later sending"""
        data = {"schedule_time": schedule_time}
        return self._make_request('POST', f'/campaigns/{campaign_id}/actions/schedule', json=data)
    
    def unschedule_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Unschedule campaign"""
        return self._make_request('POST', f'/campaigns/{campaign_id}/actions/unschedule')
    
    # Template Management
    def get_templates(self, count: int = 100) -> Dict[str, Any]:
        """Get all templates"""
        params = {"count": count}
        return self._make_request('GET', '/templates', params=params)
    
    def create_template(self, 
                       name: str,
                       html: str,
                       folder_id: str = None) -> Dict[str, Any]:
        """Create a new template"""
        data = {
            "name": name,
            "html": html
        }
        
        if folder_id:
            data["folder"] = folder_id
        
        return self._make_request('POST', '/templates', json=data)
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template details"""
        return self._make_request('GET', f'/templates/{template_id}')
    
    # Content Management
    def set_campaign_content(self, campaign_id: str, template_id: str = None, html: str = None) -> Dict[str, Any]:
        """Set campaign content"""
        data = {}
        
        if template_id:
            data["template"] = {"id": template_id}
        if html:
            data["html"] = html
        
        return self._make_request('PUT', f'/campaigns/{campaign_id}/content', json=data)
    
    # Analytics and Reporting
    def get_campaign_report(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign report"""
        return self._make_request('GET', f'/reports/{campaign_id}')
    
    def get_campaign_click_details(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign click details"""
        return self._make_request('GET', f'/reports/{campaign_id}/click-details')
    
    def get_campaign_open_details(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign open details"""
        return self._make_request('GET', f'/reports/{campaign_id}/open-details')
    
    def get_list_growth_history(self, list_id: str) -> Dict[str, Any]:
        """Get list growth history"""
        return self._make_request('GET', f'/lists/{list_id}/growth-history')
    
    def get_member_activity(self, list_id: str, email: str) -> Dict[str, Any]:
        """Get member activity history"""
        subscriber_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        return self._make_request('GET', f'/lists/{list_id}/members/{subscriber_hash}/activity')
    
    # Automation
    def get_automations(self) -> Dict[str, Any]:
        """Get all automation workflows"""
        return self._make_request('GET', '/automations')
    
    def create_automation(self, 
                         title: str,
                         trigger_settings: Dict[str, Any],
                         recipients: Dict[str, Any],
                         settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create automation workflow"""
        data = {
            "title": title,
            "trigger_settings": trigger_settings,
            "recipients": recipients,
            "settings": settings
        }
        
        return self._make_request('POST', '/automations', json=data)
    
    def start_automation(self, workflow_id: str) -> Dict[str, Any]:
        """Start automation workflow"""
        return self._make_request('POST', f'/automations/{workflow_id}/actions/start')
    
    def pause_automation(self, workflow_id: str) -> Dict[str, Any]:
        """Pause automation workflow"""
        return self._make_request('POST', f'/automations/{workflow_id}/actions/pause')
    
    # Segmentation
    def create_segment(self, 
                      list_id: str,
                      name: str,
                      static_segment: bool = False,
                      options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create list segment"""
        data = {
            "name": name,
            "static_segment": static_segment
        }
        
        if options:
            data["options"] = options
        
        return self._make_request('POST', f'/lists/{list_id}/segments', json=data)
    
    def get_segments(self, list_id: str) -> Dict[str, Any]:
        """Get all segments for a list"""
        return self._make_request('GET', f'/lists/{list_id}/segments')
    
    def add_members_to_segment(self, list_id: str, segment_id: str, members: List[str]) -> Dict[str, Any]:
        """Add members to segment"""
        data = {"members_to_add": members}
        return self._make_request('POST', f'/lists/{list_id}/segments/{segment_id}', json=data)
    
    # Tag Management
    def get_tags(self, list_id: str) -> Dict[str, Any]:
        """Get all tags for a list"""
        return self._make_request('GET', f'/lists/{list_id}/tag-search')
    
    def create_tag(self, list_id: str, name: str) -> Dict[str, Any]:
        """Create a new tag"""
        data = {"name": name}
        return self._make_request('POST', f'/lists/{list_id}/segments', json=data)
    
    def add_tag_to_members(self, list_id: str, tag_name: str, members: List[str]) -> Dict[str, Any]:
        """Add tag to multiple members"""
        data = {
            "tag_name": tag_name,
            "members": members
        }
        
        return self._make_request('POST', f'/lists/{list_id}/segments', json=data)


# Helm AI specific Mailchimp operations
class HelmAIMailchimp:
    """Helm AI specific email marketing operations using Mailchimp"""
    
    def __init__(self):
        self.mailchimp = MailchimpClient()
        self.lists = {}
        self.templates = {}
        self.segments = {}
        self._initialize_lists_and_segments()
    
    def _initialize_lists_and_segments(self):
        """Initialize default lists and segments"""
        try:
            # Get existing lists
            lists_response = self.mailchimp.get_lists()
            existing_lists = {lst['name']: lst['id'] for lst in lists_response.get('lists', [])}
            
            # Default list names
            default_lists = {
                'Helm AI Newsletter': 'newsletter',
                'Helm AI Trial Users': 'trial_users',
                'Helm AI Free Users': 'free_users',
                'Helm AI Pro Users': 'pro_users',
                'Helm AI Business Users': 'business_users',
                'Helm AI Enterprise Users': 'enterprise_users',
                'Helm AI Inactive Users': 'inactive_users'
            }
            
            # Create lists if they don't exist
            for list_name, list_key in default_lists.items():
                if list_name in existing_lists:
                    self.lists[list_key] = existing_lists[list_name]
                else:
                    new_list = self.mailchimp.create_list(
                        name=list_name,
                        company="Helm AI",
                        address1="123 Tech Street",
                        city="San Francisco",
                        state="CA",
                        zip="94105",
                        country="US",
                        phone="1-800-HELM-AI"
                    )
                    self.lists[list_key] = new_list['id']
                
                # Create segments for the list
                self._create_segments_for_list(self.lists[list_key])
            
        except Exception as e:
            logger.error(f"Failed to initialize lists and segments: {e}")
    
    def _create_segments_for_list(self, list_id: str):
        """Create default segments for a list"""
        try:
            segments_response = self.mailchimp.get_segments(list_id)
            existing_segments = {seg['name']: seg['id'] for seg in segments_response.get('segments', [])}
            
            default_segments = {
                'New Subscribers': {
                    'options': {
                        'match': 'all',
                        'conditions': [
                            {
                                'field': 'timestamp_signup',
                                'op': 'after',
                                'value': '30 days ago'
                            }
                        ]
                    }
                },
                'Active Users': {
                    'options': {
                        'match': 'all',
                        'conditions': [
                            {
                                'field': 'last_changed',
                                'op': 'after',
                                'value': '7 days ago'
                            }
                        ]
                    }
                },
                'Inactive Users': {
                    'options': {
                        'match': 'all',
                        'conditions': [
                            {
                                'field': 'last_changed',
                                'op': 'before',
                                'value': '30 days ago'
                            }
                        ]
                    }
                }
            }
            
            for segment_name, segment_options in default_segments.items():
                if segment_name not in existing_segments:
                    segment = self.mailchimp.create_segment(
                        list_id=list_id,
                        name=segment_name,
                        options=segment_options['options']
                    )
                    existing_segments[segment_name] = segment['id']
            
            # Store segments for this list
            self.segments[list_id] = existing_segments
            
        except Exception as e:
            logger.error(f"Failed to create segments for list {list_id}: {e}")
    
    def add_user_to_list(self, 
                        email: str,
                        first_name: str,
                        last_name: str,
                        list_key: str,
                        plan: str = "free",
                        company: str = "",
                        job_title: str = "",
                        tags: List[str] = None) -> Dict[str, Any]:
        """Add user to specific list"""
        list_id = self.lists.get(list_key)
        if not list_id:
            raise ValueError(f"List '{list_key}' not found")
        
        merge_fields = {
            "FNAME": first_name,
            "LNAME": last_name,
            "PLAN": plan,
            "COMPANY": company,
            "JOBTITLE": job_title,
            "SIGNUP_DATE": datetime.now().strftime("%Y-%m-%d")
        }
        
        return self.mailchimp.add_member(
            list_id=list_id,
            email=email,
            merge_fields=merge_fields,
            tags=tags or []
        )
    
    def send_welcome_campaign(self, email: str, first_name: str, plan: str) -> Dict[str, Any]:
        """Send welcome email campaign"""
        # Create campaign
        campaign_settings = {
            "subject_line": f"Welcome to Helm AI, {first_name}!",
            "preview_text": f"Get started with your {plan} plan",
            "title": f"Welcome - {first_name}",
            "from_name": "Helm AI",
            "reply_to": "noreply@helm-ai.com",
            "auto_footer": True,
            "inline_css": True
        }
        
        recipients = {
            "list_id": self.lists.get('newsletter', self.lists['free_users'])
        }
        
        campaign = self.mailchimp.create_campaign(
            type="regular",
            recipients=recipients,
            settings=campaign_settings
        )
        
        # Set content (you would typically use a template)
        html_content = f"""
        <h1>Welcome to Helm AI, {first_name}!</h1>
        <p>Thank you for signing up for our {plan} plan.</p>
        <p><a href="https://helm-ai.com/dashboard">Access Your Dashboard</a></p>
        """
        
        self.mailchimp.set_campaign_content(campaign['id'], html=html_content)
        
        # Send campaign
        return self.mailchimp.send_campaign(campaign['id'])
    
    def send_newsletter_campaign(self, 
                                 subject: str,
                                 content: str,
                                 target_lists: List[str] = None) -> Dict[str, Any]:
        """Send newsletter campaign to multiple lists"""
        if not target_lists:
            target_lists = ['newsletter']
        
        campaign_settings = {
            "subject_line": subject,
            "preview_text": "Latest updates from Helm AI",
            "title": subject,
            "from_name": "Helm AI Newsletter",
            "reply_to": "newsletter@helm-ai.com",
            "auto_footer": True,
            "inline_css": True
        }
        
        # Create campaign for first list
        recipients = {
            "list_id": self.lists.get(target_lists[0])
        }
        
        campaign = self.mailchimp.create_campaign(
            type="regular",
            recipients=recipients,
            settings=campaign_settings
        )
        
        # Set content
        self.mailchimp.set_campaign_content(campaign['id'], html=content)
        
        # Send campaign
        return self.mailchimp.send_campaign(campaign['id'])
    
    def create_onboarding_automation(self) -> Dict[str, Any]:
        """Create automated onboarding email series"""
        trigger_settings = {
            "workflow_type": "email",
            "workflow_auth": "welcome",
            "workflow_email": {
                "list_id": self.lists['newsletter']
            }
        }
        
        recipients = {
            "list_id": self.lists['newsletter']
        }
        
        settings = {
            "from_name": "Helm AI",
            "reply_to": "noreply@helm-ai.com",
            "use_conversation": False,
            "doc_id": None,
            "title": "Helm AI Onboarding Series",
            "authenticate": True,
            "auto_footer": True,
            "inline_css": True
        }
        
        return self.mailchimp.create_automation(
            title="Helm AI Onboarding Series",
            trigger_settings=trigger_settings,
            recipients=recipients,
            settings=settings
        )
    
    def segment_users_by_activity(self, list_key: str, days_inactive: int = 30) -> Dict[str, Any]:
        """Create segment of inactive users"""
        list_id = self.lists.get(list_key)
        if not list_id:
            raise ValueError(f"List '{list_key}' not found")
        
        segment_options = {
            'match': 'all',
            'conditions': [
                {
                    'field': 'last_changed',
                    'op': 'before',
                    'value': f'{days_inactive} days ago'
                }
            ]
        }
        
        segment = self.mailchimp.create_segment(
            list_id=list_id,
            name=f'Inactive {days_inactive}+ Days',
            options=segment_options
        )
        
        return segment
    
    def get_user_engagement_report(self, email: str, list_key: str = 'newsletter') -> Dict[str, Any]:
        """Get comprehensive user engagement report"""
        list_id = self.lists.get(list_key)
        if not list_id:
            raise ValueError(f"List '{list_key}' not found")
        
        try:
            # Get member activity
            activity = self.mailchimp.get_member_activity(list_id, email)
            
            # Get member details
            member = self.mailchimp.get_member(list_id, email)
            
            return {
                "member": member,
                "activity": activity.get('activity', []),
                "engagement_score": self._calculate_engagement_score(activity.get('activity', []))
            }
            
        except Exception as e:
            logger.error(f"Failed to get engagement report for {email}: {e}")
            return {"error": str(e)}
    
    def _calculate_engagement_score(self, activities: List[Dict[str, Any]]) -> int:
        """Calculate engagement score based on activity history"""
        score = 0
        
        for activity in activities:
            action = activity.get('action', '')
            
            if action == 'open':
                score += 5
            elif action == 'click':
                score += 10
            elif action == 'sent':
                score += 1
        
        return min(100, score)
    
    def sync_user_data(self, 
                      email: str,
                      plan: str,
                      usage_metrics: Dict[str, Any],
                      list_key: str = 'newsletter') -> Dict[str, Any]:
        """Sync user data with Mailchimp"""
        list_id = self.lists.get(list_key)
        if not list_id:
            raise ValueError(f"List '{list_key}' not found")
        
        merge_fields = {
            "PLAN": plan,
            "LAST_LOGIN": usage_metrics.get('last_login', ''),
            "USAGE_COUNT": str(usage_metrics.get('usage_count', 0)),
            "LAST_FEATURE": usage_metrics.get('last_feature', ''),
            "SESSION_DURATION": str(usage_metrics.get('session_duration', 0))
        }
        
        return self.mailchimp.update_member(
            list_id=list_id,
            email=email,
            merge_fields=merge_fields
        )
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive campaign analytics"""
        try:
            # Get basic report
            report = self.mailchimp.get_campaign_report(campaign_id)
            
            # Get click details
            click_details = self.mailchimp.get_campaign_click_details(campaign_id)
            
            # Get open details
            open_details = self.mailchimp.get_campaign_open_details(campaign_id)
            
            return {
                "report": report,
                "click_details": click_details,
                "open_details": open_details,
                "performance_metrics": {
                    "open_rate": report.get('opens', 0) / report.get('emails_sent', 1) * 100,
                    "click_rate": report.get('clicks', 0) / report.get('emails_sent', 1) * 100,
                    "bounce_rate": report.get('bounces', 0) / report.get('emails_sent', 1) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign analytics: {e}")
            return {"error": str(e)}

    def batch_update_members(self, list_id: str, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update multiple members"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        for update in updates:
            try:
                email = update.get('email')
                if not email:
                    results["error_count"] += 1
                    results["errors"].append({"error": "Missing email", "update": update})
                    continue
                
                self.mailchimp.update_member(
                    list_id=list_id,
                    email=email,
                    merge_fields=update.get('merge_fields', {}),
                    status=update.get('status'),
                    tags=update.get('tags')
                )
                results["success_count"] += 1
                
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append({"error": str(e), "email": update.get('email')})
        
        return results

    def create_ab_test_campaign(self, 
                              subject_a: str,
                              subject_b: str,
                              content_a: str,
                              content_b: str,
                              list_id: str,
                              test_size: int = 50) -> Dict[str, Any]:
        """Create A/B test campaign"""
        try:
            # Create campaign A
            campaign_a_settings = {
                "subject_line": subject_a,
                "preview_text": f"A/B Test - Variant A",
                "title": f"A/B Test A - {subject_a}",
                "from_name": "Helm AI",
                "reply_to": "noreply@helm-ai.com"
            }
            
            campaign_a = self.mailchimp.create_campaign(
                type="regular",
                recipients={"list_id": list_id},
                settings=campaign_a_settings
            )
            
            # Create campaign B
            campaign_b_settings = {
                "subject_line": subject_b,
                "preview_text": f"A/B Test - Variant B",
                "title": f"A/B Test B - {subject_b}",
                "from_name": "Helm AI",
                "reply_to": "noreply@helm-ai.com"
            }
            
            campaign_b = self.mailchimp.create_campaign(
                type="regular",
                recipients={"list_id": list_id},
                settings=campaign_b_settings
            )
            
            # Set content for both campaigns
            self.mailchimp.set_campaign_content(campaign_a['id'], html=content_a)
            self.mailchimp.set_campaign_content(campaign_b['id'], html=content_b)
            
            return {
                "campaign_a": campaign_a,
                "campaign_b": campaign_b,
                "test_size": test_size,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Failed to create A/B test campaign: {e}")
            return {"error": str(e)}

    def get_list_insights(self, list_id: str) -> Dict[str, Any]:
        """Get comprehensive list insights"""
        try:
            # Get list details
            list_details = self.mailchimp.get_list_details(list_id)
            
            # Get growth history
            growth_history = self.mailchimp.get_list_growth_history(list_id)
            
            # Get member count by status
            members_subscribed = self.mailchimp.get_members(list_id, status="subscribed", count=1000)
            members_unsubscribed = self.mailchimp.get_members(list_id, status="unsubscribed", count=1000)
            
            return {
                "list_details": list_details,
                "growth_history": growth_history.get('history', []),
                "member_stats": {
                    "subscribed": members_subscribed.get('total_items', 0),
                    "unsubscribed": members_unsubscribed.get('total_items', 0),
                    "total": list_details.get('stats', {}).get('member_count', 0)
                },
                "engagement_rate": self._calculate_list_engagement_rate(list_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get list insights: {e}")
            return {"error": str(e)}
    
    def _calculate_list_engagement_rate(self, list_id: str) -> float:
        """Calculate list engagement rate"""
        try:
            # Get recent campaigns for this list
            campaigns = self.mailchimp.get_campaigns(count=10)
            list_campaigns = [c for c in campaigns.get('campaigns', []) 
                            if c.get('recipients', {}).get('list_id') == list_id]
            
            if not list_campaigns:
                return 0.0
            
            total_opens = 0
            total_sends = 0
            
            for campaign in list_campaigns:
                report = self.mailchimp.get_campaign_report(campaign['id'])
                total_opens += report.get('opens', 0)
                total_sends += report.get('emails_sent', 0)
            
            return (total_opens / total_sends * 100) if total_sends > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement rate: {e}")
            return 0.0
