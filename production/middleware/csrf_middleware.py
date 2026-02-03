#!/usr/bin/env python3
import json
import secrets
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CSRFProtectionMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.config_file = "production/config/csrf_protection_config.json"
        self.data_file = "production/storage/csrf/csrf_data.json"
        self.load_configuration()
        self.load_data()
        
    def load_configuration(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"enabled": False}
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"active_tokens": {}, "token_statistics": {}}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    def generate_token(self, session_id: str = None) -> str:
        if not self.config.get("enabled", False):
            return ""
        
        token = secrets.token_urlsafe(self.config.get("token_length", 32))
        current_time = datetime.now()
        expiry = current_time + timedelta(seconds=self.config.get("token_expiry", 3600))
        
        token_data = {
            "token": token,
            "created_at": current_time.isoformat(),
            "expires_at": expiry.isoformat(),
            "session_id": session_id,
            "used": False
        }
        
        # Store token
        if "active_tokens" not in self.data:
            self.data["active_tokens"] = {}
        
        self.data["active_tokens"][token] = token_data
        
        # Update statistics
        if "token_statistics" not in self.data:
            self.data["token_statistics"] = {}
        
        self.data["token_statistics"]["tokens_generated"] = self.data["token_statistics"].get("tokens_generated", 0) + 1
        self.data["token_statistics"]["last_token_generated"] = current_time.isoformat()
        
        self.save_data()
        return token
    
    def validate_token(self, token: str, session_id: str = None) -> Dict[str, Any]:
        if not self.config.get("enabled", False):
            return {"valid": True, "reason": "CSRF protection disabled"}
        
        if not token:
            return {"valid": False, "reason": "No token provided"}
        
        # Check if token exists
        active_tokens = self.data.get("active_tokens", {})
        if token not in active_tokens:
            return {"valid": False, "reason": "Invalid token"}
        
        token_data = active_tokens[token]
        current_time = datetime.now()
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if current_time > expires_at:
            # Remove expired token
            del active_tokens[token]
            self.data["token_statistics"]["tokens_expired"] = self.data["token_statistics"].get("tokens_expired", 0) + 1
            self.save_data()
            return {"valid": False, "reason": "Token expired"}
        
        # Check session ID if provided
        if session_id and token_data.get("session_id") and token_data["session_id"] != session_id:
            return {"valid": False, "reason": "Session mismatch"}
        
        # Mark token as used (optional one-time use)
        token_data["used"] = True
        
        # Update statistics
        self.data["token_statistics"]["tokens_validated"] = self.data["token_statistics"].get("tokens_validated", 0) + 1
        
        self.save_data()
        return {"valid": True, "reason": "Token valid"}
    
    def is_endpoint_exempt(self, endpoint: str) -> bool:
        exempt_endpoints = self.config.get("exempt_endpoints", [])
        return endpoint in exempt_endpoints
    
    def cleanup_expired_tokens(self):
        current_time = datetime.now()
        expired_tokens = []
        
        for token, token_data in self.data.get("active_tokens", {}).items():
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        # Remove expired tokens
        for token in expired_tokens:
            del self.data["active_tokens"][token]
        
        if expired_tokens:
            self.data["token_statistics"]["tokens_expired"] = self.data["token_statistics"].get("tokens_expired", 0) + len(expired_tokens)
            self.data["token_statistics"]["last_cleanup"] = current_time.isoformat()
            self.save_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        stats = self.data.get("token_statistics", {})
        stats["active_tokens"] = len(self.data.get("active_tokens", {}))
        return stats
    
    def refresh_token(self, old_token: str, session_id: str = None) -> Optional[str]:
        if not self.config.get("enabled", False):
            return None
        
        # Validate old token
        validation = self.validate_token(old_token, session_id)
        if not validation["valid"]:
            return None
        
        # Generate new token
        new_token = self.generate_token(session_id)
        
        # Invalidate old token
        if old_token in self.data.get("active_tokens", {}):
            del self.data["active_tokens"][old_token]
        
        return new_token
