#!/usr/bin/env python3
"""
JWT Secret Rotation System
Automatic JWT secret rotation for enhanced security in Stella Logic AI
"""

import os
import json
import time
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from flask import Flask, request, current_app, g
from functools import wraps
import hashlib
import hmac

class JWTSecretRotation:
    """JWT secret rotation system for enhanced security"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.secrets_file = 'jwt_secrets.json'
        self.current_secret_id = None
        self.secrets = {}
        self.rotation_interval = 30  # days
        self.grace_period = 7  # days
        self.max_secrets = 5  # maximum number of secrets to keep
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize JWT secret rotation"""
        self.app = app
        app.jwt_rotation = self
        
        # Load existing secrets
        self.load_secrets()
        
        # Check if rotation is needed
        self.check_rotation_needed()
        
        # Store JWT configuration
        app.config.setdefault('JWT_SECRET_KEY', self.get_current_secret())
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    
    def load_secrets(self):
        """Load JWT secrets from file"""
        try:
            if os.path.exists(self.secrets_file):
                with open(self.secrets_file, 'r') as f:
                    data = json.load(f)
                    self.secrets = data.get('secrets', {})
                    self.current_secret_id = data.get('current_secret_id')
                    self.rotation_interval = data.get('rotation_interval', 30)
                    self.grace_period = data.get('grace_period', 7)
                    print(f"✅ Loaded {len(self.secrets)} JWT secrets")
            else:
                # Initialize with first secret
                self.create_initial_secret()
        except Exception as e:
            print(f"❌ Error loading JWT secrets: {e}")
            self.create_initial_secret()
    
    def create_initial_secret(self):
        """Create initial JWT secret"""
        print("🔐 Creating initial JWT secret for Stella Logic AI")
        
        secret_id = self.generate_secret_id()
        secret_value = self.generate_secret_value()
        
        self.secrets = {
            secret_id: {
                'secret': secret_value,
                'created_at': datetime.utcnow().isoformat(),
                'last_used': datetime.utcnow().isoformat(),
                'status': 'active'
            }
        }
        
        self.current_secret_id = secret_id
        self.save_secrets()
    
    def generate_secret_id(self) -> str:
        """Generate unique secret ID"""
        timestamp = int(time.time())
        random_part = secrets.token_hex(8)
        return f"stella_jwt_{timestamp}_{random_part}"
    
    def generate_secret_value(self) -> str:
        """Generate secure secret value"""
        return secrets.token_urlsafe(64)  # 64 bytes of random data
    
    def save_secrets(self):
        """Save secrets to file"""
        try:
            data = {
                'secrets': self.secrets,
                'current_secret_id': self.current_secret_id,
                'rotation_interval': self.rotation_interval,
                'grace_period': self.grace_period,
                'last_rotation': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            with open(self.secrets_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Saved JWT secrets to {self.secrets_file}")
            
        except Exception as e:
            print(f"❌ Error saving JWT secrets: {e}")
    
    def check_rotation_needed(self):
        """Check if JWT secret rotation is needed"""
        if not self.current_secret_id:
            return
        
        current_secret = self.secrets.get(self.current_secret_id)
        if not current_secret:
            return
        
        created_at = datetime.fromisoformat(current_secret['created_at'])
        rotation_date = created_at + timedelta(days=self.rotation_interval)
        
        if datetime.utcnow() >= rotation_date:
            print("🔄 JWT secret rotation needed for Stella Logic AI")
            self.rotate_secret()
    
    def rotate_secret(self):
        """Rotate JWT secret"""
        print("🔄 Rotating JWT secret for Stella Logic AI")
        
        # Create new secret
        new_secret_id = self.generate_secret_id()
        new_secret_value = self.generate_secret_value()
        
        # Mark old secret as deprecated (but keep for grace period)
        if self.current_secret_id:
            old_secret = self.secrets.get(self.current_secret_id)
            if old_secret:
                old_secret['status'] = 'deprecated'
                old_secret['deprecated_at'] = datetime.utcnow().isoformat()
        
        # Add new secret
        self.secrets[new_secret_id] = {
            'secret': new_secret_value,
            'created_at': datetime.utcnow().isoformat(),
            'last_used': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        self.current_secret_id = new_secret_id
        
        # Clean up old secrets
        self.cleanup_old_secrets()
        
        # Save to file
        self.save_secrets()
        
        # Update Flask config
        if self.app:
            self.app.config['JWT_SECRET_KEY'] = new_secret_value
        
        print(f"✅ JWT secret rotated successfully: {new_secret_id}")
    
    def cleanup_old_secrets(self):
        """Clean up old secrets beyond grace period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.grace_period)
        
        secrets_to_remove = []
        for secret_id, secret_data in self.secrets.items():
            if secret_data['status'] == 'deprecated':
                deprecated_at = datetime.fromisoformat(secret_data.get('deprecated_at', '1970-01-01'))
                if deprecated_at < cutoff_date:
                    secrets_to_remove.append(secret_id)
        
        # Remove old secrets
        for secret_id in secrets_to_remove:
            del self.secrets[secret_id]
            print(f"🗑️ Removed old JWT secret: {secret_id}")
        
        # Ensure we don't exceed max secrets
        if len(self.secrets) > self.max_secrets:
            # Sort by creation date and remove oldest
            sorted_secrets = sorted(
                self.secrets.items(),
                key=lambda x: x[1]['created_at']
            )
            
            excess_count = len(self.secrets) - self.max_secrets
            for i in range(excess_count):
                secret_id = sorted_secrets[i][0]
                if secret_id != self.current_secret_id:
                    del self.secrets[secret_id]
                    print(f"🗑️ Removed excess JWT secret: {secret_id}")
    
    def get_current_secret(self) -> str:
        """Get current JWT secret"""
        if self.current_secret_id and self.current_secret_id in self.secrets:
            return self.secrets[self.current_secret_id]['secret']
        return None
    
    def get_all_secrets(self) -> List[str]:
        """Get all active and deprecated secrets (for token validation)"""
        secrets = []
        for secret_data in self.secrets.values():
            if secret_data['status'] in ['active', 'deprecated']:
                secrets.append(secret_data['secret'])
        return secrets
    
    def validate_token(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate JWT token with multiple secrets"""
        secrets = self.get_all_secrets()
        
        for secret in secrets:
            try:
                decoded = jwt.decode(
                    token,
                    secret,
                    algorithms=[self.app.config.get('JWT_ALGORITHM', 'HS256')]
                )
                
                # Update last used time for the secret
                for secret_id, secret_data in self.secrets.items():
                    if secret_data['secret'] == secret:
                        secret_data['last_used'] = datetime.utcnow().isoformat()
                        break
                
                return True, decoded
                
            except jwt.ExpiredSignatureError:
                return False, {'error': 'Token expired'}
            except jwt.InvalidTokenError:
                continue
        
        return False, {'error': 'Invalid token'}
    
    def create_token(self, payload: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Create JWT token with current secret"""
        current_secret = self.get_current_secret()
        if not current_secret:
            raise ValueError("No current JWT secret available")
        
        # Add standard claims
        now = datetime.utcnow()
        payload.update({
            'iat': now,
            'jti': secrets.token_urlsafe(32),
            'iss': 'stella-logic-ai',
            'aud': 'stella-logic-ai-users'
        })
        
        # Set expiration
        if expires_delta:
            payload['exp'] = now + expires_delta
        else:
            payload['exp'] = now + self.app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
        # Create token
        token = jwt.encode(
            payload,
            current_secret,
            algorithm=self.app.config.get('JWT_ALGORITHM', 'HS256')
        )
        
        return token
    
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        is_valid, decoded = self.validate_token(refresh_token)
        
        if not is_valid or decoded.get('type') != 'refresh':
            return None
        
        # Create new access token
        access_payload = {
            'user_id': decoded.get('user_id'),
            'username': decoded.get('username'),
            'role': decoded.get('role'),
            'type': 'access'
        }
        
        return self.create_token(access_payload)
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """Get rotation status"""
        current_secret = self.secrets.get(self.current_secret_id, {})
        created_at = datetime.fromisoformat(current_secret.get('created_at', '1970-01-01'))
        rotation_date = created_at + timedelta(days=self.rotation_interval)
        days_until_rotation = (rotation_date - datetime.utcnow()).days
        
        return {
            'current_secret_id': self.current_secret_id,
            'total_secrets': len(self.secrets),
            'active_secrets': len([s for s in self.secrets.values() if s['status'] == 'active']),
            'deprecated_secrets': len([s for s in self.secrets.values() if s['status'] == 'deprecated']),
            'rotation_interval_days': self.rotation_interval,
            'grace_period_days': self.grace_period,
            'days_until_rotation': max(0, days_until_rotation),
            'last_rotation': current_secret.get('created_at'),
            'next_rotation': rotation_date.isoformat()
        }

# Decorator for JWT authentication
def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Get token from cookie
        if not token:
            token = request.cookies.get('access_token')
        
        if not token:
            abort(401, description='No token provided')
        
        # Validate token
        jwt_rotation = current_app.jwt_rotation if hasattr(current_app, 'jwt_rotation') else None
        if jwt_rotation:
            is_valid, decoded = jwt_rotation.validate_token(token)
            
            if not is_valid:
                abort(401, description=decoded.get('error', 'Invalid token'))
            
            # Store decoded token in context
            g.current_user = decoded
        else:
            abort(500, description='JWT rotation not configured')
        
        return f(*args, **kwargs)
    return decorated_function

# Flask extension factory
def create_jwt_rotation(app=None) -> JWTSecretRotation:
    """Factory function to create JWT rotation system"""
    return JWTSecretRotation(app)

# Example usage
if __name__ == "__main__":
    # Test JWT secret rotation
    app = Flask(__name__)
    app.secret_key = 'stella-logic-ai-secret-key'
    
    # Initialize JWT rotation
    jwt_rotation = create_jwt_rotation(app)
    
    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate user (simplified)
        if username and password:
            # Create access token
            access_payload = {
                'user_id': 1,
                'username': username,
                'role': 'user',
                'type': 'access'
            }
            access_token = jwt_rotation.create_token(access_payload)
            
            # Create refresh token
            refresh_payload = {
                'user_id': 1,
                'username': username,
                'role': 'user',
                'type': 'refresh'
            }
            refresh_token = jwt_rotation.create_token(
                refresh_payload, 
                timedelta(days=30)
            )
            
            from flask import jsonify
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer'
            })
        
        abort(401, description='Invalid credentials')
    
    @app.route('/protected')
    @jwt_required
    def protected():
        from flask import jsonify
        return jsonify({
            'message': 'Protected endpoint accessed',
            'user': g.current_user
        })
    
    @app.route('/refresh', methods=['POST'])
    def refresh():
        refresh_token = request.form.get('refresh_token')
        
        if refresh_token:
            new_token = jwt_rotation.refresh_token(refresh_token)
            
            if new_token:
                from flask import jsonify
                return jsonify({'access_token': new_token})
        
        abort(401, description='Invalid refresh token')
    
    @app.route('/jwt-status')
    def jwt_status():
        status = jwt_rotation.get_rotation_status()
        from flask import jsonify
        return jsonify(status)
    
    app.run(debug=True)
