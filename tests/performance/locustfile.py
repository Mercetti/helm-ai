"""
Helm AI Performance Testing Framework
Uses Locust for load testing and performance analysis
"""

import os
import sys
import json
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history, global_stats
from locust.log import setup_logging, logger

# Performance test configuration
PERFORMANCE_CONFIG = {
    "base_url": os.getenv("PERFORMANCE_BASE_URL", "http://localhost:8000"),
    "api_key": os.getenv("PERFORMANCE_API_KEY", ""),
    "test_duration": int(os.getenv("PERFORMANCE_DURATION", "300")),  # 5 minutes
    "ramp_up_time": int(os.getenv("PERFORMANCE_RAMP_UP", "60")),  # 1 minute
    "max_users": int(os.getenv("PERFORMANCE_MAX_USERS", "100")),
    "spawn_rate": int(os.getenv("PERFORMANCE_SPAWN_RATE", "10")),
    "host": os.getenv("PERFORMANCE_HOST", "http://localhost:8000"),
}

class HelmAIUser(HttpUser):
    """Simulated Helm AI user for load testing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.api_key = None
        self.auth_token = None
        self.created_resources = []
        
    def on_start(self):
        """Called when a user starts"""
        self.setup_user()
        
    def setup_user(self):
        """Set up user authentication and initial data"""
        try:
            # Create user account
            user_data = {
                "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
                "name": f"Test User {random.randint(1000, 9999)}",
                "role": "USER"
            }
            
            response = self.client.post(
                "/api/users/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                user_info = response.json()
                self.user_id = user_info.get("id")
                
                # Login to get token
                login_data = {
                    "email": user_data["email"],
                    "password": "testpassword123"
                }
                
                login_response = self.client.post(
                    "/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    login_info = login_response.json()
                    self.auth_token = login_info.get("access_token")
                    
                    # Create API key
                    api_key_data = {
                        "name": f"Performance Test Key {uuid.uuid4().hex[:8]}",
                        "scopes": ["read", "write"]
                    }
                    
                    api_key_response = self.client.post(
                        "/api/keys",
                        json=api_key_data,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.auth_token}"
                        }
                    )
                    
                    if api_key_response.status_code == 201:
                        api_key_info = api_key_response.json()
                        self.api_key = api_key_info.get("key")
                        logger.info(f"User {self.user_id} setup complete")
                        
        except Exception as e:
            logger.error(f"User setup failed: {e}")
    
    @task(3)
    def health_check(self):
        """Basic health check endpoint"""
        self.client.get("/health")
        
    @task(2)
    def get_user_profile(self):
        """Get user profile"""
        if self.auth_token:
            self.client.get(
                "/api/users/profile",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(5)
    def get_api_keys(self):
        """Get API keys"""
        if self.auth_token:
            self.client.get(
                "/api/keys",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(4)
    def create_api_key(self):
        """Create new API key"""
        if self.auth_token:
            api_key_data = {
                "name": f"Load Test Key {uuid.uuid4().hex[:8]}",
                "scopes": ["read"]
            }
            
            response = self.client.post(
                "/api/keys",
                json=api_key_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code == 201:
                key_info = response.json()
                self.created_resources.append(("api_key", key_info.get("id")))
    
    @task(3)
    def get_audit_logs(self):
        """Get audit logs"""
        if self.auth_token:
            self.client.get(
                "/api/audit/logs",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(2)
    def get_security_events(self):
        """Get security events"""
        if self.auth_token:
            self.client.get(
                "/api/security/events",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(1)
    def get_game_sessions(self):
        """Get game sessions"""
        if self.auth_token:
            self.client.get(
                "/api/game/sessions",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(2)
    def create_game_session(self):
        """Create game session"""
        if self.auth_token:
            session_data = {
                "game_type": "POKER",
                "session_id": f"session_{uuid.uuid4().hex[:8]}",
                "buy_in": 100.0
            }
            
            response = self.client.post(
                "/api/game/sessions",
                json=session_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code == 201:
                session_info = response.json()
                self.created_resources.append(("game_session", session_info.get("id")))
    
    @task(1)
    def update_game_session(self):
        """Update game session"""
        if self.auth_token and self.created_resources:
            # Find a game session to update
            for resource_type, resource_id in self.created_resources:
                if resource_type == "game_session":
                    update_data = {
                        "status": "ACTIVE",
                        "current_chips": random.randint(50, 200)
                    }
                    
                    self.client.put(
                        f"/api/game/sessions/{resource_id}",
                        json=update_data,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.auth_token}"
                        }
                    )
                    break
    
    @task(1)
    def get_metrics(self):
        """Get application metrics"""
        if self.auth_token:
            self.client.get(
                "/metrics",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    def on_stop(self):
        """Clean up created resources"""
        if self.auth_token and self.created_resources:
            for resource_type, resource_id in self.created_resources:
                try:
                    if resource_type == "api_key":
                        self.client.delete(
                            f"/api/keys/{resource_id}",
                            headers={"Authorization": f"Bearer {self.auth_token}"}
                        )
                    elif resource_type == "game_session":
                        self.client.delete(
                            f"/api/game/sessions/{resource_id}",
                            headers={"Authorization": f"Bearer {self.auth_token}"}
                        )
                except Exception as e:
                    logger.error(f"Failed to cleanup {resource_type} {resource_id}: {e}")

class AdminUser(HelmAIUser):
    """Simulated admin user for admin endpoint testing"""
    
    weight = 1  # Fewer admin users
    
    def setup_user(self):
        """Set up admin user"""
        try:
            # Create admin account
            user_data = {
                "email": f"admin_{uuid.uuid4().hex[:8]}@example.com",
                "name": f"Admin User {random.randint(1000, 9999)}",
                "role": "ADMIN"
            }
            
            response = self.client.post(
                "/api/users/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                user_info = response.json()
                self.user_id = user_info.get("id")
                
                # Login to get token
                login_data = {
                    "email": user_data["email"],
                    "password": "adminpassword123"
                }
                
                login_response = self.client.post(
                    "/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    login_info = login_response.json()
                    self.auth_token = login_info.get("access_token")
                    logger.info(f"Admin user {self.user_id} setup complete")
                    
        except Exception as e:
            logger.error(f"Admin user setup failed: {e}")
    
    @task(3)
    def get_all_users(self):
        """Get all users (admin only)"""
        if self.auth_token:
            self.client.get(
                "/api/admin/users",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(2)
    def get_system_metrics(self):
        """Get system metrics (admin only)"""
        if self.auth_token:
            self.client.get(
                "/api/admin/metrics",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
    
    @task(1)
    def get_audit_logs_admin(self):
        """Get all audit logs (admin only)"""
        if self.auth_token:
            self.client.get(
                "/api/admin/audit/logs",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )

class PerformanceMonitor:
    """Monitor and analyze performance during tests"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.stats = {}
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring and collect results"""
        self.end_time = time.time()
        self.collect_stats()
        logger.info("Performance monitoring stopped")
        
    def collect_stats(self):
        """Collect performance statistics"""
        try:
            # Get Locust stats
            stats = global_stats
            
            self.stats = {
                "test_duration": self.end_time - self.start_time,
                "total_requests": stats.total.num_requests,
                "total_failures": stats.total.num_failures,
                "avg_response_time": stats.total.avg_response_time,
                "median_response_time": stats.total.median_response_time,
                "min_response_time": stats.total.min_response_time,
                "max_response_time": stats.total.max_response_time,
                "requests_per_second": stats.total.current_rps if hasattr(stats.total, 'current_rps') else 0,
                "failures_per_second": stats.total.current_fail_per_sec if hasattr(stats.total, 'current_fail_per_sec') else 0,
                "p95_response_time": stats.total.get_response_time_percentile(0.95),
                "p99_response_time": stats.total.get_response_time_percentile(0.99),
            }
            
            # Get endpoint-specific stats
            endpoint_stats = {}
            for name, stat in stats.requests.items():
                if name != "Total":
                    endpoint_stats[name] = {
                        "requests": stat.num_requests,
                        "failures": stat.num_failures,
                        "avg_response_time": stat.avg_response_time,
                        "median_response_time": stat.median_response_time,
                        "min_response_time": stat.min_response_time,
                        "max_response_time": stat.max_response_time,
                    }
            
            self.stats["endpoint_stats"] = endpoint_stats
            
        except Exception as e:
            logger.error(f"Failed to collect stats: {e}")
    
    def save_results(self, filename: str = None):
        """Save performance results to file"""
        if filename is None:
            filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
            logger.info(f"Performance results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_summary(self):
        """Print performance summary"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        print(f"Test Duration: {self.stats.get('test_duration', 0):.2f} seconds")
        print(f"Total Requests: {self.stats.get('total_requests', 0)}")
        print(f"Total Failures: {self.stats.get('total_failures', 0)}")
        print(f"Success Rate: {((self.stats.get('total_requests', 0) - self.stats.get('total_failures', 0)) / max(self.stats.get('total_requests', 1)) * 100):.2f}%")
        print(f"Average Response Time: {self.stats.get('avg_response_time', 0):.2f} ms")
        print(f"Median Response Time: {self.stats.get('median_response_time', 0):.2f} ms")
        print(f"95th Percentile: {self.stats.get('p95_response_time', 0):.2f} ms")
        print(f"99th Percentile: {self.stats.get('p99_response_time', 0):.2f} ms")
        print(f"Requests/Second: {self.stats.get('requests_per_second', 0):.2f}")
        print("="*60)

