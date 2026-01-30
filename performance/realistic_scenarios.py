"""
Realistic Load Testing Scenarios for Helm AI
These scenarios simulate real-world traffic patterns based on user analytics
"""

from locust import HttpUser, task, between, events
import json
import random
import time
from datetime import datetime, timedelta
import statistics

class RealisticUserBehavior(HttpUser):
    """
    Base class for realistic user behavior patterns
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.verify = False
        self.session_data = self.generate_session_data()
        self.user_journey = []
        self.start_time = time.time()
        
    def generate_session_data(self):
        """Generate realistic session data"""
        return {
            "session_id": f"session_{random.randint(100000, 999999)}",
            "device_type": random.choice(["desktop", "mobile", "tablet"]),
            "browser": random.choice(["chrome", "firefox", "safari", "edge"]),
            "location": random.choice(["US", "EU", "APAC", "LATAM"]),
            "referrer": random.choice(["direct", "google", "social", "email", "organic"]),
            "session_start": datetime.now().isoformat()
        }
    
    def log_action(self, action, duration=0):
        """Log user action for analysis"""
        self.user_journey.append({
            "action": action,
            "timestamp": time.time() - self.start_time,
            "duration": duration,
            "session_id": self.session_data["session_id"]
        })


class BusinessUser(RealisticUserBehavior):
    """
    Simulates business user behavior patterns
    Typical workday: 9am-5pm with lunch break patterns
    """
    
    wait_time = between(2, 8)  # Business users are more deliberate
    
    def on_start(self):
        """Initialize business user session"""
        super().on_start()
        self.login_business_user()
        
    def login_business_user(self):
        """Login as business user"""
        login_data = {
            "email": f"{self.session_data['session_id']}@company.com",
            "password": "business_password",
            "remember_me": random.choice([True, False])
        }
        
        start = time.time()
        response = self.client.post("/api/auth/login", json=login_data, catch_response=True)
        duration = time.time() - start
        
        self.log_action("login", duration)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
            except json.JSONDecodeError:
                pass
    
    @task(4)
    def view_dashboard(self):
        """View main dashboard - most common action"""
        start = time.time()
        params = {
            "period": random.choice(["today", "week", "month"]),
            "widgets": random.choice(["all", "analytics", "projects", "team"])
        }
        self.client.get("/api/dashboard", params=params, catch_response=True)
        self.log_action("view_dashboard", time.time() - start)
    
    @task(3)
    def analyze_data(self):
        """Analyze business data"""
        start = time.time()
        analysis_types = ["sales", "customers", "products", "performance", "financial"]
        analysis_type = random.choice(analysis_types)
        
        params = {
            "type": analysis_type,
            "period": random.choice(["7d", "30d", "90d", "1y"]),
            "granularity": random.choice(["hour", "day", "week", "month"]),
            "filters": json.dumps({
                "region": random.choice(["US", "EU", "APAC"]),
                "department": random.choice(["sales", "marketing", "support", "engineering"])
            })
        }
        
        self.client.get("/api/analytics/business", params=params, catch_response=True)
        self.log_action("analyze_data", time.time() - start)
    
    @task(2)
    def manage_projects(self):
        """Project management operations"""
        start = time.time()
        
        # View projects list
        self.client.get("/api/projects", catch_response=True)
        
        # Random project operation
        operations = ["view", "create", "edit", "archive", "assign"]
        operation = random.choice(operations)
        
        if operation == "create":
            project_data = {
                "name": f"Business Project {random.randint(1000, 9999)}",
                "type": random.choice(["client", "internal", "research"]),
                "priority": random.choice(["high", "medium", "low"]),
                "budget": random.randint(10000, 100000),
                "deadline": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
            }
            self.client.post("/api/projects", json=project_data, catch_response=True)
        elif operation == "edit":
            project_id = f"proj_{random.randint(100, 999)}"
            update_data = {
                "status": random.choice(["active", "on_hold", "completed"]),
                "progress": random.randint(0, 100)
            }
            self.client.put(f"/api/projects/{project_id}", json=update_data, catch_response=True)
        
        self.log_action("manage_projects", time.time() - start)
    
    @task(2)
    def team_collaboration(self):
        """Team collaboration features"""
        start = time.time()
        
        # View team members
        self.client.get("/api/team/members", catch_response=True)
        
        # Collaboration actions
        actions = ["messages", "files", "tasks", "meetings"]
        action = random.choice(actions)
        
        if action == "messages":
            self.client.get("/api/messages/unread", catch_response=True)
        elif action == "files":
            self.client.get("/api/files/recent", catch_response=True)
        elif action == "tasks":
            self.client.get("/api/tasks/assigned", catch_response=True)
        
        self.log_action("team_collaboration", time.time() - start)
    
    @task(1)
    def generate_reports(self):
        """Generate business reports"""
        start = time.time()
        
        report_types = ["executive", "department", "project", "financial"]
        report_type = random.choice(report_types)
        
        params = {
            "type": report_type,
            "format": random.choice(["pdf", "excel", "web"]),
            "period": random.choice(["weekly", "monthly", "quarterly"]),
            "include_charts": random.choice([True, False])
        }
        
        self.client.post("/api/reports/generate", params=params, catch_response=True)
        self.log_action("generate_reports", time.time() - start)


class CasualUser(RealisticUserBehavior):
    """
    Simulates casual user behavior patterns
    More sporadic usage, shorter sessions
    """
    
    wait_time = between(1, 5)  # Casual users are faster
    
    def on_start(self):
        """Initialize casual user session"""
        super().on_start()
        self.login_casual_user()
        
    def login_casual_user(self):
        """Login as casual user"""
        login_data = {
            "email": f"user{random.randint(10000, 99999)}@{random.choice(['gmail', 'yahoo', 'outlook'])}.com",
            "password": "casual_password"
        }
        
        start = time.time()
        response = self.client.post("/api/auth/login", json=login_data, catch_response=True)
        duration = time.time() - start
        
        self.log_action("login", duration)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
            except json.JSONDecodeError:
                pass
    
    @task(5)
    def browse_content(self):
        """Browse content - most common action"""
        start = time.time()
        
        content_types = ["articles", "tutorials", "videos", "podcasts"]
        content_type = random.choice(content_types)
        
        params = {
            "type": content_type,
            "category": random.choice(["beginner", "intermediate", "advanced"]),
            "page": random.randint(1, 10),
            "limit": random.choice([10, 20, 50])
        }
        
        self.client.get("/api/content/browse", params=params, catch_response=True)
        self.log_action("browse_content", time.time() - start)
    
    @task(3)
    def search_content(self):
        """Search for specific content"""
        start = time.time()
        
        search_terms = [
            "getting started", "tutorial", "help", "how to", "guide",
            "best practices", "tips", "troubleshooting", "examples"
        ]
        
        query = random.choice(search_terms)
        params = {
            "q": query,
            "type": random.choice(["all", "articles", "videos", "courses"]),
            "sort": random.choice(["relevance", "date", "popularity"])
        }
        
        self.client.get("/api/search", params=params, catch_response=True)
        self.log_action("search_content", time.time() - start)
    
    @task(2)
    def interact_with_content(self):
        """Interact with content (like, comment, share)"""
        start = time.time()
        
        # Get a random content item
        content_id = f"content_{random.randint(1000, 9999)}"
        
        # Random interaction
        interactions = ["like", "comment", "bookmark", "share"]
        interaction = random.choice(interactions)
        
        if interaction == "like":
            self.client.post(f"/api/content/{content_id}/like", catch_response=True)
        elif interaction == "comment":
            comment_data = {
                "text": f"Great content! {random.choice(['👍', '🎉', '💡', '👏'])}",
                "rating": random.randint(4, 5)
            }
            self.client.post(f"/api/content/{content_id}/comment", json=comment_data, catch_response=True)
        elif interaction == "bookmark":
            self.client.post(f"/api/content/{content_id}/bookmark", catch_response=True)
        
        self.log_action("interact_content", time.time() - start)
    
    @task(1)
    def update_profile(self):
        """Update user profile"""
        start = time.time()
        
        profile_data = {
            "bio": f"Interested in {random.choice(['technology', 'business', 'design', 'marketing'])}",
            "interests": random.sample(["AI", "ML", "Data Science", "Web Dev", "Mobile", "Cloud"], 
                              random.randint(2, 4)),
            "location": random.choice(["US", "UK", "Canada", "Australia", "Germany"])
        }
        
        self.client.put("/api/user/profile", json=profile_data, catch_response=True)
        self.log_action("update_profile", time.time() - start)


class PowerUser(RealisticUserBehavior):
    """
    Simulates power user behavior patterns
    Heavy usage, advanced features, automation
    """
    
    wait_time = between(0.5, 3)  # Power users are very fast
    
    def on_start(self):
        """Initialize power user session"""
        super().on_start()
        self.login_power_user()
        
    def login_power_user(self):
        """Login as power user"""
        login_data = {
            "email": f"poweruser{random.randint(100, 999)}@{random.choice(['tech', 'dev', 'pro'])}.com",
            "password": "power_password",
            "two_factor": random.choice([None, "123456"])  # Some have 2FA
        }
        
        start = time.time()
        response = self.client.post("/api/auth/login", json=login_data, catch_response=True)
        duration = time.time() - start
        
        self.log_action("login", duration)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
            except json.JSONDecodeError:
                pass
    
    @task(6)
    def advanced_analytics(self):
        """Advanced analytics operations"""
        start = time.time()
        
        # Complex analytics queries
        queries = [
            "user_behavior_analysis",
            "conversion_funnel_analysis", 
            "retention_cohort_analysis",
            "feature_adoption_metrics",
            "performance_benchmarks"
        ]
        
        query = random.choice(queries)
        
        params = {
            "query": query,
            "dimensions": json.dumps(random.sample(["user_type", "device", "location", "time"], 3)),
            "metrics": json.dumps(random.sample(["sessions", "conversions", "revenue", "engagement"], 3)),
            "filters": json.dumps({
                "date_range": random.choice(["7d", "30d", "90d"]),
                "segment": random.choice(["all", "active", "new", "returning"])
            })
        }
        
        self.client.get("/api/analytics/advanced", params=params, catch_response=True)
        self.log_action("advanced_analytics", time.time() - start)
    
    @task(4)
    def api_integration(self):
        """API integration and automation"""
        start = time.time()
        
        # Test API endpoints
        endpoints = [
            "/api/v2/users/export",
            "/api/v2/analytics/stream",
            "/api/v2/projects/bulk",
            "/api/v2/reports/schedule"
        ]
        
        endpoint = random.choice(endpoints)
        
        if "export" in endpoint:
            params = {
                "format": random.choice(["json", "csv", "xml"]),
                "fields": random.sample(["id", "name", "email", "created_at"], 3)
            }
            self.client.get(endpoint, params=params, catch_response=True)
        elif "stream" in endpoint:
            stream_data = {
                "event": random.choice(["user_action", "system_event", "error"]),
                "real_time": True
            }
            self.client.post(endpoint, json=stream_data, catch_response=True)
        else:
            self.client.get(endpoint, catch_response=True)
        
        self.log_action("api_integration", time.time() - start)
    
    @task(3)
    def automation_workflows(self):
        """Automation workflow operations"""
        start = time.time()
        
        workflows = [
            "daily_report_automation",
            "user_onboarding_sequence",
            "data_sync_workflow",
            "alert_configuration"
        ]
        
        workflow = random.choice(workflows)
        
        workflow_data = {
            "name": workflow,
            "enabled": True,
            "schedule": random.choice(["daily", "weekly", "monthly"]),
            "actions": json.dumps([
                {"type": "send_email", "template": workflow},
                {"type": "update_database", "table": "analytics"},
                {"type": "trigger_webhook", "url": "https://api.example.com/webhook"}
            ])
        }
        
        self.client.post("/api/automation/workflows", json=workflow_data, catch_response=True)
        self.log_action("automation_workflows", time.time() - start)
    
    @task(2)
    def bulk_operations(self):
        """Bulk data operations"""
        start = time.time()
        
        operations = ["bulk_import", "bulk_export", "bulk_update", "bulk_delete"]
        operation = random.choice(operations)
        
        if operation == "bulk_import":
            import_data = {
                "source": random.choice(["csv", "json", "xml"]),
                "mapping": json.dumps({
                    "name": "full_name",
                    "email": "email_address",
                    "company": "organization"
                }),
                "preview": random.choice([True, False])
            }
            self.client.post("/api/bulk/import", json=import_data, catch_response=True)
        elif operation == "bulk_export":
            export_data = {
                "entity": random.choice(["users", "projects", "analytics", "reports"]),
                "format": random.choice(["csv", "json", "xlsx"]),
                "filters": json.dumps({
                    "date_range": "30d",
                    "status": "active"
                })
            }
            self.client.post("/api/bulk/export", json=export_data, catch_response=True)
        
        self.log_action("bulk_operations", time.time() - start)
    
    @task(1)
    def system_administration(self):
        """System administration tasks"""
        start = time.time()
        
        admin_tasks = [
            "system_health_check",
            "user_management",
            "security_audit",
            "performance_monitoring"
        ]
        
        task = random.choice(admin_tasks)
        
        if task == "system_health_check":
            self.client.get("/api/admin/health/detailed", catch_response=True)
        elif task == "user_management":
            params = {
                "status": random.choice(["all", "active", "suspended", "pending"]),
                "role": random.choice(["user", "admin", "moderator"])
            }
            self.client.get("/api/admin/users", params=params, catch_response=True)
        elif task == "security_audit":
            self.client.get("/api/admin/security/audit", catch_response=True)
        else:
            self.client.get("/api/admin/performance/metrics", catch_response=True)
        
        self.log_action("system_administration", time.time() - start)


# Traffic pattern simulators
class PeakHourUser(BusinessUser):
    """
    Simulates peak hour behavior (9am-11am, 2pm-4pm)
    """
    
    wait_time = between(1, 4)  # Faster during peak hours
    
    @task(6)
    def view_dashboard(self):
        """More dashboard views during peak hours"""
        super().view_dashboard()
    
    @task(4)
    def analyze_data(self):
        """More data analysis during peak hours"""
        super().analyze_data()


class OffHoursUser(CasualUser):
    """
    Simulates off-hours behavior (evenings, weekends)
    """
    
    wait_time = between(3, 10)  # Slower during off hours
    
    @task(6)
    def browse_content(self):
        """More content browsing during off hours"""
        super().browse_content()
    
    @task(4)
    def search_content(self):
        """More searching during off hours"""
        super().search_content()


class MobileAppUser(RealisticUserBehavior):
    """
    Simulates mobile app user behavior
    """
    
    wait_time = between(1, 6)
    
    def on_start(self):
        """Initialize mobile app user"""
        super().on_start()
        self.client.headers.update({
            "User-Agent": "HelmAI-Mobile/1.0",
            "X-Platform": random.choice(["iOS", "Android"])
        })
        self.login_mobile_user()
        
    def login_mobile_user(self):
        """Mobile app login"""
        login_data = {
            "email": f"mobile{random.randint(10000, 99999)}@{random.choice(['gmail', 'yahoo'])}.com",
            "password": "mobile_password",
            "device_token": f"token_{random.randint(100000, 999999)}",
            "platform": random.choice(["ios", "android"])
        }
        
        start = time.time()
        response = self.client.post("/api/auth/mobile/login", json=login_data, catch_response=True)
        duration = time.time() - start
        
        self.log_action("mobile_login", duration)
        
        if response.status_code == 200:
            try:
                token_data = response.json()
                if "access_token" in token_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {token_data['access_token']}"
                    })
            except json.JSONDecodeError:
                pass
    
    @task(5)
    def mobile_dashboard(self):
        """Mobile-optimized dashboard"""
        start = time.time()
        params = {
            "mobile": "true",
            "compact": "true",
            "widgets": random.choice(["essential", "all"])
        }
        self.client.get("/api/mobile/dashboard", params=params, catch_response=True)
        self.log_action("mobile_dashboard", time.time() - start)
    
    @task(3)
    def push_notifications(self):
        """Push notification interactions"""
        start = time.time()
        
        # Register for notifications
        notification_data = {
            "device_token": f"token_{random.randint(100000, 999999)}",
            "platform": random.choice(["ios", "android"]),
            "preferences": {
                "marketing": random.choice([True, False]),
                "updates": True,
                "messages": random.choice([True, False])
            }
        }
        
        self.client.post("/api/mobile/notifications/register", json=notification_data, catch_response=True)
        self.log_action("push_notifications", time.time() - start)
    
    @task(2)
    def mobile_features(self):
        """Mobile-specific features"""
        start = time.time()
        
        features = ["camera_upload", "location_services", "offline_mode", "biometric_auth"]
        feature = random.choice(features)
        
        if feature == "camera_upload":
            file_data = {
                "type": "image",
                "source": "camera",
                "metadata": {
                    "location": random.choice(["gallery", "camera"]),
                    "timestamp": datetime.now().isoformat()
                }
            }
            self.client.post("/api/mobile/upload", json=file_data, catch_response=True)
        elif feature == "location_services":
            location_data = {
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
                "accuracy": random.uniform(10, 100)
            }
            self.client.post("/api/mobile/location", json=location_data, catch_response=True)
        
        self.log_action("mobile_features", time.time() - start)


# Event handlers for realistic scenario analysis
@events.request.add_listener
def on_realistic_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track realistic user behavior patterns"""
    if hasattr(request, 'user') and hasattr(request.user, 'log_action'):
        # This would be used to analyze user journey patterns
        pass


@events.test_start.add_listener
def on_realistic_test_start(environment, **kwargs):
    """Initialize realistic scenario tracking"""
    print(f"Starting realistic load test at: {datetime.now()}")
    print("User behavior patterns:")
    print("- Business users: Work hours, deliberate actions")
    print("- Casual users: Sporadic usage, content-focused")
    print("- Power users: Advanced features, automation")
    print("- Mobile users: App-specific behaviors")
    print("- Peak hours: 9am-11am, 2pm-4pm")
    print("- Off hours: Evenings, weekends")


@events.test_stop.add_listener
def on_realistic_test_stop(environment, **kwargs):
    """Analyze realistic scenario results"""
    print(f"Realistic load test completed at: {datetime.now()}")
    print("User journey analysis available in results")
