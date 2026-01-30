"""
Real-time Analytics with Stream Processing for Helm AI
======================================================

This module provides comprehensive real-time analytics and stream processing capabilities:
- Real-time data ingestion from multiple sources
- Stream processing with windowing and aggregations
- Real-time analytics and metrics calculation
- Anomaly detection in streaming data
- Real-time dashboards and alerts
"""

import asyncio
import json
import logging
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import threading
from collections import defaultdict, deque

# Third-party imports
import pandas as pd
import numpy as np
import redis
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import aiokafka
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum as spark_sum, avg, max as spark_max, min as spark_min
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import websockets
import aiohttp
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager
from src.ml.anomaly_detection import AnomalyDetector
from src.websocket.realtime import WebSocketManager

logger = StructuredLogger("realtime_analytics")

# FastAPI app for real-time dashboard
app = FastAPI(title="Helm AI Real-time Analytics")


class StreamType(str, Enum):
    """Types of data streams"""
    USER_EVENTS = "user_events"
    SYSTEM_METRICS = "system_metrics"
    BUSINESS_EVENTS = "business_events"
    SECURITY_EVENTS = "security_events"
    IOT_DATA = "iot_data"
    LOG_STREAMS = "log_streams"
    CUSTOM = "custom"


class AggregationType(str, Enum):
    """Types of stream aggregations"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"
    PERCENTILE = "percentile"


class WindowType(str, Enum):
    """Types of time windows"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"


@dataclass
class StreamDefinition:
    """Stream definition configuration"""
    id: str
    name: str
    description: str
    type: StreamType
    source_topic: str
    schema: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StreamAggregation:
    """Stream aggregation configuration"""
    id: str
    name: str
    stream_id: str
    aggregation_type: AggregationType
    field: str
    window_type: WindowType
    window_size: str  # e.g., "1 minute", "5 minutes", "1 hour"
    group_by: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class RealtimeAlert:
    """Real-time alert configuration"""
    id: str
    name: str
    description: str
    stream_id: str
    condition: str  # expression to evaluate
    threshold: float
    severity: str = "medium"
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    cooldown_period: int = 300  # seconds


