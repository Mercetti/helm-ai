"""
Helm AI Main Application
This is the main entry point for the Helm AI application
"""

import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our modules
try:
    from .api.middleware import api_middleware
    from .monitoring.health_checks import health_endpoint
    from .monitoring.structured_logging import log_manager
    from .monitoring.performance_monitor import performance_monitor
    from .security.llm_security_dashboard import SimpleLLMSecurityDashboard
except ImportError:
    # Create placeholder modules if they don't exist yet
    api_middleware = None
    health_endpoint = None
    log_manager = None
    performance_monitor = None
    SimpleLLMSecurityDashboard = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'development')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.config['RATE_LIMIT_ENABLED'] = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    
    # Enable CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://helm-ai.com').split(',')
    CORS(app, origins=cors_origins)
    
    # Initialize middleware
    if api_middleware:
        api_middleware.init_app(app)
    else:
        # Basic middleware setup
        @app.before_request
        def before_request():
            g.start_time = datetime.now()
            g.request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(request)}"
            
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = (datetime.now() - g.start_time).total_seconds()
                response.headers['X-Response-Time'] = f"{duration:.3f}s"
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            return response
    
    # Basic routes
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Helm AI',
            'version': '1.0.0',
            'status': 'running',
            'environment': app.config['ENVIRONMENT'],
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'health': '/health',
                'metrics': '/metrics',
                'docs': '/docs'
            }
        })
    
    @app.route('/health')
    def health():
        if health_endpoint:
            return health_endpoint.get_health()
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Helm AI',
            'version': '1.0.0'
        }
    
    @app.route('/health/ready')
    def health_ready():
        """Readiness check for Kubernetes"""
        checks = {
            'database': check_database(),
            'ai_models': check_ai_models(),
            'external_services': check_external_services()
        }
        
        all_healthy = all(status == 'healthy' for status in checks.values())
        status_code = 200 if all_healthy else 503
        
        return jsonify({
            'status': 'ready' if all_healthy else 'not_ready',
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }), status_code
    
    @app.route('/health/live')
    def health_live():
        """Liveness check for Kubernetes"""
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/health/detailed')
    def health_detailed():
        if health_endpoint:
            return health_endpoint.get_health(detailed=True)
        return health()
    
    @app.route('/metrics')
    def metrics():
        if performance_monitor:
            return jsonify(performance_monitor.get_performance_summary())
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'status': 'basic_metrics_only'
        })
    
    # API v1 routes
    @app.route('/api/v1/ai/status')
    def ai_status():
        """AI service status"""
        return jsonify({
            'status': 'operational',
            'models_loaded': check_ai_models() == 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/v1/security/scan', methods=['POST'])
    def security_scan():
        """Security scan endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Placeholder for security scanning logic
            return jsonify({
                'scan_id': f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'status': 'initiated',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Security scan error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/security/dashboard')
    def security_dashboard():
        """LLM Security Dashboard"""
        try:
            # Import SimpleLLMSecurityDashboard directly
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from llm_security_dashboard_simple import SimpleLLMSecurityDashboard
            
            dashboard = SimpleLLMSecurityDashboard()
            html_content = dashboard.generate_dashboard_html()
            return html_content, 200, {'Content-Type': 'text/html'}
        except Exception as e:
            logger.error(f"Security dashboard error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/security/metrics')
    def security_metrics():
        """Security metrics API endpoint"""
        try:
            if SimpleLLMSecurityDashboard:
                dashboard = SimpleLLMSecurityDashboard()
                return jsonify({
                    'metrics': dashboard.metrics,
                    'recent_events': dashboard.recent_events[:10],
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'error': 'Security metrics not available',
                    'message': 'LLM Security Dashboard module not found'
                }), 503
        except Exception as e:
            logger.error(f"Security metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/ai-performance/metrics')
    def ai_performance_metrics():
        """AI Performance metrics API endpoint"""
        try:
            # Import AI Performance Monitor
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.ai_performance import ai_performance_monitor
            
            summary = ai_performance_monitor.get_performance_summary(hours=1)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"AI Performance metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/ai-performance/health')
    def ai_performance_health():
        """AI Performance health check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.ai_performance import ai_performance_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': True,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(ai_performance_monitor.metrics_history)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"AI Performance health error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/ai-performance/alerts')
    def ai_performance_alerts():
        """AI Performance alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.ai_performance import ai_performance_monitor
            
            summary = ai_performance_monitor.get_performance_summary(hours=1)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"AI Performance alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/system-health/metrics')
    def system_health_metrics():
        """System Health metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.system_health import system_health_monitor
            
            # Collect current metrics
            system_health_monitor.collect_system_metrics()
            system_health_monitor.check_service_health()
            
            summary = system_health_monitor.get_health_summary(hours=1)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"System Health metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/system-health/status')
    def system_health_status():
        """System Health status check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.system_health import system_health_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': True,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(system_health_monitor.metrics_history),
                'services_count': len(system_health_monitor.service_health)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"System Health status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/system-health/alerts')
    def system_health_alerts():
        """System Health alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.system_health import system_health_monitor
            
            summary = system_health_monitor.get_health_summary(hours=1)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"System Health alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/financial/metrics')
    def financial_metrics():
        """Financial Analytics metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.financial_analytics import financial_analytics_monitor
            
            # Add mock data for testing
            financial_analytics_monitor.record_revenue_metrics(
                mrr=15000.0,
                arr=180000.0,
                total_revenue=250000.0,
                revenue_growth_rate=0.15,
                average_revenue_per_user=125.0,
                revenue_by_plan={
                    "free": 5000.0,
                    "basic": 7500.0,
                    "premium": 15000.0,
                    "enterprise": 50000.0
                },
                revenue_by_region={
                    "north_america": 100000.0,
                    "europe": 75000.0,
                    "asia_pacific": 50000.0,
                    "other": 25000.0
                }
            )
            
            financial_analytics_monitor.record_user_metrics(
                active_users=1200,
                new_signups=45,
                churn_rate=0.03,
                retention_rate=0.92,
                avg_session_duration=180.0,
                conversion_rate=0.04,
                monthly_recurring_revenue=15000.0,
                customer_lifetime_value=1200.0
            )
            
            summary = financial_analytics_monitor.get_financial_summary(hours=24)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Financial metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/financial/status')
    def financial_status():
        """Financial Analytics status check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.financial_analytics import financial_analytics_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': True,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(financial_analytics_monitor.metrics_history),
                'user_metrics_available': bool(financial_analytics_monitor.user_metrics),
                'revenue_metrics_available': bool(financial_analytics_monitor.revenue_metrics)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"Financial status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/financial/alerts')
    def financial_alerts():
        """Financial Analytics alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.financial_analytics import financial_analytics_monitor
            
            summary = financial_analytics_monitor.get_financial_summary(hours=24)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Financial alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/analytics/metrics')
    def user_analytics_metrics():
        """User Analytics metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.user_engagement import user_engagement_monitor
            
            # Add mock data for testing
            user_engagement_monitor.record_user_behavior(
                user_id="user_001",
                session_id="session_001",
                page_views=15,
                session_duration=180.5,
                bounce_rate=0.25,
                pages_per_session=3.2,
                exit_page="/dashboard",
                entry_page="/home",
                device_type="desktop",
                browser="Chrome",
                location="north_america"
            )
            
            user_engagement_monitor.record_feature_usage(
                feature_name="AI Assistant",
                active_users=850,
                total_users=1200,
                usage_frequency=4.5,
                average_session_time=120.0,
                adoption_rate=0.85,
                satisfaction_score=4.2
            )
            
            user_engagement_monitor.record_device_data("desktop", 800, 1500)
            user_engagement_monitor.record_device_data("mobile", 350, 800)
            user_engagement_monitor.record_device_data("tablet", 50, 200)
            
            summary = user_engagement_monitor.get_engagement_summary(hours=24)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"User Analytics metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/analytics/status')
    def user_analytics_status():
        """User Analytics status check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.user_engagement import user_engagement_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': True,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(user_engagement_monitor.metrics_history),
                'user_behavior_available': bool(user_engagement_monitor.user_behavior),
                'feature_usage_available': bool(user_engagement_monitor.feature_usage)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"User Analytics status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/analytics/alerts')
    def user_analytics_alerts():
        """User Analytics alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.user_engagement import user_engagement_monitor
            
            summary = user_engagement_monitor.get_engagement_summary(hours=24)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"User Analytics alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/database/performance')
    def database_performance():
        """Database Performance metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.database_performance import database_performance_monitor
            
            # Start monitoring if not already running
            if not database_performance_monitor.monitoring_active:
                database_performance_monitor.start_monitoring()
            
            # Collect current metrics
            summary = database_performance_monitor.get_performance_summary(hours=1)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Database Performance error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
            
            metrics = realtime_data_collector.get_recent_metrics(category=category, limit=50)
            return jsonify({
                'category': category,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Real-time metrics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/database/status')
    def database_status():
        """Database Performance status check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.database_performance import database_performance_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': database_performance_monitor.monitoring_active,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(database_performance_monitor.metrics_history),
                'query_performance_available': bool(database_performance_monitor.query_performance),
                'connection_pools_available': bool(database_performance_monitor.connection_pools)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"Database status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/database/alerts')
    def database_alerts():
        """Database Performance alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.database_performance import database_performance_monitor
            
            summary = database_performance_monitor.get_performance_summary(hours=1)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Database alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/database/queries')
    def database_queries():
        """Database query performance API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.database_performance import database_performance_monitor
            
            # Get recent query performance
            queries = dict(database_performance_monitor.query_performance)
            
            return jsonify({
                'total_queries': len(queries),
                'queries': queries,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Database queries error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/database/connections')
    def database_connections():
        """Database connection pool API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.database_performance import database_performance_monitor
            
            # Get connection pool metrics
            pools = dict(database_performance_monitor.connection_pools)
            
            return jsonify({
                'total_pools': len(pools),
                'connection_pools': pools,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Database connections error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/usage')
    def resource_usage():
        """Resource Usage metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Start monitoring if not already running
            if not resource_usage_monitor.monitoring_active:
                resource_usage_monitor.start_monitoring()
            
            # Collect current metrics
            summary = resource_usage_monitor.get_resource_summary(hours=1)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Resource Usage error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/status')
    def resource_status():
        """Resource Usage status check endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Mock health check
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': resource_usage_monitor.monitoring_active,
                'last_update': datetime.now().isoformat(),
                'metrics_count': len(resource_usage_monitor.metrics_history),
                'cpu_metrics_available': bool(resource_usage_monitor.cpu_metrics),
                'memory_metrics_available': bool(resource_usage_monitor.memory_metrics),
                'disk_metrics_available': bool(resource_usage_monitor.disk_metrics),
                'network_metrics_available': bool(resource_usage_monitor.network_metrics)
            }
            
            return jsonify(health_status)
        except Exception as e:
            logger.error(f"Resource status error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/alerts')
    def resource_alerts():
        """Resource Usage alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            summary = resource_usage_monitor.get_resource_summary(hours=1)
            return jsonify({
                'alerts': summary['alerts'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Resource alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/cpu')
    def resource_cpu():
        """CPU resource metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Get CPU metrics
            cpu_metrics = dict(resource_usage_monitor.cpu_metrics)
            
            return jsonify({
                'cpu_metrics': cpu_metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Resource CPU error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/memory')
    def resource_memory():
        """Memory resource metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Get memory metrics
            memory_metrics = dict(resource_usage_monitor.memory_metrics)
            
            return jsonify({
                'memory_metrics': memory_metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Resource Memory error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/disk')
    def resource_disk():
        """Disk resource metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Get disk metrics
            disk_metrics = dict(resource_usage_monitor.disk_metrics)
            
            return jsonify({
                'disk_metrics': disk_metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Resource Disk error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/resources/network')
    def resource_network():
        """Network resource metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.resource_usage import resource_usage_monitor
            
            # Get network metrics
            network_metrics = dict(resource_usage_monitor.network_metrics)
            
            return jsonify({
                'network_metrics': network_metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Resource Network error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/alerts/active')
    def alerts_active():
        """Active alerts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.unified_alert_system import unified_alert_system
            
            # Start monitoring if not already running
            if not unified_alert_system.monitoring_active:
                unified_alert_system.start_monitoring()
            
            # Get active alerts
            active_alerts = unified_alert_system.get_active_alerts()
            return jsonify({
                'active_alerts': active_alerts,
                'count': len(active_alerts),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Active alerts error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/alerts/history')
    def alerts_history():
        """Alert history API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.unified_alert_system import unified_alert_system
            
            # Get alert history
            alert_history = unified_alert_system.get_alert_history(hours=24)
            return jsonify({
                'alert_history': alert_history,
                'count': len(alert_history),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Alert history error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/alerts/statistics')
    def alerts_statistics():
        """Alert statistics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.unified_alert_system import unified_alert_system
            
            # Get alert statistics
            statistics = unified_alert_system.get_alert_statistics()
            return jsonify(statistics)
        except Exception as e:
            logger.error(f"Alert statistics error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/alerts/acknowledge/<alert_id>', methods=['POST'])
    def alerts_acknowledge(alert_id):
        """Acknowledge alert API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.unified_alert_system import unified_alert_system
            
            # Acknowledge alert
            success = unified_alert_system.acknowledge_alert(alert_id, acknowledged_by="system")
            
            return jsonify({
                'success': success,
                'alert_id': alert_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Alert acknowledge error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/alerts/resolve/<alert_id>', methods=['POST'])
    def alerts_resolve(alert_id):
        """Resolve alert API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.unified_alert_system import unified_alert_system
            
            # Get resolution from request
            resolution = request.json.get('resolution', 'Manual resolution')
            resolved_by = request.json.get('resolved_by', 'system')
            
            # Resolve alert
            success = unified_alert_system.resolve_alert(alert_id, resolution, resolved_by)
            
            return jsonify({
                'success': success,
                'alert_id': alert_id,
                'resolution': resolution,
                'resolved_by': resolved_by,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Alert resolve error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/historical/summary')
    def historical_summary():
        """Historical data summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.historical_data_analysis import historical_data_analyzer
            
            # Get historical summary
            summary = historical_data_analyzer.get_historical_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Historical summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/historical/trends')
    def historical_trends():
        """Historical trends API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.historical_data_analysis import historical_data_analyzer
            
            # Get query parameters
            category = request.args.get('category')
            metric_name = request.args.get('metric')
            days = int(request.args.get('days', 30))
            
            # Get trend analysis
            trends = historical_data_analyzer.get_trend_analysis(
                category=category,
                metric_name=metric_name,
                days=days
            )
            
            return jsonify({
                'trends': trends,
                'category': category,
                'metric_name': metric_name,
                'period_days': days,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Historical trends error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/historical/anomalies')
    def historical_anomalies():
        """Historical anomalies API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.historical_data_analysis import historical_data_analyzer
            
            # Get query parameters
            category = request.args.get('category')
            metric_name = request.args.get('metric')
            days = int(request.args.get('days', 7))
            
            # Get anomaly detection
            anomalies = historical_data_analyzer.get_anomaly_detection(
                category=category,
                metric_name=metric_name,
                days=days
            )
            
            return jsonify({
                'anomalies': anomalies,
                'category': category,
                'metric_name': metric_name,
                'period_days': days,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Historical anomalies error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/historical/data-points', methods=['POST'])
    def historical_data_points():
        """Add historical data points API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.historical_data_analysis import historical_data_analyzer
            
            # Get data from request
            data = request.json
            metric_name = data.get('metric_name')
            value = data.get('value')
            category = data.get('category')
            source = data.get('source', 'api')
            metadata = data.get('metadata', {})
            
            # Add data point
            historical_data_analyzer.add_data_point(
                metric_name=metric_name,
                value=value,
                category=category,
                source=source,
                metadata=metadata
            )
            
            return jsonify({
                'success': True,
                'message': 'Data point added successfully',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Historical data points error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/performance/load-test', methods=['POST'])
    def performance_load_test():
        """Performance load test API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.performance_testing import performance_test_suite
            
            # Get test configuration from request
            data = request.json
            endpoint = data.get('endpoint')
            config = data.get('config')
            
            if not endpoint:
                return jsonify({'error': 'Endpoint is required'}), 400
            
            # Run load test
            test_id = performance_test_suite.run_load_test(endpoint, config)
            
            return jsonify({
                'success': True,
                'test_id': test_id,
                'message': 'Load test started',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Performance load test error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/performance/stress-test', methods=['POST'])
    def performance_stress_test():
        """Performance stress test API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.performance_testing import performance_test_suite
            
            # Get test configuration from request
            data = request.json
            endpoint = data.get('endpoint')
            config = data.get('config')
            
            if not endpoint:
                return jsonify({'error': 'Endpoint is required'}), 400
            
            # Run stress test
            test_id = performance_test_suite.run_stress_test(endpoint, config)
            
            return jsonify({
                'success': True,
                'test_id': test_id,
                'message': 'Stress test started',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Performance stress test error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/performance/benchmark-test', methods=['POST'])
    def performance_benchmark_test():
        """Performance benchmark test API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.performance_testing import performance_test_suite
            
            # Get test configuration from request
            data = request.json
            endpoint = data.get('endpoint')
            config = data.get('config')
            
            if not endpoint:
                return jsonify({'error': 'Endpoint is required'}), 400
            
            # Run benchmark test
            test_id = performance_test_suite.run_benchmark_test(endpoint, config)
            
            return jsonify({
                'success': True,
                'test_id': test_id,
                'message': 'Benchmark test started',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Performance benchmark test error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/performance/results/<test_id>')
    def performance_test_results(test_id):
        """Performance test results API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.performance_testing import performance_test_suite
            
            # Get test results
            results = performance_test_suite.get_test_results(test_id)
            
            return jsonify(results)
        except Exception as e:
            logger.error(f"Performance test results error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/performance/summary')
    def performance_test_summary():
        """Performance test summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.performance_testing import performance_test_suite
            
            # Get test summary
            summary = performance_test_suite.get_test_summary()
            
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Performance test summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/compliance/summary')
    def compliance_summary():
        """Compliance summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.compliance_audit import compliance_audit_system
            
            # Get compliance summary
            summary = compliance_audit_system.get_compliance_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Compliance summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/compliance/audit-summary')
    def compliance_audit_summary():
        """Compliance audit summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.compliance_audit import compliance_audit_system
            
            # Get query parameters
            hours = int(request.args.get('hours', 24))
            
            # Get audit summary
            summary = compliance_audit_system.get_audit_summary(hours)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Compliance audit summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/compliance/security-summary')
    def compliance_security_summary():
        """Compliance security summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.compliance_audit import compliance_audit_system
            
            # Get security summary
            summary = compliance_audit_system.get_security_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Compliance security summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/compliance/audit-log', methods=['POST'])
    def compliance_audit_log():
        """Compliance audit log API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.compliance_audit import compliance_audit_system, AuditEventType, RiskLevel
            
            # Get data from request
            data = request.json
            event_type_str = data.get('event_type', 'data_access')
            user_id = data.get('user_id', 'unknown')
            resource_accessed = data.get('resource_accessed', 'unknown')
            action_performed = data.get('action_performed', 'unknown')
            outcome = data.get('outcome', 'success')
            risk_level_str = data.get('risk_level', 'low')
            details = data.get('details', {})
            
            # Convert strings to enums
            event_type = AuditEventType(event_type_str)
            risk_level = RiskLevel(risk_level_str)
            
            # Log audit event
            correlation_id = compliance_audit_system.log_audit_event(
                event_type=event_type,
                user_id=user_id,
                resource_accessed=resource_accessed,
                action_performed=action_performed,
                outcome=outcome,
                risk_level=risk_level,
                details=details
            )
            
            return jsonify({
                'success': True,
                'correlation_id': correlation_id,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Compliance audit log error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/devops/pipeline-summary')
    def devops_pipeline_summary():
        """DevOps pipeline summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.devops_monitoring import devops_monitoring_system
            
            # Get query parameters
            hours = int(request.args.get('hours', 24))
            
            # Get pipeline summary
            summary = devops_monitoring_system.get_pipeline_summary(hours)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"DevOps pipeline summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/devops/code-quality-summary')
    def devops_code_quality_summary():
        """DevOps code quality summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.devops_monitoring import devops_monitoring_system
            
            # Get code quality summary
            summary = devops_monitoring_system.get_code_quality_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"DevOps code quality summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/devops/bug-summary')
    def devops_bug_summary():
        """DevOps bug summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.devops_monitoring import devops_monitoring_system
            
            # Get bug summary
            summary = devops_monitoring_system.get_bug_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"DevOps bug summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/devops/deployment-summary')
    def devops_deployment_summary():
        """DevOps deployment summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.devops_monitoring import devops_monitoring_system
            
            # Get query parameters
            days = int(request.args.get('days', 30))
            
            # Get deployment summary
            summary = devops_monitoring_system.get_deployment_summary(days)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"DevOps deployment summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/devops/environment-summary')
    def devops_environment_summary():
        """DevOps environment summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.devops_monitoring import devops_monitoring_system
            
            # Get environment summary
            summary = devops_monitoring_system.get_environment_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"DevOps environment summary error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/v1/advanced-ai/research-summary')
    def advanced_ai_research_summary():
        """Advanced AI research summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.advanced_ai_research import advanced_ai_research_system
            
            # Get research summary
            summary = advanced_ai_research_system.get_research_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Advanced AI research summary error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/advanced-ai/quantum-algorithms')
    def advanced_ai_quantum_algorithms():
        """Advanced AI quantum algorithms API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.advanced_ai_research import advanced_ai_research_system
            
            # Get quantum algorithms
            algorithms = advanced_ai_research_system.get_quantum_algorithms()
            return jsonify({"algorithms": algorithms})
        except Exception as e:
            logger.error(f"Advanced AI quantum algorithms error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/advanced-ai/cognitive-architectures')
    def advanced_ai_cognitive_architectures():
        """Advanced AI cognitive architectures API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.advanced_ai_research import advanced_ai_research_system
            
            # Get cognitive architectures
            architectures = advanced_ai_research_system.get_cognitive_architectures()
            return jsonify({"architectures": architectures})
        except Exception as e:
            logger.error(f"Advanced AI cognitive architectures error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/advanced-ai/neuromorphic-systems')
    def advanced_ai_neuromorphic_systems():
        """Advanced AI neuromorphic systems API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.advanced_ai_research import advanced_ai_research_system
            
            # Get neuromorphic systems
            systems = advanced_ai_research_system.get_neuromorphic_systems()
            return jsonify({"systems": systems})
        except Exception as e:
            logger.error(f"Advanced AI neuromorphic systems error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/advanced-ai/next-generation')
    def advanced_ai_next_generation():
        """Advanced AI next-generation capabilities API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.advanced_ai_research import advanced_ai_research_system
            
            # Get next-generation capabilities
            capabilities = advanced_ai_research_system.get_next_generation_capabilities()
            return jsonify(capabilities)
        except Exception as e:
            logger.error(f"Advanced AI next-generation capabilities error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/executive/kpi-summary')
    def executive_kpi_summary():
        """Executive KPI summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.executive_reporting import executive_reporting_system
            
            # Get KPI summary
            summary = executive_reporting_system.get_kpi_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Executive KPI summary error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/executive/reports')
    def executive_reports():
        """Executive reports API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.executive_reporting import executive_reporting_system
            
            # Get query parameters
            report_type = request.args.get('report_type')
            limit = int(request.args.get('limit', 10))
            
            # Get executive reports
            reports = executive_reporting_system.get_executive_reports(report_type, limit)
            return jsonify({"reports": reports})
        except Exception as e:
            logger.error(f"Executive reports error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/executive/business-intelligence')
    def executive_business_intelligence():
        """Executive business intelligence API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.executive_reporting import executive_reporting_system
            
            # Get query parameters
            category = request.args.get('category')
            impact_level = request.args.get('impact_level')
            
            # Get business intelligence
            insights = executive_reporting_system.get_business_intelligence(category, impact_level)
            return jsonify({"insights": insights})
        except Exception as e:
            logger.error(f"Executive business intelligence error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/executive/dashboard-configs')
    def executive_dashboard_configs():
        """Executive dashboard configurations API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.executive_reporting import executive_reporting_system
            
            # Get query parameters
            access_level = request.args.get('access_level')
            
            # Get dashboard configurations
            configs = executive_reporting_system.get_dashboard_configurations(access_level)
            return jsonify({"configurations": configs})
        except Exception as e:
            logger.error(f"Executive dashboard configurations error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/executive/summary')
    def executive_summary():
        """Executive summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.executive_reporting import executive_reporting_system
            
            # Get query parameters
            period_days = int(request.args.get('period_days', 30))
            
            # Generate executive summary
            summary = executive_reporting_system.generate_executive_summary(period_days)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Executive summary error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/mobile/apps')
    def mobile_apps():
        """Mobile apps API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.native_mobile_apps import native_mobile_apps_system
            
            # Get query parameters
            platform = request.args.get('platform')
            
            # Get mobile apps
            apps = native_mobile_apps_system.get_mobile_apps(platform)
            return jsonify({"apps": apps})
        except Exception as e:
            logger.error(f"Mobile apps error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/mobile/features')
    def mobile_features():
        """Mobile app features API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.native_mobile_apps import native_mobile_apps_system
            
            # Get query parameters
            platform = request.args.get('platform')
            status = request.args.get('status')
            
            # Get app features
            features = native_mobile_apps_system.get_app_features(platform, status)
            return jsonify({"features": features})
        except Exception as e:
            logger.error(f"Mobile app features error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/mobile/metrics')
    def mobile_metrics():
        """Mobile app metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.native_mobile_apps import native_mobile_apps_system
            
            # Get query parameters
            app_id = request.args.get('app_id')
            days = int(request.args.get('days', 30))
            
            # Get app metrics
            metrics = native_mobile_apps_system.get_app_metrics(app_id, days)
            return jsonify({"metrics": metrics})
        except Exception as e:
            logger.error(f"Mobile app metrics error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app('/api/v1/mobile/performance-summary')
    def mobile_performance_summary():
        """Mobile app performance summary API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.native_mobile_apps import native_mobile_apps_system
            
            # Get performance summary
            summary = native_mobile_apps_system.get_app_performance_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Mobile app performance summary error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app('/api/v1/mobile/roadmap')
    def mobile_roadmap():
        """Mobile app development roadmap API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.native_mobile_apps import native_mobile_apps_system
            
            # Get development roadmap
            roadmap = native_mobile_apps_system.get_development_roadmap()
            return jsonify(roadmap)
        except Exception as e:
            logger.error(f"Mobile app development roadmap error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/predictive/models')
    def predictive_models():
        """Predictive models API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.predictive_analytics import predictive_analytics_system
            
            # Get query parameters
            prediction_type = request.args.get('prediction_type')
            model_type = request.args.get('model_type')
            
            # Get prediction models
            models = predictive_analytics_system.get_prediction_models(prediction_type, model_type)
            return jsonify({"models": models})
        except Exception as e:
            logger.error(f"Predictive models error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/predictive/results')
    def predictive_results():
        """Predictive results API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.predictive_analytics import predictive_analytics_system
            
            # Get query parameters
            prediction_type = request.args.get('prediction_type')
            days = int(request.args.get('days', 30))
            
            # Get prediction results
            results = predictive_analytics_system.get_prediction_results(prediction_type, days)
            return jsonify({"results": results})
        except Exception as e:
            logger.error(f"Predictive results error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app('/api/v1/predictive/forecasts')
    def predictive_forecasts():
        """Predictive forecasts API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.predictive_analytics import predictive_analytics_system
            
            # Get query parameters
            forecast_type = request.args.get('forecast_type')
            
            # Get forecast data
            forecasts = predictive_analytics_system.get_forecast_data(forecast_type)
            return jsonify({"forecasts": forecasts})
        except Exception as e:
            logger.error(f"Predictive forecasts error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/predictive/accuracy')
    def predictive_accuracy():
        """Predictive accuracy metrics API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.predictive_analytics import predictive_analytics_system
            
            # Get accuracy metrics
            accuracy = predictive_analytics_system.get_prediction_accuracy_metrics()
            return jsonify(accuracy)
        except Exception as e:
            logger.error(f"Predictive accuracy metrics error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/predictive/forecast')
    def predictive_forecast():
        """Predictive business forecast API endpoint"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.predictive_analytics import predictive_analytics_system
            
            # Get query parameters
            forecast_type = request.json.get('forecast_type', 'revenue_forecast')
            months = request.json.get('months', 12)
            
            # Generate business forecast
            forecast = predictive_analytics_system.generate_business_forecast(forecast_type, months)
            return jsonify(forecast)
        except Exception as e:
            logger.error(f"Predictive business forecast error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/solutions')
    def multi_sector_solutions():
        """Multi-sector solutions API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get query parameters
            industry = request.args.get('industry')
            solution_type = request.args.get('solution_type')
            
            # Get industry solutions
            solutions = multi_sector_expansion_system.get_industry_solutions(industry, solution_type)
            return jsonify({"solutions": solutions})
        except Exception as e:
            logger.error(f"Multi-sector solutions error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/market-segments')
    def multi_sector_market_segments():
        """Multi-sector market segments API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get query parameters
            industry = request.args.get('industry')
            
            # Get market segments
            segments = multi_sector_expansion_system.get_market_segments(industry)
            return jsonify({"segments": segments})
        except Exception as e:
            logger.error(f"Multi-sector market segments error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/competitive-analysis')
    def multi_sector_competitive_analysis():
        """Multi-sector competitive analysis API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get query parameters
            industry = request.args.get('industry')
            
            # Get competitive analysis
            analysis = multi_sector_expansion_system.get_competitive_analysis(industry)
            return jsonify({"analysis": analysis})
        except Exception as e:
            logger.error(f"Multi-sector competitive analysis error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/expansion-strategies')
    def multi_sector_expansion_strategies():
        """Multi-sector expansion strategies API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get query parameters
            industry = request.args.get('industry')
            status = request.args.get('status')
            
            # Get expansion strategies
            strategies = multi_sector_expansion_system.get_expansion_strategies(industry, status)
            return jsonify({"strategies": strategies})
        except Exception as e:
            logger.error(f"Multi-sector expansion strategies error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/market-opportunities')
    def multi_sector_market_opportunities():
        """Multi-sector market opportunities analysis API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get market opportunity analysis
            analysis = multi_sector_expansion_system.get_market_opportunity_analysis()
            return jsonify(analysis)
        except Exception as e:
            logger.error(f"Multi-sector market opportunities analysis error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/multi-sector/expansion-pipeline')
    def multi_sector_expansion_pipeline():
        """Multi-sector expansion pipeline API endpoint"""
        try:
            from dashboard.multi_sector_expansion import multi_sector_expansion_system
            
            # Get expansion pipeline
            pipeline = multi_sector_expansion_system.get_expansion_pipeline()
            return jsonify(pipeline)
        except Exception as e:
            logger.error(f"Multi-sector expansion pipeline error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    # Database Management API Routes
    @app.route('/api/v1/database/backup-summary', methods=['GET'])
    def get_database_backup_summary():
        """Get database backup summary"""
        try:
            days = request.args.get('days', 30, type=int)
            summary = database_management_system.get_backup_summary(days)
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Database backup summary error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/database/maintenance-schedule', methods=['GET'])
    def get_maintenance_schedule():
        """Get maintenance schedule"""
        try:
            days = request.args.get('days', 7, type=int)
            schedule = database_management_system.get_maintenance_schedule(days)
            return jsonify(schedule)
        except Exception as e:
            logger.error(f"Maintenance schedule error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/database/start-backup', methods=['POST'])
    def start_database_backup():
        """Start database backup"""
        try:
            data = request.get_json()
            database_type = data.get('database_type')
            backup_type = data.get('backup_type')
            database_name = data.get('database_name')
            created_by = data.get('created_by', 'system')
            
            result = database_management_system.start_backup(
                database_type, backup_type, database_name, created_by
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Start database backup error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/database/backup-status/<backup_id>', methods=['GET'])
    def get_backup_status(backup_id):
        """Get backup status"""
        try:
            status = database_management_system.get_backup_status(backup_id)
            return jsonify(status)
        except Exception as e:
            logger.error(f"Backup status error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/database/start-recovery', methods=['POST'])
    def start_database_recovery():
        """Start database recovery"""
        try:
            data = request.get_json()
            backup_id = data.get('backup_id')
            target_database = data.get('target_database')
            created_by = data.get('created_by', 'system')
            
            result = database_management_system.start_recovery(
                backup_id, target_database, created_by
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Start database recovery error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    # Configuration Management API Routes
    @app.route('/api/v1/config/get', methods=['GET'])
    def get_configuration():
        """Get configuration"""
        try:
            environment = request.args.get('environment', 'production')
            config_type = request.args.get('config_type')
            key = request.args.get('key')
            
            config = configuration_manager.get_configuration(environment, config_type, key)
            return jsonify(config)
        except Exception as e:
            logger.error(f"Get configuration error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/config/set', methods=['POST'])
    def set_configuration():
        """Set configuration"""
        try:
            data = request.get_json()
            environment = data.get('environment')
            config_type = data.get('config_type')
            key = data.get('key')
            value = data.get('value')
            description = data.get('description', '')
            is_encrypted = data.get('is_encrypted', False)
            updated_by = data.get('updated_by', 'system')
            
            result = configuration_manager.set_configuration(
                environment, config_type, key, value, description, is_encrypted, updated_by
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Set configuration error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/config/templates', methods=['GET'])
    def get_config_templates():
        """Get configuration templates"""
        try:
            template_id = request.args.get('template_id')
            templates = configuration_manager.get_config_template(template_id)
            return jsonify(templates)
        except Exception as e:
            logger.error(f"Get config templates error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/config/apply-template', methods=['POST'])
    def apply_config_template():
        """Apply configuration template"""
        try:
            data = request.get_json()
            template_id = data.get('template_id')
            environment = data.get('environment')
            values = data.get('values', {})
            updated_by = data.get('updated_by', 'system')
            
            result = configuration_manager.apply_template(
                template_id, environment, values, updated_by
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Apply config template error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/config/changes', methods=['GET'])
    def get_config_changes():
        """Get configuration changes"""
        try:
            environment = request.args.get('environment')
            config_id = request.args.get('config_id')
            days = request.args.get('days', 30, type=int)
            
            changes = configuration_manager.get_config_changes(environment, config_id, days)
            return jsonify(changes)
        except Exception as e:
            logger.error(f"Get config changes error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    # Monitoring & Alerting API Routes
    @app.route('/api/v1/monitoring/alerts', methods=['GET'])
    def get_monitoring_alerts():
        """Get monitoring alerts"""
        try:
            severity = request.args.get('severity')
            status = request.args.get('status')
            hours = request.args.get('hours', 24, type=int)
            
            alerts = monitoring_alerting_system.get_alerts(severity, status, hours)
            return jsonify(alerts)
        except Exception as e:
            logger.error(f"Get monitoring alerts error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/monitoring/metrics', methods=['GET'])
    def get_monitoring_metrics():
        """Get monitoring metrics"""
        try:
            metric_type = request.args.get('metric_type')
            service_name = request.args.get('service_name')
            hours = request.args.get('hours', 1, type=int)
            
            metrics = monitoring_alerting_system.get_metrics(metric_type, service_name, hours)
            return jsonify(metrics)
        except Exception as e:
            logger.error(f"Get monitoring metrics error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/monitoring/health-status', methods=['GET'])
    def get_health_status():
        """Get health status"""
        try:
            status = monitoring_alerting_system.get_health_status()
            return jsonify(status)
        except Exception as e:
            logger.error(f"Get health status error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/monitoring/add-metric', methods=['POST'])
    def add_monitoring_metric():
        """Add monitoring metric"""
        try:
            data = request.get_json()
            metric_type = data.get('metric_type')
            value = data.get('value')
            service_name = data.get('service_name')
            host_name = data.get('host_name')
            tags = data.get('tags', {})
            
            result = monitoring_alerting_system.add_metric(
                metric_type, value, service_name, host_name, tags
            )
            return jsonify(result)
        except Exception as e:
            logger.error(f"Add monitoring metric error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/monitoring/acknowledge-alert/<alert_id>', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge alert"""
        try:
            data = request.get_json()
            acknowledged_by = data.get('acknowledged_by', 'system')
            
            result = monitoring_alerting_system.acknowledge_alert(alert_id, acknowledged_by)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Acknowledge alert error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    @app.route('/api/v1/monitoring/resolve-alert/<alert_id>', methods=['POST'])
    def resolve_alert(alert_id):
        """Resolve alert"""
        try:
            data = request.get_json()
            resolved_by = data.get('resolved_by', 'system')
            
            result = monitoring_alerting_system.resolve_alert(alert_id, resolved_by)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Resolve alert error: {e}")
            return jsonify({'error': 'internal server error'}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests, please try again later',
            'timestamp': datetime.now().isoformat()
        }), 429
    
    return app

def check_database():
    """Check database connectivity"""
    try:
        # Placeholder for database check
        return 'healthy'
    except Exception:
        return 'unhealthy'

def check_ai_models():
    """Check AI models status"""
    try:
        # Placeholder for AI models check
        return 'healthy'
    except Exception:
        return 'unhealthy'

def check_external_services():
    """Check external service connectivity"""
    try:
        # Placeholder for external services check
        return 'healthy'
    except Exception:
        return 'unhealthy'

if __name__ == '__main__':
    app = create_app()
    
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = app.config['DEBUG']
    
    # Use localhost in production, 0.0.0.0 only in development with explicit flag
    host = '127.0.0.1'  # Secure default
    if debug and os.getenv('BIND_ALL_INTERFACES', 'False').lower() == 'true':
        host = '0.0.0.0'
    
    logger.info(f"Starting Helm AI application on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
