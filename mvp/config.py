#!/usr/bin/env python3
"""
Helm AI - Configuration Management
Centralized configuration for all Helm AI components
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    path: str = "helm_ai.db"
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 100
    socket_timeout: int = 30
    socket_connect_timeout: int = 30

@dataclass
class ModelConfig:
    """AI model configuration"""
    device: str = "auto"  # auto, cpu, cuda
    model_path: str = "models/"
    batch_size: int = 32
    max_sequence_length: int = 512
    confidence_threshold: float = 0.5
    enable_gpu: bool = True
    model_cache_size: int = 1000
    
    # Vision model settings
    vision_model: str = "resnet50"
    image_size: tuple = (224, 224)
    normalization_mean: tuple = (0.485, 0.456, 0.406)
    normalization_std: tuple = (0.229, 0.224, 0.225)
    
    # Audio model settings
    audio_model: str = "wav2vec2"
    sample_rate: int = 16000
    n_mfcc: int = 40
    audio_length: float = 1.0  # seconds
    
    # Network model settings
    network_model: str = "lstm"
    sequence_length: int = 100
    n_features: int = 10

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    log_level: str = "info"
    access_log: bool = True
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate limiting
    default_rate_limit: int = 100
    rate_limit_window: int = 60  # seconds
    
    # CORS settings
    allow_origins: list = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: list = field(default_factory=lambda: ["*"])
    allow_headers: list = field(default_factory=lambda: ["*"])

@dataclass
class StreamlitConfig:
    """Streamlit app configuration"""
    page_title: str = "Helm AI - Anti-Cheat Detection"
    page_icon: str = "🛡️"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # File upload settings
    max_file_size: int = 200  # MB
    allowed_image_types: list = field(default_factory=lambda: ["png", "jpg", "jpeg"])
    allowed_audio_types: list = field(default_factory=lambda: ["wav", "mp3", "ogg"])
    
    # Display settings
    theme: str = "dark"
    custom_css: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "logs/helm_ai.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    
    # Structured logging
    structured: bool = True
    json_format: bool = False

@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    metrics_prefix: str = "helm_ai"
    
    # Performance monitoring
    track_latency: bool = True
    track_memory: bool = True
    track_cpu: bool = True
    track_gpu: bool = True
    
    # Health checks
    health_check_interval: int = 30  # seconds
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "latency_p95": 100.0,  # ms
        "error_rate": 0.01,    # 1%
        "memory_usage": 0.8,   # 80%
        "cpu_usage": 0.8       # 80%
    })

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: Optional[str] = None
    hash_algorithm: str = "sha256"
    password_min_length: int = 8
    session_timeout: int = 3600  # seconds
    
    # API key settings
    api_key_length: int = 32
    api_key_prefix: str = "helm_"
    
    # Data protection
    encrypt_sensitive_data: bool = True
    anonymize_logs: bool = True
    data_retention_days: int = 90

@dataclass
class HelmAIConfig:
    """Main configuration class"""
    # Environment
    environment: str = "development"  # development, staging, production
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    api: APIConfig = field(default_factory=APIConfig)
    streamlit: StreamlitConfig = field(default_factory=StreamlitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Paths
    base_path: Path = field(default_factory=lambda: Path(__file__).parent)
    data_path: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    logs_path: Path = field(default_factory=lambda: Path(__file__).parent / "logs")
    models_path: Path = field(default_factory=lambda: Path(__file__).parent / "models")
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Create directories if they don't exist
        self.data_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        self.models_path.mkdir(exist_ok=True)
        
        # Set device based on availability and configuration
        if self.model.device == "auto":
            import torch
            self.model.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load environment-specific overrides
        self._load_environment_overrides()
    
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        # API Configuration
        if os.getenv("API_HOST"):
            self.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_SECRET_KEY"):
            self.api.secret_key = os.getenv("API_SECRET_KEY")
        
        # Database Configuration
        if os.getenv("DATABASE_URL"):
            self.database.type = "postgresql"
            # Parse DATABASE_URL and set connection parameters
            # Implementation depends on your database URL format
        
        # Redis Configuration
        if os.getenv("REDIS_HOST"):
            self.redis.host = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            self.redis.port = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_PASSWORD"):
            self.redis.password = os.getenv("REDIS_PASSWORD")
        
        # Model Configuration
        if os.getenv("MODEL_DEVICE"):
            self.model.device = os.getenv("MODEL_DEVICE")
        if os.getenv("MODEL_PATH"):
            self.model.model_path = os.getenv("MODEL_PATH")
        
        # Logging Configuration
        if os.getenv("LOG_LEVEL"):
            self.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.logging.file_path = os.getenv("LOG_FILE")
    
    @classmethod
    def from_file(cls, config_path: str) -> "HelmAIConfig":
        """Load configuration from file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine file format
        if config_file.suffix.lower() == ".json":
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        elif config_file.suffix.lower() in [".yml", ".yaml"]:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
        
        # Create configuration instance
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment,
            "database": asdict(self.database),
            "redis": asdict(self.redis),
            "model": asdict(self.model),
            "api": asdict(self.api),
            "streamlit": asdict(self.streamlit),
            "logging": asdict(self.logging),
            "monitoring": asdict(self.monitoring),
            "security": asdict(self.security),
            "base_path": str(self.base_path),
            "data_path": str(self.data_path),
            "logs_path": str(self.logs_path),
            "models_path": str(self.models_path)
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        config_file = Path(config_path)
        config_data = self.to_dict()
        
        # Determine file format
        if config_file.suffix.lower() == ".json":
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
        elif config_file.suffix.lower() in [".yml", ".yaml"]:
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Validate required fields
            if not self.api.secret_key or self.api.secret_key == "your-secret-key-change-in-production":
                if self.environment == "production":
                    raise ValueError("API secret key must be set in production")
            
            # Validate paths
            if not self.base_path.exists():
                raise ValueError(f"Base path does not exist: {self.base_path}")
            
            # Validate model configuration
            if self.model.device not in ["auto", "cpu", "cuda"]:
                raise ValueError(f"Invalid device: {self.model.device}")
            
            # Validate API configuration
            if not (1 <= self.api.port <= 65535):
                raise ValueError(f"Invalid API port: {self.api.port}")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.type == "sqlite":
            return f"sqlite:///{self.database.path}"
        elif self.database.type == "postgresql":
            return f"postgresql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database}"
        elif self.database.type == "mysql":
            return f"mysql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.database.type}")
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        else:
            return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"

