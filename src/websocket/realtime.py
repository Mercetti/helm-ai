"""
Helm AI Real-time WebSocket Features
Provides real-time communication, notifications, and live updates
"""

import os
import sys
import json
import asyncio
import websockets
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import jwt
from enum import Enum

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from monitoring.distributed_tracing import distributed_tracer
from database.database_manager import get_database_manager

class EventType(Enum):
    """WebSocket event types"""
    NOTIFICATION = "notification"
    SYSTEM_UPDATE = "system_update"
    USER_ACTIVITY = "user_activity"
    ANALYTICS_UPDATE = "analytics_update"
    SECURITY_ALERT = "security_alert"
    CHAT_MESSAGE = "chat_message"
    PRESENCE_UPDATE = "presence_update"
    FILE_UPLOAD = "file_upload"
    TASK_UPDATE = "task_update"
    REAL_TIME_METRICS = "real_time_metrics"

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    event_id: str
    event_type: EventType
    user_id: Optional[str]
    channel: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, critical
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'channel': self.channel,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'ttl': self.ttl,
            'metadata': self.metadata
        }

@dataclass
class WebSocketConnection:
    """WebSocket connection information"""
    connection_id: str
    user_id: Optional[str]
    websocket: Any
    channels: Set[str]
    connected_at: datetime
    last_heartbeat: datetime
    ip_address: str
    user_agent: str
    is_authenticated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'connection_id': self.connection_id,
            'user_id': self.user_id,
            'channels': list(self.channels),
            'connected_at': self.connected_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_authenticated': self.is_authenticated,
            'metadata': self.metadata
        }

@dataclass
class Notification:
    """Real-time notification"""
    notification_id: str
    user_id: str
    title: str
    message: str
    type: str  # info, warning, error, success
    priority: str = "normal"
    read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'read': self.read,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'action_url': self.action_url,
            'metadata': self.metadata
        }

