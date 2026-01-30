"""
Tests for Mailchimp Client Integration
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

class TestMailchimpClient:
    """Test Mailchimp client functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock environment variable
        self.test_api_key = "test-api-key-us1"
        self.test_server_prefix = "us1"
        
        # Create client with test API key
        self.client = MailchimpClient(api_key=self.test_api_key)
    
    def test_client_initialization(self):
        """Test client initialization"""
        # Test with provided API key
        client = MailchimpClient(api_key=self.test_api_key)
        assert client.api_key == self.test_api_key
        assert client.server_prefix == "us1"
        assert client.base_url == "https://us1.api.mailchimp.com/3.0"
        assert client.session is not None
    
    def test_client_initialization_with_env_var(self):
        """Test client initialization with environment variable"""
        with patch.dict(os.environ, {'MAILCHIMP_API_KEY': self.test_api_key}):
            client = MailchimpClient()
            assert client.api_key == self.test_api_key
            assert client.server_prefix == "us1"
    
    def test_client_initialization_missing_api_key(self):
        """Test client initialization with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Mailchimp API key is required"):
                MailchimpClient()
    
    def test_server_prefix_extraction(self):
        """Test server prefix extraction from API key"""
        client = MailchimpClient(api_key="test-api-key-us2")
        assert client.server_prefix == "us2"
        assert client.base_url == "https://us2.api.mailchimp.com/3.0"
        
        # Test with explicit server prefix
        client = MailchimpClient(api_key="test-api-key-us3", server_prefix="us4")
        assert client.server_prefix == "us4"
        assert client.base_url == "https://us4.api.mailchimp.com/3.0"
    
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
    
    @patch('requests.Session.post')
    def test_create_list(self, mock_post):
        """Test creating a list"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_list", "name": "New List"}
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        list_data = {
            "name": "Test List",
            "email_type": "html",
            "permission_reminder": False,
            "company": "Test Company",
            "address1": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip": "12345",
            "country": "US"
        }
        
        result = self.client.create_list(list_data)
        
        assert result["id"] == "new_list"
        assert result["name"] == "New List"
        mock_post.assert_called_once_with(
            f"{self.client.base_url}/lists",
            json=list_data
        )
    
    @patch('requests.Session.post')
    def test_batch_subscribe(self, mock_post):
        """Test batch subscribing members"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_created": 2,
            "total_updated": 0,
            "errors": []
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        members = [
            {"email": "test1@example.com", "status": "subscribed"},
            {"email": "test2@example.com", "status": "subscribed"}
        ]
        
        result = self.client.batch_subscribe("list123", members)
        
        assert result["total_created"] == 2
        assert result["total_updated"] == 0
        assert len(result["errors"]) == 0
        mock_post.assert_called_once()
        
        # Check the request data
        call_args = mock_post.call_args
        assert "members" in call_args[1]["json"]
        assert len(call_args[1]["json"]["members"]) == 2
    
    @patch('requests.Session.post')
    def test_batch_subscribe_with_errors(self, mock_post):
        """Test batch subscribing with some errors"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_created": 1,
            "total_updated": 0,
            "errors": [
                {
                    "email_address": "invalid-email",
                    "error": "Invalid email address"
                }
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        members = [
            {"email": "valid@example.com", "status": "subscribed"},
            {"email": "invalid-email", "status": "subscribed"}
        ]
        
        result = self.client.batch_subscribe("list123", members)
        
        assert result["total_created"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["email_address"] == "invalid-email"
    
    @patch('requests.Session.post')
    def test_batch_update_members(self, mock_post):
        """Test batch updating multiple members"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success_count": 2,
            "error_count": 0,
            "errors": []
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        updates = [
            {"email": "test1@example.com", "merge_fields": {"FNAME": "John"}},
            {"email": "test2@example.com", "merge_fields": {"FNAME": "Jane"}}
        ]
        
        result = self.client.batch_update_members("list123", updates)
        
        assert result["success_count"] == 2
        assert result["error_count"] == 0
        assert len(result["errors"]) == 0
    
    @patch('requests.Session.post')
    def test_create_ab_test_campaign(self, mock_post):
        """Test creating A/B test campaign"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "campaign123",
            "type": "ab_split",
            "settings": {
                "title": "A/B Test Campaign"
            }
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.create_ab_test_campaign(
            subject_a="Subject A",
            subject_b="Subject B",
            content_a="Content A",
            content_b="Content B",
            list_id="list123"
        )
        
        assert result["id"] == "campaign123"
        assert result["type"] == "ab_split"
        mock_post.assert_called_once()
        
        # Check the request data structure
        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        assert request_data["type"] == "ab_split"
        assert "content_a" in request_data
        assert "content_b" in request_data
    
    @patch('requests.Session.get')
    def test_get_campaign_analytics(self, mock_get):
        """Test getting campaign analytics"""
        mock_response = Mock()
        mock_response.json.return_value = {
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
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_campaign_analytics("campaign123")
        
        assert result["sends"] == 1000
        assert result["opens"] == 500
        assert result["clicks"] == 100
        assert result["revenue"] == 1000.50
        assert "list_stats" in result
        assert len(result["list_stats"]) == 1
    
    @patch('requests.Session.get')
    def test_get_list_insights(self, mock_get):
        """Test getting list insights"""
        mock_response = Mock()
        mock_response.json.return_value = {
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
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_list_insights("list123")
        
        assert result["list_id"] == "list123"
        assert result["member_count"] == 5000
        assert result["unsubscribe_count"] == 250
        assert result["avg_sub_rate"] == 0.95
        assert result["open_rate"] == 0.42
        assert result["click_rate"] == 0.06
    
    @patch('requests.Session.get')
    def test_get_list_insights_with_error(self, mock_get):
        """Test getting list insights with API error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_get.return_value = mock_response
        
        result = self.client.get_list_insights("list123")
        
        assert "error" in result
        assert result["error"] == "API Error"
    
    @patch('requests.Session.post')
    def test_send_campaign(self, mock_post):
        """Test sending a campaign"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "send123",
            "status": "sent",
            "total_sent": 1000,
            "send_time": "2024-01-15T10:00:00+00:00"
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.send_campaign("campaign123")
        
        assert result["id"] == "send123"
        assert result["status"] == "sent"
        assert result["total_sent"] == 1000
        mock_post.assert_called_once_with(
            f"{self.client.base_url}/campaigns/campaign123/actions/send"
        )
    
    @patch('requests.Session.get')
    def test_get_member(self, mock_get):
        """Test getting member information"""
        mock_response = Mock()
        mock_response.json.return_value = {
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
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_member("list123", "test@example.com")
        
        assert result["id"] == "member123"
        assert result["email_address"] == "test@example.com"
        assert result["status"] == "subscribed"
        assert result["merge_fields"]["FNAME"] == "John"
    
    @patch('requests.Session.delete')
    def test_remove_member(self, mock_delete):
        """Test removing a member"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "unsubscribed",
            "timestamp": "2024-01-15T10:00:00+00:00"
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        result = self.client.remove_member("list123", "test@example.com")
        
        assert result["status"] == "unsubscribed"
        mock_delete.assert_called_once_with(
            f"{self.client.base_url}/lists/list123/members/5d41402c8044a4099552e855fda2a6e"
        )
    
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
            
            result = self.client._make_request('GET', '/test')
            
            assert "error" in result
            assert result["error"] == "Bad request"
    
    def test_retry_strategy(self):
        """Test retry strategy configuration"""
        # Check that retry strategy is properly configured
        adapter = self.client.session.get_adapter("https://")
        assert adapter.max_retries.total == 3
        assert adapter.max_retries.backoff_factor == 1
        assert 429 in adapter.max_retries.status_forcelist
        assert 500 in adapter.max_retries.status_forcelist
    
    @patch('requests.Session.get')
    def test_get_campaign_analytics_with_multiple_lists(self, mock_get):
        """Test campaign analytics with multiple lists"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "sends": 2000,
            "opens": 1000,
            "clicks": 200,
            "bounces": 100,
            "unsubscribes": 50,
            "revenue": 2000.00,
            "list_stats": [
                {
                    "list_id": "list123",
                    "sends": 1000,
                    "opens": 500,
                    "clicks": 100
                },
                {
                    "list_id": "list456",
                    "sends": 1000,
                    "opens": 500,
                    "clicks": 100
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_campaign_analytics("campaign123")
        
        assert result["sends"] == 2000
        assert len(result["list_stats"]) == 2
        assert result["list_stats"][0]["list_id"] == "list123"
        assert result["list_stats"][1]["list_id"] == "list456"
    
    @patch('requests.Session.post')
    def test_batch_subscribe_large_batch(self, mock_post):
        """Test batch subscribing with large member list"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_created": 100,
            "total_updated": 0,
            "errors": []
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create 100 members
        members = [
            {"email": f"test{i}@example.com", "status": "subscribed"}
            for i in range(100)
        ]
        
        result = self.client.batch_subscribe("list123", members)
        
        assert result["total_created"] == 100
        assert result["total_updated"] == 0
        assert len(result["errors"]) == 0
    
    @patch('requests.Session.post')
    def test_create_ab_test_campaign_with_options(self, mock_post):
        """Test creating A/B test campaign with additional options"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "campaign456",
            "type": "ab_split",
            "settings": {
                "title": "Advanced A/B Test Campaign"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.create_ab_test_campaign(
            subject_a="Subject A",
            subject_b="Subject B", 
            content_a="Content A",
            content_b="Content B",
            list_id="list123",
            split_size=50,
            winner_criteria="open_rate"
        )
        
        assert result["id"] == "campaign456"
        assert result["type"] == "ab_split"
        
        # Check that additional options were included
        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        assert request_data["split_size"] == 50
        assert request_data["winner_criteria"] == "open_rate"
    
    @patch('requests.Session.get')
    def test_get_list_insights_detailed(self, mock_get):
        """Test getting detailed list insights"""
        mock_response = Mock()
        mock_response.json.return_value = {
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
            "click_rate": 0.06,
            "growth_rate": 0.02,
            "activity_score": 8.5,
            "list_rating": "A",
            "industry_stats": {
                "avg_open_rate": 0.35,
                "avg_click_rate": 0.04
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_list_insights("list123")
        
        assert result["growth_rate"] == 0.02
        assert result["activity_score"] == 8.5
        assert result["list_rating"] == "A"
        assert "industry_stats" in result
        assert result["industry_stats"]["avg_open_rate"] == 0.35


class TestMailchimpClientIntegration:
    """Integration tests for Mailchimp client"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.test_api_key = "test-api-key-us1"
        self.client = MailchimpClient(api_key=self.test_api_key)
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow with mocked API calls"""
        with patch('requests.Session.get') as mock_get, \
             patch('requests.Session.post') as mock_post, \
             patch('requests.Session.delete') as mock_delete:
            
            # Mock all API responses
            mock_get.return_value.json.return_value = {"lists": []}
            mock_post.return_value.json.return_value = {"id": "test"}
            mock_delete.return_value.json.return_value = {"status": "ok"}
            
            # Create list
            list_data = {"name": "Test List", "email_type": "html"}
            list_result = self.client.create_list(list_data)
            assert "id" in list_result
            
            # Batch subscribe members
            members = [
                {"email": "test1@example.com", "status": "subscribed"},
                {"email": "test2@example.com", "status": "subscribed"}
            ]
            batch_result = self.client.batch_subscribe("test_list", members)
            assert batch_result["total_created"] == 2
            
            # Create A/B test campaign
            ab_result = self.client.create_ab_test_campaign(
                subject_a="Subject A",
                subject_b="Subject B",
                content_a="Content A",
                content_b="Content B",
                list_id="test_list"
            )
            assert "id" in ab_result
            
            # Get campaign analytics
            analytics_result = self.client.get_campaign_analytics(ab_result["id"])
            assert "sends" in analytics_result
            
            # Get list insights
            insights_result = self.client.get_list_insights("test_list")
            assert "member_count" in insights_result
    
    def test_error_handling_workflow(self):
        """Test error handling in workflow"""
        with patch('requests.Session.post') as mock_post:
            # Mock API error
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid data"}
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
            mock_post.return_value = mock_response
            
            # Try batch subscribe with invalid data
            members = [
                {"email": "invalid-email", "status": "subscribed"}
            ]
            result = self.client.batch_subscribe("test_list", members)
            
            # Should handle error gracefully
            assert "error" in result
    
    def test_performance_with_large_data(self):
        """Test performance with large datasets"""
        with patch('requests.Session.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {
                "total_created": 1000,
                "total_updated": 0,
                "errors": []
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
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
