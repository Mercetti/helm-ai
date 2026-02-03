#!/usr/bin/env python3
"""
Stellar Logic AI - Load Balancing with Security
Advanced load balancing system with integrated security features
"""

import os
import sys
import json
import time
import logging
import threading
import hashlib
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import socket
import ssl

@dataclass
class BackendServer:
    """Backend server data structure"""
    server_id: str
    host: str
    port: int
    weight: int
    max_connections: int
    current_connections: int
    health_status: str  # HEALTHY, UNHEALTHY, MAINTENANCE
    last_health_check: datetime
    response_time: float
    security_score: float
    ssl_enabled: bool
    location: str

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    algorithm: str  # ROUND_ROBIN, LEAST_CONNECTIONS, WEIGHTED_ROUND_ROBIN, IP_HASH
    health_check_interval: int
    health_check_timeout: int
    max_retries: int
    ssl_termination: bool
    security_headers: bool
    rate_limiting: bool
    session_affinity: bool

@dataclass
class LoadBalancerStats:
    """Load balancer statistics"""
    total_requests: int
    requests_per_second: float
    active_connections: int
    failed_requests: int
    average_response_time: float
    backend_distribution: Dict[str, int]
    security_events: int

class SecurityLoadBalancer:
    """Security-enabled load balancer for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.production_path, "logs/load_balancer.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load balancer components
        self.backend_servers = {}
        self.request_queue = deque()
        self.session_affinity_map = {}
        self.rate_limit_map = defaultdict(int)
        self.security_events = deque(maxlen=1000)
        
        # Load balancing algorithms
        self.algorithms = {
            "ROUND_ROBIN": RoundRobinAlgorithm(),
            "LEAST_CONNECTIONS": LeastConnectionsAlgorithm(),
            "WEIGHTED_ROUND_ROBIN": WeightedRoundRobinAlgorithm(),
            "IP_HASH": IPHashAlgorithm()
        }
        
        # Security features
        self.security_features = {
            "ssl_termination": SSLTerminationHandler(),
            "security_headers": SecurityHeadersHandler(),
            "rate_limiting": RateLimitingHandler(),
            "ddos_protection": DDoSProtectionHandler(),
            "web_application_firewall": WebApplicationFirewallHandler()
        }
        
        # Statistics
        self.stats = LoadBalancerStats(
            total_requests=0,
            requests_per_second=0.0,
            active_connections=0,
            failed_requests=0,
            average_response_time=0.0,
            backend_distribution={},
            security_events=0
        )
        
        # Load configuration
        self.load_configuration()
        
        # Initialize health checking
        self.start_health_checks()
        
        # Initialize metrics collection
        self.start_metrics_collection()
        
        self.logger.info("Security Load Balancer initialized")
    
    def load_configuration(self):
        """Load load balancer configuration"""
        config_file = os.path.join(self.production_path, "config/load_balancer_config.json")
        
        default_config = {
            "load_balancer": {
                "enabled": True,
                "algorithm": "WEIGHTED_ROUND_ROBIN",
                "health_check": {
                    "interval": 30,  # seconds
                    "timeout": 5,    # seconds
                    "path": "/health",
                    "expected_status": 200
                },
                "security": {
                    "ssl_termination": True,
                    "security_headers": True,
                    "rate_limiting": True,
                    "rate_limit": {
                        "requests_per_minute": 1000,
                        "burst_size": 100
                    },
                    "ddos_protection": True,
                    "ddos_threshold": 1000,  # requests per minute
                    "web_application_firewall": True,
                    "waf_rules": ["SQL_INJECTION", "XSS", "PATH_TRAVERSAL"]
                },
                "session_affinity": {
                    "enabled": True,
                    "timeout": 3600  # seconds
                },
                "backend_servers": [
                    {
                        "server_id": "web01",
                        "host": "192.168.1.10",
                        "port": 8080,
                        "weight": 3,
                        "max_connections": 1000,
                        "ssl_enabled": True,
                        "location": "us-east-1"
                    },
                    {
                        "server_id": "web02",
                        "host": "192.168.1.11",
                        "port": 8080,
                        "weight": 2,
                        "max_connections": 1000,
                        "ssl_enabled": True,
                        "location": "us-east-1"
                    },
                    {
                        "server_id": "web03",
                        "host": "192.168.1.12",
                        "port": 8080,
                        "weight": 1,
                        "max_connections": 500,
                        "ssl_enabled": True,
                        "location": "us-west-1"
                    }
                ]
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                # Save default configuration
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.logger.info("Created default load balancer configuration")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = default_config
        
        # Initialize backend servers
        self.initialize_backend_servers()
    
    def initialize_backend_servers(self):
        """Initialize backend servers from configuration"""
        for server_config in self.config["load_balancer"]["backend_servers"]:
            server = BackendServer(
                server_id=server_config["server_id"],
                host=server_config["host"],
                port=server_config["port"],
                weight=server_config["weight"],
                max_connections=server_config["max_connections"],
                current_connections=0,
                health_status="UNKNOWN",
                last_health_check=datetime.now(),
                response_time=0.0,
                security_score=0.0,
                ssl_enabled=server_config.get("ssl_enabled", False),
                location=server_config.get("location", "unknown")
            )
            
            self.backend_servers[server.server_id] = server
        
        self.logger.info(f"Initialized {len(self.backend_servers)} backend servers")
    
    def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route incoming request to appropriate backend server"""
        start_time = time.time()
        
        try:
            self.stats.total_requests += 1
            
            # Apply security features
            security_result = self.apply_security_features(request_data)
            
            if not security_result["allowed"]:
                self.stats.failed_requests += 1
                self.stats.security_events += 1
                
                return {
                    "status": "blocked",
                    "reason": security_result["reason"],
                    "security_event": True
                }
            
            # Select backend server
            selected_server = self.select_backend_server(request_data)
            
            if not selected_server:
                self.stats.failed_requests += 1
                return {
                    "status": "error",
                    "reason": "No healthy backend servers available"
                }
            
            # Forward request to backend
            response = self.forward_request(selected_server, request_data)
            
            # Update statistics
            response_time = time.time() - start_time
            self.update_statistics(selected_server, response_time, True)
            
            # Update session affinity if enabled
            if self.config["load_balancer"]["session_affinity"]["enabled"]:
                client_ip = request_data.get("client_ip", "unknown")
                self.session_affinity_map[client_ip] = selected_server.server_id
            
            return {
                "status": "success",
                "backend_server": selected_server.server_id,
                "response_time": response_time,
                "security_applied": security_result["applied_features"]
            }
            
        except Exception as e:
            self.logger.error(f"Error routing request: {str(e)}")
            self.stats.failed_requests += 1
            
            return {
                "status": "error",
                "reason": f"Internal error: {str(e)}"
            }
    
    def apply_security_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply security features to request"""
        result = {
            "allowed": True,
            "reason": "",
            "applied_features": []
        }
        
        # SSL termination
        if self.config["load_balancer"]["security"]["ssl_termination"]:
            ssl_result = self.security_features["ssl_termination"].handle(request_data)
            if not ssl_result["valid"]:
                result["allowed"] = False
                result["reason"] = "SSL validation failed"
                return result
            result["applied_features"].append("ssl_termination")
        
        # Rate limiting
        if self.config["load_balancer"]["security"]["rate_limiting"]:
            rate_result = self.security_features["rate_limiting"].handle(request_data)
            if not rate_result["allowed"]:
                result["allowed"] = False
                result["reason"] = "Rate limit exceeded"
                return result
            result["applied_features"].append("rate_limiting")
        
        # DDoS protection
        if self.config["load_balancer"]["security"]["ddos_protection"]:
            ddos_result = self.security_features["ddos_protection"].handle(request_data)
            if not ddos_result["allowed"]:
                result["allowed"] = False
                result["reason"] = "DDoS attack detected"
                return result
            result["applied_features"].append("ddos_protection")
        
        # Web Application Firewall
        if self.config["load_balancer"]["security"]["web_application_firewall"]:
            waf_result = self.security_features["web_application_firewall"].handle(request_data)
            if not waf_result["allowed"]:
                result["allowed"] = False
                result["reason"] = f"WAF blocked: {waf_result['rule']}"
                return result
            result["applied_features"].append("web_application_firewall")
        
        # Security headers
        if self.config["load_balancer"]["security"]["security_headers"]:
            headers_result = self.security_features["security_headers"].handle(request_data)
            result["applied_features"].append("security_headers")
        
        return result
    
    def select_backend_server(self, request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select backend server using configured algorithm"""
        algorithm_name = self.config["load_balancer"]["algorithm"]
        algorithm = self.algorithms.get(algorithm_name)
        
        if not algorithm:
            self.logger.error(f"Unknown load balancing algorithm: {algorithm_name}")
            return None
        
        # Get healthy servers
        healthy_servers = [
            server for server in self.backend_servers.values()
            if server.health_status == "HEALTHY" and 
               server.current_connections < server.max_connections
        ]
        
        if not healthy_servers:
            self.logger.warning("No healthy backend servers available")
            return None
        
        # Check session affinity
        if self.config["load_balancer"]["session_affinity"]["enabled"]:
            client_ip = request_data.get("client_ip", "unknown")
            if client_ip in self.session_affinity_map:
                server_id = self.session_affinity_map[client_ip]
                if server_id in self.backend_servers:
                    server = self.backend_servers[server_id]
                    if (server.health_status == "HEALTHY" and 
                        server.current_connections < server.max_connections):
                        return server
        
        # Use algorithm to select server
        selected_server = algorithm.select_server(healthy_servers, request_data)
        
        if selected_server:
            selected_server.current_connections += 1
        
        return selected_server
    
    def forward_request(self, server: BackendServer, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to backend server (simulated)"""
        try:
            # Simulate request forwarding
            time.sleep(random.uniform(0.01, 0.1))  # Simulate network latency
            
            # Update server response time
            server.response_time = random.uniform(10, 100)  # ms
            
            # Simulate response
            return {
                "status": "success",
                "server_id": server.server_id,
                "response_time": server.response_time
            }
            
        except Exception as e:
            self.logger.error(f"Error forwarding request to {server.server_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            # Decrease connection count
            server.current_connections = max(0, server.current_connections - 1)
    
    def update_statistics(self, server: BackendServer, response_time: float, success: bool):
        """Update load balancer statistics"""
        # Update backend distribution
        if server.server_id not in self.stats.backend_distribution:
            self.stats.backend_distribution[server.server_id] = 0
        self.stats.backend_distribution[server.server_id] += 1
        
        # Update average response time
        total_requests = self.stats.total_requests
        current_avg = self.stats.average_response_time
        self.stats.average_response_time = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update active connections
        self.stats.active_connections = sum(
            server.current_connections for server in self.backend_servers.values()
        )
    
    def start_health_checks(self):
        """Start background health checking"""
        def health_check_loop():
            while True:
                try:
                    self.perform_health_checks()
                    time.sleep(self.config["load_balancer"]["health_check"]["interval"])
                except Exception as e:
                    self.logger.error(f"Error in health check: {str(e)}")
                    time.sleep(60)
        
        health_check_thread = threading.Thread(target=health_check_loop, daemon=True)
        health_check_thread.start()
        
        self.logger.info("Health check thread started")
    
    def perform_health_checks(self):
        """Perform health checks on all backend servers"""
        health_config = self.config["load_balancer"]["health_check"]
        
        for server in self.backend_servers.values():
            try:
                # Simulate health check
                is_healthy = self.check_server_health(server)
                
                server.health_status = "HEALTHY" if is_healthy else "UNHEALTHY"
                server.last_health_check = datetime.now()
                
                if is_healthy:
                    server.security_score = random.uniform(0.8, 1.0)
                else:
                    server.security_score = 0.0
                
                self.logger.debug(f"Health check for {server.server_id}: {server.health_status}")
                
            except Exception as e:
                self.logger.error(f"Error checking health of {server.server_id}: {str(e)}")
                server.health_status = "UNHEALTHY"
    
    def check_server_health(self, server: BackendServer) -> bool:
        """Check if server is healthy (simulated)"""
        # Simulate health check - in real implementation, would make HTTP request
        return random.random() > 0.1  # 90% chance of being healthy
    
    def start_metrics_collection(self):
        """Start metrics collection"""
        def metrics_loop():
            while True:
                try:
                    self.calculate_requests_per_second()
                    time.sleep(10)  # Calculate every 10 seconds
                except Exception as e:
                    self.logger.error(f"Error in metrics collection: {str(e)}")
                    time.sleep(60)
        
        metrics_thread = threading.Thread(target=metrics_loop, daemon=True)
        metrics_thread.start()
        
        self.logger.info("Metrics collection thread started")
    
    def calculate_requests_per_second(self):
        """Calculate requests per second"""
        # This is a simplified calculation
        # In real implementation, would track requests over time window
        self.stats.requests_per_second = self.stats.total_requests / max(1, time.time() - 1630000000)
    
    def get_load_balancer_statistics(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        return {
            "statistics": {
                "total_requests": self.stats.total_requests,
                "requests_per_second": self.stats.requests_per_second,
                "active_connections": self.stats.active_connections,
                "failed_requests": self.stats.failed_requests,
                "average_response_time": self.stats.average_response_time,
                "security_events": self.stats.security_events
            },
            "backend_servers": {
                server_id: {
                    "host": server.host,
                    "port": server.port,
                    "health_status": server.health_status,
                    "current_connections": server.current_connections,
                    "max_connections": server.max_connections,
                    "response_time": server.response_time,
                    "security_score": server.security_score,
                    "ssl_enabled": server.ssl_enabled
                }
                for server_id, server in self.backend_servers.items()
            },
            "backend_distribution": self.stats.backend_distribution,
            "security_features": {
                feature: handler.get_stats()
                for feature, handler in self.security_features.items()
            },
            "algorithm": self.config["load_balancer"]["algorithm"],
            "session_affinity": {
                "enabled": self.config["load_balancer"]["session_affinity"]["enabled"],
                "active_sessions": len(self.session_affinity_map)
            }
        }

# Load Balancing Algorithms
class RoundRobinAlgorithm:
    """Round-robin load balancing algorithm"""
    
    def __init__(self):
        self.current_index = 0
    
    def select_server(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select server using round-robin"""
        if not servers:
            return None
        
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        
        return server

class LeastConnectionsAlgorithm:
    """Least connections load balancing algorithm"""
    
    def select_server(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select server with least connections"""
        if not servers:
            return None
        
        return min(servers, key=lambda s: s.current_connections)

class WeightedRoundRobinAlgorithm:
    """Weighted round-robin load balancing algorithm"""
    
    def __init__(self):
        self.current_weights = {}
    
    def select_server(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select server using weighted round-robin"""
        if not servers:
            return None
        
        # Initialize weights if needed
        for server in servers:
            if server.server_id not in self.current_weights:
                self.current_weights[server.server_id] = 0
        
        # Find server with highest current weight
        selected_server = max(
            servers,
            key=lambda s: self.current_weights[s.server_id] + s.weight
        )
        
        # Update weights
        for server in servers:
            if server == selected_server:
                self.current_weights[server.server_id] -= sum(s.weight for s in servers)
            else:
                self.current_weights[server.server_id] += server.weight
        
        return selected_server

class IPHashAlgorithm:
    """IP hash load balancing algorithm"""
    
    def select_server(self, servers: List[BackendServer], request_data: Dict[str, Any]) -> Optional[BackendServer]:
        """Select server based on client IP hash"""
        if not servers:
            return None
        
        client_ip = request_data.get("client_ip", "unknown")
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        
        server_index = hash_value % len(servers)
        return servers[server_index]

# Security Feature Handlers
class SSLTerminationHandler:
    """SSL termination handler"""
    
    def handle(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SSL termination"""
        # Simulate SSL validation
        return {
            "valid": request_data.get("https", False),
            "certificate_info": "Valid certificate"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {"type": "ssl_termination", "status": "active"}

class SecurityHeadersHandler:
    """Security headers handler"""
    
    def handle(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers"""
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        return {
            "headers": headers,
            "applied": True
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {"type": "security_headers", "status": "active"}

class RateLimitingHandler:
    """Rate limiting handler"""
    
    def __init__(self):
        self.rate_limits = defaultdict(list)
    
    def handle(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rate limiting"""
        client_ip = request_data.get("client_ip", "unknown")
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit (100 requests per minute)
        if len(self.rate_limits[client_ip]) >= 100:
            return {
                "allowed": False,
                "current_count": len(self.rate_limits[client_ip])
            }
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        
        return {
            "allowed": True,
            "current_count": len(self.rate_limits[client_ip])
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "type": "rate_limiting",
            "active_clients": len(self.rate_limits),
            "status": "active"
        }

class DDoSProtectionHandler:
    """DDoS protection handler"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.window_start = time.time()
    
    def handle(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DDoS protection"""
        current_time = time.time()
        
        # Reset window every minute
        if current_time - self.window_start > 60:
            self.request_counts.clear()
            self.window_start = current_time
        
        client_ip = request_data.get("client_ip", "unknown")
        self.request_counts[client_ip] += 1
        
        # Check if client exceeds threshold (1000 requests per minute)
        if self.request_counts[client_ip] > 1000:
            return {
                "allowed": False,
                "request_count": self.request_counts[client_ip]
            }
        
        return {
            "allowed": True,
            "request_count": self.request_counts[client_ip]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "type": "ddos_protection",
            "active_clients": len(self.request_counts),
            "status": "active"
        }

class WebApplicationFirewallHandler:
    """Web Application Firewall handler"""
    
    def handle(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WAF rules"""
        # Get request data
        url = request_data.get("url", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # Check for common attack patterns
        patterns = {
            "SQL_INJECTION": r"(union|select|insert|update|delete|drop|exec|script)",
            "XSS": r"(<script|javascript:|onload=|onerror=)",
            "PATH_TRAVERSAL": r"(\.\./|\.\.\\)"
        }
        
        for rule_name, pattern in patterns.items():
            # Check URL
            if re.search(pattern, url, re.IGNORECASE):
                return {
                    "allowed": False,
                    "rule": rule_name,
                    "matched_in": "url"
                }
            
            # Check headers
            for header_name, header_value in headers.items():
                if re.search(pattern, str(header_value), re.IGNORECASE):
                    return {
                        "allowed": False,
                        "rule": rule_name,
                        "matched_in": f"header_{header_name}"
                    }
            
            # Check body
            if re.search(pattern, body, re.IGNORECASE):
                return {
                    "allowed": False,
                    "rule": rule_name,
                    "matched_in": "body"
                }
        
        return {
            "allowed": True,
            "rule": None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {"type": "web_application_firewall", "status": "active"}

def main():
    """Main function to test security load balancing"""
    load_balancer = SecurityLoadBalancer()
    
    print("⚖️ STELLAR LOGIC AI - SECURITY LOAD BALANCING")
    print("=" * 60)
    
    # Test load balancing with different requests
    test_requests = [
        {
            "client_ip": "192.168.1.100",
            "url": "/api/users",
            "method": "GET",
            "headers": {"User-Agent": "Mozilla/5.0"},
            "body": "",
            "https": True
        },
        {
            "client_ip": "192.168.1.101",
            "url": "/api/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": '{"username": "admin", "password": "password"}',
            "https": True
        },
        {
            "client_ip": "192.168.1.102",
            "url": "/api/data",
            "method": "GET",
            "headers": {"Authorization": "Bearer token123"},
            "body": "",
            "https": True
        },
        {
            "client_ip": "192.168.1.103",
            "url": "/admin/config",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": '{"setting": "value"}',
            "https": False  # This should be blocked by SSL termination
        },
        {
            "client_ip": "192.168.1.104",
            "url": "/api/search?q=<script>alert('xss')</script>",
            "method": "GET",
            "headers": {"User-Agent": "Mozilla/5.0"},
            "body": "",
            "https": True  # This should be blocked by WAF
        }
    ]
    
    print(f"\n🚀 Testing Load Balancing with {len(test_requests)} requests...")
    
    # Process requests
    for i, request in enumerate(test_requests, 1):
        print(f"\n📡 Request {i}: {request['method']} {request['url']}")
        
        result = load_balancer.route_request(request)
        
        if result["status"] == "success":
            print(f"   ✅ Routed to: {result['backend_server']}")
            print(f"   📊 Response time: {result['response_time']:.3f}s")
            print(f"   🔒 Security applied: {', '.join(result['security_applied'])}")
        elif result["status"] == "blocked":
            print(f"   🚫 Blocked: {result['reason']}")
            print(f"   🔴 Security event detected")
        else:
            print(f"   ❌ Error: {result['reason']}")
    
    # Test load with multiple requests from same client (session affinity)
    print(f"\n🔄 Testing Session Affinity...")
    client_ip = "192.168.1.200"
    
    for i in range(3):
        request = {
            "client_ip": client_ip,
            "url": f"/api/request/{i}",
            "method": "GET",
            "headers": {"User-Agent": "Test Client"},
            "body": "",
            "https": True
        }
        
        result = load_balancer.route_request(request)
        if result["status"] == "success":
            print(f"   Request {i+1}: {result['backend_server']}")
    
    # Display statistics
    stats = load_balancer.get_load_balancer_statistics()
    print(f"\n📊 Load Balancer Statistics:")
    print(f"   Total requests: {stats['statistics']['total_requests']}")
    print(f"   Requests per second: {stats['statistics']['requests_per_second']:.2f}")
    print(f"   Active connections: {stats['statistics']['active_connections']}")
    print(f"   Failed requests: {stats['statistics']['failed_requests']}")
    print(f"   Average response time: {stats['statistics']['average_response_time']:.3f}s")
    print(f"   Security events: {stats['statistics']['security_events']}")
    
    print(f"\n🖥️ Backend Server Status:")
    for server_id, server_info in stats['backend_servers'].items():
        status_emoji = "🟢" if server_info['health_status'] == "HEALTHY" else "🔴"
        print(f"   {status_emoji} {server_id}: {server_info['health_status']}")
        print(f"      Connections: {server_info['current_connections']}/{server_info['max_connections']}")
        print(f"      Response time: {server_info['response_time']:.1f}ms")
        print(f"      Security score: {server_info['security_score']:.2f}")
    
    print(f"\n🔐 Security Features Status:")
    for feature, feature_stats in stats['security_features'].items():
        print(f"   ✅ {feature}: {feature_stats['status']}")
    
    print(f"\n🎯 Load Balancing Algorithm: {stats['algorithm']}")
    print(f"   Session affinity: {'Enabled' if stats['session_affinity']['enabled'] else 'Disabled'}")
    print(f"   Active sessions: {stats['session_affinity']['active_sessions']}")
    
    print(f"\n🎯 Security Load Balancing is operational!")

if __name__ == "__main__":
    main()
