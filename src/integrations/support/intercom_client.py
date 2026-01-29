"""
Helm AI Intercom Integration
This module provides integration with Intercom for customer support and live chat
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class IntercomClient:
    """Intercom API client for customer support and live chat"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Intercom client
        
        Args:
            access_token: Intercom access token
        """
        self.access_token = access_token or os.getenv('INTERCOM_ACCESS_TOKEN')
        
        if not self.access_token:
            raise ValueError("Intercom access token is required")
        
        self.base_url = "https://api.intercom.io"
        
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
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Intercom-Version': '2.10'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Intercom API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Intercom API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    # Contact Management
    def create_contact(self, 
                      email: str,
                      name: str = None,
                      phone: str = None,
                      user_id: str = None,
                      custom_attributes: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create or update contact"""
        contact_data = {
            "role": "user",
            "email": email
        }
        
        if name:
            contact_data["name"] = name
        
        if phone:
            contact_data["phone"] = phone
        
        if user_id:
            contact_data["user_id"] = user_id
        
        if custom_attributes:
            contact_data["custom_attributes"] = custom_attributes
        
        return self._make_request('POST', '/contacts', json=contact_data)
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID"""
        return self._make_request('GET', f'/contacts/{contact_id}')
    
    def find_contact_by_email(self, email: str) -> Dict[str, Any]:
        """Find contact by email"""
        params = {"email": email}
        return self._make_request('GET', '/contacts', params=params)
    
    def update_contact(self, contact_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact"""
        return self._make_request('PUT', f'/contacts/{contact_id}', json=update_data)
    
    def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        """Delete contact"""
        return self._make_request('DELETE', f'/contacts/{contact_id}')
    
    def merge_contacts(self, primary_contact_id: str, secondary_contact_id: str) -> Dict[str, Any]:
        """Merge two contacts"""
        merge_data = {
            "primary": primary_contact_id,
            "secondary": secondary_contact_id
        }
        
        return self._make_request('POST', '/contacts/merge', json=merge_data)
    
    # Conversation Management
    def create_conversation(self, 
                           from_user_id: str,
                           body: str,
                           message_type: str = "comment",
                           assignee_id: str = None,
                           custom_attributes: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create new conversation"""
        conversation_data = {
            "from": {
                "type": "user",
                "id": from_user_id
            },
            "body": body,
            "type": message_type
        }
        
        if assignee_id:
            conversation_data["assignee_id"] = assignee_id
        
        if custom_attributes:
            conversation_data["custom_attributes"] = custom_attributes
        
        return self._make_request('POST', '/conversations', json=conversation_data)
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation by ID"""
        return self._make_request('GET', f'/conversations/{conversation_id}')
    
    def reply_to_conversation(self, 
                             conversation_id: str,
                             message_type: str,
                             body: str,
                             author_id: str = None,
                             author_type: str = "admin") -> Dict[str, Any]:
        """Reply to conversation"""
        reply_data = {
            "type": message_type,
            "message_type": message_type,
            "body": body
        }
        
        if author_id:
            reply_data["author_id"] = author_id
            reply_data["author_type"] = author_type
        
        return self._make_request('POST', f'/conversations/{conversation_id}/reply', json=reply_data)
    
    def assign_conversation(self, conversation_id: str, assignee_id: str) -> Dict[str, Any]:
        """Assign conversation to admin"""
        assign_data = {
            "assignee_id": assignee_id,
            "admin_id": assignee_id
        }
        
        return self._make_request('PUT', f'/conversations/{conversation_id}/assign', json=assign_data)
    
    def close_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Close conversation"""
        return self._make_request('PUT', f'/conversations/{conversation_id}/close')
    
    def reopen_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Reopen conversation"""
        return self._make_request('PUT', f'/conversations/{conversation_id}/reopen')
    
    def search_conversations(self, query: str, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Search conversations"""
        params = {
            "query": query,
            "page": page,
            "per_page": per_page
        }
        
        return self._make_request('GET', '/conversations/search', params=params)
    
    def get_conversations_by_contact(self, contact_id: str, page: int = 1) -> Dict[str, Any]:
        """Get conversations for specific contact"""
        params = {
            "contact_id": contact_id,
            "page": page
        }
        
        return self._make_request('GET', '/conversations', params=params)
    
    # Note Management
    def create_note(self, contact_id: str, body: str, author_id: str = None) -> Dict[str, Any]:
        """Create note for contact"""
        note_data = {
            "contact_id": contact_id,
            "body": body
        }
        
        if author_id:
            note_data["author_id"] = author_id
        
        return self._make_request('POST', '/notes', json=note_data)
    
    def get_notes(self, contact_id: str) -> Dict[str, Any]:
        """Get notes for contact"""
        params = {"contact_id": contact_id}
        return self._make_request('GET', '/notes', params=params)
    
    # Team Management
    def get_admins(self) -> Dict[str, Any]:
        """Get all admins"""
        return self._make_request('GET', '/admins')
    
    def get_admin(self, admin_id: str) -> Dict[str, Any]:
        """Get admin by ID"""
        return self._make_request('GET', f'/admins/{admin_id}')
    
    def get_teams(self) -> Dict[str, Any]:
        """Get all teams"""
        return self._make_request('GET, /teams')
    
    # Data Attributes
    def create_data_attribute(self, 
                             name: str,
                             attribute_type: str,
                             model: str = "contact",
                             description: str = None,
                             options: List[str] = None) -> Dict[str, Any]:
        """Create custom data attribute"""
        attribute_data = {
            "name": name,
            "data_type": attribute_type,
            "model": model
        }
        
        if description:
            attribute_data["description"] = description
        
        if options:
            attribute_data["options"] = options
        
        return self._make_request('POST, /data_attributes', json=attribute_data)
    
    def get_data_attributes(self, model: str = "contact") -> Dict[str, Any]:
        """Get data attributes"""
        params = {"model": model}
        return self._make_request('GET', '/data_attributes', params=params)
    
    # Tags
    def create_tag(self, name: str, color: str = None) -> Dict[str, Any]:
        """Create tag"""
        tag_data = {"name": name}
        
        if color:
            tag_data["color"] = color
        
        return self._make_request('POST', '/tags', json=tag_data)
    
    def get_tags(self) -> Dict[str, Any]:
        """Get all tags"""
        return self._make_request('GET', '/tags')
    
    def tag_conversation(self, conversation_id: str, tag_id: str) -> Dict[str, Any]:
        """Tag conversation"""
        tag_data = {"id": tag_id}
        return self._make_request('POST', f'/conversations/{conversation_id}/tags', json=tag_data)
    
    def untag_conversation(self, conversation_id: str, tag_id: str) -> Dict[str, Any]:
        """Remove tag from conversation"""
        return self._make_request('DELETE', f'/conversations/{conversation_id}/tags/{tag_id}')
    
    # Segments
    def create_segment(self, 
                      name: str,
                      filters: List[Dict[str, Any]],
                      person_type: str = "user") -> Dict[str, Any]:
        """Create user segment"""
        segment_data = {
            "name": name,
            "person_type": person_type,
            "filters": filters
        }
        
        return self._make_request('POST', '/segments', json=segment_data)
    
    def get_segments(self) -> Dict[str, Any]:
        """Get all segments"""
        return self._make_request('GET', '/segments')
    
    # Articles and Help Center
    def create_article(self, 
                      title: str,
                      body: str,
                      author_id: str,
                      state: str = "published",
                      parent_id: str = None) -> Dict[str, Any]:
        """Create help center article"""
        article_data = {
            "title": title,
            "body": body,
            "author_id": author_id,
            "state": state
        }
        
        if parent_id:
            article_data["parent_id"] = parent_id
        
        return self._make_request('POST', '/articles', json=article_data)
    
    def get_articles(self, section_id: str = None) -> Dict[str, Any]:
        """Get help center articles"""
        if section_id:
            params = {"section_id": section_id}
            return self._make_request('GET', '/articles', params=params)
        else:
            return self._make_request('GET', '/articles')
    
    # Webhooks
    def create_webhook(self, 
                      url: str,
                      topics: List[str],
                      secret: str = None) -> Dict[str, Any]:
        """Create webhook"""
        webhook_data = {
            "url": url,
            "topics": topics
        }
        
        if secret:
            webhook_data["secret"] = secret
        
        return self._make_request('POST', '/subscriptions', json=webhook_data)
    
    def get_webhooks(self) -> Dict[str, Any]:
        """Get all webhooks"""
        return self._make_request('GET', '/subscriptions')
    
    # Analytics
    def get_conversation_statistics(self, 
                                  start_date: str,
                                  end_date: str,
                                  conversation_type: str = "all") -> Dict[str, Any]:
        """Get conversation statistics"""
        params = {
            "start": start_date,
            "end": end_date,
            "type": conversation_type
        }
        
        return self._make_request('GET', '/conversations/statistics', params=params)
    
    def get_admin_statistics(self, 
                            start_date: str,
                            end_date: str,
                            admin_id: str = None) -> Dict[str, Any]:
        """Get admin statistics"""
        params = {
            "start": start_date,
            "end": end_date
        }
        
        if admin_id:
            params["admin_id"] = admin_id
        
        return self._make_request('GET', '/admins/statistics', params=params)


# Helm AI specific Intercom operations
class HelmAIIntercom:
    """Helm AI specific support operations using Intercom"""
    
    def __init__(self):
        self.intercom = IntercomClient()
    
    def create_support_conversation(self, 
                                   user_email: str,
                                   user_name: str,
                                   subject: str,
                                   message: str,
                                   category: str = "general",
                                   priority: str = "normal",
                                   user_id: str = None,
                                   plan: str = "free") -> Dict[str, Any]:
        """Create support conversation with Helm AI specific data"""
        # First, find or create contact
        try:
            contact_result = self.intercom.find_contact_by_email(user_email)
            contacts = contact_result.get('data', [])
            
            if contacts:
                contact = contacts[0]
                contact_id = contact['id']
            else:
                # Create new contact
                custom_attributes = {
                    "plan": plan,
                    "source": "helm_ai_support",
                    "signup_date": datetime.now().isoformat()
                }
                
                contact = self.intercom.create_contact(
                    email=user_email,
                    name=user_name,
                    user_id=user_id,
                    custom_attributes=custom_attributes
                )
                contact_id = contact['id']
            
            # Create conversation
            conversation_body = f"""
**Subject:** {subject}

**Category:** {category}

**Message:**
{message}

**User Plan:** {plan}
**Priority:** {priority}
            """.strip()
            
            custom_attributes = {
                "category": category,
                "priority": priority,
                "plan": plan,
                "source": "helm_ai_support"
            }
            
            conversation = self.intercom.create_conversation(
                from_user_id=contact_id,
                body=conversation_body,
                custom_attributes=custom_attributes
            )
            
            # Add tags based on category and priority
            self._add_conversation_tags(conversation['id'], category, priority, plan)
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create support conversation: {e}")
            raise
    
    def _add_conversation_tags(self, conversation_id: str, category: str, priority: str, plan: str):
        """Add tags to conversation based on category, priority, and plan"""
        try:
            # Get existing tags
            tags_result = self.intercom.get_tags()
            existing_tags = {tag['name']: tag['id'] for tag in tags_result.get('data', [])}
            
            # Tags to add
            tags_to_add = [category, plan, "helm-ai"]
            
            # Add priority tag if high priority
            if priority in ["urgent", "high"]:
                tags_to_add.append(priority)
            
            # Create tags if they don't exist
            for tag_name in tags_to_add:
                if tag_name not in existing_tags:
                    tag = self.intercom.create_tag(tag_name)
                    existing_tags[tag_name] = tag['id']
            
            # Add tags to conversation
            for tag_name in tags_to_add:
                self.intercom.tag_conversation(conversation_id, existing_tags[tag_name])
                
        except Exception as e:
            logger.warning(f"Failed to add tags to conversation: {e}")
    
    def create_bug_report_conversation(self, 
                                      user_email: str,
                                      user_name: str,
                                      bug_title: str,
                                      description: str,
                                      steps_to_reproduce: str,
                                      expected_behavior: str,
                                      actual_behavior: str,
                                      environment: str = None,
                                      severity: str = "medium",
                                      user_id: str = None) -> Dict[str, Any]:
        """Create bug report conversation"""
        subject = f"[BUG] {bug_title}"
        
        message = f"""
**Bug Report:**
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
        
        return self.create_support_conversation(
            user_email=user_email,
            user_name=user_name,
            subject=subject,
            message=message,
            category="bug_report",
            priority=severity,
            user_id=user_id
        )
    
    def create_feature_request_conversation(self, 
                                          user_email: str,
                                          user_name: str,
                                          feature_title: str,
                                          description: str,
                                          use_case: str,
                                          priority: str = "medium",
                                          user_id: str = None) -> Dict[str, Any]:
        """Create feature request conversation"""
        subject = f"[FEATURE] {feature_title}"
        
        message = f"""
**Feature Request:**
{description}

**Use Case:**
{use_case}

**Priority:** {priority}
        """.strip()
        
        return self.create_support_conversation(
            user_email=user_email,
            user_name=user_name,
            subject=subject,
            message=message,
            category="feature_request",
            priority=priority,
            user_id=user_id
        )
    
    def create_billing_conversation(self, 
                                  user_email: str,
                                  user_name: str,
                                  inquiry_type: str,
                                  description: str,
                                  invoice_id: str = None,
                                  user_id: str = None) -> Dict[str, Any]:
        """Create billing inquiry conversation"""
        subject = f"[BILLING] {inquiry_type.title()}: {user_name}"
        
        message = f"""
**Inquiry Type:** {inquiry_type}

**Description:**
{description}

**Invoice ID:** {invoice_id or 'Not specified'}
        """.strip()
        
        return self.create_support_conversation(
            user_email=user_email,
            user_name=user_name,
            subject=subject,
            message=message,
            category="billing",
            priority="high",
            user_id=user_id
        )
    
    def escalate_conversation(self, conversation_id: str, escalation_reason: str, assignee_id: str = None) -> Dict[str, Any]:
        """Escalate conversation to higher priority"""
        # Add escalation note
        escalation_message = f"""
**ESCALATION:** {escalation_reason}

This conversation has been escalated due to the reason above.
        """.strip()
        
        self.intercom.reply_to_conversation(
            conversation_id=conversation_id,
            message_type="note",
            body=escalation_message
        )
        
        # Assign to specific admin if provided
        if assignee_id:
            return self.intercom.assign_conversation(conversation_id, assignee_id)
        
        return {"status": "escalated"}
    
    def get_support_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get support analytics for the specified period"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get conversation statistics
            conv_stats = self.intercom.get_conversation_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            # Get admin statistics
            admin_stats = self.intercom.get_admin_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "period": f"Last {days} days",
                "conversation_stats": conv_stats,
                "admin_stats": admin_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get support analytics: {e}")
            raise
    
    def create_proactive_support_message(self, 
                                       user_email: str,
                                       message: str,
                                       message_type: str = "proactive_support") -> Dict[str, Any]:
        """Send proactive support message to user"""
        try:
            # Find contact
            contact_result = self.intercom.find_contact_by_email(user_email)
            contacts = contact_result.get('data', [])
            
            if not contacts:
                return {"error": "User not found"}
            
            contact = contacts[0]
            contact_id = contact['id']
            
            # Create conversation
            return self.intercom.create_conversation(
                from_user_id=contact_id,
                body=message,
                message_type=message_type
            )
            
        except Exception as e:
            logger.error(f"Failed to send proactive message: {e}")
            raise
    
    def setup_customer_segments(self) -> Dict[str, Any]:
        """Setup customer segments for better targeting"""
        segments = [
            {
                "name": "Enterprise Customers",
                "filters": [
                    {
                        "field": "custom_attributes.plan",
                        "operator": "=",
                        "value": "enterprise"
                    }
                ]
            },
            {
                "name": "New Users (30 days)",
                "filters": [
                    {
                        "field": "custom_attributes.signup_date",
                        "operator": ">",
                        "value": (datetime.now() - timedelta(days=30)).isoformat()
                    }
                ]
            },
            {
                "name": "High Priority Customers",
                "filters": [
                    {
                        "field": "custom_attributes.plan",
                        "operator": "in",
                        "value": ["business", "enterprise"]
                    }
                ]
            },
            {
                "name": "At Risk Customers",
                "filters": [
                    {
                        "field": "last_seen_at",
                        "operator": "<",
                        "value": (datetime.now() - timedelta(days=14)).isoformat()
                    }
                ]
            }
        ]
        
        created_segments = []
        
        for segment_data in segments:
            try:
                segment = self.intercom.create_segment(
                    name=segment_data['name'],
                    filters=segment_data['filters']
                )
                created_segments.append(segment)
            except Exception as e:
                logger.warning(f"Failed to create segment {segment_data['name']}: {e}")
        
        return {
            "created_segments": created_segments,
            "total": len(created_segments)
        }
    
    def integrate_with_slack(self, webhook_url: str) -> Dict[str, Any]:
        """Integrate Intercom with Slack for notifications"""
        topics = [
            "conversation.user.created",
            "conversation.admin.replied",
            "conversation.missed",
            "conversation.snoozed",
            "conversation.opened"
        ]
        
        webhook = self.intercom.create_webhook(
            url=webhook_url,
            topics=topics
        )
        
        return webhook
    
    def create_knowledge_base_article(self, 
                                    title: str,
                                    content: str,
                                    category: str,
                                    author_id: str) -> Dict[str, Any]:
        """Create knowledge base article"""
        # Format content with Helm AI styling
        formatted_content = f"""
# {title}

{content}

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Category: {category}*
*Source: Helm AI Support*
        """.strip()
        
        return self.intercom.create_article(
            title=title,
            body=formatted_content,
            author_id=author_id
        )
    
    def get_customer_support_history(self, user_email: str) -> Dict[str, Any]:
        """Get complete support history for a customer"""
        try:
            # Find contact
            contact_result = self.intercom.find_contact_by_email(user_email)
            contacts = contact_result.get('data', [])
            
            if not contacts:
                return {"error": "User not found"}
            
            contact = contacts[0]
            contact_id = contact['id']
            
            # Get conversations
            conversations_result = self.intercom.get_conversations_by_contact(contact_id)
            conversations = conversations_result.get('conversations', [])
            
            # Analyze conversation history
            total_conversations = len(conversations)
            open_conversations = len([c for c in conversations if c.get('state') == 'open'])
            closed_conversations = len([c for c in conversations if c.get('state') == 'closed'])
            
            # Get conversation categories from tags
            categories = {}
            for conv in conversations:
                tags = conv.get('tags', [])
                for tag in tags:
                    if tag in ['technical', 'billing', 'feature_request', 'bug_report']:
                        categories[tag] = categories.get(tag, 0) + 1
            
            return {
                "contact": contact,
                "total_conversations": total_conversations,
                "open_conversations": open_conversations,
                "closed_conversations": closed_conversations,
                "resolution_rate": (closed_conversations / total_conversations * 100) if total_conversations > 0 else 0,
                "categories": categories,
                "recent_conversations": conversations[:5]  # Last 5 conversations
            }
            
        except Exception as e:
            logger.error(f"Failed to get customer support history: {e}")
            raise
    
    def setup_automated_workflows(self) -> Dict[str, Any]:
        """Setup automated workflows for common scenarios"""
        workflows = [
            {
                "name": "Welcome New Users",
                "trigger": "user.created",
                "action": "send_proactive_message",
                "message": "Welcome to Helm AI! I'm here to help you get started. Feel free to ask any questions."
            },
            {
                "name": "High Priority Assignment",
                "trigger": "conversation.created",
                "condition": "tags contains 'urgent' or 'high'",
                "action": "assign_to_team",
                "team": "priority_support"
            },
            {
                "name": "Billing Escalation",
                "trigger": "conversation.created",
                "condition": "tags contains 'billing'",
                "action": "assign_to_team",
                "team": "billing"
            },
            {
                "name": "Bug Report Triage",
                "trigger": "conversation.created",
                "condition": "tags contains 'bug_report'",
                "action": "create_note",
                "note": "Bug report received. Engineering team has been notified."
            }
        ]
        
        # Note: Actual workflow creation would require Intercom's workflow API
        # This is a placeholder for the setup process
        return {
            "status": "setup_required",
            "workflows": workflows,
            "message": "Workflows need to be configured in Intercom admin panel"
        }