# Performance monitor instance
performance_monitor = PerformanceMonitor()

# Custom event handlers
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Custom request handler for additional logging"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    else:
        logger.debug(f"Request: {name} - {response_time:.2f}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    performance_monitor.start_monitoring()
    logger.info(f"Performance test started: {environment.parsed_options.host}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    performance_monitor.stop_monitoring()
    performance_monitor.print_summary()
    performance_monitor.save_results()

# Environment setup
def setup_environment():
    """Set up Locust environment"""
    env = Environment(user_classes=[HelmAIUser, AdminUser])
    
    # Set host from configuration
    env.host = PERFORMANCE_CONFIG["host"]
    
    # Set up logging
    setup_logging("INFO", None)
    
    return env

if __name__ == "__main__":
    # Run performance test
    env = setup_environment()
    
    # Create user classes
    env.create_local_runner()
    
    # Start test
    env.runner.start(max_users=PERFORMANCE_CONFIG["max_users"], 
                     spawn_rate=PERFORMANCE_CONFIG["spawn_rate"],
                     host=PERFORMANCE_CONFIG["host"])
    
    # Wait for test to complete
    time.sleep(PERFORMANCE_CONFIG["test_duration"])
    
    # Stop test
    env.runner.stop()
    env.runner.greenlet.join()
