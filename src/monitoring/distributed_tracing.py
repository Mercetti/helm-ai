"""
Helm AI Advanced Monitoring with Distributed Tracing
Provides distributed tracing, observability, and performance monitoring
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger

class SpanStatus(Enum):
    """Span status enumeration"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class SpanKind(Enum):
    """Span kind enumeration"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"

@dataclass
class TraceContext:
    """Trace context for distributed tracing"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)
    sampled: bool = True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert trace context to dictionary for propagation"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'sampled': str(self.sampled),
            **{f'baggage_{k}': v for k, v in self.baggage.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'TraceContext':
        """Create trace context from dictionary"""
        baggage = {}
        for key, value in data.items():
            if key.startswith('baggage_'):
                baggage[key[8:]] = value
        
        return cls(
            trace_id=data.get('trace_id', ''),
            span_id=data.get('span_id', ''),
            parent_span_id=data.get('parent_span_id'),
            baggage=baggage,
            sampled=data.get('sampled', 'true').lower() == 'true'
        )

@dataclass
class Span:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: SpanStatus = SpanStatus.OK
    kind: SpanKind = SpanKind.INTERNAL
    service_name: str = "helm-ai"
    resource: str = ""
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """Get span duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'status': self.status.value,
            'kind': self.kind.value,
            'service_name': self.service_name,
            'resource': self.resource,
            'tags': self.tags,
            'logs': self.logs,
            'events': self.events
        }

class Tracer:
    """Distributed tracer implementation"""
    
    def __init__(self, service_name: str = "helm-ai"):
        self.service_name = service_name
        self.active_spans: Dict[str, Span] = {}
        self.finished_spans: deque = deque(maxlen=10000)  # Keep last 10k spans
        self.lock = threading.Lock()
        self.sampling_rate = float(os.getenv('TRACE_SAMPLING_RATE', '1.0'))
        
    def start_span(
        self,
        operation_name: str,
        parent_span: Optional[Span] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None,
        resource: str = ""
    ) -> Span:
        """Start a new span"""
        trace_id = parent_span.trace_id if parent_span else self._generate_trace_id()
        span_id = self._generate_span_id()
        parent_span_id = parent_span.span_id if parent_span else None
        
        # Check sampling
        sampled = self._should_sample(trace_id)
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            kind=kind,
            service_name=self.service_name,
            resource=resource,
            tags=tags or {}
        )
        
        if sampled:
            with self.lock:
                self.active_spans[span_id] = span
        
        return span
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK) -> None:
        """Finish a span"""
        span.end_time = datetime.utcnow()
        span.status = status
        
        with self.lock:
            if span.span_id in self.active_spans:
                del self.active_spans[span.span_id]
            self.finished_spans.append(span)
    
    def add_tag(self, span: Span, key: str, value: Any) -> None:
        """Add tag to span"""
        span.tags[key] = value
    
    def add_log(self, span: Span, level: str, message: str, **kwargs) -> None:
        """Add log to span"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        span.logs.append(log_entry)
    
    def add_event(self, span: Span, name: str, **kwargs) -> None:
        """Add event to span"""
        event = {
            'name': name,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        span.events.append(event)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        spans = []
        
        with self.lock:
            # Check active spans
            for span in self.active_spans.values():
                if span.trace_id == trace_id:
                    spans.append(span)
            
            # Check finished spans
            for span in self.finished_spans:
                if span.trace_id == trace_id:
                    spans.append(span)
        
        return sorted(spans, key=lambda s: s.start_time)
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return str(uuid.uuid4()).replace('-', '')
    
    def _generate_span_id(self) -> str:
        """Generate unique span ID"""
        return str(uuid.uuid4()).replace('-', '')[:16]
    
    def _should_sample(self, trace_id: str) -> bool:
        """Determine if trace should be sampled"""
        # Simple sampling strategy - can be enhanced with more sophisticated algorithms
        import random
        return random.random() < self.sampling_rate

class DistributedTracingManager:
    """Manager for distributed tracing operations"""
    
    def __init__(self):
        self.tracers: Dict[str, Tracer] = {}
        self.global_tracer = Tracer("helm-ai")
        self.exporters: List[Any] = []
        self.lock = threading.Lock()
        
    def get_tracer(self, service_name: str) -> Tracer:
        """Get or create tracer for service"""
        with self.lock:
            if service_name not in self.tracers:
                self.tracers[service_name] = Tracer(service_name)
            return self.tracers[service_name]
    
    def inject_context(self, headers: Dict[str, str], context: TraceContext) -> Dict[str, str]:
        """Inject trace context into headers"""
        headers = headers.copy()
        headers.update(context.to_dict())
        return headers
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """Extract trace context from headers"""
        context_data = {}
        
        # Look for trace context headers
        for key in ['trace_id', 'span_id', 'parent_span_id', 'sampled']:
            if key in headers:
                context_data[key] = headers[key]
        
        # Look for baggage items
        for key, value in headers.items():
            if key.startswith('baggage_'):
                context_data[key] = value
        
        if 'trace_id' in context_data and 'span_id' in context_data:
            return TraceContext.from_dict(context_data)
        
        return None
    
    def register_exporter(self, exporter: Any) -> None:
        """Register trace exporter"""
        self.exporters.append(exporter)
    
    def export_spans(self) -> None:
        """Export finished spans to registered exporters"""
        for tracer in self.tracers.values():
            spans_to_export = list(tracer.finished_spans)
            for exporter in self.exporters:
                try:
                    exporter.export(spans_to_export)
                except Exception as e:
                    logger.error(f"Failed to export spans: {e}")

class TraceExporter:
    """Base class for trace exporters"""
    
    def export(self, spans: List[Span]) -> None:
        """Export spans to external system"""
        raise NotImplementedError

class JaegerExporter(TraceExporter):
    """Jaeger trace exporter"""
    
    def __init__(self, endpoint: str, service_name: str = "helm-ai"):
        self.endpoint = endpoint
        self.service_name = service_name
        self.batch_size = 100
        
    def export(self, spans: List[Span]) -> None:
        """Export spans to Jaeger"""
        try:
            import requests
            
            # Convert spans to Jaeger format
            jaeger_spans = []
            for span in spans:
                jaeger_span = {
                    'traceID': span.trace_id,
                    'spanID': span.span_id,
                    'parentSpanID': span.parent_span_id,
                    'operationName': span.operation_name,
                    'startTime': int(span.start_time.timestamp() * 1000000),  # microseconds
                    'duration': int(span.duration) if span.duration else 0,
                    'tags': [
                        {'key': k, 'value': str(v)} for k, v in span.tags.items()
                    ],
                    'logs': span.logs,
                    'status': {'code': 0 if span.status == SpanStatus.OK else 1},
                    'process': {
                        'serviceName': span.service_name,
                        'tags': [
                            {'key': 'service.name', 'value': span.service_name}
                        ]
                    }
                }
                jaeger_spans.append(jaeger_span)
            
            # Send to Jaeger collector
            data = {
                'spans': jaeger_spans
            }
            
            response = requests.post(
                f"{self.endpoint}/api/traces",
                json=data,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to export spans to Jaeger: {response.status_code}")
                
        except ImportError:
            logger.warning("Requests library not available for Jaeger export")
        except Exception as e:
            logger.error(f"Jaeger export error: {e}")

class PrometheusExporter(TraceExporter):
    """Prometheus metrics exporter for tracing"""
    
    def __init__(self):
        self.metrics = {
            'trace_spans_total': 0,
            'trace_spans_duration_seconds': 0,
            'trace_spans_error_total': 0
        }
    
    def export(self, spans: List[Span]) -> None:
        """Export span metrics to Prometheus"""
        for span in spans:
            self.metrics['trace_spans_total'] += 1
            
            if span.duration:
                self.metrics['trace_spans_duration_seconds'] += span.duration / 1000
            
            if span.status == SpanStatus.ERROR:
                self.metrics['trace_spans_error_total'] += 1
        
        # In a real implementation, this would push to Prometheus gateway
        logger.info(f"Trace metrics: {self.metrics}")

class OpenTelemetryExporter(TraceExporter):
    """OpenTelemetry compatible exporter"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        
    def export(self, spans: List[Span]) -> None:
        """Export spans in OpenTelemetry format"""
        try:
            import requests
            
            otel_spans = []
            for span in spans:
                otel_span = {
                    'traceId': span.trace_id,
                    'spanId': span.span_id,
                    'parentSpanId': span.parent_span_id,
                    'name': span.operation_name,
                    'kind': span.kind.value.upper(),
                    'startTimeUnixNano': int(span.start_time.timestamp() * 1e9),
                    'endTimeUnixNano': int(span.end_time.timestamp() * 1e9) if span.end_time else None,
                    'status': {'code': 0 if span.status == SpanStatus.OK else 1},
                    'attributes': span.tags,
                    'events': span.events,
                    'resource': {
                        'service.name': span.service_name,
                        'service.version': '1.0.0'
                    }
                }
                otel_spans.append(otel_span)
            
            # Send to OpenTelemetry collector
            response = requests.post(
                f"{self.endpoint}/v1/traces",
                json={'resourceSpans': [{'spans': otel_spans}]},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to export spans to OpenTelemetry: {response.status_code}")
                
        except Exception as e:
            logger.error(f"OpenTelemetry export error: {e}")

# Decorator for automatic tracing
def trace(operation_name: str = None, kind: SpanKind = SpanKind.INTERNAL):
    """Decorator for automatic function tracing"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            tracer = distributed_tracing.get_tracer("helm-ai")
            
            # Get operation name
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Start span
            span = tracer.start_span(op_name, kind=kind)
            
            try:
                # Add function arguments as tags
                if args:
                    tracer.add_tag(span, 'args_count', len(args))
                if kwargs:
                    tracer.add_tag(span, 'kwargs_count', len(kwargs))
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Add result info
                tracer.add_tag(span, 'success', True)
                
                return result
                
            except Exception as e:
                # Add error info
                tracer.add_tag(span, 'success', False)
                tracer.add_tag(span, 'error_type', type(e).__name__)
                tracer.add_log(span, 'ERROR', str(e), exception_type=type(e).__name__)
                
                # Finish span with error status
                tracer.finish_span(span, SpanStatus.ERROR)
                raise
                
            finally:
                # Finish span
                if span.status != SpanStatus.ERROR:
                    tracer.finish_span(span)
        
        return wrapper
    return decorator

# Global distributed tracing manager
distributed_tracing = DistributedTracingManager()

# Register default exporters
if os.getenv('JAEGER_ENDPOINT'):
    distributed_tracing.register_exporter(JaegerExporter(os.getenv('JAEGER_ENDPOINT')))

if os.getenv('OPENTELEMETRY_ENDPOINT'):
    distributed_tracing.register_exporter(OpenTelemetryExporter(os.getenv('OPENTELEMETRY_ENDPOINT')))

distributed_tracing.register_exporter(PrometheusExporter())

# Export main components
__all__ = [
    'Tracer',
    'Span',
    'TraceContext',
    'SpanStatus',
    'SpanKind',
    'DistributedTracingManager',
    'TraceExporter',
    'JaegerExporter',
    'PrometheusExporter',
    'OpenTelemetryExporter',
    'trace',
    'distributed_tracing'
]
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import contextlib

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from database.database_manager import get_database_manager

@dataclass
class TraceSpan:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "ok"  # ok, error, timeout
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    baggage: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'service_name': self.service_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms,
            'status': self.status,
            'tags': self.tags,
            'logs': self.logs,
            'baggage': self.baggage
        }

@dataclass
class TraceContext:
    """Trace context for propagation"""
    trace_id: str
    span_id: str
    baggage: Dict[str, str] = field(default_factory=dict)
    sampled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'baggage': self.baggage,
            'sampled': self.sampled
        }

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_name: str
    timestamp: datetime
    request_count: int
    error_count: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float  # requests per second
    error_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'timestamp': self.timestamp.isoformat(),
            'request_count': self.request_count,
            'error_count': self.error_count,
            'avg_response_time': self.avg_response_time,
            'p95_response_time': self.p95_response_time,
            'p99_response_time': self.p99_response_time,
            'throughput': self.throughput,
            'error_rate': self.error_rate
        }

