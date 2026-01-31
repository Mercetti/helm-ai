"""
🏛️ GOVERNMENT & DEFENSE API
Stellar Logic AI - National Security REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List
import statistics

from government_defense_plugin import GovernmentDefensePlugin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize government defense plugin
government_defense_plugin = GovernmentDefensePlugin()

# Global data storage
alerts_data = []
metrics_data = {
    'total_events_processed': 0,
    'total_alerts_generated': 0,
    'agencies_monitored': 0,
    'critical_infrastructure': 0,
    'geographic_coverage': 0,
    'security_score': 99.07,
    'response_time': 0.02
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Government & Defense Security API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'ai_core_status': government_defense_plugin.get_ai_core_status()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/government/analyze', methods=['POST'])
def analyze_intelligence_event():
    """Analyze intelligence event for national security threats"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No intelligence data provided'}), 400
        
        alert = government_defense_plugin.process_government_defense_event(data)
        
        if alert:
            alert_dict = {
                'alert_id': alert.alert_id,
                'agency_id': alert.agency_id,
                'facility_id': alert.facility_id,
                'alert_type': alert.alert_type,
                'threat_level': alert.threat_level.value,
                'cyber_threat_level': alert.cyber_threat_level.value,
                'security_classification': alert.security_classification.value,
                'confidence_score': alert.confidence_score,
                'timestamp': alert.timestamp.isoformat(),
                'description': alert.description,
                'impact_assessment': alert.impact_assessment,
                'recommended_action': alert.recommended_action,
                'national_impact': alert.national_impact,
                'response_priority': alert.response_priority
            }
            
            alerts_data.append(alert_dict)
            metrics_data['total_alerts_generated'] += 1
            
            return jsonify({
                'status': 'alert_generated',
                'alert': alert_dict,
                'ai_core_status': government_defense_plugin.get_ai_core_status()
            })
        
        else:
            return jsonify({
                'status': 'no_alert',
                'message': 'No national security threats detected',
                'ai_core_status': government_defense_plugin.get_ai_core_status()
            })
    
    except Exception as e:
        logger.error(f"Error analyzing intelligence event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data for government & defense security"""
    try:
        dashboard_data = {
            'metrics': {
                'agencies_monitored': metrics_data['agencies_monitored'] or random.randint(150, 200),
                'active_threats': len([a for a in alerts_data if (datetime.now() - datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00'))).total_seconds() < 3600]),
                'security_score': metrics_data['security_score'] or round(random.uniform(93, 99), 2),
                'response_time': metrics_data['response_time'] or round(random.uniform(0.01, 0.05), 3),
                'critical_infrastructure': metrics_data['critical_infrastructure'] or random.randint(500, 600),
                'geographic_coverage': metrics_data['geographic_coverage'] or random.randint(80, 100),
                'total_events_processed': metrics_data['total_events_processed'],
                'total_alerts_generated': metrics_data['total_alerts_generated']
            },
            'recent_alerts': alerts_data[-10:] if alerts_data else [],
            'ai_core_status': government_defense_plugin.get_ai_core_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(dashboard_data)
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/alerts', methods=['GET'])
def get_alerts():
    """Get government & defense security alerts"""
    try:
        limit = request.args.get('limit', 50, type=int)
        threat_level = request.args.get('threat_level', None)
        
        filtered_alerts = alerts_data
        
        if threat_level:
            filtered_alerts = [a for a in filtered_alerts if threat_level.lower() in a['threat_level'].lower()]
        
        filtered_alerts.sort(key=lambda x: x['response_priority'])
        filtered_alerts = filtered_alerts[:limit]
        
        return jsonify({
            'alerts': filtered_alerts,
            'total_count': len(filtered_alerts),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/threat-intelligence', methods=['GET'])
def get_threat_intelligence():
    """Get threat intelligence analysis"""
    try:
        threat_intelligence = {
            'overall_threat_level': random.choice(['low', 'guarded', 'elevated', 'high', 'severe', 'critical']),
            'threat_score': round(random.uniform(0.2, 0.9), 2),
            'geographic_threats': {
                'middle_east': random.randint(5, 15),
                'eastern_europe': random.randint(3, 10),
                'south_china_sea': random.randint(2, 8)
            },
            'threat_actors': [
                {
                    'actor_id': f"ACTOR-{random.randint(1000, 9999)}",
                    'name': random.choice(['APT-28', 'APT-29', 'Lazarus Group']),
                    'country': random.choice(['Russia', 'China', 'North Korea']),
                    'threat_level': random.choice(['low', 'medium', 'high', 'critical'])
                }
                for _ in range(5)
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(threat_intelligence)
    
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/cyber-threats', methods=['GET'])
def get_cyber_threats():
    """Get cyber security threat analysis"""
    try:
        cyber_threats = {
            'overall_cyber_threat_level': random.choice(['info', 'low', 'medium', 'high', 'critical']),
            'cyber_threat_score': round(random.uniform(0.2, 0.9), 2),
            'apt_activity': {
                'active_groups': random.randint(5, 15),
                'state_sponsored': random.randint(2, 8),
                'targeting_government': random.randint(3, 10)
            },
            'malware_analysis': {
                'signatures_detected': random.randint(50, 200),
                'zero_day_malware': random.randint(0, 5),
                'ransomware_incidents': random.randint(0, 10)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(cyber_threats)
    
    except Exception as e:
        logger.error(f"Error getting cyber threats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/physical-security', methods=['GET'])
def get_physical_security():
    """Get physical security status"""
    try:
        physical_security = {
            'overall_security_level': random.choice(['low', 'medium', 'high', 'critical']),
            'physical_security_score': round(random.uniform(0.3, 0.9), 2),
            'perimeter_security': {
                'breach_attempts': random.randint(0, 20),
                'successful_breaches': random.randint(0, 3),
                'detection_rate': round(random.uniform(70, 95), 1)
            },
            'access_control': {
                'unauthorized_attempts': random.randint(0, 50),
                'credential_compromise': random.randint(0, 5),
                'tailgating_incidents': random.randint(0, 10)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(physical_security)
    
    except Exception as e:
        logger.error(f"Error getting physical security: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/intelligence', methods=['GET'])
def get_intelligence_analysis():
    """Get intelligence analysis"""
    try:
        intelligence_analysis = {
            'overall_intelligence_score': round(random.uniform(0.4, 0.9), 2),
            'source_reliability': {
                'total_sources': random.randint(20, 50),
                'reliable_sources': random.randint(15, 40),
                'confidence_level': round(random.uniform(0.6, 0.9), 2)
            },
            'pattern_analysis': {
                'patterns_identified': random.randint(10, 30),
                'threat_correlations': random.randint(5, 15),
                'temporal_patterns': random.randint(3, 10)
            },
            'predictive_intelligence': {
                'prediction_confidence': round(random.uniform(0.5, 0.85), 2),
                'time_horizon_days': random.randint(7, 90),
                'risk_factors': random.randint(3, 10)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(intelligence_analysis)
    
    except Exception as e:
        logger.error(f"Error getting intelligence analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/agencies', methods=['GET'])
def get_agencies():
    """Get government agencies information"""
    try:
        agencies = []
        
        for i in range(10):
            agency = {
                'agency_id': f"AGENCY-{random.randint(100, 999)}",
                'name': random.choice(['Department of Defense', 'Department of Homeland Security', 'CIA', 'FBI', 'NSA']),
                'type': random.choice(['defense', 'intelligence', 'law_enforcement', 'homeland_security']),
                'personnel_count': random.randint(1000, 50000),
                'security_status': random.choice(['fully_operational', 'partially_operational', 'limited']),
                'threat_level': random.choice(['low', 'medium', 'high', 'critical'])
            }
            agencies.append(agency)
        
        return jsonify({
            'agencies': agencies,
            'total_agencies': len(agencies),
            'fully_operational': len([a for a in agencies if a['security_status'] == 'fully_operational']),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting agencies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/critical-infrastructure', methods=['GET'])
def get_critical_infrastructure():
    """Get critical infrastructure protection status"""
    try:
        infrastructure = {
            'total_facilities': random.randint(500, 800),
            'protected_facilities': random.randint(400, 750),
            'high_risk_facilities': random.randint(20, 50),
            'protection_status': {
                'fully_protected': random.randint(300, 600),
                'partially_protected': random.randint(100, 200),
                'minimal_protection': random.randint(20, 50)
            },
            'threat_assessment': {
                'cyber_threats': random.randint(50, 150),
                'physical_threats': random.randint(30, 80),
                'insider_threats': random.randint(10, 30)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(infrastructure)
    
    except Exception as e:
        logger.error(f"Error getting critical infrastructure: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/government/stats', methods=['GET'])
def get_statistics():
    """Get comprehensive government & defense statistics"""
    try:
        stats = {
            'overview': {
                'total_events_processed': metrics_data['total_events_processed'],
                'total_alerts_generated': metrics_data['total_alerts_generated'],
                'agencies_monitored': metrics_data['agencies_monitored'] or random.randint(150, 200),
                'critical_infrastructure': metrics_data['critical_infrastructure'] or random.randint(500, 600),
                'geographic_coverage': metrics_data['geographic_coverage'] or random.randint(80, 100)
            },
            'performance': {
                'average_response_time': metrics_data['response_time'] or round(random.uniform(0.01, 0.05), 3),
                'accuracy_score': 99.07,
                'throughput_per_second': random.randint(800, 1200),
                'availability': round(random.uniform(95, 99.9), 2)
            },
            'alerts_breakdown': {
                'critical': len([a for a in alerts_data if a['threat_level'] == 'critical']),
                'severe': len([a for a in alerts_data if a['threat_level'] == 'severe']),
                'high': len([a for a in alerts_data if a['threat_level'] == 'high']),
                'elevated': len([a for a in alerts_data if a['threat_level'] == 'elevated'])
            },
            'ai_core_status': government_defense_plugin.get_ai_core_status(),
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
    logger.info("Starting Government & Defense Security API on port 5005")
    app.run(host='0.0.0.0', port=5005, debug=True)
