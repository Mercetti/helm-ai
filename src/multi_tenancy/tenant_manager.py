"""
Helm AI Multi-Tenancy Architecture
Provides comprehensive multi-tenant support with data isolation, resource management, and tenant-specific configurations
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
from contextlib import contextmanager

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class TenantStatus(Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TERMINATED = "terminated"

class TenantTier(Enum):
    """Tenant tier enumeration"""
    STARTUP = "startup"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class DataIsolationLevel(Enum):
    """Data isolation level enumeration"""
    SHARED_DATABASE = "shared_database"
    SCHEMA_ISOLATION = "schema_isolation"
    DATABASE_ISOLATION = "database_isolation"
    CONTAINER_ISOLATION = "container_isolation"

class ResourceType(Enum):
    """Resource type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    USERS = "users"
    CONNECTIONS = "connections"

@dataclass
class Tenant:
    """Tenant definition"""
    tenant_id: str
    name: str
    domain: str
    tier: TenantTier
    status: TenantStatus
    owner_id: str
    admin_email: str
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    limits: Dict[str, Any]
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    custom_configurations: Dict[str, Any]
    branding: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary"""
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'domain': self.domain,
            'tier': self.tier.value,
            'status': self.status.value,
            'owner_id': self.owner_id,
            'admin_email': self.admin_email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings': self.settings,
            'limits': self.limits,
            'usage': self.usage,
            'metadata': self.metadata,
            'custom_configurations': self.custom_configurations,
            'branding': self.branding
        }

@dataclass
class TenantUser:
    """Tenant user definition"""
    user_id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    role: str
    permissions: Set[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant user to dictionary"""
        return {
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'permissions': list(self.permissions),
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class TenantResource:
    """Tenant resource allocation"""
    resource_id: str
    tenant_id: str
    resource_type: ResourceType
    allocated_amount: Union[int, float]
    used_amount: Union[int, float]
    unit: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant resource to dictionary"""
        return {
            'resource_id': self.resource_id,
            'tenant_id': self.tenant_id,
            'resource_type': self.resource_type.value,
            'allocated_amount': self.allocated_amount,
            'used_amount': self.used_amount,
            'unit': self.unit,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class TenantDatabase:
    """Tenant database configuration"""
    database_id: str
    tenant_id: str
    database_name: str
    database_type: str
    host: str
    port: int
    username: str
    password_encrypted: str
    isolation_level: DataIsolationLevel
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant database to dictionary"""
        return {
            'database_id': self.database_id,
            'tenant_id': self.tenant_id,
            'database_name': self.database_name,
            'database_type': self.database_type,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password_encrypted': self.password_encrypted,
            'isolation_level': self.isolation_level.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

class TenantManager:
    """Multi-tenant management system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_users: Dict[str, TenantUser] = {}
        self.tenant_resources: Dict[str, TenantResource] = {}
        self.tenant_databases: Dict[str, TenantDatabase] = {}
        self.domain_mappings: Dict[str, str] = {}  # domain -> tenant_id
        self.user_tenant_mappings: Dict[str, str] = {}  # user_id -> tenant_id
        self.lock = threading.Lock()
        
        # Configuration
        self.default_tier = TenantTier.STARTUP
        self.default_isolation_level = DataIsolationLevel.SCHEMA_ISOLATION
        self.max_tenant_users = int(os.getenv('MAX_TENANT_USERS', '10000'))
        self.resource_check_interval = int(os.getenv('RESOURCE_CHECK_INTERVAL', '300'))  # 5 minutes
        
        # Initialize default tenant configurations
        self._initialize_tier_configurations()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_tier_configurations(self) -> None:
        """Initialize default tier configurations"""
        self.tier_configs = {
            TenantTier.STARTUP: {
                'limits': {
                    'users': 10,
                    'storage_gb': 10,
                    'api_calls_per_day': 10000,
                    'cpu_cores': 2,
                    'memory_gb': 4,
                    'bandwidth_gb_per_month': 100
                },
                'features': {
                    'basic_analytics': True,
                    'email_support': True,
                    'api_access': True,
                    'custom_domain': False,
                    'white_labeling': False,
                    'advanced_security': False,
                    'priority_support': False
                },
                'pricing': {
                    'monthly': 29.99,
                    'yearly': 299.99
                }
            },
            TenantTier.BUSINESS: {
                'limits': {
                    'users': 100,
                    'storage_gb': 100,
                    'api_calls_per_day': 100000,
                    'cpu_cores': 8,
                    'memory_gb': 16,
                    'bandwidth_gb_per_month': 1000
                },
                'features': {
                    'basic_analytics': True,
                    'email_support': True,
                    'api_access': True,
                    'custom_domain': True,
                    'white_labeling': False,
                    'advanced_security': True,
                    'priority_support': True
                },
                'pricing': {
                    'monthly': 99.99,
                    'yearly': 999.99
                }
            },
            TenantTier.ENTERPRISE: {
                'limits': {
                    'users': 10000,
                    'storage_gb': 1000,
                    'api_calls_per_day': 10000000,
                    'cpu_cores': 32,
                    'memory_gb': 64,
                    'bandwidth_gb_per_month': 10000
                },
                'features': {
                    'basic_analytics': True,
                    'phone_support': True,
                    'api_access': True,
                    'custom_domain': True,
                    'white_labeling': True,
                    'advanced_security': True,
                    'priority_support': True,
                    'dedicated_support': True,
                    'custom_integrations': True
                },
                'pricing': {
                    'monthly': 499.99,
                    'yearly': 4999.99
                }
            }
        }
    
    def create_tenant(self, name: str, domain: str, owner_id: str, admin_email: str,
                      tier: Optional[TenantTier] = None, settings: Optional[Dict[str, Any]] = None,
                      custom_configurations: Optional[Dict[str, Any]] = None) -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Validate domain uniqueness
        if domain in self.domain_mappings:
            raise ValueError(f"Domain {domain} is already in use")
        
        # Set default tier if not specified
        if tier is None:
            tier = self.default_tier
        
        # Get tier configuration
        tier_config = self.tier_configs.get(tier, self.tier_configs[TenantTier.STARTUP])
        
        # Create tenant
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            domain=domain,
            tier=tier,
            status=TenantStatus.PENDING,
            owner_id=owner_id,
            admin_email=admin_email,
            created_at=now,
            updated_at=now,
            settings=settings or {},
            limits=tier_config['limits'].copy(),
            usage={},
            metadata={},
            custom_configurations=custom_configurations or {},
            branding={
                'logo_url': '',
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'custom_css': '',
                'custom_domain': domain
            }
        )
        
        with self.lock:
            self.tenants[tenant_id] = tenant
            self.domain_mappings[domain] = tenant_id
            self.user_tenant_mappings[owner_id] = tenant_id
        
        # Create tenant database
        self._create_tenant_database(tenant)
        
        # Allocate resources
        self._allocate_tenant_resources(tenant)
        
        # Create admin user
        self._create_tenant_admin(tenant, owner_id, admin_email)
        
        # Activate tenant
        tenant.status = TenantStatus.ACTIVE
        tenant.updated_at = now
        
        logger.info(f"Created tenant {tenant_id} ({name}) with domain {domain}")
        
        return tenant
    
    def _create_tenant_database(self, tenant: Tenant) -> TenantDatabase:
        """Create tenant database"""
        database_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Generate database name
        database_name = f"tenant_{tenant.tenant_id.replace('-', '_')}"
        
        # Generate credentials
        username = f"tenant_user_{tenant.tenant_id[:8]}"
        password = self._generate_database_password()
        password_encrypted = self.encryption_manager.encrypt(password)
        
        # Determine host and port based on isolation level
        if self.default_isolation_level == DataIsolationLevel.DATABASE_ISOLATION:
            host = f"{database_name}.db.helm-ai.com"
            port = 5432
        else:
            host = "shared.db.helm-ai.com"
            port = 5432
        
        database = TenantDatabase(
            database_id=database_id,
            tenant_id=tenant.tenant_id,
            database_name=database_name,
            database_type="postgresql",
            host=host,
            port=port,
            username=username,
            password_encrypted=password_encrypted,
            isolation_level=self.default_isolation_level,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        
        with self.lock:
            self.tenant_databases[database_id] = database
        
        # In production, this would actually create the database
        logger.info(f"Created database {database_name} for tenant {tenant.tenant_id}")
        
        return database
    
    def _generate_database_password(self) -> str:
        """Generate secure database password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        return password
    
    def _allocate_tenant_resources(self, tenant: Tenant) -> None:
        """Allocate resources to tenant"""
        tier_config = self.tier_configs.get(tenant.tier, self.tier_configs[TenantTier.STARTUP])
        
        for resource_type, limit in tier_config['limits'].items():
            if resource_type in ['cpu_cores', 'memory_gb', 'storage_gb', 'bandwidth_gb_per_month']:
                resource_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # Determine unit
                if resource_type == 'cpu_cores':
                    unit = 'cores'
                elif resource_type == 'memory_gb' or resource_type == 'storage_gb':
                    unit = 'GB'
                elif resource_type == 'bandwidth_gb_per_month':
                    unit = 'GB/month'
                else:
                    unit = 'count'
                
                resource = TenantResource(
                    resource_id=resource_id,
                    tenant_id=tenant.tenant_id,
                    resource_type=ResourceType(resource_type),
                    allocated_amount=limit,
                    used_amount=0,
                    unit=unit,
                    created_at=now,
                    updated_at=now,
                    metadata={}
                )
                
                with self.lock:
                    self.tenant_resources[resource_id] = resource
        
        logger.info(f"Allocated resources for tenant {tenant.tenant_id}")
    
    def _create_tenant_admin(self, tenant: Tenant, owner_id: str, admin_email: str) -> TenantUser:
        """Create tenant admin user"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        tenant_user = TenantUser(
            user_id=user_id,
            tenant_id=tenant.tenant_id,
            email=admin_email,
            first_name="Tenant",
            last_name="Admin",
            role="admin",
            permissions={
                'tenant_admin',
                'user_management',
                'billing_management',
                'configuration_management',
                'analytics_view',
                'api_access'
            },
            is_active=True,
            last_login=None,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        
        with self.lock:
            self.tenant_users[user_id] = tenant_user
        
        return tenant_user
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        with self.lock:
            tenant_id = self.domain_mappings.get(domain)
            if tenant_id:
                return self.tenants.get(tenant_id)
            return None
    
    def get_tenant_by_user(self, user_id: str) -> Optional[Tenant]:
        """Get tenant by user ID"""
        with self.lock:
            tenant_id = self.user_tenant_mappings.get(user_id)
            if tenant_id:
                return self.tenants.get(tenant_id)
            return None
    
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get all users for a tenant"""
        with self.lock:
            return [user for user in self.tenant_users.values() if user.tenant_id == tenant_id]
    
    def add_tenant_user(self, tenant_id: str, email: str, first_name: str, last_name: str,
                       role: str = "user", permissions: Optional[Set[str]] = None) -> TenantUser:
        """Add user to tenant"""
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        tenant = self.tenants[tenant_id]
        
        # Check user limit
        current_users = len([u for u in self.tenant_users.values() if u.tenant_id == tenant_id])
        if current_users >= tenant.limits.get('users', self.max_tenant_users):
            raise ValueError(f"Tenant {tenant_id} has reached user limit")
        
        # Check if user already exists
        existing_user = next((u for u in self.tenant_users.values() if u.email == email and u.tenant_id == tenant_id), None)
        if existing_user:
            raise ValueError(f"User with email {email} already exists in tenant {tenant_id}")
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Set default permissions based on role
        if permissions is None:
            if role == "admin":
                permissions = {
                    'tenant_admin',
                    'user_management',
                    'billing_management',
                    'configuration_management',
                    'analytics_view',
                    'api_access'
                }
            elif role == "manager":
                permissions = {
                    'user_management',
                    'analytics_view',
                    'api_access'
                }
            else:
                permissions = {
                    'analytics_view',
                    'api_access'
                }
        
        tenant_user = TenantUser(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            permissions=permissions,
            is_active=True,
            last_login=None,
            created_at=now,
            updated_at=now,
            metadata={}
        )
        
        with self.lock:
            self.tenant_users[user_id] = tenant_user
            self.user_tenant_mappings[user_id] = tenant_id
        
        logger.info(f"Added user {email} to tenant {tenant_id}")
        
        return tenant_user
    
    def update_tenant_usage(self, tenant_id: str, resource_type: str, amount: Union[int, float]) -> bool:
        """Update tenant resource usage"""
        with self.lock:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            
            # Update usage
            if resource_type not in tenant.usage:
                tenant.usage[resource_type] = 0
            
            tenant.usage[resource_type] += amount
            tenant.updated_at = datetime.utcnow()
            
            # Check limits
            limit = tenant.limits.get(resource_type)
            if limit and tenant.usage[resource_type] > limit:
                logger.warning(f"Tenant {tenant_id} exceeded limit for {resource_type}: {tenant.usage[resource_type]} > {limit}")
                
                # Update resource usage
                for resource in self.tenant_resources.values():
                    if (resource.tenant_id == tenant_id and 
                        resource.resource_type.value == resource_type):
                        resource.used_amount = tenant.usage[resource_type]
                        resource.updated_at = datetime.utcnow()
                        break
            
            return True
    
    def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant usage and limits"""
        with self.lock:
            if tenant_id not in self.tenants:
                return {}
            
            tenant = self.tenants[tenant_id]
            
            usage_report = {
                'tenant_id': tenant_id,
                'tier': tenant.tier.value,
                'usage': tenant.usage.copy(),
                'limits': tenant.limits.copy(),
                'utilization': {},
                'over_limits': []
            }
            
            # Calculate utilization
            for resource, limit in tenant.limits.items():
                usage = tenant.usage.get(resource, 0)
                if limit > 0:
                    utilization = (usage / limit) * 100
                    usage_report['utilization'][resource] = round(utilization, 2)
                    
                    if usage > limit:
                        usage_report['over_limits'].append(resource)
            
            return usage_report
    
    def upgrade_tenant(self, tenant_id: str, new_tier: TenantTier) -> bool:
        """Upgrade tenant to new tier"""
        with self.lock:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            old_tier = tenant.tier
            
            if new_tier == old_tier:
                return True  # Already at this tier
            
            # Get new tier configuration
            new_config = self.tier_configs.get(new_tier)
            if not new_config:
                return False
            
            # Update tenant
            tenant.tier = new_tier
            tenant.limits = new_config['limits'].copy()
            tenant.updated_at = datetime.utcnow()
            
            # Reallocate resources
            self._reallocate_tenant_resources(tenant)
            
            logger.info(f"Upgraded tenant {tenant_id} from {old_tier.value} to {new_tier.value}")
            
            return True
    
    def _reallocate_tenant_resources(self, tenant: Tenant) -> None:
        """Reallocate resources for tier change"""
        new_config = self.tier_configs.get(tenant.tier, self.tier_configs[TenantTier.STARTUP])
        
        # Remove existing resources
        resources_to_remove = [
            r for r in self.tenant_resources.values() 
            if r.tenant_id == tenant.tenant_id
        ]
        
        for resource in resources_to_remove:
            del self.tenant_resources[resource.resource_id]
        
        # Allocate new resources
        for resource_type, limit in new_config['limits'].items():
            if resource_type in ['cpu_cores', 'memory_gb', 'storage_gb', 'bandwidth_gb_per_month']:
                resource_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # Determine unit
                if resource_type == 'cpu_cores':
                    unit = 'cores'
                elif resource_type == 'memory_gb' or resource_type == 'storage_gb':
                    unit = 'GB'
                elif resource_type == 'bandwidth_gb_per_month':
                    unit = 'GB/month'
                else:
                    unit = 'count'
                
                resource = TenantResource(
                    resource_id=resource_id,
                    tenant_id=tenant.tenant_id,
                    resource_type=ResourceType(resource_type),
                    allocated_amount=limit,
                    used_amount=0,
                    unit=unit,
                    created_at=now,
                    updated_at=now,
                    metadata={}
                )
                
                self.tenant_resources[resource_id] = resource
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Suspend tenant"""
        with self.lock:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.SUSPENDED
            tenant.updated_at = datetime.utcnow()
            
            if reason:
                tenant.metadata['suspension_reason'] = reason
            
            # Deactivate all users
            for user in self.tenant_users.values():
                if user.tenant_id == tenant_id:
                    user.is_active = False
                    user.updated_at = datetime.utcnow()
            
            logger.info(f"Suspended tenant {tenant_id}: {reason}")
            
            return True
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate suspended tenant"""
        with self.lock:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            
            if tenant.status != TenantStatus.SUSPENDED:
                return False
            
            tenant.status = TenantStatus.ACTIVE
            tenant.updated_at = datetime.utcnow()
            
            # Remove suspension reason
            if 'suspension_reason' in tenant.metadata:
                del tenant.metadata['suspension_reason']
            
            # Reactivate all users
            for user in self.tenant_users.values():
                if user.tenant_id == tenant_id:
                    user.is_active = True
                    user.updated_at = datetime.utcnow()
            
            logger.info(f"Activated tenant {tenant_id}")
            
            return True
    
    def terminate_tenant(self, tenant_id: str, reason: str = "") -> bool:
        """Terminate tenant"""
        with self.lock:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            tenant.status = TenantStatus.TERMINATED
            tenant.updated_at = datetime.utcnow()
            
            if reason:
                tenant.metadata['termination_reason'] = reason
            
            # Remove domain mapping
            if tenant.domain in self.domain_mappings:
                del self.domain_mappings[tenant.domain]
            
            # Remove user mappings
            users_to_remove = [
                user_id for user_id, mapped_tenant_id in self.user_tenant_mappings.items()
                if mapped_tenant_id == tenant_id
            ]
            
            for user_id in users_to_remove:
                del self.user_tenant_mappings[user_id]
            
            logger.info(f"Terminated tenant {tenant_id}: {reason}")
            
            return True
    
    def get_tenant_metrics(self) -> Dict[str, Any]:
        """Get tenant management metrics"""
        with self.lock:
            total_tenants = len(self.tenants)
            active_tenants = len([t for t in self.tenants.values() if t.status == TenantStatus.ACTIVE])
            suspended_tenants = len([t for t in self.tenants.values() if t.status == TenantStatus.SUSPENDED])
            
            # Tier distribution
            tier_distribution = defaultdict(int)
            for tenant in self.tenants.values():
                tier_distribution[tenant.tier.value] += 1
            
            # Resource utilization
            total_resources = defaultdict(float)
            used_resources = defaultdict(float)
            
            for resource in self.tenant_resources.values():
                total_resources[resource.resource_type.value] += resource.allocated_amount
                used_resources[resource.resource_type.value] += resource.used_amount
            
            utilization = {}
            for resource_type in total_resources:
                if total_resources[resource_type] > 0:
                    utilization[resource_type] = (used_resources[resource_type] / total_resources[resource_type]) * 100
            
            return {
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'suspended_tenants': suspended_tenants,
                'tier_distribution': dict(tier_distribution),
                'total_users': len(self.tenant_users),
                'active_users': len([u for u in self.tenant_users.values() if u.is_active]),
                'total_resources': dict(total_resources),
                'used_resources': dict(used_resources),
                'resource_utilization': utilization,
                'total_databases': len(self.tenant_databases)
            }
    
    @contextmanager
    def tenant_context(self, tenant_id: str):
        """Context manager for tenant-specific operations"""
        original_tenant = getattr(self, '_current_tenant', None)
        
        try:
            self._current_tenant = tenant_id
            yield tenant_id
        finally:
            self._current_tenant = original_tenant
    
    def _start_background_tasks(self) -> None:
        """Start background tenant management tasks"""
        # Start resource monitoring thread
        resource_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        resource_thread.start()
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_resources, daemon=True)
        cleanup_thread.start()
    
    def _monitor_resources(self) -> None:
        """Monitor tenant resource usage"""
        while True:
            try:
                # Check every resource_check_interval seconds
                time.sleep(self.resource_check_interval)
                
                with self.lock:
                    for tenant in self.tenants.values():
                        if tenant.status == TenantStatus.ACTIVE:
                            usage_report = self.get_tenant_usage(tenant.tenant_id)
                            
                            # Check for over-limit usage
                            if usage_report['over_limits']:
                                logger.warning(f"Tenant {tenant.tenant_id} over limits: {usage_report['over_limits']}")
                                
                                # In production, this could trigger alerts or automatic actions
                                for resource in usage_report['over_limits']:
                                    if resource in ['api_calls_per_day']:
                                        # Could implement rate limiting
                                        pass
                                    elif resource in ['storage_gb']:
                                        # Could implement storage quotas
                                        pass
                
            except Exception as e:
                logger.error(f"Resource monitoring failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _cleanup_resources(self) -> None:
        """Cleanup terminated tenant resources"""
        while True:
            try:
                # Run cleanup daily
                time.sleep(86400)  # 24 hours
                
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                with self.lock:
                    # Find terminated tenants older than cutoff
                    terminated_tenants = [
                        tenant for tenant in self.tenants.values()
                        if (tenant.status == TenantStatus.TERMINATED and 
                            tenant.updated_at < cutoff_date)
                    ]
                    
                    for tenant in terminated_tenants:
                        # Remove tenant resources
                        resources_to_remove = [
                            r for r in self.tenant_resources.values() 
                            if r.tenant_id == tenant.tenant_id
                        ]
                        
                        for resource in resources_to_remove:
                            del self.tenant_resources[resource.resource_id]
                        
                        # Remove tenant database
                        databases_to_remove = [
                            d for d in self.tenant_databases.values()
                            if d.tenant_id == tenant.tenant_id
                        ]
                        
                        for database in databases_to_remove:
                            del self.tenant_databases[database.database_id]
                        
                        # Remove tenant users
                        users_to_remove = [
                            u for u in self.tenant_users.values()
                            if u.tenant_id == tenant.tenant_id
                        ]
                        
                        for user in users_to_remove:
                            del self.tenant_users[user.user_id]
                        
                        # Remove tenant
                        del self.tenants[tenant.tenant_id]
                        
                        logger.info(f"Cleaned up terminated tenant {tenant.tenant_id}")
                
            except Exception as e:
                logger.error(f"Resource cleanup failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying

# Global tenant manager instance
tenant_manager = TenantManager()

# Export main components
__all__ = [
    'TenantManager',
    'Tenant',
    'TenantUser',
    'TenantResource',
    'TenantDatabase',
    'TenantStatus',
    'TenantTier',
    'DataIsolationLevel',
    'ResourceType',
    'tenant_manager'
]
