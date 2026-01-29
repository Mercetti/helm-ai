"""
Helm AI Database Connection Pool
This module provides database connection pooling and management
"""

import os
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import queue
import weakref
import psycopg2
from psycopg2 import pool, OperationalError
import sqlite3
import contextlib

logger = logging.getLogger(__name__)

class PoolStatus(Enum):
    """Connection pool status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CLOSED = "closed"

@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    created_at: datetime
    last_used: datetime
    usage_count: int = 0
    total_query_time: float = 0.0
    avg_query_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None

@dataclass
class PoolStatistics:
    """Connection pool statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_wait_time: float = 0.0
    max_wait_time: float = 0.0
    avg_connection_lifetime: float = 0.0
    connection_errors: List[str] = field(default_factory=list)

class DatabaseConnection:
    """Wrapper for database connection with metrics"""
    
    def __init__(self, connection, pool_ref: weakref.ref):
        self.connection = connection
        self.pool_ref = pool_ref
        self.metrics = ConnectionMetrics(
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        self.in_use = False
        self.last_health_check = datetime.now()
    
    def __getattr__(self, name):
        """Delegate attribute access to underlying connection"""
        return getattr(self.connection, name)
    
    def execute(self, query: str, params: tuple = None):
        """Execute query with timing"""
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time)
            
            return cursor
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            raise
    
    def executemany(self, query: str, params_list: List[tuple]):
        """Execute multiple queries with timing"""
        start_time = time.time()
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time)
            
            return cursor
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            raise
    
    def _update_metrics(self, execution_time: float):
        """Update connection metrics"""
        self.metrics.last_used = datetime.now()
        self.metrics.usage_count += 1
        self.metrics.total_query_time += execution_time
        self.metrics.avg_query_time = self.metrics.total_query_time / self.metrics.usage_count
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        try:
            # Simple health check
            cursor = self.connection.cursor()
            if hasattr(self.connection, 'database'):  # PostgreSQL
                cursor.execute("SELECT 1")
            else:  # SQLite
                cursor.execute("SELECT 1")
            cursor.close()
            
            self.last_health_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Connection health check failed: {e}")
            return False
    
    def close(self):
        """Close connection"""
        try:
            self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")


