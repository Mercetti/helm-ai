"""
Helm AI Enterprise SSO Configuration
This module provides enterprise SSO configuration and setup utilities
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SSOProvider:
    """SSO provider configuration"""
    name: str
    type: str  # oauth2, saml, oidc
    display_name: str
    enabled: bool = True
    config: Dict[str, Any] = None
    created_at: datetime = None

class EnterpriseSSO:
    """Enterprise SSO configuration manager"""
    
    def __init__(self):
        self.providers: Dict[str, SSOProvider] = {}
        self._load_default_providers()
    
    def _load_default_providers(self):
        """Load default SSO provider configurations"""
        # Google Workspace
        google_provider = SSOProvider(
            name="google",
            type="oauth2",
            display_name="Google Workspace",
            enabled=bool(os.getenv('GOOGLE_CLIENT_ID')),
            config={
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "redirect_uri": os.getenv('GOOGLE_REDIRECT_URI', 'https://helm-ai.com/auth/google/callback'),
                "scope": "openid profile email",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo"
            }
        )
        self.providers["google"] = google_provider
        
        # Microsoft Azure AD
        microsoft_provider = SSOProvider(
            name="microsoft",
            type="oauth2",
            display_name="Microsoft Azure AD",
            enabled=bool(os.getenv('MICROSOFT_CLIENT_ID')),
            config={
                "client_id": os.getenv('MICROSOFT_CLIENT_ID'),
                "client_secret": os.getenv('MICROSOFT_CLIENT_SECRET'),
                "redirect_uri": os.getenv('MICROSOFT_REDIRECT_URI', 'https://helm-ai.com/auth/microsoft/callback'),
                "scope": "openid profile email",
                "tenant_id": os.getenv('MICROSOFT_TENANT_ID', 'common'),
                "auth_url": "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me"
            }
        )
        self.providers["microsoft"] = microsoft_provider
        
        # Okta
        okta_provider = SSOProvider(
            name="okta",
            type="oauth2",
            display_name="Okta",
            enabled=bool(os.getenv('OKTA_CLIENT_ID')),
            config={
                "client_id": os.getenv('OKTA_CLIENT_ID'),
                "client_secret": os.getenv('OKTA_CLIENT_SECRET'),
                "redirect_uri": os.getenv('OKTA_REDIRECT_URI', 'https://helm-ai.com/auth/okta/callback'),
                "scope": "openid profile email",
                "domain": os.getenv('OKTA_DOMAIN'),
                "auth_url": "https://{domain}/oauth2/v1/authorize",
                "token_url": "https://{domain}/oauth2/v1/token",
                "user_info_url": "https://{domain}/oauth2/v1/userinfo"
            }
        )
        self.providers["okta"] = okta_provider
        
        # SAML (generic)
        saml_provider = SSOProvider(
            name="saml",
            type="saml",
            display_name="SAML SSO",
            enabled=bool(os.getenv('SAML_ENTITY_ID')),
            config={
                "entity_id": os.getenv('SAML_ENTITY_ID'),
                "sso_url": os.getenv('SAML_SSO_URL'),
                "slo_url": os.getenv('SAML_SLO_URL'),
                "certificate": os.getenv('SAML_CERTIFICATE'),
                "private_key": os.getenv('SAML_PRIVATE_KEY'),
                "name_id_format": os.getenv('SAML_NAME_ID_FORMAT', 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress')
            }
        )
        self.providers["saml"] = saml_provider
    
    def get_provider(self, name: str) -> Optional[SSOProvider]:
        """Get SSO provider by name"""
        return self.providers.get(name)
    
    def get_enabled_providers(self) -> List[SSOProvider]:
        """Get all enabled SSO providers"""
        return [provider for provider in self.providers.values() if provider.enabled]
    
    def get_all_providers(self) -> List[SSOProvider]:
        """Get all SSO providers"""
        return list(self.providers.values())
    
    def enable_provider(self, name: str) -> bool:
        """Enable SSO provider"""
        provider = self.get_provider(name)
        if provider:
            provider.enabled = True
            return True
        return False
    
    def disable_provider(self, name: str) -> bool:
        """Disable SSO provider"""
        provider = self.get_provider(name)
        if provider:
            provider.enabled = False
            return True
        return False
    
    def add_provider(self, provider: SSOProvider) -> bool:
        """Add new SSO provider"""
        if provider.name in self.providers:
            return False
        
        self.providers[provider.name] = provider
        return True
    
    def remove_provider(self, name: str) -> bool:
        """Remove SSO provider"""
        if name in self.providers:
            del self.providers[name]
            return True
        return False
    
    def update_provider_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Update provider configuration"""
        provider = self.get_provider(name)
        if provider:
            provider.config.update(config)
            return True
        return False
    
    def validate_provider_config(self, name: str) -> Dict[str, Any]:
        """Validate provider configuration"""
        provider = self.get_provider(name)
        if not provider:
            return {"valid": False, "error": "Provider not found"}
        
        errors = []
        warnings = []
        
        if provider.type == "oauth2":
            required_fields = ["client_id", "client_secret", "redirect_uri"]
            for field in required_fields:
                if not provider.config.get(field):
                    errors.append(f"Missing required field: {field}")
            
            # Check redirect URI format
            redirect_uri = provider.config.get("redirect_uri", "")
            if not redirect_uri.startswith("https://"):
                warnings.append("Redirect URI should use HTTPS")
        
        elif provider.type == "saml":
            required_fields = ["entity_id", "sso_url"]
            for field in required_fields:
                if not provider.config.get(field):
                    errors.append(f"Missing required field: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_provider_metadata(self, name: str) -> Dict[str, Any]:
        """Get provider metadata for discovery"""
        provider = self.get_provider(name)
        if not provider:
            return {}
        
        metadata = {
            "name": provider.name,
            "type": provider.type,
            "display_name": provider.display_name,
            "enabled": provider.enabled
        }
        
        if provider.type == "oauth2":
            metadata.update({
                "authorization_url": provider.config.get("auth_url", "").format(**provider.config),
                "scopes": provider.config.get("scope", "").split(),
                "response_types": ["code"],
                "grant_types": ["authorization_code", "refresh_token"]
            })
        
        return metadata
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export SSO configuration"""
        return {
            "providers": {
                name: {
                    "type": provider.type,
                    "display_name": provider.display_name,
                    "enabled": provider.enabled,
                    "config": {k: v for k, v in (provider.config or {}).items() 
                              if not any(secret in k.lower() for secret in ['secret', 'key', 'password'])}
                }
                for name, provider in self.providers.items()
            }
        }
    
    def import_configuration(self, config: Dict[str, Any]) -> bool:
        """Import SSO configuration"""
        try:
            for name, provider_data in config.get("providers", {}).items():
                provider = SSOProvider(
                    name=name,
                    type=provider_data["type"],
                    display_name=provider_data["display_name"],
                    enabled=provider_data.get("enabled", False),
                    config=provider_data.get("config", {})
                )
                self.providers[name] = provider
            
            return True
        except Exception as e:
            logger.error(f"Failed to import SSO configuration: {e}")
            return False
    
    def generate_setup_instructions(self, provider_name: str) -> Dict[str, Any]:
        """Generate setup instructions for provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {"error": "Provider not found"}
        
        instructions = {
            "provider": provider.display_name,
            "type": provider.type,
            "steps": []
        }
        
        if provider_name == "google":
            instructions["steps"] = [
                "1. Go to Google Cloud Console (console.cloud.google.com)",
                "2. Create a new project or select existing project",
                "3. Enable Google+ API and Google OAuth2 API",
                "4. Go to Credentials -> Create Credentials -> OAuth client ID",
                "5. Select 'Web application' as application type",
                "6. Add authorized redirect URI: " + provider.config.get("redirect_uri", ""),
                "7. Copy Client ID and Client Secret to environment variables",
                "8. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment"
            ]
        
        elif provider_name == "microsoft":
            instructions["steps"] = [
                "1. Go to Azure Portal (portal.azure.com)",
                "2. Navigate to Azure Active Directory",
                "3. Go to App registrations -> New registration",
                "4. Enter application name and select supported account types",
                "5. Add redirect URI: " + provider.config.get("redirect_uri", ""),
                "6. Go to Authentication and enable ID tokens",
                "7. Go to Certificates & secrets to create client secret",
                "8. Copy Application ID and client secret to environment variables",
                "9. Set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET in your environment"
            ]
        
        elif provider_name == "okta":
            instructions["steps"] = [
                "1. Login to Okta Admin Console",
                "2. Go to Applications -> Applications -> Create App Integration",
                "3. Select 'OIDC - OpenID Connect' and 'Web Application'",
                "4. Configure application settings",
                "5. Add redirect URI: " + provider.config.get("redirect_uri", ""),
                "6. Go to Sign On tab to get authorization server info",
                "7. Go to Client Credentials to get Client ID and Secret",
                "8. Set OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, and OKTA_DOMAIN in environment"
            ]
        
        elif provider_name == "saml":
            instructions["steps"] = [
                "1. Obtain SAML metadata from your identity provider",
                "2. Extract Entity ID, SSO URL, and certificate",
                "3. Generate private key for your service provider",
                "4. Configure SAML settings in your identity provider",
                "5. Set SAML_ENTITY_ID, SAML_SSO_URL, and SAML_CERTIFICATE in environment",
                "6. Optionally set SAML_PRIVATE_KEY for signed requests"
            ]
        
        return instructions
    
    def test_provider_connection(self, provider_name: str) -> Dict[str, Any]:
        """Test connection to SSO provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {"success": False, "error": "Provider not found"}
        
        try:
            if provider.type == "oauth2":
                # Test OAuth2 configuration by checking well-known endpoints
                auth_url = provider.config.get("auth_url", "").format(**provider.config)
                if not auth_url:
                    return {"success": False, "error": "Invalid authorization URL"}
                
                # For now, just validate URL format
                if auth_url.startswith("https://"):
                    return {"success": True, "message": "Provider configuration appears valid"}
                else:
                    return {"success": False, "error": "Authorization URL must use HTTPS"}
            
            elif provider.type == "saml":
                # Test SAML configuration
                entity_id = provider.config.get("entity_id")
                sso_url = provider.config.get("sso_url")
                
                if entity_id and sso_url:
                    return {"success": True, "message": "SAML configuration appears valid"}
                else:
                    return {"success": False, "error": "Missing SAML configuration"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unknown provider type"}


# Global instance
enterprise_sso = EnterpriseSSO()
