#!/usr/bin/env python3
"""
Helm AI - Deployment Scripts
Production deployment automation for anti-cheat detection system
"""

import os
import sys
import subprocess
import json
import yaml
import shutil
from pathlib import Path
import logging
import argparse
from typing import Dict, List, Optional
import docker
import kubernetes
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HelmAIDeployment:
    """Production deployment manager for Helm AI"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.deployment_dir = Path("deployment")
        self.deployment_dir.mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict:
        """Load deployment configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                if self.config_file.suffix in ['.yml', '.yaml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            "environment": "production",
            "api": {
                "replicas": 3,
                "image": "helm-ai/api:latest",
                "port": 8000,
                "resources": {
                    "requests": {"cpu": "500m", "memory": "1Gi"},
                    "limits": {"cpu": "2000m", "memory": "4Gi"}
                }
            },
            "database": {
                "type": "postgresql",
                "host": "postgres",
                "port": 5432,
                "database": "helm_ai",
                "username": "helm_ai",
                "password": "change_me_in_production"
            },
            "redis": {
                "host": "redis",
                "port": 6379,
                "password": "change_me_in_production"
            },
            "monitoring": {
                "prometheus": {
                    "enabled": True,
                    "port": 9090
                },
                "grafana": {
                    "enabled": True,
                    "port": 3000
                }
            },
            "security": {
                "ssl": True,
                "cert_manager": True,
                "ingress": {
                    "host": "api.helm-ai.com",
                    "tls_secret": "helm-ai-tls"
                }
            }
        }
    
    def build_docker_images(self):
        """Build Docker images for deployment"""
        logger.info("Building Docker images...")
        
        # Build API image
        api_dockerfile = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash helmai
