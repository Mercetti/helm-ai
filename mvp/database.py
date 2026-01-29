#!/usr/bin/env python3
"""
Helm AI - Database Management System
SQLite database with advanced features for anti-cheat detection
"""

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from contextlib import contextmanager
import threading
import hashlib
import secrets
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    SAFE = "Safe"
    SUSPICIOUS = "Suspicious"
    CHEATING_DETECTED = "Cheating Detected"

class DetectionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DetectionResult:
    request_id: str
    user_id: str
    game_id: str
    session_id: Optional[str]
    risk_level: RiskLevel
    confidence: float
    processing_time_ms: float
    modalities_used: List[str]
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None
    status: DetectionStatus = DetectionStatus.COMPLETED

@dataclass
class UserProfile:
    user_id: str
    username: Optional[str]
    email: Optional[str]
    created_at: datetime
    last_seen: datetime
    total_detections: int = 0
    cheating_detections: int = 0
    suspicious_detections: int = 0
    risk_score: float = 0.0
    is_banned: bool = False
    ban_reason: Optional[str] = None
    ban_until: Optional[datetime] = None

@dataclass
class GameSession:
    session_id: str
    user_id: str
    game_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_detections: int = 0
    max_risk_level: RiskLevel = RiskLevel.SAFE
    average_confidence: float = 0.0
    is_active: bool = True

