"""
Performance Testing Configuration for Helm AI
"""

PERFORMANCE_CONFIG = {
    "host": "http://localhost:5000",
    "scenarios": {
        "smoke": {
            "users": 10,
            "spawn_rate": 2,
            "run_time": "60s",
            "description": "Quick smoke test to verify basic functionality"
        },
        "load": {
            "users": 50,
            "spawn_rate": 5,
            "run_time": "300s",
            "description": "Standard load test simulating normal traffic"
        },
        "stress": {
            "users": 200,
            "spawn_rate": 20,
            "run_time": "600s",
            "description": "Stress test to find system limits"
        },
        "spike": {
            "users": 500,
            "spawn_rate": 50,
            "run_time": "120s",
            "description": "Spike test simulating sudden traffic surge"
        },
        "endurance": {
            "users": 30,
            "spawn_rate": 3,
            "run_time": "3600s",
            "description": "Endurance test for long-running stability"
        },
        "api_focus": {
            "users": 100,
            "spawn_rate": 10,
            "run_time": "300s",
            "description": "API-focused performance test"
        },
        "mobile_focus": {
            "users": 25,
            "spawn_rate": 5,
            "run_time": "180s",
            "description": "Mobile app performance test"
        },
        "admin_focus": {
            "users": 5,
            "spawn_rate": 1,
            "run_time": "120s",
            "description": "Admin panel performance test"
        }
    },
    "user_types": {
        "regular": {
            "weight": 70,
            "description": "Regular web users"
        },
        "admin": {
            "weight": 5,
            "description": "Administrative users"
        },
        "api": {
            "weight": 20,
            "description": "API-only users"
        },
        "mobile": {
            "weight": 5,
            "description": "Mobile app users"
        }
    },
    "thresholds": {
        "response_time": {
            "warning": 1000,
            "critical": 2000
        },
        "error_rate": {
            "warning": 0.01,
            "critical": 0.05
        },
        "throughput": {
            "minimum": 100,
            "warning": 50
        }
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_interval": 10,
        "enable_profiling": False,
        "memory_monitoring": True,
        "cpu_monitoring": True
    },
    "reporting": {
        "generate_html": True,
        "generate_csv": True,
        "generate_json": True,
        "include_charts": True,
        "email_results": False
    },
    "environment": {
        "name": "development",
        "database": "sqlite",
        "cache": "redis",
        "message_queue": "celery"
    }
}
