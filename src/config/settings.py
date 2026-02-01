# Helm AI - Configuration Management
"""
Centralized configuration management with validation,
environment variable support, and type safety.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field, SecretStr, ConfigDict
from enum import Enum

from src.common.exceptions import ValidationException, SystemException

class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class CacheType(str, Enum):
    """Supported cache types"""
    REDIS = "redis"
    MEMORY = "memory"

class Settings(BaseSettings):
    """Application settings with validation"""

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    # Application
    app_name: str = Field(default="Helm AI")
    app_version: str = Field(default="2.0.0")
    api_port: int = Field(default=8000)
    api_host: str = Field(default="0.0.0.0")

    # Security
    secret_key: SecretStr = Field(...)
    jwt_secret_key: SecretStr = Field(...)
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)

    # Database
    database_type: DatabaseType = Field(default=DatabaseType.POSTGRESQL)
    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)
    database_name: str = Field(default="helm_ai")
    database_user: str = Field(default="helm_ai")
    database_password: SecretStr = Field(...)

    # Database Pool
    db_pool_size: int = Field(default=20)
    db_max_overflow: int = Field(default=40)
    db_pool_timeout: int = Field(default=30)
    db_pool_recycle: int = Field(default=3600)

    # Redis/Cache
    cache_type: CacheType = Field(default=CacheType.REDIS)
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[SecretStr] = Field(default=None)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)

    # External Services
    openai_api_key: Optional[SecretStr] = Field(default=None)
    anthropic_api_key: Optional[SecretStr] = Field(default=None)

    # Monitoring
    enable_prometheus: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO)
    enable_file_logging: bool = Field(default=False)
    log_file: Optional[str] = Field(default=None)
    enable_performance_logging: bool = Field(default=True)

    # File Upload
    upload_max_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    upload_allowed_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".json"]
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # Feature Flags
    enable_ai_features: bool = Field(default=True)
    enable_analytics: bool = Field(default=True)
    enable_caching: bool = Field(default=True)

    @field_validator('api_port', 'database_port', 'redis_port', 'prometheus_port')
    @classmethod
    def validate_port(cls, v):
        """Validate port numbers"""
        if not 1 <= v <= 65535:
            raise ValueError(f'Port {v} must be between 1 and 65535')
        return v

    @field_validator('db_pool_size', 'db_max_overflow')
    @classmethod
    def validate_pool_size(cls, v):
        """Validate database pool sizes"""
        if not 1 <= v <= 100:
            raise ValueError(f'Pool size {v} must be between 1 and 100')
        return v

    @field_validator('upload_max_size')
    @classmethod
    def validate_upload_size(cls, v):
        """Validate upload max size (max 100MB)"""
        if not 1024 <= v <= 100 * 1024 * 1024:
            raise ValueError('Upload max size must be between 1KB and 100MB')
        return v

    @field_validator('upload_allowed_extensions')
    @classmethod
    def validate_extensions(cls, v):
        """Validate file extensions start with dot"""
        for ext in v:
            if not ext.startswith('.'):
                raise ValueError(f'Extension {ext} must start with dot')
        return v

    @field_validator('cors_origins')
    @classmethod
    def validate_cors_origins(cls, v):
        """Validate CORS origins are valid URLs"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        for origin in v:
            if not url_pattern.match(origin) and origin != "*":
                raise ValueError(f'Invalid CORS origin: {origin}')
        return v

    @property
    def database_url(self) -> str:
        """Generate database URL from settings"""
        if self.database_type == DatabaseType.POSTGRESQL:
            return (
                f"postgresql://{self.database_user}:"
                f"{self.database_password.get_secret_value()}@"
                f"{self.database_host}:{self.database_port}/"
                f"{self.database_name}"
            )
        elif self.database_type == DatabaseType.MYSQL:
            return (
                f"mysql://{self.database_user}:"
                f"{self.database_password.get_secret_value()}@"
                f"{self.database_host}:{self.database_port}/"
                f"{self.database_name}"
            )
        elif self.database_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database_name}.db"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")

    @property
    def redis_url(self) -> str:
        """Generate Redis URL from settings"""
        auth = ""
        if self.redis_password:
            auth = f":{self.redis_password.get_secret_value()}@"

        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        data = self.dict()

        if not include_secrets:
            # Remove or mask secret fields
            for field in self.__fields__:
                if "password" in field.lower() or "secret" in field.lower():
                    if field in data:
                        data[field] = "***masked***"

        return data

    def save_to_file(self, file_path: str, include_secrets: bool = False):
        """Save settings to JSON file"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(self.to_dict(include_secrets), f, indent=2, default=str)

    @classmethod
    def from_file(cls, file_path: str) -> "Settings":
        """Load settings from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        return cls(**data)

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            raise SystemException(
                "Failed to load application settings",
                component="Configuration",
                cause=e
            )
    return _settings

def init_settings(**kwargs) -> Settings:
    """Initialize settings with optional overrides"""
    global _settings
    _settings = Settings(**kwargs)
    return _settings

def validate_settings() -> bool:
    """Validate current settings"""
    try:
        settings = get_settings()
        # Additional validation logic can go here
        return True
    except Exception as e:
        raise ValidationException(f"Settings validation failed: {e}")

# Initialize settings on import
try:
    _settings = Settings()
except Exception as e:
    # Allow import even if settings are invalid (will be caught later)
    pass