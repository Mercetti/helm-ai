"""
Simplified Tests for Mailchimp Client Integration
Tests new features: batch operations, A/B testing, analytics, and insights
"""

import pytest
import json
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os

# Import the modules we're testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'integrations', 'email'))

from mailchimp_client import MailchimpClient

class TestMailchimpClientSimple:
    """Simplified tests for Mailchimp client functionality"""
    
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
    def test_batch_update_members(self, mock_make_request):
        """Test batch updating multiple members"""
        mock_make_request.return_value = {
            "success_count": 2,
            "error_count": 0,
            "errors": []
        }
        
        updates = [
            {"email": "test1@example.com", "merge_fields": {"FNAME": "John"}},
            {"email": "test2@example.com", "merge_fields": {"FNAME": "Jane"}}
        ]
        
        result = self.client.batch_update_members("list123", updates)
        
        assert result["success_count"] == 2
        assert result["error_count"] == 0
        assert len(result["errors"]) == 0
    
    @patch.object(MailchimpClient, '_make_request')
    def test_create_ab_test_campaign(self, mock_make_request):
        """Test creating A/B test campaign"""
        mock_make_request.return_value = {
            "id": "campaign123",
            "type": "ab_split",
            "settings": {"title": "A/B Test Campaign"}
        }
        
        result = self.client.create_ab_test_campaign(
            subject_a="Subject A",
            subject_b="Subject B",
            content_a="Content A",
            content_b="Content B",
            list_id="list123"
        )
        
        assert result["id"] == "campaign123"
        assert result["type"] == "ab_split"
        mock_make_request.assert_called_once()
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_campaign_analytics(self, mock_make_request):
        """Test getting campaign analytics"""
        mock_make_request.return_value = {
            "sends": 1000,
            "opens": 500,
            "clicks": 100,
            "bounces": 50,
            "unsubscribes": 25,
            "revenue": 1000.50,
            "list_stats": [
                {
                    "list_id": "list123",
                    "sends": 1000,
                    "opens": 500,
                    "clicks": 100
                }
            ]
        }
        
        result = self.client.get_campaign_analytics("campaign123")
        
        assert result["sends"] == 1000
        assert result["opens"] == 500
        assert result["clicks"] == 100
        assert result["revenue"] == 1000.50
        assert "list_stats" in result
        assert len(result["list_stats"]) == 1
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_list_insights(self, mock_make_request):
        """Test getting list insights"""
        mock_make_request.return_value = {
            "list_id": "list123",
            "list_name": "Test List",
            "member_count": 5000,
            "unsubscribe_count": 250,
            "cleaned_count": 4750,
            "member_count_since_send": 100,
            "campaign_count": 10,
            "campaign_last_sent": "2024-01-15T10:00:00+00:00",
            "merge_field_count": 5,
            "avg_sub_rate": 0.95,
            "avg_unsub_rate": 0.05,
            "target_open_rate": 0.40,
            "target_click_rate": 0.05,
            "open_rate": 0.42,
            "click_rate": 0.06
        }
        
        result = self.client.get_list_insights("list123")
        
        assert result["list_id"] == "list123"
        assert result["member_count"] == 5000
        assert result["unsubscribe_count"] == 250
        assert result["avg_sub_rate"] == 0.95
        assert result["open_rate"] == 0.42
        assert result["click_rate"] == 0.06
    
    @patch.object(MailchimpClient, '_make_request')
    def test_get_list_insights_with_error(self, mock_make_request):
        """Test getting list insights with API error"""
        mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
        
        result = self.client.get_list_insights("list123")
        
        assert "error" in result
        assert result["error"] == "API Error"
    
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
    def test_get_member(self, mock_make_request):
        """Test getting member information"""
        mock_make_request.return_value = {
            "id": "member123",
            "email_address": "test@example.com",
            "status": "subscribed",
            "merge_fields": {
                "FNAME": "John",
                "LNAME": "Doe"
            },
            "timestamp_signup": "2024-01-01T10:00:00+00:00",
            "last_changed": "2024-01-15T10:00:00+00:00"
        }
        
        result = self.client.get_member("list123", "test@example.com")
        
        assert result["id"] == "member123"
        assert result["email_address"] == "test@example.com"
        assert result["status"] == "subscribed"
        assert result["merge_fields"]["FNAME"] == "John"
    
    @patch.object(MailchimpClient, '_make_request')
    def test_remove_member(self, mock_make_request):
        """Test removing a member"""
        mock_make_request.return_value = {
            "status": "unsubscribed",
            "timestamp": "2024-01-15T10:00:00+00:00"
        }
        
        result = self.client.remove_member("list123", "test@example.com")
        
        assert result["status"] == "unsubscribed"
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


class TestMailchimpClientIntegrationSimple:
    """Simplified integration tests for Mailchimp client"""
    
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
            {"id": "campaign123", "type": "ab_split"},  # create_ab_test_campaign
            {"sends": 1000, "opens": 500, "clicks": 100},  # get_campaign_analytics
            {"member_count": 5000, "open_rate": 0.42}  # get_list_insights
        ]
        mock_make_request.side_effect = responses
        
        # Get lists
        lists = self.client.get_lists()
        assert "lists" in lists
        assert len(lists["lists"]) == 1
        
        # Create A/B test campaign
        campaign = self.client.create_ab_test_campaign(
            subject_a="Subject A",
            subject_b="Subject B",
            content_a="Content A",
            content_b="Content B",
            list_id="list123"
        )
        assert campaign["id"] == "campaign123"
        
        # Get campaign analytics
        analytics = self.client.get_campaign_analytics(campaign["id"])
        assert analytics["sends"] == 1000
        
        # Get list insights
        insights = self.client.get_list_insights("list123")
        assert insights["member_count"] == 5000
        
        # Verify all calls were made
        assert mock_make_request.call_count == 4
    
    @patch.object(MailchimpClient, '_make_request')
    def test_error_handling_workflow(self, mock_make_request):
        """Test error handling in workflow"""
        # Mock API error
        mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
        
        # Try batch subscribe with invalid data
        members = [{"email": "invalid-email", "status": "subscribed"}]
        
        with pytest.raises(requests.exceptions.RequestException):
            self.client.batch_subscribe("test_list", members)
    
    @patch.object(MailchimpClient, '_make_request')
    def test_performance_with_large_data(self, mock_make_request):
        """Test performance with large datasets"""
        # Mock successful response
        mock_make_request.return_value = {
            "total_created": 1000,
            "total_updated": 0,
            "errors": []
        }
        
        # Create large member list
        members = [
            {"email": f"test{i}@example.com", "status": "subscribed"}
            for i in range(1000)
        ]
        
        # Measure time for batch operation
        import time
        start_time = time.time()
        result = self.client.batch_subscribe("test_list", members)
        end_time = time.time()
        
        # Verify results
        assert result["total_created"] == 1000
        assert end_time - start_time < 1.0  # Should be fast with mocking


if __name__ == "__main__":
    pytest.main([__file__])
