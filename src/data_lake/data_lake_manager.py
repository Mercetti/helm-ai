"""
Helm AI Centralized Data Lake Architecture
Provides comprehensive data lake management with storage, processing, and analytics capabilities
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class DataFormat(Enum):
    """Data format enumeration"""
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    JSON = "json"
    CSV = "csv"
    DELTA = "delta"
    ICEBERG = "iceberg"
    HUDI = "hudi"

class StorageTier(Enum):
    """Storage tier enumeration"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataType(Enum):
    """Data type enumeration"""
    STRUCTURED = "structured"
    SEMI_STRUCTURED = "semi_structured"
    UNSTRUCTURED = "unstructured"
    STREAMING = "streaming"
    BATCH = "batch"
    REAL_TIME = "real_time"

@dataclass
class DataLakeZone:
    """Data lake zone definition"""
    zone_id: str
    name: str
    description: str
    tier: StorageTier
    storage_path: str
    data_format: DataFormat
    retention_days: int
    compression: str
    encryption: bool
    partitioning: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert zone to dictionary"""
        return {
            'zone_id': self.zone_id,
            'name': self.name,
            'description': self.description,
            'tier': self.tier.value,
            'storage_path': self.storage_path,
            'data_format': self.data_format.value,
            'retention_days': self.retention_days,
            'compression': self.compression,
            'encryption': self.encryption,
            'partitioning': self.partitioning,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class DataIngestionJob:
    """Data ingestion job definition"""
    job_id: str
    name: str
    source_type: str
    source_config: Dict[str, Any]
    target_zone_id: str
    data_format: DataFormat
    processing_config: Dict[str, Any]
    schedule: str
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    run_count: int
    success_count: int
    failure_count: int
    bytes_processed: int
    records_processed: int
    error_message: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'name': self.name,
            'source_type': self.source_type,
            'source_config': self.source_config,
            'target_zone_id': self.target_zone_id,
            'data_format': self.data_format.value,
            'processing_config': self.processing_config,
            'schedule': self.schedule,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'bytes_processed': self.bytes_processed,
            'records_processed': self.records_processed,
            'error_message': self.error_message,
            'metadata': self.metadata
        }

@dataclass
class DataQuery:
    """Data query definition"""
    query_id: str
    name: str
    description: str
    zone_ids: List[str]
    query_type: str
    query_sql: str
    parameters: Dict[str, Any]
    created_by: str
    created_at: datetime
    last_executed: Optional[datetime]
    execution_count: int
    avg_execution_time: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary"""
        return {
            'query_id': self.query_id,
            'name': self.name,
            'description': self.description,
            'zone_ids': self.zone_ids,
            'query_type': self.query_type,
            'query_sql': self.query_sql,
            'parameters': self.parameters,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'execution_count': self.execution_count,
            'avg_execution_time': self.avg_execution_time,
            'metadata': self.metadata
        }

