#!/usr/bin/env python3
"""
Stellar Logic AI - Security Monitoring and Alerting System
Real-time security event monitoring with intelligent alerting
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import re

class StellarSecurityMonitor:
    """Advanced security monitoring and alerting system for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.log_file = os.path.join(self.production_path, "logs/stellar_security.log")
        self.monitoring_config = os.path.join(self.production_path, "monitoring/security_monitoring.json")
        
        # Monitoring data structures
        self.security_events = deque(maxlen=10000)
        self.alert_thresholds = {
            "failed_logins": 10,
            "suspicious_patterns": 5,
            "rate_limit_hits": 100,
            "csrf_failures": 10,
            "sql_injection_attempts": 3,
            "xss_attempts": 3,
            "unauthorized_access": 5
        }
        
        # Event counters
        self.event_counters = defaultdict(int)
        self.ip_addresses = defaultdict(list)
        self.user_agents = defaultdict(list)
        self.alert_history = deque(maxlen=1000)
        
        # Monitoring status
        self.monitoring_active = False
        self.monitoring_thread = None
        self.last_alert_time = {}
        
        # Load configuration
        self.load_configuration()
    
    def load_configuration(self):
        """Load monitoring configuration"""
        try:
            if os.path.exists(self.monitoring_config):
                with open(self.monitoring_config, 'r') as f:
                    config = json.load(f)
                    self.alert_thresholds.update(config.get("security_monitoring", {}).get("alert_thresholds", {}))
                    print("✅ Monitoring configuration loaded")
            else:
                print("⚠️ Monitoring config not found, using defaults")
        except Exception as e:
            print(f"❌ Error loading monitoring config: {e}")
    
    def parse_security_log(self) -> List[Dict[str, Any]]:
        """Parse security log file for events"""
        events = []
        
        if not os.path.exists(self.log_file):
            return events
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines[-1000:]:  # Last 1000 lines
                try:
                    # Try to parse JSON log entries
                    if line.strip().startswith('{') and line.strip().endswith('}'):
                        event = json.loads(line.strip())
                        events.append(event)
                    else:
                        # Parse text log entries
                        if "Stellar Logic AI Security Event" in line:
                            event = self.parse_text_log_entry(line)
                            if event:
                                events.append(event)
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ Error parsing security log: {e}")
        
        return events
    
    def parse_text_log_entry(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse text-based log entry"""
        try:
            # Extract timestamp
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().isoformat()
            
            # Extract event type
            if "suspicious" in line.lower():
                event_type = "suspicious_activity"
            elif "failed" in line.lower() or "error" in line.lower():
                event_type = "security_error"
            elif "login" in line.lower():
                event_type = "authentication"
            elif "csrf" in line.lower():
                event_type = "csrf_violation"
            else:
                event_type = "security_event"
            
            return {
                "timestamp": timestamp,
                "event_type": event_type,
                "raw_message": line.strip(),
                "source": "security_log"
            }
        except:
            return None
    
    def analyze_security_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze security events for threats and anomalies"""
        alerts = []
        current_time = datetime.now()
        
        # Reset counters for new analysis
        recent_events = [e for e in events if self.is_recent_event(e, hours=1)]
        
        # Analyze different threat patterns
        alerts.extend(self.analyze_failed_logins(recent_events, current_time))
        alerts.extend(self.analyze_suspicious_patterns(recent_events, current_time))
        alerts.extend(self.analyze_rate_limiting(recent_events, current_time))
        alerts.extend(self.analyze_ip_anomalies(recent_events, current_time))
        alerts.extend(self.analyze_sql_injection(recent_events, current_time))
        alerts.extend(self.analyze_xss_attempts(recent_events, current_time))
        
        return alerts
    
    def is_recent_event(self, event: Dict[str, Any], hours: int = 1) -> bool:
        """Check if event is within specified time window"""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", "").replace("Z", "+00:00"))
            return datetime.now() - event_time <= timedelta(hours=hours)
        except:
            return False
    
    def analyze_failed_logins(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze failed login attempts"""
        alerts = []
        failed_logins = [e for e in events if "login" in str(e).lower() and ("fail" in str(e).lower() or "error" in str(e).lower())]
        
        if len(failed_logins) >= self.alert_thresholds["failed_logins"]:
            alert = {
                "timestamp": current_time.isoformat(),
                "alert_type": "brute_force_attack",
                "severity": "HIGH",
                "message": f"Multiple failed login attempts detected: {len(failed_logins)} attempts",
                "count": len(failed_logins),
                "threshold": self.alert_thresholds["failed_logins"],
                "events": failed_logins[-5:]  # Last 5 events
            }
            alerts.append(alert)
        
        return alerts
    
    def analyze_suspicious_patterns(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze suspicious activity patterns"""
        alerts = []
        suspicious_events = [e for e in events if "suspicious" in str(e).lower() or "attack" in str(e).lower()]
        
        if len(suspicious_events) >= self.alert_thresholds["suspicious_patterns"]:
            alert = {
                "timestamp": current_time.isoformat(),
                "alert_type": "suspicious_activity",
                "severity": "MEDIUM",
                "message": f"Suspicious activity patterns detected: {len(suspicious_events)} events",
                "count": len(suspicious_events),
                "threshold": self.alert_thresholds["suspicious_patterns"],
                "events": suspicious_events[-5:]
            }
            alerts.append(alert)
        
        return alerts
    
    def analyze_rate_limiting(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze rate limiting violations"""
        alerts = []
        rate_limit_events = [e for e in events if "rate" in str(e).lower() and ("limit" in str(e).lower() or "exceed" in str(e).lower())]
        
        if len(rate_limit_events) >= self.alert_thresholds["rate_limit_hits"]:
            alert = {
                "timestamp": current_time.isoformat(),
                "alert_type": "rate_limit_exceeded",
                "severity": "MEDIUM",
                "message": f"Rate limiting violations: {len(rate_limit_events)} violations",
                "count": len(rate_limit_events),
                "threshold": self.alert_thresholds["rate_limit_hits"],
                "events": rate_limit_events[-5:]
            }
            alerts.append(alert)
        
        return alerts
    
    def analyze_ip_anomalies(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze IP address anomalies"""
        alerts = []
        ip_counts = defaultdict(int)
        
        for event in events:
            ip = event.get("remote_addr", "unknown")
            ip_counts[ip] += 1
        
        # Check for IPs with excessive activity
        for ip, count in ip_counts.items():
            if count > 50:  # More than 50 events from single IP
                alert = {
                    "timestamp": current_time.isoformat(),
                    "alert_type": "ip_anomaly",
                    "severity": "MEDIUM",
                    "message": f"Excessive activity from IP {ip}: {count} events",
                    "ip_address": ip,
                    "count": count,
                    "threshold": 50
                }
                alerts.append(alert)
        
        return alerts
    
    def analyze_sql_injection(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze SQL injection attempts"""
        alerts = []
        sql_injection_events = [e for e in events if "sql" in str(e).lower() and ("injection" in str(e).lower() or "union" in str(e).lower())]
        
        if len(sql_injection_events) >= self.alert_thresholds["sql_injection_attempts"]:
            alert = {
                "timestamp": current_time.isoformat(),
                "alert_type": "sql_injection_attempt",
                "severity": "HIGH",
                "message": f"SQL injection attempts detected: {len(sql_injection_events)} attempts",
                "count": len(sql_injection_events),
                "threshold": self.alert_thresholds["sql_injection_attempts"],
                "events": sql_injection_events[-5:]
            }
            alerts.append(alert)
        
        return alerts
    
    def analyze_xss_attempts(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Analyze XSS attempts"""
        alerts = []
        xss_events = [e for e in events if "xss" in str(e).lower() or "script" in str(e).lower() or "javascript:" in str(e).lower()]
        
        if len(xss_events) >= self.alert_thresholds["xss_attempts"]:
            alert = {
                "timestamp": current_time.isoformat(),
                "alert_type": "xss_attempt",
                "severity": "HIGH",
                "message": f"XSS attempts detected: {len(xss_events)} attempts",
                "count": len(xss_events),
                "threshold": self.alert_thresholds["xss_attempts"],
                "events": xss_events[-5:]
            }
            alerts.append(alert)
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send security alert"""
        # Check if we should throttle this alert type
        alert_type = alert["alert_type"]
        current_time = datetime.now()
        
        if alert_type in self.last_alert_time:
            time_since_last = current_time - self.last_alert_time[alert_type]
            if time_since_last < timedelta(minutes=5):  # Throttle to 5 minutes
                return
        
        self.last_alert_time[alert_type] = current_time
        self.alert_history.append(alert)
        
        # Log alert
        print(f"🚨 SECURITY ALERT: {alert['severity']} - {alert['message']}")
        
        # Save alert to file
        alert_file = os.path.join(self.production_path, "monitoring/security_alerts.json")
        try:
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            alerts.append(alert)
            
            # Keep only last 1000 alerts
            alerts = alerts[-1000:]
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving alert: {e}")
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        events = self.parse_security_log()
        current_time = datetime.now()
        
        # Calculate statistics
        total_events = len(events)
        recent_events = [e for e in events if self.is_recent_event(e, hours=24)]
        
        # Event type breakdown
        event_types = defaultdict(int)
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] += 1
        
        # Recent alerts
        recent_alerts = [a for a in self.alert_history if self.is_recent_event(a, hours=24)]
        
        report = {
            "timestamp": current_time.isoformat(),
            "system": "Stellar Logic AI",
            "report_type": "security_monitoring_report",
            "statistics": {
                "total_events": total_events,
                "recent_events_24h": len(recent_events),
                "event_types": dict(event_types),
                "total_alerts": len(self.alert_history),
                "recent_alerts_24h": len(recent_alerts)
            },
            "alerts": recent_alerts[-10:],  # Last 10 alerts
            "threat_level": self.calculate_threat_level(recent_alerts),
            "recommendations": self.generate_recommendations(recent_alerts)
        }
        
        return report
    
    def calculate_threat_level(self, alerts: List[Dict[str, Any]]) -> str:
        """Calculate current threat level"""
        if not alerts:
            return "LOW"
        
        high_severity = len([a for a in alerts if a.get("severity") == "HIGH"])
        medium_severity = len([a for a in alerts if a.get("severity") == "MEDIUM"])
        
        if high_severity >= 3:
            return "CRITICAL"
        elif high_severity >= 1 or medium_severity >= 5:
            return "HIGH"
        elif medium_severity >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_recommendations(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on alerts"""
        recommendations = []
        
        if not alerts:
            recommendations.append("System security posture is good - continue monitoring")
            return recommendations
        
        # Analyze alert types
        alert_types = [a.get("alert_type", "") for a in alerts]
        
        if "brute_force_attack" in alert_types:
            recommendations.append("Implement stronger password policies and account lockout mechanisms")
        
        if "sql_injection_attempt" in alert_types:
            recommendations.append("Review and strengthen input validation and parameterized queries")
        
        if "xss_attempt" in alert_types:
            recommendations.append("Enhance output encoding and Content Security Policy")
        
        if "rate_limit_exceeded" in alert_types:
            recommendations.append("Adjust rate limiting thresholds and consider IP blocking")
        
        if "ip_anomaly" in alert_types:
            recommendations.append("Implement IP reputation checking and geolocation filtering")
        
        recommendations.append("Review security logs for patterns and update detection rules")
        
        return recommendations
    
    def start_monitoring(self):
        """Start continuous security monitoring"""
        if self.monitoring_active:
            print("⚠️ Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print("✅ Security monitoring started")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        print("🔍 Starting security monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Parse security events
                events = self.parse_security_log()
                
                # Analyze for threats
                alerts = self.analyze_security_events(events)
                
                # Send alerts
                for alert in alerts:
                    self.send_alert(alert)
                
                # Generate hourly report
                current_time = datetime.now()
                if current_time.minute == 0:  # Top of the hour
                    report = self.generate_security_report()
                    self.save_report(report)
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Security monitoring stopped")
    
    def save_report(self, report: Dict[str, Any]):
        """Save security report"""
        report_file = os.path.join(self.production_path, "monitoring/security_report.json")
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Security report saved: {report['threat_level']} threat level")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "total_events": len(self.security_events),
            "total_alerts": len(self.alert_history),
            "last_check": datetime.now().isoformat(),
            "alert_thresholds": self.alert_thresholds
        }

def main():
    """Main function to start security monitoring"""
    print("🔍 STELLAR LOGIC AI - SECURITY MONITORING SYSTEM")
    print("=" * 60)
    
    # Initialize monitoring system
    monitor = StellarSecurityMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        print("📊 Security monitoring is active. Press Ctrl+C to stop.")
        
        # Generate initial report
        report = monitor.generate_security_report()
        monitor.save_report(report)
        
        print(f"🎯 Current Threat Level: {report['threat_level']}")
        print(f"📈 Recent Events (24h): {report['statistics']['recent_events_24h']}")
        print(f"🚨 Recent Alerts (24h): {report['statistics']['recent_alerts_24h']}")
        
        # Keep monitoring running
        while True:
            time.sleep(10)
            status = monitor.get_current_status()
            print(f"🔍 Monitoring: {status['total_events']} events, {status['total_alerts']} alerts")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping security monitoring...")
        monitor.stop_monitoring()
        print("✅ Security monitoring stopped safely")

if __name__ == "__main__":
    main()
