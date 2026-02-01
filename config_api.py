#!/usr/bin/env python3
"""
Stellar Logic AI Configuration API
REST API for configuration management
"""

from flask import Flask, request, jsonify
from config_manager import config_manager
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/api/v1/config', methods=['GET'])
def list_all_configs():
    """List all configurations"""
    return jsonify({
        'status': 'success',
        'data': config_manager.list_configs(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/config/<config_type>', methods=['GET'])
def list_configs(config_type):
    """List configurations by type"""
    configs = config_manager.list_configs(config_type)
    return jsonify({
        'status': 'success',
        'data': configs,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/config/<config_type>/<config_name>', methods=['GET'])
def get_config(config_type, config_name):
    """Get specific configuration"""
    config = config_manager.get_config(config_type, config_name)
    
    if config is None:
        return jsonify({
            'status': 'error',
            'message': 'Configuration not found',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': config,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/config/<config_type>/<config_name>', methods=['POST'])
def set_config(config_type, config_name):
    """Set configuration value"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    success = config_manager.set_config(config_type, config_name, data)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Configuration updated',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to update configuration',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/config/<config_type>/<config_name>/reload', methods=['POST'])
def reload_config(config_type, config_name):
    """Reload configuration from file"""
    success = config_manager.reload_config(config_type, config_name)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Configuration reloaded',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to reload configuration',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/config/<config_type>/<config_name>', methods=['DELETE'])
def delete_config(config_type, config_name):
    """Delete configuration"""
    success = config_manager.delete_config(config_type, config_name)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Configuration deleted',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete configuration',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Configuration API',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Configuration API Server...")
    print("📊 Available endpoints:")
    print("  GET /api/v1/config - List all configs")
    print("  GET /api/v1/config/<type> - List configs by type")
    print("  GET /api/v1/config/<type>/<name> - Get config")
    print("  POST /api/v1/config/<type>/<name> - Set config")
    print("  POST /api/v1/config/<type>/<name>/reload - Reload config")
    print("  DELETE /api/v1/config/<type>/<name> - Delete config")
    
    app.run(host='0.0.0.0', port=8081, debug=False)
