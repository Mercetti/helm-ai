"""
Helm AI Input Validation
This module provides comprehensive input validation and sanitization
"""

import os
import json
import logging
import re
import html
from typing import Dict, List, Optional, Any, Union, Callable, Type
from datetime import datetime, date
from enum import Enum
from dataclasses import dataclass, field
import email.utils
import ipaddress
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationType(Enum):
    """Validation types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    PASSWORD = "password"
    API_KEY = "api_key"

class ValidationRule:
    """Base validation rule"""
    
    def __init__(self, required: bool = True, nullable: bool = False):
        self.required = required
        self.nullable = nullable
    
    def validate(self, value: Any, field_name: str = None) -> Any:
        """Validate input value"""
        if value is None:
            if self.required and not self.nullable:
                raise ValueError(f"{field_name or 'Field'} is required")
            return value
        
        return self._validate_value(value, field_name)
    
    def _validate_value(self, value: Any, field_name: str = None) -> Any:
        """Override in subclasses"""
        return value

class StringRule(ValidationRule):
    """String validation rule"""
    
    def __init__(self, 
                 min_length: int = None,
                 max_length: int = None,
                 pattern: str = None,
                 allow_empty: bool = False,
                 sanitize_html: bool = False,
                 trim: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allow_empty = allow_empty
        self.sanitize_html = sanitize_html
        self.trim = trim
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            try:
                value = str(value)
            except (ValueError, TypeError):
                raise ValueError(f"{field_name or 'Field'} must be a string")
        
        # Trim whitespace
        if self.trim:
            value = value.strip()
        
        # Check empty string
        if not value and not self.allow_empty and self.required:
            raise ValueError(f"{field_name or 'Field'} cannot be empty")
        
        # Length validation
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(f"{field_name or 'Field'} must be at least {self.min_length} characters")
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(f"{field_name or 'Field'} cannot exceed {self.max_length} characters")
        
        # Pattern validation
        if self.pattern and not re.match(self.pattern, value):
            raise ValueError(f"{field_name or 'Field'} does not match required pattern")
        
        # HTML sanitization
        if self.sanitize_html:
            value = html.escape(value)
        
        return value

class NumberRule(ValidationRule):
    """Number validation rule"""
    
    def __init__(self, 
                 min_value: Union[int, float] = None,
                 max_value: Union[int, float] = None,
                 allow_zero: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.allow_zero = allow_zero
    
    def _validate_value(self, value: Any, field_name: str = None) -> Union[int, float]:
        if isinstance(value, str):
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                raise ValueError(f"{field_name or 'Field'} must be a valid number")
        
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name or 'Field'} must be a number")
        
        if not self.allow_zero and value == 0:
            raise ValueError(f"{field_name or 'Field'} cannot be zero")
        
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{field_name or 'Field'} must be at least {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{field_name or 'Field'} cannot exceed {self.max_value}")
        
        return value

class EmailRule(ValidationRule):
    """Email validation rule"""
    
    def __init__(self, allow_display_name: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.allow_display_name = allow_display_name
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name or 'Field'} must be a string")
        
        value = value.strip()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError(f"{field_name or 'Field'} must be a valid email address")
        
        # Additional validation using email.utils
        try:
            parsed = email.utils.parseaddr(value)
            if not parsed[1]:  # No email address found
                raise ValueError(f"{field_name or 'Field'} must be a valid email address")
        except Exception:
            raise ValueError(f"{field_name or 'Field'} must be a valid email address")
        
        return value.lower()

class URLRule(ValidationRule):
    """URL validation rule"""
    
    def __init__(self, schemes: List[str] = None, require_https: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.schemes = schemes or ['http', 'https']
        self.require_https = require_https
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name or 'Field'} must be a string")
        
        value = value.strip()
        
        try:
            parsed = urlparse(value)
            
            if not parsed.scheme:
                raise ValueError(f"{field_name or 'Field'} must include a scheme (http/https)")
            
            if parsed.scheme not in self.schemes:
                raise ValueError(f"{field_name or 'Field'} scheme must be one of: {', '.join(self.schemes)}")
            
            if self.require_https and parsed.scheme != 'https':
                raise ValueError(f"{field_name or 'Field'} must use HTTPS")
            
            if not parsed.netloc:
                raise ValueError(f"{field_name or 'Field'} must include a domain")
            
        except Exception as e:
            if "must include" in str(e):
                raise
            raise ValueError(f"{field_name or 'Field'} must be a valid URL")
        
        return value

class UUIDRule(ValidationRule):
    """UUID validation rule"""
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name or 'Field'} must be a string")
        
        value = value.strip()
        
        # UUID pattern validation
        uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        if not re.match(uuid_pattern, value):
            raise ValueError(f"{field_name or 'Field'} must be a valid UUID")
        
        return value.lower()

class DateRule(ValidationRule):
    """Date validation rule"""
    
    def __init__(self, format: str = '%Y-%m-%d', min_date: date = None, max_date: date = None, **kwargs):
        super().__init__(**kwargs)
        self.format = format
        self.min_date = min_date
        self.max_date = max_date
    
    def _validate_value(self, value: Any, field_name: str = None) -> date:
        if isinstance(value, str):
            try:
                value = datetime.strptime(value.strip(), self.format).date()
            except ValueError:
                raise ValueError(f"{field_name or 'Field'} must be a valid date in format {self.format}")
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            raise ValueError(f"{field_name or 'Field'} must be a date")
        
        if self.min_date and value < self.min_date:
            raise ValueError(f"{field_name or 'Field'} must be on or after {self.min_date}")
        
        if self.max_date and value > self.max_date:
            raise ValueError(f"{field_name or 'Field'} must be on or before {self.max_date}")
        
        return value

class DateTimeRule(ValidationRule):
    """DateTime validation rule"""
    
    def __init__(self, format: str = '%Y-%m-%dT%H:%M:%S', **kwargs):
        super().__init__(**kwargs)
        self.format = format
    
    def _validate_value(self, value: Any, field_name: str = None) -> datetime:
        if isinstance(value, str):
            try:
                value = datetime.strptime(value.strip(), self.format)
            except ValueError:
                raise ValueError(f"{field_name or 'Field'} must be a valid datetime in format {self.format}")
        elif not isinstance(value, datetime):
            raise ValueError(f"{field_name or 'Field'} must be a datetime")
        
        return value

class JSONRule(ValidationRule):
    """JSON validation rule"""
    
    def __init__(self, schema: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
    
    def _validate_value(self, value: Any, field_name: str = None) -> Dict[str, Any]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError(f"{field_name or 'Field'} must be valid JSON")
        elif not isinstance(value, dict):
            raise ValueError(f"{field_name or 'Field'} must be a JSON object")
        
        # Schema validation (basic)
        if self.schema:
            self._validate_schema(value, self.schema, field_name)
        
        return value
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any], field_name: str = None):
        """Validate data against schema"""
        for key, rule in schema.items():
            if isinstance(rule, ValidationRule):
                if key in data:
                    data[key] = rule.validate(data[key], f"{field_name}.{key}" if field_name else key)
                elif rule.required:
                    raise ValueError(f"Required field '{key}' is missing")

class PasswordRule(StringRule):
    """Password validation rule"""
    
    def __init__(self, 
                 min_length: int = 8,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special: bool = True,
                 forbidden_patterns: List[str] = None,
                 **kwargs):
        super().__init__(min_length=min_length, **kwargs)
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.forbidden_patterns = forbidden_patterns or []
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        value = super()._validate_value(value, field_name)
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            raise ValueError(f"{field_name or 'Field'} must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            raise ValueError(f"{field_name or 'Field'} must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', value):
            raise ValueError(f"{field_name or 'Field'} must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError(f"{field_name or 'Field'} must contain at least one special character")
        
        for pattern in self.forbidden_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"{field_name or 'Field'} contains forbidden pattern")
        
        return value

class APIKeyRule(StringRule):
    """API key validation rule"""
    
    def __init__(self, prefix: str = None, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix
    
    def _validate_value(self, value: Any, field_name: str = None) -> str:
        value = super()._validate_value(value, field_name)
        
        if self.prefix and not value.startswith(self.prefix):
            raise ValueError(f"{field_name or 'Field'} must start with '{self.prefix}'")
        
        # API key pattern (alphanumeric with optional underscores and hyphens)
        api_key_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(api_key_pattern, value):
            raise ValueError(f"{field_name or 'Field'} contains invalid characters")
        
        return value

class InputValidator:
    """Input validation manager"""
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.global_rules: Dict[str, ValidationRule] = {}
        
        # Initialize global rules
        self._initialize_global_rules()
    
    def _initialize_global_rules(self):
        """Initialize global validation rules"""
        self.global_rules.update({
            'email': EmailRule(),
            'url': URLRule(),
            'uuid': UUIDRule(),
            'date': DateRule(),
            'datetime': DateTimeRule(),
            'json': JSONRule(),
            'password': PasswordRule(),
            'api_key': APIKeyRule()
        })
    
    def add_rule(self, field_name: str, rule: ValidationRule):
        """Add validation rule for field"""
        self.rules[field_name] = rule
    
    def add_global_rule(self, rule_name: str, rule: ValidationRule):
        """Add global validation rule"""
        self.global_rules[rule_name] = rule
    
    def validate(self, data: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
        """Validate input data"""
        validated_data = {}
        
        # Validate field-specific rules
        for field_name, rule in self.rules.items():
            try:
                value = data.get(field_name)
                validated_value = rule.validate(value, field_name)
                validated_data[field_name] = validated_value
            except ValueError as e:
                raise ValueError(str(e))
        
        # Validate remaining fields if strict mode
        if strict:
            for field_name, value in data.items():
                if field_name not in self.rules:
                    raise ValueError(f"Unexpected field: {field_name}")
        
        return validated_data
    
    def validate_field(self, field_name: str, value: Any, rule_name: str = None) -> Any:
        """Validate single field"""
        if rule_name and rule_name in self.global_rules:
            rule = self.global_rules[rule_name]
        elif field_name in self.rules:
            rule = self.rules[field_name]
        else:
            # Default to string validation
            rule = StringRule(required=False)
        
        return rule.validate(value, field_name)
    
    def create_schema(self, schema_def: Dict[str, Any]) -> Dict[str, ValidationRule]:
        """Create validation schema from definition"""
        schema = {}
        
        for field_name, field_def in schema_def.items():
            rule_type = field_def.get('type', 'string')
            rule_kwargs = {k: v for k, v in field_def.items() if k != 'type'}
            
            if rule_type == 'string':
                rule = StringRule(**rule_kwargs)
            elif rule_type == 'integer':
                rule = NumberRule(**rule_kwargs)
            elif rule_type == 'float':
                rule = NumberRule(**rule_kwargs)
            elif rule_type == 'email':
                rule = EmailRule(**rule_kwargs)
            elif rule_type == 'url':
                rule = URLRule(**rule_kwargs)
            elif rule_type == 'uuid':
                rule = UUIDRule(**rule_kwargs)
            elif rule_type == 'date':
                rule = DateRule(**rule_kwargs)
            elif rule_type == 'datetime':
                rule = DateTimeRule(**rule_kwargs)
            elif rule_type == 'json':
                rule = JSONRule(**rule_kwargs)
            elif rule_type == 'password':
                rule = PasswordRule(**rule_kwargs)
            elif rule_type == 'api_key':
                rule = APIKeyRule(**rule_kwargs)
            else:
                rule = StringRule(**rule_kwargs)
            
            schema[field_name] = rule
        
        return schema
    
    def sanitize_input(self, data: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Sanitize input data"""
        if isinstance(data, str):
            # Basic HTML sanitization
            return html.escape(data.strip())
        elif isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, str):
                    sanitized[key] = html.escape(value.strip())
                else:
                    sanitized[key] = value
            return sanitized
        
        return data
    
    def validate_pagination(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pagination parameters"""
        pagination_schema = {
            'page': {'type': 'integer', 'min_value': 1, 'default': 1},
            'limit': {'type': 'integer', 'min_value': 1, 'max_value': 100, 'default': 20},
            'sort': {'type': 'string', 'required': False},
            'order': {'type': 'string', 'pattern': '^(asc|desc)$', 'required': False}
        }
        
        schema = self.create_schema(pagination_schema)
        
        # Apply defaults
        for field_name, field_def in pagination_schema.items():
            if 'default' in field_def and field_name not in data:
                data[field_name] = field_def['default']
        
        return self.validate(data)
    
    def validate_search_params(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate search parameters"""
        search_schema = {
            'q': {'type': 'string', 'min_length': 1, 'max_length': 100},
            'filters': {'type': 'json', 'required': False},
            'page': {'type': 'integer', 'min_value': 1, 'default': 1},
            'limit': {'type': 'integer', 'min_value': 1, 'max_value': 100, 'default': 20}
        }
        
        schema = self.create_schema(search_schema)
        
        # Apply defaults
        for field_name, field_def in search_schema.items():
            if 'default' in field_def and field_name not in data:
                data[field_name] = field_def['default']
        
        return self.validate(data)


# Global validator instance
input_validator = InputValidator()
