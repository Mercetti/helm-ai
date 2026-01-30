"""
Realistic Load Testing Configuration for Helm AI
Configuration for realistic traffic patterns and user behavior scenarios
"""

REALISTIC_LOAD_CONFIG = {
    "host": "http://localhost:5000",
    "base_users": 100,
    "scenarios": {
        "daily_pattern": {
            "enabled": True,
            "description": "Daily traffic pattern simulation with hourly variations",
            "focus_hours": "all_day",
            "user_distribution": {
                "BusinessUser": 60,
                "CasualUser": 25,
                "PowerUser": 10,
                "MobileAppUser": 5
            }
        },
        "business_hours": {
            "enabled": True,
            "description": "Business hours focused testing (9am-5pm)",
            "focus_hours": "9am-5pm",
            "user_distribution": {
                "BusinessUser": 70,
                "CasualUser": 15,
                "PowerUser": 10,
                "MobileAppUser": 5
            }
        },
        "weekend_pattern": {
            "enabled": True,
            "description": "Weekend traffic pattern with evening focus",
            "focus_hours": "evening",
            "user_distribution": {
                "BusinessUser": 30,
                "CasualUser": 50,
                "PowerUser": 5,
                "MobileAppUser": 15
            }
        },
        "product_launch": {
            "enabled": True,
            "description": "Product launch high traffic scenario",
            "focus_hours": "all_day",
            "user_distribution": {
                "BusinessUser": 40,
                "CasualUser": 35,
                "PowerUser": 15,
                "MobileAppUser": 10
            }
        },
        "maintenance_window": {
            "enabled": True,
            "description": "Maintenance window low traffic scenario",
            "focus_hours": "minimal",
            "user_distribution": {
                "BusinessUser": 20,
                "CasualUser": 30,
                "PowerUser": 10,
                "MobileAppUser": 40
            }
        },
        "burst_traffic": {
            "enabled": True,
            "description": "Sudden traffic burst simulation",
            "burst_factor": 3.0,
            "burst_duration_minutes": 30,
            "user_distribution": {
                "BusinessUser": 50,
                "CasualUser": 30,
                "PowerUser": 15,
                "MobileAppUser": 5
            }
        },
        "gradual_ramp": {
            "enabled": True,
            "description": "Gradual user ramp-up scenario",
            "start_users": 50,
            "end_users": 200,
            "duration_hours": 4,
            "user_distribution": {
                "BusinessUser": 60,
                "CasualUser": 25,
                "PowerUser": 10,
                "MobileAppUser": 5
            }
        }
    },
    "traffic_patterns": {
        "hourly_multipliers": {
            "business_hours": {
                "9am-11am": 1.0,
                "11am-1pm": 0.8,
                "2pm-4pm": 0.9,
                "4pm-5pm": 0.6
            },
            "weekend": {
                "morning": 0.3,
                "afternoon": 0.5,
                "evening": 1.0,
                "night": 0.2
            },
            "product_launch": {
                "all_hours": 2.0
            },
            "maintenance": {
                "all_hours": 0.1
            }
        },
        "weekly_multipliers": {
            "monday": 1.0,
            "tuesday": 0.95,
            "wednesday": 0.9,
            "thursday": 0.85,
            "friday": 0.8,
            "saturday": 0.4,
            "sunday": 0.3
        },
        "seasonal_multipliers": {
            "spring": 1.1,
            "summer": 0.9,
            "fall": 1.0,
            "winter": 0.95
        }
    },
    "user_behaviors": {
        "BusinessUser": {
            "session_duration": "15-30min",
            "actions_per_session": 10,
            "peak_hours": "9am-5pm",
            "common_actions": [
                "view_dashboard",
                "analyze_data",
                "manage_projects",
                "team_collaboration",
                "generate_reports"
            ],
            "wait_time": "2-8s"
        },
        "CasualUser": {
            "session_duration": "5-15min",
            "actions_per_session": 5,
            "peak_hours": "evening",
            "common_actions": [
                "browse_content",
                "search_content",
                "interact_with_content",
                "update_profile"
            ],
            "wait_time": "1-5s"
        },
        "PowerUser": {
            "session_duration": "30-60min",
            "actions_per_session": 20,
            "peak_hours": "all_day",
            "common_actions": [
                "advanced_analytics",
                "api_integration",
                "automation_workflows",
                "bulk_operations",
                "system_administration"
            ],
            "wait_time": "0.5-3s"
        },
        "MobileAppUser": {
            "session_duration": "2-10min",
            "actions_per_session": 8,
            "peak_hours": "evening",
            "common_actions": [
                "mobile_dashboard",
                "push_notifications",
                "mobile_features"
            ],
            "wait_time": "1-6s"
        }
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_interval": 30,
        "save_user_journeys": True,
        "track_response_times": True,
        "track_error_rates": True,
        "track_throughput": True,
        "enable_profiling": False,
        "memory_monitoring": True,
        "cpu_monitoring": True
    },
    "reporting": {
        "generate_charts": True,
        "compare_patterns": True,
        "export_csv": True,
        "export_json": True,
        "generate_html": True,
        "include_user_journeys": True,
        "performance_analysis": True,
        "bottleneck_detection": True
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
        },
        "user_satisfaction": {
            "warning": 0.95,
            "critical": 0.90
        }
    },
    "environment": {
        "name": "development",
        "database": "sqlite",
        "cache": "redis",
        "message_queue": "celery",
        "cdn": "cloudflare",
        "load_balancer": "nginx"
    },
    "test_execution": {
        "parallel_scenarios": False,
        "scenario_wait_time": 60,
        "health_check_interval": 30,
        "max_retry_attempts": 3,
        "retry_backoff": 10
    },
    "data_generation": {
        "realistic_user_data": True,
        "diverse_content": True,
        "natural_timing": True,
        "geographic_distribution": True,
        "device_distribution": {
            "desktop": 60,
            "mobile": 30,
            "tablet": 10
        },
        "browser_distribution": {
            "chrome": 65,
            "firefox": 15,
            "safari": 10,
            "edge": 8,
            "other": 2
        }
    }
}
