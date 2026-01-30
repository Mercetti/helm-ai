"""
ETL Data Pipeline and Warehousing for Helm AI
=============================================

This module provides comprehensive ETL capabilities:
- Data extraction from multiple sources
- Data transformation and enrichment
- Data loading into data warehouse
- Pipeline orchestration and scheduling
- Data quality validation
- Incremental and full load processing
- Pipeline monitoring and alerting
- Data lineage tracking
"""

import asyncio
import json
import logging
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import defaultdict

# Third-party imports
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import redis
import aiohttp
from prometheus_client import Counter, Histogram, Gauge

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager

logger = StructuredLogger("etl_pipeline")

Base = declarative_base()


class DataSourceType(str, Enum):
    """Types of data sources"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"
    CLOUD_STORAGE = "cloud_storage"


class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class LoadType(str, Enum):
    """Types of data loading"""
    FULL = "full"
    INCREMENTAL = "incremental"
    UPSERT = "upsert"
    MERGE = "merge"


class TransformationType(str, Enum):
    """Types of data transformations"""
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    PIVOT = "pivot"
    CLEAN = "clean"
    ENRICH = "enrich"
    VALIDATE = "validate"


@dataclass
class DataSource:
    """Data source configuration"""
    id: str
    name: str
    type: DataSourceType
    connection_config: Dict[str, Any]
    extraction_query: Optional[str] = None
    schema: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Transformation:
    """Data transformation configuration"""
    id: str
    name: str
    type: TransformationType
    config: Dict[str, Any]
    input_columns: List[str]
    output_columns: List[str]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataPipeline:
    """Data pipeline configuration"""
    id: str
    name: str
    description: str
    sources: List[str]  # Source IDs
    transformations: List[str]  # Transformation IDs
    target_config: Dict[str, Any]
    schedule: str  # Cron expression
    load_type: LoadType
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PipelineExecution:
    """Pipeline execution record"""
    id: str
    pipeline_id: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class DataSources(Base):
    """SQLAlchemy model for data sources"""
    __tablename__ = "data_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    connection_config = Column(JSONB)
    extraction_query = Column(Text)
    schema = Column(JSONB)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transformations(Base):
    """SQLAlchemy model for transformations"""
    __tablename__ = "transformations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transformation_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    config = Column(JSONB)
    input_columns = Column(JSONB)
    output_columns = Column(JSONB)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataPipelines(Base):
    """SQLAlchemy model for data pipelines"""
    __tablename__ = "data_pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sources = Column(JSONB)  # List of source IDs
    transformations = Column(JSONB)  # List of transformation IDs
    target_config = Column(JSONB)
    schedule = Column(String(100))
    load_type = Column(String(20), default="full")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PipelineExecutions(Base):
    """SQLAlchemy model for pipeline executions"""
    __tablename__ = "pipeline_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(String(255), nullable=False, unique=True, index=True)
    pipeline_id = Column(String(255), nullable=False, index=True)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text)
    execution_log = Column(JSONB)
    metrics = Column(JSONB)


class ETLPipeline:
    """ETL Data Pipeline and Warehousing System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        
        # Initialize Redis for caching and queue
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Storage
        self.data_sources: Dict[str, DataSource] = {}
        self.transformations: Dict[str, Transformation] = {}
        self.pipelines: Dict[str, DataPipeline] = {}
        
        # Metrics
        self.pipeline_counter = Counter('etl_pipeline_executions_total', ['status', 'pipeline_id'])
        self.records_processed = Histogram('etl_records_processed', ['pipeline_id'])
        self.execution_duration = Histogram('etl_execution_duration_seconds', ['pipeline_id'])
        self.active_pipelines = Gauge('etl_active_pipelines')
        
        logger.info("ETL Pipeline System initialized")
    
    async def add_data_source(self, source: DataSource) -> bool:
        """Add a new data source"""
        try:
            # Validate source
            if not await self._validate_data_source(source):
                return False
            
            # Store source
            self.data_sources[source.id] = source
            
            # Save to database
            source_record = DataSources(
                source_id=source.id,
                name=source.name,
                type=source.type.value,
                connection_config=source.connection_config,
                extraction_query=source.extraction_query,
                schema=source.schema,
                enabled=source.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(source_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Data source added", source_id=source.id, source_type=source.type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to add data source", source_id=source.id, error=str(e))
            return False
    
    async def _validate_data_source(self, source: DataSource) -> bool:
        """Validate data source configuration"""
        try:
            # Check required fields
            if not source.name or not source.type:
                return False
            
            # Validate type
            if source.type not in DataSourceType:
                return False
            
            # Validate connection config based on type
            if source.type == DataSourceType.DATABASE:
                required_fields = ['connection_string']
            elif source.type == DataSourceType.API:
                required_fields = ['url']
            elif source.type == DataSourceType.FILE:
                required_fields = ['path']
            else:
                required_fields = []
            
            for field in required_fields:
                if field not in source.connection_config:
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Data source validation failed", error=str(e))
            return False
    
    async def add_transformation(self, transformation: Transformation) -> bool:
        """Add a new data transformation"""
        try:
            # Validate transformation
            if not await self._validate_transformation(transformation):
                return False
            
            # Store transformation
            self.transformations[transformation.id] = transformation
            
            # Save to database
            transformation_record = Transformations(
                transformation_id=transformation.id,
                name=transformation.name,
                type=transformation.type.value,
                config=transformation.config,
                input_columns=transformation.input_columns,
                output_columns=transformation.output_columns,
                enabled=transformation.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(transformation_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Transformation added", transformation_id=transformation.id)
            return True
            
        except Exception as e:
            logger.error("Failed to add transformation", transformation_id=transformation.id, error=str(e))
            return False
    
    async def _validate_transformation(self, transformation: Transformation) -> bool:
        """Validate transformation configuration"""
        try:
            # Check required fields
            if not transformation.name or not transformation.type:
                return False
            
            # Validate type
            if transformation.type not in TransformationType:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Transformation validation failed", error=str(e))
            return False
    
    async def create_pipeline(self, pipeline: DataPipeline) -> bool:
        """Create a new data pipeline"""
        try:
            # Validate pipeline
            if not await self._validate_pipeline(pipeline):
                return False
            
            # Store pipeline
            self.pipelines[pipeline.id] = pipeline
            
            # Save to database
            pipeline_record = DataPipelines(
                pipeline_id=pipeline.id,
                name=pipeline.name,
                description=pipeline.description,
                sources=pipeline.sources,
                transformations=pipeline.transformations,
                target_config=pipeline.target_config,
                schedule=pipeline.schedule,
                load_type=pipeline.load_type.value,
                enabled=pipeline.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(pipeline_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Pipeline created", pipeline_id=pipeline.id)
            return True
            
        except Exception as e:
            logger.error("Failed to create pipeline", pipeline_id=pipeline.id, error=str(e))
            return False
    
    async def _validate_pipeline(self, pipeline: DataPipeline) -> bool:
        """Validate pipeline configuration"""
        try:
            # Check required fields
            if not pipeline.name or not pipeline.sources or not pipeline.target_config:
                return False
            
            # Validate sources exist
            for source_id in pipeline.sources:
                if source_id not in self.data_sources:
                    return False
            
            # Validate transformations exist
            for transformation_id in pipeline.transformations:
                if transformation_id not in self.transformations:
                    return False
            
            # Validate load type
            if pipeline.load_type not in LoadType:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Pipeline validation failed", error=str(e))
            return False
    
    async def execute_pipeline(self, pipeline_id: str) -> str:
        """Execute a data pipeline"""
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            pipeline = self.pipelines[pipeline_id]
            
            # Create execution record
            execution = PipelineExecution(
                id=str(uuid.uuid4()),
                pipeline_id=pipeline_id,
                status=PipelineStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            
            # Save execution
            await self._save_execution(execution)
            
            # Execute pipeline
            try:
                # Extract data
                extracted_data = await self._extract_data(pipeline)
                
                # Transform data
                transformed_data = await self._transform_data(pipeline, extracted_data)
                
                # Load data
                await self._load_data(pipeline, transformed_data, execution)
                
                # Update execution status
                execution.status = PipelineStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                
                self.pipeline_counter.labels(status="completed", pipeline_id=pipeline_id).inc()
                
            except Exception as e:
                execution.status = PipelineStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.utcnow()
                
                self.pipeline_counter.labels(status="failed", pipeline_id=pipeline_id).inc()
                raise
            
            finally:
                # Update execution
                await self._save_execution(execution)
            
            logger.info("Pipeline executed successfully", 
                       pipeline_id=pipeline_id, execution_id=execution.id)
            
            return execution.id
            
        except Exception as e:
            logger.error("Pipeline execution failed", pipeline_id=pipeline_id, error=str(e))
            raise
    
    async def _extract_data(self, pipeline: DataPipeline) -> Dict[str, pd.DataFrame]:
        """Extract data from sources"""
        try:
            extracted_data = {}
            
            for source_id in pipeline.sources:
                source = self.data_sources[source_id]
                
                if source.type == DataSourceType.DATABASE:
                    data = await self._extract_from_database(source)
                elif source.type == DataSourceType.API:
                    data = await self._extract_from_api(source)
                elif source.type == DataSourceType.FILE:
                    data = await self._extract_from_file(source)
                else:
                    logger.warning(f"Unsupported source type: {source.type}")
                    continue
                
                extracted_data[source_id] = data
            
            return extracted_data
            
        except Exception as e:
            logger.error("Data extraction failed", error=str(e))
            raise
    
    async def _extract_from_database(self, source: DataSource) -> pd.DataFrame:
        """Extract data from database"""
        try:
            connection_string = source.connection_config['connection_string']
            query = source.extraction_query or "SELECT * FROM table"
            
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine)
            
            logger.info(f"Extracted {len(df)} records from database source {source.id}")
            return df
            
        except Exception as e:
            logger.error(f"Database extraction failed for source {source.id}", error=str(e))
            raise
    
    async def _extract_from_api(self, source: DataSource) -> pd.DataFrame:
        """Extract data from API"""
        try:
            url = source.connection_config['url']
            headers = source.connection_config.get('headers', {})
            params = source.connection_config.get('params', {})
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    df = pd.DataFrame(data)
                    
                    logger.info(f"Extracted {len(df)} records from API source {source.id}")
                    return df
            
        except Exception as e:
            logger.error(f"API extraction failed for source {source.id}", error=str(e))
            raise
    
    async def _extract_from_file(self, source: DataSource) -> pd.DataFrame:
        """Extract data from file"""
        try:
            file_path = source.connection_config['path']
            file_type = source.connection_config.get('type', 'csv')
            
            if file_type == 'csv':
                df = pd.read_csv(file_path)
            elif file_type == 'json':
                df = pd.read_json(file_path)
            elif file_type == 'excel':
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            logger.info(f"Extracted {len(df)} records from file source {source.id}")
            return df
            
        except Exception as e:
            logger.error(f"File extraction failed for source {source.id}", error=str(e))
            raise
    
    async def _transform_data(self, pipeline: DataPipeline, 
                            extracted_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Transform data using configured transformations"""
        try:
            # Start with first source data
            if not extracted_data:
                raise ValueError("No data to transform")
            
            first_source_id = list(extracted_data.keys())[0]
            result_df = extracted_data[first_source_id].copy()
            
            # Apply transformations
            for transformation_id in pipeline.transformations:
                transformation = self.transformations[transformation_id]
                
                if not transformation.enabled:
                    continue
                
                result_df = await self._apply_transformation(transformation, result_df)
            
            logger.info(f"Transformed data to {len(result_df)} records")
            return result_df
            
        except Exception as e:
            logger.error("Data transformation failed", error=str(e))
            raise
    
    async def _apply_transformation(self, transformation: Transformation, 
                                 df: pd.DataFrame) -> pd.DataFrame:
        """Apply a single transformation"""
        try:
            if transformation.type == TransformationType.FILTER:
                df = self._apply_filter_transformation(transformation, df)
            elif transformation.type == TransformationType.AGGREGATE:
                df = self._apply_aggregate_transformation(transformation, df)
            elif transformation.type == TransformationType.CLEAN:
                df = self._apply_clean_transformation(transformation, df)
            elif transformation.type == TransformationType.VALIDATE:
                df = self._apply_validate_transformation(transformation, df)
            else:
                logger.warning(f"Unsupported transformation type: {transformation.type}")
            
            return df
            
        except Exception as e:
            logger.error(f"Transformation {transformation.id} failed", error=str(e))
            raise
    
    def _apply_filter_transformation(self, transformation: Transformation, 
                                   df: pd.DataFrame) -> pd.DataFrame:
        """Apply filter transformation"""
        try:
            filter_config = transformation.config
            condition = filter_config.get('condition')
            
            if condition:
                # Simple filter implementation
                # In production, this would be more sophisticated
                df = df.query(condition)
            
            return df
            
        except Exception as e:
            logger.error("Filter transformation failed", error=str(e))
            raise
    
    def _apply_aggregate_transformation(self, transformation: Transformation, 
                                      df: pd.DataFrame) -> pd.DataFrame:
        """Apply aggregate transformation"""
        try:
            agg_config = transformation.config
            group_by = agg_config.get('group_by', [])
            aggregations = agg_config.get('aggregations', {})
            
            if group_by and aggregations:
                df = df.groupby(group_by).agg(aggregations).reset_index()
            
            return df
            
        except Exception as e:
            logger.error("Aggregate transformation failed", error=str(e))
            raise
    
    def _apply_clean_transformation(self, transformation: Transformation, 
                                 df: pd.DataFrame) -> pd.DataFrame:
        """Apply data cleaning transformation"""
        try:
            clean_config = transformation.config
            
            # Remove duplicates
            if clean_config.get('remove_duplicates', False):
                df = df.drop_duplicates()
            
            # Handle missing values
            if clean_config.get('fill_missing'):
                fill_value = clean_config.get('fill_value', 0)
                df = df.fillna(fill_value)
            
            # Remove outliers (simple implementation)
            if clean_config.get('remove_outliers'):
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for col in numeric_columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            
            return df
            
        except Exception as e:
            logger.error("Clean transformation failed", error=str(e))
            raise
    
    def _apply_validate_transformation(self, transformation: Transformation, 
                                    df: pd.DataFrame) -> pd.DataFrame:
        """Apply data validation transformation"""
        try:
            validation_config = transformation.config
            rules = validation_config.get('rules', [])
            
            for rule in rules:
                column = rule.get('column')
                rule_type = rule.get('type')
                params = rule.get('params', {})
                
                if column not in df.columns:
                    continue
                
                if rule_type == 'range':
                    min_val = params.get('min')
                    max_val = params.get('max')
                    if min_val is not None:
                        df = df[df[column] >= min_val]
                    if max_val is not None:
                        df = df[df[column] <= max_val]
                elif rule_type == 'not_null':
                    df = df[df[column].notna()]
            
            return df
            
        except Exception as e:
            logger.error("Validate transformation failed", error=str(e))
            raise
    
    async def _load_data(self, pipeline: DataPipeline, data: pd.DataFrame, 
                        execution: PipelineExecution):
        """Load data to target"""
        try:
            target_config = pipeline.target_config
            target_type = target_config.get('type')
            
            if target_type == 'database':
                await self._load_to_database(target_config, data, execution)
            elif target_type == 'data_lake':
                await self._load_to_data_lake(target_config, data, execution)
            elif target_type == 'file':
                await self._load_to_file(target_config, data, execution)
            else:
                raise ValueError(f"Unsupported target type: {target_type}")
            
            logger.info(f"Loaded {len(data)} records to target")
            
        except Exception as e:
            logger.error("Data loading failed", error=str(e))
            raise
    
    async def _load_to_database(self, target_config: Dict[str, Any], 
                              data: pd.DataFrame, execution: PipelineExecution):
        """Load data to database"""
        try:
            connection_string = target_config['connection_string']
            table_name = target_config['table']
            load_type = target_config.get('load_type', 'append')
            
            engine = create_engine(connection_string)
            
            if load_type == 'replace':
                data.to_sql(table_name, engine, if_exists='replace', index=False)
            elif load_type == 'append':
                data.to_sql(table_name, engine, if_exists='append', index=False)
            else:
                # Upsert logic would go here
                data.to_sql(table_name, engine, if_exists='append', index=False)
            
            execution.records_processed = len(data)
            
        except Exception as e:
            logger.error("Database loading failed", error=str(e))
            raise
    
    async def _load_to_data_lake(self, target_config: Dict[str, Any], 
                               data: pd.DataFrame, execution: PipelineExecution):
        """Load data to data lake"""
        try:
            bucket = target_config['bucket']
            path = target_config['path']
            format_type = target_config.get('format', 'parquet')
            
            if format_type == 'parquet':
                buffer = data.to_parquet(index=False)
            elif format_type == 'csv':
                buffer = data.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Upload to data lake
            await self.data_lake.upload_data(bucket, path, buffer)
            
            execution.records_processed = len(data)
            
        except Exception as e:
            logger.error("Data lake loading failed", error=str(e))
            raise
    
    async def _load_to_file(self, target_config: Dict[str, Any], 
                           data: pd.DataFrame, execution: PipelineExecution):
        """Load data to file"""
        try:
            file_path = target_config['path']
            format_type = target_config.get('format', 'csv')
            
            if format_type == 'csv':
                data.to_csv(file_path, index=False)
            elif format_type == 'parquet':
                data.to_parquet(file_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            execution.records_processed = len(data)
            
        except Exception as e:
            logger.error("File loading failed", error=str(e))
            raise
    
    async def _save_execution(self, execution: PipelineExecution):
        """Save pipeline execution"""
        try:
            execution_record = PipelineExecutions(
                execution_id=execution.id,
                pipeline_id=execution.pipeline_id,
                status=execution.status.value,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                records_processed=execution.records_processed,
                records_failed=execution.records_failed,
                error_message=execution.error_message,
                execution_log=execution.execution_log,
                metrics=execution.metrics
            )
            
            session = self.db_manager.get_session()
            try:
                # Upsert execution record
                existing = session.query(PipelineExecutions).filter(
                    PipelineExecutions.execution_id == execution.id
                ).first()
                
                if existing:
                    existing.status = execution.status.value
                    existing.completed_at = execution.completed_at
                    existing.records_processed = execution.records_processed
                    existing.records_failed = execution.records_failed
                    existing.error_message = execution.error_message
                    existing.execution_log = execution.execution_log
                    existing.metrics = execution.metrics
                else:
                    session.add(execution_record)
                
                session.commit()
            finally:
                session.close()
            
        except Exception as e:
            logger.error("Failed to save execution", execution_id=execution.id, error=str(e))
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_sources": len(self.data_sources),
            "total_transformations": len(self.transformations),
            "total_pipelines": len(self.pipelines),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
ETL_PIPELINE_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "data_lake": {
        "s3_bucket": "helm-ai-data-lake"
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": 0
    }
}


# Initialize ETL pipeline system
etl_pipeline = ETLPipeline(ETL_PIPELINE_CONFIG)

# Export main components
__all__ = [
    'ETLPipeline',
    'DataSource',
    'Transformation',
    'DataPipeline',
    'PipelineExecution',
    'DataSourceType',
    'PipelineStatus',
    'LoadType',
    'TransformationType',
    'etl_pipeline'
]