@dataclass
class StreamEvent:
    """Stream event data"""
    event_id: str
    stream_id: str
    timestamp: datetime
    data: Dict[str, Any]
    processed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealtimeAnalyticsEngine:
    """Real-time Analytics and Stream Processing Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        self.anomaly_detector = AnomalyDetector(config.get('ml', {}))
        self.websocket_manager = WebSocketManager(config.get('websocket', {}))
        
        # Initialize Spark for stream processing
        self.spark = self._initialize_spark()
        
        # Initialize Kafka
        self.kafka_producer = KafkaProducer(**config.get('kafka_producer', {}))
        self.kafka_consumers: Dict[str, KafkaConsumer] = {}
        
        # Initialize Redis for caching and state
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Stream storage
        self.streams: Dict[str, StreamDefinition] = {}
        self.aggregations: Dict[str, StreamAggregation] = {}
        self.alerts: Dict[str, RealtimeAlert] = {}
        self.active_streams: Dict[str, bool] = {}
        
        # Real-time data storage
        self.stream_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregation_results: Dict[str, Dict[str, Any]] = {}
        self.alert_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Background processing
        self.processing_threads: Dict[str, threading.Thread] = {}
        self.running = False
        
        logger.info("Real-time Analytics Engine initialized")
    
    def _initialize_spark(self) -> SparkSession:
        """Initialize Spark session for stream processing"""
        spark_config = self.config.get('spark', {})
        
        builder = SparkSession.builder.appName("Helm-AI-Realtime-Analytics")
        
        # Add Spark configurations
        for key, value in spark_config.items():
            builder = builder.config(key, value)
        
        spark = builder.getOrCreate()
        
        # Configure for streaming
        spark.conf.set("spark.sql.streaming.checkpointLocation", "checkpoints/")
        spark.conf.set("spark.sql.shuffle.partitions", "200")
        
        return spark
    
    async def create_stream(self, stream: StreamDefinition) -> bool:
        """Create a new data stream"""
        try:
            # Validate stream configuration
            if not await self._validate_stream(stream):
                logger.error("Stream validation failed", stream_id=stream.id)
                return False
            
            # Store stream
            self.streams[stream.id] = stream
            
            # Create Kafka topic if needed
            await self._create_kafka_topic(stream.source_topic)
            
            # Start stream processing
            if stream.enabled:
                await self._start_stream_processing(stream.id)
            
            logger.info("Stream created successfully", 
                       stream_id=stream.id, stream_type=stream.type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create stream", 
                        stream_id=stream.id, error=str(e))
            return False
    
    async def _validate_stream(self, stream: StreamDefinition) -> bool:
        """Validate stream configuration"""
        try:
            # Check required fields
            if not stream.name or not stream.source_topic:
                return False
            
            # Validate schema
            if not stream.schema or not isinstance(stream.schema, dict):
                return False
            
            return True
            
        except Exception as e:
            logger.error("Stream validation failed", stream_id=stream.id, error=str(e))
            return False
    
    async def _create_kafka_topic(self, topic_name: str):
        """Create Kafka topic if it doesn't exist"""
        try:
            # This would typically use Kafka admin client
            logger.info("Kafka topic validation", topic=topic_name)
            
        except Exception as e:
            logger.error("Failed to create Kafka topic", topic=topic_name, error=str(e))
    
    async def _start_stream_processing(self, stream_id: str):
        """Start processing a stream"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        stream = self.streams[stream_id]
        
        # Start consumer thread
        consumer_thread = threading.Thread(
            target=self._process_stream_thread,
            args=(stream_id,),
            daemon=True
        )
        
        self.processing_threads[stream_id] = consumer_thread
        self.active_streams[stream_id] = True
        
        consumer_thread.start()
        
        logger.info("Stream processing started", stream_id=stream_id)
    
    def _process_stream_thread(self, stream_id: str):
        """Process stream in background thread"""
        try:
            stream = self.streams[stream_id]
            
            # Create Kafka consumer
            consumer = KafkaConsumer(
                stream.source_topic,
                bootstrap_servers=self.config['kafka_producer']['bootstrap_servers'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id=f"helm-ai-{stream_id}",
                auto_offset_reset='latest'
            )
            
            self.kafka_consumers[stream_id] = consumer
            
            # Process messages
            for message in consumer:
                if not self.active_streams.get(stream_id, False):
                    break
                
                try:
                    # Process event
                    event = StreamEvent(
                        event_id=str(uuid.uuid4()),
                        stream_id=stream_id,
                        timestamp=datetime.utcnow(),
                        data=message.value
                    )
                    
                    asyncio.run(self._process_event(event))
                    
                except Exception as e:
                    logger.error("Failed to process event", 
                                stream_id=stream_id, error=str(e))
            
        except Exception as e:
            logger.error("Stream processing thread failed", 
                        stream_id=stream_id, error=str(e))
    
    async def _process_event(self, event: StreamEvent):
        """Process a single stream event"""
        try:
            # Store event in memory
            self.stream_data[event.stream_id].append(event)
            
            # Apply aggregations
            await self._apply_aggregations(event)
            
            # Check alerts
            await self._check_alerts(event)
            
            # Detect anomalies
            await self._detect_anomalies(event)
            
            # Update real-time dashboards
            await self._update_dashboards(event)
            
            # Mark as processed
            event.processed = True
            
        except Exception as e:
            logger.error("Failed to process event", 
                        event_id=event.event_id, error=str(e))
    
    async def _apply_aggregations(self, event: StreamEvent):
        """Apply stream aggregations to event"""
        stream_aggregations = [agg for agg in self.aggregations.values() 
                             if agg.stream_id == event.stream_id and agg.enabled]
        
        for aggregation in stream_aggregations:
            try:
                # Get window data
                window_data = await self._get_window_data(event, aggregation)
                
                if window_data.empty:
                    continue
                
                # Apply aggregation
                result = await self._calculate_aggregation(window_data, aggregation)
                
                # Store result
                self.aggregation_results[aggregation.id] = {
                    "aggregation_id": aggregation.id,
                    "timestamp": datetime.utcnow(),
                    "result": result,
                    "window_size": aggregation.window_size
                }
                
                # Cache in Redis
                await self._cache_aggregation_result(aggregation.id, result)
                
            except Exception as e:
                logger.error("Failed to apply aggregation", 
                            aggregation_id=aggregation.id, error=str(e))
    
    async def _get_window_data(self, event: StreamEvent, aggregation: StreamAggregation) -> pd.DataFrame:
        """Get data within the aggregation window"""
        try:
            # Parse window size
            window_seconds = self._parse_window_size(aggregation.window_size)
            
            # Get recent events
            cutoff_time = event.timestamp - timedelta(seconds=window_seconds)
            
            recent_events = [
                e for e in self.stream_data[event.stream_id]
                if e.timestamp >= cutoff_time
            ]
            
            if not recent_events:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for e in recent_events:
                row = e.data.copy()
                row['timestamp'] = e.timestamp
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Apply filters
            for field, value in aggregation.filters.items():
                if field in df.columns:
                    df = df[df[field] == value]
            
            return df
            
        except Exception as e:
            logger.error("Failed to get window data", error=str(e))
            return pd.DataFrame()
    
    def _parse_window_size(self, window_size: str) -> int:
        """Parse window size string to seconds"""
        try:
            if "minute" in window_size:
                minutes = int(window_size.split()[0])
                return minutes * 60
            elif "hour" in window_size:
                hours = int(window_size.split()[0])
                return hours * 3600
            elif "second" in window_size:
                seconds = int(window_size.split()[0])
                return seconds
            else:
                return 60  # Default to 1 minute
        except:
            return 60
    
    async def _calculate_aggregation(self, data: pd.DataFrame, 
                                  aggregation: StreamAggregation) -> Dict[str, Any]:
        """Calculate aggregation result"""
        try:
            if aggregation.field not in data.columns:
                return {"error": f"Field {aggregation.field} not found"}
            
            field_data = data[aggregation.field]
            
            # Apply aggregation type
            if aggregation.aggregation_type == AggregationType.COUNT:
                result = len(field_data)
            elif aggregation.aggregation_type == AggregationType.SUM:
                result = field_data.sum()
            elif aggregation.aggregation_type == AggregationType.AVERAGE:
                result = field_data.mean()
            elif aggregation.aggregation_type == AggregationType.MIN:
                result = field_data.min()
            elif aggregation.aggregation_type == AggregationType.MAX:
                result = field_data.max()
            elif aggregation.aggregation_type == AggregationType.DISTINCT_COUNT:
                result = field_data.nunique()
            elif aggregation.aggregation_type == AggregationType.PERCENTILE:
                result = field_data.quantile(0.95)  # 95th percentile
            else:
                result = 0
            
            return {
                "value": result,
                "count": len(field_data),
                "field": aggregation.field,
                "type": aggregation.aggregation_type.value
            }
            
        except Exception as e:
            logger.error("Failed to calculate aggregation", error=str(e))
            return {"error": str(e)}
    
    async def _cache_aggregation_result(self, aggregation_id: str, result: Dict[str, Any]):
        """Cache aggregation result in Redis"""
        try:
            key = f"aggregation:{aggregation_id}"
            self.redis_client.setex(key, 3600, json.dumps(result))  # 1 hour TTL
            
        except Exception as e:
            logger.error("Failed to cache aggregation result", error=str(e))
    
    async def _check_alerts(self, event: StreamEvent):
        """Check if event triggers any alerts"""
        stream_alerts = [alert for alert in self.alerts.values() 
                        if alert.stream_id == event.stream_id and alert.enabled]
        
        for alert in stream_alerts:
            try:
                # Check cooldown period
                if await self._is_alert_in_cooldown(alert.id):
                    continue
                
                # Evaluate alert condition
                triggered = await self._evaluate_alert_condition(alert, event)
                
                if triggered:
                    await self._trigger_alert(alert, event)
                
            except Exception as e:
                logger.error("Failed to check alert", 
                            alert_id=alert.id, error=str(e))
    
    async def _is_alert_in_cooldown(self, alert_id: str) -> bool:
        """Check if alert is in cooldown period"""
        try:
            key = f"alert_cooldown:{alert_id}"
            return self.redis_client.exists(key)
        except:
            return False
    
    async def _evaluate_alert_condition(self, alert: RealtimeAlert, 
                                      event: StreamEvent) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation
            if "count" in alert.condition.lower():
                # Count-based alert
                window_seconds = 300  # 5 minutes
                cutoff_time = event.timestamp - timedelta(seconds=window_seconds)
                
                recent_events = [
                    e for e in self.stream_data[event.stream_id]
                    if e.timestamp >= cutoff_time
                ]
                
                count = len(recent_events)
                return count >= alert.threshold
            
            elif "value" in alert.condition.lower():
                # Value-based alert
                field_name = alert.condition.split(" ")[-1]
                if field_name in event.data:
                    value = event.data[field_name]
                    return value >= alert.threshold
            
            return False
            
        except Exception as e:
            logger.error("Failed to evaluate alert condition", error=str(e))
            return False
    
    async def _trigger_alert(self, alert: RealtimeAlert, event: StreamEvent):
        """Trigger an alert"""
        try:
            # Create alert record
            alert_record = {
                "alert_id": alert.id,
                "alert_name": alert.name,
                "severity": alert.severity,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": event.event_id,
                "stream_id": event.stream_id,
                "condition": alert.condition,
                "threshold": alert.threshold
            }
            
            # Store in alert history
            self.alert_history[alert.id].append(alert_record)
            
            # Set cooldown
            key = f"alert_cooldown:{alert.id}"
            self.redis_client.setex(key, alert.cooldown_period, "1")
            
            # Send notifications
            await self._send_alert_notifications(alert, alert_record)
            
            # Update dashboard
            await self.websocket_manager.broadcast({
                "type": "alert",
                "data": alert_record
            })
            
            logger.warning("Alert triggered", 
                          alert_id=alert.id, alert_name=alert.name)
            
        except Exception as e:
            logger.error("Failed to trigger alert", 
                        alert_id=alert.id, error=str(e))
    
    async def _send_alert_notifications(self, alert: RealtimeAlert, 
                                       alert_record: Dict[str, Any]):
        """Send alert notifications"""
        try:
            # Send to configured channels
            for channel in alert.notification_channels:
                if channel == "websocket":
                    await self.websocket_manager.broadcast({
                        "type": "alert",
                        "data": alert_record
                    })
                elif channel == "email":
                    # Send email notification
                    await self._send_email_alert(alert, alert_record)
                elif channel == "slack":
                    # Send Slack notification
                    await self._send_slack_alert(alert, alert_record)
                
        except Exception as e:
            logger.error("Failed to send alert notifications", error=str(e))
    
    async def _send_email_alert(self, alert: RealtimeAlert, alert_record: Dict[str, Any]):
        """Send email alert"""
        logger.info("Email alert sent", alert_id=alert.id)
    
    async def _send_slack_alert(self, alert: RealtimeAlert, alert_record: Dict[str, Any]):
        """Send Slack alert"""
        logger.info("Slack alert sent", alert_id=alert.id)
    
    async def _detect_anomalies(self, event: StreamEvent):
        """Detect anomalies in stream data"""
        try:
            # Get recent data for anomaly detection
            recent_events = list(self.stream_data[event.stream_id])[-100:]  # Last 100 events
            
            if len(recent_events) < 10:
                return
            
            # Prepare data for anomaly detection
            data = []
            for e in recent_events:
                row = e.data.copy()
                row['timestamp'] = e.timestamp
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Use anomaly detector
            anomalies = await self.anomaly_detector.detect_anomalies(df)
            
            if anomalies and len(anomalies) > 0:
                # Handle detected anomalies
                await self._handle_anomalies(event, anomalies)
                
        except Exception as e:
            logger.error("Failed to detect anomalies", error=str(e))
    
    async def _handle_anomalies(self, event: StreamEvent, anomalies: List[Dict[str, Any]]):
        """Handle detected anomalies"""
        try:
            for anomaly in anomalies:
                anomaly_record = {
                    "anomaly_id": str(uuid.uuid4()),
                    "event_id": event.event_id,
                    "stream_id": event.stream_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "anomaly_type": anomaly.get("type", "unknown"),
                    "severity": anomaly.get("severity", "medium"),
                    "description": anomaly.get("description", ""),
                    "score": anomaly.get("score", 0.0)
                }
                
                # Send notification
                await self.websocket_manager.broadcast({
                    "type": "anomaly",
                    "data": anomaly_record
                })
                
                logger.warning("Anomaly detected", 
                             stream_id=event.stream_id, anomaly_type=anomaly.get("type"))
                
        except Exception as e:
            logger.error("Failed to handle anomalies", error=str(e))
    
    async def _update_dashboards(self, event: StreamEvent):
        """Update real-time dashboards"""
        try:
            # Send event to dashboard subscribers
            await self.websocket_manager.broadcast({
                "type": "event",
                "stream_id": event.stream_id,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            })
            
        except Exception as e:
            logger.error("Failed to update dashboards", error=str(e))
    
    async def get_realtime_metrics(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "streams": {},
                "aggregations": {},
                "alerts": {},
                "system": {}
            }
            
            # Stream metrics
            for sid, stream in self.streams.items():
                if stream_id and sid != stream_id:
                    continue
                
                event_count = len(self.stream_data[sid])
                recent_events = [
                    e for e in self.stream_data[sid]
                    if e.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                ]
                
                metrics["streams"][sid] = {
                    "name": stream.name,
                    "type": stream.type.value,
                    "total_events": event_count,
                    "recent_events": len(recent_events),
                    "events_per_second": len(recent_events) / 300 if recent_events else 0,
                    "active": self.active_streams.get(sid, False)
                }
            
            # Aggregation metrics
            for agg_id, result in self.aggregation_results.items():
                if stream_id and self.aggregations[agg_id].stream_id != stream_id:
                    continue
                
                metrics["aggregations"][agg_id] = result
            
            # Alert metrics
            for alert_id, history in self.alert_history.items():
                if stream_id and self.alerts[alert_id].stream_id != stream_id:
                    continue
                
                recent_alerts = [
                    a for a in history
                    if datetime.fromisoformat(a["timestamp"]) >= datetime.utcnow() - timedelta(hours=24)
                ]
                
                metrics["alerts"][alert_id] = {
                    "name": self.alerts[alert_id].name,
                    "severity": self.alerts[alert_id].severity,
                    "total_alerts": len(history),
                    "recent_alerts": len(recent_alerts)
                }
            
            # System metrics
            metrics["system"] = {
                "active_streams": len([s for s in self.active_streams.values() if s]),
                "total_streams": len(self.streams),
                "total_aggregations": len(self.aggregations),
                "total_alerts": len(self.alerts),
                "processing_threads": len(self.processing_threads)
            }
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get real-time metrics", error=str(e))
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_streams": len(self.streams),
            "active_streams": len([s for s in self.active_streams.values() if s]),
            "total_aggregations": len(self.aggregations),
            "total_alerts": len(self.alerts),
            "kafka_consumers": len(self.kafka_consumers),
            "processing_threads": len(self.processing_threads),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
REALTIME_CONFIG = {
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
    },
    "kafka_producer": {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "value_serializer": lambda v: json.dumps(v).encode()
    },
    "spark": {
        "spark.sql.streaming.checkpointLocation": "checkpoints/",
        "spark.sql.shuffle.partitions": "200"
    },
    "websocket": {
        "host": "0.0.0.0",
        "port": 8000
    },
    "ml": {
        "model_path": "models/anomaly_detection.pkl"
    }
}


# Initialize real-time analytics engine
realtime_engine = RealtimeAnalyticsEngine(REALTIME_CONFIG)

# Export main components
__all__ = [
    'RealtimeAnalyticsEngine',
    'StreamDefinition',
    'StreamAggregation',
    'RealtimeAlert',
    'StreamEvent',
    'StreamType',
    'AggregationType',
    'WindowType',
    'realtime_engine',
    'app'
]
