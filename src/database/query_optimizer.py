"""
Helm AI Database Query Optimizer
This module provides database query optimization and performance tuning
"""

import os
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from collections import defaultdict
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database_manager import get_database_manager
from monitoring.structured_logging import logger

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Query types"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"

class OptimizationLevel(Enum):
    """Optimization levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class QueryPlan:
    """Query execution plan"""
    query: str
    plan_type: str
    cost: float
    rows: int
    width: int
    actual_time: Optional[float] = None
    planning_time: Optional[float] = None
    execution_time: Optional[float] = None
    indexes_used: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=dict)

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_hash: str
    query_type: QueryType
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    rows_returned: int = 0
    rows_examined: int = 0
    index_scans: int = 0
    index_hits: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_executed: Optional[datetime] = None
    slow_queries: List[float] = field(default_factory=list)

@dataclass
class IndexRecommendation:
    """Index recommendation"""
    table_name: str
    column_names: List[str]
    index_type: str
    estimated_benefit: float
    creation_sql: str
    reason: str
    priority: str  # high, medium, low

class QueryOptimizer:
    """Database query optimizer and analyzer"""
    
    def __init__(self):
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.query_plans: Dict[str, QueryPlan] = {}
        self.index_recommendations: List[IndexRecommendation] = []
        
        # Configuration
        self.db_type = os.getenv('DB_TYPE', 'postgresql')
        self.slow_query_threshold = float(os.getenv('SLOW_QUERY_THRESHOLD', '1.0'))  # seconds
        self.query_cache_ttl = int(os.getenv('QUERY_CACHE_TTL', '3600'))  # seconds
        
        # Database connection
        self.db_connection = None
        self._initialize_connection()
        
        # Redis for caching
        self.redis_client = None
        if os.getenv('REDIS_URL'):
            self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            # Skip database connection in test environment
            if os.getenv('ENVIRONMENT') == 'test' or os.getenv('TESTING') == 'true':
                logger.info("Skipping database connection in test environment")
                self.db_connection = None
                return
                
            if self.db_type == 'postgresql':
                self.db_connection = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5432'),
                    database=os.getenv('DB_NAME', 'helm_ai'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', ''),
                    cursor_factory=RealDictCursor
                )
            elif self.db_type == 'sqlite':
                self.db_connection = sqlite3.connect(
                    os.getenv('DB_PATH', '/var/lib/helm-ai/database.db'),
                    check_same_thread=False
                )
                self.db_connection.row_factory = sqlite3.Row
            
            logger.info(f"Connected to {self.db_type} database")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def analyze_query(self, query: str, params: Tuple = None) -> QueryPlan:
        """Analyze query execution plan"""
        query_hash = self._hash_query(query)
        
        try:
            if self.db_type == 'postgresql':
                plan = self._analyze_postgresql_query(query, params)
            elif self.db_type == 'sqlite':
                plan = self._analyze_sqlite_query(query, params)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            self.query_plans[query_hash] = plan
            return plan
            
        except Exception as e:
            logger.error(f"Failed to analyze query: {e}")
            return QueryPlan(
                query=query,
                plan_type="error",
                cost=0.0,
                rows=0,
                width=0,
                recommendations=[f"Analysis failed: {str(e)}"]
            )
    
    def _analyze_postgresql_query(self, query: str, params: Tuple = None) -> QueryPlan:
        """Analyze PostgreSQL query using EXPLAIN"""
        try:
            with self.db_connection.cursor() as cursor:
                # Get execution plan
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                cursor.execute(explain_query, params or ())
                result = cursor.fetchone()
                
                if result and 'plan' in result:
                    plan_data = result['plan']
                    
                    # Extract plan information
                    cost = plan_data.get('Total Cost', 0.0)
                    rows = plan_data.get('Plan Rows', 0)
                    width = plan_data.get('Plan Width', 0)
                    
                    # Extract execution time
                    execution_time = plan_data.get('Execution Time', 0.0)
                    planning_time = plan_data.get('Planning Time', 0.0)
                    actual_time = plan_data.get('Actual Total Time', 0.0)
                    
                    # Extract indexes used
                    indexes_used = self._extract_indexes_from_plan(plan_data)
                    
                    # Generate recommendations
                    recommendations = self._generate_recommendations(plan_data)
                    
                    return QueryPlan(
                        query=query,
                        plan_type=plan_data.get('Node Type', 'unknown'),
                        cost=cost,
                        rows=rows,
                        width=width,
                        actual_time=actual_time,
                        planning_time=planning_time,
                        execution_time=execution_time,
                        indexes_used=indexes_used,
                        recommendations=recommendations
                    )
                
        except Exception as e:
            logger.error(f"PostgreSQL query analysis failed: {e}")
            raise
    
    def _analyze_sqlite_query(self, query: str, params: Tuple = None) -> QueryPlan:
        """Analyze SQLite query using EXPLAIN QUERY PLAN"""
        try:
            cursor = self.db_connection.cursor()
            
            # Get query plan
            cursor.execute(f"EXPLAIN QUERY PLAN {query}", params or ())
            plan_rows = cursor.fetchall()
            
            # Parse plan information
            plan_type = plan_rows[0]['detail'] if plan_rows else 'unknown'
            
            return QueryPlan(
                query=query,
                plan_type=plan_type,
                cost=0.0,  # SQLite doesn't provide cost
                rows=0,
                width=0,
                recommendations=self._generate_sqlite_recommendations(plan_rows)
            )
            
        except Exception as e:
            logger.error(f"SQLite query analysis failed: {e}")
            raise
    
    def _extract_indexes_from_plan(self, plan_data: Dict[str, Any]) -> List[str]:
        """Extract index names from PostgreSQL plan"""
        indexes = []
        
        def extract_from_node(node):
            if 'Index Name' in node:
                indexes.append(node['Index Name'])
            
            if 'Plans' in node:
                for sub_plan in node['Plans']:
                    extract_from_node(sub_plan)
        
        extract_from_node(plan_data)
        return indexes
    
    def _generate_recommendations(self, plan_data: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for sequential scans
        if plan_data.get('Node Type') == 'Seq Scan':
            table_name = plan_data.get('Relation Name', 'unknown')
            recommendations.append(f"Consider adding an index on table '{table_name}' to avoid sequential scan")
        
        # Check for high cost
        if plan_data.get('Total Cost', 0) > 1000:
            recommendations.append("Query has high cost - consider optimizing or adding indexes")
        
        # Check for sort operations
        if plan_data.get('Node Type') == 'Sort':
            recommendations.append("Consider adding an index to avoid sorting")
        
        # Check for hash joins
        if plan_data.get('Node Type') == 'Hash Join':
            recommendations.append("Consider optimizing join conditions or adding indexes")
        
        return recommendations
    
    def _generate_sqlite_recommendations(self, plan_rows: List) -> List[str]:
        """Generate SQLite-specific recommendations"""
        recommendations = []
        
        for row in plan_rows:
            detail = row['detail']
            
            if 'SCAN TABLE' in detail:
                recommendations.append("Consider adding an index to avoid full table scan")
            elif 'USING INDEX' in detail:
                # Index is being used - good
                pass
            elif 'TEMP B-TREE' in detail:
                recommendations.append("Consider adding an index to avoid temporary B-tree")
        
        return recommendations
    
    def execute_query_with_metrics(self, query: str, params: Tuple = None, fetch: str = 'all') -> Any:
        """Execute query and collect performance metrics"""
        query_hash = self._hash_query(query)
        query_type = self._detect_query_type(query)
        
        start_time = time.time()
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, params or ())
                
                # Fetch results based on fetch parameter
                if fetch == 'all':
                    result = cursor.fetchall()
                elif fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'many':
                    result = cursor.fetchmany()
                else:
                    result = None
                
                # Get row count
                if hasattr(cursor, 'rowcount'):
                    rows_returned = cursor.rowcount
                else:
                    rows_returned = len(result) if result else 0
                
                execution_time = time.time() - start_time
                
                # Update metrics
                self._update_query_metrics(query_hash, query_type, execution_time, rows_returned)
                
                # Log slow queries
                if execution_time > self.slow_query_threshold:
                    logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
                    self._log_slow_query(query, execution_time, params)
                
                return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query failed after {execution_time:.3f}s: {e}")
            raise
    
    def _update_query_metrics(self, query_hash: str, query_type: QueryType, execution_time: float, rows_returned: int):
        """Update query performance metrics"""
        if query_hash not in self.query_metrics:
            self.query_metrics[query_hash] = QueryMetrics(
                query_hash=query_hash,
                query_type=query_type
            )
        
        metrics = self.query_metrics[query_hash]
        metrics.execution_count += 1
        metrics.total_time += execution_time
        metrics.avg_time = metrics.total_time / metrics.execution_count
        metrics.min_time = min(metrics.min_time, execution_time)
        metrics.max_time = max(metrics.max_time, execution_time)
        metrics.rows_returned += rows_returned
        metrics.last_executed = datetime.now()
        
        # Track slow queries
        if execution_time > self.slow_query_threshold:
            metrics.slow_queries.append(execution_time)
            # Keep only last 10 slow queries
            if len(metrics.slow_queries) > 10:
                metrics.slow_queries.pop(0)
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detect query type from SQL string"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        else:
            return QueryType.SELECT  # Default
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query identification"""
        # Normalize query (remove extra whitespace, convert to uppercase)
        normalized = ' '.join(query.split()).upper()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _log_slow_query(self, query: str, execution_time: float, params: Tuple = None):
        """Log slow query details"""
        slow_query_data = {
            'query': query,
            'execution_time': execution_time,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log to file
        slow_query_log = os.getenv('SLOW_QUERY_LOG', '/var/log/helm-ai/slow_queries.log')
        try:
            with open(slow_query_log, 'a') as f:
                f.write(json.dumps(slow_query_data) + '\n')
        except Exception as e:
            logger.error(f"Failed to log slow query: {e}")
    
    def recommend_indexes(self, table_name: str = None) -> List[IndexRecommendation]:
        """Generate index recommendations for tables"""
        recommendations = []
        
        try:
            if self.db_type == 'postgresql':
                recommendations = self._analyze_postgresql_indexes(table_name)
            elif self.db_type == 'sqlite':
                recommendations = self._analyze_sqlite_indexes(table_name)
            
            self.index_recommendations = recommendations
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate index recommendations: {e}")
            return []
    
    def _analyze_postgresql_indexes(self, table_name: str = None) -> List[IndexRecommendation]:
        """Analyze PostgreSQL tables for index recommendations"""
        recommendations = []
        
        try:
            with self.db_connection.cursor() as cursor:
                # Get table statistics
                if table_name:
                    tables = [table_name]
                else:
                    cursor.execute("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """)
                    tables = [row['tablename'] for row in cursor.fetchall()]
                
                for table in tables:
                    # Get table size and row count
                    cursor.execute(f"""
                        SELECT 
                            pg_size_pretty(pg_total_relation_size('{table}')) as size,
                            (SELECT COUNT(*) FROM "{table}") as row_count
                    """)
                    stats = cursor.fetchone()
                    
                    # Get column statistics
                    cursor.execute(f"""
                        SELECT 
                            column_name,
                            data_type,
                            n_distinct,
                            null_frac
                        FROM pg_stats 
                        WHERE tablename = '{table}'
                    """)
                    columns = cursor.fetchall()
                    
                    # Analyze columns for index recommendations
                    for col in columns:
                        col_name = col['column_name']
                        data_type = col['data_type']
                        n_distinct = col['n_distinct']
                        null_frac = col['null_frac']
                        
                        # Recommend index for high-cardinality columns
                        if n_distinct and n_distinct > 100 and null_frac < 0.1:
                            if data_type in ['integer', 'bigint', 'text', 'varchar']:
                                recommendations.append(IndexRecommendation(
                                    table_name=table,
                                    column_names=[col_name],
                                    index_type='btree',
                                    estimated_benefit=0.8,
                                    creation_sql=f"CREATE INDEX idx_{table}_{col_name} ON \"{table}\" ({col_name});",
                                    reason=f"High cardinality column {col_name} with good selectivity",
                                    priority='medium'
                                ))
                        
                        # Recommend composite index for common query patterns
                        if col_name in ['user_id', 'created_at', 'status', 'email']:
                            recommendations.append(IndexRecommendation(
                                table_name=table,
                                column_names=[col_name],
                                index_type='btree',
                                estimated_benefit=0.9,
                                creation_sql=f"CREATE INDEX idx_{table}_{col_name} ON \"{table}\" ({col_name});",
                                reason=f"Common query column {col_name}",
                                priority='high'
                            ))
                
        except Exception as e:
            logger.error(f"PostgreSQL index analysis failed: {e}")
        
        return recommendations
    
    def _analyze_sqlite_indexes(self, table_name: str = None) -> List[IndexRecommendation]:
        """Analyze SQLite tables for index recommendations"""
        recommendations = []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get table list
            if table_name:
                tables = [table_name]
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # Get existing indexes
                cursor.execute(f"PRAGMA index_list({table})")
                existing_indexes = [row[1] for row in cursor.fetchall()]
                
                # Analyze columns for index recommendations
                for col in columns:
                    col_name = col[1]
                    data_type = col[2]
                    
                    # Recommend index for common query columns
                    if col_name in ['id', 'user_id', 'created_at', 'status', 'email']:
                        index_name = f"idx_{table}_{col_name}"
                        if index_name not in existing_indexes:
                            recommendations.append(IndexRecommendation(
                                table_name=table,
                                column_names=[col_name],
                                index_type='btree',
                                estimated_benefit=0.8,
                                creation_sql=f"CREATE INDEX {index_name} ON {table} ({col_name});",
                                reason=f"Common query column {col_name}",
                                priority='high'
                            ))
                
        except Exception as e:
            logger.error(f"SQLite index analysis failed: {e}")
        
        return recommendations
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        stats = {
            'total_queries': len(self.query_metrics),
            'total_executions': sum(m.execution_count for m in self.query_metrics.values()),
            'avg_execution_time': 0.0,
            'slow_queries': 0,
            'queries_by_type': {},
            'top_slow_queries': [],
            'index_recommendations': len(self.index_recommendations)
        }
        
        if self.query_metrics:
            total_time = sum(m.total_time for m in self.query_metrics.values())
            total_executions = sum(m.execution_count for m in self.query_metrics.values())
            stats['avg_execution_time'] = total_time / total_executions if total_executions > 0 else 0
            
            # Count by type
            for metrics in self.query_metrics.values():
                query_type = metrics.query_type.value
                stats['queries_by_type'][query_type] = stats['queries_by_type'].get(query_type, 0) + metrics.execution_count
            
            # Count slow queries
            stats['slow_queries'] = sum(len(m.slow_queries) for m in self.query_metrics.values())
            
            # Get top slow queries
            slow_queries = sorted(
                [(hash_val, m.avg_time, m.execution_count) for hash_val, m in self.query_metrics.items() if m.slow_queries],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            stats['top_slow_queries'] = [
                {
                    'query_hash': hash_val,
                    'avg_time': avg_time,
                    'execution_count': exec_count
                }
                for hash_val, avg_time, exec_count in slow_queries
            ]
        
        return stats
    
    def optimize_query(self, query: str, level: OptimizationLevel = OptimizationLevel.INTERMEDIATE) -> str:
        """Optimize SQL query based on level"""
        optimized_query = query
        
        if level == OptimizationLevel.BASIC:
            optimized_query = self._basic_optimization(optimized_query)
        elif level == OptimizationLevel.INTERMEDIATE:
            optimized_query = self._basic_optimization(optimized_query)
            optimized_query = self._intermediate_optimization(optimized_query)
        elif level == OptimizationLevel.ADVANCED:
            optimized_query = self._basic_optimization(optimized_query)
            optimized_query = self._intermediate_optimization(optimized_query)
            optimized_query = self._advanced_optimization(optimized_query)
        
        return optimized_query
    
    def _basic_optimization(self, query: str) -> str:
        """Basic query optimizations"""
        # Remove unnecessary whitespace
        query = ' '.join(query.split())
        
        # Convert SELECT * to specific columns (simplified)
        if 'SELECT *' in query:
            # This is a simplified approach - in practice, you'd analyze the schema
            query = query.replace('SELECT *', 'SELECT id, created_at, updated_at')
        
        return query
    
    def _intermediate_optimization(self, query: str) -> str:
        """Intermediate query optimizations"""
        # Add LIMIT if not present for SELECT queries
        if query.upper().startswith('SELECT') and 'LIMIT' not in query.upper():
            query += ' LIMIT 1000'
        
        # Optimize JOIN conditions (simplified)
        if 'JOIN' in query.upper():
            # Ensure join conditions use indexed columns
            pass
        
        return query
    
    def _advanced_optimization(self, query: str) -> str:
        """Advanced query optimizations"""
        # Add query hints for PostgreSQL
        if self.db_type == 'postgresql':
            # Add appropriate hints based on query analysis
            pass
        
        return query
    
    def create_missing_indexes(self, priority: str = 'high') -> List[str]:
        """Create recommended indexes"""
        created_indexes = []
        
        try:
            recommendations = [r for r in self.index_recommendations if r.priority == priority]
            
            with self.db_connection.cursor() as cursor:
                for rec in recommendations:
                    try:
                        cursor.execute(rec.creation_sql)
                        self.db_connection.commit()
                        created_indexes.append(rec.creation_sql)
                        logger.info(f"Created index: {rec.creation_sql}")
                    except Exception as e:
                        logger.error(f"Failed to create index: {e}")
                        self.db_connection.rollback()
        
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
        
        return created_indexes


# Global instance
query_optimizer = QueryOptimizer()
