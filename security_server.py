#!/usr/bin/env python3
"""
Stellar Logic AI - Security & Compliance Server
Advanced security monitoring and compliance management
"""

import sqlite3
import json
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import re

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityComplianceEngine:
    def __init__(self, db_path="security_compliance.db"):
        self.db_path = db_path
        self.init_database()
        
        # Security patterns
        self.sensitive_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit cards
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
        ]
        
        # Compliance rules
        self.compliance_rules = {
            'data_retention_days': 2555,  # 7 years
            'session_timeout_minutes': 30,
            'max_login_attempts': 5,
            'password_min_length': 12,
            'require_2fa': True
        }
    
    def init_database(self):
        """Initialize security and compliance database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Security events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Compliance audits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_type TEXT NOT NULL,
                compliance_rule TEXT NOT NULL,
                status TEXT NOT NULL,
                findings TEXT,
                remediation TEXT,
                auditor TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Data access logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                access_type TEXT NOT NULL,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_token TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Encryption keys
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT NOT NULL,
                key_value TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_security_event(self, event_type, severity, user_id=None, ip_address=None, user_agent=None, event_data=None):
        """Log security event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events (event_type, severity, user_id, ip_address, user_agent, event_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, severity, user_id, ip_address, user_agent, json.dumps(event_data) if event_data else None))
        
        conn.commit()
        conn.close()
        
        # Auto-resolve low severity events
        if severity == 'low':
            self.resolve_security_event(event_type, user_id)
    
    def detect_sensitive_data(self, text):
        """Detect sensitive data in text"""
        detected = []
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, text)
            if matches:
                detected.append({
                    'pattern': pattern,
                    'matches': matches,
                    'count': len(matches)
                })
        return detected
    
    def sanitize_data(self, text):
        """Sanitize sensitive data"""
        sanitized = text
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        return sanitized
    
    def log_data_access(self, user_id, resource_type, resource_id, access_type, ip_address=None):
        """Log data access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_access_logs (user_id, resource_type, resource_id, access_type, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, resource_type, resource_id, access_type, ip_address))
        
        conn.commit()
        conn.close()
    
    def create_user_session(self, user_id, ip_address, user_agent):
        """Create user session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate session token
        session_token = hmac.new(
            b'stellar-logic-secret',
            f"{user_id}{time.time()}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Calculate expiry
        expires_at = datetime.now() + timedelta(minutes=self.compliance_rules['session_timeout_minutes'])
        
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_token, ip_address, user_agent, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def validate_session(self, session_token, ip_address=None):
        """Validate user session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, expires_at, is_active FROM user_sessions 
            WHERE session_token = ? AND is_active = TRUE
        ''', (session_token,))
        
        result = cursor.fetchone()
        
        if result:
            user_id, expires_at, is_active = result
            
            # Check expiry
            if datetime.now() > datetime.fromisoformat(expires_at):
                # Session expired
                cursor.execute('''
                    UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?
                ''', (session_token,))
                conn.commit()
                conn.close()
                return False
            
            # Update last activity
            cursor.execute('''
                UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = ?
            ''', (session_token,))
            conn.commit()
            conn.close()
            
            return True, user_id
        else:
            conn.close()
            return False
    
    def get_security_dashboard(self):
        """Get security dashboard data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recent security events
        cursor.execute('''
            SELECT event_type, severity, COUNT(*) as count
            FROM security_events 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY event_type, severity
            ORDER BY count DESC
        ''')
        recent_events = cursor.fetchall()
        
        # Active sessions
        cursor.execute('''
            SELECT COUNT(*) FROM user_sessions 
            WHERE is_active = TRUE AND expires_at > datetime('now')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        # Compliance status
        cursor.execute('''
            SELECT audit_type, status, COUNT(*) as count
            FROM compliance_audits 
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY audit_type, status
        ''')
        compliance_status = cursor.fetchall()
        
        # Data access trends
        cursor.execute('''
            SELECT resource_type, access_type, COUNT(*) as count
            FROM data_access_logs 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY resource_type, access_type
            ORDER BY count DESC
            LIMIT 10
        ''')
        access_trends = cursor.fetchall()
        
        conn.close()
        
        return {
            'recent_events': [
                {'type': row[0], 'severity': row[1], 'count': row[2]}
                for row in recent_events
            ],
            'active_sessions': active_sessions,
            'compliance_status': [
                {'audit': row[0], 'status': row[1], 'count': row[2]}
                for row in compliance_status
            ],
            'access_trends': [
                {'resource': row[0], 'access_type': row[1], 'count': row[2]}
                for row in access_trends
            ]
        }
    
    def run_compliance_check(self):
        """Run automated compliance check"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check data retention
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(self.compliance_rules['data_retention_days']))
        
        old_records = cursor.fetchone()[0]
        
        # Check session timeouts
        cursor.execute('''
            SELECT COUNT(*) FROM user_sessions 
            WHERE expires_at < datetime('now') AND is_active = TRUE
        ''')
        
        expired_sessions = cursor.fetchone()[0]
        
        # Log compliance audit
        cursor.execute('''
            INSERT INTO compliance_audits (audit_type, compliance_rule, status, findings)
            VALUES (?, ?, ?, ?)
        ''', ('automated', 'data_retention', 'pass' if old_records == 0 else 'fail', 
              f'Old records: {old_records}'))
        
        cursor.execute('''
            INSERT INTO compliance_audits (audit_type, compliance_rule, status, findings)
            VALUES (?, ?, ?, ?)
        ''', ('automated', 'session_timeout', 'pass' if expired_sessions == 0 else 'fail',
              f'Expired sessions: {expired_sessions}'))
        
        conn.commit()
        conn.close()
        
        return {
            'data_retention_status': 'pass' if old_records == 0 else 'fail',
            'old_records_count': old_records,
            'session_timeout_status': 'pass' if expired_sessions == 0 else 'fail',
            'expired_sessions_count': expired_sessions
        }
    
    def resolve_security_event(self, event_type, user_id=None):
        """Resolve security event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                UPDATE security_events SET resolved = TRUE 
                WHERE event_type = ? AND user_id = ?
            ''', (event_type, user_id))
        else:
            cursor.execute('''
                UPDATE security_events SET resolved = TRUE 
                WHERE event_type = ?
            ''', (event_type,))
        
        conn.commit()
        conn.close()

# Initialize security engine
security = SecurityComplianceEngine()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'security_server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/security/dashboard', methods=['GET'])
def get_security_dashboard():
    """Get security dashboard data"""
    dashboard = security.get_security_dashboard()
    return jsonify(dashboard)