USER helmai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        # Write Dockerfile
        with open("Dockerfile", "w") as f:
            f.write(api_dockerfile)
        
        # Build image
        try:
            subprocess.run([
                "docker", "build",
                "-t", "helm-ai/api:latest",
                "."
            ], check=True)
            logger.info("✅ API Docker image built successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to build API image: {e}")
            raise
    
    def create_kubernetes_manifests(self):
        """Create Kubernetes manifests"""
        logger.info("Creating Kubernetes manifests...")
        
        k8s_dir = self.deployment_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # Namespace
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "helm-ai"
            }
        }
        
        with open(k8s_dir / "namespace.yaml", "w") as f:
            yaml.dump(namespace, f)
        
        # ConfigMap
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "helm-ai-config",
                "namespace": "helm-ai"
            },
            "data": {
                "config.yaml": yaml.dump(self.config, default_flow_style=False)
            }
        }
        
        with open(k8s_dir / "configmap.yaml", "w") as f:
            yaml.dump(configmap, f)
        
        # Secret
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "helm-ai-secrets",
                "namespace": "helm-ai"
            },
            "type": "Opaque",
            "data": {
                "database-password": self.config["database"]["password"],
                "redis-password": self.config["redis"]["password"]
            }
        }
        
        with open(k8s_dir / "secret.yaml", "w") as f:
            yaml.dump(secret, f)
        
        # API Deployment
        api_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "helm-ai-api",
                "namespace": "helm-ai",
                "labels": {
                    "app": "helm-ai-api"
                }
            },
            "spec": {
                "replicas": self.config["api"]["replicas"],
                "selector": {
                    "matchLabels": {
                        "app": "helm-ai-api"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "helm-ai-api"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "helm-ai-api",
                            "image": self.config["api"]["image"],
                            "ports": [{
                                "containerPort": self.config["api"]["port"],
                                "protocol": "TCP"
                            }],
                            "env": [
                                {
                                    "name": "DATABASE_URL",
                                    "value": f"postgresql://{self.config['database']['username']}:{self.config['database']['password']}@{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['database']}"
                                },
                                {
                                    "name": "REDIS_URL",
                                    "value": f"redis://:{self.config['redis']['password']}@{self.config['redis']['host']}:{self.config['redis']['port']}/0"
                                }
                            ],
                            "resources": self.config["api"]["resources"],
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": self.config["api"]["port"]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": self.config["api"]["port"]
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        with open(k8s_dir / "api-deployment.yaml", "w") as f:
            yaml.dump(api_deployment, f)
        
        # API Service
        api_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "helm-ai-api",
                "namespace": "helm-ai",
                "labels": {
                    "app": "helm-ai-api"
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "helm-ai-api"
                    }
                },
                "ports": [{
                    "port": self.config["api"]["port"],
                    "targetPort": self.config["api"]["port"],
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
        
        with open(k8s_dir / "api-service.yaml", "w") as f:
            yaml.dump(api_service, f)
        
        # Ingress (if SSL enabled)
        if self.config["security"]["ssl"]:
            ingress = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "helm-ai-ingress",
                    "namespace": "helm-ai",
                    "annotations": {
                        "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                    }
                },
                "spec": {
                    "tls": [
                        {
                            "hosts": [self.config["security"]["ingress"]["host"]],
                            "secretName": self.config["security"]["ingress"]["tls_secret"]
                        }
                    ],
                    "rules": [
                        {
                            "host": self.config["security"]["ingress"]["host"],
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "helm-ai-api",
                                                "port": {
                                                    "number": self.config["api"]["port"]
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            
            with open(k8s_dir / "ingress.yaml", "w") as f:
                yaml.dump(inggress, f)
        
        # Horizontal Pod Autoscaler
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "helm-ai-api-hpa",
                "namespace": "helm-ai"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "helm-ai-api"
                },
                "minReplicas": 2,
                "maxReplicas": 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    }
                ]
            }
        }
        
        with open(k8s_dir / "hpa.yaml", "w") as f:
            yaml.dump(hpa, f)
        
        logger.info("✅ Kubernetes manifests created successfully")
    
    def setup_monitoring(self):
        """Setup monitoring with Prometheus and Grafana"""
        logger.info("Setting up monitoring stack...")
        
        monitoring_dir = self.deployment_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        # Prometheus Config
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "helm_ai_rules.yml"

scrape_configs:
  - job_name: 'helm-ai-api'
    static_configs:
      - targets: ['helm-ai-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
"""
        
        with open(monitoring_dir / "prometheus.yml", "w") as f:
            f.write(prometheus_config)
        
        # Prometheus Rules
        prometheus_rules = """
groups:
  - name: helm_ai_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for 5 minutes"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is above 500ms"
"""
        
        with open(monitoring_dir / "helm_ai_rules.yml", "w") as f:
            f.write(prometheus_rules)
        
        # Grafana Config
        grafana_config = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": "http://prometheus:9090"
                }
            ],
            "dashboards": [
                {
                    "title": "Helm AI API Dashboard",
                    "panels": [
                        {
                            "title": "Request Rate",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "rate(http_requests_total[5m])",
                                    "legendFormat": "{{method}} {{status}}"
                                }
                            ]
                        },
                        {
                            "title": "Response Time",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                    "legendFormat": "95th percentile"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with open(monitoring_dir / "grafana_config.json", "w") as f:
            json.dump(grafana_config, f, indent=2)
        
        logger.info("✅ Monitoring configuration created")
    
    def deploy_to_kubernetes(self):
        """Deploy to Kubernetes cluster"""
        logger.info("Deploying to Kubernetes...")
        
        try:
            # Apply namespace
            subprocess.run([
                "kubectl", "apply", "-f", 
                str(self.deployment_dir / "k8s" / "namespace.yaml")
            ], check=True)
            
            # Apply ConfigMap and Secret
            subprocess.run([
                "kubectl", "apply", "-f",
                str(self.deployment_dir / "k8s" / "configmap.yaml")
            ], check=True)
            
            subprocess.run([
                "kubectl", "apply", "-f",
                str(self.deployment_dir / "k8s" / "secret.yaml")
            ], check=True)
            
            # Apply deployment
            subprocess.run([
                "kubectl", "apply", "-f",
                str(self.deployment_dir / "k8s" / "api-deployment.yaml")
            ], check=True)
            
            # Apply service
            subprocess.run([
                "kubectl", "apply", "-f",
                str(self.deployment_dir / "k8s" / "api-service.yaml")
            ], check=True)
            
            # Apply HPA
            subprocess.run([
                "kubectl", "apply", "-f",
                str(self.deployment_dir / "k8s" / "hpa.yaml")
            ], check=True)
            
            # Apply Ingress if SSL enabled
            if self.config["security"]["ssl"]:
                subprocess.run([
                    "kubectl", "apply", "-f",
                    str(self.deployment_dir / "k8s" / "ingress.yaml")
                ], check=True)
            
            logger.info("✅ Deployment to Kubernetes completed")
            
            # Wait for deployment to be ready
            self._wait_for_deployment()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Kubernetes deployment failed: {e}")
            raise
    
    def _wait_for_deployment(self):
        """Wait for deployment to be ready"""
        logger.info("Waiting for deployment to be ready...")
        
        max_wait_time = 300  # 5 minutes
        wait_interval = 10
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                result = subprocess.run([
                    "kubectl", "get", "deployment", "helm-ai-api",
                    "-n", "helm-ai", "-o", "jsonpath='{.status.readyReplicas}'"
                ], capture_output=True, text=True, check=True)
                
                ready_replicas = int(result.stdout.strip())
                
                if ready_replicas == self.config["api"]["replicas"]:
                    logger.info("✅ Deployment is ready")
                    return
                
            except subprocess.CalledProcessError:
                pass
            
            logger.info(f"Waiting for deployment... ({int((time.time() - start_time) / wait_interval)}/{max_wait_time // wait_interval})")
            time.sleep(wait_interval)
        
        raise TimeoutError("Deployment did not become ready in time")
    
    def setup_database(self):
        """Setup database (PostgreSQL)"""
        logger.info("Setting up PostgreSQL database...")
        
        # Create database initialization script
        db_init_sql = """
-- Create database
CREATE DATABASE IF NOT EXISTS helm_ai;

-- Create user
CREATE USER IF NOT EXISTS helm_ai WITH PASSWORD 'change_me_in_production';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE helm_ai TO helm_ai;

-- Connect to helm_ai database
\\c helm_ai

-- Create tables
CREATE TABLE IF NOT EXISTS detection_results (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    game_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    risk_level VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    modalities_used TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    status VARCHAR(20) DEFAULT 'completed'
);

CREATE INDEX IF NOT EXISTS idx_detection_results_user_id ON detection_results(user_id);
CREATE INDEX IF NOT EXISTS idx_detection_results_timestamp ON detection_results(timestamp);
CREATE INDEX IF NOT EXISTS idx_detection_results_risk_level ON detection_results(risk_level);

-- Create user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_detections INTEGER DEFAULT 0,
    cheating_detections INTEGER DEFAULT 0,
    suspicious_detections INTEGER DEFAULT 0,
    risk_score DECIMAL(5,2) DEFAULT 0.0,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,
    ban_until TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_last_seen ON user_profiles(last_seen);

-- Create game sessions table
CREATE TABLE IF NOT EXISTS game_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    game_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_detections INTEGER DEFAULT 0,
    max_risk_level VARCHAR(50) DEFAULT 'Safe',
    average_confidence DECIMAL(5,4) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_start_time ON game_sessions(start_time);

-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    permissions TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key);

-- Insert sample data
INSERT INTO api_keys (key, name, permissions, created_at, created_by) VALUES 
('helm_ai_demo_key', 'Demo Key', '["detect"]', NOW(), 'system');
"""
        
        with open(self.deployment_dir / "database_init.sql", "w") as f:
            f.write(db_init_sql)
        
        logger.info("✅ Database initialization script created")
    
    def setup_redis(self):
        """Setup Redis cache"""
        logger.info("Setting up Redis configuration...")
        
        redis_config = """
# Redis configuration for Helm AI
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
stop-writes-on-bgsave-error yes

# Security
requirepass your_redis_password_here
protected-mode no

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Network
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 300

# Performance
tcp-backlog 511
"""
        
        with open(self.deployment_dir / "redis.conf", "w") as f:
            f.write(redis_config)
        
        logger.info("✅ Redis configuration created")
    
    def create_deployment_scripts(self):
        """Create deployment automation scripts"""
        logger.info("Creating deployment scripts...")
        
        # Deploy script
        deploy_script = """#!/bin/bash
# Helm AI Deployment Script

set -e

echo "🚀 Starting Helm AI Deployment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed"; exit 1; }

# Build Docker images
echo "📦 Building Docker images..."
python deployment.py --build-images

# Create Kubernetes manifests
echo "📋 Creating Kubernetes manifests..."
python deployment.py --create-k8s-manifests

# Setup monitoring
echo "📊 Setting up monitoring..."
python deployment.py --setup-monitoring

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
python deployment.py --deploy-k8s

echo "✅ Deployment completed successfully!"
echo "🌐 Access your API at: https://api.helm-ai.com"
echo "📊 Access Grafana at: https://grafana.helm-ai.com"
"""
        
        with open(self.deployment_dir / "deploy.sh", "w") as f:
            f.write(deploy_script)
        
        # Make script executable
        os.chmod(self.deployment_dir / "deploy.sh", 0o755)
        
        # Cleanup script
        cleanup_script = """#!/bin/bash
# Helm AI Cleanup Script

set -e

echo "🧹 Cleaning up Helm AI deployment..."

# Delete Kubernetes resources
echo "🗑️  Deleting Kubernetes resources..."
kubectl delete -f k8s/namespace.yaml 2>/dev/null || true
kubectl delete -f k8s/configmap.yaml 2>/dev/null || true
kubectl delete -f k8s/secret.yaml 2>/dev/null || true
kubectl delete -f k8s/api-deployment.yaml 2>/dev/null || true
kubectl delete -f k8s/api-service.yaml 2>/dev/null || true
kubectl delete -f k8s/hpa.yaml 2>/dev/null || true
kubectl delete -f k8s/ingress.yaml 2>/dev/null || true

# Remove Docker images
echo "🗑️  Removing Docker images..."
docker rmi helm-ai/api:latest 2>/dev/null || true

echo "✅ Cleanup completed!"
"""
        
        with open(self.deployment_dir / "cleanup.sh", "w") as f:
            f.write(cleanup_script)
        
        # Make script executable
        os.chmod(self.deployment_dir / "cleanup.sh", 0o755)
        
        logger.info("✅ Deployment scripts created")
    
    def create_helm_chart(self):
        """Create Helm chart for Kubernetes deployment"""
        logger.info("Creating Helm chart...")
        
        chart_dir = self.deployment_dir / "helm-chart"
        chart_dir.mkdir(exist_ok=True)
        
        # Chart.yaml
        chart_yaml = {
            "apiVersion": "v2",
            "name": "helm-ai",
            "description": "Helm AI Anti-Cheat Detection System",
            "type": "application",
            "version": "1.0.0",
            "appVersion": "1.0.0"
        }
        
        with open(chart_dir / "Chart.yaml", "w") as f:
            yaml.dump(chart_yaml, f)
        
        # Values.yaml
        values_yaml = self.config
        
        with open(chart_dir / "values.yaml", "w") as f:
            yaml.dump(values_yaml, f)
        
        # Templates directory
        templates_dir = chart_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Use the Kubernetes manifests we created earlier
        k8s_dir = self.deployment_dir / "k8s"
        if k8s_dir.exists():
            for file in k8s_dir.glob("*.yaml"):
                shutil.copy(file, templates_dir / file.name)
        
        logger.info("✅ Helm chart created")
    
    def run_health_checks(self):
        """Run health checks on deployed services"""
        logger.info("Running health checks...")
        
        try:
            # Check API health
            result = subprocess.run([
                "curl", "-f", 
                f"https://{self.config['security']['ingress']['host']}/health"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("✅ API health check passed")
            else:
                logger.error("❌ API health check failed")
            
            # Check Prometheus
            if self.config["monitoring"]["prometheus"]["enabled"]:
                result = subprocess.run([
                    "curl", "-f", "http://localhost:9090/-/healthy"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    logger.info("✅ Prometheus health check passed")
                else:
                    logger.error("❌ Prometheus health check failed")
            
            # Check Grafana
            if self.config["monitoring"]["grafana"]["enabled"]:
                result = subprocess.run([
                    "curl", "-f", "http://localhost:3000/api/health"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    logger.info("✅ Grafana health check passed")
                else:
                    logger.error("❌ Grafana health check failed")
                    
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def parse_args(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description="Helm AI Deployment Manager")
        parser.add_argument(
            "--build-images",
            action="store_true",
            help="Build Docker images"
        )
        parser.add_argument(
            "--create-k8s-manifests",
            action="store_true",
            help="Create Kubernetes manifests"
        )
        parser.add_argument(
            "--setup-monitoring",
            action="store_true",
            help="Setup monitoring stack"
        )
        parser.add_argument(
            "--deploy-k8s",
            action="store_true",
            help="Deploy to Kubernetes"
        )
        parser.add_argument(
            "--create-helm-chart",
            action="store_true",
            help="Create Helm chart"
        )
        parser.add_argument(
            "--health-check",
            action="store_true",
            help="Run health checks"
        )
        parser.add_argument(
            "--config",
            default="config.yaml",
            help="Configuration file path"
        )
        
        return parser.parse_args()

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Helm AI Deployment Manager")
    parser.add_argument(
        "--build-images",
        action="store_true",
        help="Build Docker images"
    )
    parser.add_argument(
        "--create-k8s-manifests",
        action="store_true",
        help="Create Kubernetes manifests"
    )
    parser.add_argument(
        "--setup-monitoring",
        action="store_true",
        help="Setup monitoring stack"
    )
    parser.add_argument(
        "--deploy-k8s",
        action="store_true",
        help="Deploy to Kubernetes"
    )
    parser.add_argument(
        "--create-helm-chart",
        action="store_true",
        help="Create Helm chart"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health checks"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Configuration file path"
    )
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployment = HelmAIDeployment(args.config)
    
    try:
        if args.build_images:
            deployment.build_docker_images()
        
        if args.create_k8s_manifests:
            deployment.create_kubernetes_manifests()
        
        if args.setup_monitoring:
            deployment.setup_monitoring()
        
        if args.create_helm_chart:
            deployment.create_helm_chart()
        
        if args.deploy_k8s:
            deployment.deploy_to_kubernetes()
        
        if args.health_check:
            deployment.run_health_checks()
        
        # Create deployment scripts if none specified
        if not any([args.build_images, args.create_k8s_manifests, args.setup_monitoring, 
                     args.deploy_k8s, args.create_helm_chart, args.health_check]):
            deployment.create_deployment_scripts()
            logger.info("📝 Created deployment scripts. Run './deployment/deploy.sh' to deploy.")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
