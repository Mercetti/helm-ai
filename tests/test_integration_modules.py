"""
Integration modules test - focused on email, analytics, and support integration modules
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

def test_integration_imports():
    """Test that integration modules can be imported"""
    try:
        from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
        from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
        from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
        assert EmailManager is not None
        assert AnalyticsManager is not None
        assert SupportManager is not None
        assert EmailProvider is not None
        assert AnalyticsProvider is not None
        assert SupportProvider is not None
        assert EmailMessage is not None
        assert AnalyticsEvent is not None
        assert SupportTicket is not None
    except ImportError as e:
        pytest.fail(f"Failed to import integration modules: {e}")

@pytest.mark.integration
def test_email_manager_basic():
    """Test basic email manager functionality"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    
    # Test email manager creation
    manager = EmailManager()
    assert manager is not None
    assert hasattr(manager, 'send_email')
    assert hasattr(manager, 'send_campaign')
    assert hasattr(manager, 'get_provider_status')
    
    # Test email provider enum
    assert EmailProvider.SENDGRID.value == "sendgrid"
    assert EmailProvider.MAILCHIMP.value == "mailchimp"

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
def test_email_manager_send_email():
    """Test email manager send email functionality"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    
    manager = EmailManager()
    
    # Create test message
    message = EmailMessage(
        to_emails=["recipient@example.com"],
        subject="Test Email",
        content="Test content"
    )
    
    # Mock the email sending
    with patch.object(manager, '_send_via_sendgrid') as mock_sendgrid, \
         patch.object(manager, '_send_via_mailchimp') as mock_mailchimp:
        
        mock_sendgrid.return_value = {"status": "sent", "message_id": "sg_123"}
        mock_mailchimp.return_value = {"status": "sent", "message_id": "mc_456"}
        
        # Test sending via SendGrid
        result = manager.send_email(message, EmailProvider.SENDGRID)
        assert result is not None
        assert result["status"] == "sent"
        mock_sendgrid.assert_called_once()
        
        # Test sending via Mailchimp
        result = manager.send_email(message, EmailProvider.MAILCHIMP)
        assert result is not None
        assert result["status"] == "sent"
        mock_mailchimp.assert_called_once()

@pytest.mark.integration
def test_email_manager_campaign():
    """Test email manager campaign functionality"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider
    
    manager = EmailManager()
    
    # Mock campaign creation
    with patch.object(manager, '_create_sendgrid_campaign') as mock_campaign:
        mock_campaign.return_value = {
            "campaign_id": "camp_123",
            "status": "created",
            "recipients": 100
        }
        
        # Test campaign creation
        result = manager.send_campaign(
            subject="Test Campaign",
            content="<h1>Campaign Content</h1>",
            recipient_list=["user1@example.com", "user2@example.com"],
            provider=EmailProvider.SENDGRID
        )
        
        assert result is not None
        assert result["campaign_id"] == "camp_123"
        assert result["status"] == "created"
        mock_campaign.assert_called_once()

