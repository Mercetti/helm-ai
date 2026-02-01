#!/usr/bin/env python3
"""
Comprehensive Input Validation System
Advanced input validation and sanitization for Stella Logic AI
"""

import re
import html
import json
import urllib.parse
from typing import Dict, List, Any, Optional, Union, Callable
from flask import Flask, request, abort, current_app, g
from functools import wraps
import bleach
from datetime import datetime
import os

class InputValidator:
    """Comprehensive input validation system"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.validation_rules = self._load_validation_rules()
        self.sanitization_rules = self._load_sanitization_rules()
        self.security_patterns = self._load_security_patterns()
        
        if app:
            self.init_app(app)
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules"""
        return {
            'username': {
                'required': True,
                'min_length': 3,
                'max_length': 50,
                'pattern': r'^[a-zA-Z0-9_-]+$',
                'forbidden_patterns': [r'admin', r'root', r'system', r'null'],
                'error_message': 'Username must be 3-50 characters, alphanumeric, underscore, or hyphen'
            },
            'email': {
                'required': True,
                'min_length': 5,
                'max_length': 254,
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'error_message': 'Valid email address required'
            },
            'password': {
                'required': True,
                'min_length': 12,
                'max_length': 128,
                'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]).+$',
                'error_message': 'Password must be 12+ characters with uppercase, lowercase, digit, and special character'
            },
            'name': {
                'required': True,
                'min_length': 1,
                'max_length': 100,
                'pattern': r'^[a-zA-Z\s\'-]+$',
                'error_message': 'Name must contain only letters, spaces, apostrophes, and hyphens'
            },
            'phone': {
                'required': False,
                'pattern': r'^\+?[\d\s\-\(\)]{10,20}$',
                'error_message': 'Valid phone number required'
            },
            'url': {
                'required': False,
                'pattern': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
                'error_message': 'Valid URL required'
            },
            'id': {
                'required': True,
                'pattern': r'^[a-zA-Z0-9_-]+$',
                'error_message': 'ID must be alphanumeric with underscores and hyphens'
            },
            'text': {
                'required': False,
                'max_length': 10000,
                'error_message': 'Text too long (max 10,000 characters)'
            },
            'number': {
                'required': False,
                'pattern': r'^-?\d+(\.\d+)?$',
                'error_message': 'Valid number required'
            },
            'integer': {
                'required': False,
                'pattern': r'^-?\d+$',
                'error_message': 'Valid integer required'
            },
            'boolean': {
                'required': False,
                'pattern': r'^(true|false|1|0|yes|no)$',
                'error_message': 'Valid boolean value required'
            },
            'date': {
                'required': False,
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'error_message': 'Date must be in YYYY-MM-DD format'
            },
            'datetime': {
                'required': False,
                'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',
                'error_message': 'DateTime must be in YYYY-MM-DDTHH:MM:SS format'
            },
            'json': {
                'required': False,
                'error_message': 'Valid JSON required'
            },
            'api_key': {
                'required': False,
                'pattern': r'^[a-zA-Z0-9_-]{20,64}$',
                'error_message': 'API key must be 20-64 alphanumeric characters'
            },
            'filename': {
                'required': False,
                'pattern': r'^[a-zA-Z0-9._-]+$',
                'forbidden_patterns': [r'\.\.', r'\/', r'\\', r'[<>:"|?*]'],
                'error_message': 'Valid filename required'
            }
        }
    
    def _load_sanitization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load sanitization rules"""
        return {
            'text': {
                'strip_html': True,
                'escape_html': True,
                'normalize_whitespace': True,
                'max_length': 10000
            },
            'html': {
                'allowed_tags': ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'img'],
                'allowed_attributes': {
                    'a': ['href', 'title'],
                    'img': ['src', 'alt', 'title', 'width', 'height']
                },
                'strip_comments': True
            },
            'url': {
                'encode_special_chars': True,
                'validate_scheme': True,
                'allowed_schemes': ['http', 'https']
            },
            'filename': {
                'remove_special_chars': True,
                'replace_spaces': True,
                'max_length': 255
            },
            'json': {
                'validate_structure': True,
                'remove_null_values': False,
                'max_depth': 10
            }
        }
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns to detect"""
        return {
            'sql_injection': [
                r'(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+',
                r'(--|#|\/\*|\*\/)',
                r'(\'|\'\'|")',
                r'(or|and)\s+\d+\s*=\s*\d+',
                r'(or|and)\s+\'[^\']*\'\s*=\s*\'[^\']*\'',
                r'(sleep|benchmark|waitfor\s+delay)',
                r'(xp_cmdshell|sp_executesql|sp_oacreate)',
                r'(\.\.\/|\.\.\\)',
                r'(load_file|into\s+outfile|into\s+dumpfile)'
            ],
            'xss': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'<link[^>]*>',
                r'<meta[^>]*>',
                r'expression\s*\(',
                r'@import',
                r'vbscript:',
                r'data:text/html'
            ],
            'command_injection': [
                r'(;|&&|\|\||`|\$\(|\$\{)',
                r'(cat|ls|pwd|whoami|id|uname|ps|kill|rm|mv|cp)\s',
                r'(nc|netcat|telnet|ssh|ftp|wget|curl)\s',
                r'(/bin|/usr/bin|/usr/local/bin)',
                r'(python|perl|ruby|bash|sh|cmd|powershell)\s'
            ],
            'path_traversal': [
                r'(\.\.\/|\.\.\\)',
                r'(%2e%2e%2f|%2e%2e%5c)',
                r'(/etc/passwd|/etc/shadow|/etc/hosts)',
                r'(\/proc\/|\/sys\/|\/dev\/)',
                r'(windows\/system32|c:\\windows)'
            ],
            'ldap_injection': [
                r'(\*|\(|\)|\&|\|\|=)',
                r'(cn=|ou=|dc=|uid=)',
                r'(\(\|\)|\(\!\))',
                r'(objectClass=|memberOf=)'
            ]
        }
    
    def init_app(self, app: Flask):
        """Initialize input validator"""
        self.app = app
        app.input_validator = self
        
        # Register before request handler
        app.before_request(self._validate_request)
    
    def _validate_request(self):
        """Validate incoming request data"""
        # Skip validation for static files and health checks
        if request.path.startswith('/static') or request.path.startswith('/health'):
            return
        
        # Store validation results in context
        g.validation_results = {}
        
        # Validate query parameters
        if request.args:
            for key, value in request.args.items():
                result = self.validate_input(key, value, 'query_param')
                g.validation_results[f'query_{key}'] = result
        
        # Validate form data
        if request.form:
            for key, value in request.form.items():
                result = self.validate_input(key, value, 'form')
                g.validation_results[f'form_{key}'] = result
        
        # Validate JSON data
        if request.is_json:
            json_data = request.get_json()
            if json_data:
                result = self.validate_json_data(json_data)
                g.validation_results['json'] = result
    
    def validate_input(self, field_name: str, value: Any, input_type: str = 'text', 
                      custom_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate individual input field"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_value': value,
            'security_issues': []
        }
        
        # Handle None values
        if value is None:
            if custom_rules and custom_rules.get('required', False):
                result['valid'] = False
                result['errors'].append(f'{field_name} is required')
            return result
        
        # Convert to string for validation
        if not isinstance(value, str):
            try:
                value = str(value)
            except:
                result['valid'] = False
                result['errors'].append(f'{field_name} cannot be converted to string')
                return result
        
        # Get validation rules
        rules = custom_rules or self.validation_rules.get(input_type, {})
        
        # Check required
        if rules.get('required', False) and not value.strip():
            result['valid'] = False
            result['errors'].append(f'{field_name} is required')
            return result
        
        # Skip further validation if empty and not required
        if not value.strip() and not rules.get('required', False):
            return result
        
        # Length validation
        min_length = rules.get('min_length')
        max_length = rules.get('max_length')
        
        if min_length and len(value) < min_length:
            result['valid'] = False
            result['errors'].append(f'{field_name} must be at least {min_length} characters')
        
        if max_length and len(value) > max_length:
            result['valid'] = False
            result['errors'].append(f'{field_name} must be no more than {max_length} characters')
        
        # Pattern validation
        pattern = rules.get('pattern')
        if pattern and not re.match(pattern, value, re.IGNORECASE):
            result['valid'] = False
            result['errors'].append(rules.get('error_message', f'{field_name} format is invalid'))
        
        # Forbidden patterns
        forbidden_patterns = rules.get('forbidden_patterns', [])
        for forbidden_pattern in forbidden_patterns:
            if re.search(forbidden_pattern, value, re.IGNORECASE):
                result['valid'] = False
                result['errors'].append(f'{field_name} contains forbidden content')
                break
        
        # Security checks
        security_issues = self.check_security_issues(value)
        if security_issues:
            result['security_issues'] = security_issues
            result['warnings'].extend(security_issues)
        
        # Sanitize value
        sanitized_value = self.sanitize_input(value, input_type)
        result['sanitized_value'] = sanitized_value
        
        return result
    
    def validate_json_data(self, json_data: Dict[str, Any], schema: Dict[str, str] = None) -> Dict[str, Any]:
        """Validate JSON data"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_data': {},
            'security_issues': []
        }
        
        if not isinstance(json_data, dict):
            result['valid'] = False
            result['errors'].append('JSON data must be an object')
            return result
        
        # Validate each field
        for field_name, field_value in json_data.items():
            input_type = schema.get(field_name, 'text') if schema else 'text'
            field_result = self.validate_input(field_name, field_value, input_type)
            
            if not field_result['valid']:
                result['valid'] = False
                result['errors'].extend(field_result['errors'])
            
            result['warnings'].extend(field_result['warnings'])
            result['security_issues'].extend(field_result['security_issues'])
            result['sanitized_data'][field_name] = field_result['sanitized_value']
        
        return result
    
    def check_security_issues(self, value: str) -> List[str]:
        """Check for security issues in input"""
        issues = []
        value_lower = value.lower()
        
        for issue_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    issues.append(f'Potential {issue_type.replace("_", " ")} detected')
                    break
        
        return issues
    
    def sanitize_input(self, value: str, input_type: str) -> str:
        """Sanitize input based on type"""
        if input_type == 'text':
            return self._sanitize_text(value)
        elif input_type == 'html':
            return self._sanitize_html(value)
        elif input_type == 'url':
            return self._sanitize_url(value)
        elif input_type == 'filename':
            return self._sanitize_filename(value)
        elif input_type == 'json':
            return self._sanitize_json(value)
        else:
            return self._sanitize_text(value)
    
    def _sanitize_text(self, value: str) -> str:
        """Sanitize text input"""
        rules = self.sanitization_rules.get('text', {})
        
        # Strip HTML
        if rules.get('strip_html', True):
            value = bleach.clean(value, tags=[], strip=True)
        
        # Escape HTML
        if rules.get('escape_html', True):
            value = html.escape(value)
        
        # Normalize whitespace
        if rules.get('normalize_whitespace', True):
            value = re.sub(r'\s+', ' ', value.strip())
        
        # Truncate if too long
        max_length = rules.get('max_length', 10000)
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def _sanitize_html(self, value: str) -> str:
        """Sanitize HTML input"""
        rules = self.sanitization_rules.get('html', {})
        
        # Use bleach for HTML sanitization
        allowed_tags = rules.get('allowed_tags', [])
        allowed_attributes = rules.get('allowed_attributes', {})
        strip_comments = rules.get('strip_comments', True)
        
        return bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=strip_comments
        )
    
    def _sanitize_url(self, value: str) -> str:
        """Sanitize URL input"""
        rules = self.sanitization_rules.get('url', {})
        
        # Encode special characters
        if rules.get('encode_special_chars', True):
            value = urllib.parse.quote(value, safe=':/?#[]@!$&\'()*+,;=')
        
        # Validate scheme
        if rules.get('validate_scheme', True):
            allowed_schemes = rules.get('allowed_schemes', ['http', 'https'])
            parsed = urllib.parse.urlparse(value)
            if parsed.scheme not in allowed_schemes:
                value = ''
        
        return value
    
    def _sanitize_filename(self, value: str) -> str:
        """Sanitize filename input"""
        rules = self.sanitization_rules.get('filename', {})
        
        # Remove special characters
        if rules.get('remove_special_chars', True):
            value = re.sub(r'[^\w\-_\.]', '', value)
        
        # Replace spaces
        if rules.get('replace_spaces', True):
            value = re.sub(r'\s+', '_', value)
        
        # Remove path traversal
        value = value.replace('..', '').replace('/', '').replace('\\', '')
        
        # Truncate if too long
        max_length = rules.get('max_length', 255)
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def _sanitize_json(self, value: str) -> str:
        """Sanitize JSON input"""
        rules = self.sanitization_rules.get('json', {})
        
        try:
            # Parse and re-serialize JSON
            parsed = json.loads(value)
            
            # Validate structure
            if rules.get('validate_structure', True):
                max_depth = rules.get('max_depth', 10)
                if self._get_json_depth(parsed) > max_depth:
                    raise ValueError("JSON structure too deep")
            
            # Remove null values if specified
            if rules.get('remove_null_values', False):
                parsed = self._remove_null_values(parsed)
            
            return json.dumps(parsed)
            
        except (json.JSONDecodeError, ValueError) as e:
            # Return empty JSON if invalid
            return '{}'
    
    def _get_json_depth(self, obj, current_depth=0):
        """Get depth of JSON object"""
        if current_depth > 10:
            return current_depth
        
        if isinstance(obj, dict):
            return max(self._get_json_depth(v, current_depth + 1) for v in obj.values()) if obj else current_depth
        elif isinstance(obj, list):
            return max(self._get_json_depth(item, current_depth + 1) for item in obj) if obj else current_depth
        else:
            return current_depth
    
    def _remove_null_values(self, obj):
        """Remove null values from JSON object"""
        if isinstance(obj, dict):
            return {k: self._remove_null_values(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [self._remove_null_values(item) for item in obj if item is not None]
        else:
            return obj
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary for current request"""
        if hasattr(g, 'validation_results'):
            results = g.validation_results
            
            summary = {
                'total_fields': len(results),
                'valid_fields': len([r for r in results.values() if r['valid']]),
                'invalid_fields': len([r for r in results.values() if not r['valid']]),
                'security_issues': [],
                'warnings': []
            }
            
            # Collect all security issues and warnings
            for result in results.values():
                summary['security_issues'].extend(result.get('security_issues', []))
                summary['warnings'].extend(result.get('warnings', []))
            
            return summary
        
        return {'total_fields': 0, 'valid_fields': 0, 'invalid_fields': 0}