class DatabaseManager:
    """Advanced database management for Helm AI"""
    
    def __init__(self, db_path: str = "helm_ai.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys=ON")
            # Set busy timeout
            self._local.connection.execute("PRAGMA busy_timeout=30000")
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def initialize_database(self):
        """Initialize database with all required tables"""
        with self.get_cursor() as cursor:
            # Detection results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detection_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    session_id TEXT,
                    risk_level TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    processing_time_ms REAL NOT NULL,
                    modalities_used TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME NOT NULL,
                    ip_address TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
                )
            ''')
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    email TEXT,
                    created_at DATETIME NOT NULL,
                    last_seen DATETIME NOT NULL,
                    total_detections INTEGER DEFAULT 0,
                    cheating_detections INTEGER DEFAULT 0,
                    suspicious_detections INTEGER DEFAULT 0,
                    risk_score REAL DEFAULT 0.0,
                    is_banned BOOLEAN DEFAULT FALSE,
                    ban_reason TEXT,
                    ban_until DATETIME,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Game sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    total_detections INTEGER DEFAULT 0,
                    max_risk_level TEXT DEFAULT 'Safe',
                    average_confidence REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    last_used DATETIME,
                    usage_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    rate_limit INTEGER DEFAULT 100,
                    created_by TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Rate limiting table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    api_key TEXT NOT NULL,
                    request_count INTEGER DEFAULT 0,
                    window_start DATETIME NOT NULL,
                    window_end DATETIME NOT NULL,
                    PRIMARY KEY (api_key, window_start)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_detections INTEGER DEFAULT 0,
                    safe_detections INTEGER DEFAULT 0,
                    suspicious_detections INTEGER DEFAULT 0,
                    cheating_detections INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    unique_games INTEGER DEFAULT 0,
                    average_processing_time REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io REAL,
                    active_connections INTEGER,
                    queue_size INTEGER,
                    error_rate REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_detection_results_user_id ON detection_results(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_detection_results_game_id ON detection_results(game_id)",
                "CREATE INDEX IF NOT EXISTS idx_detection_results_timestamp ON detection_results(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_detection_results_risk_level ON detection_results(risk_level)",
                "CREATE INDEX IF NOT EXISTS idx_user_profiles_last_seen ON user_profiles(last_seen)",
                "CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_game_sessions_start_time ON game_sessions(start_time)",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key)",
                "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            logger.info("Database initialized successfully")
    
    def save_detection_result(self, result: DetectionResult) -> bool:
        """Save detection result to database"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    INSERT OR REPLACE INTO detection_results 
                    (request_id, user_id, game_id, session_id, risk_level, confidence,
                     processing_time_ms, modalities_used, details, timestamp, ip_address, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.request_id,
                    result.user_id,
                    result.game_id,
                    result.session_id,
                    result.risk_level.value,
                    result.confidence,
                    result.processing_time_ms,
                    json.dumps(result.modalities_used),
                    json.dumps(result.details),
                    result.timestamp,
                    result.ip_address,
                    result.status.value
                ))
                
                # Update user profile
                self._update_user_profile(cursor, result)
                
                # Update game session if provided
                if result.session_id:
                    self._update_game_session(cursor, result)
                
                # Update analytics
                self._update_analytics(cursor, result)
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving detection result: {e}")
            return False
    
    def _update_user_profile(self, cursor: sqlite3.Cursor, result: DetectionResult):
        """Update user profile with detection result"""
        # Get current user profile
        cursor.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?",
            (result.user_id,)
        )
        user_data = cursor.fetchone()
        
        if user_data:
            # Update existing profile
            total_detections = user_data['total_detections'] + 1
            cheating_detections = user_data['cheating_detections']
            suspicious_detections = user_data['suspicious_detections']
            
            if result.risk_level == RiskLevel.CHEATING_DETECTED:
                cheating_detections += 1
            elif result.risk_level == RiskLevel.SUSPICIOUS:
                suspicious_detections += 1
            
            # Calculate new risk score
            risk_score = (cheating_detections * 10 + suspicious_detections * 3) / total_detections
            
            cursor.execute('''
                UPDATE user_profiles 
                SET total_detections = ?, cheating_detections = ?, suspicious_detections = ?,
                    risk_score = ?, last_seen = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (total_detections, cheating_detections, suspicious_detections, 
                  risk_score, result.timestamp, result.user_id))
        else:
            # Create new profile
            cheating_detections = 1 if result.risk_level == RiskLevel.CHEATING_DETECTED else 0
            suspicious_detections = 1 if result.risk_level == RiskLevel.SUSPICIOUS else 0
            risk_score = (cheating_detections * 10 + suspicious_detections * 3)
            
            cursor.execute('''
                INSERT INTO user_profiles 
                (user_id, created_at, last_seen, total_detections, cheating_detections,
                 suspicious_detections, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (result.user_id, result.timestamp, result.timestamp, 1,
                  cheating_detections, suspicious_detections, risk_score))
    
    def _update_game_session(self, cursor: sqlite3.Cursor, result: DetectionResult):
        """Update game session with detection result"""
        # Get current session
        cursor.execute(
            "SELECT * FROM game_sessions WHERE session_id = ?",
            (result.session_id,)
        )
        session_data = cursor.fetchone()
        
        if session_data:
            # Update existing session
            total_detections = session_data['total_detections'] + 1
            
            # Update max risk level
            current_max = RiskLevel(session_data['max_risk_level'])
            new_max = max(current_max, result.risk_level, key=lambda x: x.value)
            
            # Calculate average confidence
            current_avg = session_data['average_confidence']
            new_avg = (current_avg * (total_detections - 1) + result.confidence) / total_detections
            
            cursor.execute('''
                UPDATE game_sessions 
                SET total_detections = ?, max_risk_level = ?, average_confidence = ?
                WHERE session_id = ?
            ''', (total_detections, new_max.value, new_avg, result.session_id))
        else:
            # Create new session
            cursor.execute('''
                INSERT INTO game_sessions 
                (session_id, user_id, game_id, start_time, total_detections, 
                 max_risk_level, average_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (result.session_id, result.user_id, result.game_id, 
                  result.timestamp, 1, result.risk_level.value, result.confidence))
    
    def _update_analytics(self, cursor: sqlite3.Cursor, result: DetectionResult):
        """Update daily analytics"""
        date = result.timestamp.date()
        
        # Get current analytics for date
        cursor.execute(
            "SELECT * FROM analytics WHERE date = ?",
            (date,)
        )
        analytics_data = cursor.fetchone()
        
        if analytics_data:
            # Update existing analytics
            total_detections = analytics_data['total_detections'] + 1
            safe_detections = analytics_data['safe_detections']
            suspicious_detections = analytics_data['suspicious_detections']
            cheating_detections = analytics_data['cheating_detections']
            
            if result.risk_level == RiskLevel.SAFE:
                safe_detections += 1
            elif result.risk_level == RiskLevel.SUSPICIOUS:
                suspicious_detections += 1
            elif result.risk_level == RiskLevel.CHEATING_DETECTED:
                cheating_detections += 1
            
            cursor.execute('''
                UPDATE analytics 
                SET total_detections = ?, safe_detections = ?, suspicious_detections = ?,
                    cheating_detections = ?
                WHERE date = ?
            ''', (total_detections, safe_detections, suspicious_detections, 
                  cheating_detections, date))
        else:
            # Create new analytics entry
            safe_detections = 1 if result.risk_level == RiskLevel.SAFE else 0
            suspicious_detections = 1 if result.risk_level == RiskLevel.SUSPICIOUS else 0
            cheating_detections = 1 if result.risk_level == RiskLevel.CHEATING_DETECTED else 0
            
            cursor.execute('''
                INSERT INTO analytics 
                (date, total_detections, safe_detections, suspicious_detections, cheating_detections)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, 1, safe_detections, suspicious_detections, cheating_detections))
    
    def get_detection_result(self, request_id: str) -> Optional[DetectionResult]:
        """Get detection result by request ID"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM detection_results WHERE request_id = ?",
                    (request_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    return DetectionResult(
                        request_id=result['request_id'],
                        user_id=result['user_id'],
                        game_id=result['game_id'],
                        session_id=result['session_id'],
                        risk_level=RiskLevel(result['risk_level']),
                        confidence=result['confidence'],
                        processing_time_ms=result['processing_time_ms'],
                        modalities_used=json.loads(result['modalities_used']),
                        details=json.loads(result['details']) if result['details'] else {},
                        timestamp=datetime.fromisoformat(result['timestamp']),
                        ip_address=result['ip_address'],
                        status=DetectionStatus(result['status'])
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting detection result: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM user_profiles WHERE user_id = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    return UserProfile(
                        user_id=result['user_id'],
                        username=result['username'],
                        email=result['email'],
                        created_at=datetime.fromisoformat(result['created_at']),
                        last_seen=datetime.fromisoformat(result['last_seen']),
                        total_detections=result['total_detections'],
                        cheating_detections=result['cheating_detections'],
                        suspicious_detections=result['suspicious_detections'],
                        risk_score=result['risk_score'],
                        is_banned=bool(result['is_banned']),
                        ban_reason=result['ban_reason'],
                        ban_until=datetime.fromisoformat(result['ban_until']) if result['ban_until'] else None
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def get_user_detections(self, user_id: str, limit: int = 100, offset: int = 0) -> List[DetectionResult]:
        """Get detection history for a user"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute('''
                    SELECT * FROM detection_results 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
                
                results = []
                for row in cursor.fetchall():
                    results.append(DetectionResult(
                        request_id=row['request_id'],
                        user_id=row['user_id'],
                        game_id=row['game_id'],
                        session_id=row['session_id'],
                        risk_level=RiskLevel(row['risk_level']),
                        confidence=row['confidence'],
                        processing_time_ms=row['processing_time_ms'],
                        modalities_used=json.loads(row['modalities_used']),
                        details=json.loads(row['details']) if row['details'] else {},
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        ip_address=row['ip_address'],
                        status=DetectionStatus(row['status'])
                    ))
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting user detections: {e}")
            return []
    
    def get_game_statistics(self, game_id: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics for a specific game"""
        try:
            with self.get_cursor() as cursor:
                # Get detection counts by risk level
                cursor.execute('''
                    SELECT risk_level, COUNT(*) as count
                    FROM detection_results 
                    WHERE game_id = ? AND timestamp >= datetime('now', '-{} days')
                    GROUP BY risk_level
                '''.format(days), (game_id,))
                
                risk_distribution = dict(cursor.fetchall())
                
                # Get total detections
                cursor.execute('''
                    SELECT COUNT(*) as total
                    FROM detection_results 
                    WHERE game_id = ? AND timestamp >= datetime('now', '-{} days')
                '''.format(days), (game_id,))
                
                total_detections = cursor.fetchone()['total']
                
                # Get unique users
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) as unique_users
                    FROM detection_results 
                    WHERE game_id = ? AND timestamp >= datetime('now', '-{} days')
                '''.format(days), (game_id,))
                
                unique_users = cursor.fetchone()['unique_users']
                
                # Get average processing time
                cursor.execute('''
                    SELECT AVG(processing_time_ms) as avg_time
                    FROM detection_results 
                    WHERE game_id = ? AND timestamp >= datetime('now', '-{} days')
                '''.format(days), (game_id,))
                
                avg_processing_time = cursor.fetchone()['avg_time'] or 0
                
                return {
                    'total_detections': total_detections,
                    'risk_distribution': risk_distribution,
                    'unique_users': unique_users,
                    'average_processing_time_ms': round(avg_processing_time, 2),
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Error getting game statistics: {e}")
            return {}
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for the specified period"""
        try:
            with self.get_cursor() as cursor:
                # Get daily analytics
                cursor.execute('''
                    SELECT date, total_detections, safe_detections, suspicious_detections, 
                           cheating_detections, unique_users, unique_games, average_processing_time
                    FROM analytics 
                    WHERE date >= date('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days))
                
                daily_data = []
                for row in cursor.fetchall():
                    daily_data.append({
                        'date': row['date'],
                        'total_detections': row['total_detections'],
                        'safe_detections': row['safe_detections'],
                        'suspicious_detections': row['suspicious_detections'],
                        'cheating_detections': row['cheating_detections'],
                        'unique_users': row['unique_users'],
                        'unique_games': row['unique_games'],
                        'average_processing_time_ms': row['average_processing_time']
                    })
                
                # Calculate totals
                cursor.execute('''
                    SELECT 
                        SUM(total_detections) as total_detections,
                        SUM(safe_detections) as safe_detections,
                        SUM(suspicious_detections) as suspicious_detections,
                        SUM(cheating_detections) as cheating_detections,
                        AVG(average_processing_time) as avg_processing_time
                    FROM analytics 
                    WHERE date >= date('now', '-{} days')
                '''.format(days))
                
                totals = cursor.fetchone()
                
                return {
                    'daily_data': daily_data,
                    'totals': {
                        'total_detections': totals['total_detections'] or 0,
                        'safe_detections': totals['safe_detections'] or 0,
                        'suspicious_detections': totals['suspicious_detections'] or 0,
                        'cheating_detections': totals['cheating_detections'] or 0,
                        'average_processing_time_ms': round(totals['avg_processing_time'] or 0, 2)
                    },
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    def create_api_key(self, name: str, permissions: List[str], created_by: str = None) -> Optional[str]:
        """Create new API key"""
        try:
            api_key = secrets.token_urlsafe(32)
            
            with self.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO api_keys (key, name, permissions, created_at, created_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (api_key, name, json.dumps(permissions), datetime.now(), created_by))
                
                return api_key
                
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key info"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM api_keys WHERE key = ? AND is_active = TRUE",
                    (api_key,)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update last used and usage count
                    cursor.execute('''
                        UPDATE api_keys 
                        SET last_used = ?, usage_count = usage_count + 1, updated_at = CURRENT_TIMESTAMP
                        WHERE key = ?
                    ''', (datetime.now(), api_key))
                    
                    return {
                        'key': result['key'],
                        'name': result['name'],
                        'permissions': json.loads(result['permissions']),
                        'usage_count': result['usage_count'],
                        'rate_limit': result['rate_limit']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data to manage database size"""
        try:
            with self.get_cursor() as cursor:
                # Delete old detection results
                cursor.execute('''
                    DELETE FROM detection_results 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                # Delete old analytics
                cursor.execute('''
                    DELETE FROM analytics 
                    WHERE date < date('now', '-{} days')
                '''.format(days))
                
                # Delete old system metrics
                cursor.execute('''
                    DELETE FROM system_metrics 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old records")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()

# Global database instance
db_manager = DatabaseManager()

# Convenience functions
def save_detection_result(result: DetectionResult) -> bool:
    """Save detection result using global database manager"""
    return db_manager.save_detection_result(result)

def get_detection_result(request_id: str) -> Optional[DetectionResult]:
    """Get detection result using global database manager"""
    return db_manager.get_detection_result(request_id)

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get user profile using global database manager"""
    return db_manager.get_user_profile(user_id)

def get_user_detections(user_id: str, limit: int = 100, offset: int = 0) -> List[DetectionResult]:
    """Get user detections using global database manager"""
    return db_manager.get_user_detections(user_id, limit, offset)

def get_game_statistics(game_id: str, days: int = 30) -> Dict[str, Any]:
    """Get game statistics using global database manager"""
    return db_manager.get_game_statistics(game_id, days)

def get_analytics_summary(days: int = 30) -> Dict[str, Any]:
    """Get analytics summary using global database manager"""
    return db_manager.get_analytics_summary(days)

def create_api_key(name: str, permissions: List[str], created_by: str = None) -> Optional[str]:
    """Create API key using global database manager"""
    return db_manager.create_api_key(name, permissions, created_by)

def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Validate API key using global database manager"""
    return db_manager.validate_api_key(api_key)

if __name__ == "__main__":
    # Test database functionality
    print("Testing Helm AI Database...")
    
    # Create test detection result
    test_result = DetectionResult(
        request_id="test_123",
        user_id="user_456",
        game_id="game_789",
        session_id="session_101",
        risk_level=RiskLevel.SUSPICIOUS,
        confidence=0.75,
        processing_time_ms=85.5,
        modalities_used=["vision", "audio"],
        details={"test": "data"},
        timestamp=datetime.now()
    )
    
    # Save test result
    success = save_detection_result(test_result)
    print(f"Save detection result: {success}")
    
    # Retrieve detection result
    retrieved = get_detection_result("test_123")
    print(f"Retrieve detection result: {retrieved is not None}")
    
    # Get user profile
    profile = get_user_profile("user_456")
    print(f"User profile: {profile}")
    
    # Get analytics
    analytics = get_analytics_summary(30)
    print(f"Analytics: {analytics}")
    
    print("Database test completed!")
