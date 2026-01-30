"""
Working integration modules test - focused on actual working functionality with proper mocking
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os

def test_integration_imports():
    """Test that integration modules can be imported"""
    try:
        from src.integrations.email.email_manager import EmailProvider, EmailMessage
        from src.integrations.analytics.analytics_manager import AnalyticsProvider, AnalyticsEvent
        from src.integrations.support.support_manager import SupportProvider, SupportTicket
        assert EmailProvider is not None
        assert AnalyticsProvider is not None
        assert SupportProvider is not None
        assert EmailMessage is not None
        assert AnalyticsEvent is not None
        assert SupportTicket is not None
    except ImportError as e:
        pytest.fail(f"Failed to import integration modules: {e}")

@pytest.mark.integration
def test_integration_enums():
    """Test integration module enums"""
    from src.integrations.email.email_manager import EmailProvider
    from src.integrations.analytics.analytics_manager import AnalyticsProvider
    from src.integrations.support.support_manager import SupportProvider
    
    # Test email provider enum
    assert EmailProvider.SENDGRID.value == "sendgrid"
    assert EmailProvider.MAILCHIMP.value == "mailchimp"
    
    # Test analytics provider enum
    assert AnalyticsProvider.GOOGLE_ANALYTICS.value == "google_analytics"
    assert AnalyticsProvider.MIXPANEL.value == "mixpanel"
    
    # Test support provider enum
    assert SupportProvider.ZENDESK.value == "zendesk"
    assert SupportProvider.INTERCOM.value == "intercom"

@pytest.mark.integration
def test_email_message_creation():
    """Test email message creation"""
    from src.integrations.email.email_manager import EmailMessage
    
    # Create email message
    message = EmailMessage(
        to_emails=["test@example.com"],
        subject="Test Subject",
        content="<h1>Test Content</h1>",
        content_type="text/html",
        from_email="sender@helm-ai.com"
    )
    
    # Verify message attributes
    assert message.to_emails == ["test@example.com"]
    assert message.subject == "Test Subject"
    assert message.content == "<h1>Test Content</h1>"
    assert message.content_type == "text/html"
    assert message.from_email == "sender@helm-ai.com"

@pytest.mark.integration
def test_analytics_event_creation():
    """Test analytics event creation"""
    from src.integrations.analytics.analytics_manager import AnalyticsEvent
    
    # Create analytics event
    event = AnalyticsEvent(
        event_name="user_signup",
        user_id="user_123",
        client_id="client_456",
        properties={"source": "web", "plan": "premium"},
        user_properties={"name": "John Doe", "email": "john@example.com"}
    )
    
    # Verify event attributes
    assert event.event_name == "user_signup"
    assert event.user_id == "user_123"
    assert event.client_id == "client_456"
    assert event.properties["source"] == "web"
    assert event.user_properties["name"] == "John Doe"

@pytest.mark.integration
def test_support_ticket_creation():
    """Test support ticket creation"""
    from src.integrations.support.support_manager import SupportTicket
    
    # Create support ticket
    ticket = SupportTicket(
        user_email="customer@example.com",
        user_name="John Doe",
        subject="Login Issue",
        description="I cannot log in to my account",
        category="authentication",
        priority="high"
    )
    
    # Verify ticket attributes
    assert ticket.user_email == "customer@example.com"
    assert ticket.user_name == "John Doe"
    assert ticket.subject == "Login Issue"
    assert ticket.description == "I cannot log in to my account"
    assert ticket.category == "authentication"
    assert ticket.priority == "high"

@pytest.mark.integration
def test_email_manager_with_mocking():
    """Test email manager with proper mocking"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    
    # Mock the external dependencies
    with patch('src.integrations.email.sendgrid_client.SendGridClient'), \
         patch('src.integrations.email.mailchimp_client.MailchimpClient'), \
         patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key', 'MAILCHIMP_API_KEY': 'test_key'}):
        
        # Test email manager creation
        manager = EmailManager()
        assert manager is not None
        assert hasattr(manager, 'providers')
        assert hasattr(manager, 'default_provider')
        
        # Test that providers were initialized
        assert EmailProvider.SENDGRID.value in manager.providers
        assert EmailProvider.MAILCHIMP.value in manager.providers