# Decorator for input validation
def validate_input_fields(schema: Dict[str, str], source: str = 'form'):
    """Decorator to validate input fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            validator = current_app.input_validator if hasattr(current_app, 'input_validator') else None
            
            if validator:
                if source == 'form' and request.form:
                    data = request.form
                elif source == 'json' and request.is_json:
                    data = request.get_json()
                elif source == 'args' and request.args:
                    data = request.args
                else:
                    data = {}
                
                # Validate data against schema
                validation_result = validator.validate_json_data(data, schema)
                
                if not validation_result['valid']:
                    abort(400, description={
                        'error': 'Validation failed',
                        'errors': validation_result['errors'],
                        'warnings': validation_result['warnings']
                    })
                
                # Store sanitized data
                g.validated_data = validation_result['sanitized_data']
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask extension factory
def create_input_validator(app=None) -> InputValidator:
    """Factory function to create input validator"""
    return InputValidator(app)

# Example usage
if __name__ == "__main__":
    # Test input validation
    app = Flask(__name__)
    
    # Initialize input validator
    validator = create_input_validator(app)
    
    @app.route('/register', methods=['POST'])
    @validate_input_fields({
        'username': 'username',
        'email': 'email',
        'password': 'password',
        'name': 'name'
    }, source='form')
    def register():
        from flask import jsonify
        return jsonify({
            'message': 'Registration successful',
            'data': g.validated_data
        })
    
    @app.route('/validation-status')
    def validation_status():
        summary = validator.get_validation_summary()
        from flask import jsonify
        return jsonify(summary)
    
    app.run(debug=True)
