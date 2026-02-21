#!/usr/bin/env python3
"""
Real-time Data Collection System
WebSocket implementation for live dashboard updates and metrics streaming
"""

import os
import sys
import json
import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from flask import Flask, request, jsonify
try:
    from flask_socketio import SocketIO, emit, join, leave
    import eventlet
except ImportError:
    # Fallback for environments without flask-socketio
    SocketIO = None
    emit = None
    join = None
    leave = None
    eventlet = None

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class RealtimeMetric:
    """Real-time metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str
    source: str  # ai_performance, system_health, financial_analytics, user_engagement
    metadata: Dict[str, Any] = None

@dataclass
class WebSocketConnection:
    """WebSocket connection data structure"""
    connection_id: str
    client_id: str
    connected_at: datetime
    last_activity: datetime
    subscriptions: List[str]
    user_agent: str
    ip_address: str

class RealtimeDataCollector:
    """Real-time Data Collection System"""
    
    def __init__(self):
        self.logger = logging.getLogger("realtime_data_collector")
        self.connections = {}  # connection_id -> WebSocketConnection
        self.metrics_buffer = deque(maxlen=1000)  # Last 1000 metrics
        self.subscribers = defaultdict(set)  # category -> set of connection_ids
        self.collection_interval = 5  # seconds
        self.max_connections = 1000
        self.is_running = False
        self.collection_thread = None
        self.socketio = None
        self.websocket_available = False
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'realtime-data-secret-key'
        
        # Initialize SocketIO if available
        if SocketIO is not None:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
            self.websocket_available = True
            self.setup_socketio_handlers()
        else:
            self.logger.warning("Flask-SocketIO not available, WebSocket features disabled")
            self.setup_fallback_handlers()
        
        # Setup API routes
        self.setup_api_routes()
    
    def setup_api_routes(self):
        """Setup API routes for real-time data"""
        if self.websocket_available:
            # Add routes to Flask app
            self.app.add_url_rule('/api/v1/realtime/status', 'realtime_status', self.realtime_status)
            self.app.add_url_rule('/api/v1/realtime/metrics/<category>', 'realtime_metrics', self.realtime_metrics)
            self.app.add_url_rule('/api/v1/realtime/connections', 'realtime_connections', self.realtime_connections)
            self.app.add_url_rule('/api/v1/realtime/start', 'realtime_start', self.start_collection)
            self.app.add_url_rule('/api/v1/realtime/stop', 'realtime_stop', self.stop_collection)
        else:
            # Fallback routes without WebSocket
            self.app.add_url_rule('/api/v1/realtime/status', 'realtime_status', self.fallback_realtime_status)
            self.app.add_url_rule('/api/v1/realtime/metrics/<category>', 'realtime_metrics', self.fallback_realtime_metrics)
            self.app.add_url_rule('/api/v1/realtime/connections', 'realtime_connections', self.fallback_realtime_connections)
            self.app.add_url_rule('/api/v1/realtime/start', 'realtime_start', self.fallback_start_collection)
            self.app.add_url_rule('/api/v1/realtime/stop', 'realtime_stop', self.fallback_stop_collection)
    
    def setup_fallback_handlers(self):
        """Setup fallback handlers without WebSocket"""
        @self.app.route('/api/v1/realtime/status')
        def fallback_realtime_status():
            return jsonify({
                'status': 'limited',
                'message': 'WebSocket not available, using fallback mode',
                'websocket_available': False,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/v1/realtime/metrics/<category>')
        def fallback_realtime_metrics(category):
            # Return mock data for fallback mode
            mock_data = {
                'ai_performance': [
                    {'metric_name': 'response_time', 'value': 1250.5, 'timestamp': datetime.now().isoformat()},
                    {'metric_name': 'accuracy', 'value': 0.92, 'timestamp': datetime.now().isoformat()}
                ],
                'system_health': [
                    {'metric_name': 'cpu_usage', 'value': 45.2, 'timestamp': datetime.now().isoformat()},
                    {'metric_name': 'memory_usage', 'value': 78.3, 'timestamp': datetime.now().isoformat()}
                ],
                'financial_analytics': [
                    {'metric_name': 'mrr', 'value': 15000.0, 'timestamp': datetime.now().isoformat()},
                    {'metric_name': 'active_users', 'value': 1200, 'timestamp': datetime.now().isoformat()}
                ],
                'user_engagement': [
                    {'metric_name': 'active_users', 'value': 850, 'timestamp': datetime.now().isoformat()},
                    {'metric_name': 'bounce_rate', 'value': 0.25, 'timestamp': datetime.now().isoformat()}
                ]
            }
            
            return jsonify({
                'category': category,
                'metrics': mock_data.get(category, []),
                'timestamp': datetime.now().isoformat(),
                'websocket_available': False
            })
        
        @self.app.route('/api/v1/realtime/connections')
        def fallback_realtime_connections():
            return jsonify({
                'status': 'limited',
                'connections': [],
                'websocket_available': False,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/v1/realtime/start')
        def fallback_start_collection():
            return jsonify({
                'status': 'limited',
                'message': 'WebSocket not available, cannot start collection',
                'websocket_available': False,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/v1/realtime/stop')
        def fallback_stop_collection():
            return jsonify({
                'status': 'limited',
                'message': 'WebSocket not available, cannot stop collection',
                'websocket_available': False,
                'timestamp': datetime.now().isoformat()
            })
    
    def realtime_status(self):
        """Real-time data collection status"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.realtime_data_collection import realtime_data_collector
            
            stats = realtime_data_collector.get_connection_stats()
            return jsonify({
                'status': 'healthy' if realtime_data_collector.is_running else 'stopped',
                'timestamp': datetime.now().isoformat(),
                'connection_stats': stats,
                'websocket_available': realtime_data_collector.websocket_available
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e),
                'websocket_available': False
            })
    
    def realtime_metrics(self, category):
        """Get real-time metrics for specific category"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.realtime_data_collection import realtime_data_collector
            
            metrics = realtime_data_collector.get_recent_metrics(category=category, limit=50)
            return jsonify({
                'category': category,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'category': category,
                'metrics': [],
                'timestamp': datetime.now().isoformat()
            })
    
    def realtime_connections(self):
        """Get active WebSocket connections"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.realtime_data_collection import realtime_data_collector
            
            stats = realtime_data_collector.get_connection_stats()
            return jsonify({
                'status': 'active' if realtime_data_collector.is_running else 'inactive',
                'connections': [
                    {
                        'connection_id': conn.connection_id,
                        'client_id': conn.client_id,
                        'connected_at': conn.connected_at.isoformat(),
                        'last_activity': conn.last_activity.isoformat(),
                        'subscriptions': conn.subscriptions,
                        'user_agent': conn.user_agent,
                        'ip_address': conn.ip_address
                    } for conn in realtime_data_collector.connections.values()
                ],
                'timestamp': datetime.now().isoformat(),
                'websocket_available': realtime_data_collector.websocket_available
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'connections': [],
                'timestamp': datetime.now().isoformat(),
                'websocket_available': False
            })
    
    def start_collection(self):
        """Start real-time data collection"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.realtime_data_collection import realtime_data_collector
            
            realtime_data_collector.start_collection()
            return jsonify({
                'status': 'started',
                'message': 'Real-time data collection started',
                'timestamp': datetime.now().isoformat(),
                'websocket_available': realtime_data_collector.websocket_available
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e),
                'websocket_available': False
            })
    
    def stop_collection(self):
        """Stop real-time data collection"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            from dashboard.realtime_data_collection import realtime_data_collector
            
            realtime_data_collector.stop_collection()
            return jsonify({
                'status': 'stopped',
                'message': 'Real-time data collection stopped',
                'timestamp': datetime.now().isoformat(),
                'websocket_available': realtime_data_collector.websocket_available
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e),
                'websocket_available': False
            })
    
    def setup_socketio_handlers(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            connection_id = request.sid
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            connection = WebSocketConnection(
                connection_id=connection_id,
                client_id=f"client_{connection_id}",
                connected_at=datetime.now(),
                last_activity=datetime.now(),
                subscriptions=[],
                user_agent=user_agent,
                ip_address=client_ip
            )
            
            self.connections[connection_id] = connection
            self.logger.info(f"Client connected: {connection_id} from {client_ip}")
            
            # Send initial data
            emit('connected', {
                'connection_id': connection_id,
                'server_time': datetime.now().isoformat(),
                'available_categories': ['ai_performance', 'system_health', 'financial_analytics', 'user_engagement']
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            connection_id = request.sid
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                self.logger.info(f"Client disconnected: {connection_id}")
                
                # Remove from all subscriptions
                for category in connection.subscriptions:
                    self.subscribers[category].discard(connection_id)
                
                del self.connections[connection_id]
        
        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            connection_id = request.sid
            category = data.get('category')
            
            if connection_id in self.connections and category:
                self.connections[connection_id].subscriptions.append(category)
                self.subscribers[category].add(connection_id)
                self.connections[connection_id].last_activity = datetime.now()
                
                # Join room for category
                join(self.socketio, category)
                
                self.logger.info(f"Client {connection_id} subscribed to {category}")
                
                # Send current metrics for this category
                recent_metrics = [
                    m for m in self.metrics_buffer 
                    if m.category == category and m.timestamp > datetime.now() - timedelta(minutes=5)
                ]
                
                emit('metrics_update', {
                    'category': category,
                    'metrics': [asdict(m) for m in recent_metrics[-10:]],
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            connection_id = request.sid
            category = data.get('category')
            
            if connection_id in self.connections and category:
                if category in self.connections[connection_id].subscriptions:
                    self.connections[connection_id].subscriptions.remove(category)
                
                self.subscribers[category].discard(connection_id)
                self.connections[connection_id].last_activity = datetime.now()
                
                # Leave room for category
                leave(self.socketio, category)
                
                self.logger.info(f"Client {connection_id} unsubscribed from {category}")
        
        @self.socketio.on('ping')
        def handle_ping():
            connection_id = request.sid
            if connection_id in self.connections:
                self.connections[connection_id].last_activity = datetime.now()
                emit('pong', {'timestamp': datetime.now().isoformat()})
    
    def start_collection(self):
        """Start real-time data collection"""
        if self.is_running:
            self.logger.warning("Data collection is already running")
            return
        
        self.is_running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        self.logger.info("Real-time data collection started")
    
    def stop_collection(self):
        """Stop real-time data collection"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=10)
        self.logger.info("Real-time data collection stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.is_running:
            try:
                # Collect metrics from all sources
                self._collect_ai_performance_metrics()
                self._collect_system_health_metrics()
                self._collect_financial_metrics()
                self._collect_user_engagement_metrics()
                
                # Broadcast to subscribers
                self._broadcast_metrics()
                
                # Clean up old connections
                self._cleanup_connections()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                time.sleep(5)
    
    def _collect_ai_performance_metrics(self):
        """Collect AI performance metrics"""
        try:
            # Import and collect AI performance metrics
            from dashboard.ai_performance import ai_performance_monitor
            
            # Get current metrics
            metrics = ai_performance_monitor.get_performance_summary(hours=1)
            
            # Add to buffer
            if metrics.get('performance_stats'):
                metric = RealtimeMetric(
                    timestamp=datetime.now(),
                    metric_name="ai_performance_summary",
                    value=metrics['performance_stats'].get('avg_response_time', 0),
                    unit="ms",
                    category="ai_performance",
                    source="ai_performance_monitor",
                    metadata=metrics['performance_stats']
                )
                self.metrics_buffer.append(metric)
                
        except Exception as e:
            self.logger.error(f"Error collecting AI performance metrics: {e}")
    
    def _collect_system_health_metrics(self):
        """Collect system health metrics"""
        try:
            from dashboard.system_health import system_health_monitor
            
            # Collect current metrics
            system_health_monitor.collect_system_metrics()
            system_health_monitor.check_service_health()
            
            metrics = system_health_monitor.get_health_summary(hours=1)
            
            if metrics.get('performance_stats'):
                metric = RealtimeMetric(
                    timestamp=datetime.now(),
                    metric_name="system_health_summary",
                    value=metrics['performance_stats'].get('cpu_usage', 0),
                    unit="%",
                    category="system_health",
                    source="system_health_monitor",
                    metadata=metrics['performance_stats']
                )
                self.metrics_buffer.append(metric)
                
        except Exception as e:
            self.logger.error(f"Error collecting system health metrics: {e}")
    
    def _collect_financial_metrics(self):
        """Collect financial metrics"""
        try:
            from dashboard.financial_analytics import financial_analytics_monitor
            
            metrics = financial_analytics_monitor.get_financial_summary(hours=1)
            
            if metrics.get('revenue_metrics'):
                metric = RealtimeMetric(
                    timestamp=datetime.now(),
                    metric_name="financial_summary",
                    value=metrics['revenue_metrics'].get('mrr', 0),
                    unit="$",
                    category="financial_analytics",
                    source="financial_analytics_monitor",
                    metadata=metrics['revenue_metrics']
                )
                self.metrics_buffer.append(metric)
                
        except Exception as e:
            self.logger.error(f"Error collecting financial metrics: {e}")
    
    def _collect_user_engagement_metrics(self):
        """Collect user engagement metrics"""
        try:
            from dashboard.user_engagement import user_engagement_monitor
            
            metrics = user_engagement_monitor.get_engagement_summary(hours=1)
            
            if metrics.get('engagement_stats'):
                metric = RealtimeMetric(
                    timestamp=datetime.now(),
                    metric_name="user_engagement_summary",
                    value=metrics['engagement_stats'].get('active_users', 0),
                    unit="users",
                    category="user_engagement",
                    source="user_engagement_monitor",
                    metadata=metrics['engagement_stats']
                )
                self.metrics_buffer.append(metric)
                
        except Exception as e:
            self.logger.error(f"Error collecting user engagement metrics: {e}")
    
    def _broadcast_metrics(self):
        """Broadcast metrics to subscribers"""
        current_time = datetime.now()
        
        for category in ['ai_performance', 'system_health', 'financial_analytics', 'user_engagement']:
            if category in self.subscribers and self.subscribers[category]:
                # Get recent metrics for this category
                recent_metrics = [
                    m for m in self.metrics_buffer 
                    if m.category == category and m.timestamp > current_time - timedelta(seconds=30)
                ]
                
                if recent_metrics:
                    self.socketio.emit('metrics_update', {
                        'category': category,
                        'metrics': [asdict(m) for m in recent_metrics[-5:]],
                        'timestamp': current_time.isoformat()
                    }, room=category)
    
    def _cleanup_connections(self):
        """Clean up inactive connections"""
        current_time = datetime.now()
        inactive_connections = []
        
        for connection_id, connection in self.connections.items():
            if (current_time - connection.last_activity).seconds > 300:  # 5 minutes
                inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            if connection_id in self.connections:
                del self.connections[connection_id]
                # Remove from all subscriptions
                for category in self.subscribers:
                    self.subscribers[category].discard(connection_id)
                
                self.logger.info(f"Cleaned up inactive connection: {connection_id}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'total_connections': len(self.connections),
            'active_connections': len([c for c in self.connections.values() 
                                     if (datetime.now() - c.last_activity).seconds < 60]),
            'subscribers_by_category': {
                category: len(subscribers) 
                for category, subscribers in self.subscribers.items()
            },
            'metrics_buffer_size': len(self.metrics_buffer),
            'is_running': self.is_running,
            'collection_interval': self.collection_interval,
            'max_connections': self.max_connections
        }
    
    def get_recent_metrics(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        if category:
            filtered_metrics = [
                asdict(m) for m in self.metrics_buffer 
                if m.category == category
            ]
        else:
            filtered_metrics = [asdict(m) for m in self.metrics_buffer]
        
        return filtered_metrics[-limit:]
    
    def create_flask_app(self):
        """Create Flask app with SocketIO"""
        return self.app, self.socketio

# Global real-time data collector instance
realtime_data_collector = RealtimeDataCollector()
