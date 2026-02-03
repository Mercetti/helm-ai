#!/usr/bin/env python3
import json
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any

class RateLimitingMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.config_file = "production/config/rate_limiting_config.json"
        self.data_file = "production/storage/rate_limiting/rate_limit_data.json"
        self.load_configuration()
        self.load_data()
        
    def load_configuration(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"enabled": False}
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"ip_requests": {}, "blocked_ips": {}, "statistics": {}}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    def is_rate_limited(self, ip_address: str, endpoint: str) -> Dict[str, Any]:
        if not self.config.get("enabled", False):
            return {"allowed": True, "reason": "Rate limiting disabled"}
        
        current_time = datetime.now()
        
        # Check if IP is blocked
        if ip_address in self.data.get("blocked_ips", {}):
            blocked_until = datetime.fromisoformat(self.data["blocked_ips"][ip_address])
            if current_time < blocked_until:
                return {"allowed": False, "reason": "IP blocked", "retry_after": int((blocked_until - current_time).total_seconds())}
            else:
                # Unblock IP
                del self.data["blocked_ips"][ip_address]
        
        # Get limits for this endpoint
        endpoint_limits = self.config.get("endpoint_limits", {}).get(endpoint, self.config.get("default_limits", {}))
        
        # Check IP-based limits
        ip_requests = self.data.get("ip_requests", {}).get(ip_address, {})
        
        for period, limit in endpoint_limits.items():
            if period == "requests_per_minute":
                window = timedelta(minutes=1)
            elif period == "requests_per_hour":
                window = timedelta(hours=1)
            elif period == "requests_per_day":
                window = timedelta(days=1)
            else:
                continue
            
            # Count requests in window
            requests_in_window = 0
            for timestamp in ip_requests.get(period, []):
                request_time = datetime.fromisoformat(timestamp)
                if current_time - request_time <= window:
                    requests_in_window += 1
            
            if requests_in_window >= limit:
                # Apply penalty if threshold exceeded
                penalty_threshold = self.config.get("penalty_threshold", 100)
                if requests_in_window >= penalty_threshold:
                    penalty_duration = self.config.get("penalty_duration", 300)
                    blocked_until = current_time + timedelta(seconds=penalty_duration)
                    self.data["blocked_ips"][ip_address] = blocked_until.isoformat()
                    self.save_data()
                    return {"allowed": False, "reason": "IP blocked for excessive requests", "retry_after": penalty_duration}
                
                return {"allowed": False, "reason": f"Rate limit exceeded: {period}", "retry_after": int(window.total_seconds())}
        
        return {"allowed": True, "reason": "Request allowed"}
    
    def record_request(self, ip_address: str, endpoint: str):
        if not self.config.get("enabled", False):
            return
        
        current_time = datetime.now().isoformat()
        
        # Update IP requests
        if "ip_requests" not in self.data:
            self.data["ip_requests"] = {}
        
        if ip_address not in self.data["ip_requests"]:
            self.data["ip_requests"][ip_address] = {
                "requests_per_minute": [],
                "requests_per_hour": [],
                "requests_per_day": []
            }
        
        # Add current request to all time windows
        for period in ["requests_per_minute", "requests_per_hour", "requests_per_day"]:
            self.data["ip_requests"][ip_address][period].append(current_time)
        
        # Update statistics
        if "statistics" not in self.data:
            self.data["statistics"] = {}
        
        self.data["statistics"]["total_requests"] = self.data["statistics"].get("total_requests", 0) + 1
        self.data["statistics"]["active_ips"] = len(self.data["ip_requests"])
        self.data["statistics"]["last_request"] = current_time
        
        self.save_data()
    
    def cleanup_old_data(self):
        current_time = datetime.now()
        cleanup_interval = self.config.get("cleanup_interval", 3600)
        last_cleanup = self.data.get("statistics", {}).get("last_cleanup")
        
        if last_cleanup:
            last_cleanup_time = datetime.fromisoformat(last_cleanup)
            if current_time - last_cleanup_time < timedelta(seconds=cleanup_interval):
                return
        
        # Clean up old request records
        for ip_address, ip_data in self.data.get("ip_requests", {}).items():
            for period, requests in ip_data.items():
                if period == "requests_per_minute":
                    window = timedelta(minutes=5)  # Keep 5 minutes
                elif period == "requests_per_hour":
                    window = timedelta(hours=2)  # Keep 2 hours
                elif period == "requests_per_day":
                    window = timedelta(days=2)  # Keep 2 days
                else:
                    continue
                
                # Filter old requests
                filtered_requests = []
                for timestamp in requests:
                    request_time = datetime.fromisoformat(timestamp)
                    if current_time - request_time <= window:
                        filtered_requests.append(timestamp)
                
                ip_data[period] = filtered_requests
        
        # Clean up blocked IPs
        blocked_ips = self.data.get("blocked_ips", {})
        for ip_address, blocked_until in list(blocked_ips.items()):
            if datetime.fromisoformat(blocked_until) < current_time:
                del blocked_ips[ip_address]
        
        # Update cleanup time
        self.data["statistics"]["last_cleanup"] = current_time.isoformat()
        self.save_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        return self.data.get("statistics", {})