# Global configuration instance
config = HelmAIConfig()

# Configuration factory functions
def load_config(config_path: Optional[str] = None) -> HelmAIConfig:
    """Load configuration from file or use defaults"""
    if config_path:
        return HelmAIConfig.from_file(config_path)
    else:
        # Try to load from default locations
        default_paths = [
            "config.yaml",
            "config.yml",
            "config.json",
            "helm_ai_config.yaml",
            "helm_ai_config.yml",
            "helm_ai_config.json"
        ]
        
        for path in default_paths:
            if Path(path).exists():
                return HelmAIConfig.from_file(path)
        
        # Return default configuration
        return HelmAIConfig()

def get_config() -> HelmAIConfig:
    """Get global configuration instance"""
    return config

def update_config(updates: Dict[str, Any]):
    """Update global configuration"""
    global config
    
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown configuration key: {key}")

# Environment-specific configurations
def get_development_config() -> HelmAIConfig:
    """Get development configuration"""
    return HelmAIConfig(
        environment="development",
        api=APIConfig(debug=True, reload=True),
        logging=LoggingConfig(level="DEBUG", console_output=True),
        monitoring=MonitoringConfig(enable_prometheus=False)
    )

def get_staging_config() -> HelmAIConfig:
    """Get staging configuration"""
    return HelmAIConfig(
        environment="staging",
        api=APIConfig(debug=False, reload=False),
        logging=LoggingConfig(level="INFO", console_output=False),
        monitoring=MonitoringConfig(enable_prometheus=True)
    )

def get_production_config() -> HelmAIConfig:
    """Get production configuration"""
    return HelmAIConfig(
        environment="production",
        api=APIConfig(debug=False, reload=False, workers=4),
        logging=LoggingConfig(level="WARNING", console_output=False),
        monitoring=MonitoringConfig(enable_prometheus=True),
        security=SecurityConfig(
            encrypt_sensitive_data=True,
            anonymize_logs=True,
            data_retention_days=30
        )
    )

# Configuration validation
def validate_config(config: HelmAIConfig) -> bool:
    """Validate configuration and return True if valid"""
    return config.validate()

if __name__ == "__main__":
    # Test configuration
    print("Testing Helm AI Configuration...")
    
    # Load configuration
    cfg = get_config()
    print(f"Environment: {cfg.environment}")
    print(f"API Host: {cfg.api.host}")
    print(f"API Port: {cfg.api.port}")
    print(f"Database Type: {cfg.database.type}")
    print(f"Model Device: {cfg.model.device}")
    
    # Validate configuration
    is_valid = validate_config(cfg)
    print(f"Configuration valid: {is_valid}")
    
    # Save configuration to file
    cfg.save_to_file("config_example.yaml")
    print("Configuration saved to config_example.yaml")
    
    print("Configuration test completed!")