@pytest.mark.integration
def test_analytics_manager_with_mocking():
    """Test analytics manager with proper mocking"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider
    
    # Mock the external dependencies
    with patch('src.integrations.analytics.google_analytics.GoogleAnalyticsClient'), \
         patch('src.integrations.analytics.mixpanel_client.MixpanelClient'), \
         patch.dict(os.environ, {'GOOGLE_ANALYTICS_ID': 'test_id', 'MIXPANEL_TOKEN': 'test_token'}):
        
        # Test analytics manager creation
        manager = AnalyticsManager()
        assert manager is not None
        assert hasattr(manager, 'providers')
        assert hasattr(manager, 'default_provider')
        
        # Test that providers were initialized
        assert AnalyticsProvider.GOOGLE_ANALYTICS.value in manager.providers
        assert AnalyticsProvider.MIXPANEL.value in manager.providers

@pytest.mark.integration
def test_support_manager_with_mocking():
    """Test support manager with proper mocking"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider
    
    # Mock the external dependencies
    with patch('src.integrations.support.zendesk_client.ZendeskClient'), \
         patch('src.integrations.support.intercom_client.IntercomClient'), \
         patch.dict(os.environ, {'ZENDESK_SUBDOMAIN': 'test_domain', 'INTERCOM_ACCESS_TOKEN': 'test_token'}):
        
        # Test support manager creation
        manager = SupportManager()
        assert manager is not None
        assert hasattr(manager, 'providers')
        assert hasattr(manager, 'default_provider')
        
        # Test that providers were initialized
        assert SupportProvider.ZENDESK.value in manager.providers
        assert SupportProvider.INTERCOM.value in manager.providers

@pytest.mark.integration
def test_email_manager_operations():
    """Test email manager operations with mocked clients"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    
    # Mock the external dependencies and environment
    with patch('src.integrations.email.sendgrid_client.SendGridClient') as mock_sendgrid, \
         patch('src.integrations.email.mailchimp_client.MailchimpClient') as mock_mailchimp, \
         patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key', 'MAILCHIMP_API_KEY': 'test_key'}):
        
        # Configure mock clients
        mock_sendgrid.return_value.send_email.return_value = {"status": "sent", "message_id": "sg_123"}
        mock_mailchimp.return_value.send_email.return_value = {"status": "sent", "message_id": "mc_456"}
        
        # Create manager
        manager = EmailManager()
        
        # Create test message
        message = EmailMessage(
            to_emails=["recipient@example.com"],
            subject="Test Email",
            content="Test content"
        )
        
        # Test sending via SendGrid
        result = manager.send_email(message, EmailProvider.SENDGRID)
        assert result is not None
        assert result["status"] == "sent"
        assert result["message_id"] == "sg_123"
        
        # Test sending via Mailchimp
        result = manager.send_email(message, EmailProvider.MAILCHIMP)
        assert result is not None
        assert result["status"] == "sent"
        assert result["message_id"] == "mc_456"

@pytest.mark.integration
def test_analytics_manager_operations():
    """Test analytics manager operations with mocked clients"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    
    # Mock the external dependencies and environment
    with patch('src.integrations.analytics.google_analytics.GoogleAnalyticsClient') as mock_ga, \
         patch('src.integrations.analytics.mixpanel_client.MixpanelClient') as mock_mixpanel, \
         patch.dict(os.environ, {'GOOGLE_ANALYTICS_ID': 'test_id', 'MIXPANEL_TOKEN': 'test_token'}):
        
        # Configure mock clients
        mock_ga.return_value.track_event.return_value = {"status": "tracked", "event_id": "ga_123"}
        mock_mixpanel.return_value.track.return_value = {"status": "tracked", "event_id": "mp_456"}
        
        # Create manager
        manager = AnalyticsManager()
        
        # Create test event
        event = AnalyticsEvent(
            event_name="button_click",
            user_id="user_123",
            client_id="client_456",
            properties={"button": "signup", "location": "homepage"}
        )
        
        # Test tracking via Google Analytics
        result = manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
        assert result is not None
        assert result["status"] == "tracked"
        assert result["event_id"] == "ga_123"
        
        # Test tracking via Mixpanel
        result = manager.track_event(event, AnalyticsProvider.MIXPANEL)
        assert result is not None
        assert result["status"] == "tracked"
        assert result["event_id"] == "mp_456"

