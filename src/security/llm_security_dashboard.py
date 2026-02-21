#!/usr/bin/env python3
"""
LLM Security Dashboard
Real-time monitoring dashboard for LLM security events and metrics
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.security.llm_security_pipeline import llm_security_pipeline, LLMPipelineRequest, LLMSecurityEvent

@dataclass
class DashboardMetrics:
    """Dashboard metrics structure"""
    timestamp: datetime
    total_requests: int
    blocked_requests: int
    block_rate: float
    security_score: int
    top_threats: Dict[str, int]
    user_activity: Dict[str, int]
    recent_events: List[Dict[str, Any]]
    recommendations: List[str]

class LLMSecurityDashboard:
    """LLM Security Dashboard for real-time monitoring"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "block_rate_warning": 20.0,  # 20% block rate warning
            "block_rate_critical": 50.0,  # 50% block rate critical
            "security_score_warning": 70,     # Security score below 70 warning
            "security_score_critical": 50,    # Security score below 50 critical
            "hourly_requests_warning": 1000, # 1000 requests per hour warning
            "hourly_requests_critical": 2000, # 2000 requests per hour critical
        }
    
    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard"""
        metrics = self._get_current_metrics()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Security Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .events-section {{
            padding: 20px;
            background: #f8f9fa;
        }}
        .events-header {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #495057;
        }}
        .event-item {{
            background: white;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 4px 4px 0;
        }}
        .event-time {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        .event-details {{
            font-size: 14px;
            line-height: 1.4;
        }}
        .recommendations {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px;
        }}
        .recommendations h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .refresh-info {{
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #6c757d;
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            🛡️ LLM Security Dashboard
            <div style="font-size: 14px; font-weight: normal; margin-top: 5px;">
                Last Updated: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value status-{'good' if metrics['security_score'] >= 80 else 'warning' if metrics['security_score'] >= 60 else 'critical'}">
                    {metrics['security_score']}/100
                </div>
                <div class="metric-label">Security Score</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-{'good' if metrics['block_rate'] <= 20 else 'warning' if metrics['block_rate'] <= 50 else 'critical'}">
                    {metrics['block_rate']:.1f}%
                </div>
                <div class="metric-label">Block Rate</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {metrics['total_requests']}
                </div>
                <div class="metric-label">Total Requests</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {metrics['blocked_requests']}
                </div>
                <div class="metric-label">Blocked Requests</div>
            </div>
        </div>
        
        <div class="events-section">
            <div class="events-header">📊 Recent Security Events</div>
            {self._generate_events_html(metrics['recent_events'])}
        </div>
        
        <div class="recommendations">
            <h3>🎯 Security Recommendations</h3>
            <ul>
                {self._generate_recommendations_html(metrics['recommendations'])}
            </ul>
        </div>
        
        <div class="refresh-info">
            🔄 Auto-refresh every 30 seconds | Last updated: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function(){{
            location.reload();
        }}, 30000);
        
        // Add real-time updates (WebSocket would be implemented here)
        console.log('LLM Security Dashboard loaded');
    </script>
</body>
</html>
        """
        
        return html
    
    def _get_current_metrics(self) -> DashboardMetrics:
        """Get current dashboard metrics"""
        # Get security metrics from pipeline
        security_metrics = llm_security_pipeline.get_security_metrics()
        
        # Get recent events
        recent_events = llm_security_pipeline.review_security_events(1)
        
        # Analyze top threats
        top_threats = {}
        for event in llm_security_manager.security_events[-100:]:  # Last 100 events
            threat_type = event.threat_type
            top_threats[threat_type] = top_threats.get(threat_type, 0) + 1
        
        # Get user activity
        user_activity = {}
        for event in llm_security_manager.security_events[-100:]:
            if event.user_id:
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
        
        return DashboardMetrics(
            timestamp=datetime.now(),
            total_requests=security_metrics['total_requests'],
            blocked_requests=security_metrics['blocked_requests'],
            block_rate=security_metrics['block_rate'],
            security_score=security_metrics['security_score'],
            top_threats=top_threats,
            user_activity=user_activity,
            recent_events=recent_events['threat_analysis'],
            recommendations=recent_events['recommendations']
        )
    
    def _generate_events_html(self, events: List[Dict[str, Any]]) -> str:
        """Generate HTML for recent events"""
        if not events:
            return "<div style='text-align: center; color: #6c757d; padding: 20px;'>No recent security events</div>"
        
        events_html = ""
        for event in events[:10]:  # Show last 10 events
            events_html += f"""
                <div class="event-item">
                    <div class="event-time">{event.get('timestamp', 'Unknown')}</div>
                    <div class="event-details">
                        <strong>{event.get('threat_type', 'Unknown')}</strong>: {event.get('description', 'No description')}
                    </div>
                </div>
            """
        
        return events_html
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations"""
        if not recommendations:
            return "<li>No security recommendations at this time</li>"
        
        recommendations_html = ""
        for rec in recommendations:
            recommendations_html += f"<li>{rec}</li>"
        
        return recommendations_html
    
    def save_dashboard(self, filename: str = "llm_security_dashboard.html") -> str:
        """Save dashboard to HTML file"""
        html_content = self.generate_dashboard_html()
        
        dashboard_path = os.path.join(os.getcwd(), filename)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return dashboard_path
    
    def start_dashboard_server(self, port: int = 8080):
        """Start dashboard server"""
        import http.server
        import socketserver
        import webbrowser
        
        # Save dashboard
        dashboard_path = self.save_dashboard()
        
        # Change to dashboard directory
        os.chdir(os.path.dirname(dashboard_path))
        
        # Start server
        handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), handler)
        
        print(f"🚀 LLM Security Dashboard starting on http://localhost:{port}")
        print(f"📊 Dashboard file: {dashboard_path}")
        print("🔄 Press Ctrl+C to stop the server")
        
        # Open browser
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 Dashboard server stopped")
            httpd.server_close()

def main():
    """Main function to run the dashboard"""
    dashboard = LLMSecurityDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start server mode
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        dashboard.start_dashboard_server(port)
    else:
        # Generate static dashboard
        dashboard_path = dashboard.save_dashboard()
        print(f"✅ LLM Security Dashboard generated: {dashboard_path}")
        print("🌐 Open the file in your browser to view the dashboard")
        print("🚀 Run 'python llm_security_dashboard.py server [port]' to start live server")

if __name__ == "__main__":
    main()
