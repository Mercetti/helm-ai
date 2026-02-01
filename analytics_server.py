#!/usr/bin/env python3
"""
Stellar Logic AI - Analytics & Intelligence Server
Real-time business analytics and platform intelligence
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import new unified systems
from src.common.exceptions import (
    DatabaseException, ValidationException,
    handle_errors, safe_execute
)
from src.logging_config.logger import get_logger
from src.monitoring.metrics import track_request, track_database_query, track_error
from src.database.connection_manager import get_connection_manager

# Configure logging
logger = get_logger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000'])

# Initialize database connection manager
try:
    db_manager = get_connection_manager("sqlite:///analytics.db")
    logger.info("Database connection manager initialized")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    db_manager = None

class AnalyticsEngine:
    """Enhanced analytics engine with proper error handling and monitoring"""

    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.db_manager = db_manager
        self.init_database()

    @handle_errors(error_category="database")
    def init_database(self) -> None:
        """Initialize analytics database with proper error handling"""
        if not self.db_manager:
            raise DatabaseException("Database manager not available")

        with self.db_manager.get_session() as session:
            try:
                # User activity tracking
                session.execute('''
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
                session.execute('''
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
                session.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        server_name TEXT
                    )
                ''')

                # Business intelligence
                session.execute('''
                    CREATE TABLE IF NOT EXISTS business_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_type TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # AI interactions
                session.execute('''
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

                session.commit()
                logger.info("Analytics database initialized successfully")

            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise DatabaseException(
                    "Failed to initialize analytics database",
                    operation="init_database",
                    cause=e
                )

    @handle_errors(error_category="database")
    def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Track user activity with comprehensive error handling.

        Args:
            user_id: Unique user identifier
            activity_type: Type of activity being tracked
            activity_data: Optional activity metadata
            session_id: Optional session identifier
            ip_address: Optional client IP address

        Returns:
            True if tracked successfully, False otherwise

        Raises:
            ValidationException: If required parameters are missing
            DatabaseException: If database operation fails
        """
        if not user_id or not activity_type:
            raise ValidationException(
                "user_id and activity_type are required",
                field="user_id" if not user_id else "activity_type"
            )

        start_time = time.time()

        try:
            with self.db_manager.get_session() as session:
                session.execute('''
                    INSERT INTO user_activity (user_id, activity_type, activity_data, session_id, ip_address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    activity_type,
                    json.dumps(activity_data) if activity_data else None,
                    session_id,
                    ip_address
                ))

                session.commit()

            # Track performance
            duration = (time.time() - start_time) * 1000
            track_database_query("INSERT", "user_activity", duration / 1000)

            logger.info(
                f"User activity tracked: {activity_type}",
                extra={
                    "user_id": user_id,
                    "activity_type": activity_type,
                    "session_id": session_id
                }
            )

            return True

        except Exception as e:
            track_error("database_error", "analytics")
            logger.error(f"Failed to track user activity: {e}")
            raise DatabaseException(
                "Failed to track user activity",
                operation="track_user_activity",
                cause=e
            )

    @handle_errors(error_category="database")
    def track_feature_usage(
        self,
        feature_name: str,
        user_id: str,
        session_duration: Optional[int] = None
    ) -> bool:
        """
        Track feature usage with proper error handling.

        Args:
            feature_name: Name of the feature being used
            user_id: User identifier
            session_duration: Optional session duration in seconds

        Returns:
            True if tracked successfully

        Raises:
            ValidationException: If required parameters are missing
            DatabaseException: If database operation fails
        """
        if not feature_name or not user_id:
            raise ValidationException(
                "feature_name and user_id are required",
                field="feature_name" if not feature_name else "user_id"
            )

        start_time = time.time()

        try:
            with self.db_manager.get_session() as session:
                # Check if feature exists for this user
                result = session.execute('''
                    SELECT id, usage_count FROM feature_usage
                    WHERE feature_name = ? AND user_id = ?
                ''', (feature_name, user_id)).fetchone()

                if result:
                    # Update existing
                    session.execute('''
                        UPDATE feature_usage
                        SET usage_count = usage_count + 1,
                            last_used = CURRENT_TIMESTAMP,
                            session_duration = ?
                        WHERE id = ?
                    ''', (session_duration, result[0]))
                else:
                    # Create new
                    session.execute('''
                        INSERT INTO feature_usage (feature_name, user_id, session_duration)
                        VALUES (?, ?, ?)
                    ''', (feature_name, user_id, session_duration))

                session.commit()

            # Track performance
            duration = (time.time() - start_time) * 1000
            track_database_query("INSERT/UPDATE", "feature_usage", duration / 1000)

            logger.info(
                f"Feature usage tracked: {feature_name}",
                extra={
                    "feature_name": feature_name,
                    "user_id": user_id,
                    "session_duration": session_duration
                }
            )

            return True

        except Exception as e:
            track_error("database_error", "analytics")
            logger.error(f"Failed to track feature usage: {e}")
            raise DatabaseException(
                "Failed to track feature usage",
                operation="track_feature_usage",
                cause=e
            )

    @safe_execute(default_return={})
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time platform metrics with comprehensive error handling.

        Returns:
            Dictionary containing real-time metrics

        Note:
            Returns empty dict on error to prevent API failures
        """
        start_time = time.time()

        try:
            with self.db_manager.get_session() as session:
                # Active users (last 5 minutes)
                active_users_result = session.execute('''
                    SELECT COUNT(DISTINCT user_id) FROM user_activity
                    WHERE timestamp > datetime('now', '-5 minutes')
                ''').fetchone()

                active_users = active_users_result[0] if active_users_result else 0

                # Feature usage stats
                feature_stats_result = session.execute('''
                    SELECT feature_name, SUM(usage_count) as total_usage
                    FROM feature_usage
                    GROUP BY feature_name
                    ORDER BY total_usage DESC
                    LIMIT 10
                ''').fetchall()

                feature_stats = [
                    {"feature": row[0], "usage": row[1]}
                    for row in feature_stats_result
                ]

                # AI interaction metrics
                ai_metrics_result = session.execute('''
                    SELECT
                        COUNT(*) as total_interactions,
                        AVG(response_time) as avg_response_time,
                        AVG(satisfaction_score) as avg_satisfaction
                    FROM ai_interactions
                    WHERE timestamp > datetime('now', '-1 hour')
                ''').fetchone()

                ai_metrics = {
                    "total_interactions": ai_metrics_result[0] if ai_metrics_result else 0,
                    "avg_response_time": ai_metrics_result[1] if ai_metrics_result else 0.0,
                    "avg_satisfaction": ai_metrics_result[2] if ai_metrics_result else 0.0
                }

                # Performance metrics
                perf_metrics_result = session.execute('''
                    SELECT metric_name, AVG(metric_value) as avg_value
                    FROM performance_metrics
                    WHERE timestamp > datetime('now', '-1 hour')
                    GROUP BY metric_name
                ''').fetchall()

                perf_metrics = {row[0]: row[1] for row in perf_metrics_result}

                metrics = {
                    "active_users": active_users,
                    "feature_usage": feature_stats,
                    "ai_metrics": ai_metrics,
                    "performance": perf_metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Track performance
            duration = (time.time() - start_time) * 1000
            track_database_query("SELECT", "multiple_tables", duration / 1000)

            logger.info("Real-time metrics retrieved successfully")
            return metrics

        except Exception as e:
            track_error("database_error", "analytics")
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

@app.route('/health', methods=['GET'])
@handle_errors()
def health_check():
    """Health check endpoint with proper error handling"""
    start_time = time.time()

    try:
        # Check database health
        if db_manager:
            health_status = db_manager.health_check()
            db_healthy = health_status.get("status") == "healthy"
        else:
            db_healthy = False

        response = {
            "status": "healthy" if db_healthy else "degraded",
            "service": "Analytics Server",
            "database": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Track request
        duration = time.time() - start_time
        track_request("GET", "/health", 200, duration)

        return jsonify(response)

    except Exception as e:
        track_error("health_check_error", "analytics")
        duration = time.time() - start_time
        track_request("GET", "/health", 500, duration)
        raise

@app.route('/api/analytics/track-activity', methods=['POST'])
@handle_errors()
def track_activity():
    """Track user activity endpoint"""
    start_time = time.time()

    try:
        data = request.get_json()

        if not data:
            raise ValidationException("Request body is required")

        required_fields = ['user_id', 'activity_type']
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Field '{field}' is required", field=field)

        # Track the activity
        success = analytics_engine.track_user_activity(
            user_id=data['user_id'],
            activity_type=data['activity_type'],
            activity_data=data.get('activity_data'),
            session_id=data.get('session_id'),
            ip_address=request.remote_addr
        )

        response = {
            "success": True,
            "message": "Activity tracked successfully",
            "tracked": success
        }

        # Track request
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-activity", 200, duration)

        return jsonify(response)

    except ValidationException:
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-activity", 400, duration)
        raise
    except Exception as e:
        track_error("api_error", "analytics")
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-activity", 500, duration)
        raise

@app.route('/api/analytics/track-feature', methods=['POST'])
@handle_errors()
def track_feature():
    """Track feature usage endpoint"""
    start_time = time.time()

    try:
        data = request.get_json()

        if not data:
            raise ValidationException("Request body is required")

        required_fields = ['feature_name', 'user_id']
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Field '{field}' is required", field=field)

        # Track the feature usage
        success = analytics_engine.track_feature_usage(
            feature_name=data['feature_name'],
            user_id=data['user_id'],
            session_duration=data.get('session_duration')
        )

        response = {
            "success": True,
            "message": "Feature usage tracked successfully",
            "tracked": success
        }

        # Track request
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-feature", 200, duration)

        return jsonify(response)

    except ValidationException:
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-feature", 400, duration)
        raise
    except Exception as e:
        track_error("api_error", "analytics")
        duration = time.time() - start_time
        track_request("POST", "/api/analytics/track-feature", 500, duration)
        raise

@app.route('/api/analytics/metrics', methods=['GET'])
@handle_errors()
def get_metrics():
    """Get real-time metrics endpoint"""
    start_time = time.time()

    try:
        metrics = analytics_engine.get_real_time_metrics()

        # Track request
        duration = time.time() - start_time
        track_request("GET", "/api/analytics/metrics", 200, duration)

        return jsonify(metrics)

    except Exception as e:
        track_error("api_error", "analytics")
        duration = time.time() - start_time
        track_request("GET", "/api/analytics/metrics", 500, duration)
        raise

if __name__ == '__main__':
    logger.info("Starting Analytics Server...")
    app.run(host='0.0.0.0', port=5001, debug=False)
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