class ConnectionPool:
    """Generic database connection pool"""
    
    def __init__(self,
                 min_connections: int = 5,
                 max_connections: int = 20,
                 connection_timeout: int = 30,
                 idle_timeout: int = 300,
                 max_lifetime: int = 3600,
                 health_check_interval: int = 60):
        
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime
        self.health_check_interval = health_check_interval
        
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections: Dict[int, DatabaseConnection] = {}
        self.statistics = PoolStatistics()
        self.status = PoolStatus.HEALTHY
        self.lock = threading.RLock()
        self.closed = False
        
        # Background threads
        self._start_maintenance_thread()
        
        # Initialize minimum connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize pool with minimum connections"""
        logger.info(f"Initializing connection pool with {self.min_connections} connections")
        
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                self.pool.put(conn)
                self.statistics.total_connections += 1
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")
                self.statistics.failed_connections += 1
    
    def _create_connection(self) -> DatabaseConnection:
        """Create new database connection"""
        raise NotImplementedError("Subclasses must implement _create_connection")
    
    def get_connection(self, timeout: Optional[int] = None) -> DatabaseConnection:
        """Get connection from pool"""
        if self.closed:
            raise RuntimeError("Connection pool is closed")
        
        timeout = timeout or self.connection_timeout
        start_time = time.time()
        
        try:
            self.statistics.total_requests += 1
            
            # Try to get existing connection
            try:
                conn = self.pool.get(timeout=timeout)
            except queue.Empty:
                # Pool is empty, try to create new connection
                if len(self.active_connections) < self.max_connections:
                    conn = self._create_connection()
                    self.statistics.total_connections += 1
                else:
                    # Wait for connection to become available
                    conn = self.pool.get(timeout=timeout)
            
            # Check if connection is healthy
            if not conn.is_healthy():
                logger.warning("Unhealthy connection detected, creating new one")
                conn.close()
                conn = self._create_connection()
                self.statistics.total_connections += 1
            
            # Register as active
            self.active_connections[id(conn)] = conn
            conn.in_use = True
            
            # Update statistics
            wait_time = time.time() - start_time
            self.statistics.successful_requests += 1
            self.statistics.avg_wait_time = (
                (self.statistics.avg_wait_time * (self.statistics.successful_requests - 1) + wait_time) /
                self.statistics.successful_requests
            )
            self.statistics.max_wait_time = max(self.statistics.max_wait_time, wait_time)
            
            return conn
            
        except Exception as e:
            self.statistics.failed_requests += 1
            self.statistics.connection_errors.append(str(e))
            logger.error(f"Failed to get connection: {e}")
            raise
    
    def return_connection(self, conn: DatabaseConnection):
        """Return connection to pool"""
        with self.lock:
            if id(conn) in self.active_connections:
                del self.active_connections[id(conn)]
                conn.in_use = False
                
                # Check if connection should be discarded
                if self._should_discard_connection(conn):
                    conn.close()
                    self.statistics.total_connections -= 1
                    # Create new connection to maintain minimum
                    if self.pool.qsize() < self.min_connections:
                        try:
                            new_conn = self._create_connection()
                            self.pool.put(new_conn)
                            self.statistics.total_connections += 1
                        except Exception as e:
                            logger.error(f"Failed to create replacement connection: {e}")
                else:
                    self.pool.put(conn)
    
    def _should_discard_connection(self, conn: DatabaseConnection) -> bool:
        """Check if connection should be discarded"""
        # Check age
        age = (datetime.now() - conn.metrics.created_at).total_seconds()
        if age > self.max_lifetime:
            return True
        
        # Check error count
        if conn.metrics.error_count > 5:
            return True
        
        # Check last error time
        if conn.metrics.last_error and (datetime.now() - conn.metrics.last_used).total_seconds() < 60:
            return True
        
        return False
    
    @contextlib.contextmanager
    def get_connection_context(self, timeout: Optional[int] = None):
        """Context manager for getting and returning connection"""
        conn = None
        try:
            conn = self.get_connection(timeout)
            yield conn
        finally:
            if conn:
                self.return_connection(conn)
    
    def close(self):
        """Close connection pool"""
        self.closed = True
        self.status = PoolStatus.CLOSED
        
        # Close all connections
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
        
        # Close active connections
        for conn in self.active_connections.values():
            conn.close()
        
        self.active_connections.clear()
        logger.info("Connection pool closed")
    
    def get_statistics(self) -> PoolStatistics:
        """Get pool statistics"""
        with self.lock:
            self.statistics.total_connections = len(self.active_connections) + self.pool.qsize()
            self.statistics.active_connections = len(self.active_connections)
            self.statistics.idle_connections = self.pool.qsize()
            
            # Calculate average connection lifetime
            if self.statistics.total_connections > 0:
                total_age = sum(
                    (datetime.now() - conn.metrics.created_at).total_seconds()
                    for conn in list(self.active_connections.values()) + list(self.pool.queue)
                )
                self.statistics.avg_connection_lifetime = total_age / self.statistics.total_connections
            
            return self.statistics
    
    def _start_maintenance_thread(self):
        """Start background maintenance thread"""
        def maintenance():
            while not self.closed:
                try:
                    self._perform_maintenance()
                    threading.Event().wait(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Pool maintenance error: {e}")
                    threading.Event().wait(60)
        
        maintenance_thread = threading.Thread(target=maintenance, daemon=True)
        maintenance_thread.start()
    
    def _perform_maintenance(self):
        """Perform pool maintenance"""
        with self.lock:
            # Remove idle connections that have timed out
            connections_to_remove = []
            
            # Check pool queue
            temp_connections = []
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    idle_time = (datetime.now() - conn.metrics.last_used).total_seconds()
                    
                    if idle_time > self.idle_timeout:
                        connections_to_remove.append(conn)
                    else:
                        temp_connections.append(conn)
                except queue.Empty:
                    break
            
            # Put back valid connections
            for conn in temp_connections:
                self.pool.put(conn)
            
            # Close timed out connections
            for conn in connections_to_remove:
                conn.close()
                self.statistics.total_connections -= 1
            
            # Ensure minimum connections
            current_total = len(self.active_connections) + self.pool.qsize()
            if current_total < self.min_connections:
                for _ in range(self.min_connections - current_total):
                    try:
                        conn = self._create_connection()
                        self.pool.put(conn)
                        self.statistics.total_connections += 1
                    except Exception as e:
                        logger.error(f"Failed to create maintenance connection: {e}")
                        break
            
            # Update pool status
            self._update_pool_status()
            
            if connections_to_remove:
                logger.debug(f"Removed {len(connections_to_remove)} idle connections")
    
    def _update_pool_status(self):
        """Update pool health status"""
        stats = self.get_statistics()
        
        if stats.failed_requests > stats.successful_requests * 0.1:  # > 10% failure rate
            self.status = PoolStatus.UNHEALTHY
        elif stats.failed_requests > 0:
            self.status = PoolStatus.DEGRADED
        else:
            self.status = PoolStatus.HEALTHY


class PostgreSQLConnectionPool(ConnectionPool):
    """PostgreSQL connection pool"""
    
    def __init__(self, **kwargs):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'helm_ai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'application_name': 'helm_ai_pool'
        }
        
        super().__init__(**kwargs)
    
    def _create_connection(self) -> DatabaseConnection:
        """Create PostgreSQL connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            
            # Set connection parameters
            with conn.cursor() as cursor:
                cursor.execute("SET application_name TO 'helm_ai_pool'")
                cursor.execute("SET statement_timeout TO '30s'")
            
            return DatabaseConnection(conn, weakref.ref(self))
            
        except OperationalError as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise


class SQLiteConnectionPool(ConnectionPool):
    """SQLite connection pool"""
    
    def __init__(self, db_path: str = None, **kwargs):
        self.db_path = db_path or os.getenv('DB_PATH', '/var/lib/helm-ai/database.db')
        super().__init__(**kwargs)
    
    def _create_connection(self) -> DatabaseConnection:
        """Create SQLite connection"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            
            return DatabaseConnection(conn, weakref.ref(self))
            
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            raise