@pytest.mark.integration
def test_email_manager_provider_status():
    """Test email manager provider status"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider
    
    manager = EmailManager()
    
    # Mock provider status checks
    with patch.object(manager, '_check_sendgrid_health') as mock_sendgrid, \
         patch.object(manager, '_check_mailchimp_health') as mock_mailchimp:
        
        mock_sendgrid.return_value = {"healthy": True, "last_check": datetime.now()}
        mock_mailchimp.return_value = {"healthy": True, "last_check": datetime.now()}
        
        # Test provider status
        status = manager.get_provider_status()
        assert status is not None
        assert EmailProvider.SENDGRID.value in status
        assert EmailProvider.MAILCHIMP.value in status

@pytest.mark.integration
def test_analytics_manager_basic():
    """Test basic analytics manager functionality"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    
    # Test analytics manager creation
    manager = AnalyticsManager()
    assert manager is not None
    assert hasattr(manager, 'track_event')
    assert hasattr(manager, 'track_page_view')
    assert hasattr(manager, 'identify_user')
    assert hasattr(manager, 'get_provider_status')
    
    # Test analytics provider enum
    assert AnalyticsProvider.GOOGLE_ANALYTICS.value == "google_analytics"
    assert AnalyticsProvider.MIXPANEL.value == "mixpanel"

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
def test_analytics_manager_track_event():
    """Test analytics manager track event functionality"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    
    manager = AnalyticsManager()
    
    # Create test event
    event = AnalyticsEvent(
        event_name="button_click",
        user_id="user_123",
        client_id="client_456",
        properties={"button": "signup", "location": "homepage"}
    )
    
    # Mock event tracking
    with patch.object(manager, '_track_via_google_analytics') as mock_ga, \
         patch.object(manager, '_track_via_mixpanel') as mock_mixpanel:
        
        mock_ga.return_value = {"status": "tracked", "event_id": "ga_123"}
        mock_mixpanel.return_value = {"status": "tracked", "event_id": "mp_456"}
        
        # Test tracking via Google Analytics
        result = manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
        assert result is not None
        assert result["status"] == "tracked"
        mock_ga.assert_called_once()
        
        # Test tracking via Mixpanel
        result = manager.track_event(event, AnalyticsProvider.MIXPANEL)
        assert result is not None
        assert result["status"] == "tracked"
        mock_mixpanel.assert_called_once()

@pytest.mark.integration
def test_analytics_manager_page_view():
    """Test analytics manager page view tracking"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider
    
    manager = AnalyticsManager()
    
    # Mock page view tracking
    with patch.object(manager, '_track_page_view_ga') as mock_ga, \
         patch.object(manager, '_track_page_view_mixpanel') as mock_mixpanel:
        
        mock_ga.return_value = {"status": "tracked", "pageview_id": "ga_123"}
        mock_mixpanel.return_value = {"status": "tracked", "pageview_id": "mp_456"}
        
        # Test page view via Google Analytics
        result = manager.track_page_view(
            page_path="/dashboard",
            page_title="Dashboard",
            user_id="user_123",
            provider=AnalyticsProvider.GOOGLE_ANALYTICS
        )
        
        assert result is not None
        assert result["status"] == "tracked"
        mock_ga.assert_called_once()
        
        # Test page view via Mixpanel
        result = manager.track_page_view(
            page_path="/settings",
            page_title="Settings",
            user_id="user_456",
            provider=AnalyticsProvider.MIXPANEL
        )
        
        assert result is not None
        assert result["status"] == "tracked"
        mock_mixpanel.assert_called_once()

@pytest.mark.integration
def test_analytics_manager_user_identification():
    """Test analytics manager user identification"""
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider
    
    manager = AnalyticsManager()
    
    # Mock user identification
    with patch.object(manager, '_identify_user_ga') as mock_ga, \
         patch.object(manager, '_identify_user_mixpanel') as mock_mixpanel:
        
        mock_ga.return_value = {"status": "identified", "user_id": "ga_123"}
        mock_mixpanel.return_value = {"status": "identified", "user_id": "mp_456"}
        
        # Test identification via Google Analytics
        result = manager.identify_user(
            user_id="user_123",
            traits={"name": "John Doe", "email": "john@example.com"},
            provider=AnalyticsProvider.GOOGLE_ANALYTICS
        )
        
        assert result is not None
        assert result["status"] == "identified"
        mock_ga.assert_called_once()
        
        # Test identification via Mixpanel
        result = manager.identify_user(
            user_id="user_456",
            traits={"name": "Jane Smith", "plan": "premium"},
            provider=AnalyticsProvider.MIXPANEL
        )
        
        assert result is not None
        assert result["status"] == "identified"
        mock_mixpanel.assert_called_once()

@pytest.mark.integration
def test_support_manager_basic():
    """Test basic support manager functionality"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Test support manager creation
    manager = SupportManager()
    assert manager is not None
    assert hasattr(manager, 'create_ticket')
    assert hasattr(manager, 'update_ticket')
    assert hasattr(manager, 'get_tickets')
    assert hasattr(manager, 'get_provider_status')
    
    # Test support provider enum
    assert SupportProvider.ZENDESK.value == "zendesk"
    assert SupportProvider.INTERCOM.value == "intercom"

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
def test_support_manager_create_ticket():
    """Test support manager create ticket functionality"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
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
    
    # Mock ticket creation
    with patch.object(manager, '_create_zendesk_ticket') as mock_zendesk, \
         patch.object(manager, '_create_intercom_ticket') as mock_intercom:
        
        mock_zendesk.return_value = {"ticket_id": "zd_123", "status": "created"}
        mock_intercom.return_value = {"ticket_id": "ic_456", "status": "created"}
        
        # Test creation via Zendesk
        result = manager.create_ticket(ticket, SupportProvider.ZENDESK)
        assert result is not None
        assert result["ticket_id"] == "zd_123"
        assert result["status"] == "created"
        mock_zendesk.assert_called_once()
        
        # Test creation via Intercom
        result = manager.create_ticket(ticket, SupportProvider.INTERCOM)
        assert result is not None
        assert result["ticket_id"] == "ic_456"
        assert result["status"] == "created"
        mock_intercom.assert_called_once()

