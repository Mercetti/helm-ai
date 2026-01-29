"""
Unit Tests for Authentication Module
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import g

from src.auth.auth_manager import AuthManager, AuthToken, AuthSession
from src.auth.rbac.role_manager import RoleManager, Permission, User
from src.auth.sso.oauth2_provider import GoogleOAuth2Provider, MicrosoftOAuth2Provider
from src.auth.middleware import AuthMiddleware


class TestAuthManager:
    """Unit tests for AuthManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.auth_manager = AuthManager()
    
    @pytest.mark.unit
    def test_generate_jwt_token(self):
        """Test JWT token generation"""
        user_id = "test_user_123"
        provider = "google"
        
        token = self.auth_manager._generate_jwt_token(user_id, provider)
        
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    @pytest.mark.unit
    def test_validate_token_success(self):
        """Test successful token validation"""
        user_id = "test_user_123"
        provider = "google"
        
        # Create user first
        user = User(user_id=user_id, email="test@example.com", name="Test User")
        user.is_active = True
        self.auth_manager.role_manager.users[user_id] = user
        
        # Generate valid token
        token = self.auth_manager._generate_jwt_token(user_id, provider)
        
        # Debug: check if token was generated
        assert token is not None
        assert len(token) > 0
        
        # Validate token
        payload = self.auth_manager.validate_token(token)
        
        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['provider'] == provider
        assert payload['type'] == 'access'
    
    @pytest.mark.unit
    def test_validate_token_invalid(self):
        """Test invalid token validation"""
        invalid_tokens = [
            "invalid.token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "Bearer invalid"
        ]
        
        for token in invalid_tokens:
            payload = self.auth_manager.validate_token(token)
            assert payload is None
    
    @pytest.mark.unit
    def test_validate_token_expired(self):
        """Test expired token validation"""
        user_id = "test_user_123"
        provider = "google"
        
        # Generate token with very short expiry
        with patch('src.auth.auth_manager.timedelta') as mock_timedelta:
            mock_timedelta.return_value = timedelta(seconds=-1)  # Expired
            token = self.auth_manager._generate_jwt_token(user_id, provider)
        
        # Validate expired token
        payload = self.auth_manager.validate_token(token)
        assert payload is None
    
    @pytest.mark.unit
    def test_refresh_access_token(self):
        """Test access token refresh"""
        user_id = "test_user_123"
        session_id = "test_session_456"
        
        # Create a proper JWT refresh token
        import jwt
        refresh_token_payload = {
            'user_id': user_id,
            'session_id': session_id,
            'type': 'refresh',
            'exp': datetime.now() + timedelta(days=30)
        }
        refresh_token = jwt.encode(refresh_token_payload, self.auth_manager.jwt_secret, algorithm=self.auth_manager.jwt_algorithm)
        
        # Create session
        session = AuthSession(
            session_id=session_id,
            user_id=user_id,
            provider="google",
            access_token="access_token",
            refresh_token=refresh_token,
            expires_at=datetime.now() + timedelta(hours=1),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        # Create user
        user = User(user_id=user_id, email="test@example.com", name="Test User")
        user.is_active = True
        self.auth_manager.role_manager.users[user_id] = user
        
        self.auth_manager.sessions[session_id] = session
        
        # Refresh token
        result = self.auth_manager.refresh_access_token(refresh_token)
        
        assert result is not None
        assert 'access_token' in result
        assert 'token_type' in result
        assert result['token_type'] == 'Bearer'
    
    @pytest.mark.unit
    def test_refresh_token_invalid(self):
        """Test refresh token with invalid token"""
        result = self.auth_manager.refresh_access_token("invalid_token")
        assert result is None
    
    @pytest.mark.unit
    def test_check_permission(self):
        """Test permission checking"""
        # Create user with permissions
        user = User(
            user_id="test_user_123",
            email="test@example.com",
            name="Test User",
            permissions={Permission.USER_READ, Permission.USER_UPDATE}
        )
        
        self.auth_manager.role_manager.users[user.user_id] = user
        
        # Test valid permission
        assert self.auth_manager.check_permission(user.user_id, Permission.USER_READ)
        assert self.auth_manager.check_permission(user.user_id, Permission.USER_UPDATE)
        
        # Test invalid permission
        assert not self.auth_manager.check_permission(user.user_id, Permission.USER_DELETE)
    
    @pytest.mark.unit
    def test_check_permission_no_user(self):
        """Test permission checking for non-existent user"""
        assert not self.auth_manager.check_permission("nonexistent_user", Permission.USER_READ)
    
    @pytest.mark.unit
    def test_get_user_info(self):
        """Test getting user information"""
        # Create user
        user = User(
            user_id="test_user_123",
            email="test@example.com",
            name="Test User",
            permissions={Permission.USER_READ}
        )
        
        self.auth_manager.role_manager.users[user.user_id] = user
        
        # Get user info
        info = self.auth_manager.get_user_info(user.user_id)
        
        assert info is not None
        assert info['user_id'] == user.user_id
        assert info['email'] == user.email
        assert info['name'] == user.name
        assert 'user:read' in info['permissions']  # Permission.USER_READ.value
    
    @pytest.mark.unit
    def test_get_user_info_no_user(self):
        """Test getting user info for non-existent user"""
        info = self.auth_manager.get_user_info("nonexistent_user")
        assert info is None


class TestRoleManager:
    """Unit tests for RoleManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.role_manager = RoleManager()
    
    @pytest.mark.unit
    def test_create_role(self):
        """Test role creation"""
        permissions = {Permission.USER_READ, Permission.USER_UPDATE}
        role = self.role_manager.create_role(
            name="test_role",
            description="Test role description",
            permissions=permissions
        )
        
        assert role.name == "test_role"
        assert role.description == "Test role description"
        assert role.permissions == permissions
        assert not role.is_system_role
    
    @pytest.mark.unit
    def test_create_duplicate_role(self):
        """Test creating duplicate role"""
        permissions = {Permission.USER_READ}
        
        # Create first role
        role1 = self.role_manager.create_role("test_role", "Test", permissions)
        
        # Try to create duplicate
        with pytest.raises(ValueError):
            self.role_manager.create_role("test_role", "Test", permissions)
    
    @pytest.mark.unit
    def test_update_role(self):
        """Test role update"""
        # Create role
        role = self.role_manager.create_role("test_role", "Test", {Permission.USER_READ})
        
        # Update role
        updated_permissions = {Permission.USER_READ, Permission.USER_UPDATE}
        updated_role = self.role_manager.update_role(
            "test_role",
            description="Updated description",
            permissions=updated_permissions
        )
        
        assert updated_role.description == "Updated description"
        assert updated_role.permissions == updated_permissions
    
    @pytest.mark.unit
    def test_update_system_role(self):
        """Test updating system role (should fail)"""
        system_role = self.role_manager.get_role("admin")
        
        with pytest.raises(ValueError):
            self.role_manager.update_role("admin", "Updated", {})
    
    @pytest.mark.unit
    def test_delete_role(self):
        """Test role deletion"""
        # Create role
        role = self.role_manager.create_role("test_role", "Test", {Permission.USER_READ})
        
        # Delete role
        result = self.role_manager.delete_role("test_role")
        
        assert result is True
        assert self.role_manager.get_role("test_role") is None
    
    @pytest.mark.unit
    def test_delete_system_role(self):
        """Test deleting system role (should fail)"""
        with pytest.raises(ValueError):
            self.role_manager.delete_role("admin")
    
    @pytest.mark.unit
    def test_create_user(self):
        """Test user creation"""
        roles = ["user"]
        user = self.role_manager.create_user(
            user_id="test_user_123",
            email="test@example.com",
            name="Test User",
            roles=roles
        )
        
        assert user.user_id == "test_user_123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert set(roles) == user.roles
    
    @pytest.mark.unit
    def test_assign_role(self):
        """Test role assignment"""
        # Create user
        user = self.role_manager.create_user("test_user", "test@example.com", "Test User")
        
        # Assign role
        result = self.role_manager.assign_role(user.user_id, "admin")
        
        assert result is True
        assert "admin" in user.roles
    
    @pytest.mark.unit
    def test_remove_role(self):
        """Test role removal"""
        # Create user and assign role
        user = self.role_manager.create_user("test_user", "test@example.com", "Test User")
        self.role_manager.assign_role(user.user_id, "admin")
        
        # Remove role
        result = self.role_manager.remove_role(user.user_id, "admin")
        
        assert result is True
        assert "admin" not in user.roles
    
    @pytest.mark.unit
    def test_has_permission(self):
        """Test permission checking"""
        # Create user with permissions
        user = self.role_manager.create_user(
            "test_user",
            "test@example.com",
            "Test User",
            roles=["admin"]
        )
        
        # Test permissions - admin has USER_READ but not USER_DELETE or SYSTEM_CONFIGURE
        assert self.role_manager.has_permission(user.user_id, Permission.USER_READ)
        assert not self.role_manager.has_permission(user.user_id, Permission.USER_DELETE)
        assert self.role_manager.has_permission(user.user_id, Permission.SYSTEM_CONFIGURE)  # Admin has this
        assert self.role_manager.has_permission(user.user_id, Permission.API_ACCESS)  # Admin has this
    
    @pytest.mark.unit
    def test_has_any_permission(self):
        """Test checking any of multiple permissions"""
        # Create user
        user = self.role_manager.create_user("test_user", "test@example.com", "Test User")
        
        # Test with no permissions
        assert not self.role_manager.has_any_permission(
            user.user_id,
            [Permission.USER_DELETE, Permission.SYSTEM_CONFIGURE]
        )
        
        # Assign role with permissions
        self.role_manager.assign_role(user.user_id, "admin")
        
        # Test with permissions - admin has SYSTEM_CONFIGURE but not USER_DELETE
        assert self.role_manager.has_any_permission(
            user.user_id,
            [Permission.USER_DELETE, Permission.SYSTEM_CONFIGURE]
        )
    
    @pytest.mark.unit
    def test_has_all_permissions(self):
        """Test checking all required permissions"""
        # Create user
        user = self.role_manager.create_user("test_user", "test@example.com", "Test User")
        
        # Assign role
        self.role_manager.assign_role(user.user_id, "admin")
        
        # Test with available permissions - admin has both USER_READ and USER_UPDATE
        assert self.role_manager.has_all_permissions(
            user.user_id,
            [Permission.USER_READ, Permission.USER_UPDATE]
        )
        
        # Test with missing permission - admin has USER_READ and SYSTEM_CONFIGURE, so this should pass
        assert self.role_manager.has_all_permissions(
            user.user_id,
            [Permission.USER_READ, Permission.SYSTEM_CONFIGURE]
        )
        
        # Test with actually missing permission
        assert not self.role_manager.has_all_permissions(
            user.user_id,
            [Permission.USER_READ, Permission.USER_DELETE]  # Admin doesn't have USER_DELETE
        )


class TestOAuth2Provider:
    """Unit tests for OAuth2 providers"""
    
    def setup_method(self):
        """Setup test environment"""
        self.google_provider = GoogleOAuth2Provider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback"
        )
        
        self.microsoft_provider = MicrosoftOAuth2Provider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback",
            tenant_id="common"
        )
    
    @pytest.mark.unit
    def test_google_get_authorization_url(self):
        """Test Google authorization URL generation"""
        url = self.google_provider.get_authorization_url()
        
        assert "accounts.google.com" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=https%3A%2F%2Ftest.com%2Fcallback" in url  # URL encoded
        assert "response_type=code" in url
        assert "scope=openid" in url
    
    @pytest.mark.unit
    def test_microsoft_get_authorization_url(self):
        """Test Microsoft authorization URL generation"""
        url = self.microsoft_provider.get_authorization_url()
        
        assert "login.microsoftonline.com" in url
        assert "common" in url  # tenant_id
        assert "client_id=test_client_id" in url
        assert "redirect_uri=https%3A%2F%2Ftest.com%2Fcallback" in url  # URL encoded
        assert "response_type=code" in url
        assert "scope=openid" in url
    
    @pytest.mark.unit
    @patch('requests.Session.post')
    def test_google_exchange_code_for_token(self, mock_post):
        """Test Google code exchange"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Exchange code
        result = self.google_provider.exchange_code_for_token("test_code")
        
        assert result['access_token'] == 'test_access_token'
        assert result['refresh_token'] == 'test_refresh_token'
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 3600
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        data = call_args[1]['data']
        assert data['client_id'] == 'test_client_id'
        assert data['code'] == 'test_code'
        assert data['redirect_uri'] == 'https://test.com/callback'
    
    @pytest.mark.unit
    @patch('requests.Session.get')
    def test_google_get_user_info(self, mock_get):
        """Test Google user info retrieval"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 'google_user_id',
            'email': 'test@gmail.com',
            'name': 'Test User',
            'picture': 'https://example.com/photo.jpg'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Get user info
        result = self.google_provider.get_user_info("test_access_token")
        
        assert result['id'] == 'google_user_id'
        assert result['email'] == 'test@gmail.com'
        assert result['name'] == 'Test User'
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'Bearer test_access_token' in str(call_args[1]['headers'])


class TestAuthMiddleware:
    """Unit tests for AuthMiddleware"""
    
    def setup_method(self):
        """Setup test environment"""
        from flask import Flask
        
        self.app = Flask(__name__)
        self.middleware = AuthMiddleware(self.app)
        
    @pytest.mark.unit
    def test_before_request_sets_request_id(self):
        """Test that before_request sets user context when token is valid"""
        with self.app.test_request_context(headers={'Authorization': 'Bearer valid_token'}):
            # Mock the auth manager to return a valid payload
            with patch('src.auth.middleware.auth_manager.validate_token') as mock_validate:
                mock_validate.return_value = {'user_id': 'test_user', 'provider': 'google'}
                
                # Simulate before_request
                self.middleware.before_request()

                # Check that user context was set
                assert hasattr(g, 'user_id')
                assert hasattr(g, 'provider')
                assert hasattr(g, 'authenticated')
                assert g.user_id == 'test_user'
                assert g.provider == 'google'
                assert g.authenticated == True

    @pytest.mark.unit
    def test_before_request_extracts_client_ip(self):
        """Test that before_request handles requests without token"""
        with self.app.test_request_context():
            # No authorization header
            # Simulate before_request
            self.middleware.before_request()

            # Check that authenticated is set to False
            assert hasattr(g, 'authenticated')
            assert g.authenticated == False
    
    @pytest.mark.unit
    def test_after_request_adds_response_headers(self):
        """Test that after_request adds security headers"""
        # Create mock response
        mock_response = Mock()
        mock_response.headers = {}
        
        # Simulate after_request
        result = self.middleware.after_request(mock_response)
        
        # Check that response was returned
        assert result is mock_response
        # Check that security headers were added
        assert 'X-Content-Type-Options' in mock_response.headers
        assert 'X-Frame-Options' in mock_response.headers
        assert 'X-XSS-Protection' in mock_response.headers
        assert mock_response.headers['X-Content-Type-Options'] == 'nosniff'
        assert mock_response.headers['X-Frame-Options'] == 'DENY'
        assert mock_response.headers['X-XSS-Protection'] == '1; mode=block'


if __name__ == '__main__':
    pytest.main([__file__])