@pytest.mark.integration
def test_support_manager_operations():
    """Test support manager operations with mocked clients"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Mock the external dependencies and environment
    with patch('src.integrations.support.zendesk_client.ZendeskClient') as mock_zendesk, \
         patch('src.integrations.support.intercom_client.IntercomClient') as mock_intercom, \
         patch.dict(os.environ, {'ZENDESK_SUBDOMAIN': 'test_domain', 'INTERCOM_ACCESS_TOKEN': 'test_token'}):
        
        # Configure mock clients
        mock_zendesk.return_value.create_ticket.return_value = {"ticket_id": "zd_123", "status": "created"}
        mock_intercom.return_value.create_ticket.return_value = {"ticket_id": "ic_456", "status": "created"}
        
        # Create manager
        manager = SupportManager()
        
        # Create test ticket
        ticket = SupportTicket(
            user_email="customer@example.com",
            user_name="Jane Smith",
            subject="Billing Question",
            description="I have a question about my invoice",
            category="billing",
            priority="medium"
        )
        
        # Test creation via Zendesk
        result = manager.create_ticket(ticket, SupportProvider.ZENDESK)
        assert result is not None
        assert result["ticket_id"] == "zd_123"
        assert result["status"] == "created"
        
        # Test creation via Intercom
        result = manager.create_ticket(ticket, SupportProvider.INTERCOM)
        assert result is not None
        assert result["ticket_id"] == "ic_456"
        assert result["status"] == "created"

@pytest.mark.integration
def test_integration_error_handling():
    """Test integration modules error handling"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Test email manager error handling
    with patch('src.integrations.email.sendgrid_client.SendGridClient') as mock_sendgrid, \
         patch('src.integrations.email.mailchimp_client.MailchimpClient'), \
         patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key', 'MAILCHIMP_API_KEY': 'test_key'}):
        
        # Configure mock to raise exception
        mock_sendgrid.return_value.send_email.side_effect = Exception("Email service unavailable")
        
        manager = EmailManager()
        message = EmailMessage(
            to_emails=["test@example.com"],
            subject="Test",
            content="Test content"
        )
        
        result = manager.send_email(message, EmailProvider.SENDGRID)
        assert result is not None
        assert result["status"] == "error"
    
    # Test analytics manager error handling
    with patch('src.integrations.analytics.google_analytics.GoogleAnalyticsClient') as mock_ga, \
         patch('src.integrations.analytics.mixpanel_client.MixpanelClient'), \
         patch.dict(os.environ, {'GOOGLE_ANALYTICS_ID': 'test_id', 'MIXPANEL_TOKEN': 'test_token'}):
        
        # Configure mock to raise exception
        mock_ga.return_value.track_event.side_effect = Exception("Analytics service unavailable")
        
        manager = AnalyticsManager()
        event = AnalyticsEvent(
            event_name="test_event",
            user_id="user_123",
            client_id="client_456"
        )
        
        result = manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
        assert result is not None
        assert result["status"] == "error"
    
    # Test support manager error handling
    with patch('src.integrations.support.zendesk_client.ZendeskClient') as mock_zendesk, \
         patch('src.integrations.support.intercom_client.IntercomClient'), \
         patch.dict(os.environ, {'ZENDESK_SUBDOMAIN': 'test_domain', 'INTERCOM_ACCESS_TOKEN': 'test_token'}):
        
        # Configure mock to raise exception
        mock_zendesk.return_value.create_ticket.side_effect = Exception("Support service unavailable")
        
        manager = SupportManager()
        ticket = SupportTicket(
            user_email="test@example.com",
            user_name="Test User",
            subject="Test Issue",
            description="Test description"
        )
        
        result = manager.create_ticket(ticket, SupportProvider.ZENDESK)
        assert result is not None
        assert result["status"] == "error"