@app.route('/api/security/event', methods=['POST'])
def log_security_event():
    """Log security event"""
    data = request.get_json()
    event_type = data.get('event_type')
    severity = data.get('severity')
    user_id = data.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    event_data = data.get('event_data')
    
    security.log_security_event(event_type, severity, user_id, ip_address, user_agent, event_data)
    return jsonify({'success': True})

@app.route('/api/security/scan-data', methods=['POST'])
def scan_sensitive_data():
    """Scan for sensitive data"""
    data = request.get_json()
    text = data.get('text', '')
    
    detected = security.detect_sensitive_data(text)
    sanitized = security.sanitize_data(text)
    
    return jsonify({
        'detected': detected,
        'sanitized': sanitized,
        'has_sensitive': len(detected) > 0
    })

@app.route('/api/security/compliance-check', methods=['POST'])
def run_compliance_check():
    """Run compliance check"""
    results = security.run_compliance_check()
    return jsonify(results)

@app.route('/api/security/session/create', methods=['POST'])
def create_session():
    """Create user session"""
    data = request.get_json()
    user_id = data.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    session_token = security.create_user_session(user_id, ip_address, user_agent)
    
    return jsonify({
        'session_token': session_token,
        'expires_in': security.compliance_rules['session_timeout_minutes'] * 60
    })

@app.route('/api/security/session/validate', methods=['POST'])
def validate_session():
    """Validate user session"""
    data = request.get_json()
    session_token = data.get('session_token')
    ip_address = request.remote_addr
    
    result = security.validate_session(session_token, ip_address)
    
    if result:
        return jsonify({'valid': True, 'user_id': result[1]})
    else:
        return jsonify({'valid': False})

@app.route('/api/security/access-log', methods=['POST'])
def log_access():
    """Log data access"""
    data = request.get_json()
    user_id = data.get('user_id')
    resource_type = data.get('resource_type')
    resource_id = data.get('resource_id')
    access_type = data.get('access_type')
    ip_address = request.remote_addr
    
    security.log_data_access(user_id, resource_type, resource_id, access_type, ip_address)
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🔒 Starting Security & Compliance Server...")
    print("🛡️ Advanced security monitoring ready!")
    print("📋 Compliance management active!")
    print("🔐 Available at: http://localhost:5007")
    app.run(host='0.0.0.0', port=5007, debug=False)
