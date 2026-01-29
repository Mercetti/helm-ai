"""
Helm AI Support Manager
This module provides a unified interface for customer support across multiple platforms
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .zendesk_client import ZendeskClient, HelmAISupport as ZendeskSupport
from .intercom_client import IntercomClient, HelmAIIntercom as IntercomSupport

logger = logging.getLogger(__name__)

class SupportProvider(Enum):
    """Supported support providers"""
    ZENDESK = "zendesk"
    INTERCOM = "intercom"

@dataclass
class SupportTicket:
    """Support ticket data structure"""
    user_email: str
    user_name: str
    subject: str
    description: str
    category: str = "general"
    priority: str = "normal"
    user_id: str = None
    plan: str = "free"
    custom_fields: Dict[str, Any] = None

@dataclass
class SupportConversation:
    """Support conversation data structure"""
    user_email: str
    user_name: str
    subject: str
    message: str
    category: str = "general"
    priority: str = "normal"
    user_id: str = None
    plan: str = "free"
    message_type: str = "comment"

@dataclass
class BugReport:
    """Bug report data structure"""
    user_email: str
    user_name: str
    title: str
    description: str
    steps_to_reproduce: str
    expected_behavior: str
    actual_behavior: str
    environment: str = None
    severity: str = "medium"
    user_id: str = None

@dataclass
class FeatureRequest:
    """Feature request data structure"""
    user_email: str
    user_name: str
    title: str
    description: str
    use_case: str
    priority: str = "medium"
    user_id: str = None

class SupportManager:
    """Unified support manager supporting multiple providers"""
    
    def __init__(self, primary_provider: SupportProvider = SupportProvider.ZENDESK):
        """
        Initialize support manager
        
        Args:
            primary_provider: Primary support provider to use
        """
        self.primary_provider = primary_provider
        self.providers = {}
        
        # Initialize primary provider
        self._initialize_provider(primary_provider)
        
        # Initialize secondary provider if configured
        if primary_provider == SupportProvider.ZENDESK:
            if os.getenv('INTERCOM_ACCESS_TOKEN'):
                self._initialize_provider(SupportProvider.INTERCOM)
        else:
            if os.getenv('ZENDESK_SUBDOMAIN') and os.getenv('ZENDESK_API_TOKEN'):
                self._initialize_provider(SupportProvider.ZENDESK)
    
    def _initialize_provider(self, provider: SupportProvider):
        """Initialize a specific support provider"""
        try:
            if provider == SupportProvider.ZENDESK:
                self.providers[provider] = ZendeskSupport()
                logger.info("Zendesk support provider initialized successfully")
            elif provider == SupportProvider.INTERCOM:
                self.providers[provider] = IntercomSupport()
                logger.info("Intercom support provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {provider.value}: {e}")
            raise
    
    def create_support_ticket(self, ticket: SupportTicket, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Create support ticket
        
        Args:
            ticket: Ticket data
            provider: Specific provider to use (defaults to primary)
            
        Returns:
            Created ticket data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.create_support_ticket(
                    user_email=ticket.user_email,
                    user_name=ticket.user_name,
                    subject=ticket.subject,
                    description=ticket.description,
                    category=ticket.category,
                    priority=ticket.priority,
                    user_id=ticket.user_id,
                    plan=ticket.plan
                )
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.create_support_conversation(
                    user_email=ticket.user_email,
                    user_name=ticket.user_name,
                    subject=ticket.subject,
                    message=ticket.description,
                    category=ticket.category,
                    priority=ticket.priority,
                    user_id=ticket.user_id,
                    plan=ticket.plan
                )
                
        except Exception as e:
            logger.error(f"Failed to create support ticket via {provider.value}: {e}")
            raise
    
    def create_bug_report(self, bug_report: BugReport, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Create bug report
        
        Args:
            bug_report: Bug report data
            provider: Specific provider to use
            
        Returns:
            Created bug report data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.create_bug_report(
                    user_email=bug_report.user_email,
                    user_name=bug_report.user_name,
                    bug_title=bug_report.title,
                    description=bug_report.description,
                    steps_to_reproduce=bug_report.steps_to_reproduce,
                    expected_behavior=bug_report.expected_behavior,
                    actual_behavior=bug_report.actual_behavior,
                    environment=bug_report.environment,
                    severity=bug_report.severity
                )
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.create_bug_report_conversation(
                    user_email=bug_report.user_email,
                    user_name=bug_report.user_name,
                    bug_title=bug_report.title,
                    description=bug_report.description,
                    steps_to_reproduce=bug_report.steps_to_reproduce,
                    expected_behavior=bug_report.expected_behavior,
                    actual_behavior=bug_report.actual_behavior,
                    environment=bug_report.environment,
                    severity=bug_report.severity,
                    user_id=bug_report.user_id
                )
                
        except Exception as e:
            logger.error(f"Failed to create bug report via {provider.value}: {e}")
            raise
    
    def create_feature_request(self, feature_request: FeatureRequest, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Create feature request
        
        Args:
            feature_request: Feature request data
            provider: Specific provider to use
            
        Returns:
            Created feature request data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.create_feature_request(
                    user_email=feature_request.user_email,
                    user_name=feature_request.user_name,
                    feature_title=feature_request.title,
                    description=feature_request.description,
                    use_case=feature_request.use_case,
                    priority=feature_request.priority
                )
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.create_feature_request_conversation(
                    user_email=feature_request.user_email,
                    user_name=feature_request.user_name,
                    feature_title=feature_request.title,
                    description=feature_request.description,
                    use_case=feature_request.use_case,
                    priority=feature_request.priority,
                    user_id=feature_request.user_id
                )
                
        except Exception as e:
            logger.error(f"Failed to create feature request via {provider.value}: {e}")
            raise
    
    def create_billing_inquiry(self, 
                             user_email: str,
                             user_name: str,
                             inquiry_type: str,
                             description: str,
                             invoice_id: str = None,
                             provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Create billing inquiry
        
        Args:
            user_email: User email
            user_name: User name
            inquiry_type: Type of billing inquiry
            description: Description of the inquiry
            invoice_id: Invoice ID if applicable
            provider: Specific provider to use
            
        Returns:
            Created billing inquiry data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.create_billing_inquiry(
                    user_email=user_email,
                    user_name=user_name,
                    inquiry_type=inquiry_type,
                    description=description,
                    invoice_id=invoice_id
                )
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.create_billing_conversation(
                    user_email=user_email,
                    user_name=user_name,
                    inquiry_type=inquiry_type,
                    description=description,
                    invoice_id=invoice_id
                )
                
        except Exception as e:
            logger.error(f"Failed to create billing inquiry via {provider.value}: {e}")
            raise
    
    def escalate_support_request(self, 
                               request_id: str,
                               escalation_reason: str,
                               assignee_id: str = None,
                               provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Escalate support request
        
        Args:
            request_id: Ticket or conversation ID
            escalation_reason: Reason for escalation
            assignee_id: ID of assignee (optional)
            provider: Specific provider to use
            
        Returns:
            Escalation result
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.escalate_ticket(
                    ticket_id=int(request_id),
                    escalation_reason=escalation_reason,
                    assignee_id=assignee_id
                )
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.escalate_conversation(
                    conversation_id=request_id,
                    escalation_reason=escalation_reason,
                    assignee_id=assignee_id
                )
                
        except Exception as e:
            logger.error(f"Failed to escalate support request via {provider.value}: {e}")
            raise
    
    def get_support_analytics(self, days: int = 30, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Get support analytics
        
        Args:
            days: Number of days to analyze
            provider: Specific provider to use
            
        Returns:
            Support analytics data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            return support_client.get_support_analytics(days)
        except Exception as e:
            logger.error(f"Failed to get support analytics from {provider.value}: {e}")
            raise
    
    def get_customer_support_history(self, user_email: str, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Get support history for a customer
        
        Args:
            user_email: Customer email
            provider: Specific provider to use
            
        Returns:
            Customer support history
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            return support_client.get_customer_support_history(user_email)
        except Exception as e:
            logger.error(f"Failed to get customer support history from {provider.value}: {e}")
            raise
    
    def create_knowledge_base_article(self, 
                                    title: str,
                                    content: str,
                                    category: str,
                                    provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Create knowledge base article
        
        Args:
            title: Article title
            content: Article content
            category: Article category
            provider: Specific provider to use
            
        Returns:
            Created article data
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.create_knowledge_base_article(
                    title=title,
                    content=content,
                    category=category
                )
            
            elif provider == SupportProvider.INTERCOM:
                # Need author_id for Intercom - use a default or get from admin
                # For now, we'll use a placeholder
                return support_client.create_knowledge_base_article(
                    title=title,
                    content=content,
                    category=category,
                    author_id="admin_id_placeholder"
                )
                
        except Exception as e:
            logger.error(f"Failed to create knowledge base article via {provider.value}: {e}")
            raise
    
    def send_proactive_support_message(self, 
                                     user_email: str,
                                     message: str,
                                     provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Send proactive support message
        
        Args:
            user_email: User email
            message: Message content
            provider: Specific provider to use
            
        Returns:
            Message result
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.INTERCOM:
                return support_client.create_proactive_support_message(
                    user_email=user_email,
                    message=message
                )
            
            elif provider == SupportProvider.ZENDESK:
                # Zendesk doesn't have direct proactive messaging
                # Would need to create a ticket or use other method
                return {
                    "provider": "zendesk",
                    "message": "Proactive messaging requires additional setup",
                    "user_email": user_email
                }
                
        except Exception as e:
            logger.error(f"Failed to send proactive message via {provider.value}: {e}")
            raise
    
    def setup_customer_segments(self, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Setup customer segments for better support targeting
        
        Args:
            provider: Specific provider to use
            
        Returns:
            Setup result
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.INTERCOM:
                return support_client.setup_customer_segments()
            
            elif provider == SupportProvider.ZENDESK:
                # Zendesk segments are called "views"
                return {
                    "provider": "zendesk",
                    "message": "Customer segments setup requires Zendesk admin configuration",
                    "action": "Create views in Zendesk admin panel"
                }
                
        except Exception as e:
            logger.error(f"Failed to setup customer segments with {provider.value}: {e}")
            raise
    
    def integrate_with_slack(self, webhook_url: str, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Integrate support system with Slack
        
        Args:
            webhook_url: Slack webhook URL
            provider: Specific provider to use
            
        Returns:
            Integration result
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.integrate_with_slack(webhook_url)
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.integrate_with_slack(webhook_url)
                
        except Exception as e:
            logger.error(f"Failed to integrate with Slack via {provider.value}: {e}")
            raise
    
    def setup_automated_workflows(self, provider: Optional[SupportProvider] = None) -> Dict[str, Any]:
        """
        Setup automated workflows for common support scenarios
        
        Args:
            provider: Specific provider to use
            
        Returns:
            Setup result
        """
        provider = provider or self.primary_provider
        support_client = self.providers.get(provider)
        
        if not support_client:
            raise ValueError(f"Support provider {provider.value} not initialized")
        
        try:
            if provider == SupportProvider.ZENDESK:
                return support_client.setup_automated_responses()
            
            elif provider == SupportProvider.INTERCOM:
                return support_client.setup_automated_workflows()
                
        except Exception as e:
            logger.error(f"Failed to setup automated workflows with {provider.value}: {e}")
            raise
    
    def sync_support_data(self, 
                        source_provider: SupportProvider,
                        target_provider: SupportProvider,
                        user_email: str) -> Dict[str, Any]:
        """
        Sync support data between providers
        
        Args:
            source_provider: Source support provider
            target_provider: Target support provider
            user_email: User email
            
        Returns:
            Sync result
        """
        try:
            # Get support history from source provider
            source_client = self.providers.get(source_provider)
            target_client = self.providers.get(target_provider)
            
            if not source_client or not target_client:
                raise ValueError("Both support providers must be initialized")
            
            history = source_client.get_customer_support_history(user_email)
            
            # Create summary ticket/conversation in target provider
            if history.get('total_tickets', 0) > 0:
                summary = f"""
