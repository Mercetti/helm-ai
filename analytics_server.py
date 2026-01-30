#!/usr/bin/env python3
"""
Stellar Logic AI - Analytics & Intelligence Server
Real-time business analytics and platform intelligence
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self, db_path="analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                ip_address TEXT
            )
        ''')
        
        # Feature usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                session_duration INTEGER
            )
        ''')
        
        # Performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                server_name TEXT
            )
        ''')
        
        # Business intelligence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                prompt TEXT,
                response_length INTEGER,
                response_time REAL,
                satisfaction_score INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def track_user_activity(self, user_id, activity_type, activity_data=None, session_id=None, ip_address=None):
        """Track user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (user_id, activity_type, activity_data, session_id, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, activity_type, json.dumps(activity_data) if activity_data else None, session_id, ip_address))
        
        conn.commit()
        conn.close()
    
    def track_feature_usage(self, feature_name, user_id, session_duration=None):
        """Track feature usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if feature exists for this user
        cursor.execute('''
            SELECT id, usage_count FROM feature_usage 
            WHERE feature_name = ? AND user_id = ?
        ''', (feature_name, user_id))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing
            cursor.execute('''
                UPDATE feature_usage 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP, session_duration = ?
                WHERE id = ?
            ''', (session_duration, result[0]))
        else:
            # Create new
            cursor.execute('''
                INSERT INTO feature_usage (feature_name, user_id, session_duration)
                VALUES (?, ?, ?)
            ''', (feature_name, user_id, session_duration))
        
        conn.commit()
        conn.close()
    
    def get_real_time_metrics(self):
        """Get real-time platform metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Active users (last 5 minutes)
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM user_activity 
            WHERE timestamp > datetime('now', '-5 minutes')
        ''')
        active_users = cursor.fetchone()[0]
        
        # Total users today
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM user_activity 
            WHERE date(timestamp) = date('now')
        ''')
        daily_users = cursor.fetchone()[0]
        
        # Feature usage today
        cursor.execute('''
            SELECT feature_name, SUM(usage_count) as total_usage
            FROM feature_usage 
            WHERE date(last_used) = date('now')
            GROUP BY feature_name
            ORDER BY total_usage DESC
            LIMIT 10
        ''')
        feature_usage = cursor.fetchall()
        
        # AI interactions today
        cursor.execute('''
            SELECT COUNT(*) FROM ai_interactions 
            WHERE date(timestamp) = date('now')
        ''')
        ai_interactions = cursor.fetchone()[0]
        
        # Average response time
        cursor.execute('''
            SELECT AVG(response_time) FROM ai_interactions 
            WHERE date(timestamp) = date('now') AND response_time IS NOT NULL
        ''')
        avg_response_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'active_users': active_users,
            'daily_users': daily_users,
            'feature_usage': dict(feature_usage),
            'ai_interactions': ai_interactions,
            'avg_response_time': round(avg_response_time, 2)
        }
    
    def get_business_intelligence(self):
        """Get business intelligence metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User growth over time
        cursor.execute('''
            SELECT date(timestamp) as date, COUNT(DISTINCT user_id) as users
            FROM user_activity 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY date(timestamp)
            ORDER BY date
        ''')
        user_growth = cursor.fetchall()
        
        # Feature adoption rates
        cursor.execute('''
            SELECT feature_name, COUNT(DISTINCT user_id) as adopters,
                   (SELECT COUNT(DISTINCT user_id) FROM user_activity) * 100.0 / COUNT(DISTINCT user_id) as adoption_rate
            FROM feature_usage
            GROUP BY feature_name
            ORDER BY adoption_rate DESC
        ''')
        feature_adoption = cursor.fetchall()
        
        # AI satisfaction scores
        cursor.execute('''
            SELECT AVG(satisfaction_score) as avg_satisfaction,
                   COUNT(*) as total_ratings
            FROM ai_interactions 
            WHERE satisfaction_score IS NOT NULL
        ''')
        ai_satisfaction = cursor.fetchone()
        
        # Peak usage times
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as activity_count
            FROM user_activity 
            WHERE date(timestamp) = date('now')
            GROUP BY hour
            ORDER BY activity_count DESC
            LIMIT 5
        ''')
        peak_hours = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_growth': dict(user_growth),
            'feature_adoption': [
                {'feature': row[0], 'adopters': row[1], 'rate': round(row[2], 2)}
                for row in feature_adoption
            ],
            'ai_satisfaction': {
                'avg_score': round(ai_satisfaction[0] or 0, 2),
                'total_ratings': ai_satisfaction[1] or 0
            },
            'peak_hours': dict(peak_hours)
        }
    
    def track_ai_interaction(self, user_id, interaction_type, prompt, response_length, response_time, satisfaction_score=None):
        """Track AI interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_interactions (user_id, interaction_type, prompt, response_length, response_time, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, interaction_type, prompt, response_length, response_time, satisfaction_score))
        
        conn.commit()
        conn.close()

# Initialize analytics engine
analytics = AnalyticsEngine()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'analytics_server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analytics/realtime', methods=['GET'])
def get_realtime_analytics():
    """Get real-time analytics data"""
    metrics = analytics.get_real_time_metrics()
    return jsonify(metrics)

@app.route('/api/analytics/business-intelligence', methods=['GET'])
def get_business_intelligence():
    """Get business intelligence data"""
    intelligence = analytics.get_business_intelligence()
    return jsonify(intelligence)

@app.route('/api/analytics/track', methods=['POST'])
def track_activity():
    """Track user activity"""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous')
    activity_type = data.get('activity_type')
    activity_data = data.get('activity_data')
    session_id = data.get('session_id')
    ip_address = request.remote_addr
    
    analytics.track_user_activity(user_id, activity_type, activity_data, session_id, ip_address)
    return jsonify({'success': True})

@app.route('/api/analytics/feature-usage', methods=['POST'])
def track_feature_usage():
    """Track feature usage"""
    data = request.get_json()
    feature_name = data.get('feature_name')
    user_id = data.get('user_id', 'anonymous')
    session_duration = data.get('session_duration')
    
    analytics.track_feature_usage(feature_name, user_id, session_duration)
    return jsonify({'success': True})

@app.route('/api/analytics/ai-interaction', methods=['POST'])
def track_ai_interaction():
    """Track AI interaction"""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous')
    interaction_type = data.get('interaction_type')
    prompt = data.get('prompt')
    response_length = data.get('response_length')
    response_time = data.get('response_time')
    satisfaction_score = data.get('satisfaction_score')
    
    analytics.track_ai_interaction(user_id, interaction_type, prompt, response_length, response_time, satisfaction_score)
    return jsonify({'success': True})

if __name__ == '__main__':
    print("📊 Starting Analytics & Intelligence Server...")
    print("📈 Real-time business analytics ready!")
    print("🎯 Available at: http://localhost:5006")
    app.run(host='0.0.0.0', port=5006, debug=False)
