"""
Stellar Logic AI - API Documentation Generator
Comprehensive API documentation for all plugins and endpoints
"""

from flask import Flask, Blueprint, jsonify
from flask_restx import Api, Resource, fields, Namespace
import inspect
import glob
from typing import Dict, List, Any
from datetime import datetime

class APIDocumentationGenerator:
    """Generate comprehensive API documentation for Stellar Logic AI"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(
            self.app, 
            version='1.0', 
            title='Stellar Logic AI API',
            description='Comprehensive AI Security Platform API Documentation',
            doc='/api/docs/'
        )
        self.endpoints = []
        self.models = []
        self.examples = []
        
    def generate_plugin_documentation(self) -> Dict[str, Any]:
        """Generate documentation for all plugins"""
        docs = {
            'title': 'Stellar Logic AI API Documentation',
            'version': '1.0.0',
            'description': 'Comprehensive AI Security Platform API',
            'generated_at': datetime.now().isoformat(),
            'endpoints': {},
            'models': {},
            'examples': {},
            'authentication': {
                'type': 'API Key',
                'header': 'X-API-Key',
                'description': 'API key for authentication',
                'example': 'Bearer your-api-key-here'
            }
        }
        
        # Generate documentation for each plugin
        plugin_files = glob.glob('*_plugin.py')
        for plugin_file in plugin_files:
            plugin_name = plugin_file.replace('_plugin.py', '')
            docs['endpoints'][plugin_name] = self._generate_plugin_endpoints(plugin_name)
            docs['models'][plugin_name] = self._generate_plugin_models(plugin_name)
            docs['examples'][plugin_name] = self._generate_plugin_examples(plugin_name)
        
        return docs
    
    def _generate_plugin_endpoints(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Generate endpoint documentation for a plugin"""
        endpoints = [
            {
                'path': f'/api/v1/{plugin_name}/health',
                'method': 'GET',
                'description': f'Health check endpoint for {plugin_name} plugin',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': 'Success',
                        'schema': {
                            'status': 'string',
                            'timestamp': 'string',
                            'plugin': plugin_name
                        }
                    }
                }
            },
            {
                'path': f'/api/v1/{plugin_name}/analyze',
                'method': 'POST',
                'description': f'Analyze security event using {plugin_name} plugin',
                'parameters': [
                    {
                        'name': 'event_data',
                        'in': 'body',
                        'required': True,
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'event_id': {'type': 'string'},
                                'timestamp': {'type': 'string'},
                                'source': {'type': 'string'},
                                'data': {'type': 'object'}
                            }
                        }
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Analysis complete',
                        'schema': {
                            'status': 'string',
                            'threat_level': 'string',
                            'confidence': 'number',
                            'recommendations': ['string']
                        }
                    }
                }
            },
            {
                'path': f'/api/v1/{plugin_name}/dashboard',
                'method': 'GET',
                'description': f'Get dashboard data for {plugin_name} plugin',
                'parameters': [
                    {
                        'name': 'time_range',
                        'in': 'query',
                        'required': False,
                        'type': 'string',
                        'enum': ['1h', '24h', '7d', '30d']
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Dashboard data',
                        'schema': {
                            'metrics': 'object',
                            'alerts': ['object'],
                            'trends': 'object'
                        }
                    }
                }
            }
        ]
        
        return endpoints
    
    def _generate_plugin_models(self, plugin_name: str) -> Dict[str, Any]:
        """Generate data models for a plugin"""
        return {
            'Event': {
                'type': 'object',
                'properties': {
                    'event_id': {'type': 'string', 'description': 'Unique event identifier'},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'description': 'Event timestamp'},
                    'source': {'type': 'string', 'description': 'Event source'},
                    'event_type': {'type': 'string', 'description': 'Type of event'},
                    'severity': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
                    'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
                    'data': {'type': 'object', 'description': 'Event-specific data'}
                },
                'required': ['event_id', 'timestamp', 'source', 'event_type']
            },
            'Alert': {
                'type': 'object',
                'properties': {
                    'alert_id': {'type': 'string', 'description': 'Unique alert identifier'},
                    'event_id': {'type': 'string', 'description': 'Related event ID'},
                    'severity': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
                    'threat_type': {'type': 'string', 'description': 'Type of threat detected'},
                    'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
                    'description': {'type': 'string', 'description': 'Alert description'},
                    'recommendations': {'type': 'array', 'items': {'type': 'string'}},
                    'timestamp': {'type': 'string', 'format': 'date-time'}
                },
                'required': ['alert_id', 'event_id', 'severity', 'threat_type']
            },
            'DashboardMetrics': {
                'type': 'object',
                'properties': {
                    'total_events': {'type': 'integer', 'description': 'Total events processed'},
                    'alerts_generated': {'type': 'integer', 'description': 'Total alerts generated'},
                    'threats_detected': {'type': 'integer', 'description': 'Total threats detected'},
                    'accuracy_score': {'type': 'number', 'minimum': 0, 'maximum': 1},
                    'average_response_time': {'type': 'number', 'description': 'Average response time in ms'},
                    'uptime_percentage': {'type': 'number', 'minimum': 0, 'maximum': 100}
                }
            }
        }
    
    def _generate_plugin_examples(self, plugin_name: str) -> Dict[str, Any]:
        """Generate usage examples for a plugin"""
        return {
            'python_client': f'''
import requests

# Initialize client
base_url = "https://api.stellarlogic.ai/v1/{plugin_name}"
headers = {{
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}}

# Health check
response = requests.get(f"{{base_url}}/health", headers=headers)
print(response.json())

# Analyze event
event_data = {{
    "event_id": "example-001",
    "timestamp": "2026-01-31T09:30:00Z",
    "source": "security_monitor",
    "event_type": "suspicious_activity",
    "severity": "medium",
    "confidence": 0.85,
    "data": {{
        "user_id": "user123",
        "action": "login_attempt",
        "ip_address": "192.168.1.1"
    }}
}}

response = requests.post(f"{{base_url}}/analyze", 
                        json=event_data, 
                        headers=headers)
print(response.json())
''',
            'javascript_client': f'''
const axios = require('axios');

// Initialize client
const baseURL = 'https://api.stellarlogic.ai/v1/{plugin_name}';
const headers = {{
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
}};

// Health check
axios.get(`${{baseURL}}/health`, {{ headers }})
    .then(response => console.log(response.data))
    .catch(error => console.error(error));

// Analyze event
const eventData = {{
    event_id: 'example-001',
    timestamp: '2026-01-31T09:30:00Z',
    source: 'security_monitor',
    event_type: 'suspicious_activity',
    severity: 'medium',
    confidence: 0.85,
    data: {{
        user_id: 'user123',
        action: 'login_attempt',
        ip_address: '192.168.1.1'
    }}
}};

axios.post(`${{baseURL}}/analyze`, eventData, {{ headers }})
    .then(response => console.log(response.data))
    .catch(error => console.error(error));
''',
            'curl_commands': f'''
# Health check
curl -X GET "https://api.stellarlogic.ai/v1/{plugin_name}/health" \\
     -H "X-API-Key: your-api-key-here" \\
     -H "Content-Type: application/json"

# Analyze event
curl -X POST "https://api.stellarlogic.ai/v1/{plugin_name}/analyze" \\
     -H "X-API-Key: your-api-key-here" \\
     -H "Content-Type: application/json" \\
     -d '{{
         "event_id": "example-001",
         "timestamp": "2026-01-31T09:30:00Z",
         "source": "security_monitor",
         "event_type": "suspicious_activity",
         "severity": "medium",
         "confidence": 0.85,
         "data": {{
             "user_id": "user123",
             "action": "login_attempt",
             "ip_address": "192.168.1.1"
         }}
     }}'
'''
        }
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'Stellar Logic AI API',
                'version': '1.0.0',
                'description': 'Comprehensive AI Security Platform API',
                'contact': {
                    'name': 'Stellar Logic AI Support',
                    'email': 'support@stellarlogic.ai',
                    'url': 'https://stellarlogic.ai/support'
                },
                'license': {
                    'name': 'MIT',
                    'url': 'https://opensource.org/licenses/MIT'
                }
            },
            'servers': [
                {
                    'url': 'https://api.stellarlogic.ai/v1',
                    'description': 'Production server'
                },
                {
                    'url': 'https://staging-api.stellarlogic.ai/v1',
                    'description': 'Staging server'
                }
            ],
            'security': [
                {
                    'ApiKeyAuth': []
                }
            ],
            'components': {
                'securitySchemes': {
                    'ApiKeyAuth': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key',
                        'description': 'API key for authentication'
                    }
                },
                'schemas': {
                    'Event': {
                        'type': 'object',
                        'required': ['event_id', 'timestamp', 'source', 'event_type'],
                        'properties': {
                            'event_id': {'type': 'string', 'description': 'Unique event identifier'},
                            'timestamp': {'type': 'string', 'format': 'date-time'},
                            'source': {'type': 'string'},
                            'event_type': {'type': 'string'},
                            'severity': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
                            'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
                            'data': {'type': 'object'}
                        }
                    },
                    'Alert': {
                        'type': 'object',
                        'required': ['alert_id', 'event_id', 'severity', 'threat_type'],
                        'properties': {
                            'alert_id': {'type': 'string'},
                            'event_id': {'type': 'string'},
                            'severity': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
                            'threat_type': {'type': 'string'},
                            'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
                            'description': {'type': 'string'},
                            'recommendations': {'type': 'array', 'items': {'type': 'string'}},
                            'timestamp': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            },
            'paths': {
                '/health': {
                    'get': {
                        'summary': 'Health check',
                        'description': 'Check API health status',
                        'responses': {
                            '200': {
                                'description': 'Success',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'status': {'type': 'string'},
                                                'timestamp': {'type': 'string'},
                                                'version': {'type': 'string'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def save_documentation(self, output_file: str = 'API_DOCUMENTATION.md') -> None:
        """Save documentation to markdown file"""
        docs = self.generate_plugin_documentation()
        
        with open(output_file, 'w') as f:
            f.write(f"# {docs['title']}\n\n")
            f.write(f"**Version:** {docs['version']}\n")
            f.write(f"**Generated:** {docs['generated_at']}\n\n")
            f.write(f"{docs['description']}\n\n")
            
            # Authentication
            f.write("## Authentication\n\n")
            f.write(f"**Type:** {docs['authentication']['type']}\n")
            f.write(f"**Header:** `{docs['authentication']['header']}`\n")
            f.write(f"**Example:** `{docs['authentication']['example']}`\n\n")
            
            # Endpoints
            f.write("## Endpoints\n\n")
            for plugin_name, endpoints in docs['endpoints'].items():
                f.write(f"### {plugin_name.title()}\n\n")
                for endpoint in endpoints:
                    f.write(f"#### {endpoint['method']} {endpoint['path']}\n\n")
                    f.write(f"{endpoint['description']}\n\n")
                    
                    if endpoint['parameters']:
                        f.write("**Parameters:**\n\n")
                        for param in endpoint['parameters']:
                            f.write(f"- `{param['name']}` ({param.get('in', 'query')})")
                            if param.get('required'):
                                f.write(" **Required**")
                            f.write(f"\n  - {param.get('description', '')}\n")
                        f.write("\n")
                    
                    f.write("**Responses:**\n\n")
                    for status, response in endpoint['responses'].items():
                        f.write(f"- **{status}**: {response['description']}\n")
                    f.write("\n")
            
            # Models
            f.write("## Data Models\n\n")
            for plugin_name, models in docs['models'].items():
                f.write(f"### {plugin_name.title()} Models\n\n")
                for model_name, model_schema in models.items():
                    f.write(f"#### {model_name}\n\n")
                    f.write(f"**Type:** {model_schema['type']}\n\n")
                    
                    if 'properties' in model_schema:
                        f.write("**Properties:**\n\n")
                        for prop_name, prop_schema in model_schema['properties'].items():
                            f.write(f"- `{prop_name}` ({prop_schema['type']})")
                            if prop_name in model_schema.get('required', []):
                                f.write(" **Required**")
                            if 'description' in prop_schema:
                                f.write(f" - {prop_schema['description']}")
                            f.write("\n")
                        f.write("\n")
            
            # Examples
            f.write("## Usage Examples\n\n")
            for plugin_name, examples in docs['examples'].items():
                f.write(f"### {plugin_name.title()}\n\n")
                for example_name, example_code in examples.items():
                    f.write(f"#### {example_name.replace('_', ' ').title()}\n\n")
                    f.write("```python\n" if 'python' in example_name else "")
                    f.write("```javascript\n" if 'javascript' in example_name else "")
                    f.write("```bash\n" if 'curl' in example_name else "")
                    f.write(f"{example_code.strip()}\n")
                    f.write("```\n\n")

# Generate documentation
if __name__ == "__main__":
    doc_generator = APIDocumentationGenerator()
    doc_generator.save_documentation()
    
    # Also generate OpenAPI spec
    openapi_spec = doc_generator.generate_openapi_spec()
    import json
    with open('openapi_spec.json', 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    
    print("✅ API Documentation generated successfully!")
    print("📄 API_DOCUMENTATION.md - Complete API documentation")
    print("📄 openapi_spec.json - OpenAPI 3.0 specification")
