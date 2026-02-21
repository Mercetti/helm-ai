#!/usr/bin/env python3
"""
LLM Security Pipeline Integration
Integrates LLM security enhancements with existing Stellar Logic AI pipeline
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from security.llm_security_enhancements import llm_security_manager, LLMSecurityEvent, ThreatLevel
from audit.audit_logger import audit_logger, AuditEventType, ComplianceFramework

@dataclass
class LLMPipelineRequest:
    """LLM pipeline request structure"""
    request_id: str
    user_id: str
    user_tier: str  # free, basic, premium, enterprise
    prompt: str
    context: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class LLMPipelineResponse:
    """LLM pipeline response structure"""
    request_id: str
    user_id: str
    response: Optional[str]
    security_events: List[LLMSecurityEvent]
    blocked: bool
    reason: Optional[str]
    processing_time: float
    timestamp: datetime

class LLMSecurityPipeline:
    """Integrated LLM security pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger("llm_security_pipeline")
        self.user_tier_configs = self._load_tier_configs()
        self.security_metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "injection_attempts": 0,
            "content_violations": 0,
            "rate_limit_violations": 0,
            "false_positives": 0
        }
        
    def _load_tier_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load user tier configurations"""
        return {
            "free": {
                "requests_per_minute": 10,
                "requests_per_hour": 100,
                "requests_per_day": 500,
                "max_prompt_length": 1000,
                "max_response_length": 2000,
                "features": ["basic_security"]
            },
            "basic": {
                "requests_per_minute": 30,
                "requests_per_hour": 500,
                "requests_per_day": 2000,
                "max_prompt_length": 2000,
                "max_response_length": 4000,
                "features": ["basic_security", "content_filtering"]
            },
            "premium": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 5000,
                "max_prompt_length": 5000,
                "max_response_length": 8000,
                "features": ["basic_security", "content_filtering", "advanced_validation"]
            },
            "enterprise": {
                "requests_per_minute": 120,
                "requests_per_hour": 2000,
                "requests_per_day": 10000,
                "max_prompt_length": 10000,
                "max_response_length": 15000,
                "features": ["basic_security", "content_filtering", "advanced_validation", "custom_models"]
            }
        }
    
    def configure_user_limits(self, user_id: str, tier: str) -> bool:
        """Configure rate limits based on user tier"""
        if tier not in self.user_tier_configs:
            self.logger.error(f"Unknown user tier: {tier}")
            return False
        
        config = self.user_tier_configs[tier]
        
        # Update user limits in security manager
        if user_id not in llm_security_manager.user_limits:
            llm_security_manager.user_limits[user_id] = {}
        
        llm_security_manager.user_limits[user_id].update(config)
        llm_security_manager.user_limits[user_id]["tier"] = tier
        
        self.logger.info(f"Configured user {user_id} with {tier} tier limits")
        return True
    
    def process_request(self, request: LLMPipelineRequest) -> LLMPipelineResponse:
        """Process LLM request through security pipeline"""
        start_time = time.time()
        security_events = []
        
        # Configure user limits if not already done
        if request.user_id not in llm_security_manager.user_limits:
            self.configure_user_limits(request.user_id, request.user_tier)
        
        # Get user config
        user_config = self.user_tier_configs.get(request.user_tier, self.user_tier_configs["free"])
        
        # Check prompt length
        if len(request.prompt) > user_config["max_prompt_length"]:
            event = LLMSecurityEvent(
                event_id=f"length_{int(time.time())}",
                timestamp=datetime.now(),
                threat_level=ThreatLevel.MEDIUM,
                threat_type="prompt_length_limit",
                user_id=request.user_id,
                prompt=request.prompt,
                blocked=True,
                reason=f"Prompt exceeds {user_tier} tier limit ({len(request.prompt)} > {user_config['max_prompt_length']})"
            )
            security_events.append(event)
            llm_security_manager.security_events.append(event)
            
            return LLMPipelineResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                response=None,
                security_events=security_events,
                blocked=True,
                reason=event.reason,
                processing_time=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        # Process through security manager
        can_proceed, reason, security_event = llm_security_manager.process_request(request.prompt, request.user_id)
        
        if security_event:
            security_events.append(security_event)
        
        if not can_proceed:
            self.security_metrics["blocked_requests"] += 1
            if "injection" in security_event.threat_type:
                self.security_metrics["injection_attempts"] += 1
            elif "rate_limit" in security_event.threat_type:
                self.security_metrics["rate_limit_violations"] += 1
            
            return LLMPipelineResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                response=None,
                security_events=security_events,
                blocked=True,
                reason=reason,
                processing_time=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        # Simulate LLM processing (in real implementation, this would call the actual LLM)
        response = self._generate_llm_response(request.prompt, user_config)
        
        # Process response through security
        is_safe, response_events = llm_security_manager.process_response(response, request.prompt, request.user_id)
        security_events.extend(response_events)
        
        if not is_safe:
            self.security_metrics["blocked_requests"] += 1
            self.security_metrics["content_violations"] += 1
            
            return LLMPipelineResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                response=None,
                security_events=security_events,
                blocked=True,
                reason="Response content violated security policies",
                processing_time=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        # Check response length
        if len(response) > user_config["max_response_length"]:
            event = LLMSecurityEvent(
                event_id=f"resp_len_{int(time.time())}",
                timestamp=datetime.now(),
                threat_level=ThreatLevel.MEDIUM,
                threat_type="response_length_limit",
                user_id=request.user_id,
                prompt=request.prompt,
                response=response,
                blocked=True,
                reason=f"Response exceeds {request.user_tier} tier limit ({len(response)} > {user_config['max_response_length']})"
            )
            security_events.append(event)
            llm_security_manager.security_events.append(event)
            
            return LLMPipelineResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                response=None,
                security_events=security_events,
                blocked=True,
                reason=event.reason,
                processing_time=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        # Log successful request
        self._log_security_event(request, response, security_events)
        
        self.security_metrics["total_requests"] += 1
        
        return LLMPipelineResponse(
            request_id=request.request_id,
            user_id=request.user_id,
            response=response,
            security_events=security_events,
            blocked=False,
            reason=None,
            processing_time=time.time() - start_time,
            timestamp=datetime.now()
        )
    
    def _generate_llm_response(self, prompt: str, user_config: Dict[str, Any]) -> str:
        """Generate LLM response (mock implementation)"""
        # In real implementation, this would call the actual LLM
        responses = [
            "I understand your request. Here's a helpful response based on your input.",
            "Based on your question, I can provide the following information.",
            "That's an interesting question. Let me help you with that.",
            "I can assist with that. Here's what you need to know.",
            "Thank you for your question. Here's my response."
        ]
        
        # Simple mock response based on prompt length
        response_index = min(len(prompt) // 100, len(responses) - 1)
        base_response = responses[response_index]
        
        # Add tier-specific features
        if "advanced_validation" in user_config["features"]:
            base_response += " This response has been validated for accuracy and compliance."
        
        if "custom_models" in user_config["features"]:
            base_response += " Generated using enterprise-grade AI models."
        
        return base_response
    
    def _log_security_event(self, request: LLMPipelineRequest, response: str, security_events: List[LLMSecurityEvent]):
        """Log security events to audit system"""
        try:
            # Log to audit logger
            audit_logger.log_security_event(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=request.user_id,
                details={
                    "request_id": request.request_id,
                    "user_tier": request.user_tier,
                    "prompt_length": len(request.prompt),
                    "response_length": len(response),
                    "security_events": len(security_events),
                    "processing_time": time.time()
                }
            )
            
            # Log compliance events
            audit_logger.log_compliance_event(
                event_type=AuditEventType.DATA_ACCESS,
                framework=ComplianceFramework.GDPR,
                user_id=request.user_id,
                details={
                    "llm_request": True,
                    "data_processed": True,
                    "security_checks_passed": True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        total_requests = self.security_metrics["total_requests"]
        blocked_requests = self.security_metrics["blocked_requests"]
        
        return {
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "block_rate": (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
            "injection_attempts": self.security_metrics["injection_attempts"],
            "content_violations": self.security_metrics["content_violations"],
            "rate_limit_violations": self.security_metrics["rate_limit_violations"],
            "false_positives": self.security_metrics["false_positives"],
            "security_score": max(0, 100 - (blocked_requests / total_requests * 100)) if total_requests > 0 else 100
        }
    
    def update_security_patterns(self, new_patterns: List[str]) -> bool:
        """Update security patterns for injection detection"""
        try:
            # Add new patterns to injection detector
            llm_security_manager.injection_detector.injection_patterns.extend(new_patterns)
            
            # Recompile patterns
            import re
            llm_security_manager.injection_detector.compiled_patterns = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in llm_security_manager.injection_detector.injection_patterns
            ]
            
            self.logger.info(f"Updated security patterns with {len(new_patterns)} new patterns")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update security patterns: {e}")
            return False
    
    def review_security_events(self, hours: int = 24) -> Dict[str, Any]:
        """Review security events for the specified period"""
        summary = llm_security_manager.get_security_summary(hours)
        
        # Add additional analysis
        recent_events = [
            event for event in llm_security_manager.security_events
            if event.timestamp > datetime.now() - timedelta(hours=hours)
        ]
        
        # Analyze patterns
        threat_types = {}
        user_activity = {}
        
        for event in recent_events:
            threat_types[event.threat_type] = threat_types.get(event.threat_type, 0) + 1
            if event.user_id:
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
        
        # Identify top users
        top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            **summary,
            "threat_analysis": threat_types,
            "top_active_users": top_users,
            "recommendations": self._generate_security_recommendations(threat_types, recent_events)
        }
    
    def _generate_security_recommendations(self, threat_types: Dict[str, int], events: List[LLMSecurityEvent]) -> List[str]:
        """Generate security recommendations based on threat analysis"""
        recommendations = []
        
        # High injection attempts
        if threat_types.get("pattern_injection", 0) > 10:
            recommendations.append("High number of injection attempts detected - consider strengthening detection patterns")
        
        # High rate limit violations
        if threat_types.get("rate_limit", 0) > 20:
            recommendations.append("Excessive rate limit violations - consider implementing CAPTCHA or stricter limits")
        
        # Content violations
        if threat_types.get("inappropriate_prompt", 0) > 5:
            recommendations.append("Multiple content violations - review and update content filtering rules")
        
        # PII leakage
        if threat_types.get("pii_leak", 0) > 0:
            recommendations.append("URGENT: PII detected in responses - review output validation immediately")
        
        # Length anomalies
        if threat_types.get("length_anomaly", 0) > 5:
            recommendations.append("Unusual prompt lengths detected - monitor for potential abuse")
        
        return recommendations

# Global pipeline instance
llm_security_pipeline = LLMSecurityPipeline()
