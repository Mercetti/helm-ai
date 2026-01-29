"""
Helm AI Comprehensive Audit Logger
This module provides enterprise-grade audit logging for compliance and security
"""

import os
import json
import logging
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict
import threading
from queue import Queue, Empty
import gzip
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Audit event types"""
    # Authentication Events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    
    # Authorization Events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Data Access Events
    DATA_READ = "data_read"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # System Events
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    API_KEY_CREATED = "api_key_created"
    API_KEY_DELETED = "api_key_deleted"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # Security Events
    SECURITY_BREACH = "security_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALICIOUS_REQUEST = "malicious_request"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Compliance Events
    GDPR_REQUEST = "gdpr_request"
    DATA_RETENTION_POLICY = "data_retention_policy"
    COMPLIANCE_REPORT = "compliance_report"

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: AuditEventType = None
    user_id: str = None
    session_id: str = None
    ip_address: str = None
    user_agent: str = None
    resource_id: str = None
    resource_type: str = None
    action: str = None
    outcome: str = None  # success, failure, error
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    data_classification: DataClassification = DataClassification.INTERNAL
    risk_score: int = 0  # 0-100
    correlation_id: str = None
    source_service: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AuditLogger:
    """Enterprise audit logger with compliance support"""
    
    def __init__(self):
        self.events_queue = Queue()
        self.batch_size = int(os.getenv('AUDIT_BATCH_SIZE', '100'))
        self.flush_interval = int(os.getenv('AUDIT_FLUSH_INTERVAL', '60'))  # seconds
        self.retention_days = int(os.getenv('AUDIT_RETENTION_DAYS', '2555'))  # 7 years default
        
        # Storage backends
        self.use_s3 = os.getenv('AUDIT_S3_BUCKET') is not None
        self.use_local = os.getenv('AUDIT_LOCAL_PATH') is not None
        
        # Initialize S3 client if configured
        if self.use_s3:
            self.s3_client = boto3.client('s3')
            self.s3_bucket = os.getenv('AUDIT_S3_BUCKET')
        
        # Start background thread for processing events
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        # Schedule periodic flush
        self._schedule_flush()
    
    def log_event(self, event: AuditEvent):
        """Log audit event"""
        try:
            # Add correlation ID if not present
            if not event.correlation_id:
                event.correlation_id = str(uuid.uuid4())
            
            # Calculate risk score if not set
            if event.risk_score == 0:
                event.risk_score = self._calculate_risk_score(event)
            
            # Add to queue for processing
            self.events_queue.put(event)
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def log_authentication_event(self, 
                                event_type: AuditEventType,
                                user_id: str,
                                outcome: str,
                                ip_address: str = None,
                                user_agent: str = None,
                                details: Dict[str, Any] = None):
        """Log authentication event"""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=outcome,
            details=details or {},
            compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
            source_service="auth_service"
        )
        
        self.log_event(event)
    
    def log_data_access(self, 
                       user_id: str,
                       resource_id: str,
                       resource_type: str,
                       action: str,
                       outcome: str,
                       data_classification: DataClassification = DataClassification.INTERNAL,
                       details: Dict[str, Any] = None):
        """Log data access event"""
        event = AuditEvent(
            event_type=AuditEventType.DATA_READ if action == "read" else AuditEventType.DATA_UPDATED,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            outcome=outcome,
            data_classification=data_classification,
            details=details or {},
            compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOC2],
            source_service="api_service"
        )
        
        self.log_event(event)
    
    def log_security_event(self, 
                          event_type: AuditEventType,
                          user_id: str = None,
                          ip_address: str = None,
                          details: Dict[str, Any] = None,
                          risk_score: int = None):
        """Log security event"""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            outcome="detected",
            details=details or {},
            risk_score=risk_score or self._calculate_risk_score(event),
            compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
            source_service="security_service"
        )
        
        self.log_event(event)
    
    def log_compliance_event(self, 
                           event_type: AuditEventType,
                           framework: ComplianceFramework,
                           user_id: str = None,
                           details: Dict[str, Any] = None):
        """Log compliance event"""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            outcome="processed",
            details=details or {},
            compliance_frameworks=[framework],
            source_service="compliance_service"
        )
        
        self.log_event(event)
    
    def _calculate_risk_score(self, event: AuditEvent) -> int:
        """Calculate risk score for event"""
        base_score = 0
        
        # Event type risk scoring
        event_risk_scores = {
            AuditEventType.SECURITY_BREACH: 100,
            AuditEventType.MALICIOUS_REQUEST: 90,
            AuditEventType.SUSPICIOUS_ACTIVITY: 70,
            AuditEventType.LOGIN_FAILED: 30,
            AuditEventType.DATA_DELETED: 60,
            AuditEventType.DATA_EXPORTED: 40,
            AuditEventType.PERMISSION_GRANTED: 20,
            AuditEventType.ROLE_ASSIGNED: 15
        }
        
        base_score += event_risk_scores.get(event.event_type, 10)
        
        # Data classification risk
        classification_scores = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 10,
            DataClassification.CONFIDENTIAL: 30,
            DataClassification.RESTRICTED: 50
        }
        
        base_score += classification_scores.get(event.data_classification, 10)
        
        # Outcome risk
        if event.outcome == "failure":
            base_score += 20
        elif event.outcome == "error":
            base_score += 15
        
        # Time-based risk (off-hours access)
        hour = event.timestamp.hour
        if hour < 6 or hour > 22:
            base_score += 10
        
        return min(base_score, 100)
    
    def _process_events(self):
        """Process audit events from queue"""
        batch = []
        
        while True:
            try:
                # Get event from queue with timeout
                try:
                    event = self.events_queue.get(timeout=1)
                    batch.append(event)
                except Empty:
                    continue
                
                # Process batch if full or timeout
                if len(batch) >= self.batch_size:
                    self._flush_batch(batch)
                    batch = []
                    
            except Exception as e:
                logger.error(f"Error processing audit events: {e}")
    
    def _flush_batch(self, events: List[AuditEvent]):
        """Flush batch of events to storage"""
        try:
            # Convert events to JSON
            events_data = [asdict(event) for event in events]
            
            # Convert datetime objects to ISO format
            for event_data in events_data:
                event_data['timestamp'] = event_data['timestamp'].isoformat()
                event_data['event_type'] = event_data['event_type'].value
                event_data['data_classification'] = event_data['data_classification'].value
                event_data['compliance_frameworks'] = [fw.value for fw in event_data['compliance_frameworks']]
            
            # Store in different backends
            if self.use_s3:
                self._store_to_s3(events_data)
            
            if self.use_local:
                self._store_to_local(events_data)
            
            logger.info(f"Flushed {len(events)} audit events")
            
        except Exception as e:
            logger.error(f"Failed to flush audit batch: {e}")
    
    def _store_to_s3(self, events_data: List[Dict[str, Any]]):
        """Store events to S3"""
        try:
            # Create daily partition
            date_str = datetime.now().strftime('%Y/%m/%d')
            filename = f"audit-logs/{date_str}/audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json.gz"
            
            # Compress data
            json_data = json.dumps(events_data)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=filename,
                Body=compressed_data,
                ContentEncoding='gzip',
                ContentType='application/json'
            )
            
        except ClientError as e:
            logger.error(f"Failed to store audit events to S3: {e}")
    
    def _store_to_local(self, events_data: List[Dict[str, Any]]):
        """Store events to local filesystem"""
        try:
            local_path = os.getenv('AUDIT_LOCAL_PATH', '/var/log/audit')
            os.makedirs(local_path, exist_ok=True)
            
            # Create daily file
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"audit-{date_str}.json"
            filepath = os.path.join(local_path, filename)
            
            # Append to file
            with open(filepath, 'a') as f:
                for event_data in events_data:
                    f.write(json.dumps(event_data) + '\n')
            
        except Exception as e:
            logger.error(f"Failed to store audit events locally: {e}")
    
    def _schedule_flush(self):
        """Schedule periodic flush"""
        def flush_timer():
            while True:
                try:
                    # Collect any remaining events
                    batch = []
                    while True:
                        try:
                            event = self.events_queue.get_nowait()
                            batch.append(event)
                        except Empty:
                            break
                    
                    if batch:
                        self._flush_batch(batch)
                    
                    # Wait for next interval
                    threading.Event().wait(self.flush_interval)
                    
                except Exception as e:
                    logger.error(f"Error in flush timer: {e}")
        
        flush_thread = threading.Thread(target=flush_timer, daemon=True)
        flush_thread.start()
    
    def search_events(self, 
                     start_time: datetime = None,
                     end_time: datetime = None,
                     user_id: str = None,
                     event_type: AuditEventType = None,
                     resource_id: str = None,
                     min_risk_score: int = None,
                     compliance_framework: ComplianceFramework = None,
                     limit: int = 1000) -> List[Dict[str, Any]]:
        """Search audit events"""
        # This would integrate with your search backend (Elasticsearch, etc.)
        # For now, return placeholder
        return {
            "query": {
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "user_id": user_id,
                "event_type": event_type.value if event_type else None,
                "resource_id": resource_id,
                "min_risk_score": min_risk_score,
                "compliance_framework": compliance_framework.value if compliance_framework else None,
                "limit": limit
            },
            "message": "Search requires integration with audit backend"
        }
    
    def generate_compliance_report(self, 
                                 framework: ComplianceFramework,
                                 start_date: datetime,
                                 end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report"""
        report = {
            "framework": framework.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "events": []
        }
        
        # Framework-specific requirements
        if framework == ComplianceFramework.GDPR:
            report["requirements"] = {
                "data_processing_records": "Required",
                "consent_management": "Required",
                "data_subject_requests": "Required",
                "breach_notifications": "Required"
            }
        elif framework == ComplianceFramework.SOC2:
            report["requirements"] = {
                "access_controls": "Required",
                "security_monitoring": "Required",
                "change_management": "Required",
                "incident_response": "Required"
            }
        
        return report
    
    def cleanup_old_events(self):
        """Clean up events older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        if self.use_s3:
            try:
                # List and delete old S3 objects
                prefix = "audit-logs/"
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=prefix
                )
                
                for obj in response.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        
            except ClientError as e:
                logger.error(f"Failed to cleanup old S3 audit events: {e}")
        
        if self.use_local:
            try:
                local_path = os.getenv('AUDIT_LOCAL_PATH', '/var/log/audit')
                for filename in os.listdir(local_path):
                    if filename.startswith('audit-') and filename.endswith('.json'):
                        filepath = os.path.join(local_path, filename)
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            
            except Exception as e:
                logger.error(f"Failed to cleanup old local audit events: {e}")
        
        logger.info(f"Cleaned up audit events older than {cutoff_date}")


# Global instance
audit_logger = AuditLogger()
