"""
Helm AI Main Application
This is the main entry point for the Helm AI application
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import our modules
from src.api.middleware import api_middleware
from src.monitoring.health_checks import health_endpoint
from src.monitoring.structured_logging import log_manager
from src.monitoring.performance_monitor import performance_monitor

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
    
    # Enable CORS
    CORS(app, origins=['http://localhost:3000', 'https://helm-ai.com'])
    
    # Initialize middleware
    api_middleware.init_app(app)
    
    # Basic routes
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Helm AI',
            'version': '1.0.0',
            'status': 'running',
            'environment': app.config['ENVIRONMENT']
        })
    
    @app.route('/health')
    def health():
        return health_endpoint.get_health()
    
    @app.route('/health/detailed')
    def health_detailed():
        return health_endpoint.get_health(detailed=True)
    
    @app.route('/metrics')
    def metrics():
        return jsonify(performance_monitor.get_performance_summary())
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Helm AI application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
