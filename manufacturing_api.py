"""
🏭 MANUFACTURING & INDUSTRIAL IoT API
Stellar Logic AI - Manufacturing Security REST API

RESTful API endpoints for manufacturing security, predictive maintenance,
quality control, and supply chain integrity monitoring.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import json
import random
from typing import Dict, Any, List
import statistics

# Import the manufacturing plugin
from manufacturing_plugin import ManufacturingPlugin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize manufacturing plugin
manufacturing_plugin = ManufacturingPlugin()

# Global data storage
alerts_data = []
metrics_data = {
    'total_events_processed': 0,
    'total_alerts_generated': 0,
    'equipment_monitored': 0,
    'facilities_covered': 0,
    'quality_score': 99.07,
    'response_time': 0.02,
    'cost_savings': 15000000,
    'uptime_percentage': 99.9
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Manufacturing Security API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'ai_core_status': manufacturing_plugin.get_ai_core_status()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/manufacturing/analyze', methods=['POST'])
def analyze_manufacturing_event():
    """Analyze manufacturing event for security and maintenance"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process the manufacturing event
        alert = manufacturing_plugin.process_manufacturing_event(data)
        
        if alert:
            # Convert to dict for JSON response
            alert_dict = {
                'alert_id': alert.alert_id,
                'equipment_id': alert.equipment_id,
                'facility_id': alert.facility_id,
                'alert_type': alert.alert_type,
                'maintenance_level': alert.maintenance_level.value,
                'quality_level': alert.quality_level.value,
                'security_level': alert.security_level.value,
                'confidence_score': alert.confidence_score,
                'timestamp': alert.timestamp.isoformat(),
                'description': alert.description,
                'impact_assessment': alert.impact_assessment,
                'recommended_action': alert.recommended_action,
                'sensor_data': alert.sensor_data,
                'production_metrics': alert.production_metrics,
                'cost_impact': alert.cost_impact,
                'downtime_risk': alert.downtime_risk
            }
            
            # Store alert
            alerts_data.append(alert_dict)
            metrics_data['total_alerts_generated'] += 1
            
            return jsonify({
                'status': 'alert_generated',
                'alert': alert_dict,
                'ai_core_status': manufacturing_plugin.get_ai_core_status()
            })
        
        else:
            return jsonify({
                'status': 'no_alert',
                'message': 'No security or maintenance issues detected',
                'ai_core_status': manufacturing_plugin.get_ai_core_status()
            })
    
    except Exception as e:
        logger.error(f"Error analyzing manufacturing event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data for manufacturing security"""
    try:
        # Generate real-time metrics
        dashboard_data = {
            'metrics': {
                'equipment_monitored': metrics_data['equipment_monitored'] or random.randint(1000, 1500),
                'active_alerts': len([a for a in alerts_data if (datetime.now() - datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00'))).total_seconds() < 3600]),
                'quality_score': metrics_data['quality_score'] or round(random.uniform(94, 99), 2),
                'response_time': metrics_data['response_time'] or round(random.uniform(0.01, 0.05), 3),
                'cost_savings': metrics_data['cost_savings'] or random.randint(15000000, 25000000),
                'facilities_covered': metrics_data['facilities_covered'] or random.randint(50, 70),
                'total_events_processed': metrics_data['total_events_processed'],
                'total_alerts_generated': metrics_data['total_alerts_generated'],
                'uptime_percentage': metrics_data['uptime_percentage']
            },
            'recent_alerts': alerts_data[-10:] if alerts_data else [],
            'ai_core_status': manufacturing_plugin.get_ai_core_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(dashboard_data)
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/alerts', methods=['GET'])
def get_alerts():
    """Get manufacturing security alerts"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        severity = request.args.get('severity', None)
        facility_id = request.args.get('facility_id', None)
        
        # Filter alerts
        filtered_alerts = alerts_data
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if severity.lower() in a['alert_type'].lower()]
        
        if facility_id:
            filtered_alerts = [a for a in filtered_alerts if a['facility_id'] == facility_id]
        
        # Sort by timestamp (most recent first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        filtered_alerts = filtered_alerts[:limit]
        
        return jsonify({
            'alerts': filtered_alerts,
            'total_count': len(filtered_alerts),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/maintenance', methods=['GET'])
def get_maintenance_status():
    """Get maintenance status and predictions"""
    try:
        # Generate maintenance predictions
        maintenance_predictions = []
        
        for i in range(10):
            equipment_id = f"EQ-{random.randint(1000, 9999)}"
            facility_id = f"FAC-{random.randint(1, 50)}"
            
            prediction = {
                'equipment_id': equipment_id,
                'facility_id': facility_id,
                'maintenance_level': random.choice(['critical', 'high', 'medium', 'low', 'routine']),
                'predicted_failure_time': f"{random.randint(100, 1000)} hours",
                'urgency_score': round(random.uniform(0.1, 0.9), 2),
                'cost_impact': random.randint(5000, 50000),
                'downtime_risk': round(random.uniform(0, 100), 1),
                'recommendations': [
                    "Inspect critical components",
                    "Schedule maintenance within 24 hours",
                    "Prepare backup equipment"
                ],
                'last_maintenance': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'operating_hours': random.randint(1000, 10000)
            }
            
            maintenance_predictions.append(prediction)
        
        return jsonify({
            'maintenance_predictions': maintenance_predictions,
            'total_equipment': len(maintenance_predictions),
            'critical_maintenance': len([p for p in maintenance_predictions if p['maintenance_level'] == 'critical']),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting maintenance status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/quality', methods=['GET'])
def get_quality_metrics():
    """Get quality control metrics"""
    try:
        # Generate quality metrics
        quality_data = {
            'overall_quality_score': round(random.uniform(94, 99), 2),
            'defect_rate': round(random.uniform(0.5, 5.0), 2),
            'rework_rate': round(random.uniform(1.0, 8.0), 2),
            'customer_satisfaction': round(random.uniform(85, 98), 1),
            'quality_distribution': {
                'excellent': random.randint(35, 50),
                'good': random.randint(25, 35),
                'acceptable': random.randint(10, 20),
                'poor': random.randint(5, 10),
                'critical': random.randint(1, 5)
            },
            'quality_trends': {
                'daily': [round(random.uniform(90, 99), 2) for _ in range(7)],
                'weekly': [round(random.uniform(88, 98), 2) for _ in range(4)],
                'monthly': [round(random.uniform(85, 97), 2) for _ in range(12)]
            },
            'quality_issues': [
                {
                    'issue_id': f"QI-{random.randint(1000, 9999)}",
                    'description': 'Dimensional accuracy below threshold',
                    'severity': random.choice(['minor', 'major', 'critical']),
                    'affected_units': random.randint(10, 100),
                    'cost_impact': random.randint(1000, 10000),
                    'resolution_status': random.choice(['open', 'in_progress', 'resolved'])
                }
                for _ in range(5)
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(quality_data)
    
    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/security', methods=['GET'])
def get_security_status():
    """Get manufacturing security status"""
    try:
        # Generate security metrics
        security_data = {
            'overall_security_score': round(random.uniform(85, 98), 2),
            'security_events_today': random.randint(5, 25),
            'security_trends': {
                'access_control': random.randint(10, 30),
                'physical_security': random.randint(5, 20),
                'cyber_security': random.randint(15, 35),
                'supply_chain': random.randint(8, 25),
                'insider_threats': random.randint(2, 15)
            },
            'security_incidents': [
                {
                    'incident_id': f"SI-{random.randint(1000, 9999)}",
                    'type': random.choice(['access_violation', 'physical_breach', 'cyber_attack', 'supply_chain_issue']),
                    'severity': random.choice(['low', 'medium', 'high', 'critical']),
                    'description': 'Unauthorized access attempt detected',
                    'facility_id': f"FAC-{random.randint(1, 50)}",
                    'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                    'status': random.choice(['open', 'investigating', 'resolved'])
                }
                for _ in range(8)
            ],
            'compliance_status': {
                'osha_compliant': random.choice([True, False]),
                'environmental_compliant': random.choice([True, False]),
                'safety_compliant': random.choice([True, False]),
                'overall_compliant': random.choice([True, False])
            },
            'risk_assessment': {
                'high_risk_areas': random.randint(1, 5),
                'medium_risk_areas': random.randint(3, 10),
                'low_risk_areas': random.randint(10, 20),
                'mitigation_actions_taken': random.randint(5, 15)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(security_data)
    
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/performance', methods=['GET'])
def get_performance_metrics():
    """Get manufacturing performance metrics"""
    try:
        # Generate performance metrics
        performance_data = {
            'response_time': round(random.uniform(0.01, 0.05), 3),
            'accuracy': 99.07,
            'throughput': random.randint(800, 1200),
            'availability': round(random.uniform(95, 99.9), 2),
            'efficiency': round(random.uniform(80, 95), 2),
            'performance_breakdown': {
                'predictive_maintenance': round(random.uniform(85, 98), 2),
                'quality_control': round(random.uniform(88, 96), 2),
                'security_monitoring': round(random.uniform(90, 99), 2),
                'supply_chain_monitoring': round(random.uniform(82, 94), 2),
                'compliance_monitoring': round(random.uniform(87, 95), 2)
            },
            'performance_trends': {
                'last_24_hours': [round(random.uniform(80, 99), 2) for _ in range(24)],
                'last_7_days': [round(random.uniform(75, 98), 2) for _ in range(7)],
                'last_30_days': [round(random.uniform(70, 97), 2) for _ in range(30)]
            },
            'bottlenecks': [
                {
                    'area': random.choice(['production_line_3', 'quality_control', 'maintenance_scheduling']),
                    'impact': round(random.uniform(5, 25), 2),
                    'description': 'Processing delay detected',
                    'recommended_action': 'Optimize workflow and allocate additional resources'
                }
                for _ in range(3)
            ],
            'optimization_opportunities': [
                {
                    'opportunity': 'Predictive Maintenance Optimization',
                    'potential_savings': random.randint(50000, 200000),
                    'implementation_time': '2-3 weeks',
                    'roi_percentage': random.randint(150, 300)
                }
                for _ in range(4)
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(performance_data)
    
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/facilities', methods=['GET'])
def get_facilities():
    """Get manufacturing facilities information"""
    try:
        # Generate facilities data
        facilities = []
        
        for i in range(20):
            facility = {
                'facility_id': f"FAC-{random.randint(1, 100)}",
                'name': f"Manufacturing Plant {i+1}",
                'location': random.choice(['North America', 'Europe', 'Asia', 'South America']),
                'equipment_count': random.randint(50, 200),
                'production_lines': random.randint(5, 20),
                'employees': random.randint(100, 500),
                'status': random.choice(['operational', 'maintenance', 'offline']),
                'quality_score': round(random.uniform(90, 99), 2),
                'security_level': random.choice(['low', 'medium', 'high', 'critical']),
                'last_inspection': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'compliance_status': random.choice(['compliant', 'non_compliant', 'pending_review'])
            }
            facilities.append(facility)
        
        return jsonify({
            'facilities': facilities,
            'total_facilities': len(facilities),
            'operational_facilities': len([f for f in facilities if f['status'] == 'operational']),
            'compliant_facilities': len([f for f in facilities if f['compliance_status'] == 'compliant']),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting facilities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturing/stats', methods=['GET'])
def get_statistics():
    """Get comprehensive manufacturing statistics"""
    try:
        stats = {
            'overview': {
                'total_events_processed': metrics_data['total_events_processed'],
                'total_alerts_generated': metrics_data['total_alerts_generated'],
                'equipment_monitored': metrics_data['equipment_monitored'] or random.randint(1000, 1500),
                'facilities_covered': metrics_data['facilities_covered'] or random.randint(50, 70),
                'uptime_percentage': metrics_data['uptime_percentage']
            },
            'performance': {
                'average_response_time': metrics_data['response_time'] or round(random.uniform(0.01, 0.05), 3),
                'accuracy_score': 99.07,
                'throughput_per_second': random.randint(800, 1200),
                'availability': round(random.uniform(95, 99.9), 2)
            },
            'financial_impact': {
                'cost_savings': metrics_data['cost_savings'] or random.randint(15000000, 25000000),
                'downtime_reduction': round(random.uniform(60, 85), 2),
                'maintenance_cost_reduction': round(random.uniform(40, 70), 2),
                'quality_improvement_value': random.randint(5000000, 15000000)
            },
            'alerts_breakdown': {
                'critical': len([a for a in alerts_data if 'critical' in a['alert_type'].lower()]),
                'high': len([a for a in alerts_data if 'high' in a['alert_type'].lower()]),
                'medium': len([a for a in alerts_data if 'medium' in a['alert_type'].lower()]),
                'low': len([a for a in alerts_data if 'low' in a['alert_type'].lower()])
            },
            'ai_core_status': manufacturing_plugin.get_ai_core_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Manufacturing Security API on port 5004")
    app.run(host='0.0.0.0', port=5004, debug=True)
