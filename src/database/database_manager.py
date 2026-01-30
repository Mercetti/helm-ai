"""
Helm AI Database Manager
Integration layer between SQLAlchemy models and connection pool
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text

from .connection_pool import connection_pool_manager
from models import Base, User, APIKey, AuditLog, SecurityEvent, GameSession, APIUsageLog
from models.api_key import APIKeyStatus

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling SQLAlchemy operations"""
    
    def __init__(self, pool_name: str = "postgresql"):
        self.pool_name = pool_name
        self.engine = None
        self.session_factory = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pool"""
        try:
            # Get connection pool
            pool = connection_pool_manager.get_pool(self.pool_name)
            
            # Create engine URL from pool configuration
            if hasattr(pool, 'db_config'):
                # PostgreSQL pool
                db_config = pool.db_config
                engine_url = (
                    f"postgresql://{db_config['user']}:{db_config['password']}"
                    f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                )
            else:
                # SQLite pool
                engine_url = f"sqlite:///{pool.db_path}"
            
            # Create engine with connection pool
            self.engine = create_engine(
                engine_url,
                poolclass=None,  # We're using our own connection pool
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5,
                max_overflow=10
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            logger.info(f"Database manager initialized with pool: {self.pool_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_connection(self):
        """Get raw database connection from pool"""
        return connection_pool_manager.get_connection(self.pool_name)
    
    @contextmanager
    def get_connection_context(self):
        """Get database connection context manager"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                connection_pool_manager.return_connection(conn, self.pool_name)
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    # User operations
    def create_user(self, email: str, name: str, **kwargs) -> User:
        """Create new user"""
        with self.get_session() as session:
            try:
                user = User.create_user(email, name, **kwargs)
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created user: {email}")
                return user
            except IntegrityError as e:
                session.rollback()
                logger.error(f"User already exists: {email}")
                raise ValueError(f"User with email {email} already exists") from e
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to create user: {e}")
                raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.get_session() as session:
            return session.query(User).filter(User.email == email.lower()).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user"""
        with self.get_session() as session:
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    for key, value in kwargs.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    user.updated_at = datetime.now()
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Updated user: {user_id}")
                    return user
                return None
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to update user {user_id}: {e}")
                raise
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete)"""
        with self.get_session() as session:
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.deleted_at = datetime.now()
                    user.updated_at = datetime.now()
                    session.commit()
                    logger.info(f"Deleted user: {user_id}")
                    return True
                return False
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to delete user {user_id}: {e}")
                raise
    
    # API Key operations
    def create_api_key(self, user_id: int, name: str, **kwargs) -> tuple[APIKey, str]:
        """Create new API key"""
        with self.get_session() as session:
            try:
                api_key, key = APIKey.create_api_key(user_id, name, **kwargs)
                session.add(api_key)
                session.commit()
                session.refresh(api_key)
                logger.info(f"Created API key: {api_key.key_id}")
                return api_key, key
            except IntegrityError as e:
                session.rollback()
                logger.error(f"API key creation failed: {e}")
                raise ValueError(f"API key creation failed: {e}") from e
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to create API key: {e}")
                raise
    
    def get_api_key_by_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        with self.get_session() as session:
            return session.query(APIKey).filter(APIKey.key_id == key_id).first()
    
    def get_api_keys_by_user(self, user_id: int) -> List[APIKey]:
        """Get all API keys for user"""
        with self.get_session() as session:
            return session.query(APIKey).filter(APIKey.user_id == user_id).filter(APIKey.deleted_at.is_(None)).all()
    
    def update_api_key(self, key_id: str, **kwargs) -> Optional[APIKey]:
        """Update API key"""
        with self.get_session() as session:
            try:
                api_key = session.query(APIKey).filter(APIKey.key_id == key_id).first()
                if api_key:
                    for key, value in kwargs.items():
                        if hasattr(api_key, key):
                            setattr(api_key, key, value)
                    api_key.updated_at = datetime.now()
                    session.commit()
                    session.refresh(api_key)
                    logger.info(f"Updated API key: {key_id}")
                    return api_key
                return None
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to update API key {key_id}: {e}")
                raise
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke API key"""
        with self.get_session() as session:
            try:
                api_key = session.query(APIKey).filter(APIKey.key_id == key_id).first()
                if api_key:
                    api_key.revoke()
                    session.commit()
                    logger.info(f"Revoked API key: {key_id}")
                    return True
                return False
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to revoke API key {key_id}: {e}")
                raise
    
    # Audit Log operations
    def create_audit_log(self, **kwargs) -> AuditLog:
        """Create audit log entry"""
        with self.get_session() as session:
            try:
                audit_log = AuditLog.create_log(**kwargs)
                session.add(audit_log)
                session.commit()
                session.refresh(audit_log)
                return audit_log
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to create audit log: {e}")
                raise
    
    def get_audit_logs_by_user(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for user"""
        with self.get_session() as session:
            return (
                session.query(AuditLog)
                .filter(AuditLog.user_id == user_id)
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
                .all()
            )
    
    def get_audit_logs_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 1000) -> List[AuditLog]:
        """Get audit logs by date range"""
        with self.get_session() as session:
            return (
                session.query(AuditLog)
                .filter(AuditLog.created_at >= start_date)
                .filter(AuditLog.created_at <= end_date)
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
                .all()
            )
    
    # Security Event operations
    def create_security_event(self, **kwargs) -> SecurityEvent:
        """Create security event"""
        with self.get_session() as session:
            try:
                security_event = SecurityEvent.create_event(**kwargs)
                session.add(security_event)
                session.commit()
                session.refresh(security_event)
                return security_event
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to create security event: {e}")
                raise
    
    def get_security_events_by_user(self, user_id: int, limit: int = 100) -> List[SecurityEvent]:
        """Get security events for user"""
        with self.get_session() as session:
            return (
                session.query(SecurityEvent)
                .filter(SecurityEvent.user_id == user_id)
                .order_by(SecurityEvent.occurred_at.desc())
                .limit(limit)
                .all()
            )
    
    def get_security_events_by_severity(self, severity: SecuritySeverity, limit: int = 100) -> List[SecurityEvent]:
        """Get security events by severity"""
        with self.get_session() as session:
            return (
                session.query(SecurityEvent)
                .filter(SecurityEvent.severity == severity)
                .order_by(SecurityEvent.occurred_at.desc())
                .limit(limit)
                .all()
            )
    
    def get_unresolved_security_events(self, limit: int = 100) -> List[SecurityEvent]:
        """Get unresolved security events"""
        with self.get_session() as session:
            return (
                session.query(SecurityEvent)
                .filter(SecurityEvent.status.in_([EventStatus.NEW, EventStatus.INVESTIGATING]))
                .order_by(SecurityEvent.occurred_at.desc())
                .limit(limit)
                .all()
            )
    
    # Game Session operations
    def create_game_session(self, **kwargs) -> GameSession:
        """Create game session"""
        with self.get_session() as session:
            try:
                game_session = GameSession.create_session(**kwargs)
                session.add(game_session)
                session.commit()
                session.refresh(game_session)
                return game_session
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to create game session: {e}")
                raise
    
    def get_game_session_by_id(self, session_id: str) -> Optional[GameSession]:
        """Get game session by ID"""
        with self.get_session() as session:
            return session.query(GameSession).filter(GameSession.session_id == session_id).first()
    
    def get_game_sessions_by_user(self, user_id: int, limit: int = 100) -> List[GameSession]:
        """Get game sessions for user"""
        with self.get_session() as session:
            return (
                session.query(GameSession)
                .filter(GameSession.user_id == user_id)
                .order_by(GameSession.started_at.desc())
                .limit(limit)
                .all()
            )
    
    def get_active_game_sessions(self, limit: int = 100) -> List[GameSession]:
        """Get active game sessions"""
        with self.get_session() as session:
            return (
                session.query(GameSession)
                .filter(GameSession.status == GameSessionStatus.ACTIVE)
                .order_by(GameSession.started_at.desc())
                .limit(limit)
                .all()
            )
    
    def get_suspicious_game_sessions(self, limit: int = 100) -> List[GameSession]:
        """Get suspicious game sessions"""
        with self.get_session() as session:
            return (
                session.query(GameSession)
                .filter(GameSession.cheat_detection_status.in_([
                    CheatDetectionStatus.SUSPICIOUS, 
                    CheatDetectionStatus.DETECTED, 
                    CheatDetectionStatus.CONFIRMED
                ]))
                .order_by(GameSession.risk_score.desc())
                .limit(limit)
                .all()
            )
    
    # Statistics and reporting
    def get_user_count(self) -> int:
        """Get total user count"""
        with self.get_session() as session:
            return session.query(User).filter(User.deleted_at.is_(None)).count()
    
    def get_active_api_key_count(self) -> int:
        """Get active API key count"""
        with self.get_session() as session:
            return (
                session.query(APIKey)
                .filter(APIKey.status == APIKeyStatus.ACTIVE)
                .filter(APIKey.expires_at > datetime.now())
                .count()
            )
    
    def get_security_event_count(self, days: int = 30) -> int:
        """Get security event count for last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        with self.get_session() as session:
            return (
                session.query(SecurityEvent)
                .filter(SecurityEvent.occurred_at >= cutoff_date)
                .count()
            )
    
    def get_game_session_count(self, days: int = 7) -> int:
        """Get game session count for last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        with self.get_session() as session:
            return (
                session.query(GameSession)
                .filter(GameSession.started_at >= cutoff_date)
                .count()
            )
    
    def cleanup_old_data(self, days: int = 2555):
        """Clean up old data based on retention policies"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_session() as session:
            try:
                # Clean up old audit logs
                audit_count = (
                    session.query(AuditLog)
                    .filter(AuditLog.created_at < cutoff_date)
                    .delete()
                )
                
                # Clean up old security events (except critical ones)
                security_count = (
                    session.query(SecurityEvent)
                    .filter(
                        SecurityEvent.occurred_at < cutoff_date,
                        SecurityEvent.severity != SecuritySeverity.CRITICAL
                    )
                    .delete()
                )
                
                # Clean up old game sessions
                session_count = (
                    session.query(GameSession)
                    .filter(GameSession.ended_at < cutoff_date)
                    .delete()
                )
                
                session.commit()
                logger.info(f"Cleaned up old data: {audit_count} audit logs, {security_count} security events, {session_count} game sessions")
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Failed to cleanup old data: {e}")
                raise
    
    def execute_raw_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query and return results"""
        with self.get_connection_context() as conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch all rows
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return results
                
            except Exception as e:
                logger.error(f"Failed to execute SQL: {sql}")
                raise
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                # Get connection pool stats
                pool_stats = connection_pool_manager.get_all_statistics()
                
                return {
                    "status": "healthy",
                    "database": "connected",
                    "pool_stats": pool_stats,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global database manager instance (created lazily)
database_manager = None

def get_database_manager(pool_name: str = "postgresql"):
    """Get database manager instance"""
    global database_manager
    if database_manager is None:
        database_manager = DatabaseManager(pool_name)
    return database_manager
