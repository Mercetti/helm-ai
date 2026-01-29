"""
Helm AI OAuth2 Provider Integration
This module provides OAuth2 integration for enterprise SSO with multiple providers
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import secrets
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)

class OAuth2Provider:
    """Base OAuth2 provider class"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str = "openid profile email"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.session = requests.Session()
    
    def get_authorization_url(self, state: str = None, **kwargs) -> str:
        raise NotImplementedError
    
    def exchange_code_for_token(self, code: str, state: str = None) -> Dict[str, Any]:
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        raise NotImplementedError


class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri, "openid profile email")
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str = None, **kwargs) -> str:
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        params.update(kwargs)
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, state: str = None) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = self.session.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.session.get(self.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()


class MicrosoftOAuth2Provider(OAuth2Provider):
    """Microsoft Azure AD OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant_id: str = "common"):
        super().__init__(client_id, client_secret, redirect_uri, "openid profile email")
        self.tenant_id = tenant_id
        self.auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.user_info_url = "https://graph.microsoft.com/v1.0/me"
    
    def get_authorization_url(self, state: str = None, **kwargs) -> str:
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
            "response_mode": "query"
        }
        params.update(kwargs)
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, state: str = None) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = self.session.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.session.get(self.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()


class SAMLProvider:
    """SAML provider for enterprise SSO"""
    
    def __init__(self, entity_id: str, sso_url: str, slo_url: str = None):
        self.entity_id = entity_id
        self.sso_url = sso_url
        self.slo_url = slo_url
    
    def get_sso_url(self, relay_state: str = None) -> str:
        """Get SSO URL for SAML authentication"""
        # This would require a SAML library like python3-saml
        # For now, return the base SSO URL
        return self.sso_url


class SSOManager:
    """SSO manager for multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize configured SSO providers"""
        # Google OAuth2
        if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
            self.providers['google'] = GoogleOAuth2Provider(
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'https://helm-ai.com/auth/google/callback')
            )
        
        # Microsoft OAuth2
        if os.getenv('MICROSOFT_CLIENT_ID') and os.getenv('MICROSOFT_CLIENT_SECRET'):
            self.providers['microsoft'] = MicrosoftOAuth2Provider(
                client_id=os.getenv('MICROSOFT_CLIENT_ID'),
                client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
                redirect_uri=os.getenv('MICROSOFT_REDIRECT_URI', 'https://helm-ai.com/auth/microsoft/callback'),
                tenant_id=os.getenv('MICROSOFT_TENANT_ID', 'common')
            )
        
        # SAML
        if os.getenv('SAML_ENTITY_ID') and os.getenv('SAML_SSO_URL'):
            self.providers['saml'] = SAMLProvider(
                entity_id=os.getenv('SAML_ENTITY_ID'),
                sso_url=os.getenv('SAML_SSO_URL'),
                slo_url=os.getenv('SAML_SLO_URL')
            )
    
    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """Get SSO provider by name"""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available SSO providers"""
        return list(self.providers.keys())
    
    def authenticate_user(self, provider_name: str, code: str, state: str = None) -> Dict[str, Any]:
        """Authenticate user using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        
        # Exchange code for token
        token_data = provider.exchange_code_for_token(code, state)
        
        # Get user info
        user_info = provider.get_user_info(token_data['access_token'])
        
        return {
            'provider': provider_name,
            'user_info': user_info,
            'token_data': token_data,
            'authenticated_at': datetime.now().isoformat()
        }
