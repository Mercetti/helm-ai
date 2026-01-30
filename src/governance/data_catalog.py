"""
Helm AI Data Governance and Catalog System
Provides comprehensive data governance, cataloging, and compliance management
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from decimal import Decimal

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class DataClassification(Enum):
    """Data classification enumeration"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SENSITIVE = "sensitive"

class DataCategory(Enum):
    """Data category enumeration"""
    PERSONAL = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    LOG = "log"
    CONFIGURATION = "configuration"
    METADATA = "metadata"

class DataQualityLevel(Enum):
    """Data quality level enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

class RetentionPolicy(Enum):
    """Retention policy enumeration"""
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    PERMANENT = "permanent"
    CUSTOM = "custom"

class AccessLevel(Enum):
    """Access level enumeration"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class DataAsset:
    """Data asset definition"""
    asset_id: str
    name: str
    description: str
    data_type: str
    classification: DataClassification
    category: DataCategory
    owner_id: str
    steward_id: str
    location: str
    source_system: str
    format: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime]
    retention_policy: RetentionPolicyPolicy
    quality_level: DataQualityLevel
    tags: Set[str]
    metadata: Dict[str, Any]
    schema: Dict[str, Any]
    lineage: List[str]
    dependencies: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary"""
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'description': self.description,
            'data_type': self.data_type,
            'classification': self.classification.value,
            'category': self.category.value,
            'owner_id': self.owner_id,
            'steward_id': self.steward_id,
            'location': self.location,
            'source_system': self.source_system,
            'format': self.format,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'retention_policy': self.retention_policy.to_dict() if self.retention_policy else None,
            'quality_level': self.quality_level.value,
            'tags': list(self.tags),
            'metadata': self.metadata,
            'schema': self.schema,
            'lineage': self.lineage,
            'dependencies': self.dependencies
        }

@dataclass
class RetentionPolicyPolicy:
    """Retention policy definition"""
    policy_id: str
    name: str
    description: str
    retention_period_days: int
    archive_after_days: Optional[int]
    delete_after_days: Optional[int]
    auto_archive: bool
    auto_delete: bool
    conditions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary"""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'retention_period_days': self.retention_period_days,
            'archive_after_days': self.archive_after_days,
            'delete_after_days': self.delete_after_days,
            'auto_archive': self.auto_archive,
            'auto_delete': self.auto_delete,
            'conditions': self.conditions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class DataAccessRequest:
    """Data access request definition"""
    request_id: str
    asset_id: str
    requester_id: str
    requested_access: AccessLevel
    purpose: str
    duration_days: int
    status: str
    requested_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    approved_at: Optional[datetime]
    expires_at: Optional[datetime]
    justification: str
    conditions: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'request_id': self.request_id,
            'asset_id': self.asset_id,
            'requester_id': self.requester_id,
            'requested_access': self.requested_access.value,
            'purpose': self.purpose,
            'duration_days': self.duration_days,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'justification': self.justification,
            'conditions': self.conditions,
            'metadata': self.metadata
        }