@pytest.mark.integration
def test_integration_configuration():
    """Test integration modules configuration"""
    from src.integrations.email.email_manager import EmailProvider
    from src.integrations.analytics.analytics_manager import AnalyticsProvider
    from src.integrations.support.support_manager import SupportProvider
    
    # Test provider enums
    assert len(list(EmailProvider)) == 2
    assert len(list(AnalyticsProvider)) == 2
    assert len(list(SupportProvider)) == 2
    
    # Test that all expected providers are available
    expected_email_providers = [EmailProvider.SENDGRID, EmailProvider.MAILCHIMP]
    expected_analytics_providers = [AnalyticsProvider.GOOGLE_ANALYTICS, AnalyticsProvider.MIXPANEL]
    expected_support_providers = [SupportProvider.ZENDESK, SupportProvider.INTERCOM]
    
    for provider in expected_email_providers:
        assert provider.value in ["sendgrid", "mailchimp"]
    
    for provider in expected_analytics_providers:
        assert provider.value in ["google_analytics", "mixpanel"]
    
    for provider in expected_support_providers:
        assert provider.value in ["zendesk", "intercom"]

@pytest.mark.integration
def test_integration_data_structures():
    """Test integration data structures"""
    from src.integrations.email.email_manager import EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsEvent
    from src.integrations.support.support_manager import SupportTicket
    
    # Test email message with all fields
    email_message = EmailMessage(
        to_emails=["user1@example.com", "user2@example.com"],
        subject="Newsletter",
        content="<h1>Monthly Newsletter</h1>",
        content_type="text/html",
        from_email="newsletter@helm-ai.com",
        reply_to="support@helm-ai.com",
        attachments=[{"name": "file.pdf", "content": "base64data"}],
        metadata={"campaign_id": "camp_123"}
    )
    
    assert len(email_message.to_emails) == 2
    assert email_message.reply_to == "support@helm-ai.com"
    assert len(email_message.attachments) == 1
    assert email_message.metadata["campaign_id"] == "camp_123"
    
    # Test analytics event with all fields
    analytics_event = AnalyticsEvent(
        event_name="purchase",
        user_id="user_123",
        client_id="client_456",
        properties={"product": "premium", "price": 99.99, "currency": "USD"},
        user_properties={"name": "John Doe", "email": "john@example.com", "plan": "premium"},
        timestamp=datetime.now(),
        source="web",
        campaign="summer_sale"
    )
    
    assert analytics_event.properties["price"] == 99.99
    assert analytics_event.user_properties["plan"] == "premium"
    assert analytics_event.source == "web"
    assert analytics_event.campaign == "summer_sale"
    
    # Test support ticket with all fields
    support_ticket = SupportTicket(
        user_email="customer@example.com",
        user_name="John Doe",
        subject="Technical Issue",
        description="Cannot access dashboard",
        category="technical",
        priority="high",
        status="open",
        assigned_to="support_team",
        tags=["urgent", "dashboard"],
        custom_fields={"product": "premium", "version": "2.0"}
    )
    
    assert support_ticket.assigned_to == "support_team"
    assert support_ticket.status == "open"
    assert len(support_ticket.tags) == 2
    assert support_ticket.custom_fields["product"] == "premium"

