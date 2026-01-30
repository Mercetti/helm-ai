"""
Helm AI Third-Party Integration Framework
Provides comprehensive integration capabilities for external services and APIs
"""

import os
import sys
import json
import time
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import uuid

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import get_database_manager
from monitoring.structured_logging import logger

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    integration_id: str
    name: str
    provider: str
    type: str  # api, webhook, database, messaging
    version: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    credentials: Dict[str, str] = field(default_factory=dict)
    rate_limit: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'integration_id': self.integration_id,
            'name': self.name,
            'provider': self.provider,
            'type': self.type,
            'version': self.version,
            'enabled': self.enabled,
            'config': self.config,
            'credentials': {k: '***' for k, v in self.credentials.items()},  # Hide credentials
            'rate_limit': self.rate_limit,
            'retry_config': self.retry_config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class IntegrationEvent:
    """Integration event log"""
    event_id: str
    integration_id: str
    event_type: str  # request, response, error, webhook_received
    timestamp: datetime
    direction: str  # inbound, outbound
    status: str  # success, error, pending
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'integration_id': self.integration_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'direction': self.direction,
            'status': self.status,
            'request_data': self.request_data,
            'response_data': self.response_data,
            'error_message': self.error_message,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata
        }

@dataclass
class WebhookEvent:
    """Webhook event data"""
    webhook_id: str
    integration_id: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    received_at: datetime
    processed: bool = False
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'webhook_id': self.webhook_id,
            'integration_id': self.integration_id,
            'event_type': self.event_type,
            'payload': self.payload,
            'headers': self.headers,
            'received_at': self.received_at.isoformat(),
            'processed': self.processed,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message
        }

