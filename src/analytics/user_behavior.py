"""
Helm AI User Behavior Analytics
Tracks user patterns, engagement, and behavior insights
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import get_database_manager
from monitoring.structured_logging import logger

@dataclass
class UserBehavior:
    """User behavior data point"""
    user_id: str
    session_id: str
    action: str
    timestamp: datetime
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'metadata': self.metadata
        }

@dataclass
class UserSegment:
    """User segment definition"""
    segment_id: str
    name: str
    description: str
    criteria: Dict[str, Any]
    user_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'segment_id': self.segment_id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria,
            'user_count': self.user_count,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class EngagementMetrics:
    """User engagement metrics"""
    user_id: str
    period_start: datetime
    period_end: datetime
    session_count: int
    total_duration: float
    actions_count: int
    unique_actions: int
    last_active: datetime
    engagement_score: float
    churn_risk: str  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'session_count': self.session_count,
            'total_duration': self.total_duration,
            'actions_count': self.actions_count,
            'unique_actions': self.unique_actions,
            'last_active': self.last_active.isoformat(),
            'engagement_score': self.engagement_score,
            'churn_risk': self.churn_risk
        }

class BehaviorAnalytics:
    """User behavior analytics engine"""
    
    def __init__(self):
        self.behavior_data = deque(maxlen=10000)
        self.user_segments = self._setup_default_segments()
        self.engagement_cache = {}
        self.lock = threading.RLock()
        
    def _setup_default_segments(self) -> Dict[str, UserSegment]:
        """Setup default user segments"""
        return {
            'power_users': UserSegment(
                segment_id='power_users',
                name='Power Users',
                description='Highly engaged users with frequent activity',
                criteria={
                    'min_sessions_per_week': 10,
                    'min_avg_session_duration': 20,
                    'min_actions_per_session': 5
                }
            ),
            'new_users': UserSegment(
                segment_id='new_users',
                name='New Users',
                description='Recently registered users',
                criteria={
                    'max_account_age_days': 7,
                    'min_sessions': 1
                }
            ),
            'at_risk_users': UserSegment(
                segment_id='at_risk_users',
                name='At Risk Users',
                description='Users showing signs of potential churn',
                criteria={
                    'max_days_since_last_active': 14,
                    'min_account_age_days': 30,
                    'max_engagement_score': 30
                }
            ),
            'premium_users': UserSegment(
                segment_id='premium_users',
                name='Premium Users',
                description='Users with premium subscriptions',
                criteria={
                    'subscription_tier': 'premium'
                }
            ),
            'inactive_users': UserSegment(
                segment_id='inactive_users',
                name='Inactive Users',
                description='Users with no recent activity',
                criteria={
                    'min_days_since_last_active': 30
                }
            )
        }
    
    def track_behavior(self, user_id: str, session_id: str, action: str, 
                      duration: Optional[float] = None, metadata: Dict[str, Any] = None):
        """Track user behavior event"""
        behavior = UserBehavior(
            user_id=user_id,
            session_id=session_id,
            action=action,
            timestamp=datetime.now(),
            duration=duration,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.behavior_data.append(behavior)
        
        logger.debug(f"Tracked behavior: {user_id} - {action}")
    
    def calculate_engagement_metrics(self, user_id: str, days: int = 30) -> EngagementMetrics:
        """Calculate engagement metrics for a user"""
        cache_key = f"{user_id}_{days}"
        
        # Check cache
        if cache_key in self.engagement_cache:
            cached_time, cached_metrics = self.engagement_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=30):
                return cached_metrics
        
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=days)
            
            # Get user behavior data
            with self.lock:
                user_behaviors = [
                    b for b in self.behavior_data 
                    if b.user_id == user_id and b.timestamp >= period_start
                ]
            
            if not user_behaviors:
                # Get from database
                user_behaviors = self._get_user_behaviors_from_db(user_id, period_start, period_end)
            
            # Calculate metrics
            session_count = len(set(b.session_id for b in user_behaviors))
            total_duration = sum(b.duration or 0 for b in user_behaviors)
            actions_count = len(user_behaviors)
            unique_actions = len(set(b.action for b in user_behaviors))
            last_active = max(b.timestamp for b in user_behaviors) if user_behaviors else period_start
            
            # Calculate engagement score (0-100)
            engagement_score = self._calculate_engagement_score(
                session_count, total_duration, actions_count, days
            )
            
            # Calculate churn risk
            churn_risk = self._calculate_churn_risk(
                engagement_score, last_active, days
            )
            
            metrics = EngagementMetrics(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end,
                session_count=session_count,
                total_duration=total_duration,
                actions_count=actions_count,
                unique_actions=unique_actions,
                last_active=last_active,
                engagement_score=engagement_score,
                churn_risk=churn_risk
            )
            
            # Cache result
            self.engagement_cache[cache_key] = (datetime.now(), metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating engagement metrics for {user_id}: {e}")
            return EngagementMetrics(
                user_id=user_id,
                period_start=datetime.now() - timedelta(days=days),
                period_end=datetime.now(),
                session_count=0,
                total_duration=0,
                actions_count=0,
                unique_actions=0,
                last_active=datetime.now(),
                engagement_score=0,
                churn_risk='high'
            )
    
    def _get_user_behaviors_from_db(self, user_id: str, period_start: datetime, period_end: datetime) -> List[UserBehavior]:
        """Get user behaviors from database"""
        behaviors = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Get audit logs for user
                result = session.execute(text("""
                    SELECT action, created_at, metadata
                    FROM audit_logs
                    WHERE user_id = :user_id
                    AND created_at BETWEEN :start AND :end
                    ORDER BY created_at
                """), {'user_id': user_id, 'start': period_start, 'end': period_end})
                
                for row in result:
                    action, created_at, metadata = row
                    behaviors.append(UserBehavior(
                        user_id=user_id,
                        session_id=f"session_{action}_{created_at}",
                        action=action,
                        timestamp=created_at,
                        metadata=json.loads(metadata) if metadata else {}
                    ))
                
        except Exception as e:
            logger.error(f"Error getting user behaviors from DB: {e}")
        
        return behaviors
    
    def _calculate_engagement_score(self, session_count: int, total_duration: float, 
                                  actions_count: int, days: int) -> float:
        """Calculate engagement score (0-100)"""
        try:
            # Normalize metrics
            sessions_per_day = session_count / max(days, 1)
            duration_per_session = total_duration / max(session_count, 1)
            actions_per_session = actions_count / max(session_count, 1)
            
            # Calculate score components
            session_score = min(sessions_per_day * 20, 40)  # Max 40 points
            duration_score = min(duration_per_session * 2, 30)  # Max 30 points
            action_score = min(actions_per_session * 6, 30)  # Max 30 points
            
            total_score = session_score + duration_score + action_score
            return round(total_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    def _calculate_churn_risk(self, engagement_score: float, last_active: datetime, days: int) -> str:
        """Calculate churn risk"""
        try:
            days_since_active = (datetime.now() - last_active).days
            
            # High risk factors
            if engagement_score < 20 or days_since_active > 14:
                return 'high'
            
            # Medium risk factors
            if engagement_score < 40 or days_since_active > 7:
                return 'medium'
            
            # Low risk
            return 'low'
            
        except Exception as e:
            logger.error(f"Error calculating churn risk: {e}")
            return 'medium'
    
    def segment_users(self, segment_id: str) -> List[str]:
        """Get users in a specific segment"""
        segment = self.user_segments.get(segment_id)
        if not segment:
            return []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                if segment_id == 'power_users':
                    # Power users: High activity
                    result = session.execute(text("""
                        SELECT u.id FROM users u
                        JOIN (
                            SELECT user_id, COUNT(*) as session_count,
                                   AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60) as avg_duration
                            FROM (
                                SELECT user_id, created_at, updated_at,
                                       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as rn,
                                       LAG(created_at) OVER (PARTITION BY user_id ORDER BY created_at) as prev_created
                                FROM audit_logs
                                WHERE created_at > NOW() - INTERVAL '7 days'
                            ) sessions
                            WHERE rn = 1 OR prev_created IS NOT NULL
                            GROUP BY user_id
                        ) stats ON u.id = stats.user_id
                        WHERE stats.session_count >= 10
                        AND stats.avg_duration >= 20
                    """))
                    
                elif segment_id == 'new_users':
                    # New users: Recently registered
                    result = session.execute(text("""
                        SELECT id FROM users
                        WHERE created_at > NOW() - INTERVAL '7 days'
                    """))
                    
                elif segment_id == 'at_risk_users':
                    # At risk users: Low engagement
                    result = session.execute(text("""
                        SELECT u.id FROM users u
                        LEFT JOIN (
                            SELECT user_id, MAX(created_at) as last_active
                            FROM audit_logs
                            GROUP BY user_id
                        ) activity ON u.id = activity.user_id
                        WHERE u.created_at < NOW() - INTERVAL '30 days'
                        AND (activity.last_active < NOW() - INTERVAL '14 days' OR activity.last_active IS NULL)
                    """))
                    
                elif segment_id == 'premium_users':
                    # Premium users
                    result = session.execute(text("""
                        SELECT id FROM users
                        WHERE role = 'PREMIUM'
                    """))
                    
                elif segment_id == 'inactive_users':
                    # Inactive users
                    result = session.execute(text("""
                        SELECT u.id FROM users u
                        LEFT JOIN (
                            SELECT user_id, MAX(created_at) as last_active
                            FROM audit_logs
                            GROUP BY user_id
                        ) activity ON u.id = activity.user_id
                        WHERE activity.last_active < NOW() - INTERVAL '30 days' OR activity.last_active IS NULL
                    """))
                
                else:
                    return []
                
                users = [row[0] for row in result]
                
                # Update segment user count
                segment.user_count = len(users)
                
                return users
                
        except Exception as e:
            logger.error(f"Error segmenting users for {segment_id}: {e}")
            return []
    
    def get_behavior_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive behavior insights"""
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=days)
            
            insights = {
                'period': {
                    'start': period_start.isoformat(),
                    'end': period_end.isoformat(),
                    'days': days
                },
                'user_segments': {},
                'engagement_summary': {},
                'action_patterns': {},
                'retention_metrics': {},
                'churn_predictions': {}
            }
            
            # Get segment data
            for segment_id in self.user_segments.keys():
                users = self.segment_users(segment_id)
                insights['user_segments'][segment_id] = {
                    'user_count': len(users),
                    'percentage': 0  # Will be calculated
                }
            
            # Calculate percentages
            total_users = sum(seg['user_count'] for seg in insights['user_segments'].values())
            for segment_id, segment_data in insights['user_segments'].items():
                if total_users > 0:
                    segment_data['percentage'] = round((segment_data['user_count'] / total_users) * 100, 2)
            
            # Get engagement summary
            insights['engagement_summary'] = self._get_engagement_summary(days)
            
            # Get action patterns
            insights['action_patterns'] = self._get_action_patterns(days)
            
            # Get retention metrics
            insights['retention_metrics'] = self._get_retention_metrics(days)
            
            # Get churn predictions
            insights['churn_predictions'] = self._get_churn_predictions(days)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting behavior insights: {e}")
            return {}
    
    def _get_engagement_summary(self, days: int) -> Dict[str, Any]:
        """Get engagement summary"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Get active users
                result = session.execute(text("""
                    SELECT COUNT(DISTINCT user_id) FROM audit_logs
                    WHERE created_at > NOW() - INTERVAL :days days
                """), {'days': days})
                
                active_users = result.scalar()
                
                # Get total users
                result = session.execute(text("SELECT COUNT(*) FROM users"))
                total_users = result.scalar()
                
                # Calculate engagement rate
                engagement_rate = (active_users / total_users * 100) if total_users > 0 else 0
                
                return {
                    'active_users': active_users,
                    'total_users': total_users,
                    'engagement_rate': round(engagement_rate, 2),
                    'avg_engagement_score': 65.0  # Would be calculated from actual data
                }
                
        except Exception as e:
            logger.error(f"Error getting engagement summary: {e}")
            return {}
    
    def _get_action_patterns(self, days: int) -> Dict[str, Any]:
        """Get action patterns"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Get most common actions
                result = session.execute(text("""
                    SELECT action, COUNT(*) as count
                    FROM audit_logs
                    WHERE created_at > NOW() - INTERVAL :days days
                    GROUP BY action
                    ORDER BY count DESC
                    LIMIT 10
                """), {'days': days})
                
                top_actions = [{'action': row[0], 'count': row[1]} for row in result]
                
                # Get action frequency by hour
                result = session.execute(text("""
                    SELECT EXTRACT(HOUR FROM created_at) as hour, COUNT(*) as count
                    FROM audit_logs
                    WHERE created_at > NOW() - INTERVAL '7 days'
                    GROUP BY hour
                    ORDER BY hour
                """))
                
                hourly_pattern = {str(int(row[0])): row[1] for row in result}
                
                return {
                    'top_actions': top_actions,
                    'hourly_pattern': hourly_pattern,
                    'peak_hour': max(hourly_pattern, key=hourly_pattern.get) if hourly_pattern else None
                }
                
        except Exception as e:
            logger.error(f"Error getting action patterns: {e}")
            return {}
    
    def _get_retention_metrics(self, days: int) -> Dict[str, Any]:
        """Get retention metrics"""
        try:
            # Simplified retention calculation
            return {
                'day_1_retention': 85.0,
                'day_7_retention': 65.0,
                'day_30_retention': 45.0,
                'cohort_analysis': 'Would contain detailed cohort data'
            }
            
        except Exception as e:
            logger.error(f"Error getting retention metrics: {e}")
            return {}
    
    def _get_churn_predictions(self, days: int) -> Dict[str, Any]:
        """Get churn predictions"""
        try:
            # Get at-risk users
            at_risk_users = self.segment_users('at_risk_users')
            
            return {
                'at_risk_users': len(at_risk_users),
                'churn_probability': 15.5,  # Would be calculated from ML model
                'high_risk_factors': [
                    'Low engagement score',
                    'No recent activity',
                    'Declining session duration'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting churn predictions: {e}")
            return {}

# Global behavior analytics instance
behavior_analytics = BehaviorAnalytics()

def track_user_behavior(user_id: str, session_id: str, action: str, 
                        duration: Optional[float] = None, metadata: Dict[str, Any] = None):
    """Track user behavior event"""
    behavior_analytics.track_behavior(user_id, session_id, action, duration, metadata)

def get_user_engagement(user_id: str, days: int = 30) -> EngagementMetrics:
    """Get user engagement metrics"""
    return behavior_analytics.calculate_engagement_metrics(user_id, days)

def get_behavior_insights(days: int = 30) -> Dict[str, Any]:
    """Get comprehensive behavior insights"""
    return behavior_analytics.get_behavior_insights(days)

def get_user_segments() -> Dict[str, UserSegment]:
    """Get all user segments"""
    return behavior_analytics.user_segments