@pytest.mark.integration
def test_support_manager_update_ticket():
    """Test support manager update ticket functionality"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider
    
    manager = SupportManager()
    
    # Mock ticket update
    with patch.object(manager, '_update_zendesk_ticket') as mock_zendesk, \
         patch.object(manager, '_update_intercom_ticket') as mock_intercom:
        
        mock_zendesk.return_value = {"ticket_id": "zd_123", "status": "updated"}
        mock_intercom.return_value = {"ticket_id": "ic_456", "status": "updated"}
        
        # Test update via Zendesk
        result = manager.update_ticket(
            ticket_id="zd_123",
            comment="Ticket updated with new information",
            status="pending",
            provider=SupportProvider.ZENDESK
        )
        
        assert result is not None
        assert result["ticket_id"] == "zd_123"
        assert result["status"] == "updated"
        mock_zendesk.assert_called_once()
        
        # Test update via Intercom
        result = manager.update_ticket(
            ticket_id="ic_456",
            comment="Customer provided additional details",
            status="resolved",
            provider=SupportProvider.INTERCOM
        )
        
        assert result is not None
        assert result["ticket_id"] == "ic_456"
        assert result["status"] == "updated"
        mock_intercom.assert_called_once()

@pytest.mark.integration
def test_support_manager_get_tickets():
    """Test support manager get tickets functionality"""
    from src.integrations.support.support_manager import SupportManager, SupportProvider
    
    manager = SupportManager()
    
    # Mock ticket retrieval
    with patch.object(manager, '_get_zendesk_tickets') as mock_zendesk, \
         patch.object(manager, '_get_intercom_tickets') as mock_intercom:
        
        mock_zendesk.return_value = {
            "tickets": [
                {"id": "zd_123", "subject": "Issue 1", "status": "open"},
                {"id": "zd_456", "subject": "Issue 2", "status": "closed"}
            ]
        }
        mock_intercom.return_value = {
            "tickets": [
                {"id": "ic_123", "subject": "Issue 3", "status": "open"},
                {"id": "ic_456", "subject": "Issue 4", "status": "resolved"}
            ]
        }
        
        # Test getting tickets from Zendesk
        result = manager.get_tickets(provider=SupportProvider.ZENDESK)
        assert result is not None
        assert "tickets" in result
        assert len(result["tickets"]) == 2
        mock_zendesk.assert_called_once()
        
        # Test getting tickets from Intercom
        result = manager.get_tickets(provider=SupportProvider.INTERCOM)
        assert result is not None
        assert "tickets" in result
        assert len(result["tickets"]) == 2
        mock_intercom.assert_called_once()

@pytest.mark.integration
def test_integration_error_handling():
    """Test integration modules error handling"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Test email manager error handling
    email_manager = EmailManager()
    message = EmailMessage(
        to_emails=["test@example.com"],
        subject="Test",
        content="Test content"
    )
    
    with patch.object(email_manager, '_send_via_sendgrid') as mock_sendgrid:
        mock_sendgrid.side_effect = Exception("Email service unavailable")
        
        result = email_manager.send_email(message, EmailProvider.SENDGRID)
        assert result is not None
        assert result["status"] == "error"
    
    # Test analytics manager error handling
    analytics_manager = AnalyticsManager()
    event = AnalyticsEvent(
        event_name="test_event",
        user_id="user_123",
        client_id="client_456"
    )
    
    with patch.object(analytics_manager, '_track_via_google_analytics') as mock_ga:
        mock_ga.side_effect = Exception("Analytics service unavailable")
        
        result = analytics_manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
        assert result is not None
        assert result["status"] == "error"
    
    # Test support manager error handling
    support_manager = SupportManager()
    ticket = SupportTicket(
        user_email="test@example.com",
        user_name="Test User",
        subject="Test Issue",
        description="Test description"
    )
    
    with patch.object(support_manager, '_create_zendesk_ticket') as mock_zendesk:
        mock_zendesk.side_effect = Exception("Support service unavailable")
        
        result = support_manager.create_ticket(ticket, SupportProvider.ZENDESK)
        assert result is not None
        assert result["status"] == "error"

