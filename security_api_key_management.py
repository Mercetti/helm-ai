#!/usr/bin/env python3
"""
API Key Management System
Secure API key generation, management, and validation for Stella Logic AI
"""

import os
import secrets
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from flask import Flask, request, abort, current_app, g
from functools import wraps
import base64
import cryptography.fernet
from cryptography.fernet import Fernet

class APIKeyManager:
    """Secure API key management system"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.keys_file = 'api_keys.json'
        self.encryption_key_file = 'api_key_encryption.key'
        self.fernet = None
        self.api_keys = {}
        self.key_prefix = 'stella_api_'
        self.default_key_length = 32
        self.max_keys_per_user = 10
        self.key_expiry_days = 365
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize API key manager"""
        self.app = app
        app.api_key_manager = self
        
        # Initialize encryption
        self._init_encryption()
        
        # Load existing keys
        self.load_keys()
        
        # Register before request handler for API key validation
        app.before_request(self._validate_api_key)
    
    def _init_encryption(self):
        """Initialize encryption for storing API keys"""
        try:
            # Try to load existing encryption key
            if os.path.exists(self.encryption_key_file):
                with open(self.encryption_key_file, 'rb') as f:
                    key = f.read()
                    self.fernet = Fernet(key)
            else:
                # Generate new encryption key
                key = Fernet.generate_key()
                self.fernet = Fernet(key)
                
                # Save encryption key
                with open(self.encryption_key_file, 'wb') as f:
                    f.write(key)
                
                print(f"✅ Generated new encryption key for API keys")
            
            print("✅ API key encryption initialized")
            
        except Exception as e:
            print(f"❌ Error initializing API key encryption: {e}")
            self.fernet = None
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        if not self.fernet:
            return api_key  # Fallback to unencrypted
        
        try:
            encrypted = self.fernet.encrypt(api_key.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"❌ Error encrypting API key: {e}")
            return api_key
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key from storage"""
        if not self.fernet:
            return encrypted_key  # Fallback to unencrypted
        
        try:
            encrypted = base64.b64decode(encrypted_key.encode())
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            print(f"❌ Error decrypting API key: {e}")
            return encrypted_key
    
    def load_keys(self):
        """Load API keys from file"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r') as f:
                    data = json.load(f)
                    
                # Decrypt all keys
                for key_id, key_data in data.get('api_keys', {}).items():
                    if 'encrypted_key' in key_data:
                        key_data['key'] = self._decrypt_key(key_data['encrypted_key'])
                        del key_data['encrypted_key']
                
                self.api_keys = data.get('api_keys', {})
                print(f"✅ Loaded {len(self.api_keys)} API keys")
            else:
                print("📝 No existing API keys file found")
                
        except Exception as e:
            print(f"❌ Error loading API keys: {e}")
            self.api_keys = {}
    
    def save_keys(self):
        """Save API keys to file"""
        try:
            # Encrypt all keys for storage
            encrypted_keys = {}
            for key_id, key_data in self.api_keys.items():
                encrypted_data = key_data.copy()
                if 'key' in key_data:
                    encrypted_data['encrypted_key'] = self._encrypt_key(key_data['key'])
                    del encrypted_data['key']
                encrypted_keys[key_id] = encrypted_data
            
            data = {
                'api_keys': encrypted_keys,
                'last_updated': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            with open(self.keys_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Saved {len(self.api_keys)} API keys")
            
        except Exception as e:
            print(f"❌ Error saving API keys: {e}")
    
    def generate_api_key(self, user_id: str, key_name: str = None, 
                        permissions: List[str] = None, expires_in_days: int = None) -> Dict[str, Any]:
        """Generate new API key"""
        # Check user key limit
        user_keys = [k for k in self.api_keys.values() if k.get('user_id') == user_id]
        if len(user_keys) >= self.max_keys_per_user:
            raise ValueError(f"Maximum {self.max_keys_per_user} API keys per user")
        
        # Generate key components
        key_id = self._generate_key_id()
        raw_key = self._generate_raw_key()
        key_hash = self._hash_key(raw_key)
        
        # Set expiration
        expires_in_days = expires_in_days or self.key_expiry_days
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create key record
        key_data = {
            'key_id': key_id,
            'key': raw_key,
            'key_hash': key_hash,
            'key_name': key_name or f"API Key {len(user_keys) + 1}",
            'user_id': user_id,
            'permissions': permissions or ['read'],
            'created_at': datetime.utcnow().isoformat(),
            'last_used': None,
            'expires_at': expires_at.isoformat(),
            'status': 'active',
            'usage_count': 0,
            'rate_limit': {
                'requests_per_minute': 1000,
                'requests_per_hour': 10000,
                'requests_per_day': 100000
            }
        }
        
        # Store key
        self.api_keys[key_id] = key_data
        self.save_keys()
        
        # Return key info (without raw key for security)
        return {
            'key_id': key_id,
            'api_key': raw_key,  # Only return once during creation
            'key_name': key_data['key_name'],
            'permissions': key_data['permissions'],
            'expires_at': key_data['expires_at'],
            'created_at': key_data['created_at']
        }
    
    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        timestamp = int(time.time())
        random_part = secrets.token_hex(8)
        return f"{self.key_prefix}{timestamp}_{random_part}"
    
    def _generate_raw_key(self) -> str:
        """Generate raw API key"""
        random_part = secrets.token_urlsafe(self.default_key_length)
        return f"{self.key_prefix}{random_part}"
    
    def _hash_key(self, api_key: str) -> str:
        """Hash API key for comparison"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate API key"""
        if not api_key:
            return False, {'error': 'No API key provided'}
        
        # Hash the provided key
        key_hash = self._hash_key(api_key)
        
        # Find matching key
        for key_id, key_data in self.api_keys.items():
            if key_data.get('key_hash') == key_hash:
                # Check if key is active
                if key_data.get('status') != 'active':
                    return False, {'error': 'API key is inactive'}
                
                # Check expiration
                expires_at = datetime.fromisoformat(key_data.get('expires_at', '1970-01-01'))
                if datetime.utcnow() > expires_at:
                    return False, {'error': 'API key has expired'}
                
                # Update usage
                key_data['last_used'] = datetime.utcnow().isoformat()
                key_data['usage_count'] = key_data.get('usage_count', 0) + 1
                
                # Store in context
                g.api_key_info = key_data
                
                return True, key_data
        
        return False, {'error': 'Invalid API key'}
    
    def _validate_api_key(self):
        """Validate API key for incoming requests"""
        # Skip validation for certain endpoints
        skip_paths = ['/health', '/static', '/api/auth/login', '/api/auth/register']
        if any(request.path.startswith(path) for path in skip_paths):
            return
        
        # Get API key from various sources
        api_key = None
        
        # Check Authorization header (preferred)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
        
        # Check X-API-Key header
        if not api_key:
            api_key = request.headers.get('X-API-Key')
        
        # Check query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Validate key
        if api_key:
            is_valid, key_info = self.validate_api_key(api_key)
            
            if not is_valid:
                abort(401, description=key_info.get('error', 'Invalid API key'))
            
            # Check rate limiting
            self._check_rate_limit(key_info)
        else:
            # Check if endpoint requires API key
            if request.path.startswith('/api/') and request.path not in skip_paths:
                abort(401, description='API key required')
    
    def _check_rate_limit(self, key_info: Dict[str, Any]):
        """Check rate limiting for API key"""
        # This is a simplified rate limiting implementation
        # In production, you'd want to use Redis or another fast storage
        rate_limit = key_info.get('rate_limit', {})
        
        # For now, just log the rate limit check
        print(f"🔑 Rate limit check for key {key_info['key_id']}: {rate_limit}")
    
    def revoke_api_key(self, key_id: str, user_id: str = None) -> bool:
        """Revoke API key"""
        if key_id not in self.api_keys:
            return False
        
        key_data = self.api_keys[key_id]
        
        # Check user ownership (if user_id provided)
        if user_id and key_data.get('user_id') != user_id:
            return False
        
        # Revoke key
        key_data['status'] = 'revoked'
        key_data['revoked_at'] = datetime.utcnow().isoformat()
        
        self.save_keys()
        return True
    
    def regenerate_api_key(self, key_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Regenerate API key"""
        if key_id not in self.api_keys:
            return None
        
        key_data = self.api_keys[key_id]
        
        # Check user ownership (if user_id provided)
        if user_id and key_data.get('user_id') != user_id:
            return None
        
        # Generate new key
        new_raw_key = self._generate_raw_key()
        new_key_hash = self._hash_key(new_raw_key)
        
        # Update key
        key_data['key'] = new_raw_key
        key_data['key_hash'] = new_key_hash
        key_data['regenerated_at'] = datetime.utcnow().isoformat()
        
        self.save_keys()
        
        return {
            'key_id': key_id,
            'api_key': new_raw_key,  # Only return once during regeneration
            'regenerated_at': key_data['regenerated_at']
        }
    
    def get_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        user_keys = []
        
        for key_id, key_data in self.api_keys.items():
            if key_data.get('user_id') == user_id:
                # Return key info without the actual key
                key_info = {
                    'key_id': key_id,
                    'key_name': key_data.get('key_name'),
                    'permissions': key_data.get('permissions'),
                    'created_at': key_data.get('created_at'),
                    'last_used': key_data.get('last_used'),
                    'expires_at': key_data.get('expires_at'),
                    'status': key_data.get('status'),
                    'usage_count': key_data.get('usage_count', 0)
                }
                user_keys.append(key_info)
        
        return user_keys
    
    def get_key_info(self, key_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed information about an API key"""
        if key_id not in self.api_keys:
            return None
        
        key_data = self.api_keys[key_id]
        
        # Check user ownership (if user_id provided)
        if user_id and key_data.get('user_id') != user_id:
            return None
        
        # Return key info without the actual key
        key_info = {
            'key_id': key_id,
            'key_name': key_data.get('key_name'),
            'user_id': key_data.get('user_id'),
            'permissions': key_data.get('permissions'),
            'created_at': key_data.get('created_at'),
            'last_used': key_data.get('last_used'),
            'expires_at': key_data.get('expires_at'),
            'status': key_data.get('status'),
            'usage_count': key_data.get('usage_count', 0),
            'rate_limit': key_data.get('rate_limit', {})
        }
        
        if 'revoked_at' in key_data:
            key_info['revoked_at'] = key_data['revoked_at']
        
        if 'regenerated_at' in key_data:
            key_info['regenerated_at'] = key_data['regenerated_at']
        
        return key_info
    
    def cleanup_expired_keys(self):
        """Clean up expired API keys"""
        now = datetime.utcnow()
        expired_keys = []
        
        for key_id, key_data in self.api_keys.items():
            expires_at = datetime.fromisoformat(key_data.get('expires_at', '1970-01-01'))
            if now > expires_at:
                expired_keys.append(key_id)
        
        # Remove expired keys
        for key_id in expired_keys:
            del self.api_keys[key_id]
            print(f"🗑️ Removed expired API key: {key_id}")
        
        if expired_keys:
            self.save_keys()
        
        return len(expired_keys)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API key usage statistics"""
        total_keys = len(self.api_keys)
        active_keys = len([k for k in self.api_keys.values() if k.get('status') == 'active'])
        revoked_keys = len([k for k in self.api_keys.values() if k.get('status') == 'revoked'])
        
        total_usage = sum(k.get('usage_count', 0) for k in self.api_keys.values())
        
        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'revoked_keys': revoked_keys,
            'total_usage': total_usage,
            'average_usage': total_usage / total_keys if total_keys > 0 else 0
        }

# Decorator for API key authentication
def api_key_required(permissions: List[str] = None):
    """Decorator to require API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if API key info is available
            if not hasattr(g, 'api_key_info'):
                abort(401, description='API key required')
            
            key_info = g.api_key_info
            
            # Check permissions
            if permissions:
                key_permissions = key_info.get('permissions', [])
                if not any(perm in key_permissions for perm in permissions):
                    abort(403, description='Insufficient permissions')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask extension factory
def create_api_key_manager(app=None) -> APIKeyManager:
    """Factory function to create API key manager"""
    return APIKeyManager(app)

# Example usage
if __name__ == "__main__":
    # Test API key management
    app = Flask(__name__)
    
    # Initialize API key manager
    api_manager = create_api_key_manager(app)
    
    @app.route('/api/keys', methods=['POST'])
    def create_key():
        user_id = request.form.get('user_id')
        key_name = request.form.get('key_name')
        permissions = request.form.getlist('permissions')
        
        if user_id:
            try:
                key_info = api_manager.generate_api_key(user_id, key_name, permissions)
                from flask import jsonify
                return jsonify(key_info)
            except ValueError as e:
                abort(400, description=str(e))
        
        abort(400, description='user_id required')
    
    @app.route('/api/protected')
    @api_key_required(['read'])
    def protected():
        from flask import jsonify
        return jsonify({
            'message': 'Protected endpoint accessed',
            'key_info': g.api_key_info
        })
    
    @app.route('/api/admin')
    @api_key_required(['admin'])
    def admin():
        from flask import jsonify
        return jsonify({'message': 'Admin endpoint accessed'})
    
    @app.route('/api/stats')
    def stats():
        stats = api_manager.get_usage_stats()
        from flask import jsonify
        return jsonify(stats)
    
    app.run(debug=True)
