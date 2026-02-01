#!/usr/bin/env python3
"""
Stellar Logic AI API Gateway
Centralized API gateway for unified plugin access
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import time
import hashlib
from datetime import datetime
import threading
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Configuration
GATEWAY_CONFIG = {
    'name': 'Stellar Logic AI API Gateway',
    'version': '1.0.0',
    'plugins': {
        'healthcare': {'port': 5001, 'path': '/v1/healthcare'},
        'financial': {'port': 5002, 'path': '/v1/financial'},
        'cybersecurity': {'port': 5009, 'path': '/v1/cybersecurity'},
        'gaming': {'port': 5010, 'path': '/v1/gaming'}
    }
}

# Rate limiting
rate_limiter = defaultdict(list)
RATE_LIMIT = 1000  # requests per hour

# Metrics
metrics = {
    'requests': [],
    'errors': [],
    'start_time': datetime.now()
}

def check_rate_limit(client_ip):
    """Check if client has exceeded rate limit"""
    current_time = time.time()
    
    # Clean old entries (older than 1 hour)
    rate_limiter[client_ip] = [
        req_time for req_time in rate_limiter[client_ip]
        if current_time - req_time < 3600
    ]
    
    # Check limit
    if len(rate_limiter[client_ip]) >= RATE_LIMIT:
        return False
    
    rate_limiter[client_ip].append(current_time)
    return True

def record_request(method, path, status, duration, client_ip):
    """Record request metrics"""
    metrics['requests'].append({
        'method': method,
        'path': path,
        'status': status,
        'duration': duration,
        'client_ip': client_ip,
        'timestamp': datetime.now().isoformat()
    })

def record_error(method, path, error):
    """Record error metrics"""
    metrics['errors'].append({
        'method': method,
        'path': path,
        'error': str(error),
        'timestamp': datetime.now().isoformat()
    })

def proxy_to_plugin(plugin_name, path, data=None):
    """Proxy request to plugin server"""
    try:
        plugin_config = GATEWAY_CONFIG['plugins'][plugin_name]
        plugin_url = f"http://localhost:{plugin_config['port']}{plugin_config['path']}{path}"
        
        if data:
            response = requests.post(plugin_url, json=data, timeout=10)
        else:
            response = requests.get(plugin_url, timeout=10)
        
        return response.json(), response.status_code
    except Exception as e:
        return {'error': f"Plugin {plugin_name} unavailable: {str(e)}"}, 500

# Main endpoints
@app.route('/')
def root():
    return jsonify({
        'name': GATEWAY_CONFIG['name'],
        'version': GATEWAY_CONFIG['version'],
        'status': 'running',
        'plugins': list(GATEWAY_CONFIG['plugins'].keys()),
        'endpoints': {
            'health': '/health',
            'metrics': '/metrics',
            'plugins': '/v1/{plugin}'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': GATEWAY_CONFIG['name'],
        'version': GATEWAY_CONFIG['version'],
        'plugins': len(GATEWAY_CONFIG['plugins']),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/metrics')
def metrics_endpoint():
    total_requests = len(metrics['requests'])
    total_errors = len(metrics['errors'])
    successful_requests = total_requests - total_errors
    
    if metrics['requests']:
        avg_duration = sum(req['duration'] for req in metrics['requests']) / len(metrics['requests'])
    else:
        avg_duration = 0
    
    return jsonify({
        'uptime': str(datetime.now() - metrics['start_time']),
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'total_errors': total_errors,
        'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0,
        'average_response_time': avg_duration,
        'timestamp': datetime.now().isoformat()
    })

# Plugin endpoints
@app.route('/v1/<plugin_name>/health')
def plugin_health(plugin_name):
    if plugin_name not in GATEWAY_CONFIG['plugins']:
        return jsonify({'error': 'Plugin not found'}), 404
    
    result, status = proxy_to_plugin(plugin_name, '/health')
    return jsonify(result), status

@app.route('/v1/<plugin_name>/analyze', methods=['POST'])
def plugin_analyze(plugin_name):
    if plugin_name not in GATEWAY_CONFIG['plugins']:
        return jsonify({'error': 'Plugin not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status = proxy_to_plugin(plugin_name, '/analyze', data)
    
    # Add gateway metadata
    if isinstance(result, dict):
        result['gateway_metadata'] = {
            'processed_by': 'api_gateway',
            'plugin': plugin_name,
            'timestamp': datetime.now().isoformat()
        }
    
    return jsonify(result), status

@app.route('/v1/<plugin_name>/status')
def plugin_status(plugin_name):
    if plugin_name not in GATEWAY_CONFIG['plugins']:
        return jsonify({'error': 'Plugin not found'}), 404
    
    result, status = proxy_to_plugin(plugin_name, '/api/v1/status')
    
    # Add gateway metadata
    if isinstance(result, dict):
        result['gateway_metadata'] = {
            'plugin': plugin_name,
            'gateway_timestamp': datetime.now().isoformat()
        }
    
    return jsonify(result), status

@app.route('/v1/<plugin_name>/info')
def plugin_info(plugin_name):
    if plugin_name not in GATEWAY_CONFIG['plugins']:
        return jsonify({'error': 'Plugin not found'}), 404
    
    result, status = proxy_to_plugin(plugin_name, '/api/v1/status')
    
    # Add gateway metadata
    if isinstance(result, dict):
        result['gateway_metadata'] = {
            'plugin': plugin_name,
            'gateway_timestamp': datetime.now().isoformat()
        }
    
    return jsonify(result), status

# Middleware for rate limiting and logging
@app.before_request
def before_request():
    client_ip = request.remote_addr
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        return jsonify({
            'error': 'Rate limit exceeded',
            'limit': RATE_LIMIT,
            'timestamp': datetime.now().isoformat()
        }), 429

@app.after_request
def after_request(response):
    # Record metrics
    duration = time.time() - getattr(request, 'start_time', time.time())
    record_request(
        request.method,
        request.path,
        response.status_code,
        duration,
        request.remote_addr
    )
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    record_error(request.method, request.path, e)
    return jsonify({
        'error': str(e),
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Stellar Logic AI API Gateway...")
    print(f"📊 Plugins: {list(GATEWAY_CONFIG['plugins'].keys())}")
    print(f"🌐 Server: http://localhost:8080")
    print(f"📊 Health: http://localhost:8080/health")
    print(f"📈 Metrics: http://localhost:8080/metrics")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
