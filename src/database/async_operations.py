"""
Helm AI Async Database Operations
This module provides asynchronous database operations and background processing
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref

import aioredis
import asyncpg
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

T = TypeVar('T')

class OperationType(Enum):
    """Async operation types"""
    QUERY = "query"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BATCH = "batch"
    MIGRATION = "migration"
    BACKUP = "backup"
    CLEANUP = "cleanup"

class OperationStatus(Enum):
    """Operation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AsyncOperation:
    """Async operation definition"""
    operation_id: str
    operation_type: OperationType
    coroutine: Coroutine
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: OperationStatus = OperationStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300

@dataclass
class BatchOperation:
    """Batch database operation"""
    operation_id: str
    operation_type: OperationType
    queries: List[str]
    params_list: List[tuple]
    chunk_size: int = 1000
    progress: int = 0
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    errors: List[Exception] = field(default_factory=list)

class AsyncDatabaseManager:
    """Asynchronous database operations manager"""
    
    def __init__(self):
        self.operation_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running_operations: Dict[str, AsyncOperation] = {}
        self.completed_operations: Dict[str, AsyncOperation] = {}
        self.batch_operations: Dict[str, BatchOperation] = {}
        
        # Configuration
        self.max_concurrent_operations = int(os.getenv('MAX_CONCURRENT_ASYNC_OPS', '10'))
        self.operation_timeout = int(os.getenv('ASYNC_OP_TIMEOUT', '300'))
        self.cleanup_interval = int(os.getenv('ASYNC_CLEANUP_INTERVAL', '3600'))
        
        # Database connections
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.sqlite_connection: Optional[aiosqlite.Connection] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_concurrent_operations)
        
        # Background tasks
        self.processor_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("Async database manager initialized")
    
    async def initialize(self):
        """Initialize async database connections"""
        try:
            # Initialize PostgreSQL connection pool
            if os.getenv('DB_TYPE') == 'postgresql':
                self.postgres_pool = await asyncpg.create_pool(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=int(os.getenv('DB_PORT', '5432')),
                    database=os.getenv('DB_NAME', 'helm_ai'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', ''),
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("PostgreSQL async pool initialized")
            
            # Initialize SQLite connection
            if os.getenv('DB_TYPE') == 'sqlite':
                db_path = os.getenv('DB_PATH', '/var/lib/helm-ai/database.db')
                self.sqlite_connection = await aiosqlite.connect(db_path)
                await self.sqlite_connection.execute("PRAGMA journal_mode=WAL")
                await self.sqlite_connection.execute("PRAGMA synchronous=NORMAL")
                logger.info("SQLite async connection initialized")
            
            # Initialize Redis connection
            if os.getenv('REDIS_URL'):
                self.redis_client = await aioredis.from_url(os.getenv('REDIS_URL'))
                logger.info("Redis async connection initialized")
            
            # Start background tasks
            self.processor_task = asyncio.create_task(self._process_operations())
            self.cleanup_task = asyncio.create_task(self._cleanup_completed_operations())
            
        except Exception as e:
            logger.error(f"Failed to initialize async database manager: {e}")
            raise
    
    async def submit_operation(self, 
                              operation_type: OperationType,
                              coroutine: Coroutine,
                              priority: int = 0,
                              max_retries: int = 3,
                              timeout_seconds: int = 300) -> str:
        """Submit async operation for processing"""
        operation_id = f"op_{int(time.time() * 1000)}_{len(self.running_operations)}"
        
        operation = AsyncOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            coroutine=coroutine,
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds
        )
        
        # Add to queue (negative priority for higher priority)
        await self.operation_queue.put((-priority, operation))
        
        logger.info(f"Submitted async operation {operation_id} of type {operation_type.value}")
        return operation_id
    
    async def execute_query(self, 
                          query: str, 
                          params: tuple = None,
                          priority: int = 0) -> str:
        """Execute query asynchronously"""
        async def query_coroutine():
            if self.postgres_pool:
                async with self.postgres_pool.acquire() as conn:
                    if params:
                        return await conn.fetch(query, *params)
                    else:
                        return await conn.fetch(query)
            elif self.sqlite_connection:
                if params:
                    cursor = await self.sqlite_connection.execute(query, params)
                else:
                    cursor = await self.sqlite_connection.execute(query)
                return await cursor.fetchall()
            else:
                raise RuntimeError("No database connection available")
        
        return await self.submit_operation(
            OperationType.QUERY,
            query_coroutine(),
            priority
        )
    
    async def execute_batch(self,
                          operation_type: OperationType,
                          queries: List[str],
                          params_list: List[tuple],
                          chunk_size: int = 1000,
                          priority: int = 0) -> str:
        """Execute batch operations asynchronously"""
        operation_id = f"batch_{int(time.time() * 1000)}"
        
        batch_op = BatchOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            queries=queries,
            params_list=params_list,
            chunk_size=chunk_size,
            total_items=len(queries)
        )
        
        self.batch_operations[operation_id] = batch_op
        
        async def batch_coroutine():
            return await self._process_batch_operation(batch_op)
        
        await self.submit_operation(
            operation_type,
            batch_coroutine(),
            priority
        )
        
        return operation_id
    
    async def _process_batch_operation(self, batch_op: BatchOperation) -> Dict[str, Any]:
        """Process batch operation"""
        results = {
            'operation_id': batch_op.operation_id,
            'total_items': batch_op.total_items,
            'completed_items': 0,
            'failed_items': 0,
            'errors': []
        }
        
        try:
            for i in range(0, len(batch_op.queries), batch_op.chunk_size):
                chunk_queries = batch_op.queries[i:i + batch_op.chunk_size]
                chunk_params = batch_op.params_list[i:i + batch_op.chunk_size]
                
                if self.postgres_pool:
                    async with self.postgres_pool.acquire() as conn:
                        await conn.executemany(chunk_queries[0], chunk_params)
                elif self.sqlite_connection:
                    await self.sqlite_connection.executemany(chunk_queries[0], chunk_params)
                
                batch_op.completed_items += len(chunk_queries)
                batch_op.progress = (batch_op.completed_items / batch_op.total_items) * 100
                
                # Yield control to allow other operations
                await asyncio.sleep(0)
            
            results['completed_items'] = batch_op.completed_items
            
        except Exception as e:
            batch_op.failed_items = batch_op.total_items - batch_op.completed_items
            batch_op.errors.append(e)
            results['failed_items'] = batch_op.failed_items
            results['errors'] = [str(e) for e in batch_op.errors]
            raise
        
        finally:
            # Clean up batch operation
            if batch_op.operation_id in self.batch_operations:
                del self.batch_operations[batch_op.operation_id]
        
        return results
    
    async def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation status"""
        # Check running operations
        if operation_id in self.running_operations:
            op = self.running_operations[operation_id]
            return {
                'operation_id': op.operation_id,
                'operation_type': op.operation_type.value,
                'status': op.status.value,
                'created_at': op.created_at.isoformat(),
                'started_at': op.started_at.isoformat() if op.started_at else None,
                'progress': 0,
                'retry_count': op.retry_count,
                'error': str(op.error) if op.error else None
            }
        
        # Check completed operations
        if operation_id in self.completed_operations:
            op = self.completed_operations[operation_id]
            return {
                'operation_id': op.operation_id,
                'operation_type': op.operation_type.value,
                'status': op.status.value,
                'created_at': op.created_at.isoformat(),
                'started_at': op.started_at.isoformat() if op.started_at else None,
                'completed_at': op.completed_at.isoformat() if op.completed_at else None,
                'progress': 100,
                'retry_count': op.retry_count,
                'result': op.result,
                'error': str(op.error) if op.error else None
            }
        
        # Check batch operations
        if operation_id in self.batch_operations:
            batch_op = self.batch_operations[operation_id]
            return {
                'operation_id': batch_op.operation_id,
                'operation_type': batch_op.operation_type.value,
                'status': 'running',
                'created_at': datetime.now().isoformat(),
                'progress': batch_op.progress,
                'total_items': batch_op.total_items,
                'completed_items': batch_op.completed_items,
                'failed_items': batch_op.failed_items,
                'errors': [str(e) for e in batch_op.errors]
            }
        
        return None
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel operation"""
        if operation_id in self.running_operations:
            op = self.running_operations[operation_id]
            op.status = OperationStatus.CANCELLED
            
            # Move to completed
            self.completed_operations[operation_id] = op
            del self.running_operations[operation_id]
            
            logger.info(f"Cancelled operation {operation_id}")
            return True
        
        return False
    
    async def _process_operations(self):
        """Process operations from queue"""
        logger.info("Starting async operation processor")
        
        while True:
            try:
                # Get operation from queue
                priority, operation = await self.operation_queue.get()
                
                # Check if we're at capacity
                if len(self.running_operations) >= self.max_concurrent_operations:
                    # Put back in queue and wait
                    await self.operation_queue.put((priority, operation))
                    await asyncio.sleep(1)
                    continue
                
                # Start operation
                await self._execute_operation(operation)
                
            except Exception as e:
                logger.error(f"Operation processor error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_operation(self, operation: AsyncOperation):
        """Execute individual operation"""
        operation.status = OperationStatus.RUNNING
        operation.started_at = datetime.now()
        self.running_operations[operation.operation_id] = operation
        
        logger.info(f"Executing operation {operation.operation_id}")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                operation.coroutine,
                timeout=operation.timeout_seconds
            )
            
            operation.result = result
            operation.status = OperationStatus.COMPLETED
            operation.completed_at = datetime.now()
            
            logger.info(f"Operation {operation.operation_id} completed successfully")
            
        except asyncio.TimeoutError:
            operation.error = Exception("Operation timed out")
            operation.status = OperationStatus.FAILED
            operation.completed_at = datetime.now()
            
            logger.warning(f"Operation {operation.operation_id} timed out")
            
        except Exception as e:
            operation.error = e
            operation.status = OperationStatus.FAILED
            operation.completed_at = datetime.now()
            
            # Retry if allowed
            if operation.retry_count < operation.max_retries:
                operation.retry_count += 1
                operation.status = OperationStatus.PENDING
                operation.started_at = None
                operation.error = None
                
                # Re-queue with lower priority
                await self.operation_queue.put((-operation.priority - 1, operation))
                
                logger.info(f"Retrying operation {operation.operation_id} (attempt {operation.retry_count})")
                return
            
            logger.error(f"Operation {operation.operation_id} failed: {e}")
        
        finally:
            # Move from running to completed
            if operation.operation_id in self.running_operations:
                del self.running_operations[operation.operation_id]
            
            self.completed_operations[operation.operation_id] = operation
    
    async def _cleanup_completed_operations(self):
        """Clean up old completed operations"""
        logger.info("Starting async operation cleanup")
        
        while True:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=1)  # Keep operations for 1 hour
                
                # Remove old completed operations
                operations_to_remove = []
                for op_id, op in self.completed_operations.items():
                    if op.completed_at and op.completed_at < cutoff_time:
                        operations_to_remove.append(op_id)
                
                for op_id in operations_to_remove:
                    del self.completed_operations[op_id]
                
                if operations_to_remove:
                    logger.debug(f"Cleaned up {len(operations_to_remove)} old operations")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(300)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get async operation statistics"""
        return {
            'running_operations': len(self.running_operations),
            'completed_operations': len(self.completed_operations),
            'batch_operations': len(self.batch_operations),
            'queue_size': self.operation_queue.qsize(),
            'max_concurrent_operations': self.max_concurrent_operations,
            'operations_by_type': self._get_operations_by_type(),
            'operations_by_status': self._get_operations_by_status(),
            'avg_execution_time': self._get_avg_execution_time()
        }
    
    def _get_operations_by_type(self) -> Dict[str, int]:
        """Get operations count by type"""
        type_counts = {}
        
        for op in list(self.running_operations.values()) + list(self.completed_operations.values()):
            op_type = op.operation_type.value
            type_counts[op_type] = type_counts.get(op_type, 0) + 1
        
        return type_counts
    
    def _get_operations_by_status(self) -> Dict[str, int]:
        """Get operations count by status"""
        status_counts = {
            'pending': 0,
            'running': len(self.running_operations),
            'completed': 0,
            'failed': 0,
            'cancelled': 0
        }
        
        for op in self.completed_operations.values():
            status_counts[op.status.value] += 1
        
        return status_counts
    
    def _get_avg_execution_time(self) -> float:
        """Get average execution time"""
        completed_ops = [
            op for op in self.completed_operations.values()
            if op.status == OperationStatus.COMPLETED and op.started_at and op.completed_at
        ]
        
        if not completed_ops:
            return 0.0
        
        total_time = sum(
            (op.completed_at - op.started_at).total_seconds()
            for op in completed_ops
        )
        
        return total_time / len(completed_ops)
    
    async def close(self):
        """Close async database manager"""
        # Cancel background tasks
        if self.processor_task:
            self.processor_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Close database connections
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.sqlite_connection:
            await self.sqlite_connection.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        # Close thread pool
        self.thread_pool.shutdown(wait=True)
        
        logger.info("Async database manager closed")


class BackgroundTaskManager:
    """Background task manager for database operations"""
    
    def __init__(self, async_manager: AsyncDatabaseManager):
        self.async_manager = async_manager
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background task scheduler"""
        self.task_scheduler_task = asyncio.create_task(self._task_scheduler())
        logger.info("Background task scheduler started")
    
    async def schedule_task(self,
                          task_name: str,
                          coroutine: Coroutine,
                          schedule: str,  # cron-like expression or interval in seconds
                          priority: int = 0) -> str:
        """Schedule background task"""
        task_id = f"task_{task_name}_{int(time.time())}"
        
        self.scheduled_tasks[task_id] = {
            'task_id': task_id,
            'task_name': task_name,
            'coroutine': coroutine,
            'schedule': schedule,
            'priority': priority,
            'last_run': None,
            'next_run': self._calculate_next_run(schedule),
            'enabled': True
        }
        
        logger.info(f"Scheduled background task {task_name} with ID {task_id}")
        return task_id
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time for task"""
        try:
            # Simple interval scheduling (can be extended to support cron)
            interval_seconds = int(schedule)
            return datetime.now() + timedelta(seconds=interval_seconds)
        except ValueError:
            # For now, default to 1 hour
            return datetime.now() + timedelta(hours=1)
    
    async def _task_scheduler(self):
        """Background task scheduler"""
        logger.info("Starting background task scheduler")
        
        while True:
            try:
                current_time = datetime.now()
                
                # Check for tasks to run
                for task_id, task_info in list(self.scheduled_tasks.items()):
                    if (task_info['enabled'] and 
                        task_info['next_run'] and 
                        current_time >= task_info['next_run']):
                        
                        # Submit task to async manager
                        await self.async_manager.submit_operation(
                            OperationType.CLEANUP,  # Default type for background tasks
                            task_info['coroutine'],
                            task_info['priority']
                        )
                        
                        # Update schedule
                        task_info['last_run'] = current_time
                        task_info['next_run'] = self._calculate_next_run(task_info['schedule'])
                        
                        logger.info(f"Ran background task {task_info['task_name']}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(300)
    
    async def enable_task(self, task_id: str) -> bool:
        """Enable scheduled task"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id]['enabled'] = True
            return True
        return False
    
    async def disable_task(self, task_id: str) -> bool:
        """Disable scheduled task"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id]['enabled'] = False
            return True
        return False
    
    async def remove_task(self, task_id: str) -> bool:
        """Remove scheduled task"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            return True
        return False
    
    def get_scheduled_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all scheduled tasks"""
        return {
            task_id: {
                'task_name': info['task_name'],
                'schedule': info['schedule'],
                'enabled': info['enabled'],
                'last_run': info['last_run'].isoformat() if info['last_run'] else None,
                'next_run': info['next_run'].isoformat() if info['next_run'] else None
            }
            for task_id, info in self.scheduled_tasks.items()
        }


# Global async database manager
async_db_manager = AsyncDatabaseManager()
background_task_manager = BackgroundTaskManager(async_db_manager)