@dataclass
class DataQualityAssessment:
    """Data quality assessment definition"""
    assessment_id: str
    asset_id: str
    assessed_by: str
    assessment_date: datetime
    quality_level: DataQualityLevel
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    timeliness_score: float
    validity_score: float
    overall_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    next_assessment_date: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary"""
        return {
            'assessment_id': self.assessment_id,
            'asset_id': self.asset_id,
            'assessed_by': self.assessed_by,
            'assessment_date': self.assessment_date.isoformat(),
            'quality_level': self.quality_level.value,
            'completeness_score': self.completeness_score,
            'accuracy_score': self.accuracy_score,
            'consistency_score': self.consistency_score,
            'timeliness_score': self.timeliness_score,
            'validity_score': self.validity_score,
            'overall_score': self.overall_score,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'next_assessment_date': self.next_assessment_date.isoformat(),
            'metadata': self.metadata
        }

class DataGovernanceSystem:
    """Data governance and catalog system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.data_assets: Dict[str, DataAsset] = {}
        self.retention_policies: Dict[str, RetentionPolicyPolicy] = {}
        self.access_requests: Dict[str, DataAccessRequest] = {}
        self.quality_assessments: Dict[str, DataQualityAssessment] = {}
        self.asset_lineage: Dict[str, Set[str]] = defaultdict(set)  # asset_id -> dependent asset_ids
        self.lock = threading.Lock()
        
        # Configuration
        self.default_retention_days = int(os.getenv('DEFAULT_RETENTION_DAYS', '2555'))  # 7 years
        self.max_request_duration = int(os.getenv('MAX_REQUEST_DURATION', '365'))  # 1 year
        self.quality_assessment_interval = int(os.getenv('QUALITY_ASSESSMENT_INTERVAL', '90'))  # 90 days
        
        # Initialize default retention policies
        self._initialize_default_policies()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default retention policies"""
        # Public Data Policy
        public_policy = RetentionPolicyPolicy(
            policy_id="public_data",
            name="Public Data Retention",
            description="Retention policy for public data",
            retention_period_days=365,  # 1 year
            archive_after_days=None,
            delete_after_days=365,
            auto_archive=False,
            auto_delete=True,
            conditions={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Internal Data Policy
        internal_policy = RetentionPolicyPolicy(
            policy_id="internal_data",
            name="Internal Data Retention",
            description="Retention policy for internal data",
            retention_period_days=1825,  # 5 years
            archive_after_days=365,
            delete_after_days=1825,
            auto_archive=True,
            auto_delete=True,
            conditions={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Confidential Data Policy
        confidential_policy = RetentionPolicyPolicy(
            policy_id="confidential_data",
            name="Confidential Data Retention",
            description="Retention policy for confidential data",
            retention_period_days=2555,  # 7 years
            archive_after_days=365,
            delete_after_days=None,  # Manual deletion only
            auto_archive=True,
            auto_delete=False,
            conditions={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Restricted Data Policy
        restricted_policy = RetentionPolicyPolicy(
            policy_id="restricted_data",
            name="Restricted Data Retention",
            description="Retention policy for restricted data",
            retention_period_days=3650,  # 10 years
            archive_after_days=90,
            delete_after_days=None,  # Manual deletion only
            auto_archive=True,
            auto_delete=False,
            conditions={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add policies
        self.retention_policies[public_policy.policy_id] = public_policy
        self.retention_policies[internal_policy.policy_id] = internal_policy
        self.retention_policies[confidential_policy.policy_id] = confidential_policy
        self.retention_policies[restricted_policy.policy_id] = restricted_policy
        
        logger.info(f"Initialized {len(self.retention_policies)} default retention policies")
    
    def register_data_asset(self, name: str, description: str, data_type: str,
                           classification: DataClassification, category: DataCategory,
                           owner_id: str, steward_id: str, location: str, source_system: str,
                           format: str, size_bytes: int, tags: Set[str],
                           schema: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> DataAsset:
        """Register new data asset"""
        asset_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Determine retention policy based on classification
        policy_id = self._get_retention_policy_for_classification(classification)
        retention_policy = self.retention_policies.get(policy_id)
        
        asset = DataAsset(
            asset_id=asset_id,
            name=name,
            description=description,
            data_type=data_type,
            classification=classification,
            category=category,
            owner_id=owner_id,
            steward_id=steward_id,
            location=location,
            source_system=source_system,
            format=format,
            size_bytes=size_bytes,
            created_at=now,
            updated_at=now,
            last_accessed=None,
            retention_policy=retention_policy,
            quality_level=DataQualityLevel.UNKNOWN,
            tags=tags,
            metadata=metadata or {},
            schema=schema,
            lineage=[],
            dependencies=[]
        )
        
        with self.lock:
            self.data_assets[asset_id] = asset
        
        logger.info(f"Registered data asset {asset_id} ({name})")
        
        return asset
    
    def _get_retention_policy_for_classification(self, classification: DataClassification) -> str:
        """Get retention policy ID for data classification"""
        policy_mapping = {
            DataClassification.PUBLIC: "public_data",
            DataClassification.INTERNAL: "internal_data",
            DataClassification.CONFIDENTIAL: "confidential_data",
            DataClassification.RESTRICTED: "restricted_data",
            DataClassification.SENSITIVE: "confidential_data"
        }
        return policy_mapping.get(classification, "internal_data")
    
    def update_data_asset(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """Update data asset"""
        with self.lock:
            if asset_id not in self.data_assets:
                return False
            
            asset = self.data_assets[asset_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(asset, key):
                    setattr(asset, key, value)
            
            asset.updated_at = datetime.utcnow()
            
            logger.info(f"Updated data asset {asset_id}")
            
            return True
    
    def add_data_lineage(self, asset_id: str, parent_asset_id: str) -> bool:
        """Add data lineage relationship"""
        with self.lock:
            if asset_id not in self.data_assets or parent_asset_id not in self.data_assets:
                return False
            
            # Add to asset lineage
            asset = self.data_assets[asset_id]
            if parent_asset_id not in asset.lineage:
                asset.lineage.append(parent_asset_id)
                asset.updated_at = datetime.utcnow()
            
            # Add to lineage tracking
            self.asset_lineage[parent_asset_id].add(asset_id)
            
            logger.info(f"Added lineage: {parent_asset_id} -> {asset_id}")
            
            return True
    
    def request_data_access(self, asset_id: str, requester_id: str, requested_access: AccessLevel,
                          purpose: str, duration_days: int, justification: str) -> DataAccessRequest:
        """Request data access"""
        with self.lock:
            if asset_id not in self.data_assets:
                raise ValueError(f"Data asset {asset_id} not found")
            
            if duration_days > self.max_request_duration:
                raise ValueError(f"Duration exceeds maximum of {self.max_request_duration} days")
        
        request_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        request = DataAccessRequest(
            request_id=request_id,
            asset_id=asset_id,
            requester_id=requester_id,
            requested_access=requested_access,
            purpose=purpose,
            duration_days=duration_days,
            status="pending",
            requested_at=now,
            reviewed_at=None,
            reviewed_by=None,
            approved_at=None,
            expires_at=None,
            justification=justification,
            conditions=[],
            metadata={}
        )
        
        with self.lock:
            self.access_requests[request_id] = request
        
        logger.info(f"Created access request {request_id} for asset {asset_id}")
        
        return request
    
    def approve_access_request(self, request_id: str, reviewer_id: str, conditions: List[str]) -> bool:
        """Approve access request"""
        with self.lock:
            if request_id not in self.access_requests:
                return False
            
            request = self.access_requests[request_id]
            
            if request.status != "pending":
                return False
            
            request.status = "approved"
            request.reviewed_at = datetime.utcnow()
            request.reviewed_by = reviewer_id
            request.approved_at = datetime.utcnow()
            request.expires_at = datetime.utcnow() + timedelta(days=request.duration_days)
            request.conditions = conditions
        
        logger.info(f"Approved access request {request_id} by {reviewer_id}")
        
        return True
    
    def deny_access_request(self, request_id: str, reviewer_id: str, reason: str) -> bool:
        """Deny access request"""
        with self.lock:
            if request_id not in self.access_requests:
                return False
            
            request = self.access_requests[request_id]
            
            if request.status != "pending":
                return False
            
            request.status = "denied"
            request.reviewed_at = datetime.utcnow()
            request.reviewed_by = reviewer_id
            request.metadata['denial_reason'] = reason
        
        logger.info(f"Denied access request {request_id} by {reviewer_id}: {reason}")
        
        return True
    
    def conduct_quality_assessment(self, asset_id: str, assessed_by: str,
                                 completeness_score: float, accuracy_score: float,
                                 consistency_score: float, timeliness_score: float,
                                 validity_score: float, issues: List[Dict[str, Any]],
                                 recommendations: List[str]) -> DataQualityAssessment:
        """Conduct data quality assessment"""
        with self.lock:
            if asset_id not in self.data_assets:
                raise ValueError(f"Data asset {asset_id} not found")
        
        assessment_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate overall score
        overall_score = (completeness_score + accuracy_score + consistency_score + 
                        timeliness_score + validity_score) / 5
        
        # Determine quality level
        if overall_score >= 0.9:
            quality_level = DataQualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            quality_level = DataQualityLevel.GOOD
        elif overall_score >= 0.6:
            quality_level = DataQualityLevel.FAIR
        elif overall_score >= 0.4:
            quality_level = DataQualityLevel.POOR
        else:
            quality_level = DataQualityLevel.UNKNOWN
        
        assessment = DataQualityAssessment(
            assessment_id=assessment_id,
            asset_id=asset_id,
            assessed_by=assessed_by,
            assessment_date=now,
            quality_level=quality_level,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            timeliness_score=timeliness_score,
            validity_score=validity_score,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            next_assessment_date=now + timedelta(days=self.quality_assessment_interval),
            metadata={}
        )
        
        with self.lock:
            self.quality_assessments[assessment_id] = assessment
            
            # Update asset quality level
            asset = self.data_assets[asset_id]
            asset.quality_level = quality_level
            asset.updated_at = now
        
        logger.info(f"Conducted quality assessment {assessment_id} for asset {asset_id}")
        
        return assessment
    
    def search_data_assets(self, query: str, classification: Optional[DataClassification] = None,
                         category: Optional[DataCategory] = None, tags: Optional[Set[str]] = None,
                         owner_id: Optional[str] = None, limit: Optional[int] = None) -> List[DataAsset]:
        """Search data assets"""
        with self.lock:
            assets = list(self.data_assets.values())
            
            # Apply filters
            if classification:
                assets = [a for a in assets if a.classification == classification]
            
            if category:
                assets = [a for a in assets if a.category == category]
            
            if tags:
                assets = [a for a in assets if tags.intersection(a.tags)]
            
            if owner_id:
                assets = [a for a in assets if a.owner_id == owner_id]
            
            # Apply text search
            if query:
                query_lower = query.lower()
                assets = [a for a in assets if 
                        query_lower in a.name.lower() or 
                        query_lower in a.description.lower() or
                        query_lower in a.data_type.lower()]
            
            # Sort by relevance (name match first, then description)
            assets.sort(key=lambda x: (
                query_lower in x.name.lower() if query else False,
                x.updated_at
            ), reverse=True)
            
            if limit:
                assets = assets[:limit]
            
            return assets
    
    def get_asset_lineage(self, asset_id: str) -> Dict[str, Any]:
        """Get asset lineage information"""
        with self.lock:
            if asset_id not in self.data_assets:
                return {}
            
            asset = self.data_assets[asset_id]
            
            # Get upstream lineage
            upstream = asset.lineage
            
            # Get downstream lineage
            downstream = list(self.asset_lineage.get(asset_id, set()))
            
            return {
                'asset_id': asset_id,
                'asset_name': asset.name,
                'upstream': upstream,
                'downstream': downstream,
                'total_dependencies': len(upstream) + len(downstream)
            }
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance system metrics"""
        with self.lock:
            total_assets = len(self.data_assets)
            
            # Classification distribution
            classification_distribution = defaultdict(int)
            for asset in self.data_assets.values():
                classification_distribution[asset.classification.value] += 1
            
            # Category distribution
            category_distribution = defaultdict(int)
            for asset in self.data_assets.values():
                category_distribution[asset.category.value] += 1
            
            # Quality distribution
            quality_distribution = defaultdict(int)
            for asset in self.data_assets.values():
                quality_distribution[asset.quality_level.value] += 1
            
            # Access request metrics
            total_requests = len(self.access_requests)
            pending_requests = len([r for r in self.access_requests.values() if r.status == "pending"])
            approved_requests = len([r for r in self.access_requests.values() if r.status == "approved"])
            denied_requests = len([r for r in self.access_requests.values() if r.status == "denied"])
            
            # Quality assessment metrics
            total_assessments = len(self.quality_assessments)
            recent_assessments = len([
                a for a in self.quality_assessments.values()
                if (datetime.utcnow() - a.assessment_date).days <= 30
            ])
            
            # Storage metrics
            total_storage = sum(asset.size_bytes for asset in self.data_assets.values())
            
            return {
                'data_assets': {
                    'total': total_assets,
                    'classification_distribution': dict(classification_distribution),
                    'category_distribution': dict(category_distribution),
                    'quality_distribution': dict(quality_distribution),
                    'total_storage_bytes': total_storage,
                    'total_storage_gb': round(total_storage / (1024**3), 2)
                },
                'access_requests': {
                    'total': total_requests,
                    'pending': pending_requests,
                    'approved': approved_requests,
                    'denied': denied_requests,
                    'approval_rate': (approved_requests / total_requests * 100) if total_requests > 0 else 0
                },
                'quality_assessments': {
                    'total': total_assessments,
                    'recent': recent_assessments,
                    'assessment_interval_days': self.quality_assessment_interval
                },
                'retention_policies': {
                    'total': len(self.retention_policies),
                    'active': len([p for p in self.retention_policies.values()])
                }
            }
    
    def _start_background_tasks(self) -> None:
        """Start background governance tasks"""
        # Start retention policy enforcement thread
        retention_thread = threading.Thread(target=self._enforce_retention_policies, daemon=True)
        retention_thread.start()
        
        # Start access request expiration thread
        expiration_thread = threading.Thread(target=self._expire_access_requests, daemon=True)
        expiration_thread.start()
        
        # Start quality assessment reminder thread
        quality_thread = threading.Thread(target=self._schedule_quality_assessments, daemon=True)
        quality_thread.start()
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
    
    def _enforce_retention_policies(self) -> None:
        """Enforce retention policies"""
        while True:
            try:
                now = datetime.utcnow()
                
                with self.lock:
                    for asset in self.data_assets.values():
                        if asset.retention_policy:
                            policy = asset.retention_policy
                            
                            # Check for archival
                            if (policy.auto_archive and policy.archive_after_days and
                                (now - asset.created_at).days >= policy.archive_after_days):
                                
                                # Archive asset (simulated)
                                logger.info(f"Archived asset {asset.asset_id} based on policy {policy.policy_id}")
                            
                            # Check for deletion
                            if (policy.auto_delete and policy.delete_after_days and
                                (now - asset.created_at).days >= policy.delete_after_days):
                                
                                # Delete asset (simulated)
                                logger.warning(f"Deleted asset {asset.asset_id} based on policy {policy.policy_id}")
                
                # Check every hour
                time.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Retention policy enforcement failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _expire_access_requests(self) -> None:
        """Expire access requests"""
        while True:
            try:
                now = datetime.utcnow()
                expired_requests = []
                
                with self.lock:
                    for request in self.access_requests.values():
                        if (request.status == "approved" and request.expires_at and
                            now >= request.expires_at):
                            
                            request.status = "expired"
                            expired_requests.append(request.request_id)
                
                if expired_requests:
                    logger.info(f"Expired {len(expired_requests)} access requests")
                
                # Check every hour
                time.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Access request expiration failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _schedule_quality_assessments(self) -> None:
        """Schedule quality assessments"""
        while True:
            try:
                now = datetime.utcnow()
                due_assessments = []
                
                with self.lock:
                    for assessment in self.quality_assessments.values():
                        if now >= assessment.next_assessment_date:
                            due_assessments.append(assessment.asset_id)
                
                if due_assessments:
                    logger.info(f"Quality assessments due for {len(due_assessments)} assets")
                    
                    # In production, this would trigger notifications or automated assessments
                
                # Check every day
                time.sleep(86400)  # 24 hours
                
            except Exception as e:
                logger.error(f"Quality assessment scheduling failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _collect_metrics(self) -> None:
        """Collect governance metrics"""
        while True:
            try:
                # Collect metrics every hour
                time.sleep(3600)  # 1 hour
                
                metrics = self.get_governance_metrics()
                logger.info(f"Data governance metrics: {metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(1800)  # Wait 30 minutes before retrying

# Global data governance system instance
data_governance_system = DataGovernanceSystem()

# Export main components
__all__ = [
    'DataGovernanceSystem',
    'DataAsset',
    'RetentionPolicyPolicy',
    'DataAccessRequest',
    'DataQualityAssessment',
    'DataClassification',
    'DataCategory',
    'DataQualityLevel',
    'RetentionPolicy',
    'AccessLevel',
    'data_governance_system'
]