@pytest.mark.integration
def test_integration_end_to_end_scenario():
    """Test end-to-end integration scenario with proper mocking"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Mock all external services and environment variables
    with patch('src.integrations.email.sendgrid_client.SendGridClient') as mock_email, \
         patch('src.integrations.analytics.google_analytics.GoogleAnalyticsClient') as mock_analytics, \
         patch('src.integrations.support.zendesk_client.ZendeskClient') as mock_support, \
         patch.dict(os.environ, {
             'SENDGRID_API_KEY': 'test_key',
             'MAILCHIMP_API_KEY': 'test_key',
             'GOOGLE_ANALYTICS_ID': 'test_id',
             'MIXPANEL_TOKEN': 'test_token',
             'ZENDESK_SUBDOMAIN': 'test_domain',
             'INTERCOM_ACCESS_TOKEN': 'test_token'
         }):
        
        # Configure mock responses
        mock_email.return_value.send_email.return_value = {"status": "sent", "message_id": "email_123"}
        mock_analytics.return_value.track_event.return_value = {"status": "tracked", "event_id": "event_456"}
        mock_support.return_value.create_ticket.return_value = {"ticket_id": "support_789", "status": "created"}
        
        # Create integration managers
        email_manager = EmailManager()
        analytics_manager = AnalyticsManager()
        support_manager = SupportManager()
        
        # Simulate user journey
        # 1. Track user signup
        signup_event = AnalyticsEvent(
            event_name="user_signup",
            user_id="user_123",
            client_id="client_456",
            properties={"source": "web", "plan": "premium"}
        )
        
        analytics_result = analytics_manager.track_event(signup_event, AnalyticsProvider.GOOGLE_ANALYTICS)
        assert analytics_result["status"] == "tracked"
        
        # 2. Send welcome email
        welcome_email = EmailMessage(
            to_emails=["user@example.com"],
            subject="Welcome to Helm AI",
            content="<h1>Welcome!</h1><p>Thank you for signing up.</p>",
            reply_to="support@helm-ai.com"
        )
        
        email_result = email_manager.send_email(welcome_email, EmailProvider.SENDGRID)
        assert email_result["status"] == "sent"
        
        # 3. Create support ticket for follow-up
        support_ticket = SupportTicket(
            user_email="user@example.com",
            user_name="New User",
            subject="Welcome Follow-up",
            description="Follow up on new user signup",
            category="onboarding",
            priority="medium",
            tags=["new_user", "followup"]
        )
        
        support_result = support_manager.create_ticket(support_ticket, SupportProvider.ZENDESK)
        assert support_result["status"] == "created"
        
        # Verify all operations completed successfully
        assert analytics_result["status"] == "tracked"
        assert email_result["status"] == "sent"
        assert support_result["status"] == "created"

@pytest.mark.integration
def test_integration_provider_switching():
    """Test switching between different providers"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    
    # Mock the external dependencies and environment
    with patch('src.integrations.email.sendgrid_client.SendGridClient') as mock_sendgrid, \
         patch('src.integrations.email.mailchimp_client.MailchimpClient') as mock_mailchimp, \
         patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key', 'MAILCHIMP_API_KEY': 'test_key'}):
        
        # Configure mock responses
        mock_sendgrid.return_value.send_email.return_value = {"status": "sent", "message_id": "sg_123"}
        mock_mailchimp.return_value.send_email.return_value = {"status": "sent", "message_id": "mc_456"}
        
        # Create manager
        manager = EmailManager()
        
        # Create test message
        message = EmailMessage(
            to_emails=["test@example.com"],
            subject="Provider Switch Test",
            content="Testing provider switching"
        )
        
        # Test sending with different providers
        sendgrid_result = manager.send_email(message, EmailProvider.SENDGRID)
        mailchimp_result = manager.send_email(message, EmailProvider.MAILCHIMP)
        
        # Verify both providers were used
        assert sendgrid_result["status"] == "sent"
        assert mailchimp_result["status"] == "sent"
        assert sendgrid_result["message_id"] != mailchimp_result["message_id"]

@pytest.mark.integration
def test_integration_batch_operations():
    """Test batch operations across integration modules"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    
    # Mock the external dependencies and environment
    with patch('src.integrations.email.sendgrid_client.SendGridClient') as mock_email, \
         patch('src.integrations.analytics.google_analytics.GoogleAnalyticsClient') as mock_analytics, \
         patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key', 'GOOGLE_ANALYTICS_ID': 'test_id'}):
        
        # Configure mock responses
        mock_email.return_value.send_email.return_value = {"status": "sent"}
        mock_analytics.return_value.track_event.return_value = {"status": "tracked"}
        
        # Create managers
        email_manager = EmailManager()
        analytics_manager = AnalyticsManager()
        
        # Create batch of messages and events
        messages = []
        events = []
        
        for i in range(3):
            message = EmailMessage(
                to_emails=[f"user{i}@example.com"],
                subject=f"Batch Email {i}",
                content=f"Content {i}"
            )
            messages.append(message)
            
            event = AnalyticsEvent(
                event_name=f"batch_event_{i}",
                user_id=f"user_{i}",
                client_id=f"client_{i}",
                properties={"batch": True, "index": i}
            )
            events.append(event)
        
        # Send batch emails
        email_results = []
        for message in messages:
            result = email_manager.send_email(message, EmailProvider.SENDGRID)
            email_results.append(result)
        
        # Track batch events
        analytics_results = []
        for event in events:
            result = analytics_manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
            analytics_results.append(result)
        
        # Verify all operations completed
        assert len(email_results) == 3
        assert len(analytics_results) == 3
        assert all(result["status"] == "sent" for result in email_results)
        assert all(result["status"] == "tracked" for result in analytics_results)

if __name__ == '__main__':
    pytest.main([__file__])
