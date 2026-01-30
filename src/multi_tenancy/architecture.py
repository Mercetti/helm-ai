"""
Multi-Tenancy Architecture for Helm AI
====================================

This module provides comprehensive multi-tenancy capabilities:
- Tenant isolation and separation
- Resource management and allocation
- Tenant-specific configurations
- Data segregation and security
- Billing and subscription management
- Tenant onboarding and provisioning
- Performance monitoring and scaling
- Compliance and governance
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("multi_tenancy")


class TenantStatus(str, Enum):
    """Tenant status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"
    TRIAL = "trial"


class TenantTier(str, Enum):
    """Tenant subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ResourceType(str, Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    USERS = "users"
    DATABASES = "databases"
    APPLICATIONS = "applications"


class IsolationLevel(str, Enum):
    """Data isolation levels"""
    SHARED_DATABASE = "shared_database"
    SCHEMA_ISOLATION = "schema_isolation"
    DATABASE_ISOLATION = "database_isolation"
    CONTAINER_ISOLATION = "container_isolation"
    VM_ISOLATION = "vm_isolation"


@dataclass
class TenantResource:
    """Tenant resource allocation"""
    id: str
    tenant_id: str
    resource_type: ResourceType
    allocated: float
    used: float = 0.0
    unit: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TenantConfiguration:
    """Tenant-specific configuration"""
    id: str
    tenant_id: str
    key: str
    value: Any
    category: str = "general"
    encrypted: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tenant:
    """Tenant definition"""
    id: str
    name: str
    domain: str
    tier: TenantTier
    status: TenantStatus
    isolation_level: IsolationLevel
    owner_id: str
    billing_account_id: Optional[str] = None
    max_users: int = 10
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    trial_ends_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantUser:
    """Tenant user association"""
    id: str
    tenant_id: str
    user_id: str
    role: str = "user"
    permissions: List[str] = field(default_factory=list)
    invited_at: datetime = field(default_factory=datetime.utcnow)
    joined_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    active: bool = True


@dataclass
class TenantUsage:
    """Tenant usage statistics"""
    id: str
    tenant_id: str
    resource_type: ResourceType
    usage_value: float
    period_start: datetime
    period_end: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


class MultiTenancyManager:
    """Multi-Tenancy Architecture Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.tenants: Dict[str, Tenant] = {}
        self.resources: Dict[str, TenantResource] = {}
        self.configurations: Dict[str, TenantConfiguration] = {}
        self.users: Dict[str, TenantUser] = {}
        self.usage: Dict[str, TenantUsage] = {}
        
        # Initialize default tier configurations
        self._initialize_tier_configs()
        
        logger.info("Multi-Tenancy Manager initialized")
    
    def _initialize_tier_configs(self):
        """Initialize default tier configurations"""
        self.tier_configs = {
            TenantTier.FREE: {
                "max_users": 5,
                "cpu_cores": 2,
                "memory_gb": 4,
                "storage_gb": 10,
                "bandwidth_gb": 100,
                "api_calls_per_day": 1000,
                "databases": 1,
                "applications": 1,
                "isolation_level": IsolationLevel.SHARED_DATABASE
            },
            TenantTier.BASIC: {
                "max_users": 25,
                "cpu_cores": 4,
                "memory_gb": 8,
                "storage_gb": 50,
                "bandwidth_gb": 500,
                "api_calls_per_day": 10000,
                "databases": 2,
                "applications": 3,
                "isolation_level": IsolationLevel.SCHEMA_ISOLATION
            },
            TenantTier.PROFESSIONAL: {
                "max_users": 100,
                "cpu_cores": 8,
                "memory_gb": 16,
                "storage_gb": 200,
                "bandwidth_gb": 2000,
                "api_calls_per_day": 100000,
                "databases": 5,
                "applications": 10,
                "isolation_level": IsolationLevel.DATABASE_ISOLATION
            },
            TenantTier.ENTERPRISE: {
                "max_users": -1,  # Unlimited
                "cpu_cores": 32,
                "memory_gb": 64,
                "storage_gb": 1000,
                "bandwidth_gb": 10000,
                "api_calls_per_day": -1,  # Unlimited
                "databases": -1,  # Unlimited
                "applications": -1,  # Unlimited
                "isolation_level": IsolationLevel.CONTAINER_ISOLATION
            },
            TenantTier.CUSTOM: {
                "max_users": -1,
                "cpu_cores": 64,
                "memory_gb": 128,
                "storage_gb": 5000,
                "bandwidth_gb": 50000,
                "api_calls_per_day": -1,
                "databases": -1,
                "applications": -1,
                "isolation_level": IsolationLevel.VM_ISOLATION
            }
        }
    
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Tenant:
        """Create a new tenant"""
        try:
            tenant = Tenant(
                id=str(uuid.uuid4()),
                name=tenant_data.get("name", ""),
                domain=tenant_data.get("domain", ""),
                tier=TenantTier(tenant_data.get("tier", "basic")),
                status=TenantStatus.PENDING,
                isolation_level=IsolationLevel(tenant_data.get("isolation_level", "shared_database")),
                owner_id=tenant_data.get("owner_id", ""),
                billing_account_id=tenant_data.get("billing_account_id"),
                trial_ends_at=datetime.utcnow() + timedelta(days=30) if tenant_data.get("trial", False) else None,
                metadata=tenant_data.get("metadata", {})
            )
            
            # Store tenant
            self.tenants[tenant.id] = tenant
            
            # Allocate resources based on tier
            self._allocate_tenant_resources(tenant)
            
            # Create default configurations
            self._create_default_configurations(tenant)
            
            # Add owner as tenant user
            self._add_tenant_user(tenant.id, tenant.owner_id, "owner", ["admin", "billing", "users"])
            
            # Provision infrastructure
            self._provision_tenant_infrastructure(tenant)
            
            # Update status to active
            tenant.status = TenantStatus.ACTIVE
            tenant.updated_at = datetime.utcnow()
            
            logger.info(f"Tenant created: {tenant.id}")
            return tenant
            
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
            raise
    
    def _allocate_tenant_resources(self, tenant: Tenant):
        """Allocate resources to tenant based on tier"""
        try:
            tier_config = self.tier_configs[tenant.tier]
            
            resource_allocations = [
                (ResourceType.CPU, tier_config["cpu_cores"], "cores"),
                (ResourceType.MEMORY, tier_config["memory_gb"], "GB"),
                (ResourceType.STORAGE, tier_config["storage_gb"], "GB"),
                (ResourceType.BANDWIDTH, tier_config["bandwidth_gb"], "GB"),
                (ResourceType.API_CALLS, tier_config["api_calls_per_day"], "calls/day"),
                (ResourceType.USERS, tier_config["max_users"], "users"),
                (ResourceType.DATABASES, tier_config["databases"], "databases"),
                (ResourceType.APPLICATIONS, tier_config["applications"], "applications")
            ]
            
            for resource_type, allocated, unit in resource_allocations:
                if allocated > 0:  # Skip unlimited (-1) resources for now
                    resource = TenantResource(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant.id,
                        resource_type=resource_type,
                        allocated=allocated,
                        unit=unit
                    )
                    self.resources[resource.id] = resource
            
            logger.info(f"Resources allocated for tenant {tenant.id}")
            
        except Exception as e:
            logger.error(f"Resource allocation failed for tenant {tenant.id}: {e}")
            raise
    
    def _create_default_configurations(self, tenant: Tenant):
        """Create default tenant configurations"""
        try:
            default_configs = [
                ("company_name", tenant.name, "general"),
                ("domain", tenant.domain, "general"),
                ("timezone", "UTC", "general"),
                ("language", "en", "general"),
                ("theme", "default", "ui"),
                ("logo_url", "", "branding"),
                ("primary_color", "#1976d2", "branding"),
                ("email_notifications", True, "notifications"),
                ("sms_notifications", False, "notifications"),
                ("backup_enabled", True, "security"),
                ("two_factor_auth", False, "security"),
                ("session_timeout", 3600, "security"),
                ("api_rate_limit", 1000, "api"),
                ("webhook_url", "", "integrations"),
                ("slack_webhook", "", "integrations")
            ]
            
            for key, value, category in default_configs:
                config = TenantConfiguration(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    key=key,
                    value=value,
                    category=category,
                    encrypted=False
                )
                self.configurations[config.id] = config
            
            logger.info(f"Default configurations created for tenant {tenant.id}")
            
        except Exception as e:
            logger.error(f"Default configuration creation failed for tenant {tenant.id}: {e}")
            raise
    
    def _add_tenant_user(self, tenant_id: str, user_id: str, role: str, permissions: List[str]):
        """Add user to tenant"""
        try:
            tenant_user = TenantUser(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
                permissions=permissions,
                joined_at=datetime.utcnow()
            )
            
            self.users[tenant_user.id] = tenant_user
            logger.info(f"User {user_id} added to tenant {tenant_id} with role {role}")
            
        except Exception as e:
            logger.error(f"Failed to add user to tenant: {e}")
            raise
    
    def _provision_tenant_infrastructure(self, tenant: Tenant):
        """Provision infrastructure for tenant"""
        try:
            # Simulate infrastructure provisioning based on isolation level
            provisioning_steps = []
            
            if tenant.isolation_level == IsolationLevel.SHARED_DATABASE:
                provisioning_steps = [
                    "Create tenant schema in shared database",
                    "Set up row-level security policies",
                    "Create tenant-specific views",
                    "Configure connection pooling"
                ]
            elif tenant.isolation_level == IsolationLevel.SCHEMA_ISOLATION:
                provisioning_steps = [
                    "Create dedicated database schema",
                    "Set up schema-level permissions",
                    "Create tenant-specific tables",
                    "Configure schema isolation"
                ]
            elif tenant.isolation_level == IsolationLevel.DATABASE_ISOLATION:
                provisioning_steps = [
                    "Create dedicated database",
                    "Set up database-level security",
                    "Create tenant-specific users",
                    "Configure database backups"
                ]
            elif tenant.isolation_level == IsolationLevel.CONTAINER_ISOLATION:
                provisioning_steps = [
                    "Provision dedicated container",
                    "Set up container networking",
                    "Configure container security",
                    "Deploy tenant application"
                ]
            elif tenant.isolation_level == IsolationLevel.VM_ISOLATION:
                provisioning_steps = [
                    "Provision dedicated virtual machine",
                    "Set up VM networking and storage",
                    "Configure VM security groups",
                    "Deploy full tenant stack"
                ]
            
            # Simulate provisioning execution
            for step in provisioning_steps:
                # In real implementation, this would execute actual provisioning
                logger.info(f"Provisioning step: {step} for tenant {tenant.id}")
            
            logger.info(f"Infrastructure provisioned for tenant {tenant.id}")
            
        except Exception as e:
            logger.error(f"Infrastructure provisioning failed for tenant {tenant.id}: {e}")
            raise
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant information"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            
            # Update allowed fields
            if "name" in updates:
                tenant.name = updates["name"]
            if "domain" in updates:
                tenant.domain = updates["domain"]
            if "tier" in updates:
                old_tier = tenant.tier
                tenant.tier = TenantTier(updates["tier"])
                # Reallocate resources if tier changed
                if old_tier != tenant.tier:
                    self._reallocate_tenant_resources(tenant)
            if "status" in updates:
                tenant.status = TenantStatus(updates["status"])
            if "metadata" in updates:
                tenant.metadata.update(updates["metadata"])
            
            tenant.updated_at = datetime.utcnow()
            
            logger.info(f"Tenant {tenant_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update tenant {tenant_id}: {e}")
            return False
    
    def _reallocate_tenant_resources(self, tenant: Tenant):
        """Reallocate resources when tenant tier changes"""
        try:
            # Remove existing resources
            existing_resources = [r for r in self.resources.values() if r.tenant_id == tenant.id]
            for resource in existing_resources:
                del self.resources[resource.id]
            
            # Allocate new resources based on new tier
            self._allocate_tenant_resources(tenant)
            
            logger.info(f"Resources reallocated for tenant {tenant.id} due to tier change")
            
        except Exception as e:
            logger.error(f"Resource reallocation failed for tenant {tenant.id}: {e}")
            raise
    
    def add_tenant_user(self, tenant_id: str, user_id: str, role: str = "user", 
                       permissions: List[str] = None) -> bool:
        """Add user to tenant"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            # Check if user already exists in tenant
            existing_user = next((u for u in self.users.values() 
                                if u.tenant_id == tenant_id and u.user_id == user_id), None)
            if existing_user:
                return False
            
            # Check tenant user limits
            tenant = self.tenants[tenant_id]
            tier_config = self.tier_configs[tenant.tier]
            max_users = tier_config["max_users"]
            
            if max_users > 0:  # -1 means unlimited
                current_users = len([u for u in self.users.values() if u.tenant_id == tenant_id])
                if current_users >= max_users:
                    return False
            
            # Add user with default permissions if not specified
            if permissions is None:
                permissions = ["read", "write"] if role == "admin" else ["read"]
            
            self._add_tenant_user(tenant_id, user_id, role, permissions)
            
            logger.info(f"User {user_id} added to tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add user to tenant: {e}")
            return False
    
    def remove_tenant_user(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant"""
        try:
            # Find and remove user
            tenant_user = next((u for u in self.users.values() 
                              if u.tenant_id == tenant_id and u.user_id == user_id), None)
            
            if tenant_user:
                del self.users[tenant_user.id]
                logger.info(f"User {user_id} removed from tenant {tenant_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove user from tenant: {e}")
            return False
    
    def update_tenant_configuration(self, tenant_id: str, key: str, value: Any, 
                                  category: str = "general", encrypted: bool = False) -> bool:
        """Update tenant configuration"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            # Find existing configuration
            existing_config = next((c for c in self.configurations.values() 
                                   if c.tenant_id == tenant_id and c.key == key), None)
            
            if existing_config:
                existing_config.value = value
                existing_config.updated_at = datetime.utcnow()
            else:
                # Create new configuration
                config = TenantConfiguration(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    key=key,
                    value=value,
                    category=category,
                    encrypted=encrypted
                )
                self.configurations[config.id] = config
            
            logger.info(f"Configuration {key} updated for tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update tenant configuration: {e}")
            return False
    
    def get_tenant_configuration(self, tenant_id: str, key: str) -> Optional[Any]:
        """Get tenant configuration value"""
        try:
            config = next((c for c in self.configurations.values() 
                          if c.tenant_id == tenant_id and c.key == key), None)
            
            return config.value if config else None
            
        except Exception as e:
            logger.error(f"Failed to get tenant configuration: {e}")
            return None
    
    def record_resource_usage(self, tenant_id: str, resource_type: ResourceType, 
                            usage_value: float, period_start: datetime, period_end: datetime):
        """Record resource usage for tenant"""
        try:
            usage = TenantUsage(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                resource_type=resource_type,
                usage_value=usage_value,
                period_start=period_start,
                period_end=period_end
            )
            
            self.usage[usage.id] = usage
            
            # Update resource usage
            resource = next((r for r in self.resources.values() 
                           if r.tenant_id == tenant_id and r.resource_type == resource_type), None)
            
            if resource:
                resource.used = usage_value
                resource.updated_at = datetime.utcnow()
            
            logger.info(f"Usage recorded for tenant {tenant_id}, resource {resource_type}: {usage_value}")
            
        except Exception as e:
            logger.error(f"Failed to record resource usage: {e}")
            raise
    
    def get_tenant_usage(self, tenant_id: str, resource_type: Optional[ResourceType] = None,
                        period_start: Optional[datetime] = None, period_end: Optional[datetime] = None) -> List[TenantUsage]:
        """Get tenant usage statistics"""
        try:
            usage_records = [u for u in self.usage.values() if u.tenant_id == tenant_id]
            
            if resource_type:
                usage_records = [u for u in usage_records if u.resource_type == resource_type]
            
            if period_start:
                usage_records = [u for u in usage_records if u.period_start >= period_start]
            
            if period_end:
                usage_records = [u for u in usage_records if u.period_end <= period_end]
            
            return usage_records
            
        except Exception as e:
            logger.error(f"Failed to get tenant usage: {e}")
            return []
    
    def get_tenant_resources(self, tenant_id: str) -> List[TenantResource]:
        """Get tenant resource allocations"""
        try:
            return [r for r in self.resources.values() if r.tenant_id == tenant_id]
        except Exception as e:
            logger.error(f"Failed to get tenant resources: {e}")
            return []
    
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get tenant users"""
        try:
            return [u for u in self.users.values() if u.tenant_id == tenant_id]
        except Exception as e:
            logger.error(f"Failed to get tenant users: {e}")
            return []
    
    def check_resource_limits(self, tenant_id: str, resource_type: ResourceType, 
                             requested_amount: float) -> Tuple[bool, str]:
        """Check if tenant has sufficient resource allocation"""
        try:
            resource = next((r for r in self.resources.values() 
                           if r.tenant_id == tenant_id and r.resource_type == resource_type), None)
            
            if not resource:
                return False, f"Resource {resource_type} not allocated to tenant"
            
            if resource.allocated > 0 and resource.used + requested_amount > resource.allocated:
                return False, f"Resource limit exceeded: {resource.used + requested_amount}/{resource.allocated} {resource.unit}"
            
            return True, "Resource allocation sufficient"
            
        except Exception as e:
            logger.error(f"Failed to check resource limits: {e}")
            return False, f"Error checking resource limits: {str(e)}"
    
    def upgrade_tenant_tier(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to a higher tier"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            current_tier = tenant.tier
            
            # Check if this is actually an upgrade
            tier_order = [TenantTier.FREE, TenantTier.BASIC, TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE, TenantTier.CUSTOM]
            if tier_order.index(new_tier) <= tier_order.index(current_tier):
                return False
            
            # Update tenant tier
            tenant.tier = new_tier
            tenant.updated_at = datetime.utcnow()
            
            # Reallocate resources
            self._reallocate_tenant_resources(tenant)
            
            logger.info(f"Tenant {tenant_id} upgraded from {current_tier} to {new_tier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upgrade tenant tier: {e}")
            return False
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend tenant"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.SUSPENDED
            tenant.updated_at = datetime.utcnow()
            
            if reason:
                tenant.metadata["suspension_reason"] = reason
            
            # In real implementation, this would also suspend services
            logger.info(f"Tenant {tenant_id} suspended: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to suspend tenant: {e}")
            return False
    
    def terminate_tenant(self, tenant_id: str) -> bool:
        """Terminate tenant and clean up resources"""
        try:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.TERMINATED
            tenant.updated_at = datetime.utcnow()
            
            # Clean up resources
            tenant_resources = [r for r in self.resources.values() if r.tenant_id == tenant_id]
            for resource in tenant_resources:
                del self.resources[resource.id]
            
            # Clean up configurations
            tenant_configs = [c for c in self.configurations.values() if c.tenant_id == tenant_id]
            for config in tenant_configs:
                del self.configurations[config.id]
            
            # Clean up users
            tenant_users = [u for u in self.users.values() if u.tenant_id == tenant_id]
            for user in tenant_users:
                del self.users[user.id]
            
            # Clean up usage records
            tenant_usage = [u for u in self.usage.values() if u.tenant_id == tenant_id]
            for usage in tenant_usage:
                del self.usage[usage.id]
            
            # In real implementation, this would also deprovision infrastructure
            logger.info(f"Tenant {tenant_id} terminated and resources cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate tenant: {e}")
            return False
    
    def get_multi_tenant_dashboard(self) -> Dict[str, Any]:
        """Get multi-tenant dashboard data"""
        try:
            dashboard = {
                "tenant_stats": {},
                "tier_distribution": {},
                "resource_utilization": {},
                "recent_activity": [],
                "system_health": {}
            }
            
            # Tenant statistics
            total_tenants = len(self.tenants)
            tenants_by_status = defaultdict(int)
            tenants_by_tier = defaultdict(int)
            
            for tenant in self.tenants.values():
                tenants_by_status[tenant.status.value] += 1
                tenants_by_tier[tenant.tier.value] += 1
            
            dashboard["tenant_stats"] = {
                "total": total_tenants,
                "by_status": dict(tenants_by_status),
                "by_tier": dict(tenants_by_tier)
            }
            
            # Tier distribution
            dashboard["tier_distribution"] = dict(tenants_by_tier)
            
            # Resource utilization
            resource_utilization = defaultdict(lambda: {"allocated": 0, "used": 0})
            for resource in self.resources.values():
                resource_utilization[resource.resource_type.value]["allocated"] += resource.allocated
                resource_utilization[resource.resource_type.value]["used"] += resource.used
            
            # Calculate utilization percentages
            for resource_type, values in resource_utilization.items():
                if values["allocated"] > 0:
                    values["utilization_percent"] = (values["used"] / values["allocated"]) * 100
                else:
                    values["utilization_percent"] = 0
            
            dashboard["resource_utilization"] = dict(resource_utilization)
            
            # Recent activity (simulate recent tenant changes)
            recent_tenants = sorted(
                self.tenants.values(),
                key=lambda t: t.updated_at,
                reverse=True
            )[:10]
            
            dashboard["recent_activity"] = [
                {
                    "tenant_id": tenant.id,
                    "tenant_name": tenant.name,
                    "action": "updated",
                    "timestamp": tenant.updated_at.isoformat(),
                    "status": tenant.status.value
                }
                for tenant in recent_tenants
            ]
            
            # System health
            dashboard["system_health"] = {
                "total_resources": len(self.resources),
                "total_configurations": len(self.configurations),
                "total_users": len(self.users),
                "total_usage_records": len(self.usage),
                "system_uptime": datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_tenants": len(self.tenants),
            "total_resources": len(self.resources),
            "total_configurations": len(self.configurations),
            "total_users": len(self.users),
            "total_usage_records": len(self.usage),
            "supported_tiers": [t.value for t in TenantTier],
            "resource_types": [r.value for r in ResourceType],
            "isolation_levels": [i.value for i in IsolationLevel],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
MULTI_TENANCY_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "provisioning": {
        "auto_provision": True,
        "default_isolation": "schema_isolation",
        "backup_enabled": True
    },
    "monitoring": {
        "usage_tracking_interval": 3600,  # seconds
        "resource_alert_threshold": 0.8
    }
}


# Initialize multi-tenancy manager
multi_tenancy_manager = MultiTenancyManager(MULTI_TENANCY_CONFIG)

# Export main components
__all__ = [
    'MultiTenancyManager',
    'Tenant',
    'TenantResource',
    'TenantConfiguration',
    'TenantUser',
    'TenantUsage',
    'TenantStatus',
    'TenantTier',
    'ResourceType',
    'IsolationLevel',
    'multi_tenancy_manager'
]
