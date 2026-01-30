"""
Helm AI Real-Time Analytics with Stream Processing
Provides comprehensive real-time analytics and stream processing capabilities
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from decimal import Decimal

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class StreamType(Enum):
    """Stream type enumeration"""
    EVENT = "event"
    METRIC = "metric"
    LOG = "log"
    USER_ACTIVITY = "user_activity"
    SYSTEM_METRICS = "system_metrics"
    BUSINESS_EVENT = "business_event"
    CUSTOM = "custom"

class ProcessingMode(Enum):
    """Processing mode enumeration"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    MICRO_BATCH = "micro_batch"
    WINDOWED = "windowed"

class AggregationType(Enum):
    """Aggregation type enumeration"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    DISTINCT = "distinct"
    MEDIAN = "median"
    STDDEV = "stddev"

class WindowType(Enum):
    """Window type enumeration"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"

@dataclass
class StreamDefinition:
    """Stream definition"""
    stream_id: str
    name: str
    description: str
    stream_type: StreamType
    source_config: Dict[str, Any]
    schema: Dict[str, Any]
    processing_mode: ProcessingMode
    created_at: datetime
    updated_at: datetime
    is_active: bool
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stream to dictionary"""
        return {
            'stream_id': self.stream_id,
            'name': self.name,
            'description': self.description,
            'stream_type': self.stream_type.value,
            'source_config': self.source_config,
            'schema': self.schema,
            'processing_mode': self.processing_mode.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'metadata': self.metadata
        }

@dataclass
class StreamProcessor:
    """Stream processor definition"""
    processor_id: str
    name: str
    description: str
    stream_id: str
    processing_function: str
    config: Dict[str, Any]
    filters: Dict[str, Any]
    transformations: List[Dict[str, Any]]
    aggregations: List[Dict[str, Any]]
    window_config: Dict[str, Any]
    output_streams: List[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processor to dictionary"""
        return {
            'processor_id': self.processor_id,
            'name': self.name,
            'description': self.description,
            'stream_id': self.stream_id,
            'processing_function': self.processing_function,
            'config': self.config,
            'filters': self.filters,
            'transformations': self.transformations,
            'aggregations': self.aggregations,
            'window_config': self.window_config,
            'output_streams': self.output_streams,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'metrics': self.metrics
        }

@dataclass
class StreamEvent:
    """Stream event"""
    event_id: str
    stream_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    processed_at: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'stream_id': self.stream_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'metadata': self.metadata,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

