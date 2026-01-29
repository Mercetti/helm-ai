"""
Helm AI Data Protection and Privacy
This module provides data protection, privacy controls, and GDPR compliance features
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import cryptography.fernet
from cryptography.fernet import Fernet
import re

from .audit_logger import AuditLogger, DataClassification, AuditEventType

logger = logging.getLogger(__name__)

class DataSubjectRequestType(Enum):
    """Types of data subject requests"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"

class RequestStatus(Enum):
    """Data subject request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class ConsentType(Enum):
    """Types of consent"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    THIRD_PARTY_SHARING = "third_party_sharing"
    EMAIL_COMMUNICATION = "email_communication"

@dataclass
class ConsentRecord:
    """Consent record for data processing"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    consent_text: str
    purpose: str
    legal_basis: str
    retention_period: int  # days
    withdrawn_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataSubjectRequest:
    """Data subject request record"""
    request_id: str
    user_id: str
    request_type: DataSubjectRequestType
    description: str
    status: RequestStatus
    created_at: datetime
    due_date: datetime
    completed_at: Optional[datetime] = None
    assigned_to: str = None
    notes: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataProcessingRecord:
    """Record of data processing activities"""
    record_id: str
    controller: str
    processor: str
    purpose: str
    data_categories: List[str]
    recipients: List[str]
    retention_period: str
    security_measures: List[str]
    legal_basis: str
    created_at: datetime
    updated_at: datetime

class DataProtectionManager:
    """Data protection and privacy management"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # In-memory storage (would use database in production)
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        self.processing_records: Dict[str, DataProcessingRecord] = {}
        self.data_subjects: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_processing_records()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data protection"""
        key_file = os.getenv('DATA_PROTECTION_KEY_FILE', '/etc/helm-ai/data_protection.key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key
    
    def _initialize_processing_records(self):
        """Initialize default data processing records"""
        # AI Model Training Processing
        self.processing_records["ai_training"] = DataProcessingRecord(
            record_id="ai_training",
            controller="Helm AI",
            processor="Helm AI",
            purpose="AI model training and improvement",
            data_categories=["User interactions", "Model inputs", "Performance metrics"],
            recipients=["Helm AI research team"],
            retention_period="2 years",
            security_measures=["Encryption at rest", "Access controls", "Audit logging"],
            legal_basis="Legitimate interest",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Analytics Processing
        self.processing_records["analytics"] = DataProcessingRecord(
            record_id="analytics",
            controller="Helm AI",
            processor="Helm AI",
            purpose="Service analytics and improvement",
            data_categories=["Usage patterns", "Performance data", "Error logs"],
            recipients=["Helm AI analytics team"],
            retention_period="1 year",
            security_measures=["Encryption", "Anonymization", "Access controls"],
            legal_basis="Legitimate interest",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def record_consent(self, 
                      user_id: str,
                      consent_type: ConsentType,
                      granted: bool,
                      ip_address: str,
                      user_agent: str,
                      consent_text: str,
                      purpose: str,
                      legal_basis: str = "Consent",
                      retention_period: int = 365) -> str:
        """Record user consent"""
        consent_id = f"consent_{user_id}_{consent_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check if consent already exists
        existing_consent = self.get_active_consent(user_id, consent_type)
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=consent_text,
            purpose=purpose,
            legal_basis=legal_basis,
            retention_period=retention_period
        )
        
        self.consent_records[consent_id] = consent_record
        
        # Log consent event
        self.audit_logger.log_compliance_event(
            event_type=AuditEventType.GDPR_REQUEST,
            framework="gdpr",
            user_id=user_id,
            details={
                "action": "consent_recorded",
                "consent_type": consent_type.value,
                "granted": granted,
                "purpose": purpose
            }
        )
        
        return consent_id
    
    def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Withdraw user consent"""
        active_consent = self.get_active_consent(user_id, consent_type)
        
        if active_consent and active_consent.granted:
            active_consent.withdrawn_at = datetime.now()
            
            # Log consent withdrawal
            self.audit_logger.log_compliance_event(
                event_type=AuditEventType.GDPR_REQUEST,
                framework="gdpr",
                user_id=user_id,
                details={
                    "action": "consent_withdrawn",
                    "consent_type": consent_type.value,
                    "consent_id": active_consent.consent_id
                }
            )
            
            return True
        
        return False
    
    def get_active_consent(self, user_id: str, consent_type: ConsentType) -> Optional[ConsentRecord]:
        """Get active consent for user and type"""
        user_consents = [c for c in self.consent_records.values() 
                        if c.user_id == user_id and c.consent_type == consent_type]
        
        # Sort by timestamp (most recent first)
        user_consents.sort(key=lambda x: x.timestamp, reverse=True)
        
        for consent in user_consents:
            if consent.granted and (consent.withdrawn_at is None):
                return consent
        
        return None
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has given consent for specific type"""
        consent = self.get_active_consent(user_id, consent_type)
        return consent is not None and consent.granted
    
    def create_data_subject_request(self, 
                                   user_id: str,
                                   request_type: DataSubjectRequestType,
                                   description: str,
                                   evidence: List[str] = None) -> str:
        """Create data subject request"""
        request_id = f"dsr_{user_id}_{request_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate due date (30 days from creation)
        due_date = datetime.now() + timedelta(days=30)
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type=request_type,
            description=description,
            status=RequestStatus.PENDING,
            created_at=datetime.now(),
            due_date=due_date,
            metadata={"evidence": evidence or []}
        )
        
        self.data_subject_requests[request_id] = request
        
        # Log DSR creation
        self.audit_logger.log_compliance_event(
            event_type=AuditEventType.GDPR_REQUEST,
            framework="gdpr",
            user_id=user_id,
            details={
                "action": "dsr_created",
                "request_type": request_type.value,
                "request_id": request_id,
                "due_date": due_date.isoformat()
            }
        )
        
        return request_id
    
    def get_data_subject_request(self, request_id: str) -> Optional[DataSubjectRequest]:
        """Get data subject request by ID"""
        return self.data_subject_requests.get(request_id)
    
    def update_request_status(self, request_id: str, status: RequestStatus, notes: str = None) -> bool:
        """Update data subject request status"""
        request = self.get_data_subject_request(request_id)
        if not request:
            return False
        
        old_status = request.status
        request.status = status
        
        if notes:
            request.notes.append(f"{datetime.now().isoformat()}: {notes}")
        
        if status == RequestStatus.COMPLETED:
            request.completed_at = datetime.now()
        
        # Log status update
        self.audit_logger.log_compliance_event(
            event_type=AuditEventType.GDPR_REQUEST,
            framework="gdpr",
            user_id=request.user_id,
            details={
                "action": "dsr_status_updated",
                "request_id": request_id,
                "old_status": old_status.value,
                "new_status": status.value,
                "notes": notes
            }
        )
        
        return True
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get all data for data subject access request"""
        user_data = {
            "user_id": user_id,
            "consent_records": [],
            "data_subject_requests": [],
            "processing_activities": [],
            "export_date": datetime.now().isoformat()
        }
        
        # Get consent records
        user_consents = [c for c in self.consent_records.values() if c.user_id == user_id]
        for consent in user_consents:
            user_data["consent_records"].append({
                "consent_id": consent.consent_id,
                "consent_type": consent.consent_type.value,
                "granted": consent.granted,
                "timestamp": consent.timestamp.isoformat(),
                "purpose": consent.purpose,
                "legal_basis": consent.legal_basis,
                "withdrawn_at": consent.withdrawn_at.isoformat() if consent.withdrawn_at else None
            })
        
        # Get data subject requests
        user_dsrs = [dsr for dsr in self.data_subject_requests.values() if dsr.user_id == user_id]
        for dsr in user_dsrs:
            user_data["data_subject_requests"].append({
                "request_id": dsr.request_id,
                "request_type": dsr.request_type.value,
                "status": dsr.status.value,
                "created_at": dsr.created_at.isoformat(),
                "due_date": dsr.due_date.isoformat(),
                "completed_at": dsr.completed_at.isoformat() if dsr.completed_at else None
            })
        
        # Get processing activities
        user_data["processing_activities"] = [
            {
                "record_id": record.record_id,
                "purpose": record.purpose,
                "data_categories": record.data_categories,
                "retention_period": record.retention_period,
                "legal_basis": record.legal_basis
            }
            for record in self.processing_records.values()
        ]
        
        return user_data
    
    def erase_user_data(self, user_id: str, reason: str = None) -> bool:
        """Erase user data (right to be forgotten)"""
        try:
            # Anonymize consent records
            for consent in self.consent_records.values():
                if consent.user_id == user_id:
                    consent.user_id = hashlib.sha256(f"erased_{consent.user_id}".encode()).hexdigest()
                    consent.metadata["erased_at"] = datetime.now().isoformat()
                    consent.metadata["erasure_reason"] = reason
            
            # Anonymize data subject requests
            for dsr in self.data_subject_requests.values():
                if dsr.user_id == user_id:
                    dsr.user_id = hashlib.sha256(f"erased_{dsr.user_id}".encode()).hexdigest()
                    dsr.metadata["erased_at"] = datetime.now().isoformat()
                    dsr.metadata["erasure_reason"] = reason
            
            # Log data erasure
            self.audit_logger.log_compliance_event(
                event_type=AuditEventType.GDPR_REQUEST,
                framework="gdpr",
                user_id=user_id,
                details={
                    "action": "data_erased",
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to erase user data: {e}")
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def anonymize_data(self, data: Dict[str, Any], fields_to_anonymize: List[str]) -> Dict[str, Any]:
        """Anonymize specified fields in data"""
        anonymized_data = data.copy()
        
        for field in fields_to_anonymize:
            if field in anonymized_data:
                value = str(anonymized_data[field])
                # Hash the value for anonymization
                anonymized_value = hashlib.sha256(f"anon_{value}".encode()).hexdigest()
                anonymized_data[field] = f"anon_{anonymized_value[:8]}"
        
        return anonymized_data
    
    def get_data_retention_report(self) -> Dict[str, Any]:
        """Get data retention report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "consent_records": {},
            "data_subject_requests": {},
            "recommendations": []
        }
        
        # Analyze consent records retention
        consent_by_type = {}
        for consent in self.consent_records.values():
            consent_type = consent.consent_type.value
            if consent_type not in consent_by_type:
                consent_by_type[consent_type] = []
            consent_by_type[consent_type].append(consent)
        
        for consent_type, consents in consent_by_type.items():
            expired_count = 0
            for consent in consents:
                expiry_date = consent.timestamp + timedelta(days=consent.retention_period)
                if datetime.now() > expiry_date:
                    expired_count += 1
            
            report["consent_records"][consent_type] = {
                "total": len(consents),
                "expired": expired_count,
                "retention_period_days": consents[0].retention_period if consents else 0
            }
        
        # Analyze DSR retention
        dsr_by_status = {}
        for dsr in self.data_subject_requests.values():
            status = dsr.status.value
            if status not in dsr_by_status:
                dsr_by_status[status] = []
            dsr_by_status[status].append(dsr)
        
        for status, dsrs in dsr_by_status.items():
            report["data_subject_requests"][status] = {
                "total": len(dsrs),
                "average_completion_days": self._calculate_average_completion_days(dsrs)
            }
        
        # Generate recommendations
        if any(expired > 0 for expired in [data["expired"] for data in report["consent_records"].values()]):
            report["recommendations"].append("Clean up expired consent records")
        
        pending_dsrs = report["data_subject_requests"].get("pending", {}).get("total", 0)
        if pending_dsrs > 0:
            report["recommendations"].append(f"Process {pending_dsrs} pending data subject requests")
        
        return report
    
    def _calculate_average_completion_days(self, dsrs: List[DataSubjectRequest]) -> float:
        """Calculate average completion time for DSRs"""
        completed_dsrs = [dsr for dsr in dsrs if dsr.completed_at]
        
        if not completed_dsrs:
            return 0.0
        
        total_days = sum((dsr.completed_at - dsr.created_at).days for dsr in completed_dsrs)
        return total_days / len(completed_dsrs)
    
    def export_user_data_portability(self, user_id: str, format: str = "json") -> Dict[str, Any]:
        """Export user data in portable format"""
        user_data = self.get_user_data(user_id)
        
        if format == "json":
            return user_data
        elif format == "csv":
            # Convert to CSV format (simplified)
            return {
                "format": "csv",
                "data": self._convert_to_csv(user_data)
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> List[str]:
        """Convert data to CSV format"""
        csv_lines = []
        
        # Add header
        csv_lines.append("Type,ID,Timestamp,Details")
        
        # Add consent records
        for consent in data.get("consent_records", []):
            csv_lines.append(f"Consent,{consent['consent_id']},{consent['timestamp']},{consent['purpose']}")
        
        # Add data subject requests
        for dsr in data.get("data_subject_requests", []):
            csv_lines.append(f"DSR,{dsr['request_id']},{dsr['created_at']},{dsr['request_type']}")
        
        return csv_lines
    
    def get_privacy_dashboard(self) -> Dict[str, Any]:
        """Get privacy management dashboard"""
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "consent_summary": {},
            "dsr_summary": {},
            "compliance_metrics": {}
        }
        
        # Consent summary
        total_consents = len(self.consent_records)
        active_consents = len([c for c in self.consent_records.values() if c.granted and not c.withdrawn_at])
        
        dashboard["consent_summary"] = {
            "total_consents": total_consents,
            "active_consents": active_consents,
            "withdrawn_consents": total_consents - active_consents,
            "consent_by_type": {}
        }
        
        for consent_type in ConsentType:
            type_consents = [c for c in self.consent_records.values() if c.consent_type == consent_type]
            active_type_consents = [c for c in type_consents if c.granted and not c.withdrawn_at]
            
            dashboard["consent_summary"]["consent_by_type"][consent_type.value] = {
                "total": len(type_consents),
                "active": len(active_type_consents)
            }
        
        # DSR summary
        total_dsrs = len(self.data_subject_requests)
        pending_dsrs = len([dsr for dsr in self.data_subject_requests.values() if dsr.status == RequestStatus.PENDING])
        overdue_dsrs = len([dsr for dsr in self.data_subject_requests.values() 
                           if dsr.status in [RequestStatus.PENDING, RequestStatus.IN_PROGRESS] 
                           and datetime.now() > dsr.due_date])
        
        dashboard["dsr_summary"] = {
            "total_requests": total_dsrs,
            "pending_requests": pending_dsrs,
            "overdue_requests": overdue_dsrs,
            "completed_requests": len([dsr for dsr in self.data_subject_requests.values() 
                                      if dsr.status == RequestStatus.COMPLETED])
        }
        
        # Compliance metrics
        dashboard["compliance_metrics"] = {
            "average_dsr_completion_days": self._calculate_average_completion_days(
                [dsr for dsr in self.data_subject_requests.values() if dsr.completed_at]
            ),
            "consent_coverage": (active_consents / total_consents * 100) if total_consents > 0 else 0,
            "dsr_completion_rate": (len([dsr for dsr in self.data_subject_requests.values() 
                                       if dsr.status == RequestStatus.COMPLETED]) / total_dsrs * 100) if total_dsrs > 0 else 0
        }
        
        return dashboard


# Global instance
data_protection = DataProtectionManager()
