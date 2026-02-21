#!/usr/bin/env python3
"""
Simple LLM Security Dashboard
Real-time monitoring dashboard for LLM security events and metrics
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SimpleLLMSecurityDashboard:
    """Simple LLM Security Dashboard"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "injection_attempts": 0,
            "content_violations": 0,
            "rate_limit_violations": 0,
            "security_score": 100,
            "last_update": datetime.now().isoformat()
        }
        self.recent_events = []
    
    def update_metrics(self, event_type: str, blocked: bool = False):
        """Update security metrics"""
        self.metrics["total_requests"] += 1
        self.metrics["last_update"] = datetime.now().isoformat()
        
        if blocked:
            self.metrics["blocked_requests"] += 1
        
        if event_type == "injection":
            self.metrics["injection_attempts"] += 1
        elif event_type == "content":
            self.metrics["content_violations"] += 1
        elif event_type == "rate_limit":
            self.metrics["rate_limit_violations"] += 1
        
        # Calculate security score
        total_requests = self.metrics["total_requests"]
        blocked_requests = self.metrics["blocked_requests"]
        
        if total_requests > 0:
            block_rate = (blocked_requests / total_requests) * 100
            self.metrics["security_score"] = max(0, 100 - block_rate)
    
    def add_event(self, event: Dict[str, Any]):
        """Add security event"""
        self.recent_events.insert(0, event)
        if len(self.recent_events) > 20:
            self.recent_events = self.recent_events[:20]
    
    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard"""
        block_rate = 0
        if self.metrics["total_requests"] > 0:
            block_rate = (self.metrics["blocked_requests"] / self.metrics["total_requests"]) * 100
        
        security_status = "good"
        if block_rate > 20:
            security_status = "warning"
        if block_rate > 50:
            security_status = "critical"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Security Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            font-size: 16px;
            color: #666;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .metric-value {{
            font-size: 48px;
            font-weight: bold;
            margin: 15px 0;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .metric-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }}
        
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        
        .events-section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .events-header {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .event-item {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
            transition: all 0.2s ease;
        }}
        
        .event-item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        
        .event-time {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 8px;
        }}
        
        .event-details {{
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .refresh-info {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            font-size: 14px;
            color: #666;
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ LLM Security Dashboard</h1>
            <p>Real-time monitoring and threat detection for Stellar Logic AI</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value status-{security_status}">
                    {self.metrics["security_score"]}/100
                </div>
                <div class="metric-label">Security Score</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-{security_status}">
                    {block_rate:.1f}%
                </div>
                <div class="metric-label">Block Rate</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {self.metrics["total_requests"]}
                </div>
                <div class="metric-label">Total Requests</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value status-{security_status}">
                    {self.metrics["blocked_requests"]}
                </div>
                <div class="metric-label">Blocked Requests</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {self.metrics["injection_attempts"]}
                </div>
                <div class="metric-label">Injection Attempts</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {self.metrics["content_violations"]}
                </div>
                <div class="metric-label">Content Violations</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">
                    {self.metrics["rate_limit_violations"]}
                </div>
                <div class="metric-label">Rate Limit Violations</div>
            </div>
        </div>
        
        <div class="events-section">
            <div class="events-header">📊 Recent Security Events</div>
            {self._generate_events_html()}
        </div>
        
        <div class="refresh-info">
            <div class="pulse">🔄</div> Auto-refresh every 30 seconds | 
            Last updated: {self.metrics["last_update"]}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function(){{
            location.reload();
        }}, 30000);
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('LLM Security Dashboard loaded successfully');
            
            // Add click handlers to metric cards
            const cards = document.querySelectorAll('.metric-card');
            cards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(1.05)';
                    setTimeout(() => {{
                        this.style.transform = 'scale(1)';
                    }}, 200);
                }});
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_events_html(self) -> str:
        """Generate HTML for recent events"""
        if not self.recent_events:
            return "<div style='text-align: center; color: #6c757d; padding: 20px;'>No recent security events</div>"
        
        events_html = ""
        for event in self.recent_events[:10]:  # Show last 10 events
            events_html += f"""
                <div class="event-item">
                    <div class="event-time">{event.get('time', 'Unknown')}</div>
                    <div class="event-details">
                        <strong>{event.get('type', 'Unknown')}</strong>: {event.get('description', 'No description')}
                    </div>
                </div>
            """
        
        return events_html
    
    def save_dashboard(self, filename: str = "llm_security_dashboard.html") -> str:
        """Save dashboard to HTML file"""
        html_content = self.generate_dashboard_html()
        
        dashboard_path = os.path.join(os.getcwd(), filename)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return dashboard_path

def main():
    """Main function to generate the dashboard"""
    dashboard = SimpleLLMSecurityDashboard()
    
    # Add some sample events for demonstration
    dashboard.add_event({
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "type": "Injection Attempt",
        "description": "Prompt injection detected and blocked",
        "severity": "High"
    })
    
    dashboard.add_event({
        "time": (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
        "type": "Rate Limit",
        "description": "User exceeded rate limit and was temporarily blocked",
        "severity": "Medium"
    })
    
    dashboard.update_metrics("injection", blocked=True)
    dashboard.update_metrics("rate_limit", blocked=True)
    dashboard.update_metrics("content", blocked=False)
    
    # Generate dashboard
    dashboard_path = dashboard.save_dashboard()
    print(f"✅ LLM Security Dashboard generated: {dashboard_path}")
    print("🌐 Open the file in your browser to view the dashboard")
    print("🛡️ Dashboard features real-time security monitoring and metrics")

if __name__ == "__main__":
    main()