Support History Sync from {source_provider.value}:

Total Tickets: {history.get('total_tickets', 0)}
Solved Tickets: {history.get('solved_tickets', 0)}
Categories: {history.get('categories', {})}

Recent Activity:
{chr(10).join([f"- {ticket.get('subject', 'No subject')}" for ticket in history.get('recent_tickets', [])[:3]])}
                """.strip()
                
                if target_provider == SupportProvider.ZENDESK:
                    return target_client.create_support_ticket(
                        user_email=user_email,
                        user_name=user_email,
                        subject=f"Support History Sync - {source_provider.value}",
                        description=summary,
                        category="internal",
                        priority="low"
                    )
                
                elif target_provider == SupportProvider.INTERCOM:
                    return target_client.create_support_conversation(
                        user_email=user_email,
                        user_name=user_email,
                        subject=f"Support History Sync - {source_provider.value}",
                        message=summary,
                        category="internal",
                        priority="low"
                    )
            
            return {
                "source_provider": source_provider.value,
                "target_provider": target_provider.value,
                "user_email": user_email,
                "synced": False,
                "reason": "No support history found"
            }
            
        except Exception as e:
            logger.error(f"Failed to sync support data: {e}")
            raise
    
    def get_comprehensive_support_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics from all configured providers
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Comprehensive analytics data
        """
        analytics = {}
        
        for provider, client in self.providers.items():
            try:
                provider_analytics = client.get_support_analytics(days)
                analytics[provider.value] = provider_analytics
            except Exception as e:
                logger.error(f"Failed to get analytics from {provider.value}: {e}")
                analytics[provider.value] = {"error": str(e)}
        
        return {
            "period": f"Last {days} days",
            "providers": analytics,
            "total_providers": len(self.providers)
        }


# Singleton instance for easy access
support_manager = SupportManager()
