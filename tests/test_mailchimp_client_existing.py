"""
Tests for Existing Mailchimp Client Features
Tests the actual methods available in the mailchimp_client.py file
"""

import pytest
import requests
from unittest.mock import Mock, patch
import os

# Import the modules we're testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'integrations', 'email'))

from mailchimp_client import MailchimpClient

class TestMailchimpClientExisting:
    """Test existing Mailchimp client functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_api_key = "test-api-key-us1"
        self.client = MailchimpClient(api_key=self.test_api_key)
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.api_key == self.test_api_key
        assert self.client.server_prefix == "us1"
        assert self.client.base_url == "https://us1.api.mailchimp.com/3.0"
        assert self.client.session is not None
    
    def test_client_initialization_missing_api_key(self):
        """Test client initialization with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Mailchimp API key is required"):
                MailchimpClient()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_lists(self, mock_make_request):
        """Test getting lists"""
        mock_make_request.return_value = {
            "lists": [
                {"id": "list1", "name": "Test List 1"},
                {"id": "list2", "name": "Test List 2"}
            ]
        }
        
        result = self.client.get_lists()
        
        assert "lists" in result
        assert len(result["lists"]) == 2
        mock_make_request.assert_called_once_with('GET', '/lists')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_list(self, mock_make_request):
        """Test creating a list"""
        mock_make_request.return_value = {"id": "new_list", "name": "New List"}
        
        result = self.client.create_list(
            name="Test List",
            company="Test Company",
            address1="123 Test St",
            city="Test City",
            state="TS",
            zip="12345",
            country="US"
        )
        
        assert result["id"] == "new_list"
        assert result["name"] == "New List"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_list_details(self, mock_make_request):
        """Test getting list details"""
        mock_make_request.return_value = {
            "id": "list123",
            "name": "Test List",
            "member_count": 1000
        }
        
        result = self.client.get_list_details("list123")
        
        assert result["id"] == "list123"
        assert result["name"] == "Test List"
        assert result["member_count"] == 1000
        mock_make_request.assert_called_once_with('GET', '/lists/list123')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_add_member(self, mock_make_request):
        """Test adding a single member"""
        mock_make_request.return_value = {
            "id": "member123",
            "email_address": "test@example.com",
            "status": "subscribed"
        }
        
        result = self.client.add_member(
            list_id="list123",
            email="test@example.com",
            status="subscribed",
            merge_fields={"FNAME": "John"}
        )
        
        assert result["id"] == "member123"
        assert result["email_address"] == "test@example.com"
        assert result["status"] == "subscribed"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_member(self, mock_make_request):
        """Test getting member information"""
        mock_make_request.return_value = {
            "id": "member123",
            "email_address": "test@example.com",
            "status": "subscribed",
            "merge_fields": {
                "FNAME": "John",
                "LNAME": "Doe"
            }
        }
        
        result = self.client.get_member("list123", "test@example.com")
        
        assert result["id"] == "member123"
        assert result["email_address"] == "test@example.com"
        assert result["status"] == "subscribed"
        assert result["merge_fields"]["FNAME"] == "John"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_update_member(self, mock_make_request):
        """Test updating a member"""
        mock_make_request.return_value = {
            "id": "member123",
            "email_address": "test@example.com",
            "status": "subscribed",
            "merge_fields": {"FNAME": "John Updated"}
        }
        
        result = self.client.update_member(
            list_id="list123",
            email="test@example.com",
            merge_fields={"FNAME": "John Updated"}
        )
        
        assert result["merge_fields"]["FNAME"] == "John Updated"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_remove_member(self, mock_make_request):
        """Test removing a member"""
        mock_make_request.return_value = {
            "status": "deleted",
            "timestamp": "2024-01-15T10:00:00+00:00"
        }
        
        result = self.client.remove_member("list123", "test@example.com")
        
        assert result["status"] == "deleted"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_members(self, mock_make_request):
        """Test getting members from a list"""
        mock_make_request.return_value = {
            "members": [
                {"id": "member1", "email_address": "test1@example.com"},
                {"id": "member2", "email_address": "test2@example.com"}
            ],
            "total_items": 2
        }
        
        result = self.client.get_members("list123", status="subscribed")
        
        assert len(result["members"]) == 2
        assert result["total_items"] == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_batch_subscribe(self, mock_make_request):
        """Test batch subscribing members"""
        mock_make_request.return_value = {
            "total_created": 2,
            "total_updated": 0,
            "errors": []
        }
        
        members = [
            {"email": "test1@example.com", "status": "subscribed"},
            {"email": "test2@example.com", "status": "subscribed"}
        ]
        
        result = self.client.batch_subscribe("list123", members)
        
        assert result["total_created"] == 2
        assert result["total_updated"] == 0
        assert len(result["errors"]) == 0
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_batch_subscribe_with_errors(self, mock_make_request):
        """Test batch subscribing with some errors"""
        mock_make_request.return_value = {
            "total_created": 1,
            "total_updated": 0,
            "errors": [
                {
                    "email_address": "invalid-email",
                    "error": "Invalid email address"
                }
            ]
        }
        
        members = [
            {"email": "valid@example.com", "status": "subscribed"},
            {"email": "invalid-email", "status": "subscribed"}
        ]
        
        result = self.client.batch_subscribe("list123", members)
        
        assert result["total_created"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["email_address"] == "invalid-email"
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaigns(self, mock_make_request):
        """Test getting campaigns"""
        mock_make_request.return_value = {
            "campaigns": [
                {"id": "campaign1", "name": "Campaign 1"},
                {"id": "campaign2", "name": "Campaign 2"}
            ]
        }
        
        result = self.client.get_campaigns(status="sent")
        
        assert "campaigns" in result
        assert len(result["campaigns"]) == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_campaign(self, mock_make_request):
        """Test creating a campaign"""
        mock_make_request.return_value = {
            "id": "campaign123",
            "type": "regular",
            "settings": {"title": "Test Campaign"}
        }
        
        result = self.client.create_campaign(
            type="regular",
            recipients={"list_id": "list123"},
            settings={"title": "Test Campaign"}
        )
        
        assert result["id"] == "campaign123"
        assert result["type"] == "regular"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaign(self, mock_make_request):
        """Test getting campaign details"""
        mock_make_request.return_value = {
            "id": "campaign123",
            "type": "regular",
            "settings": {"title": "Test Campaign"}
        }
        
        result = self.client.get_campaign("campaign123")
        
        assert result["id"] == "campaign123"
        assert result["type"] == "regular"
        mock_make_request.assert_called_once_with('GET', '/campaigns/campaign123')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_send_campaign(self, mock_make_request):
        """Test sending a campaign"""
        mock_make_request.return_value = {
            "id": "send123",
            "status": "sent",
            "total_sent": 1000,
            "send_time": "2024-01-15T10:00:00+00:00"
        }
        
        result = self.client.send_campaign("campaign123")
        
        assert result["id"] == "send123"
        assert result["status"] == "sent"
        assert result["total_sent"] == 1000
        mock_make_request.assert_called_once_with('POST', '/campaigns/campaign123/actions/send')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_schedule_campaign(self, mock_make_request):
        """Test scheduling a campaign"""
        mock_make_request.return_value = {
            "id": "schedule123",
            "status": "scheduled",
            "schedule_time": "2024-01-20T10:00:00+00:00"
        }
        
        result = self.client.schedule_campaign("campaign123", "2024-01-20T10:00:00+00:00")
        
        assert result["id"] == "schedule123"
        assert result["status"] == "scheduled"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_unschedule_campaign(self, mock_make_request):
        """Test unscheduling a campaign"""
        mock_make_request.return_value = {
            "id": "unschedule123",
            "status": "unscheduled"
        }
        
        result = self.client.unschedule_campaign("campaign123")
        
        assert result["id"] == "unschedule123"
        assert result["status"] == "unscheduled"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_templates(self, mock_make_request):
        """Test getting templates"""
        mock_make_request.return_value = {
            "templates": [
                {"id": "template1", "name": "Template 1"},
                {"id": "template2", "name": "Template 2"}
            ]
        }
        
        result = self.client.get_templates()
        
        assert "templates" in result
        assert len(result["templates"]) == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_template(self, mock_make_request):
        """Test creating a template"""
        mock_make_request.return_value = {
            "id": "template123",
            "name": "Test Template"
        }
        
        result = self.client.create_template(
            name="Test Template",
            html="<html><body>Test</body></html>"
        )
        
        assert result["id"] == "template123"
        assert result["name"] == "Test Template"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_template(self, mock_make_request):
        """Test getting template details"""
        mock_make_request.return_value = {
            "id": "template123",
            "name": "Test Template",
            "html": "<html><body>Test</body></html>"
        }
        
        result = self.client.get_template("template123")
        
        assert result["id"] == "template123"
        assert result["name"] == "Test Template"
        mock_make_request.assert_called_once_with('GET', '/templates/template123')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_set_campaign_content(self, mock_make_request):
        """Test setting campaign content"""
        mock_make_request.return_value = {
            "template_id": "template123",
            "html": "<html><body>Test Content</body></html>"
        }
        
        result = self.client.set_campaign_content(
            campaign_id="campaign123",
            template_id="template123",
            html="<html><body>Test Content</body></html>"
        )
        
        assert result["template_id"] == "template123"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaign_report(self, mock_make_request):
        """Test getting campaign report"""
        mock_make_request.return_value = {
            "sends": 1000,
            "opens": 500,
            "clicks": 100,
            "bounces": 50,
            "unsubscribes": 25
        }
        
        result = self.client.get_campaign_report("campaign123")
        
        assert result["sends"] == 1000
        assert result["opens"] == 500
        assert result["clicks"] == 100
        mock_make_request.assert_called_once_with('GET', '/reports/campaign123')
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaign_click_details(self, mock_make_request):
        """Test getting campaign click details"""
        mock_make_request.return_value = {
            "clicks": [
                {"email": "test1@example.com", "timestamp": "2024-01-15T10:00:00+00:00"},
                {"email": "test2@example.com", "timestamp": "2024-01-15T10:05:00+00:00"}
            ],
            "total": 2
        }
        
        result = self.client.get_campaign_click_details("campaign123")
        
        assert "clicks" in result
        assert len(result["clicks"]) == 2
        assert result["total"] == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaign_open_details(self, mock_make_request):
        """Test getting campaign open details"""
        mock_make_request.return_value = {
            "opens": [
                {"email": "test1@example.com", "timestamp": "2024-01-15T10:00:00+00:00"},
                {"email": "test2@example.com", "timestamp": "2024-01-15T10:05:00+00:00"}
            ],
            "total": 2
        }
        
        result = self.client.get_campaign_open_details("campaign123")
        
        assert "opens" in result
        assert len(result["opens"]) == 2
        assert result["total"] == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_list_growth_history(self, mock_make_request):
        """Test getting list growth history"""
        mock_make_request.return_value = {
            "history": [
                {"month": "2024-01", "existing": 1000, "imports": 100, "optins": 50},
                {"month": "2024-02", "existing": 1150, "imports": 80, "optins": 40}
            ]
        }
        
        result = self.client.get_list_growth_history("list123")
        
        assert "history" in result
        assert len(result["history"]) == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_member_activity(self, mock_make_request):
        """Test getting member activity"""
        mock_make_request.return_value = {
            "activity": [
                {"action": "open", "timestamp": "2024-01-15T10:00:00+00:00"},
                {"action": "click", "timestamp": "2024-01-15T10:05:00+00:00"}
            ]
        }
        
        result = self.client.get_member_activity("list123", "test@example.com")
        
        assert "activity" in result
        assert len(result["activity"]) == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_automations(self, mock_make_request):
        """Test getting automation workflows"""
        mock_make_request.return_value = {
            "automations": [
                {"id": "automation1", "name": "Welcome Series"},
                {"id": "automation2", "name": "Abandoned Cart"}
            ]
        }
        
        result = self.client.get_automations()
        
        assert "automations" in result
        assert len(result["automations"]) == 2
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_automation(self, mock_make_request):
        """Test creating automation workflow"""
        mock_make_request.return_value = {
            "id": "automation123",
            "name": "Test Automation"
        }
        
        result = self.client.create_automation(
            title="Test Automation",
            trigger_settings={"event": "subscribe"},
            recipients={"list_id": "list123"},
            settings={"from_email": "test@example.com"}
        )
        
        assert result["id"] == "automation123"
        assert result["name"] == "Test Automation"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_start_automation(self, mock_make_request):
        """Test starting automation workflow"""
        mock_make_request.return_value = {
            "id": "start123",
            "status": "running"
        }
        
        result = self.client.start_automation("automation123")
        
        assert result["id"] == "start123"
        assert result["status"] == "running"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_pause_automation(self, mock_make_request):
        """Test pausing automation workflow"""
        mock_make_request.return_value = {
            "id": "pause123",
            "status": "paused"
        }
        
        result = self.client.pause_automation("automation123")
        
        assert result["id"] == "pause123"
        assert result["status"] == "paused"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_segment(self, mock_make_request):
        """Test creating a segment"""
        mock_make_request.return_value = {
            "id": "segment123",
            "name": "Test Segment"
        }
        
        result = self.client.create_segment(
            list_id="list123",
            name="Test Segment",
            static_segment=False
        )
        
        assert result["id"] == "segment123"
        assert result["name"] == "Test Segment"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_segments(self, mock_make_request):
        """Test getting segments"""
        mock_make_request.return_value = {
            "segments": [
                {"id": "segment1", "name": "Segment 1"},
                {"id": "segment2", "name": "Segment 2"}
            ]
        }
        
        result = self.client.get_segments("list123")
        
        assert "segments" in result
        assert len(result["segments"]) == 2
        mock_make_request.assert_called_once()
    
    def test_make_request_success(self):
        """Test successful API request"""
        with patch.object(self.client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            result = self.client._make_request('GET', '/test')
            
            assert result["success"] == True
            mock_request.assert_called_once()
    
    def test_make_request_failure(self):
        """Test failed API request"""
        with patch.object(self.client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Bad request"}
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
            mock_request.return_value = mock_response
            
            with pytest.raises(requests.exceptions.HTTPError):
                self.client._make_request('GET', '/test')
    
    def test_retry_strategy(self):
        """Test retry strategy configuration"""
        # Check that retry strategy is properly configured
        adapter = self.client.session.get_adapter("https://")
        assert adapter.max_retries.total == 3
        assert adapter.max_retries.backoff_factor == 1
        assert 429 in adapter.max_retries.status_forcelist
        assert 500 in adapter.max_retries.status_forcelist


class TestMailchimpClientIntegrationExisting:
    """Integration tests for existing Mailchimp client features"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.test_api_key = "test-api-key-us1"
        self.client = MailchimpClient(api_key=self.test_api_key)
    
    @patch.object(MailchimpClient, '_make_request')
    def test_end_to_end_workflow(self, mock_make_request):
        """Test end-to-end workflow with mocked API calls"""
        # Mock different responses for different calls
        responses = [
            {"lists": [{"id": "list123", "name": "Test List"}]},  # get_lists
            {"id": "campaign123", "type": "regular"},  # create_campaign
            {"sends": 1000, "opens": 500, "clicks": 100},  # get_campaign_report
            {"member_count": 5000, "open_rate": 0.42}  # get_list_details
        ]
        mock_make_request.side_effect = responses
        
        # Get lists
        lists = self.client.get_lists()
        assert "lists" in lists
        assert len(lists["lists"]) == 1
        
        # Create campaign
        campaign = self.client.create_campaign(
            type="regular",
            recipients={"list_id": "list123"},
            settings={"title": "Test Campaign"}
        )
        assert campaign["id"] == "campaign123"
        
        # Get campaign report
        report = self.client.get_campaign_report(campaign["id"])
        assert report["sends"] == 1000
        
        # Get list details
        details = self.client.get_list_details("list123")
        assert details["member_count"] == 5000
        
        # Verify all calls were made
        assert mock_make_request.call_count == 4
    
    @patch.object(MailchimpClient, '_make_request')
    def test_member_management_workflow(self, mock_make_request):
        """Test member management workflow"""
        # Mock responses
        responses = [
            {"id": "member123", "email_address": "test@example.com", "status": "subscribed"},  # add_member
            {"id": "member123", "email_address": "test@example.com", "status": "subscribed", "merge_fields": {"FNAME": "John"}},  # update_member
            {"activity": [{"action": "open", "timestamp": "2024-01-15T10:00:00+00:00"}]},  # get_member_activity
            {"status": "deleted"}  # remove_member
        ]
        mock_make_request.side_effect = responses
        
        # Add member
        member = self.client.add_member("list123", "test@example.com")
        assert member["email_address"] == "test@example.com"
        
        # Update member
        updated = self.client.update_member("list123", "test@example.com", merge_fields={"FNAME": "John"})
        assert updated["merge_fields"]["FNAME"] == "John"
        
        # Get member activity
        activity = self.client.get_member_activity("list123", "test@example.com")
        assert "activity" in activity
        
        # Remove member
        removed = self.client.remove_member("list123", "test@example.com")
        assert removed["status"] == "deleted"
        
        # Verify all calls were made
        assert mock_make_request.call_count == 4
    
    @patch.object(MailchimpClient, '_make_request')
    def test_campaign_workflow(self, mock_make_request):
        """Test campaign creation and management workflow"""
        # Mock responses
        responses = [
            {"id": "campaign123", "type": "regular"},  # create_campaign
            {"id": "schedule123", "status": "scheduled"},  # schedule_campaign
            {"id": "send123", "status": "sent", "total_sent": 1000},  # send_campaign
            {"sends": 1000, "opens": 500, "clicks": 100},  # get_campaign_report
        ]
        mock_make_request.side_effect = responses
        
        # Create campaign
        campaign = self.client.create_campaign(
            type="regular",
            recipients={"list_id": "list123"}
        )
        assert campaign["id"] == "campaign123"
        
        # Schedule campaign
        scheduled = self.client.schedule_campaign("campaign123", "2024-01-20T10:00:00+00:00")
        assert scheduled["status"] == "scheduled"
        
        # Send campaign
        sent = self.client.send_campaign("campaign123")
        assert sent["status"] == "sent"
        
        # Get report
        report = self.client.get_campaign_report("campaign123")
        assert report["sends"] == 1000
        
        # Verify all calls were made
        assert mock_make_request.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__])