@dataclass
class StreamWindow:
    """Stream window for aggregation"""
    window_id: str
    processor_id: str
    window_type: WindowType
    start_time: datetime
    end_time: datetime
    events: List[StreamEvent]
    aggregations: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert window to dictionary"""
        return {
            'window_id': self.window_id,
            'processor_id': self.processor_id,
            'window_type': self.window_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'event_count': len(self.events),
            'aggregations': self.aggregations,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StreamProcessingEngine:
    """Stream processing engine"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.streams: Dict[str, StreamDefinition] = {}
        self.processors: Dict[str, StreamProcessor] = {}
        self.events: Dict[str, StreamEvent] = {}
        self.windows: Dict[str, StreamWindow] = {}
        self.active_windows: Dict[str, StreamWindow] = {}
        self.stream_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.processor_functions: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.max_buffer_size = int(os.getenv('STREAM_MAX_BUFFER_SIZE', '10000'))
        self.processing_batch_size = int(os.getenv('STREAM_BATCH_SIZE', '100'))
        self.window_cleanup_interval = int(os.getenv('WINDOW_CLEANUP_INTERVAL', '300'))  # 5 minutes
        self.metrics_collection_interval = int(os.getenv('METRICS_COLLECTION_INTERVAL', '60'))  # 1 minute
        
        # Initialize default processor functions
        self._initialize_processor_functions()
        
        # Initialize default streams
        self._initialize_default_streams()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_processor_functions(self) -> None:
        """Initialize default processor functions"""
        def count_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            return {'count': len(events)}
        
        def sum_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            field = config.get('field', 'value')
            total = sum(float(event.data.get(field, 0)) for event in events)
            return {'sum': total}
        
        def avg_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            field = config.get('field', 'value')
            values = [float(event.data.get(field, 0)) for event in events]
            return {'avg': sum(values) / len(values) if values else 0}
        
        def min_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            field = config.get('field', 'value')
            values = [float(event.data.get(field, 0)) for event in events]
            return {'min': min(values) if values else 0}
        
        def max_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            field = config.get('field', 'value')
            values = [float(event.data.get(field, 0)) for event in events]
            return {'max': max(values) if values else 0}
        
        def distinct_aggregator(events: List[StreamEvent], config: Dict[str, Any]) -> Dict[str, Any]:
            field = config.get('field', 'value')
            distinct_values = set(event.data.get(field) for event in events)
            return {'distinct_count': len(distinct_values)}
        
        # Register functions
        self.processor_functions['count'] = count_aggregator
        self.processor_functions['sum'] = sum_aggregator
        self.processor_functions['avg'] = avg_aggregator
        self.processor_functions['min'] = min_aggregator
        self.processor_functions['max'] = max_aggregator
        self.processor_functions['distinct'] = distinct_aggregator
    
    def _initialize_default_streams(self) -> None:
        """Initialize default streams"""
        # User Activity Stream
        user_activity_stream = StreamDefinition(
            stream_id="user_activity",
            name="User Activity Stream",
            description="Real-time user activity events",
            stream_type=StreamType.USER_ACTIVITY,
            source_config={
                "type": "kafka",
                "topic": "user_activity",
                "bootstrap_servers": "localhost:9092"
            },
            schema={
                "user_id": "string",
                "action": "string",
                "timestamp": "datetime",
                "session_id": "string",
                "ip_address": "string",
                "user_agent": "string"
            },
            processing_mode=ProcessingMode.REAL_TIME,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            metadata={}
        )
        
        # System Metrics Stream
        system_metrics_stream = StreamDefinition(
            stream_id="system_metrics",
            name="System Metrics Stream",
            description="Real-time system metrics",
            stream_type=StreamType.SYSTEM_METRICS,
            source_config={
                "type": "prometheus",
                "endpoint": "http://localhost:9090/api/v1/metrics"
            },
            schema={
                "metric_name": "string",
                "value": "float",
                "labels": "object",
                "timestamp": "datetime"
            },
            processing_mode=ProcessingMode.REAL_TIME,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            metadata={}
        )
        
        # Business Events Stream
        business_events_stream = StreamDefinition(
            stream_id="business_events",
            name="Business Events Stream",
            description="Real-time business events",
            stream_type=StreamType.BUSINESS_EVENT,
            source_config={
                "type": "kafka",
                "topic": "business_events",
                "bootstrap_servers": "localhost:9092"
            },
            schema={
                "event_type": "string",
                "entity_id": "string",
                "entity_type": "string",
                "user_id": "string",
                "timestamp": "datetime",
                "properties": "object"
            },
            processing_mode=ProcessingMode.REAL_TIME,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
            metadata={}
        )
        
        # Add streams
        self.streams[user_activity_stream.stream_id] = user_activity_stream
        self.streams[system_metrics_stream.stream_id] = system_metrics_stream
        self.streams[business_events_stream.stream_id] = business_events_stream
        
        logger.info(f"Initialized {len(self.streams)} default streams")
    
    def create_stream(self, name: str, description: str, stream_type: StreamType,
                     source_config: Dict[str, Any], schema: Dict[str, Any],
                     processing_mode: ProcessingMode) -> StreamDefinition:
        """Create new stream"""
        stream_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        stream = StreamDefinition(
            stream_id=stream_id,
            name=name,
            description=description,
            stream_type=stream_type,
            source_config=source_config,
            schema=schema,
            processing_mode=processing_mode,
            created_at=now,
            updated_at=now,
            is_active=True,
            metadata={}
        )
        
        with self.lock:
            self.streams[stream_id] = stream
            self.stream_buffers[stream_id] = deque(maxlen=self.max_buffer_size)
        
        logger.info(f"Created stream {stream_id} ({name})")
        
        return stream
    
    def create_processor(self, name: str, description: str, stream_id: str,
                        processing_function: str, config: Dict[str, Any],
                        filters: Dict[str, Any], transformations: List[Dict[str, Any]],
                        aggregations: List[Dict[str, Any]], window_config: Dict[str, Any],
                        output_streams: List[str]) -> StreamProcessor:
        """Create stream processor"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        processor_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        processor = StreamProcessor(
            processor_id=processor_id,
            name=name,
            description=description,
            stream_id=stream_id,
            processing_function=processing_function,
            config=config,
            filters=filters,
            transformations=transformations,
            aggregations=aggregations,
            window_config=window_config,
            output_streams=output_streams,
            created_at=now,
            updated_at=now,
            is_active=True,
            metrics={
                'events_processed': 0,
                'events_filtered': 0,
                'windows_created': 0,
                'processing_time_ms': 0,
                'last_processed': None
            }
        )
        
        with self.lock:
            self.processors[processor_id] = processor
        
        logger.info(f"Created processor {processor_id} ({name})")
        
        return processor
    
    def ingest_event(self, stream_id: str, data: Dict[str, Any],
                    metadata: Optional[Dict[str, Any]] = None) -> StreamEvent:
        """Ingest event into stream"""
        with self.lock:
            if stream_id not in self.streams:
                raise ValueError(f"Stream {stream_id} not found")
            
            stream = self.streams[stream_id]
            
            if not stream.is_active:
                raise ValueError(f"Stream {stream_id} is not active")
        
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        event = StreamEvent(
            event_id=event_id,
            stream_id=stream_id,
            timestamp=now,
            data=data,
            metadata=metadata or {},
            processed_at=None
        )
        
        with self.lock:
            self.events[event_id] = event
            self.stream_buffers[stream_id].append(event)
        
        # Trigger processing
        self._process_event(event)
        
        return event
    
    def _process_event(self, event: StreamEvent) -> None:
        """Process event through active processors"""
        with self.lock:
            processors = [p for p in self.processors.values() 
                        if p.stream_id == event.stream_id and p.is_active]
        
        for processor in processors:
            try:
                self._process_event_with_processor(event, processor)
            except Exception as e:
                logger.error(f"Failed to process event {event.event_id} with processor {processor.processor_id}: {e}")
    
    def _process_event_with_processor(self, event: StreamEvent, processor: StreamProcessor) -> None:
        """Process event with specific processor"""
        start_time = time.time()
        
        # Apply filters
        if not self._apply_filters(event, processor.filters):
            processor.metrics['events_filtered'] += 1
            return
        
        # Apply transformations
        transformed_event = self._apply_transformations(event, processor.transformations)
        
        # Add to windows
        self._add_event_to_windows(transformed_event, processor)
        
        # Update metrics
        processor.metrics['events_processed'] += 1
        processor.metrics['processing_time_ms'] += (time.time() - start_time) * 1000
        processor.metrics['last_processed'] = datetime.utcnow().isoformat()
        
        # Mark event as processed
        event.processed_at = datetime.utcnow()
    
    def _apply_filters(self, event: StreamEvent, filters: Dict[str, Any]) -> bool:
        """Apply filters to event"""
        for field, condition in filters.items():
            event_value = event.data.get(field)
            
            if not self._evaluate_condition(event_value, condition):
                return False
        
        return True
    
    def _evaluate_condition(self, value: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate filter condition"""
        operator = condition.get('operator', 'eq')
        expected = condition.get('value')
        
        if operator == 'eq':
            return value == expected
        elif operator == 'ne':
            return value != expected
        elif operator == 'gt':
            return float(value) > float(expected) if value and expected else False
        elif operator == 'lt':
            return float(value) < float(expected) if value and expected else False
        elif operator == 'gte':
            return float(value) >= float(expected) if value and expected else False
        elif operator == 'lte':
            return float(value) <= float(expected) if value and expected else False
        elif operator == 'in':
            return value in expected if isinstance(expected, list) else False
        elif operator == 'contains':
            return expected in str(value) if value else False
        else:
            return True
    
    def _apply_transformations(self, event: StreamEvent, transformations: List[Dict[str, Any]]) -> StreamEvent:
        """Apply transformations to event"""
        transformed_event = StreamEvent(
            event_id=event.event_id,
            stream_id=event.stream_id,
            timestamp=event.timestamp,
            data=event.data.copy(),
            metadata=event.metadata.copy(),
            processed_at=event.processed_at
        )
        
        for transformation in transformations:
            transform_type = transformation.get('type')
            
            if transform_type == 'add_field':
                field_name = transformation.get('field')
                field_value = transformation.get('value')
                transformed_event.data[field_name] = field_value
            
            elif transform_type == 'remove_field':
                field_name = transformation.get('field')
                if field_name in transformed_event.data:
                    del transformed_event.data[field_name]
            
            elif transform_type == 'rename_field':
                old_name = transformation.get('old_field')
                new_name = transformation.get('new_field')
                if old_name in transformed_event.data:
                    transformed_event.data[new_name] = transformed_event.data.pop(old_name)
            
            elif transform_type == 'convert_type':
                field_name = transformation.get('field')
                target_type = transformation.get('target_type')
                if field_name in transformed_event.data:
                    value = transformed_event.data[field_name]
                    if target_type == 'int':
                        transformed_event.data[field_name] = int(value)
                    elif target_type == 'float':
                        transformed_event.data[field_name] = float(value)
                    elif target_type == 'str':
                        transformed_event.data[field_name] = str(value)
        
        return transformed_event
    
    def _add_event_to_windows(self, event: StreamEvent, processor: StreamProcessor) -> None:
        """Add event to processor windows"""
        window_config = processor.window_config
        window_type = WindowType(window_config.get('type', 'tumbling'))
        window_size = window_config.get('size', 60)  # seconds
        
        now = datetime.utcnow()
        
        if window_type == WindowType.TUMBLING:
            # Create tumbling window
            window_start = now - timedelta(seconds=window_size)
            window_id = f"{processor.processor_id}_{int(window_start.timestamp())}"
            
            with self.lock:
                if window_id not in self.active_windows:
                    window = StreamWindow(
                        window_id=window_id,
                        processor_id=processor.processor_id,
                        window_type=window_type,
                        start_time=window_start,
                        end_time=now,
                        events=[],
                        aggregations={},
                        created_at=now,
                        updated_at=now
                    )
                    self.active_windows[window_id] = window
                    processor.metrics['windows_created'] += 1
                
                self.active_windows[window_id].events.append(event)
                self.active_windows[window_id].end_time = now
                self.active_windows[window_id].updated_at = now
        
        elif window_type == WindowType.SLIDING:
            # Create sliding window
            window_start = now - timedelta(seconds=window_size)
            window_id = f"{processor.processor_id}_{int(now.timestamp())}"
            
            with self.lock:
                window = StreamWindow(
                    window_id=window_id,
                    processor_id=processor.processor_id,
                    window_type=window_type,
                    start_time=window_start,
                    end_time=now,
                    events=[event],
                    aggregations={},
                    created_at=now,
                    updated_at=now
                )
                self.active_windows[window_id] = window
                processor.metrics['windows_created'] += 1
        
        # Process aggregations
        self._process_aggregations(processor)
    
    def _process_aggregations(self, processor: StreamProcessor) -> None:
        """Process aggregations for processor windows"""
        with self.lock:
            processor_windows = [w for w in self.active_windows.values() 
                              if w.processor_id == processor.processor_id]
        
        for window in processor_windows:
            if not window.aggregations:
                # Calculate aggregations
                for agg_config in processor.aggregations:
                    agg_type = agg_config.get('type')
                    agg_field = agg_config.get('field')
                    
                    if agg_type in self.processor_functions:
                        function = self.processor_functions[agg_type]
                        result = function(window.events, agg_config)
                        window.aggregations.update(result)
    
    def get_stream_metrics(self, stream_id: str) -> Dict[str, Any]:
        """Get stream metrics"""
        with self.lock:
            if stream_id not in self.streams:
                return {}
            
            stream = self.streams[stream_id]
            buffer = self.stream_buffers[stream_id]
            
            # Calculate metrics
            total_events = len(buffer)
            events_per_second = 0.0
            
            if buffer:
                # Calculate events per second over last minute
                one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
                recent_events = [e for e in buffer if e.timestamp >= one_minute_ago]
                events_per_second = len(recent_events) / 60.0
            
            return {
                'stream_id': stream_id,
                'stream_name': stream.name,
                'stream_type': stream.stream_type.value,
                'processing_mode': stream.processing_mode.value,
                'is_active': stream.is_active,
                'total_events': total_events,
                'events_per_second': round(events_per_second, 2),
                'buffer_size': len(buffer),
                'max_buffer_size': self.max_buffer_size,
                'created_at': stream.created_at.isoformat(),
                'updated_at': stream.updated_at.isoformat()
            }
    
    def get_processor_metrics(self, processor_id: str) -> Dict[str, Any]:
        """Get processor metrics"""
        with self.lock:
            if processor_id not in self.processors:
                return {}
            
            processor = self.processors[processor_id]
            
            # Calculate processing rate
            processing_rate = 0.0
            if processor.metrics['events_processed'] > 0:
                processing_rate = processor.metrics['events_processed'] / max(1, processor.metrics['processing_time_ms'] / 1000)
            
            return {
                'processor_id': processor_id,
                'processor_name': processor.name,
                'stream_id': processor.stream_id,
                'is_active': processor.is_active,
                'events_processed': processor.metrics['events_processed'],
                'events_filtered': processor.metrics['events_filtered'],
                'windows_created': processor.metrics['windows_created'],
                'processing_rate': round(processing_rate, 2),
                'avg_processing_time_ms': round(processor.metrics['processing_time_ms'] / max(1, processor.metrics['events_processed']), 2),
                'last_processed': processor.metrics['last_processed'],
                'created_at': processor.created_at.isoformat(),
                'updated_at': processor.updated_at.isoformat()
            }
    
    def get_stream_analytics(self, stream_id: str, time_window: int = 300) -> Dict[str, Any]:
        """Get stream analytics for time window"""
        with self.lock:
            if stream_id not in self.streams:
                return {}
            
            buffer = self.stream_buffers[stream_id]
            cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)
            
            # Filter events in time window
            recent_events = [e for e in buffer if e.timestamp >= cutoff_time]
            
            if not recent_events:
                return {
                    'stream_id': stream_id,
                    'time_window_seconds': time_window,
                    'event_count': 0,
                    'events_per_second': 0.0,
                    'data_summary': {}
                }
            
            # Calculate analytics
            events_per_second = len(recent_events) / time_window
            
            # Data summary
            data_summary = {}
            for event in recent_events:
                for key, value in event.data.items():
                    if key not in data_summary:
                        data_summary[key] = {
                            'count': 0,
                            'unique_values': set(),
                            'numeric_values': []
                        }
                    
                    data_summary[key]['count'] += 1
                    data_summary[key]['unique_values'].add(str(value))
                    
                    # Try to convert to numeric
                    try:
                        numeric_value = float(value)
                        data_summary[key]['numeric_values'].append(numeric_value)
                    except (ValueError, TypeError):
                        pass
            
            # Calculate statistics for each field
            for key, stats in data_summary.items():
                stats['unique_count'] = len(stats['unique_values'])
                stats['unique_values'] = list(stats['unique_values'])[:10]  # Limit to 10
                
                if stats['numeric_values']:
                    numeric_values = stats['numeric_values']
                    stats['min'] = min(numeric_values)
                    stats['max'] = max(numeric_values)
                    stats['avg'] = sum(numeric_values) / len(numeric_values)
                
                # Remove large arrays
                del stats['numeric_values']
            
            return {
                'stream_id': stream_id,
                'time_window_seconds': time_window,
                'event_count': len(recent_events),
                'events_per_second': round(events_per_second, 2),
                'data_summary': data_summary
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        with self.lock:
            total_streams = len(self.streams)
            active_streams = len([s for s in self.streams.values() if s.is_active])
            
            total_processors = len(self.processors)
            active_processors = len([p for p in self.processors.values() if p.is_active])
            
            total_events = len(self.events)
            total_windows = len(self.active_windows)
            
            # Calculate system-wide rates
            total_events_processed = sum(p.metrics['events_processed'] for p in self.processors.values())
            total_processing_time = sum(p.metrics['processing_time_ms'] for p in self.processors.values())
            system_processing_rate = total_events_processed / max(1, total_processing_time / 1000)
            
            return {
                'streams': {
                    'total': total_streams,
                    'active': active_streams,
                    'inactive': total_streams - active_streams
                },
                'processors': {
                    'total': total_processors,
                    'active': active_processors,
                    'inactive': total_processors - active_processors
                },
                'events': {
                    'total': total_events,
                    'processed': total_events_processed,
                    'processing_rate': round(system_processing_rate, 2)
                },
                'windows': {
                    'active': total_windows,
                    'total_created': sum(p.metrics['windows_created'] for p in self.processors.values())
                },
                'buffers': {
                    'total_events': sum(len(buffer) for buffer in self.stream_buffers.values()),
                    'max_buffer_size': self.max_buffer_size
                }
            }
    
    def _start_background_tasks(self) -> None:
        """Start background stream processing tasks"""
        # Start window cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_windows, daemon=True)
        cleanup_thread.start()
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
        
        # Start stream processing thread
        processing_thread = threading.Thread(target=self._process_streams, daemon=True)
        processing_thread.start()
    
    def _cleanup_windows(self) -> None:
        """Clean up old windows"""
        while True:
            try:
                # Run cleanup every window_cleanup_interval seconds
                time.sleep(self.window_cleanup_interval)
                
                cutoff_time = datetime.utcnow() - timedelta(minutes=30)  # Keep 30 minutes of windows
                
                with self.lock:
                    expired_windows = [
                        window_id for window_id, window in self.active_windows.items()
                        if window.updated_at < cutoff_time
                    ]
                    
                    for window_id in expired_windows:
                        # Move to archive (in production, would save to storage)
                        del self.active_windows[window_id]
                
                if expired_windows:
                    logger.info(f"Cleaned up {len(expired_windows)} expired windows")
                
            except Exception as e:
                logger.error(f"Window cleanup failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _collect_metrics(self) -> None:
        """Collect system metrics"""
        while True:
            try:
                # Collect metrics every metrics_collection_interval seconds
                time.sleep(self.metrics_collection_interval)
                
                metrics = self.get_system_metrics()
                logger.info(f"Stream processing metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def _process_streams(self) -> None:
        """Process stream buffers"""
        while True:
            try:
                # Process every second
                time.sleep(1)
                
                with self.lock:
                    for stream_id, buffer in self.stream_buffers.items():
                        if buffer and len(buffer) >= self.processing_batch_size:
                            # Process batch of events
                            batch = list(buffer)[:self.processing_batch_size]
                            
                            # Remove processed events from buffer
                            for _ in range(len(batch)):
                                buffer.popleft()
                            
                            # Process batch
                            for event in batch:
                                self._process_event(event)
                
            except Exception as e:
                logger.error(f"Stream processing failed: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying

# Global stream processing engine instance
stream_processing_engine = StreamProcessingEngine()

# Export main components
__all__ = [
    'StreamProcessingEngine',
    'StreamDefinition',
    'StreamProcessor',
    'StreamEvent',
    'StreamWindow',
    'StreamType',
    'ProcessingMode',
    'AggregationType',
    'WindowType',
    'stream_processing_engine'
]
