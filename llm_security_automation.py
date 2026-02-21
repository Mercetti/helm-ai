#!/usr/bin/env python3
"""
LLM Security Automation Scripts
Automated security maintenance and monitoring tasks
"""

import os
import sys
import json
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class LLMSecurityAutomation:
    """Automated LLM security maintenance and monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger("llm_security_automation")
        self.setup_logging()
        self.automation_config = self.load_config()
    
    def setup_logging(self):
        """Setup logging for automation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('llm_security_automation.log'),
                logging.StreamHandler()
            ]
        )
    
    def load_config(self) -> Dict[str, Any]:
        """Load automation configuration"""
        return {
            "daily_review": {
                "enabled": True,
                "time": "09:00",
                "generate_report": True,
                "update_patterns": True,
                "cleanup_old_events": True
            },
            "hourly_monitoring": {
                "enabled": True,
                "check_thresholds": True,
                "send_alerts": True,
                "update_dashboard": True
            },
            "weekly_maintenance": {
                "enabled": True,
                "day": "sunday",
                "time": "02:00",
                "backup_data": True,
                "optimize_models": True,
                "update_compliance": True
            },
            "alerts": {
                "block_rate_threshold": 30.0,
                "security_score_threshold": 70,
                "hourly_requests_threshold": 1000,
                "critical_events_threshold": 10
            }
        }
    
    def daily_security_review(self) -> Dict[str, Any]:
        """Perform daily security review"""
        self.logger.info("Starting daily security review")
        
        review_results = {
            "timestamp": datetime.now().isoformat(),
            "total_events": 0,
            "blocked_requests": 0,
            "security_score": 100,
            "top_threats": {},
            "recommendations": [],
            "actions_taken": []
        }
        
        try:
            # Load security metrics
            metrics = self._load_security_metrics()
            review_results.update(metrics)
            
            # Analyze threat patterns
            threat_analysis = self._analyze_threat_patterns()
            review_results["top_threats"] = threat_analysis
            
            # Generate recommendations
            recommendations = self._generate_daily_recommendations(metrics, threat_analysis)
            review_results["recommendations"] = recommendations
            
            # Update security patterns if needed
            if self.automation_config["daily_review"]["update_patterns"]:
                updated_patterns = self._update_security_patterns()
                if updated_patterns:
                    review_results["actions_taken"].append(f"Updated {len(updated_patterns)} security patterns")
            
            # Cleanup old events
            if self.automation_config["daily_review"]["cleanup_old_events"]:
                cleanup_count = self._cleanup_old_events()
                review_results["actions_taken"].append(f"Cleaned up {cleanup_count} old events")
            
            # Generate daily report
            if self.automation_config["daily_review"]["generate_report"]:
                report_path = self._generate_daily_report(review_results)
                review_results["actions_taken"].append(f"Generated daily report: {report_path}")
            
            self.logger.info(f"Daily security review completed: {len(review_results['actions_taken'])} actions taken")
            
        except Exception as e:
            self.logger.error(f"Daily security review failed: {e}")
            review_results["error"] = str(e)
        
        return review_results
    
    def hourly_monitoring(self) -> Dict[str, Any]:
        """Perform hourly security monitoring"""
        self.logger.info("Starting hourly security monitoring")
        
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "alerts": [],
            "metrics": {},
            "status": "normal"
        }
        
        try:
            # Check security metrics
            metrics = self._load_security_metrics()
            monitoring_results["metrics"] = metrics
            
            # Check thresholds
            alerts = self._check_security_thresholds(metrics)
            monitoring_results["alerts"] = alerts
            
            # Update status based on alerts
            if alerts:
                monitoring_results["status"] = "warning" if len(alerts) <= 2 else "critical"
            
            # Send alerts if enabled
            if alerts and self.automation_config["hourly_monitoring"]["send_alerts"]:
                self._send_alerts(alerts)
                monitoring_results["actions_taken"] = ["Sent security alerts"]
            
            # Update dashboard if enabled
            if self.automation_config["hourly_monitoring"]["update_dashboard"]:
                self._update_dashboard()
                if "actions_taken" not in monitoring_results:
                    monitoring_results["actions_taken"] = []
                monitoring_results["actions_taken"].append("Updated security dashboard")
            
            self.logger.info(f"Hourly monitoring completed: {len(alerts)} alerts generated")
            
        except Exception as e:
            self.logger.error(f"Hourly monitoring failed: {e}")
            monitoring_results["error"] = str(e)
        
        return monitoring_results
    
    def weekly_maintenance(self) -> Dict[str, Any]:
        """Perform weekly maintenance tasks"""
        self.logger.info("Starting weekly maintenance")
        
        maintenance_results = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "backup_status": "not_attempted",
            "optimization_status": "not_attempted",
            "compliance_status": "not_attempted"
        }
        
        try:
            # Backup security data
            if self.automation_config["weekly_maintenance"]["backup_data"]:
                backup_status = self._backup_security_data()
                maintenance_results["backup_status"] = backup_status
                maintenance_results["actions_taken"].append(f"Security data backup: {backup_status}")
            
            # Optimize models
            if self.automation_config["weekly_maintenance"]["optimize_models"]:
                optimization_status = self._optimize_security_models()
                maintenance_results["optimization_status"] = optimization_status
                maintenance_results["actions_taken"].append(f"Model optimization: {optimization_status}")
            
            # Update compliance
            if self.automation_config["weekly_maintenance"]["update_compliance"]:
                compliance_status = self._update_compliance_status()
                maintenance_results["compliance_status"] = compliance_status
                maintenance_results["actions_taken"].append(f"Compliance update: {compliance_status}")
            
            self.logger.info(f"Weekly maintenance completed: {len(maintenance_results['actions_taken'])} actions taken")
            
        except Exception as e:
            self.logger.error(f"Weekly maintenance failed: {e}")
            maintenance_results["error"] = str(e)
        
        return maintenance_results
    
    def _load_security_metrics(self) -> Dict[str, Any]:
        """Load current security metrics"""
        # This would integrate with the actual security system
        # For now, return mock data
        return {
            "total_requests": 1500,
            "blocked_requests": 45,
            "block_rate": 3.0,
            "security_score": 97,
            "injection_attempts": 12,
            "content_violations": 8,
            "rate_limit_violations": 25
        }
    
    def _analyze_threat_patterns(self) -> Dict[str, int]:
        """Analyze threat patterns"""
        # Mock threat analysis
        return {
            "pattern_injection": 12,
            "rate_limit": 25,
            "inappropriate_content": 8,
            "length_anomaly": 3,
            "similarity_injection": 2
        }
    
    def _generate_daily_recommendations(self, metrics: Dict[str, Any], threats: Dict[str, int]) -> List[str]:
        """Generate daily recommendations"""
        recommendations = []
        
        # Check block rate
        if metrics["block_rate"] > 10:
            recommendations.append(f"Block rate ({metrics['block_rate']:.1f}%) is elevated - review security rules")
        
        # Check security score
        if metrics["security_score"] < 90:
            recommendations.append(f"Security score ({metrics['security_score']}) is below optimal - investigate issues")
        
        # Check specific threats
        if threats.get("pattern_injection", 0) > 10:
            recommendations.append("High injection attempts - strengthen prompt detection")
        
        if threats.get("rate_limit", 0) > 20:
            recommendations.append("Excessive rate limit violations - consider stricter controls")
        
        if threats.get("inappropriate_content", 0) > 5:
            recommendations.append("Content violations detected - review filtering rules")
        
        return recommendations
    
    def _update_security_patterns(self) -> List[str]:
        """Update security patterns with new threats"""
        # Mock pattern updates
        new_patterns = [
            "new_injection_pattern_1",
            "new_content_filter_1",
            "new_rate_limit_rule_1"
        ]
        
        self.logger.info(f"Updated security patterns: {new_patterns}")
        return new_patterns
    
    def _cleanup_old_events(self) -> int:
        """Clean up old security events"""
        # Mock cleanup
        cleanup_count = 150
        self.logger.info(f"Cleaned up {cleanup_count} old security events")
        return cleanup_count
    
    def _generate_daily_report(self, results: Dict[str, Any]) -> str:
        """Generate daily security report"""
        report_path = f"daily_security_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Generated daily security report: {report_path}")
        return report_path
    
    def _check_security_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check security thresholds and generate alerts"""
        alerts = []
        config = self.automation_config["alerts"]
        
        # Check block rate
        if metrics["block_rate"] > config["block_rate_threshold"]:
            alerts.append({
                "type": "block_rate",
                "severity": "high",
                "message": f"Block rate ({metrics['block_rate']:.1f}%) exceeds threshold ({config['block_rate_threshold']}%)"
            })
        
        # Check security score
        if metrics["security_score"] < config["security_score_threshold"]:
            alerts.append({
                "type": "security_score",
                "severity": "medium",
                "message": f"Security score ({metrics['security_score']}) below threshold ({config['security_score_threshold']})"
            })
        
        # Check hourly requests
        if metrics["total_requests"] > config["hourly_requests_threshold"]:
            alerts.append({
                "type": "request_volume",
                "severity": "medium",
                "message": f"Request volume ({metrics['total_requests']}) exceeds threshold ({config['hourly_requests_threshold']})"
            })
        
        return alerts
    
    def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send security alerts"""
        for alert in alerts:
            self.logger.warning(f"SECURITY ALERT: {alert['message']}")
        
        # In a real implementation, this would send emails, Slack messages, etc.
    
    def _update_dashboard(self):
        """Update security dashboard"""
        # In a real implementation, this would update the dashboard data
        self.logger.info("Security dashboard updated")
    
    def _backup_security_data(self) -> str:
        """Backup security data"""
        backup_path = f"security_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Mock backup
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self._load_security_metrics(),
            "events": []  # Would include actual events
        }
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        self.logger.info(f"Security data backed up: {backup_path}")
        return f"success: {backup_path}"
    
    def _optimize_security_models(self) -> str:
        """Optimize security models"""
        # Mock optimization
        self.logger.info("Security models optimized")
        return "success"
    
    def _update_compliance_status(self) -> str:
        """Update compliance status"""
        # Mock compliance update
        self.logger.info("Compliance status updated")
        return "success"
    
    def start_automation_scheduler(self):
        """Start the automation scheduler"""
        self.logger.info("Starting LLM security automation scheduler")
        
        # Schedule daily review
        if self.automation_config["daily_review"]["enabled"]:
            schedule.every().day.at(self.automation_config["daily_review"]["time"]).do(self.daily_security_review)
            self.logger.info(f"Scheduled daily review at {self.automation_config['daily_review']['time']}")
        
        # Schedule hourly monitoring
        if self.automation_config["hourly_monitoring"]["enabled"]:
            schedule.every().hour.do(self.hourly_monitoring)
            self.logger.info("Scheduled hourly monitoring")
        
        # Schedule weekly maintenance
        if self.automation_config["weekly_maintenance"]["enabled"]:
            schedule.every().sunday.at(self.automation_config["weekly_maintenance"]["time"]).do(self.weekly_maintenance)
            self.logger.info(f"Scheduled weekly maintenance on {self.automation_config['weekly_maintenance']['day']} at {self.automation_config['weekly_maintenance']['time']}")
        
        # Run the scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Automation scheduler stopped")
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)

def main():
    """Main function to run automation"""
    automation = LLMSecurityAutomation()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "daily":
            results = automation.daily_security_review()
            print(json.dumps(results, indent=2, default=str))
        elif command == "hourly":
            results = automation.hourly_monitoring()
            print(json.dumps(results, indent=2, default=str))
        elif command == "weekly":
            results = automation.weekly_maintenance()
            print(json.dumps(results, indent=2, default=str))
        elif command == "schedule":
            automation.start_automation_scheduler()
        else:
            print("Available commands: daily, hourly, weekly, schedule")
    else:
        print("LLM Security Automation")
        print("Usage: python llm_security_automation.py [daily|hourly|weekly|schedule]")

if __name__ == "__main__":
    main()