class DistributedTracer:
    """Distributed tracing system"""
    
    def __name__ = "DistributedTracer"
    
    def __init__(self):
        self.active_spans = {}
        self.completed_spans = deque(maxlen=10000)
        self.service_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.trace_contexts = {}
        self.lock = threading.RLock()
        
        # Configuration
        self.config = {
            'sample_rate': 0.1,  # 10% sampling
            'max_spans': 1000,
            'timeout_ms': 30000,
            'services': ['helm-ai-api', 'helm-ai-web', 'helm-ai-worker', 'helm-ai-db']
        }
        
        # Jaeger/OpenTelemetry configuration
        self.jaeger_config = {
            'endpoint': os.getenv('JAEGER_ENDPOINT', 'http://localhost:14268/api/traces'),
            'service_name': 'helm-ai',
            'enabled': os.getenv('JAEGER_ENABLED', 'false').lower() == 'true'
        }
    
    def start_span(self, operation_name: str, service_name: str,
                   parent_span_id: Optional[str] = None,
                   tags: Dict[str, Any] = None) -> TraceSpan:
        """Start a new trace span"""
        trace_id = self._get_or_create_trace_id()
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            start_time=datetime.now(),
            tags=tags or {}
        )
        
        with self.lock:
            self.active_spans[span_id] = span
        
        logger.debug(f"Started span: {span_id} - {operation_name}")
        return span
    
    def finish_span(self, span_id: str, status: str = "ok",
                    tags: Dict[str, Any] = None,
                    logs: List[Dict[str, Any]] = None):
        """Finish a trace span"""
        with self.lock:
            span = self.active_spans.get(span_id)
            if not span:
                logger.warning(f"Span not found: {span_id}")
                return
            
            span.end_time = datetime.now()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            
            if tags:
                span.tags.update(tags)
            
            if logs:
                span.logs.extend(logs)
            
            # Move to completed spans
            del self.active_spans[span_id]
            self.completed_spans.append(span)
            
            # Update service metrics
            self._update_service_metrics(span)
            
            # Export to Jaeger if enabled
            if self.jaeger_config['enabled']:
                self._export_to_jaeger(span)
            
            logger.debug(f"Finished span: {span_id} - {span.operation_name} ({span.duration_ms:.2f}ms)")
    
    @contextlib.contextmanager
    def trace_span(self, operation_name: str, service_name: str,
                    parent_span_id: Optional[str] = None,
                    tags: Dict[str, Any] = None):
        """Context manager for tracing"""
        span = self.start_span(operation_name, service_name, parent_span_id, tags)
        
        try:
            yield span
        except Exception as e:
            self.finish_span(span.span_id, "error", 
                           tags={'error': str(e)},
                           logs=[{'event': 'exception', 'error': str(e), 'stack_trace': 'would_capture_stack_trace'}])
            raise
        else:
            self.finish_span(span.span_id, "ok")
    
    def _get_or_create_trace_id(self) -> str:
        """Get or create trace ID from context"""
        # In practice, this would extract from HTTP headers or other context
        # For now, generate a new trace ID
        return str(uuid.uuid4())
    
    def _update_service_metrics(self, span: TraceSpan):
        """Update service performance metrics"""
        service_name = span.service_name
        
        # Get current metrics
        with self.lock:
            metrics_queue = self.service_metrics[service_name]
            
            if metrics_queue:
                current_metrics = metrics_queue[-1]
            else:
                current_metrics = ServiceMetrics(
                    service_name=service_name,
                    timestamp=datetime.now(),
                    request_count=0,
                    error_count=0,
                    avg_response_time=0,
                    p95_response_time=0,
                    p99_response_time=0,
                    throughput=0,
                    error_rate=0
                )
                metrics_queue.append(current_metrics)
        
        # Update metrics
        current_metrics.request_count += 1
        
        if span.status != "ok":
            current_metrics.error_count += 1
        
        if span.duration_ms:
            # Update response time metrics
            response_times = [s.duration_ms for s in list(metrics_queue) if s.duration_ms]
            if response_times:
                current_metrics.avg_response_time = sum(response_times) / len(response_times)
                current_metrics.p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 20 else max(response_times)
                current_metrics.p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) > 100 else max(response_times)
        
        # Calculate error rate and throughput
        if current_metrics.request_count > 0:
            current_metrics.error_rate = (current_metrics.error_count / current_metrics.request_count) * 100
            
            # Calculate throughput (requests per second over last minute)
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_requests = len([s for s in list(metrics_queue) if s.start_time > one_minute_ago])
            current_metrics.throughput = recent_requests / 60.0
    
    def _export_to_jaeger(self, span: TraceSpan):
        """Export span to Jaeger"""
        try:
            import requests
            
            # Convert to Jaeger format
            jaeger_span = {
                "traceID": span.trace_id,
                "spanID": span.span_id,
                "operationName": span.operation_name,
                "references": [],
                "startTime": int(span.start_time.timestamp() * 1000000),  # microseconds
                "duration": int(span.duration_ms * 1000),  # microseconds
                "tags": [
                    {"key": "service.name", "value": span.service_name},
                    {"key": "span.kind", "value": "server"},
                    {"key": "component", "value": "helm-ai"}
                ],
                "status": {"code": span.status},
                "logs": [
                    {
                        "timestamp": int(log.get('timestamp', time.time() * 1000000)),
                        "level": log.get('level', 'info'),
                        "message": log.get('message', '')
                    }
                    for log in span.logs
                ]
            }
            
            # Add parent reference if exists
            if span.parent_span_id:
                jaeger_span["references"].append({
                    "refType": "CHILD_OF",
                    "traceID": span.trace_id,
                    "spanID": span.parent_span_id
                })
            
            # Add custom tags
            for key, value in span.tags.items():
                jaeger_span["tags"].append({
                    "key": key,
                    "value": str(value)
                })
            
            # Send to Jaeger
            response = requests.post(
                f"{self.jaeger_config['endpoint']}/api/traces",
                json=[jaeger_span],
                timeout=5
            )
            
            if response.status_code == 202:
                logger.debug(f"Span exported to Jaeger: {span.span_id}")
            else:
                logger.warning(f"Failed to export span to Jaeger: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error exporting to Jaeger: {e}")
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get complete trace by ID"""
        with self.lock:
            spans = [s for s in self.completed_spans if s.trace_id == trace_id]
        
        if not spans:
            return None
        
        # Sort by start time to build trace tree
        spans.sort(key=lambda s: s.start_time)
        
        # Build trace tree
        trace_data = {
            'trace_id': trace_id,
            'spans': [span.to_dict() for span in spans],
            'root_span': spans[0].to_dict() if spans else None,
            'total_duration': max([s.duration_ms for s in spans if s.duration_ms]) if spans else 0,
            'span_count': len(spans),
            'services': list(set(s.service_name for s in spans)),
            'errors': len([s for s in spans if s.status != 'ok'])
        }
        
        return trace_data
    
    def get_service_metrics(self, service_name: str, minutes: int = 5) -> Optional[ServiceMetrics]:
        """Get service metrics"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            metrics_queue = self.service_metrics.get(service_name)
            
            if not metrics_queue:
                return None
            
            # Get most recent metrics within time window
            recent_metrics = [m for m in metrics_queue if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return None
            
            # Aggregate metrics
            total_requests = sum(m.request_count for m in recent_metrics)
            total_errors = sum(m.error_count for m in recent_metrics)
            
            if total_requests > 0:
                aggregated = ServiceMetrics(
                    service_name=service_name,
                    timestamp=datetime.now(),
                    request_count=total_requests,
                    error_count=total_errors,
                    avg_response_time=sum(m.avg_response_time for m in recent_metrics) / len(recent_metrics),
                    p95_response_time=max(m.p95_response_time for m in recent_metrics),
                    p99_response_time=max(m.p99_response_time for m in recent_metrics),
                    throughput=total_requests / (minutes * 60),
                    error_rate=(total_errors / total_requests) * 100
                )
            else:
                aggregated = recent_metrics[-1]  # Return most recent if no requests
            
            return aggregated
    
    def get_trace_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get tracing summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            recent_spans = [s for s in self.completed_spans if s.end_time and s.end_time >= cutoff_time]
        
        if not recent_spans:
            return {
                'period_hours': hours,
                'total_traces': 0,
                'total_spans': 0,
                'services': {},
                'error_rate': 0,
                'avg_duration': 0,
                'p95_duration': 0
            }
        
        # Group by service
        services = defaultdict(list)
        for span in recent_spans:
            services[span.service_name].append(span)
        
        # Calculate metrics
        total_spans = len(recent_spans)
        error_spans = len([s for s in recent_spans if s.status != 'ok'])
        durations = [s.duration_ms for s in recent_spans if s.duration_ms]
        
        service_summary = {}
        for service_name, service_spans in services.items():
            service_errors = len([s for s in service_spans if s.status != 'ok'])
            service_durations = [s.duration_ms for s in service_spans if s.duration_ms]
            
            service_summary[service_name] = {
                'span_count': len(service_spans),
                'error_count': service_errors,
                'error_rate': (service_errors / len(service_spans)) * 100 if service_spans else 0,
                'avg_duration': sum(service_durations) / len(service_durations) if service_durations else 0,
                'p95_duration': sorted(service_durations)[int(len(service_durations) * 0.95)] if len(service_durations) > 20 else max(service_durations) if service_durations else 0
            }
        
        return {
            'period_hours': hours,
            'total_traces': len(set(s.trace_id for s in recent_spans)),
            'total_spans': total_spans,
            'services': service_summary,
            'error_rate': (error_spans / total_spans) * 100 if total_spans > 0 else 0,
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'p95_duration': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations) if durations else 0
        }
    
    def get_active_spans(self) -> List[TraceSpan]:
        """Get currently active spans"""
        with self.lock:
            return list(self.active_spans.values())
    
    def cleanup_old_spans(self, hours: int = 24):
        """Clean up old spans to prevent memory issues"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            # Clean up completed spans
            original_size = len(self.completed_spans)
            self.completed_spans = deque(
                [s for s in self.completed_spans if s.end_time and s.end_time >= cutoff_time],
                maxlen=10000
            )
            
            # Clean up service metrics
            for service_name in list(self.service_metrics.keys()):
                metrics_queue = self.service_metrics[service_name]
                original_metrics_size = len(metrics_queue)
                self.service_metrics[service_name] = deque(
                    [m for m in metrics_queue if m.timestamp >= cutoff_time],
                    maxlen=1000
                )
            
            cleaned_spans = original_size - len(self.completed_spans)
            cleaned_metrics = sum(original_metrics_size - len(self.service_metrics[service_name]) 
                              for service_name in list(self.service_metrics.keys()))
            
            if cleaned_spans > 0 or cleaned_metrics > 0:
                logger.info(f"Cleaned up {cleaned_spans} spans and {cleaned_metrics} metrics older than {hours} hours")

class OpenTelemetryCollector:
    """OpenTelemetry-compatible collector"""
    
    def __init__(self):
        self.tracer = DistributedTracer()
        self.enabled = os.getenv('OPENTELEMETRY_ENABLED', 'false').lower() == 'true'
        
    def create_span(self, name: str, kind: str = "internal",
                    attributes: Dict[str, Any] = None) -> TraceSpan:
        """Create OpenTelemetry-compatible span"""
        if not self.enabled:
            # Return dummy span
            return TraceSpan(
                trace_id="dummy",
                span_id="dummy",
                operation_name=name,
                service_name="helm-ai",
                start_time=datetime.now(),
                tags=attributes or {}
            )
        
        return self.tracer.start_span(
            operation_name=name,
            service_name="helm-ai",
            tags=attributes
        )
    
    def finish_span(self, span: TraceSpan, status: str = "ok"):
        """Finish OpenTelemetry-compatible span"""
        if not self.enabled:
            return
        
        self.tracer.finish_span(span.span_id, status)

class PerformanceProfiler:
    """Performance profiling and analysis"""
    
    def __init__(self):
        self.profiles = deque(maxlen=1000)
        self.lock = threading.RLock()
    
    @contextlib.contextmanager
    def profile(self, operation_name: str, service_name: str):
        """Profile an operation"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            profile_data = {
                'operation_name': operation_name,
                'service_name': service_name,
                'timestamp': datetime.now(),
                'duration_ms': (end_time - start_time) * 1000,
                'memory_before': start_memory,
                'memory_after': end_memory,
                'memory_delta': end_memory - start_memory
            }
            
            with self.lock:
                self.profiles.append(profile_data)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            return psutil.Process().memory_info.rss / 1024 / 1024
        except:
            return 0.0
    
    def get_performance_report(self, minutes: int = 5) -> Dict[str, Any]:
        """Get performance profiling report"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_profiles = [p for p in self.profiles if p['timestamp'] >= cutoff_time]
        
        if not recent_profiles:
            return {
                'period_minutes': minutes,
                'total_operations': 0,
                'avg_duration_ms': 0,
                'max_duration_ms': 0,
                'memory_usage': {
                    'avg_delta': 0,
                    'max_delta': 0
                },
                'slow_operations': []
            }
        
        # Calculate metrics
        durations = [p['duration_ms'] for p in recent_profiles]
        memory_deltas = [p['memory_delta'] for p in recent_profiles]
        
        # Find slow operations
        slow_operations = sorted(
            recent_profiles,
            key=lambda p: p['duration_ms'],
            reverse=True
        )[:10]
        
        return {
            'period_minutes': minutes,
            'total_operations': len(recent_profiles),
            'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
            'max_duration_ms': max(durations) if durations else 0,
            'memory_usage': {
                'avg_delta': sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
                'max_delta': max(memory_deltas) if memory_deltas else 0
            },
            'slow_operations': [
                {
                    'operation_name': p['operation_name'],
                    'service_name': p['service_name'],
                    'duration_ms': p['duration_ms'],
                    'memory_delta': p['memory_delta'],
                    'timestamp': p['timestamp'].isoformat()
                }
                for p in slow_operations
            ]
        }

# Global instances
distributed_tracer = DistributedTracer()
otel_collector = OpenTelemetryCollector()
performance_profiler = PerformanceProfiler()

def trace_span(operation_name: str, service_name: str = "helm-ai",
                parent_span_id: Optional[str] = None,
                tags: Dict[str, Any] = None):
    """Create a trace span"""
    return distributed_tracer.trace_span(
        operation_name=operation_name,
        service_name=service_name,
        parent_span_id=parent_span_id,
        tags=tags
    )

def get_trace_summary(hours: int = 1) -> Dict[str, Any]:
    """Get distributed tracing summary"""
    return distributed_tracer.get_trace_summary(hours)

def get_service_metrics(service_name: str, minutes: int = 5) -> Optional[ServiceMetrics]:
    """Get service performance metrics"""
    return distributed_tracer.get_service_metrics(service_name, minutes)

def get_performance_report(minutes: int = 5) -> Dict[str, Any]:
    """Get performance profiling report"""
    return performance_profiler.get_performance_report(minutes)
