"""
Helm AI Performance Testing with Locust
This file defines load testing scenarios for the Helm AI application
"""

from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask
import json
import random
import time
from datetime import datetime, timedelta

class HelmAIUser(HttpUser):
    """
    Simulates a typical Helm AI user behavior
    """
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts"""
        self.client.verify = False  # Disable SSL verification for testing
        self.user_data = self.generate_user_data()
        self.login()
        
    def generate_user_data(self):
        """Generate realistic user data for testing"""
        return {
            "email": f"testuser{random.randint(1000, 9999)}@example.com",
            "name": f"Test User {random.randint(1000, 9999)}",
            "company": f"Company {random.choice(['Tech', 'Finance', 'Healthcare', 'Education'])}",
            "plan": random.choice(['free', 'basic', 'premium', 'enterprise']),
            "user_id": f"user_{random.randint(10000, 99999)}"
        }
    
    def login(self):
        """Simulate user login"""
        login_data = {
            "email": self.user_data["email"],
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", 
                                   json=login_data,
                                   catch_response=True)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
                    self.user_data["token"] = token_data['access_token']
            except json.JSONDecodeError:
                pass
        else:
            # Try to register if login fails
            self.register()
    
    def register(self):
        """Simulate user registration"""
        register_data = {
            "email": self.user_data["email"],
            "name": self.user_data["name"],
            "password": "testpassword123",
            "company": self.user_data["company"],
            "plan": self.user_data["plan"]
        }
        
        response = self.client.post("/api/auth/register", 
                                   json=register_data,
                                   catch_response=True)
        
        if response.status_code == 201:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
                    self.user_data["token"] = token_data['access_token']
            except json.JSONDecodeError:
                pass
    
    @task(3)
    def view_dashboard(self):
        """View main dashboard - most common action"""
        self.client.get("/api/dashboard", catch_response=True)
    
    @task(2)
    def get_user_profile(self):
        """Get user profile information"""
        self.client.get("/api/user/profile", catch_response=True)
    
    @task(2)
    def get_analytics_data(self):
        """Get analytics data"""
        params = {
            "period": random.choice(["day", "week", "month"]),
            "start_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        self.client.get("/api/analytics/data", params=params, catch_response=True)
    
    @task(1)
    def update_user_settings(self):
        """Update user settings"""
        settings_data = {
            "notifications": random.choice([True, False]),
            "theme": random.choice(["light", "dark"]),
            "language": random.choice(["en", "es", "fr", "de"]),
            "timezone": random.choice(["UTC", "EST", "PST", "GMT"])
        }
        self.client.put("/api/user/settings", json=settings_data, catch_response=True)
    
    @task(1)
    def create_project(self):
        """Create a new project"""
        project_data = {
            "name": f"Test Project {random.randint(1000, 9999)}",
            "description": "Performance test project",
            "type": random.choice(["web", "mobile", "api", "desktop"]),
            "settings": {
                "auto_save": random.choice([True, False]),
                "public": random.choice([True, False]),
                "collaborators": random.randint(1, 10)
            }
        }
        self.client.post("/api/projects", json=project_data, catch_response=True)
    
    @task(1)
    def get_projects_list(self):
        """Get list of user projects"""
        params = {
            "page": random.randint(1, 5),
            "limit": random.choice([10, 20, 50]),
            "sort": random.choice(["created_at", "updated_at", "name"]),
            "order": random.choice(["asc", "desc"])
        }
        self.client.get("/api/projects", params=params, catch_response=True)
    
    @task(1)
    def search_functionality(self):
        """Test search functionality"""
        search_terms = ["dashboard", "analytics", "project", "user", "settings", "report"]
        query = random.choice(search_terms)
        params = {
            "q": query,
            "type": random.choice(["all", "projects", "users", "reports"]),
            "limit": random.randint(5, 25)
        }
        self.client.get("/api/search", params=params, catch_response=True)
    
    @task(1)
    def upload_file(self):
        """Test file upload functionality"""
        # Simulate file upload with small payload
        file_data = {
            "name": f"test_file_{random.randint(1000, 9999)}.txt",
            "size": random.randint(1024, 1048576),  # 1KB to 1MB
            "type": "text/plain",
            "content": "This is a test file for performance testing"
        }
        self.client.post("/api/files/upload", json=file_data, catch_response=True)
    
    @task(1)
    def get_notifications(self):
        """Get user notifications"""
        params = {
            "unread_only": random.choice([True, False]),
            "limit": random.randint(5, 20),
            "type": random.choice(["all", "system", "user", "project"])
        }
        self.client.get("/api/notifications", params=params, catch_response=True)
    
    @task(1)
    def health_check(self):
        """Check system health"""
        self.client.get("/api/health", catch_response=True)
    
    @task(1)
    def get_metrics(self):
        """Get system metrics"""
        params = {
            "period": random.choice(["1m", "5m", "15m", "1h"]),
            "metrics": random.choice(["cpu", "memory", "requests", "errors"])
        }
        self.client.get("/api/metrics", params=params, catch_response=True)


class AdminUser(HttpUser):
    """
    Simulates an admin user with elevated permissions
    """
    
    wait_time = between(2, 8)
    weight = 1  # Fewer admin users than regular users
    
    def on_start(self):
        """Admin user initialization"""
        self.client.verify = False
        self.login_as_admin()
    
    def login_as_admin(self):
        """Login as admin user"""
        login_data = {
            "email": "admin@helm-ai.com",
            "password": "adminpassword123"
        }
        
        response = self.client.post("/api/auth/login", 
                                   json=login_data,
                                   catch_response=True)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
            except json.JSONDecodeError:
                pass
    
    @task(3)
    def get_system_status(self):
        """Get overall system status"""
        self.client.get("/api/admin/system/status", catch_response=True)
    
    @task(2)
    def get_user_statistics(self):
        """Get user statistics"""
        params = {
            "period": random.choice(["day", "week", "month"]),
            "group_by": random.choice(["plan", "company", "registration_date"])
        }
        self.client.get("/api/admin/users/stats", params=params, catch_response=True)
    
    @task(2)
    def get_performance_metrics(self):
        """Get detailed performance metrics"""
        params = {
            "start_time": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "end_time": datetime.now().isoformat(),
            "granularity": random.choice(["1m", "5m", "15m", "1h"])
        }
        self.client.get("/api/admin/metrics/performance", params=params, catch_response=True)
    
    @task(1)
    def view_error_logs(self):
        """View system error logs"""
        params = {
            "level": random.choice(["error", "warning", "critical"]),
            "limit": random.randint(10, 100),
            "component": random.choice(["api", "database", "auth", "integration"])
        }
        self.client.get("/api/admin/logs/errors", params=params, catch_response=True)
    
    @task(1)
    def manage_users(self):
        """User management operations"""
        # Get users list
        params = {
            "page": random.randint(1, 10),
            "limit": random.choice([20, 50, 100]),
            "status": random.choice(["active", "inactive", "suspended", "all"]),
            "plan": random.choice(["free", "basic", "premium", "enterprise", "all"])
        }
        self.client.get("/api/admin/users", params=params, catch_response=True)
    
    @task(1)
    def system_health_detailed(self):
        """Detailed system health check"""
        self.client.get("/api/admin/health/detailed", catch_response=True)


class APIUser(HttpUser):
    """
    Simulates API-only user (no UI)
    """
    
    wait_time = between(0.5, 2)  # Faster for API calls
    weight = 2  # More API users than regular users
    
    def on_start(self):
        """API user initialization"""
        self.client.verify = False
        self.api_key = f"api_key_{random.randint(100000, 999999)}"
        self.client.headers.update({
            "X-API-Key": self.api_key
        })
    
    @task(5)
    def api_analytics_track(self):
        """Track analytics event via API"""
        event_data = {
            "event_name": random.choice(["page_view", "button_click", "form_submit", "login", "signup"]),
            "user_id": f"api_user_{random.randint(1000, 9999)}",
            "properties": {
                "source": "api",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        self.client.post("/api/analytics/track", json=event_data, catch_response=True)
    
    @task(3)
    def api_data_export(self):
        """Export data via API"""
        params = {
            "format": random.choice(["json", "csv", "xml"]),
            "type": random.choice(["users", "projects", "analytics", "reports"]),
            "date_range": random.choice(["7d", "30d", "90d", "1y"])
        }
        self.client.get("/api/export/data", params=params, catch_response=True)
    
    @task(2)
    def api_webhook(self):
        """Test webhook endpoints"""
        webhook_data = {
            "event": random.choice(["user.created", "project.updated", "payment.completed"]),
            "data": {
                "id": random.randint(1000, 9999),
                "timestamp": datetime.now().isoformat(),
                "source": "api_test"
            }
        }
        self.client.post("/api/webhooks/handle", json=webhook_data, catch_response=True)
    
    @task(1)
    def api_health_check(self):
        """API health check"""
        self.client.get("/api/health", catch_response=True)


# Event handlers for statistics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    Called when a request is completed
    """
    if exception:
        # Log failed requests
        print(f"Failed request: {name} ({request_type}) - {exception}")
    else:
        # Log successful requests (optional)
        pass


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust starts
    """
    print("Starting Helm AI Performance Test")
    print(f"Target Host: {environment.host}")
    print(f"Number of Users: {environment.parsed_options.num_users}")
    print(f"Hatch Rate: {environment.parsed_options.hatch_rate}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test starts
    """
    print(f"Test started at: {datetime.now()}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test stops
    """
    print(f"Test stopped at: {datetime.now()}")
    print("Performance test completed")


# Custom task sets for specific scenarios
class MobileUser(HelmAIUser):
    """
    Simulates mobile app user
    """
    
    wait_time = between(2, 6)  # Mobile users typically slower
    
    @task(4)
    def mobile_dashboard(self):
        """Mobile-optimized dashboard"""
        params = {"mobile": "true", "compact": "true"}
        self.client.get("/api/dashboard", params=params, catch_response=True)
    
    @task(2)
    def push_notification_register(self):
        """Register for push notifications"""
        notification_data = {
            "device_token": f"token_{random.randint(100000, 999999)}",
            "platform": random.choice(["ios", "android"]),
            "app_version": "1.0.0"
        }
        self.client.post("/api/mobile/notifications/register", 
                        json=notification_data, 
                        catch_response=True)


class EnterpriseUser(HelmAIUser):
    """
    Simulates enterprise user with more complex workflows
    """
    
    wait_time = between(3, 10)  # Enterprise users slower, more deliberate
    
    @task(3)
    def enterprise_dashboard(self):
        """Enterprise dashboard with more data"""
        params = {"enterprise": "true", "include_billing": "true"}
        self.client.get("/api/dashboard", params=params, catch_response=True)
    
    @task(2)
    def team_management(self):
        """Team management operations"""
        self.client.get("/api/enterprise/team", catch_response=True)
    
    @task(2)
    def billing_info(self):
        """View billing information"""
        self.client.get("/api/enterprise/billing", catch_response=True)
    
    @task(1)
    def compliance_reports(self):
        """Generate compliance reports"""
        params = {
            "type": random.choice(["gdpr", "soc2", "hipaa"]),
            "format": random.choice(["pdf", "csv"]),
            "period": random.choice(["monthly", "quarterly", "annually"])
        }
        self.client.get("/api/enterprise/compliance/reports", 
                       params=params, 
                       catch_response=True)