class ConnectionPoolManager:
    """Manager for multiple connection pools"""
    
    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self.default_pool_name = None
    
    def create_postgresql_pool(self, 
                              name: str = "postgresql",
                              min_connections: int = 5,
                              max_connections: int = 20,
                              **kwargs) -> PostgreSQLConnectionPool:
        """Create PostgreSQL connection pool"""
        pool = PostgreSQLConnectionPool(
            min_connections=min_connections,
            max_connections=max_connections,
            **kwargs
        )
        
        self.pools[name] = pool
        if self.default_pool_name is None:
            self.default_pool_name = name
        
        logger.info(f"Created PostgreSQL pool '{name}'")
        return pool
    
    def create_sqlite_pool(self,
                          name: str = "sqlite",
                          db_path: str = None,
                          min_connections: int = 1,
                          max_connections: int = 10,
                          **kwargs) -> SQLiteConnectionPool:
        """Create SQLite connection pool"""
        pool = SQLiteConnectionPool(
            db_path=db_path,
            min_connections=min_connections,
            max_connections=max_connections,
            **kwargs
        )
        
        self.pools[name] = pool
        if self.default_pool_name is None:
            self.default_pool_name = name
        
        logger.info(f"Created SQLite pool '{name}'")
        return pool
    
    def get_pool(self, name: str = None) -> ConnectionPool:
        """Get connection pool by name"""
        pool_name = name or self.default_pool_name
        if pool_name not in self.pools:
            raise ValueError(f"Connection pool '{pool_name}' not found")
        return self.pools[pool_name]
    
    def get_connection(self, pool_name: str = None, timeout: Optional[int] = None) -> DatabaseConnection:
        """Get connection from specified pool"""
        pool = self.get_pool(pool_name)
        return pool.get_connection(timeout)
    
    @contextlib.contextmanager
    def get_connection_context(self, pool_name: str = None, timeout: Optional[int] = None):
        """Context manager for getting connection"""
        conn = None
        try:
            conn = self.get_connection(pool_name, timeout)
            yield conn
        finally:
            if conn:
                pool = self.get_pool(pool_name)
                pool.return_connection(conn)
    
    def close_all(self):
        """Close all connection pools"""
        for pool in self.pools.values():
            pool.close()
        self.pools.clear()
        logger.info("All connection pools closed")
    
    def get_all_statistics(self) -> Dict[str, PoolStatistics]:
        """Get statistics for all pools"""
        return {name: pool.get_statistics() for name, pool in self.pools.items()}
    
    def get_health_status(self) -> Dict[str, str]:
        """Get health status of all pools"""
        return {name: pool.status.value for name, pool in self.pools.items()}


# Global connection pool manager
connection_pool_manager = ConnectionPoolManager()
