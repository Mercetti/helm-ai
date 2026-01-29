"""
Helm AI Zendesk Integration
This module provides integration with Zendesk for customer support and ticket management
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import base64

logger = logging.getLogger(__name__)

class ZendeskClient:
    """Zendesk API client for customer support"""
    
    def __init__(self, 
                 subdomain: Optional[str] = None,
                 email: Optional[str] = None,
                 api_token: Optional[str] = None,
                 oauth_token: Optional[str] = None):
        """
        Initialize Zendesk client
        
        Args:
            subdomain: Zendesk subdomain (e.g., 'company' for company.zendesk.com)
            email: Zendesk admin email
            api_token: Zendesk API token
            oauth_token: Zendesk OAuth token
        """
        self.subdomain = subdomain or os.getenv('ZENDESK_SUBDOMAIN')
        self.email = email or os.getenv('ZENDESK_EMAIL')
        self.api_token = api_token or os.getenv('ZENDESK_API_TOKEN')
        self.oauth_token = oauth_token or os.getenv('ZENDESK_OAUTH_TOKEN')
        
        if not self.subdomain:
            raise ValueError("Zendesk subdomain is required")
        
        if not self.api_token and not self.oauth_token:
            raise ValueError("Either API token or OAuth token is required")
        
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"
        
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
        if self.oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.oauth_token}',
                'Content-Type': 'application/json'
            })
        else:
            # Basic authentication with email + API token
            auth_string = f"{self.email}/token:{self.api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            self.session.headers.update({
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Zendesk API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Zendesk API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # Ticket Management
    def create_ticket(self, 
                     subject: str,
                     comment: str,
                     requester_email: str,
                     requester_name: str = None,
                     priority: str = "normal",
                     status: str = "new",
                     type: str = "question",
                     custom_fields: List[Dict[str, Any]] = None,
                     tags: List[str] = None,
                     assignee_id: int = None,
                     group_id: int = None) -> Dict[str, Any]:
        """Create a new support ticket"""
        ticket_data = {
            "ticket": {
                "subject": subject,
                "comment": {"body": comment},
                "requester": {
                    "email": requester_email,
                    "name": requester_name or requester_email
                },
                "priority": priority,
                "status": status,
                "type": type
            }
        }
        
        if custom_fields:
            ticket_data["ticket"]["custom_fields"] = custom_fields
        
        if tags:
            ticket_data["ticket"]["tags"] = tags
        
        if assignee_id:
            ticket_data["ticket"]["assignee_id"] = assignee_id
        
        if group_id:
            ticket_data["ticket"]["group_id"] = group_id
        
        return self._make_request('POST', '/tickets', json=ticket_data)
    
    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Get ticket by ID"""
        return self._make_request('GET', f'/tickets/{ticket_id}')
    
    def update_ticket(self, ticket_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update ticket"""
        return self._make_request('PUT', f'/tickets/{ticket_id}', json={"ticket": update_data})
    
    def add_ticket_comment(self, ticket_id: int, comment: str, public: bool = True) -> Dict[str, Any]:
        """Add comment to ticket"""
        comment_data = {
            "ticket": {
                "comment": {
                    "body": comment,
                    "public": public
                }
            }
        }
        
        return self._make_request('PUT', f'/tickets/{ticket_id}', json=comment_data)
    
    def search_tickets(self, query: str) -> Dict[str, Any]:
        """Search tickets"""
        params = {"query": query}
        return self._make_request('GET', '/search', params=params)
    
    # User Management
    def create_user(self, name: str, email: str, role: str = "end-user") -> Dict[str, Any]:
        """Create new user"""
        user_data = {
            "user": {
                "name": name,
                "email": email,
                "role": role
            }
        }
        
        return self._make_request('POST', '/users', json=user_data)
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        return self._make_request('GET', f'/users/{user_id}')
    
    def find_user_by_email(self, email: str) -> Dict[str, Any]:
        """Find user by email"""
        params = {"query": f"type:user {email}"}
        return self._make_request('GET', '/search', params=params)
    
    # Organization Management
    def create_organization(self, name: str, domain_names: List[str] = None) -> Dict[str, Any]:
        """Create new organization"""
        org_data = {
            "organization": {
                "name": name
            }
        }
        
        if domain_names:
            org_data["organization"]["domain_names"] = domain_names
        
        return self._make_request('POST', '/organizations', json=org_data)
    
    def get_organization(self, org_id: int) -> Dict[str, Any]:
        """Get organization by ID"""
        return self._make_request('GET', f'/organizations/{org_id}')
    
    # Macro Management
    def get_macros(self) -> Dict[str, Any]:
        """Get all macros"""
        return self._make_request('GET', '/macros')
    
    def apply_macro(self, ticket_id: int, macro_id: int) -> Dict[str, Any]:
        """Apply macro to ticket"""
        return self._make_request('PUT', f'/tickets/{ticket_id}/macros/{macro_id}/apply')
    
    # Views and Reports
    def get_views(self) -> Dict[str, Any]:
        """Get all views"""
        return self._make_request('GET', '/views')
    
    def get_view_results(self, view_id: int) -> Dict[str, Any]:
        """Get results for specific view"""
        return self._make_request('GET', f'/views/{view_id}/tickets')
    
    def get_ticket_metrics(self, ticket_id: int) -> Dict[str, Any]:
        """Get ticket metrics"""
        return self._make_request('GET', f'/tickets/{ticket_id}/metrics')
    
    # Help Center
    def create_article(self, 
                      title: str,
                      body: str,
                      section_id: int,
                      locale: str = "en-us") -> Dict[str, Any]:
        """Create help center article"""
        article_data = {
            "article": {
                "title": title,
                "body": body,
                "locale": locale,
                "user_segment_id": None
            }
        }
        
        return self._make_request('POST', f'/help_center/sections/{section_id}/articles', json=article_data)
    
    def get_articles(self, section_id: int = None) -> Dict[str, Any]:
        """Get help center articles"""
        if section_id:
            return self._make_request('GET', f'/help_center/sections/{section_id}/articles')
        else:
            return self._make_request('GET', '/help_center/articles')
    
    # Webhooks
    def create_webhook(self, 
                      name: str,
                      endpoint: str,
                      subscriptions: List[str],
                      status: str = "active") -> Dict[str, Any]:
        """Create webhook"""
        webhook_data = {
            "webhook": {
                "name": name,
                "endpoint": endpoint,
                "subscriptions": subscriptions,
                "status": status
            }
        }
        
        return self._make_request('POST', '/webhooks', json=webhook_data)
    
    def get_webhooks(self) -> Dict[str, Any]:
        """Get all webhooks"""
        return self._make_request('GET', '/webhooks')


# Helm AI specific Zendesk operations
class HelmAISupport:
    """Helm AI specific support operations using Zendesk"""
    
    def __init__(self):
        self.zendesk = ZendeskClient()
    
    def create_support_ticket(self, 
                            user_email: str,
                            user_name: str,
                            subject: str,
                            description: str,
                            category: str = "general",
                            priority: str = "normal",
                            user_id: str = None,
                            plan: str = "free") -> Dict[str, Any]:
        """Create support ticket with Helm AI specific fields"""
        # Map category to Zend ticket type
        type_mapping = {
            "technical": "incident",
            "billing": "problem",
            "feature_request": "task",
            "bug_report": "incident",
            "general": "question"
        }
        
        # Custom fields for Helm AI data
        custom_fields = [
            {"id": 12345, "value": category},  # Category field
            {"id": 12346, "value": plan},      # Plan field
            {"id": 12347, "value": user_id}    # User ID field
        ]
        
        tags = [category, plan, "helm-ai"]
        
        return self.zendesk.create_ticket(
            subject=subject,
            comment=description,
            requester_email=user_email,
            requester_name=user_name,
            priority=priority,
            type=type_mapping.get(category, "question"),
            custom_fields=custom_fields,
            tags=tags
        )
    
    def create_bug_report(self, 
                         user_email: str,
                         user_name: str,
                         bug_title: str,
                         description: str,
                         steps_to_reproduce: str,
                         expected_behavior: str,
                         actual_behavior: str,
                         environment: str = None,
                         severity: str = "medium") -> Dict[str, Any]:
        """Create bug report ticket"""
        subject = f"[BUG] {bug_title}"
        
        comment = f"""
**Bug Description:**
{description}

**Steps to Reproduce:**
{steps_to_reproduce}

**Expected Behavior:**
{expected_behavior}

**Actual Behavior:**
{actual_behavior}

**Environment:**
{environment or 'Not specified'}

**Severity:** {severity}
        """.strip()
        
        # Map severity to priority
        priority_mapping = {
            "critical": "urgent",
            "high": "high",
            "medium": "normal",
            "low": "low"
        }
        
        custom_fields = [
            {"id": 12348, "value": "bug_report"},
            {"id": 12349, "value": severity}
        ]
        
        return self.zendesk.create_ticket(
            subject=subject,
            comment=comment,
            requester_email=user_email,
            requester_name=user_name,
            priority=priority_mapping.get(severity, "normal"),
            type="incident",
            custom_fields=custom_fields,
            tags=["bug", "helm-ai", severity]
        )
    
    def create_feature_request(self, 
                              user_email: str,
                              user_name: str,
                              feature_title: str,
                              description: str,
                              use_case: str,
                              priority: str = "medium") -> Dict[str, Any]:
        """Create feature request ticket"""
        subject = f"[FEATURE] {feature_title}"
        
        comment = f"""
**Feature Request:**
{description}

**Use Case:**
{use_case}

**Priority:** {priority}
        """.strip()
        
        custom_fields = [
            {"id": 12350, "value": "feature_request"},
            {"id": 12351, "value": priority}
        ]
        
        return self.zendesk.create_ticket(
            subject=subject,
            comment=comment,
            requester_email=user_email,
            requester_name=user_name,
            priority="normal",
            type="task",
            custom_fields=custom_fields,
            tags=["feature-request", "helm-ai"]
        )
    
    def create_billing_inquiry(self, 
                             user_email: str,
                             user_name: str,
                             inquiry_type: str,
                             description: str,
                             invoice_id: str = None) -> Dict[str, Any]:
        """Create billing inquiry ticket"""
        subject = f"[BILLING] {inquiry_type.title()}: {user_name}"
        
        comment = f"""
**Inquiry Type:** {inquiry_type}

**Description:**
{description}

**Invoice ID:** {invoice_id or 'Not specified'}
        """.strip()
        
        custom_fields = [
            {"id": 12352, "value": "billing"},
            {"id": 12353, "value": inquiry_type}
        ]
        
        if invoice_id:
            custom_fields.append({"id": 12354, "value": invoice_id})
        
        return self.zendesk.create_ticket(
            subject=subject,
            comment=comment,
            requester_email=user_email,
            requester_name=user_name,
            priority="high",
            type="problem",
            custom_fields=custom_fields,
            tags=["billing", "helm-ai", inquiry_type]
        )
    
    def escalate_ticket(self, ticket_id: int, escalation_reason: str, assignee_id: int = None) -> Dict[str, Any]:
        """Escalate ticket to higher priority"""
        update_data = {
            "priority": "high",
            "type": "incident"
        }
        
        if assignee_id:
            update_data["assignee_id"] = assignee_id
        
        # Add escalation comment
        self.zendesk.add_ticket_comment(
            ticket_id=ticket_id,
            comment=f"**ESCALATION:** {escalation_reason}",
            public=False
        )
        
        return self.zendesk.update_ticket(ticket_id, update_data)
    
    def get_support_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get support analytics for the specified period"""
        try:
            # Get recent tickets
            search_query = f"created>={days}days"
            tickets_result = self.zendesk.search_tickets(search_query)
            
            tickets = tickets_result.get('results', [])
            
            # Analyze tickets
            total_tickets = len(tickets)
            open_tickets = len([t for t in tickets if t.get('status') in ['new', 'open', 'pending']])
            solved_tickets = len([t for t in tickets if t.get('status') == 'solved'])
            
            # Categorize by type
            categories = {}
            priorities = {}
            
            for ticket in tickets:
                ticket_type = ticket.get('type', 'unknown')
                priority = ticket.get('priority', 'unknown')
                
                categories[ticket_type] = categories.get(ticket_type, 0) + 1
                priorities[priority] = priorities.get(priority, 0) + 1
            
            return {
                "period": f"Last {days} days",
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "solved_tickets": solved_tickets,
                "resolution_rate": (solved_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                "categories": categories,
                "priorities": priorities
            }
            
        except Exception as e:
            logger.error(f"Failed to get support analytics: {e}")
            raise
    
    def create_knowledge_base_article(self, 
                                    title: str,
                                    content: str,
                                    category: str,
                                    section_id: int = None) -> Dict[str, Any]:
        """Create knowledge base article"""
        if not section_id:
            # Map category to section ID (these would be predefined)
            section_mapping = {
                "getting_started": 123456,
                "ai_models": 123457,
                "gaming": 123458,
                "billing": 123459,
                "troubleshooting": 123460
            }
            section_id = section_mapping.get(category, 123456)
        
        # Add Helm AI specific formatting
        formatted_content = f"""
# {title}

{content}

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Category: {category}*
        """.strip()
        
        return self.zendesk.create_article(
            title=title,
            body=formatted_content,
            section_id=section_id
        )
    
    def setup_automated_responses(self) -> Dict[str, Any]:
        """Setup automated response macros"""
        macros = [
            {
                "title": "Welcome Response",
                "actions": [
                    {"field": "status", "value": "pending"},
                    {"field": "comment_value", "value": "Thank you for contacting Helm AI Support. We've received your ticket and will respond within 24 hours."}
                ]
            },
            {
                "title": "Bug Report Acknowledgment",
                "actions": [
                    {"field": "type", "value": "incident"},
                    {"field": "priority", "value": "high"},
                    {"field": "comment_value", "value": "Thank you for reporting this bug. Our development team has been notified and will investigate this issue."}
                ]
            },
            {
                "title": "Billing Response",
                "actions": [
                    {"field": "group_id", "value": 360012345678},  # Billing group ID
                    {"field": "comment_value", "value": "Your billing inquiry has been forwarded to our finance team. They will respond within 1 business day."}
                ]
            }
        ]
        
        # Note: Actual macro creation would require specific Zendesk API endpoints
        # This is a placeholder for the setup process
        return {
            "status": "setup_required",
            "macros": macros,
            "message": "Macros need to be created manually in Zendesk admin panel"
        }
    
    def integrate_with_slack(self, webhook_url: str) -> Dict[str, Any]:
        """Integrate Zendesk with Slack for notifications"""
        subscriptions = [
            "ticket.created",
            "ticket.updated",
            "ticket.solved"
        ]
        
        webhook = self.zendesk.create_webhook(
            name="Helm AI Slack Integration",
            endpoint=webhook_url,
            subscriptions=subscriptions
        )
        
        return webhook
    
    def get_customer_support_history(self, user_email: str) -> Dict[str, Any]:
        """Get complete support history for a customer"""
        try:
            # Find user
            user_result = self.zendesk.find_user_by_email(user_email)
            users = user_result.get('results', [])
            
            if not users:
                return {"error": "User not found"}
            
            user = users[0]
            user_id = user['id']
            
            # Get user's tickets
            tickets_result = self.zendesk.get_tickets_by_user(user_id)
            tickets = tickets_result.get('tickets', [])
            
            # Analyze support history
            total_tickets = len(tickets)
            solved_tickets = len([t for t in tickets if t.get('status') == 'solved'])
            
            # Get ticket categories
            categories = {}
            for ticket in tickets:
                tags = ticket.get('tags', [])
                for tag in tags:
                    if tag in ['technical', 'billing', 'feature_request', 'bug_report']:
                        categories[tag] = categories.get(tag, 0) + 1
            
            return {
                "user": user,
                "total_tickets": total_tickets,
                "solved_tickets": solved_tickets,
                "satisfaction_rate": (solved_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                "categories": categories,
                "recent_tickets": tickets[:5]  # Last 5 tickets
            }
            
        except Exception as e:
            logger.error(f"Failed to get customer support history: {e}")
            raise
