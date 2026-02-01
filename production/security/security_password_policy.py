#!/usr/bin/env python3
"""
Password Policy and Validation System
Comprehensive password security with strong requirements, validation, and hashing
"""

import re
import secrets
import string
import hashlib
import hmac
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from flask import abort, current_app
import json
import os

class PasswordPolicy:
    """Comprehensive password policy and validation system"""
    
    def __init__(self, app=None):
        self.app = app
        
        # Password policy configuration
        self.policy = {
            'min_length': 12,
            'max_length': 128,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'require_special': True,
            'require_no_common_passwords': True,
            'require_no_repeated_chars': True,
            'require_no_username_inclusion': True,
            'require_no_email_inclusion': True,
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'forbidden_patterns': [
                r'(.)\1{2,}',  # Repeated characters (aa, 111, etc.)
                r'(123|234|345|456|567|678|789|890|012)',  # Sequential numbers
                r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
                r'(qwer|asdf|zxcv|qwerty|password|admin|root|user|test|guest)',  # Common patterns
            ],
            'common_passwords': self._load_common_passwords(),
            'hash_algorithm': 'bcrypt',
            'bcrypt_rounds': 12,
            'password_history': 5,  # Number of previous passwords to remember
            'max_age_days': 90,  # Force password change every 90 days
            'failed_attempts_lockout': 5,
            'failed_attempts_window': 300,  # 5 minutes
            'lockout_duration': 900,  # 15 minutes
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize password policy"""
        self.app = app
        app.config.setdefault('PASSWORD_POLICY', self.policy)
        app.password_policy = self
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        # Common weak passwords
        common_passwords = {
            'password', '123456', 'password123', 'admin', 'root', 'user', 'test', 'guest',
            'qwerty', 'abc123', 'password1', 'iloveyou', 'monkey', 'dragon', 'football',
            'baseball', 'letmein', '1234567890', '12345678', 'welcome', 'login',
            'princess', '1234567', '12345678', 'sunshine', 'master', 'shadow',
            'superman', 'azerty', 'trustno1', 'whatever', 'qazwsx', 'michael',
            'football123', '123123', 'password12', '1234', '12345', 'pass',
            '123456789', 'password!', '12345', '1234567890', 'password123',
            'admin123', 'root123', 'user123', 'test123', 'guest123',
            'qwerty123', 'abc123456', 'password1!', 'admin1234', 'root1234',
            'user1234', 'test1234', 'guest1234', 'qwertyuiop', 'asdfghjkl',
            'zxcvbnm', 'qwertyui', 'asdfghjk', 'zxcvbnm1', 'password2',
            'admin12', 'root12', 'user12', 'test12', 'guest12',
            'changeme', 'default', 'password1234', 'admin12345',
            'root12345', 'user12345', 'test12345', 'guest12345'
        }
        
        return common_passwords
    
    def validate_password(self, password: str, username: str = None, email: str = None) -> Dict[str, Any]:
        """Validate password against policy"""
        errors = []
        warnings = []
        
        # Length validation
        if len(password) < self.policy['min_length']:
            errors.append(f"Password must be at least {self.policy['min_length']} characters long")
        
        if len(password) > self.policy['max_length']:
            errors.append(f"Password must be no more than {self.policy['max_length']} characters long")
        
        # Character requirements
        if self.policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.policy['require_lowercase'] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.policy['require_digits'] and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.policy['require_special'] and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            errors.append(f"Password must contain at least one special character: {self.policy['special_chars']}")
        
        # Forbidden patterns
        if self.policy['require_no_repeated_chars']:
            for pattern in self.policy['forbidden_patterns']:
                if re.search(pattern, password, re.IGNORECASE):
                    errors.append("Password contains repeated or sequential characters")
                    break
        
        # Common passwords check
        if self.policy['require_no_common_passwords']:
            password_lower = password.lower()
            if password_lower in self.policy['common_passwords']:
                errors.append("Password is too common and easily guessable")
            
            # Check if password is similar to common passwords
            for common_pwd in self.policy['common_passwords']:
                if self._password_similarity(password_lower, common_pwd) > 0.8:
                    errors.append("Password is too similar to common passwords")
                    break
        
        # Username inclusion check
        if username and self.policy['require_no_username_inclusion']:
            if username.lower() in password.lower():
                errors.append("Password cannot contain your username")
        
        # Email inclusion check
        if email and self.policy['require_no_email_inclusion']:
            email_parts = email.lower().split('@')
            if email_parts[0] and email_parts[0] in password.lower():
                errors.append("Password cannot contain your email username")
        
        # Calculate password strength
        strength = self._calculate_password_strength(password)
        
        # Warnings for weak passwords
        if strength < 60:
            warnings.append("Password strength is weak - consider using a stronger password")
        elif strength < 80:
            warnings.append("Password strength could be improved")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'strength': strength,
            'strength_text': self._get_strength_text(strength)
        }
    
    def _password_similarity(self, pwd1: str, pwd2: str) -> float:
        """Calculate similarity between two passwords"""
        if pwd1 == pwd2:
            return 1.0
        
        # Levenshtein distance approximation
        longer = max(len(pwd1), len(pwd2))
        shorter = min(len(pwd1), len(pwd2))
        
        if longer == 0:
            return 1.0
        
        # Simple similarity calculation
        common_chars = sum(1 for c in shorter if c in pwd1)
        return common_chars / longer
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length score (0-30)
        length_score = min(30, len(password) * 2)
        score += length_score
        
        # Character variety score (0-40)
        if re.search(r'[a-z]', password):
            score += 8
        if re.search(r'[A-Z]', password):
            score += 8
        if re.search(r'\d', password):
            score += 8
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 8
        if re.search(r'[^\w\s]', password):  # Non-alphanumeric
            score += 8
        
        # Complexity score (0-30)
        if len(password) >= 16:
            score += 10
        if len(password) >= 20:
            score += 10
        if not re.search(r'(.)\1{2,}', password):  # No repeated chars
            score += 5
        if not re.search(r'(123|234|345|456|567|678|789|890|012)', password):  # No sequential numbers
            score += 5
        
        return min(100, score)
    
    def _get_strength_text(self, strength: int) -> str:
        """Get strength description"""
        if strength >= 90:
            return "Very Strong"
        elif strength >= 80:
            return "Strong"
        elif strength >= 70:
            return "Good"
        elif strength >= 60:
            return "Fair"
        elif strength >= 40:
            return "Weak"
        else:
            return "Very Weak"
    
    def generate_password(self, length: int = None, include_special: bool = True) -> str:
        """Generate a secure random password"""
        if length is None:
            length = max(self.policy['min_length'], 16)
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = self.policy['special_chars']
        
        # Ensure all required character types
        all_chars = lowercase + uppercase + digits
        if include_special:
            all_chars += special
        
        # Generate password
        password = ''.join(secrets.choice(all_chars) for _ in range(length))
        
        # Ensure it meets requirements
        if self.policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            password = password[:-1] + secrets.choice(uppercase)
        
        if self.policy['require_lowercase'] and not re.search(r'[a-z]', password):
            password = password[:-1] + secrets.choice(lowercase)
        
        if self.policy['require_digits'] and not re.search(r'\d', password):
            password = password[:-1] + secrets.choice(digits)
        
        if include_special and self.policy['require_special'] and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            password = password[:-1] + secrets.choice(special)
        
        return password
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        if self.policy['hash_algorithm'] == 'bcrypt':
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=self.policy['bcrypt_rounds'])
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        else:
            # Fallback to SHA-256 (not recommended for production)
            salt = secrets.token_hex(32)
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return f"{salt}${hashed}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            if self.policy['hash_algorithm'] == 'bcrypt':
                return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            else:
                # SHA-256 fallback
                salt, hash_value = hashed_password.split('$')
                computed_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt.encode('utf-8'),
                    100000
                ).hex()
                return hmac.compare_digest(computed_hash.encode(), hash_value.encode())
        except Exception:
            return False
    
    def check_password_history(self, user_id: str, new_password: str, password_history: List[str]) -> bool:
        """Check if password has been used before"""
        for old_password in password_history:
            if self.verify_password(new_password, old_password):
                return False
        return True
    
    def check_password_age(self, last_changed: datetime) -> Dict[str, Any]:
        """Check if password needs to be changed"""
        days_old = (datetime.now() - last_changed).days
        needs_change = days_old >= self.policy['max_age_days']
        
        return {
            'needs_change': needs_change,
            'days_old': days_old,
            'max_age_days': self.policy['max_age_days'],
            'days_until_change': max(0, self.policy['max_age_days'] - days_old)
        }
    
    def get_password_requirements(self) -> Dict[str, Any]:
        """Get password requirements for UI display"""
        return {
            'min_length': self.policy['min_length'],
            'max_length': self.policy['max_length'],
            'require_uppercase': self.policy['require_uppercase'],
            'require_lowercase': self.policy['require_lowercase'],
            'require_digits': self.policy['require_digits'],
            'require_special': self.policy['require_special'],
            'special_chars': self.policy['special_chars'],
            'no_common_passwords': self.policy['require_no_common_passwords'],
            'no_repeated_chars': self.policy['require_no_repeated_chars'],
            'no_username_inclusion': self.policy['require_no_username_inclusion'],
            'no_email_inclusion': self.policy['require_no_email_inclusion']
        }

# Flask extension factory
def create_password_policy(app=None) -> PasswordPolicy:
    """Factory function to create password policy"""
    return PasswordPolicy(app)

# Decorator for password validation
def validate_password(username_field='username', email_field='email'):
    """Decorator to validate password in forms"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            password = request.form.get('password')
            username = request.form.get(username_field)
            email = request.form.get(email_field)
            
            if password:
                password_policy = current_app.password_policy if hasattr(current_app, 'password_policy') else PasswordPolicy()
                validation = password_policy.validate_password(password, username, email)
                
                if not validation['valid']:
                    abort(400, description={
                        'error': 'Password validation failed',
                        'errors': validation['errors'],
                        'warnings': validation['warnings'],
                        'strength': validation['strength']
                    })
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example usage
if __name__ == "__main__":
    # Test password policy
    policy = PasswordPolicy()
    
    # Test password validation
    test_passwords = [
        "weak123",
        "StrongP@ssw0rd!",
        "VerySecurePassword123!@#",
        "user123"
    ]
    
    print("Password Policy Test:")
    print("=" * 50)
    
    for pwd in test_passwords:
        result = policy.validate_password(pwd, "testuser", "test@example.com")
        status = "✅ Valid" if result['valid'] else "❌ Invalid"
        print(f"{status} '{pwd}'")
        print(f"   Strength: {result['strength_text']} ({result['strength']}/100)")
        if result['errors']:
            for error in result['errors']:
                print(f"   Error: {error}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   Warning: {warning}")
        print()
    
    # Test password generation
    print("Generated Passwords:")
    print("=" * 50)
    
    for i in range(3):
        generated = policy.generate_password()
        validation = policy.validate_password(generated)
        print(f"Generated: {generated}")
        print(f"   Strength: {validation['strength_text']} ({validation['strength']}/100)")
        print()
