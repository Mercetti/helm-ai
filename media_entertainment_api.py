"""
🎬 MEDIA & ENTERTAINMENT SECURITY API
Stellar Logic AI - Media Content Protection RESTful API

RESTful API for content piracy detection, copyright protection, digital rights management,
and entertainment industry compliance with comprehensive monitoring and analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import json
import random
from typing import Dict, Any, List
import statistics

# Import the media entertainment plugin
from media_entertainment_plugin import MediaEntertainmentPlugin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize media entertainment plugin
media_plugin = MediaEntertainmentPlugin()

# Global data storage
media_alerts = []
content_profiles = {}
violation_records = {}
market_data = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Media & Entertainment Security API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'ai_core_status': media_plugin.get_ai_core_status()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/media/analyze', methods=['POST'])
def analyze_media_event():
    """Analyze media security event"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No event data provided'}), 400
        
        # Process the media event
        adapted_data = media_plugin.adapt_media_data(data)
        threat_analysis = media_plugin.analyze_media_threat(adapted_data)
        
        if threat_analysis.get('threat_detected', False):
            # Generate alert
            alert = media_plugin.generate_media_alert(adapted_data, threat_analysis)
            
            if alert:
                # Convert to dict for JSON response
                alert_dict = {
                    'alert_id': alert.alert_id,
                    'content_id': alert.content_id,
                    'content_type': alert.content_type.value,
                    'threat_type': alert.threat_type.value,
                    'severity': alert.severity.value,
                    'confidence_score': alert.confidence_score,
                    'timestamp': alert.timestamp.isoformat(),
                    'detection_method': alert.detection_method,
                    'content_data': alert.content_data,
                    'violation_data': alert.violation_data,
                    'risk_assessment': alert.risk_assessment,
                    'recommended_action': alert.recommended_action,
                    'compliance_implications': alert.compliance_implications
                }
                
                # Store alert
                media_alerts.append(alert_dict)
                
                return jsonify({
                    'status': 'alert_generated',
                    'alert': alert_dict,
                    'threat_analysis': threat_analysis
                })
        
        else:
            return jsonify({
                'status': 'no_alert',
                'message': 'No media security threats detected',
                'threat_analysis': threat_analysis
            })
    
    except Exception as e:
        logger.error(f"Error analyzing media event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/dashboard', methods=['GET'])
def get_media_dashboard():
    """Get media dashboard data"""
    try:
        # Get metrics from plugin
        metrics = media_plugin.get_media_metrics()
        compliance = media_plugin.get_compliance_status()
        market = media_plugin.get_market_analysis()
        
        # Get recent alerts
        recent_alerts = sorted(media_alerts, 
                                key=lambda x: x['timestamp'], 
                                reverse=True)[:10]
        
        return jsonify({
            'metrics': metrics,
            'compliance': compliance,
            'market_analysis': market,
            'recent_alerts': recent_alerts,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/alerts', methods=['GET'])
def get_media_alerts():
    """Get media security alerts"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        threat_type = request.args.get('threat_type', None)
        severity = request.args.get('severity', None)
        content_type = request.args.get('content_type', None)
        
        # Filter alerts
        filtered_alerts = media_alerts
        
        if threat_type:
            filtered_alerts = [a for a in filtered_alerts if threat_type.lower() in a['threat_type'].lower()]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if severity.lower() in a['severity'].lower()]
        
        if content_type:
            filtered_alerts = [a for a in filtered_alerts if content_type.lower() in a['content_type'].lower()]
        
        # Sort by timestamp (most recent first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        filtered_alerts = filtered_alerts[:limit]
        
        return jsonify({
            'alerts': filtered_alerts,
            'total_count': len(filtered_alerts),
            'filter_applied': {
                'threat_type': threat_type,
                'severity': severity,
                'content_type': content_type
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/content', methods=['GET'])
def get_content_status():
    """Get content monitoring status"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        risk_level = request.args.get('risk_level', None)
        content_type = request.args.get('content_type', None)
        
        # Filter content
        filtered_content = []
        for content_id, profile in content_profiles.items():
            if risk_level and profile.get('risk_score', 0) < 0.5:
                continue
            if content_type and content_type.lower() not in content_id.lower():
                continue
            filtered_content.append({
                'content_id': content_id,
                'risk_score': profile.get('risk_score', 0),
                'violations': len(profile.get('violations', [])),
                'last_activity': profile.get('last_activity', ''),
                'status': profile.get('status', 'active')
            })
        
        # Sort by risk score (highest first)
        filtered_content.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Limit results
        filtered_content = filtered_content[:limit]
        
        return jsonify({
            'content': filtered_content,
            'total_count': len(filtered_content),
            'filter_applied': {
                'risk_level': risk_level,
                'content_type': content_type
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting content status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/violations', methods=['GET'])
def get_violation_monitoring():
    """Get violation monitoring status"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status', None)
        violation_type = request.args.get('violation_type', None)
        
        # Filter violations
        filtered_violations = []
        for violation_id, record in violation_records.items():
            if status and record.get('status') != status:
                continue
            if violation_type and violation_type.lower() not in violation_id.lower():
                continue
            
            filtered_violations.append({
                'violation_id': violation_id,
                'content_id': record.get('content_id', ''),
                'violation_type': record.get('violation_type', ''),
                'status': record.get('status', 'pending'),
                'risk_score': record.get('risk_score', 0),
                'detection_method': record.get('detection_method', ''),
                'timestamp': record.get('timestamp', ''),
                'action_taken': record.get('action_taken', '')
            })
        
        # Sort by timestamp (most recent first)
        filtered_violations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        filtered_violations = filtered_violations[:limit]
        
        return jsonify({
            'violations': filtered_violations,
            'total_count': len(filtered_violations),
            'filter_applied': {
                'status': status,
                'violation_type': violation_type
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting violation monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/threat-types', methods=['GET'])
def get_threat_type_analysis():
    """Get threat type analysis"""
    try:
        # Calculate threat type distribution
        threat_type_counts = {}
        threat_type_severity = {}
        
        for alert in media_alerts:
            threat_type = alert['threat_type']
            severity = alert['severity']
            
            threat_type_counts[threat_type] = threat_type_counts.get(threat_type, 0) + 1
            
            if threat_type not in threat_type_severity:
                threat_type_severity[threat_type] = []
            threat_type_severity[threat_type].append(severity)
        
        # Calculate statistics for each threat type
        threat_type_stats = {}
        for threat_type, count in threat_type_counts.items():
            severities = threat_type_severity.get(threat_type, [])
            avg_confidence = statistics.mean([a['confidence_score'] for a in media_alerts if a['threat_type'] == threat_type]) if media_alerts else 0
            
            threat_type_stats[threat_type] = {
                'total_cases': count,
                'severity_distribution': {
                    'critical': severities.count('critical'),
                    'high': severities.count('high'),
                    'medium': severities.count('medium'),
                    'low': severities.count('low'),
                    'informational': severities.count('informational')
                },
                'average_confidence': avg_confidence,
                'trend': 'stable'
            }
        
        return jsonify({
            'threat_type_distribution': threat_type_counts,
            'threat_type_statistics': threat_type_stats,
            'total_threat_cases': sum(threat_type_counts.values()),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting threat type analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/compliance', methods=['GET'])
def get_compliance_status():
    """Get compliance status"""
    try:
        compliance = media_plugin.get_compliance_status()
        
        return jsonify(compliance)
    
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/market-analysis', methods=['GET'])
def get_market_analysis():
    """Get market analysis"""
    try:
        market = media_plugin.get_market_analysis()
        
        return jsonify(market)
    
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/statistics', methods=['GET'])
def get_comprehensive_statistics():
    """Get comprehensive statistics"""
    try:
        # Get all metrics
        metrics = media_plugin.get_media_metrics()
        compliance = media_plugin.get_compliance_status()
        market = media_plugin.get_market_analysis()
        
        # Calculate comprehensive statistics
        stats = {
            'platform_overview': {
                'total_content_analyzed': metrics.get('total_content_analyzed', 0),
                'total_violations_detected': metrics.get('total_violations_detected', 0),
                'alerts_generated': metrics.get('alerts_generated', 0),
                'threats_detected': metrics.get('threats_detected', 0),
                'processing_capacity': metrics.get('processing_capacity', 0),
                'uptime_percentage': metrics.get('uptime_percentage', 0),
                'ai_core_connected': media_plugin.ai_core_connected
            },
            'performance_metrics': {
                'average_response_time': metrics.get('average_response_time', 0),
                'accuracy_score': metrics.get('accuracy_score', 0),
                'false_positive_rate': metrics.get('false_positive_rate', 0),
                'processing_latency': metrics.get('processing_latency', 0)
            },
            'business_metrics': {
                'total_market_value': market.get('total_market_value', 0),
                'piracy_detection_rate': 0.03,
                'average_content_value': market.get('average_content_value', 0),
                'high_risk_content': len([c for c in content_profiles.values() if c.get('risk_score', 0) > 0.7]),
                'market_trends': market.get('market_trends', {}),
                'content_type_analysis': market.get('content_type_analysis', {})
            },
            'compliance_metrics': {
                'overall_status': compliance.get('overall_compliance_status', 'unknown'),
                'compliance_score': compliance.get('compliance_score', 0),
                'frameworks_compliant': len([f for f in compliance.get('compliance_frameworks', {}).values() if f.get('status') == 'compliant']),
                'total_frameworks': len(compliance.get('compliance_frameworks', {})),
                'high_severity_alerts': compliance.get('high_severity_alerts', 0)
            },
            'alert_analytics': {
                'total_alerts': len(media_alerts),
                'alerts_by_severity': {
                    'critical': len([a for a in media_alerts if a['severity'] == 'critical']),
                    'high': len([a for a in media_alerts if a['severity'] == 'high']),
                    'medium': len([a for a in media_alerts if a['severity'] == 'medium']),
                    'low': len([a for a in media_alerts if a['severity'] == 'low']),
                    'informational': len([a for a in media_alerts if a['severity'] == 'informational'])
                },
                'alerts_by_threat_type': threat_type_counts,
                'average_confidence': statistics.mean([a['confidence_score'] for a in media_alerts]) if media_alerts else 0,
                'recent_alerts': len([a for a in media_alerts if (datetime.now() - datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) < timedelta(hours=24)])
            }
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting comprehensive statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Media & Entertainment Security API on port 5008")
    app.run(host='0.0.0.0', port=5008, debug=True)