class IntegrationManager:
    """Third-party integration management system"""
    
    def __init__(self):
        self.integrations = {}
        self.webhooks = deque(maxlen=1000)
        self.events = deque(maxlen=10000)
        self.rate_limiters = {}
        self.lock = threading.RLock()
        
        # Setup built-in integrations
        self._setup_builtin_integrations()
        
    def _setup_builtin_integrations(self):
        """Setup built-in integration templates"""
        # Stripe Integration
        self.integrations['stripe'] = IntegrationConfig(
            integration_id='stripe',
            name='Stripe Payment Processing',
            provider='Stripe',
            type='api',
            version='v1',
            config={
                'base_url': 'https://api.stripe.com/v1',
                'webhook_endpoint': '/webhooks/stripe',
                'supported_events': ['payment_intent.succeeded', 'payment_intent.payment_failed', 'invoice.payment_succeeded']
            },
            rate_limit={
                'requests_per_second': 100,
                'burst_limit': 200
            },
            retry_config={
                'max_retries': 3,
                'backoff_factor': 2,
                'retry_delay': 1.0
            }
        )
        
        # HubSpot Integration
        self.integrations['hubspot'] = IntegrationConfig(
            integration_id='hubspot',
            name='HubSpot CRM',
            provider='HubSpot',
            type='api',
            version='v3',
            config={
                'base_url': 'https://api.hubapi.com',
                'webhook_endpoint': '/webhooks/hubspot',
                'supported_events': ['contact.creation', 'deal.creation', 'company.creation']
            },
            rate_limit={
                'requests_per_second': 100,
                'burst_limit': 300
            },
            retry_config={
                'max_retries': 3,
                'backoff_factor': 2,
                'retry_delay': 1.0
            }
        )
        
        # Slack Integration
        self.integrations['slack'] = IntegrationConfig(
            integration_id='slack',
            name='Slack Messaging',
            provider='Slack',
            type='api',
            version='v1',
            config={
                'base_url': 'https://slack.com/api',
                'webhook_endpoint': '/webhooks/slack',
                'supported_events': ['message', 'reaction_added', 'member_joined']
            },
            rate_limit={
                'requests_per_second': 50,
                'burst_limit': 100
            },
            retry_config={
                'max_retries': 2,
                'backoff_factor': 2,
                'retry_delay': 1.0
            }
        )
        
        # Salesforce Integration
        self.integrations['salesforce'] = IntegrationConfig(
            integration_id='salesforce',
            name='Salesforce CRM',
            provider='Salesforce',
            type='api',
            version='v52.0',
            config={
                'base_url': 'https://login.salesforce.com',
                'webhook_endpoint': '/webhooks/salesforce',
                'supported_events': ['Account.created', 'Contact.created', 'Opportunity.created']
            },
            rate_limit={
                'requests_per_second': 100,
                'burst_limit': 200
            },
            retry_config={
                'max_retries': 3,
                'backoff_factor': 2,
                'retry_delay': 1.0
            }
        )
    
    def register_integration(self, integration_config: IntegrationConfig) -> str:
        """Register a new integration"""
        try:
            with self.lock:
                self.integrations[integration_config.integration_id] = integration_config
            
            # Initialize rate limiter
            self._initialize_rate_limiter(integration_config)
            
            logger.info(f"Integration registered: {integration_config.integration_id}")
            return integration_config.integration_id
            
        except Exception as e:
            logger.error(f"Error registering integration: {e}")
            raise
    
    def _initialize_rate_limiter(self, config: IntegrationConfig):
        """Initialize rate limiter for integration"""
        rate_limit = config.rate_limit
        self.rate_limiters[config.integration_id] = {
            'tokens': rate_limit.get('burst_limit', 100),
            'max_tokens': rate_limit.get('burst_limit', 100),
            'refill_rate': rate_limit.get('requests_per_second', 10),
            'last_refill': time.time()
        }
    
    def _check_rate_limit(self, integration_id: str) -> bool:
        """Check if request is within rate limit"""
        rate_limiter = self.rate_limiters.get(integration_id)
        if not rate_limiter:
            return True
        
        current_time = time.time()
        
        # Refill tokens based on elapsed time
        elapsed = current_time - rate_limiter['last_refill']
        tokens_to_add = int(elapsed * rate_limiter['refill_rate'])
        
        if tokens_to_add > 0:
            rate_limiter['tokens'] = min(rate_limiter['tokens'] + tokens_to_add, rate_limiter['max_tokens'])
            rate_limiter['last_refill'] = current_time
        
        # Check if we have tokens
        if rate_limiter['tokens'] > 0:
            rate_limiter['tokens'] -= 1
            return True
        else:
            return False
    
    def make_api_request(self, integration_id: str, method: str, endpoint: str,
                        data: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make API request to integration"""
        integration = self.integrations.get(integration_id)
        if not integration or not integration.enabled:
            raise ValueError(f"Integration {integration_id} not found or disabled")
        
        # Check rate limit
        if not self._check_rate_limit(integration_id):
            raise Exception(f"Rate limit exceeded for {integration_id}")
        
        event_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Build request
            url = f"{integration.config['base_url']}{endpoint}"
            
            # Add authentication
            auth_headers = self._build_auth_headers(integration)
            if headers:
                auth_headers.update(headers)
            
            # Make request
            response = requests.request(
                method=method.upper(),
                url=url,
                json=data,
                headers=auth_headers,
                timeout=30
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log event
            event = IntegrationEvent(
                event_id=event_id,
                integration_id=integration_id,
                event_type='request',
                timestamp=datetime.now(),
                direction='outbound',
                status='success' if response.status_code < 400 else 'error',
                request_data=data,
                response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                duration_ms=duration_ms,
                metadata={
                    'method': method,
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'response_headers': dict(response.headers)
                }
            )
            
            with self.lock:
                self.events.append(event)
            
            # Handle response
            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} {response.reason}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"API request successful: {integration_id} - {method} {endpoint}")
            
            return {
                'status_code': response.status_code,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'headers': dict(response.headers),
                'duration_ms': duration_ms
            }
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error event
            error_event = IntegrationEvent(
                event_id=event_id,
                integration_id=integration_id,
                event_type='request',
                timestamp=datetime.now(),
                direction='outbound',
                status='error',
                request_data=data,
                error_message=str(e),
                duration_ms=duration_ms,
                metadata={
                    'method': method,
                    'endpoint': endpoint
                }
            )
            
            with self.lock:
                self.events.append(error_event)
            
            # Retry logic
            if self._should_retry(integration, str(e)):
                logger.info(f"Retrying request for {integration_id}")
                time.sleep(integration.retry_config['retry_delay'])
                return self.make_api_request(integration_id, method, endpoint, data, headers)
            
            raise
    
    def _build_auth_headers(self, integration: IntegrationConfig) -> Dict[str, str]:
        """Build authentication headers"""
        headers = {}
        
        if integration.provider == 'Stripe':
            # Stripe uses API key in Authorization header
            api_key = integration.credentials.get('api_key')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        elif integration.provider == 'HubSpot':
            # HubSpot uses API key in Authorization header
            api_key = integration.credentials.get('api_key')
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        
        elif integration.provider == 'Slack':
            # Slack uses Bearer token
            bot_token = integration.credentials.get('bot_token')
            if bot_token:
                headers['Authorization'] = f'Bearer {bot_token}'
        
        elif integration.provider == 'Salesforce':
            # Salesforce uses OAuth token
            access_token = integration.credentials.get('access_token')
            if access_token:
                headers['Authorization'] = f'Bearer {access_token}'
        
        return headers
    
    def _should_retry(self, integration: IntegrationConfig, error_message: str) -> bool:
        """Determine if request should be retried"""
        retry_config = integration.retry_config
        
        # Don't retry authentication errors
        if '401' in error_message or '403' in error_message:
            return False
        
        # Don't retry rate limit errors (they're handled separately)
        if '429' in error_message:
            return False
        
        # Check if we have retries left
        return retry_config.get('max_retries', 0) > 0
    
    def process_webhook(self, integration_id: str, event_type: str, payload: Dict[str, Any],
                       headers: Dict[str, str]) -> str:
        """Process incoming webhook"""
        webhook_id = str(uuid.uuid4())
        
        webhook = WebhookEvent(
            webhook_id=webhook_id,
            integration_id=integration_id,
            event_type=event_type,
            payload=payload,
            headers=headers,
            received_at=datetime.now()
        )
        
        try:
            # Validate webhook signature if applicable
            if self._validate_webhook_signature(integration_id, payload, headers):
                # Process webhook
                self._handle_webhook_event(webhook)
                
                webhook.processed = True
                webhook.processed_at = datetime.now()
                
                logger.info(f"Webhook processed: {webhook_id} - {event_type}")
            else:
                webhook.error_message = "Invalid webhook signature"
                logger.warning(f"Invalid webhook signature: {webhook_id}")
            
        except Exception as e:
            webhook.error_message = str(e)
            logger.error(f"Error processing webhook {webhook_id}: {e}")
        
        with self.lock:
            self.webhooks.append(webhook)
        
        return webhook_id
    
    def _validate_webhook_signature(self, integration_id: str, payload: Dict[str, Any],
                                  headers: Dict[str, str]) -> bool:
        """Validate webhook signature"""
        integration = self.integrations.get(integration_id)
        if not integration:
            return False
        
        # Different providers have different signature methods
        if integration.provider == 'Stripe':
            return self._validate_stripe_signature(integration, payload, headers)
        elif integration.provider == 'HubSpot':
            return self._validate_hubspot_signature(integration, payload, headers)
        elif integration.provider == 'Slack':
            return self._validate_slack_signature(integration, payload, headers)
        
        # For now, accept all webhooks
        return True
    
    def _validate_stripe_signature(self, integration: IntegrationConfig, payload: Dict[str, Any],
                                 headers: Dict[str, str]) -> bool:
        """Validate Stripe webhook signature"""
        try:
            stripe_signature = headers.get('stripe-signature')
            if not stripe_signature:
                return False
            
            webhook_secret = integration.credentials.get('webhook_secret')
            if not webhook_secret:
                return False
            
            # Stripe signature format: t=timestamp,v1=signature
            timestamp, signature = stripe_signature.split('v1=')
            timestamp = timestamp.split('t=')[1]
            
            # Create expected signature
            payload_string = f"{timestamp}.{json.dumps(payload, separators=(',', ':'))}"
            expected_signature = hmac.new(
                webhook_secret.encode(),
                payload_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error validating Stripe signature: {e}")
            return False
    
    def _validate_hubspot_signature(self, integration: IntegrationConfig, payload: Dict[str, Any],
                                  headers: Dict[str, str]) -> bool:
        """Validate HubSpot webhook signature"""
        # HubSpot signature validation logic
        return True  # Simplified for now
    
    def _validate_slack_signature(self, integration: IntegrationConfig, payload: Dict[str, Any],
                               headers: Dict[str, str]) -> bool:
        """Validate Slack webhook signature"""
        # Slack signature validation logic
        return True  # Simplified for now
    
    def _handle_webhook_event(self, webhook: WebhookEvent):
        """Handle webhook event"""
        integration = self.integrations.get(webhook.integration_id)
        if not integration:
            return
        
        # Route to appropriate handler based on event type
        if integration.provider == 'Stripe':
            self._handle_stripe_webhook(webhook)
        elif integration.provider == 'HubSpot':
            self._handle_hubspot_webhook(webhook)
        elif integration.provider == 'Slack':
            self._handle_slack_webhook(webhook)
    
    def _handle_stripe_webhook(self, webhook: WebhookEvent):
        """Handle Stripe webhook event"""
        event_type = webhook.event_type
        
        if event_type == 'payment_intent.succeeded':
            # Handle successful payment
            self._process_stripe_payment_success(webhook.payload)
        elif event_type == 'payment_intent.payment_failed':
            # Handle failed payment
            self._process_stripe_payment_failure(webhook.payload)
        
        logger.info(f"Stripe webhook processed: {event_type}")
    
    def _handle_hubspot_webhook(self, webhook: WebhookEvent):
        """Handle HubSpot webhook event"""
        event_type = webhook.event_type
        
        if event_type == 'contact.creation':
            self._process_hubspot_contact_creation(webhook.payload)
        elif event_type == 'deal.creation':
            self._process_hubspot_deal_creation(webhook.payload)
        
        logger.info(f"HubSpot webhook processed: {event_type}")
    
    def _handle_slack_webhook(self, webhook: WebhookEvent):
        """Handle Slack webhook event"""
        event_type = webhook.event_type
        
        if event_type == 'message':
            self._process_slack_message(webhook.payload)
        elif event_type == 'reaction_added':
            self._process_slack_reaction(webhook.payload)
        
        logger.info(f"Slack webhook processed: {event_type}")
    
    def _process_stripe_payment_success(self, payload: Dict[str, Any]):
        """Process successful Stripe payment"""
        try:
            payment_intent = payload.get('data', {}).get('object', {})
            customer_id = payment_intent.get('customer')
            amount = payment_intent.get('amount')
            
            # Update user subscription status
            if customer_id:
                db_manager = get_database_manager()
                
                with db_manager.get_session() as session:
                    # Find user by Stripe customer ID
                    result = session.execute(text("""
                        UPDATE users SET subscription_status = 'active',
                                       updated_at = NOW()
                        WHERE stripe_customer_id = :customer_id
                    """), {'customer_id': customer_id})
                    
                    logger.info(f"Updated subscription status for customer {customer_id}")
            
        except Exception as e:
            logger.error(f"Error processing Stripe payment success: {e}")
    
    def _process_stripe_payment_failure(self, payload: Dict[str, Any]):
        """Process failed Stripe payment"""
        try:
            payment_intent = payload.get('data', {}).get('object', {})
            customer_id = payment_intent.get('customer')
            
            # Update user subscription status
            if customer_id:
                db_manager = get_database_manager()
                
                with db_manager.get_session() as session:
                    result = session.execute(text("""
                        UPDATE users SET subscription_status = 'payment_failed',
                                       updated_at = NOW()
                        WHERE stripe_customer_id = :customer_id
                    """), {'customer_id': customer_id})
                    
                    logger.info(f"Updated subscription status for customer {customer_id}")
            
        except Exception as e:
            logger.error(f"Error processing Stripe payment failure: {e}")
    
    def _process_hubspot_contact_creation(self, payload: Dict[str, Any]):
        """Process HubSpot contact creation"""
        # Handle new contact creation
        logger.info(f"Processing HubSpot contact creation: {payload}")
    
    def _process_hubspot_deal_creation(self, payload: Dict[str, Any]):
        """Process HubSpot deal creation"""
        # Handle new deal creation
        logger.info(f"Processing HubSpot deal creation: {payload}")
    
    def _process_slack_message(self, payload: Dict[str, Any]):
        """Process Slack message"""
        # Handle Slack message
        logger.info(f"Processing Slack message: {payload}")
    
    def _process_slack_reaction(self, payload: Dict[str, Any]):
        """Process Slack reaction"""
        # Handle Slack reaction
        logger.info(f"Processing Slack reaction: {payload}")
    
    def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """Get integration status"""
        integration = self.integrations.get(integration_id)
        if not integration:
            raise ValueError(f"Integration not found: {integration_id}")
        
        # Get recent events
        with self.lock:
            recent_events = [e for e in list(self.events) 
                           if e.integration_id == integration_id 
                           and e.timestamp > datetime.now() - timedelta(hours=24)]
        
        # Calculate metrics
        total_requests = len([e for e in recent_events if e.event_type == 'request'])
        successful_requests = len([e for e in recent_events if e.status == 'success'])
        error_rate = (total_requests - successful_requests) / max(total_requests, 1) * 100
        
        avg_response_time = 0
        if recent_events:
            response_times = [e.duration_ms for e in recent_events if e.duration_ms]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            'integration_id': integration_id,
            'name': integration.name,
            'provider': integration.provider,
            'enabled': integration.enabled,
            'status': 'healthy' if error_rate < 5 else 'degraded',
            'metrics': {
                'total_requests_24h': total_requests,
                'success_rate': 100 - error_rate,
                'error_rate': error_rate,
                'avg_response_time_ms': avg_response_time
            },
            'rate_limit': self.rate_limiters.get(integration_id, {}),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_all_integrations(self) -> List[IntegrationConfig]:
        """Get all registered integrations"""
        with self.lock:
            return list(self.integrations.values())
    
    def get_webhook_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get webhook processing summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            recent_webhooks = [w for w in self.webhooks if w.received_at >= cutoff_time]
        
        if not recent_webhooks:
            return {
                'period_hours': hours,
                'total_webhooks': 0,
                'processed_count': 0,
                'error_count': 0,
                'by_integration': {},
                'by_event_type': {}
            }
        
        processed_count = len([w for w in recent_webhooks if w.processed])
        error_count = len([w for w in recent_webhooks if w.error_message])
        
        # Group by integration
        by_integration = defaultdict(int)
        for webhook in recent_webhooks:
            by_integration[webhook.integration_id] += 1
        
        # Group by event type
        by_event_type = defaultdict(int)
        for webhook in recent_webhooks:
            by_event_type[webhook.event_type] += 1
        
        return {
            'period_hours': hours,
            'total_webhooks': len(recent_webhooks),
            'processed_count': processed_count,
            'error_count': error_count,
            'success_rate': (processed_count / len(recent_webhooks)) * 100 if recent_webhooks else 0,
            'by_integration': dict(by_integration),
            'by_event_type': dict(by_event_type)
        }

# Global integration manager instance
integration_manager = IntegrationManager()

def register_integration(name: str, provider: str, integration_type: str,
                      config: Dict[str, Any], credentials: Dict[str, str]) -> str:
    """Register a new integration"""
    integration_id = f"{provider.lower()}_{name.lower().replace(' ', '_')}"
    
    integration_config = IntegrationConfig(
        integration_id=integration_id,
        name=name,
        provider=provider,
        type=integration_type,
        version='v1',
        config=config,
        credentials=credentials
    )
    
    return integration_manager.register_integration(integration_config)

def make_api_request(integration_id: str, method: str, endpoint: str,
                    data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Make API request to integration"""
    return integration_manager.make_api_request(integration_id, method, endpoint, data, headers)

def process_webhook(integration_id: str, event_type: str, payload: Dict[str, Any],
                   headers: Dict[str, str]) -> str:
    """Process incoming webhook"""
    return integration_manager.process_webhook(integration_id, event_type, payload, headers)

def get_integration_status(integration_id: str) -> Dict[str, Any]:
    """Get integration status"""
    return integration_manager.get_integration_status(integration_id)
