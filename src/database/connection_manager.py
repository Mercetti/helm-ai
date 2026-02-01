# Helm AI - Optimized Database Connection Manager
"""
Advanced database connection management with connection pooling,
monitoring, and automatic retry logic.
"""

import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from src.common.exceptions import DatabaseException, SystemException

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Optimized database connection management with monitoring"""

    def __init__(
        self,
        db_url: str,
        pool_size: int = 20,
        max_overflow: int = 40,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        self.db_url = db_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

        self.engine = None
        self.session_factory = None
        self.connection_metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "connection_timeouts": 0,
            "pool_exhaustions": 0,
            "last_health_check": None
        }

        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with optimized settings"""
        try:
            # Set database-specific connection arguments
            connect_args = {}
            if not self.db_url.startswith("sqlite"):
                # Only set timeout args for non-SQLite databases
                connect_args = {
                    "connect_timeout": 10,
                    "read_timeout": 30,
                    "write_timeout": 30
                }

            self.engine = create_engine(
                self.db_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,  # Verify connections before using
                echo=self.echo,
                connect_args=connect_args
            )

            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )

            # Register connection event listeners
            self._register_event_listeners()

            logger.info(f"Database connection manager initialized: pool_size={self.pool_size}")

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise SystemException(
                "Database initialization failed",
                component="ConnectionManager",
                cause=e
            )

    def _register_event_listeners(self):
        """Register SQLAlchemy event listeners for monitoring"""
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            self.connection_metrics["total_connections"] += 1
            self.connection_metrics["active_connections"] += 1
            logger.debug(f"Database connection established: {id(dbapi_conn)}")

        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            self.connection_metrics["active_connections"] -= 1
            logger.debug(f"Database connection closed: {id(dbapi_conn)}")

        @event.listens_for(self.engine, "detach")
        def receive_detach(dbapi_conn, connection_record):
            self.connection_metrics["active_connections"] -= 1
            logger.warning(f"Database connection detached: {id(dbapi_conn)}")

    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup and error handling"""
        session = None
        try:
            session = self.session_factory()
            yield session
            session.commit()
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseException(
                "Database operation failed",
                operation="session_commit",
                cause=e
            )
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Unexpected session error: {e}")
            raise SystemException(
                "Session operation failed",
                component="ConnectionManager",
                cause=e
            )
        finally:
            if session:
                session.close()

    def get_connection(self):
        """Get raw database connection from pool"""
        try:
            return self.engine.raw_connection()
        except OperationalError as e:
            self.connection_metrics["failed_connections"] += 1
            logger.error(f"Failed to get database connection: {e}")
            raise DatabaseException(
                "Connection acquisition failed",
                operation="get_connection",
                cause=e
            )

    @contextmanager
    def get_connection_context(self):
        """Get database connection context manager"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                conn.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Dict] = None,
        fetch: bool = True
    ) -> Optional[List[Dict]]:
        """
        Execute raw SQL query with proper error handling.

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results if fetch=True, None otherwise
        """
        with self.get_session() as session:
            try:
                result = session.execute(text(query), params or {})

                if fetch:
                    # Convert to list of dicts
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]

                return None

            except SQLAlchemyError as e:
                logger.error(f"Query execution failed: {query}")
                raise DatabaseException(
                    "Query execution failed",
                    operation="execute_query",
                    cause=e
                )

    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            start_time = time.time()
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            response_time = time.time() - start_time

            self.connection_metrics["last_health_check"] = datetime.now(timezone.utc)

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "pool_status": self.get_pool_status(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        try:
            pool = self.engine.pool
            return {
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total": pool.size() + pool.overflow(),
                "available": pool.size() - pool.checkedout()
            }
        except Exception as e:
            logger.error(f"Failed to get pool status: {e}")
            return {"error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive connection metrics"""
        return {
            **self.connection_metrics,
            "pool_status": self.get_pool_status(),
            "health_status": self.health_check()
        }

    def cleanup(self):
        """Cleanup database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global connection manager instance
_connection_manager = None

def get_connection_manager(db_url: Optional[str] = None) -> ConnectionManager:
    """Get or create global connection manager instance"""
    global _connection_manager

    if _connection_manager is None:
        if db_url is None:
            raise ValueError("Database URL required for first initialization")

        _connection_manager = ConnectionManager(db_url)

    return _connection_manager

def init_database(db_url: str) -> ConnectionManager:
    """Initialize database connection manager"""
    return get_connection_manager(db_url)