class WebSocketManager:
    """WebSocket connection and message management"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.channel_subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.message_queue = deque(maxlen=10000)
        self.notifications = deque(maxlen=5000)
        self.presence_data = defaultdict(dict)
        self.lock = asyncio.Lock()
        
        # Configuration
        self.config = {
            'max_connections': 10000,
            'heartbeat_interval': 30,
            'message_timeout': 300,
            'notification_retention': 86400,  # 24 hours
            'jwt_secret': os.getenv('JWT_SECRET', 'your-secret-key'),
            'allowed_origins': os.getenv('WS_ALLOWED_ORIGINS', '*').split(',')
        }
        
        # Event handlers
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for WebSocket management"""
        # Heartbeat monitoring
        asyncio.create_task(self._heartbeat_monitor())
        
        # Message cleanup
        asyncio.create_task(self._message_cleanup())
        
        # Notification cleanup
        asyncio.create_task(self._notification_cleanup())
    
    async def register_connection(self, websocket, path: str, headers: Dict[str, str]) -> str:
        """Register new WebSocket connection"""
        connection_id = str(uuid.uuid4())
        
        try:
            # Extract authentication token
            token = self._extract_auth_token(headers)
            user_id = None
            is_authenticated = False
            
            if token:
                try:
                    payload = jwt.decode(token, self.config['jwt_secret'], algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    is_authenticated = True
                except jwt.InvalidTokenError:
                    logger.warning(f"Invalid JWT token for connection {connection_id}")
            
            # Create connection object
            connection = WebSocketConnection(
                connection_id=connection_id,
                user_id=user_id,
                websocket=websocket,
                channels=set(),
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                ip_address=headers.get('x-forwarded-for', 'unknown'),
                user_agent=headers.get('user-agent', 'unknown'),
                is_authenticated=is_authenticated
            )
            
            async with self.lock:
                self.connections[connection_id] = connection
                if user_id:
                    self.user_connections[user_id].add(connection_id)
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                event_id=str(uuid.uuid4()),
                event_type=EventType.SYSTEM_UPDATE,
                user_id=user_id,
                channel='system',
                data={
                    'type': 'connection_established',
                    'connection_id': connection_id,
                    'timestamp': datetime.now().isoformat()
                },
                timestamp=datetime.now()
            )
            
            await self._send_to_connection(connection_id, welcome_message)
            
            logger.info(f"WebSocket connection established: {connection_id} (user: {user_id})")
            return connection_id
            
        except Exception as e:
            logger.error(f"Error registering WebSocket connection: {e}")
            raise
    
    async def unregister_connection(self, connection_id: str):
        """Unregister WebSocket connection"""
        try:
            async with self.lock:
                connection = self.connections.get(connection_id)
                if connection:
                    # Remove from user connections
                    if connection.user_id:
                        self.user_connections[connection.user_id].discard(connection_id)
                    
                    # Remove from channel subscriptions
                    for channel in connection.channels:
                        self.channel_subscribers[channel].discard(connection_id)
                    
                    # Remove connection
                    del self.connections[connection_id]
                    
                    logger.info(f"WebSocket connection closed: {connection_id}")
                    
                    # Broadcast presence update
                    if connection.user_id:
                        await self._broadcast_presence_update(connection.user_id, 'offline')
                
        except Exception as e:
            logger.error(f"Error unregistering WebSocket connection: {e}")
    
    async def subscribe_to_channel(self, connection_id: str, channel: str) -> bool:
        """Subscribe connection to channel"""
        try:
            async with self.lock:
                connection = self.connections.get(connection_id)
                if not connection:
                    return False
                
                connection.channels.add(channel)
                self.channel_subscribers[channel].add(connection_id)
                
                logger.info(f"Connection {connection_id} subscribed to channel: {channel}")
                return True
                
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {e}")
            return False
    
    async def unsubscribe_from_channel(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe connection from channel"""
        try:
            async with self.lock:
                connection = self.connections.get(connection_id)
                if not connection:
                    return False
                
                connection.channels.discard(channel)
                self.channel_subscribers[channel].discard(connection_id)
                
                logger.info(f"Connection {connection_id} unsubscribed from channel: {channel}")
                return True
                
        except Exception as e:
            logger.error(f"Error unsubscribing from channel {channel}: {e}")
            return False
    
    async def broadcast_message(self, message: WebSocketMessage) -> int:
        """Broadcast message to appropriate recipients"""
        sent_count = 0
        
        try:
            # Determine recipients
            recipients = set()
            
            if message.user_id:
                # Send to specific user
                recipients.update(self.user_connections.get(message.user_id, set()))
            
            if message.channel:
                # Send to channel subscribers
                recipients.update(self.channel_subscribers.get(message.channel, set()))
            
            # Send message
            for connection_id in recipients:
                await self._send_to_connection(connection_id, message)
                sent_count += 1
            
            # Store message
            self.message_queue.append(message)
            
            # Trigger event handlers
            await self._trigger_event_handlers(message)
            
            logger.info(f"Broadcasted message {message.event_id} to {sent_count} recipients")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return 0
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send real-time notification"""
        try:
            # Store notification
            self.notifications.append(notification)
            
            # Create WebSocket message
            message = WebSocketMessage(
                event_id=str(uuid.uuid4()),
                event_type=EventType.NOTIFICATION,
                user_id=notification.user_id,
                channel=f"user_{notification.user_id}",
                data=notification.to_dict(),
                timestamp=datetime.now(),
                priority=notification.priority
            )
            
            # Send to user
            sent_count = await self.broadcast_message(message)
            
            # Also store in database for persistence
            await self._store_notification(notification)
            
            logger.info(f"Sent notification {notification.notification_id} to {notification.user_id}")
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _send_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        try:
            async with self.lock:
                connection = self.connections.get(connection_id)
                if not connection:
                    return False
            
            # Send message
            await connection.websocket.send(json.dumps(message.to_dict()))
            
            # Update last heartbeat
            connection.last_heartbeat = datetime.now()
            
            return True
            
        except websockets.exceptions.ConnectionClosed:
            # Connection closed, remove it
            await self.unregister_connection(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to connection {connection_id}: {e}")
            return False
    
    async def _trigger_event_handlers(self, message: WebSocketMessage):
        """Trigger registered event handlers"""
        handlers = self.event_handlers.get(message.event_type, [])
        
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type].append(handler)
    
    async def update_presence(self, user_id: str, status: str, metadata: Dict[str, Any] = None):
        """Update user presence status"""
        try:
            self.presence_data[user_id] = {
                'status': status,
                'last_seen': datetime.now(),
                'metadata': metadata or {}
            }
            
            # Broadcast presence update
            await self._broadcast_presence_update(user_id, status)
            
        except Exception as e:
            logger.error(f"Error updating presence for {user_id}: {e}")
    
    async def _broadcast_presence_update(self, user_id: str, status: str):
        """Broadcast presence update"""
        message = WebSocketMessage(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PRESENCE_UPDATE,
            user_id=None,
            channel='presence',
            data={
                'user_id': user_id,
                'status': status,
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now()
        )
        
        await self.broadcast_message(message)
    
    async def _heartbeat_monitor(self):
        """Monitor connection heartbeats"""
        while True:
            try:
                current_time = datetime.now()
                timeout = timedelta(seconds=self.config['heartbeat_interval'] * 2)
                
                async with self.lock:
                    connections_to_remove = []
                    
                    for connection_id, connection in self.connections.items():
                        if current_time - connection.last_heartbeat > timeout:
                            connections_to_remove.append(connection_id)
                
                # Remove timed out connections
                for connection_id in connections_to_remove:
                    await self.unregister_connection(connection_id)
                
                await asyncio.sleep(self.config['heartbeat_interval'])
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(30)
    
    async def _message_cleanup(self):
        """Clean up old messages"""
        while True:
            try:
                current_time = datetime.now()
                timeout = timedelta(seconds=self.config['message_timeout'])
                
                # Remove old messages
                while self.message_queue and current_time - self.message_queue[0].timestamp > timeout:
                    self.message_queue.popleft()
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in message cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _notification_cleanup(self):
        """Clean up expired notifications"""
        while True:
            try:
                current_time = datetime.now()
                
                # Remove expired notifications
                self.notifications = deque(
                    [n for n in self.notifications 
                     if not n.expires_at or n.expires_at > current_time],
                    maxlen=5000
                )
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _store_notification(self, notification: Notification):
        """Store notification in database"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Insert notification into database
                session.execute(text("""
                    INSERT INTO notifications (
                        notification_id, user_id, title, message, type,
                        priority, read, created_at, expires_at, action_url, metadata
                    ) VALUES (
                        :notification_id, :user_id, :title, :message, :type,
                        :priority, :read, :created_at, :expires_at, :action_url, :metadata
                    )
                """), {
                    'notification_id': notification.notification_id,
                    'user_id': notification.user_id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.type,
                    'priority': notification.priority,
                    'read': notification.read,
                    'created_at': notification.created_at,
                    'expires_at': notification.expires_at,
                    'action_url': notification.action_url,
                    'metadata': json.dumps(notification.metadata)
                })
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error storing notification in database: {e}")
    
    def _extract_auth_token(self, headers: Dict[str, str]) -> Optional[str]:
        """Extract JWT token from headers"""
        auth_header = headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Also check query parameter
        return None
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        try:
            async with self.lock:
                total_connections = len(self.connections)
                authenticated_connections = len([
                    c for c in self.connections.values() if c.is_authenticated
                ])
                
                channel_stats = {
                    channel: len(subscribers)
                    for channel, subscribers in self.channel_subscribers.items()
                }
                
                user_stats = {
                    user_id: len(connections)
                    for user_id, connections in self.user_connections.items()
                }
            
            return {
                'total_connections': total_connections,
                'authenticated_connections': authenticated_connections,
                'anonymous_connections': total_connections - authenticated_connections,
                'channel_stats': channel_stats,
                'user_stats': user_stats,
                'message_queue_size': len(self.message_queue),
                'notification_count': len(self.notifications),
                'presence_data_size': len(self.presence_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {}

class RealTimeFeatures:
    """Real-time features integration"""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for real-time features"""
        # Analytics updates
        self.ws_manager.register_event_handler(
            EventType.ANALYTICS_UPDATE,
            self._handle_analytics_update
        )
        
        # Security alerts
        self.ws_manager.register_event_handler(
            EventType.SECURITY_ALERT,
            self._handle_security_alert
        )
        
        # User activity
        self.ws_manager.register_event_handler(
            EventType.USER_ACTIVITY,
            self._handle_user_activity
        )
    
    async def _handle_analytics_update(self, message: WebSocketMessage):
        """Handle analytics update events"""
        try:
            with distributed_tracer.trace_span("handle_analytics_update", "real-time-features"):
                # Process analytics data
                analytics_data = message.data
                
                # Could trigger additional processing here
                logger.info(f"Processed analytics update: {analytics_data}")
                
        except Exception as e:
            logger.error(f"Error handling analytics update: {e}")
    
    async def _handle_security_alert(self, message: WebSocketMessage):
        """Handle security alert events"""
        try:
            with distributed_tracer.trace_span("handle_security_alert", "real-time-features"):
                # Process security alert
                alert_data = message.data
                
                # Send high-priority notifications to admins
                if alert_data.get('severity') == 'critical':
                    await self._send_admin_alert(alert_data)
                
                logger.info(f"Processed security alert: {alert_data}")
                
        except Exception as e:
            logger.error(f"Error handling security alert: {e}")
    
    async def _handle_user_activity(self, message: WebSocketMessage):
        """Handle user activity events"""
        try:
            with distributed_tracer.trace_span("handle_user_activity", "real-time-features"):
                # Process user activity
                activity_data = message.data
                
                # Update user presence
                user_id = activity_data.get('user_id')
                if user_id:
                    await self.ws_manager.update_presence(
                        user_id, 
                        activity_data.get('status', 'online'),
                        activity_data.get('metadata', {})
                    )
                
                logger.info(f"Processed user activity: {activity_data}")
                
        except Exception as e:
            logger.error(f"Error handling user activity: {e}")
    
    async def _send_admin_alert(self, alert_data: Dict[str, Any]):
        """Send alert to admin users"""
        try:
            # Get admin users from database
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                result = session.execute(text("""
                    SELECT user_id FROM users WHERE role = 'admin' AND status = 'active'
                """))
                
                admin_users = [row[0] for row in result]
            
            # Send notifications to all admins
            for admin_id in admin_users:
                notification = Notification(
                    notification_id=str(uuid.uuid4()),
                    user_id=admin_id,
                    title="Security Alert",
                    message=alert_data.get('message', 'Security event detected'),
                    type="error",
                    priority="high",
                    metadata=alert_data
                )
                
                await self.ws_manager.send_notification(notification)
                
        except Exception as e:
            logger.error(f"Error sending admin alert: {e}")

# Global instances
websocket_manager = WebSocketManager()
real_time_features = RealTimeFeatures(websocket_manager)

async def handle_websocket_connection(websocket, path):
    """Main WebSocket connection handler"""
    # Extract headers and register connection
    headers = dict(websocket.request_headers)
    connection_id = await websocket_manager.register_connection(websocket, path, headers)
    
    try:
        # Handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Handle different message types
                if data.get('type') == 'subscribe':
                    await websocket_manager.subscribe_to_channel(
                        connection_id, 
                        data.get('channel')
                    )
                elif data.get('type') == 'unsubscribe':
                    await websocket_manager.unsubscribe_from_channel(
                        connection_id, 
                        data.get('channel')
                    )
                elif data.get('type') == 'heartbeat':
                    # Update heartbeat
                    async with websocket_manager.lock:
                        connection = websocket_manager.connections.get(connection_id)
                        if connection:
                            connection.last_heartbeat = datetime.now()
                elif data.get('type') == 'presence':
                    # Update presence
                    user_id = data.get('user_id')
                    status = data.get('status', 'online')
                    metadata = data.get('metadata', {})
                    
                    if user_id:
                        await websocket_manager.update_presence(user_id, status, metadata)
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from connection {connection_id}")
            except Exception as e:
                logger.error(f"Error handling message from connection {connection_id}: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await websocket_manager.unregister_connection(connection_id)

async def send_notification(user_id: str, title: str, message: str, 
                          notification_type: str = "info", priority: str = "normal",
                          action_url: str = None, metadata: Dict[str, Any] = None) -> bool:
    """Send real-time notification"""
    notification = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        priority=priority,
        action_url=action_url,
        metadata=metadata or {}
    )
    
    return await websocket_manager.send_notification(notification)

async def broadcast_system_update(channel: str, data: Dict[str, Any], priority: str = "normal") -> int:
    """Broadcast system update"""
    message = WebSocketMessage(
        event_id=str(uuid.uuid4()),
        event_type=EventType.SYSTEM_UPDATE,
        user_id=None,
        channel=channel,
        data=data,
        timestamp=datetime.now(),
        priority=priority
    )
    
    return await websocket_manager.broadcast_message(message)

def get_websocket_stats() -> Dict[str, Any]:
    """Get WebSocket statistics"""
    return websocket_manager.get_connection_stats()