@pytest.mark.integration
def test_integration_configuration():
    """Test integration modules configuration"""
    from src.integrations.email.email_manager import EmailManager
    from src.integrations.analytics.analytics_manager import AnalyticsManager
    from src.integrations.support.support_manager import SupportManager
    
    # Test creation with default configuration
    email_manager = EmailManager()
    analytics_manager = AnalyticsManager()
    support_manager = SupportManager()
    
    # Test that managers have expected configuration attributes
    assert hasattr(email_manager, 'default_provider')
    assert hasattr(analytics_manager, 'default_provider')
    assert hasattr(support_manager, 'default_provider')
    
    # Test that managers have provider clients
    assert hasattr(email_manager, 'sendgrid_client')
    assert hasattr(email_manager, 'mailchimp_client')
    assert hasattr(analytics_manager, 'google_analytics_client')
    assert hasattr(analytics_manager, 'mixpanel_client')
    assert hasattr(support_manager, 'zendesk_client')
    assert hasattr(support_manager, 'intercom_client')

@pytest.mark.integration
def test_integration_thread_safety():
    """Test integration modules thread safety"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    import threading
    
    email_manager = EmailManager()
    analytics_manager = AnalyticsManager()
    
    # Test concurrent email sending
    def email_worker(thread_id):
        message = EmailMessage(
            to_emails=[f"user{thread_id}@example.com"],
            subject=f"Test Email {thread_id}",
            content=f"Content from thread {thread_id}"
        )
        
        with patch.object(email_manager, '_send_via_sendgrid') as mock_sendgrid:
            mock_sendgrid.return_value = {"status": "sent", "message_id": f"sg_{thread_id}"}
            result = email_manager.send_email(message, EmailProvider.SENDGRID)
            return result
    
    # Test concurrent analytics tracking
    def analytics_worker(thread_id):
        event = AnalyticsEvent(
            event_name=f"event_{thread_id}",
            user_id=f"user_{thread_id}",
            client_id=f"client_{thread_id}",
            properties={"thread_id": thread_id}
        )
        
        with patch.object(analytics_manager, '_track_via_google_analytics') as mock_ga:
            mock_ga.return_value = {"status": "tracked", "event_id": f"ga_{thread_id}"}
            result = analytics_manager.track_event(event, AnalyticsProvider.GOOGLE_ANALYTICS)
            return result
    
    # Create multiple threads for each worker
    email_threads = []
    analytics_threads = []
    
    for i in range(3):
        email_thread = threading.Thread(target=email_worker, args=(i,))
        analytics_thread = threading.Thread(target=analytics_worker, args=(i,))
        
        email_threads.append(email_thread)
        analytics_threads.append(analytics_thread)
        
        email_thread.start()
        analytics_thread.start()
    
    # Wait for all threads to complete
    for thread in email_threads + analytics_threads:
        thread.join()

@pytest.mark.integration
def test_integration_end_to_end():
    """Test end-to-end integration scenario"""
    from src.integrations.email.email_manager import EmailManager, EmailProvider, EmailMessage
    from src.integrations.analytics.analytics_manager import AnalyticsManager, AnalyticsProvider, AnalyticsEvent
    from src.integrations.support.support_manager import SupportManager, SupportProvider, SupportTicket
    
    # Create integration managers
    email_manager = EmailManager()
    analytics_manager = AnalyticsManager()
    support_manager = SupportManager()
    
    # Mock all external service calls
    with patch.object(email_manager, '_send_via_sendgrid') as mock_email, \
         patch.object(analytics_manager, '_track_via_google_analytics') as mock_analytics, \
         patch.object(support_manager, '_create_zendesk_ticket') as mock_support:
        
        mock_email.return_value = {"status": "sent", "message_id": "email_123"}
        mock_analytics.return_value = {"status": "tracked", "event_id": "event_456"}
        mock_support.return_value = {"ticket_id": "support_789", "status": "created"}
        
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
            content="<h1>Welcome!</h1><p>Thank you for signing up.</p>"
        )
        
        email_result = email_manager.send_email(welcome_email, EmailProvider.SENDGRID)
        assert email_result["status"] == "sent"
        
        # 3. Create support ticket for follow-up
        support_ticket = SupportTicket(
            user_email="user@example.com",
            user_name="New User",
            subject="Welcome Follow-up",
            description="Follow up on new user signup",
            category="onboarding"
        )
        
        support_result = support_manager.create_ticket(support_ticket, SupportProvider.ZENDESK)
        assert support_result["status"] == "created"
        
        # Verify all calls were made
        mock_analytics.assert_called_once()
        mock_email.assert_called_once()
        mock_support.assert_called_once()

if __name__ == '__main__':
    pytest.main([__file__])
