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
except ImportError:
    # Create placeholder modules if they don't exist yet
    api_middleware = None
    health_endpoint = None
    log_manager = None
    performance_monitor = None

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