class DataLakeManager:
    """Data lake management system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.zones: Dict[str, DataLakeZone] = {}
        self.ingestion_jobs: Dict[str, DataIngestionJob] = {}
        self.queries: Dict[str, DataQuery] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.data_lake_path = os.getenv('DATA_LAKE_PATH', 'data/lake')
        self.default_format = DataFormat.PARQUET
        self.default_compression = 'snappy'
        self.default_encryption = True
        self.max_query_execution_time = int(os.getenv('MAX_QUERY_EXECUTION_TIME', '300'))  # 5 minutes
        
        # Ensure data lake directory exists
        os.makedirs(self.data_lake_path, exist_ok=True)
        
        # Initialize default zones
        self._initialize_default_zones()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_zones(self) -> None:
        """Initialize default data lake zones"""
        # Bronze Zone (Hot)
        bronze_zone = DataLakeZone(
            zone_id="bronze",
            name="Bronze Zone",
            description="Hot storage for frequently accessed data",
            tier=StorageTier.HOT,
            storage_path=os.path.join(self.data_lake_path, "bronze"),
            data_format=DataFormat.PARQUET,
            retention_days=30,
            compression=self.default_compression,
            encryption=self.default_encryption,
            partitioning={
                "year": "string",
                "month": "string",
                "day": "string",
                "hour": "string"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Silver Zone (Warm)
        silver_zone = DataLakeZone(
            zone_id="silver",
            name="Silver Zone",
            description="Warm storage for occasionally accessed data",
            tier=StorageTier.WARM,
            storage_path=os.path.join(self.data_lake_path, "silver"),
            data_format=DataFormat.PARQUET,
            retention_days=365,
            compression=self.default_compression,
            encryption=self.default_encryption,
            partitioning={
                "year": "string",
                "month": "string"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Gold Zone (Cold)
        gold_zone = DataLakeZone(
            zone_id="gold",
            name="Gold Zone",
            description="Cold storage for infrequently accessed data",
            tier=StorageTier.COLD,
            storage_path=os.path.join(self.data_lake_path, "gold"),
            data_format=DataFormat.PARQUET,
            retention_days=365 * 7,  # 7 years
            compression=self.default_compression,
            encryption=self.default_encryption,
            partitioning={
                "year": "string"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Archive Zone
        archive_zone = DataLakeZone(
            zone_id="archive",
            name="Archive Zone",
            description="Archive storage for long-term retention",
            tier=StorageTier.ARCHIVE,
            storage_path=os.path.join(self.data_lake_path, "archive"),
            data_format=DataFormat.PARQUET,
            retention_days=365 * 10,  # 10 years
            compression=self.default_compression,
            encryption=self.default_encryption,
            partitioning={
                "year": "string"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Streaming Zone
        streaming_zone = DataLakeZone(
            zone_id="streaming",
            name="Streaming Zone",
            description="Real-time streaming data ingestion",
            tier=StorageTier.HOT,
            storage_path=os.path.join(self.data_lake_path, "streaming"),
            data_format=DataFormat.DELTA,
            retention_days=7,
            compression=self.default_compression,
            encryption=self.default_encryption,
            partitioning={
                "date": "string",
                "hour": "string"
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        # Add zones to registry
        self.zones[bronze_zone.zone_id] = bronze_zone
        self.zones[silver_zone.zone_id] = silver_zone
        self.zones[gold_zone.zone_id] = gold_zone
        self.zones[archive_zone.zone_id] = archive_zone
        self.zones[streaming_zone.zone_id] = streaming_zone
        
        # Create zone directories
        for zone in self.zones.values():
            os.makedirs(zone.storage_path, exist_ok=True)
            
            # Create partition directories
            for partition_key in zone.partitioning:
                partition_path = os.path.join(zone.storage_path, partition_key)
                os.makedirs(partition_path, exist_ok=True)
        
        logger.info(f"Initialized {len(self.zones)} default data lake zones")
    
    def create_zone(self, name: str, description: str, tier: StorageTier,
                    data_format: DataFormat, retention_days: int,
                    partitioning: Dict[str, Any], compression: Optional[str] = None,
                    encryption: Optional[bool] = None) -> DataLakeZone:
        """Create new data lake zone"""
        zone_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        zone = DataLakeZone(
            zone_id=zone_id,
            name=name,
            description=description,
            tier=tier,
            storage_path=os.path.join(self.data_lake_path, zone_id),
            data_format=data_format,
            retention_days=retention_days,
            compression=compression or self.default_compression,
            encryption=encryption if encryption is not None else self.default_encryption,
            partitioning=partitioning,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        
        with self.lock:
            self.zones[zone_id] = zone
        
        # Create zone directory structure
        os.makedirs(zone.storage_path, exist_ok=True)
        
        for partition_key in zone.partitioning:
            partition_path = os.path.join(zone.storage_path, partition_key)
            os.makedirs(partition_path, exist_ok=True)
        
        logger.info(f"Created data lake zone {zone_id} ({name})")
        
        return zone
    
    def create_ingestion_job(self, name: str, source_type: str, source_config: Dict[str, Any],
                            target_zone_id: str, data_format: DataFormat,
                            processing_config: Dict[str, Any], schedule: str) -> DataIngestionJob:
        """Create data ingestion job"""
        if target_zone_id not in self.zones:
            raise ValueError(f"Target zone {target_zone_id} not found")
        
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate next run based on schedule
        next_run = self._calculate_next_run(schedule, now)
        
        job = DataIngestionJob(
            job_id=job_id,
            name=name,
            source_type=source_type,
            source_config=source_config,
            target_zone_id=target_zone_id,
            data_format=data_format,
            processing_config=processing_config,
            schedule=schedule,
            status=ProcessingStatus.PENDING,
            created_at=now,
            updated_at=now,
            last_run=None,
            next_run=next_run,
            run_count=0,
            success_count=0,
            failure_count=0,
            bytes_processed=0,
            records_processed=0,
            error_message=None,
            metadata={}
        )
        
        with self.lock:
            self.ingestion_jobs[job_id] = job
        
        logger.info(f"Created ingestion job {job_id} ({name})")
        
        return job
    
    def _calculate_next_run(self, schedule: str, from_time: datetime) -> datetime:
        """Calculate next run time based on schedule"""
        # Simple schedule parsing - in production, use proper cron parser
        if schedule.startswith('@hourly'):
            return from_time + timedelta(hours=1)
        elif schedule.startswith('@daily'):
            return from_time + timedelta(days=1)
        elif schedule.startswith('@weekly'):
            return from_time + timedelta(weeks=1)
        elif schedule.startswith('@monthly'):
            return from_time + timedelta(days=30)
        else:
            # Default to daily
            return from_time + timedelta(days=1)
    
    def execute_ingestion_job(self, job_id: str) -> bool:
        """Execute data ingestion job"""
        with self.lock:
            if job_id not in self.ingestion_jobs:
                return False
            
            job = self.ingestion_jobs[job_id]
            
            if job.status != ProcessingStatus.PENDING:
                return False
            
            job.status = ProcessingStatus.PROCESSING
            job.updated_at = datetime.utcnow()
        
        try:
            # Simulate data ingestion
            start_time = time.time()
            
            # In production, this would actually process data
            records_processed = self._simulate_data_processing(job)
            bytes_processed = records_processed * 1024  # Assume 1KB per record
            
            execution_time = time.time() - start_time
            
            # Update job metrics
            with self.lock:
                job.status = ProcessingStatus.COMPLETED
                job.last_run = datetime.utcnow()
                job.run_count += 1
                job.success_count += 1
                job.bytes_processed += bytes_processed
                job.records_processed += records_processed
                job.error_message = None
                job.updated_at = datetime.utcnow()
                
                # Calculate next run
                job.next_run = self._calculate_next_run(job.schedule, datetime.utcnow())
            
            logger.info(f"Executed ingestion job {job_id}: {records_processed} records, {bytes_processed} bytes")
            
            return True
            
        except Exception as e:
            with self.lock:
                job.status = ProcessingStatus.FAILED
                job.last_run = datetime.utcnow()
                job.run_count += 1
                job.failure_count += 1
                job.error_message = str(e)
                job.updated_at = datetime.utcnow()
                
                # Calculate next run for retry
                job.next_run = self._calculate_next_run(job.schedule, datetime.utcnow())
            
            logger.error(f"Failed ingestion job {job_id}: {e}")
            
            return False
    
    def _simulate_data_processing(self, job: DataIngestionJob) -> int:
        """Simulate data processing"""
        # Simulate processing based on source type
        if job.source_type == "database":
            return 10000  # 10K records
        elif job.source_type == "api":
            return 5000   # 5K records
        elif job.source_type == "file":
            return 50000  # 50K records
        elif job.source_type == "stream":
            return 1000   # 1K records (per run)
        else:
            return 1000   # Default 1K records
    
    def create_query(self, name: str, description: str, zone_ids: List[str],
                   query_type: str, query_sql: str, parameters: Dict[str, Any],
                   created_by: str) -> DataQuery:
        """Create data query"""
        # Validate zones
        for zone_id in zone_ids:
            if zone_id not in self.zones:
                raise ValueError(f"Zone {zone_id} not found")
        
        query_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        query = DataQuery(
            query_id=query_id,
            name=name,
            description=description,
            zone_ids=zone_ids,
            query_type=query_type,
            query_sql=query_sql,
            parameters=parameters,
            created_by=created_by,
            created_at=now,
            last_executed=None,
            execution_count=0,
            avg_execution_time=0.0,
            metadata={}
        )
        
        with self.lock:
            self.queries[query_id] = query
        
        logger.info(f"Created query {query_id} ({name})")
        
        return query
    
    def execute_query(self, query_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute data query"""
        with self.lock:
            if query_id not in self.queries:
                raise ValueError(f"Query {query_id} not found")
            
            query = self.queries[query_id]
        
        # Merge parameters
        query_params = query.parameters.copy()
        if parameters:
            query_params.update(parameters)
        
        start_time = time.time()
        
        try:
            # Simulate query execution
            results = self._simulate_query_execution(query, query_params)
            
            execution_time = time.time() - start_time
            
            # Update query metrics
            with self.lock:
                query.last_executed = datetime.utcnow()
                query.execution_count += 1
                
                # Update average execution time
                if query.execution_count == 1:
                    query.avg_execution_time = execution_time
                else:
                    query.avg_execution_time = (query.avg_execution_time * (query.execution_count - 1) + execution_time) / query.execution_count
                
                query.updated_at = datetime.utcnow()
            
            logger.info(f"Executed query {query_id} in {execution_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute query {query_id}: {e}")
            raise
    
    def _simulate_query_execution(self, query: DataQuery, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate query execution"""
        # Simulate query results based on query type
        if query.query_type == "select":
            return {
                'columns': ['id', 'name', 'value', 'timestamp'],
                'rows': [
                    {'id': 1, 'name': 'Sample Data', 'value': 100, 'timestamp': datetime.utcnow().isoformat()},
                    {'id': 2, 'name': 'Another Sample', 'value': 200, 'timestamp': datetime.utcnow().isoformat()}
                ],
                'total_rows': 2,
                'execution_time': 0.5
            }
        elif query.query_type == "aggregate":
            return {
                'results': {
                    'count': 1000,
                    'sum': 50000,
                    'avg': 50.0,
                    'min': 1,
                    'max': 100
                },
                'execution_time': 1.2
            }
        else:
            return {
                'message': 'Query executed successfully',
                'execution_time': 0.8
            }
    
    def get_zone_metrics(self, zone_id: str) -> Dict[str, Any]:
        """Get zone metrics"""
        with self.lock:
            if zone_id not in self.zones:
                return {}
            
            zone = self.zones[zone_id]
            
            # Calculate storage usage (simulated)
            storage_usage = self._calculate_storage_usage(zone)
            
            return {
                'zone_id': zone_id,
                'name': zone.name,
                'tier': zone.tier.value,
                'data_format': zone.data_format.value,
                'retention_days': zone.retention_days,
                'compression': zone.compression,
                'encryption': zone.encryption,
                'storage_usage_bytes': storage_usage,
                'storage_usage_gb': round(storage_usage / (1024**3), 2),
                'partitioning': zone.partitioning,
                'created_at': zone.created_at.isoformat(),
                'updated_at': zone.updated_at.isoformat()
            }
    
    def _calculate_storage_usage(self, zone: DataLakeZone) -> int:
        """Calculate storage usage for zone (simulated)"""
        # Simulate storage calculation based on zone and retention
        base_usage = 1024 * 1024 * 100  # 100MB base usage
        
        # Add usage based on retention days
        retention_multiplier = min(zone.retention_days / 30, 10)  # Cap at 10x for very long retention
        storage_usage = int(base_usage * retention_multiplier)
        
        # Add usage based on partitioning complexity
        partition_complexity = len(zone.partitioning)
        storage_usage = int(storage_usage * (1 + partition_complexity * 0.1))
        
        return storage_usage
    
    def get_data_lake_metrics(self) -> Dict[str, Any]:
        """Get data lake metrics"""
        with self.lock:
            total_zones = len(self.zones)
            
            # Tier distribution
            tier_distribution = defaultdict(int)
            for zone in self.zones.values():
                tier_distribution[zone.tier.value] += 1
            
            # Format distribution
            format_distribution = defaultdict(int)
            for zone in self.zones.values():
                format_distribution[zone.data_format.value] += 1
            
            # Job metrics
            total_jobs = len(self.ingestion_jobs)
            active_jobs = len([job for job in self.ingestion_jobs.values() if job.status == ProcessingStatus.PROCESSING])
            completed_jobs = len([job for job in self.ingestion_jobs.values() if job.status == ProcessingStatus.COMPLETED])
            failed_jobs = len([job for job in self.ingestion_jobs.values() if job.status == ProcessingStatus.FAILED])
            
            # Query metrics
            total_queries = len(self.queries)
            
            # Storage metrics
            total_storage = sum(self._calculate_storage_usage(zone) for zone in self.zones.values())
            
            # Ingestion metrics
            total_bytes_processed = sum(job.bytes_processed for job in self.ingestion_jobs.values())
            total_records_processed = sum(job.records_processed for job in self.ingestion_jobs.values())
            
            return {
                'total_zones': total_zones,
                'tier_distribution': dict(tier_distribution),
                'format_distribution': dict(format_distribution),
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'total_queries': total_queries,
                'total_storage_bytes': total_storage,
                'total_storage_gb': round(total_storage / (1024**3), 2),
                'total_bytes_processed': total_bytes_processed,
                'total_records_processed': total_records_processed,
                'data_lake_path': self.data_lake_path
            }
    
    def archive_data(self, zone_id: str, older_than_days: int) -> bool:
        """Archive old data from zone"""
        with self.lock:
            if zone_id not in self.zones:
                return False
            
            zone = self.zones[zone_id]
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            # Find old data files (simulated)
            archived_count = 0
            
            for partition_key in zone.partitioning:
                partition_path = os.path.join(zone.storage_path, partition_key)
                
                if os.path.exists(partition_path):
                    for item in os.listdir(partition_path):
                        item_path = os.path.join(partition_path, item)
                        
                        if os.path.isfile(item_path):
                            # Check file modification time
                            mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                            
                            if mod_time < cutoff_date:
                                # Archive file (move to archive zone)
                                archive_zone = self.zones.get('archive')
                                if archive_zone:
                                    archive_path = os.path.join(archive_zone.storage_path, partition_key, item)
                                    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                                    os.rename(item_path, archive_path)
                                    archived_count += 1
            
            if archived_count > 0:
                logger.info(f"Archived {archived_count} files from zone {zone_id}")
            
            return archived_count > 0
    
    def _start_background_tasks(self) -> None:
        """Start background data lake tasks"""
        # Start ingestion scheduler thread
        scheduler_thread = threading.Thread(target=self._schedule_ingestion_jobs, daemon=True)
        scheduler_thread.start()
        
        # Start data archiving thread
        archive_thread = threading.Thread(target=self._archive_old_data, daemon=True)
        archive_thread.start()
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _schedule_ingestion_jobs(self) -> None:
        """Schedule and run ingestion jobs"""
        while True:
            try:
                now = datetime.utcnow()
                jobs_to_run = []
                
                with self.lock:
                    for job in self.ingestion_jobs.values():
                        if (job.status == ProcessingStatus.PENDING or 
                            (job.status == ProcessingStatus.COMPLETED and job.next_run and job.next_run <= now)):
                            jobs_to_run.append(job)
                
                # Execute jobs
                for job in jobs_to_run:
                    self.execute_ingestion_job(job.job_id)
                
                # Check every minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Job scheduling failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _archive_old_data(self) -> None:
        """Archive old data from zones"""
        while True:
            try:
                # Run archiving every 6 hours
                time.sleep(21600)  # 6 hours
                
                # Archive data from hot and warm zones
                for zone_id in ['bronze', 'silver']:
                    self.archive_data(zone_id, older_than_days=30)
                
                logger.info("Completed data archiving")
                
            except Exception as e:
                logger.error(f"Data archiving failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _collect_metrics(self) -> None:
        """Collect data lake metrics"""
        while True:
            try:
                # Collect metrics every hour
                time.sleep(3600)  # 1 hour
                
                metrics = self.get_data_lake_metrics()
                logger.info(f"Data lake metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(1800)  # Wait 30 minutes before retrying

# Global data lake manager instance
data_lake_manager = DataLakeManager()

# Export main components
__all__ = [
    'DataLakeManager',
    'DataLakeZone',
    'DataIngestionJob',
    'DataQuery',
    'DataFormat',
    'StorageTier',
    'ProcessingStatus',
    'DataType',
    'data_lake_manager'
]
