"""
Webhook System for Event-Driven Integrations for Helm AI
========================================================

This module provides comprehensive webhook capabilities:
- Webhook endpoint management
- Event subscription and filtering
- Secure webhook delivery
- Retry mechanisms and error handling
- Webhook analytics and monitoring
- Event transformation and enrichment
- Batch webhook processing
- Webhook signature verification
"""

import asyncio
import json
import logging
import uuid
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import defaultdict

# Third-party imports
import aiohttp
import redis
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.security.encryption import EncryptionManager

logger = StructuredLogger("webhook_system")

Base = declarative_base()


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    DISABLED = "disabled"


class EventType(str, Enum):
    """Event types"""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    PAYMENT_PROCESSED = "payment.processed"
    PAYMENT_FAILED = "payment.failed"
    INVOICE_GENERATED = "invoice.generated"
    ANALYTICS_REPORT = "analytics.report"
    SECURITY_ALERT = "security.alert"
    SYSTEM_EVENT = "system.event"


class RetryStrategy(str, Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    IMMEDIATE = "immediate"


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    id: str
    name: str
    url: str
    secret: str
    events: List[EventType]
    headers: Dict[str, str] = field(default_factory=dict)
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 3
    timeout_seconds: int = 30
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WebhookEvent:
    """Webhook event data"""
    id: str
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "stellar_logic_ai"
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt"""
    id: str
    webhook_id: str
    event_id: str
    attempt_number: int
    status: WebhookStatus
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    delivered_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class WebhookEndpoints(Base):
    """SQLAlchemy model for webhook endpoints"""
    __tablename__ = "webhook_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(1000), nullable=False)
    secret = Column(String(255), nullable=False)
    events = Column(JSONB)  # List of event types
    headers = Column(JSONB)
    retry_strategy = Column(String(50), default="exponential_backoff")
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookEvents(Base):
    """SQLAlchemy model for webhook events"""
    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False)
    data = Column(JSONB)
    source = Column(String(255), default="helm_ai")
    version = Column(String(20), default="1.0")
    metadata = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class WebhookDeliveries(Base):
    """SQLAlchemy model for webhook deliveries"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(String(255), nullable=False, unique=True, index=True)
    webhook_id = Column(String(255), nullable=False, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    attempt_number = Column(Integer, default=1)
    status = Column(String(20), default="pending")
    response_code = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)
    duration_ms = Column(Float)
    delivered_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class WebhookSystem:
    """Webhook System for Event-Driven Integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.encryption_manager = EncryptionManager(config.get('encryption', {}))
        
        # Initialize Redis for caching and queue
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Storage
        self.webhook_endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_queue = asyncio.Queue()
        
        # Metrics
        self.webhook_counter = Counter('webhook_deliveries_total', ['status', 'event_type'])
        self.webhook_duration = Histogram('webhook_delivery_duration_seconds', ['webhook_id'])
        self.pending_webhooks = Gauge('webhook_pending_deliveries')
        
        # FastAPI app
        self.app = FastAPI(title="Helm AI Webhook System")
        self._setup_routes()
        
        # Background tasks
        self.delivery_task = None
        self.retry_task = None
        
        logger.info("Webhook System initialized")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.post("/webhooks/{webhook_id}")
        async def receive_webhook(webhook_id: str, request: Request):
            """Receive incoming webhook"""
            return await self._handle_incoming_webhook(webhook_id, request)
        
        @self.app.post("/events")
        async def trigger_event(event: Dict[str, Any], background_tasks: BackgroundTasks):
            """Trigger a new event"""
            return await self._trigger_event(event, background_tasks)
        
        @self.app.get("/webhooks")
        async def list_webhooks():
            """List all webhook endpoints"""
            return await self._list_webhooks()
        
        @self.app.post("/webhooks")
        async def create_webhook(webhook: Dict[str, Any]):
            """Create a new webhook endpoint"""
            return await self._create_webhook_endpoint(webhook)
        
        @self.app.get("/webhooks/{webhook_id}/deliveries")
        async def get_webhook_deliveries(webhook_id: str):
            """Get webhook delivery history"""
            return await self._get_webhook_deliveries(webhook_id)
    
    async def start_background_tasks(self):
        """Start background processing tasks"""
        try:
            self.delivery_task = asyncio.create_task(self._process_deliveries())
            self.retry_task = asyncio.create_task(self._process_retries())
            
            logger.info("Webhook background tasks started")
            
        except Exception as e:
            logger.error("Failed to start background tasks", error=str(e))
    
    async def stop_background_tasks(self):
        """Stop background processing tasks"""
        try:
            if self.delivery_task:
                self.delivery_task.cancel()
            if self.retry_task:
                self.retry_task.cancel()
            
            logger.info("Webhook background tasks stopped")
            
        except Exception as e:
            logger.error("Failed to stop background tasks", error=str(e))
    
    async def create_webhook_endpoint(self, webhook: WebhookEndpoint) -> bool:
        """Create a new webhook endpoint"""
        try:
            # Validate webhook
            if not await self._validate_webhook_endpoint(webhook):
                return False
            
            # Store webhook
            self.webhook_endpoints[webhook.id] = webhook
            
            # Save to database
            webhook_record = WebhookEndpoints(
                webhook_id=webhook.id,
                name=webhook.name,
                url=webhook.url,
                secret=webhook.secret,
                events=[event.value for event in webhook.events],
                headers=webhook.headers,
                retry_strategy=webhook.retry_strategy.value,
                max_retries=webhook.max_retries,
                timeout_seconds=webhook.timeout_seconds,
                enabled=webhook.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(webhook_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Webhook endpoint created", webhook_id=webhook.id)
            return True
            
        except Exception as e:
            logger.error("Failed to create webhook endpoint", webhook_id=webhook.id, error=str(e))
            return False
    
    async def _validate_webhook_endpoint(self, webhook: WebhookEndpoint) -> bool:
        """Validate webhook endpoint"""
        try:
            # Check required fields
            if not webhook.name or not webhook.url or not webhook.secret:
                return False
            
            # Validate URL format
            if not webhook.url.startswith(('http://', 'https://')):
                return False
            
            # Validate events
            if not webhook.events:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Webhook endpoint validation failed", error=str(e))
            return False
    
    async def trigger_event(self, event: WebhookEvent) -> bool:
        """Trigger a new event"""
        try:
            # Store event
            event_record = WebhookEvents(
                event_id=event.id,
                event_type=event.event_type.value,
                data=event.data,
                source=event.source,
                version=event.version,
                metadata=event.metadata,
                timestamp=event.timestamp
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(event_record)
                session.commit()
            finally:
                session.close()
            
            # Find matching webhooks
            matching_webhooks = [
                webhook for webhook in self.webhook_endpoints.values()
                if webhook.enabled and event.event_type in webhook.events
            ]
            
            # Create delivery tasks
            for webhook in matching_webhooks:
                delivery = WebhookDelivery(
                    id=str(uuid.uuid4()),
                    webhook_id=webhook.id,
                    event_id=event.id,
                    attempt_number=1,
                    status=WebhookStatus.PENDING
                )
                
                # Add to queue
                await self.event_queue.put((webhook, event, delivery))
            
            logger.info("Event triggered", event_id=event.id, event_type=event.event_type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to trigger event", event_id=event.id, error=str(e))
            return False
    
    async def _process_deliveries(self):
        """Process webhook deliveries"""
        try:
            while True:
                try:
                    # Get delivery from queue
                    webhook, event, delivery = await self.event_queue.get()
                    
                    # Process delivery
                    await self._deliver_webhook(webhook, event, delivery)
                    
                    self.event_queue.task_done()
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Delivery processing error", error=str(e))
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error("Delivery processing failed", error=str(e))
    
    async def _deliver_webhook(self, webhook: WebhookEndpoint, event: WebhookEvent, delivery: WebhookDelivery):
        """Deliver webhook to endpoint"""
        try:
            start_time = time.time()
            
            # Prepare payload
            payload = {
                "id": event.id,
                "type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "version": event.version
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Helm-AI-Webhook/1.0",
                **webhook.headers
            }
            
            # Add signature
            signature = self._generate_signature(json.dumps(payload), webhook.secret)
            headers["X-Helm-Signature"] = signature
            
            # Make request
            timeout = aiohttp.ClientTimeout(total=webhook.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                ) as response:
                    response_body = await response.text()
                    
                    # Update delivery
                    delivery.duration_ms = (time.time() - start_time) * 1000
                    delivery.response_code = response.status
                    delivery.response_body = response_body
                    delivery.delivered_at = datetime.utcnow()
                    
                    if response.status < 400:
                        delivery.status = WebhookStatus.DELIVERED
                        self.webhook_counter.labels(status="delivered", event_type=event.event_type.value).inc()
                    else:
                        delivery.status = WebhookStatus.FAILED
                        self.webhook_counter.labels(status="failed", event_type=event.event_type.value).inc()
                        
                        # Schedule retry if needed
                        if delivery.attempt_number < webhook.max_retries:
                            delivery.status = WebhookStatus.RETRYING
                            delivery.next_retry_at = self._calculate_retry_time(
                                webhook.retry_strategy, delivery.attempt_number
                            )
            
            # Save delivery
            await self._save_delivery(delivery)
            
            logger.info("Webhook delivered", 
                       webhook_id=webhook.id, event_id=event.id, status=delivery.status.value)
            
        except asyncio.TimeoutError:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = "Timeout"
            await self._save_delivery(delivery)
            
        except Exception as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)
            await self._save_delivery(delivery)
            
            logger.error("Webhook delivery failed", 
                        webhook_id=webhook.id, event_id=event.id, error=str(e))
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate webhook signature"""
        try:
            signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return f"sha256={signature}"
            
        except Exception as e:
            logger.error("Signature generation failed", error=str(e))
            return ""
    
    def _calculate_retry_time(self, strategy: RetryStrategy, attempt_number: int) -> datetime:
        """Calculate retry time based on strategy"""
        try:
            base_delay = 60  # 1 minute base delay
            
            if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                delay = base_delay * (2 ** (attempt_number - 1))
            elif strategy == RetryStrategy.LINEAR_BACKOFF:
                delay = base_delay * attempt_number
            elif strategy == RetryStrategy.FIXED_INTERVAL:
                delay = base_delay
            else:  # IMMEDIATE
                delay = 1
            
            return datetime.utcnow() + timedelta(seconds=delay)
            
        except Exception as e:
            logger.error("Retry time calculation failed", error=str(e))
            return datetime.utcnow() + timedelta(minutes=5)
    
    async def _save_delivery(self, delivery: WebhookDelivery):
        """Save delivery to database"""
        try:
            delivery_record = WebhookDeliveries(
                delivery_id=delivery.id,
                webhook_id=delivery.webhook_id,
                event_id=delivery.event_id,
                attempt_number=delivery.attempt_number,
                status=delivery.status.value,
                response_code=delivery.response_code,
                response_body=delivery.response_body,
                error_message=delivery.error_message,
                duration_ms=delivery.duration_ms,
                delivered_at=delivery.delivered_at,
                next_retry_at=delivery.next_retry_at,
                created_at=delivery.created_at
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(delivery_record)
                session.commit()
            finally:
                session.close()
            
        except Exception as e:
            logger.error("Failed to save delivery", delivery_id=delivery.id, error=str(e))
    
    async def _process_retries(self):
        """Process webhook retries"""
        try:
            while True:
                try:
                    # Get failed deliveries that need retry
                    retry_deliveries = await self._get_retry_deliveries()
                    
                    for delivery_data in retry_deliveries:
                        # Get webhook and event
                        webhook = self.webhook_endpoints.get(delivery_data['webhook_id'])
                        if not webhook or not webhook.enabled:
                            continue
                        
                        # Get event
                        session = self.db_manager.get_session()
                        try:
                            event_record = session.query(WebhookEvents).filter(
                                WebhookEvents.event_id == delivery_data['event_id']
                            ).first()
                            
                            if event_record:
                                event = WebhookEvent(
                                    id=event_record.event_id,
                                    event_type=EventType(event_record.event_type),
                                    data=event_record.data,
                                    timestamp=event_record.timestamp,
                                    source=event_record.source,
                                    version=event_record.version,
                                    metadata=event_record.metadata
                                )
                                
                                # Create new delivery attempt
                                delivery = WebhookDelivery(
                                    id=str(uuid.uuid4()),
                                    webhook_id=delivery_data['webhook_id'],
                                    event_id=delivery_data['event_id'],
                                    attempt_number=delivery_data['attempt_number'] + 1,
                                    status=WebhookStatus.PENDING
                                )
                                
                                # Add to queue
                                await self.event_queue.put((webhook, event, delivery))
                                
                        finally:
                            session.close()
                    
                    # Wait before next check
                    await asyncio.sleep(60)  # Check every minute
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Retry processing error", error=str(e))
                    await asyncio.sleep(60)
                    
        except Exception as e:
            logger.error("Retry processing failed", error=str(e))
    
    async def _get_retry_deliveries(self) -> List[Dict[str, Any]]:
        """Get deliveries that need retry"""
        try:
            session = self.db_manager.get_session()
            try:
                deliveries = session.query(WebhookDeliveries).filter(
                    WebhookDeliveries.status == "retrying",
                    WebhookDeliveries.next_retry_at <= datetime.utcnow()
                ).all()
                
                return [
                    {
                        "delivery_id": d.delivery_id,
                        "webhook_id": d.webhook_id,
                        "event_id": d.event_id,
                        "attempt_number": d.attempt_number
                    }
                    for d in deliveries
                ]
            finally:
                session.close()
                
        except Exception as e:
            logger.error("Failed to get retry deliveries", error=str(e))
            return []
    
    async def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        try:
            expected_signature = self._generate_signature(payload, secret)
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error("Signature verification failed", error=str(e))
            return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_webhooks": len(self.webhook_endpoints),
            "queue_size": self.event_queue.qsize(),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
WEBHOOK_SYSTEM_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": 0
    },
    "encryption": {
        "key": os.getenv("ENCRYPTION_KEY")
    }
}


# Initialize webhook system
webhook_system = WebhookSystem(WEBHOOK_SYSTEM_CONFIG)

# Export main components
__all__ = [
    'WebhookSystem',
    'WebhookEndpoint',
    'WebhookEvent',
    'WebhookDelivery',
    'WebhookStatus',
    'EventType',
    'RetryStrategy',
    'webhook_system'
]
