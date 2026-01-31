"""
🏢 REAL ESTATE & PROPERTY SECURITY API
Stellar Logic AI - Real Estate Security RESTful API

RESTful API for property fraud detection, title verification, transaction security,
and real estate industry compliance with comprehensive monitoring and analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import json
import random
from typing import Dict, Any, List
import statistics

# Import the real estate plugin
from real_estate_plugin import RealEstatePlugin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize real estate plugin
real_estate_plugin = RealEstatePlugin()

# Global data storage
real_estate_alerts = []
property_profiles = {}
transaction_records = {}
market_data = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Real Estate & Property Security API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'ai_core_status': real_estate_plugin.get_ai_core_status()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/real-estate/analyze', methods=['POST'])
def analyze_real_estate_event():
    """Analyze real estate security event"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No event data provided'}), 400
        
        # Process the real estate event
        adapted_data = real_estate_plugin.adapt_real_estate_data(data)
        threat_analysis = real_estate_plugin.analyze_real_estate_threat(adapted_data)
        
        if threat_analysis.get('threat_detected', False):
            # Generate alert
            alert = real_estate_plugin.generate_real_estate_alert(adapted_data, threat_analysis)
            
            if alert:
                # Convert to dict for JSON response
                alert_dict = {
                    'alert_id': alert.alert_id,
                    'property_id': alert.property_id,
                    'property_type': alert.property_type.value,
                    'fraud_type': alert.fraud_type.value,
                    'severity': alert.severity.value,
                    'confidence_score': alert.confidence_score,
                    'timestamp': alert.timestamp.isoformat(),
                    'detection_method': alert.detection_method,
                    'property_data': alert.property_data,
                    'transaction_data': alert.transaction_data,
                    'risk_assessment': alert.risk_assessment,
                    'recommended_action': alert.recommended_action,
                    'compliance_implications': alert.compliance_implications
                }
                
                # Store alert
                real_estate_alerts.append(alert_dict)
                
                return jsonify({
                    'status': 'alert_generated',
                    'alert': alert_dict,
                    'threat_analysis': threat_analysis
                })
        
        else:
            return jsonify({
                'status': 'no_alert',
                'message': 'No real estate security threats detected',
                'threat_analysis': threat_analysis
            })
    
    except Exception as e:
        logger.error(f"Error analyzing real estate event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/dashboard', methods=['GET'])
def get_real_estate_dashboard():
    """Get real estate dashboard data"""
    try:
        # Get metrics from plugin
        metrics = real_estate_plugin.get_property_metrics()
        compliance = real_estate_plugin.get_compliance_status()
        market = real_estate_plugin.get_market_analysis()
        
        # Get recent alerts
        recent_alerts = sorted(real_estate_alerts, 
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

@app.route('/api/real-estate/alerts', methods=['GET'])
def get_real_estate_alerts():
    """Get real estate security alerts"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        fraud_type = request.args.get('fraud_type', None)
        severity = request.args.get('severity', None)
        property_type = request.args.get('property_type', None)
        
        # Filter alerts
        filtered_alerts = real_estate_alerts
        
        if fraud_type:
            filtered_alerts = [a for a in filtered_alerts if fraud_type.lower() in a['fraud_type'].lower()]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if severity.lower() in a['severity'].lower()]
        
        if property_type:
            filtered_alerts = [a for a in filtered_alerts if property_type.lower() in a['property_type'].lower()]
        
        # Sort by timestamp (most recent first)
        filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        filtered_alerts = filtered_alerts[:limit]
        
        return jsonify({
            'alerts': filtered_alerts,
            'total_count': len(filtered_alerts),
            'filter_applied': {
                'fraud_type': fraud_type,
                'severity': severity,
                'property_type': property_type
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/properties', methods=['GET'])
def get_properties_status():
    """Get properties monitoring status"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        risk_level = request.args.get('risk_level', None)
        property_type = request.args.get('property_type', None)
        
        # Filter properties
        filtered_properties = []
        for prop_id, profile in property_profiles.items():
            if risk_level and profile.get('risk_score', 0) < 0.5:
                continue
            if property_type and property_type.lower() not in prop_id.lower():
                continue
            filtered_properties.append({
                'property_id': prop_id,
                'risk_score': profile.get('risk_score', 0),
                'incidents': len(profile.get('incidents', [])),
                'last_activity': profile.get('last_activity', ''),
                'status': profile.get('status', 'active')
            })
        
        # Sort by risk score (highest first)
        filtered_properties.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Limit results
        filtered_properties = filtered_properties[:limit]
        
        return jsonify({
            'properties': filtered_properties,
            'total_count': len(filtered_properties),
            'filter_applied': {
                'risk_level': risk_level,
                'property_type': property_type
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting properties status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/transactions', methods=['GET'])
def get_transaction_monitoring():
    """Get transaction monitoring status"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status', None)
        amount_range = request.args.get('amount_range', None)
        
        # Filter transactions
        filtered_transactions = []
        for trans_id, record in transaction_records.items():
            if status and record.get('status') != status:
                continue
            if amount_range:
                amount = record.get('amount', 0)
                if amount_range == 'low' and amount > 100000:
                    continue
                elif amount_range == 'medium' and (amount < 100000 or amount > 500000):
                    continue
                elif amount_range == 'high' and amount < 500000:
                    continue
            
            filtered_transactions.append({
                'transaction_id': trans_id,
                'amount': record.get('amount', 0),
                'status': record.get('status', 'pending'),
                'risk_score': record.get('risk_score', 0),
                'fraud_indicators': record.get('fraud_indicators', []),
                'timestamp': record.get('timestamp', ''),
                'buyer_id': record.get('buyer_id', ''),
                'seller_id': record.get('seller_id', '')
            })
        
        # Sort by timestamp (most recent first)
        filtered_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        filtered_transactions = filtered_transactions[:limit]
        
        return jsonify({
            'transactions': filtered_transactions,
            'total_count': len(filtered_transactions),
            'filter_applied': {
                'status': status,
                'amount_range': amount_range
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting transaction monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/fraud-types', methods=['GET'])
def get_fraud_type_analysis():
    """Get fraud type analysis"""
    try:
        # Calculate fraud type distribution
        fraud_type_counts = {}
        fraud_type_severity = {}
        
        for alert in real_estate_alerts:
            fraud_type = alert['fraud_type']
            severity = alert['severity']
            
            fraud_type_counts[fraud_type] = fraud_type_counts.get(fraud_type, 0) + 1
            
            if fraud_type not in fraud_type_severity:
                fraud_type_severity[fraud_type] = []
            fraud_type_severity[fraud_type].append(severity)
        
        # Calculate statistics for each fraud type
        fraud_type_stats = {}
        for fraud_type, count in fraud_type_counts.items():
            severities = fraud_type_severity.get(fraud_type, [])
            avg_confidence = statistics.mean([a['confidence_score'] for a in real_estate_alerts if a['fraud_type'] == fraud_type]) if real_estate_alerts else 0
            
            fraud_type_stats[fraud_type] = {
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
            'fraud_type_distribution': fraud_type_counts,
            'fraud_type_statistics': fraud_type_stats,
            'total_fraud_cases': sum(fraud_type_counts.values()),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting fraud type analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/compliance', methods=['GET'])
def get_compliance_status():
    """Get compliance status"""
    try:
        compliance = real_estate_plugin.get_compliance_status()
        
        return jsonify(compliance)
    
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/market-analysis', methods=['GET'])
def get_market_analysis():
    """Get market analysis"""
    try:
        market = real_estate_plugin.get_market_analysis()
        
        return jsonify(market)
    
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/real-estate/statistics', methods=['GET'])
def get_comprehensive_statistics():
    """Get comprehensive statistics"""
    try:
        # Get all metrics
        metrics = real_estate_plugin.get_property_metrics()
        compliance = real_estate_plugin.get_compliance_status()
        market = real_estate_plugin.get_market_analysis()
        
        # Calculate comprehensive statistics
        stats = {
            'platform_overview': {
                'total_properties_analyzed': metrics.get('total_properties_analyzed', 0),
                'total_transactions_monitored': metrics.get('total_transactions_monitored', 0),
                'alerts_generated': metrics.get('alerts_generated', 0),
                'threats_detected': metrics.get('threats_detected', 0),
                'processing_capacity': metrics.get('processing_capacity', 0),
                'uptime_percentage': metrics.get('uptime_percentage', 0),
                'ai_core_connected': real_estate_plugin.ai_core_connected
            },
            'performance_metrics': {
                'average_response_time': metrics.get('average_response_time', 0),
                'accuracy_score': metrics.get('accuracy_score', 0),
                'false_positive_rate': metrics.get('false_positive_rate', 0),
                'processing_latency': metrics.get('processing_latency', 0)
            },
            'business_metrics': {
                'total_market_value': market.get('total_market_value', 0),
                'fraud_detection_rate': 0.02,
                'average_property_value': market.get('average_property_value', 0),
                'high_risk_properties': len([p for p in property_profiles.values() if p.get('risk_score', 0) > 0.7]),
                'market_coverage': market.get('market_trends', {}),
                'regional_analysis': market.get('regional_analysis', {})
            },
            'compliance_metrics': {
                'overall_status': compliance.get('overall_compliance_status', 'unknown'),
                'compliance_score': compliance.get('compliance_score', 0),
                'frameworks_compliant': len([f for f in compliance.get('compliance_frameworks', {}).values() if f.get('status') == 'compliant']),
                'total_frameworks': len(compliance.get('compliance_frameworks', {})),
                'high_severity_alerts': compliance.get('high_severity_alerts', 0)
            },
            'alert_analytics': {
                'total_alerts': len(real_estate_alerts),
                'alerts_by_severity': {
                    'critical': len([a for a in real_estate_alerts if a['severity'] == 'critical']),
                    'high': len([a for a in real_estate_alerts if a['severity'] == 'high']),
                    'medium': len([a for a in real_estate_alerts if a['severity'] == 'medium']),
                    'low': len([a for a in real_estate_alerts if a['severity'] == 'low']),
                    'informational': len([a for a in real_estate_alerts if a['severity'] == 'informational'])
                },
                'alerts_by_fraud_type': fraud_type_counts,
                'average_confidence': statistics.mean([a['confidence_score'] for a in real_estate_alerts]) if real_estate_alerts else 0,
                'recent_alerts': len([a for a in real_estate_alerts if (datetime.now() - datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) < timedelta(hours=24)])
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
    logger.info("Starting Real Estate & Property Security API on port 5007")
    app.run(host='0.0.0.0', port=5007, debug=True)
