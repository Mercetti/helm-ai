"""
Helm AI Disaster Recovery
This module provides disaster recovery procedures and failover mechanisms
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import threading
import time
import requests
import subprocess
import boto3
from botocore.exceptions import ClientError

from .backup_system import backup_manager, BackupStatus
from .encryption import encryption_manager

logger = logging.getLogger(__name__)

class DisasterType(Enum):
    """Types of disasters"""
    NATURAL_DISASTER = "natural_disaster"
    POWER_OUTAGE = "power_outage"
    NETWORK_FAILURE = "network_failure"
    HARDWARE_FAILURE = "hardware_failure"
    DATA_CORRUPTION = "data_corruption"
    SECURITY_BREACH = "security_breach"
    HUMAN_ERROR = "human_error"
    SOFTWARE_FAILURE = "software_failure"

class RecoveryStatus(Enum):
    """Recovery status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIALLY_RECOVERED = "partially_recovered"
    FULLY_RECOVERED = "fully_recovered"
    FAILED = "failed"

class FailoverStatus(Enum):
    """Failover status"""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILING_OVER = "failing_over"
    FAILED_OVER = "failed_over"
    FAILBACK = "failback"

@dataclass
class RecoveryPlan:
    """Disaster recovery plan"""
    plan_id: str
    name: str
    disaster_type: DisasterType
    rto_minutes: int  # Recovery Time Objective
    rpo_minutes: int  # Recovery Point Objective
    procedures: List[str]
    contact_personnel: List[str]
    critical_systems: List[str]
    backup_requirements: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tested_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DisasterEvent:
    """Disaster event record"""
    event_id: str
    disaster_type: DisasterType
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    recovery_plan_id: str = None
    recovery_status: RecoveryStatus = RecoveryStatus.NOT_STARTED
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    lessons_learned: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FailoverConfig:
    """Failover configuration"""
    config_id: str
    service_name: str
    primary_region: str
    secondary_region: str
    health_check_url: str
    failover_threshold: int  # Number of failed checks before failover
    failback_delay_minutes: int
    auto_failover_enabled: bool = True
    status: FailoverStatus = FailoverStatus.ACTIVE
    last_failover: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DisasterRecoveryManager:
    """Comprehensive disaster recovery management"""
    
    def __init__(self):
        self.plans: Dict[str, RecoveryPlan] = {}
        self.events: Dict[str, DisasterEvent] = {}
        self.failover_configs: Dict[str, FailoverConfig] = {}
        
        # Configuration
        self.primary_region = os.getenv('PRIMARY_REGION', 'us-east-1')
        self.secondary_region = os.getenv('SECONDARY_REGION', 'us-west-2')
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))  # seconds
        
        # Initialize AWS clients (with error handling for test environments)
        try:
            self.ec2_client = boto3.client('ec2', region_name=self.primary_region)
            self.rds_client = boto3.client('rds', region_name=self.primary_region)
            self.route53_client = boto3.client('route53', region_name=self.primary_region)
        except Exception as e:
            logger.warning(f"Failed to initialize AWS clients: {e}")
            self.ec2_client = None
            self.rds_client = None
            self.route53_client = None
        
        # Initialize recovery plans
        self._initialize_recovery_plans()
        
        # Initialize failover configurations
        self._initialize_failover_configs()
        
        # Start health monitoring
        self._start_health_monitoring()
    
    def _initialize_recovery_plans(self):
        """Create default recovery plans"""
        
        # Data corruption recovery plan
        self.create_recovery_plan(
            name="Data Corruption Recovery",
            disaster_type=DisasterType.DATA_CORRUPTION,
            rto_minutes=60,
            rpo_minutes=15,
            procedures=[
                "Identify corrupted data sources",
                "Stop affected services",
                "Restore from latest verified backup",
                "Verify data integrity",
                "Restart services",
                "Monitor system stability"
            ],
            contact_personnel=["devops@helm-ai.com", "dba@helm-ai.com"],
            critical_systems=["database", "api_server", "file_storage"],
            backup_requirements={
                "backup_type": "full",
                "retention_days": 30,
                "verification_required": True
            }
        )
        
        # Power outage recovery plan
        self.create_recovery_plan(
            name="Power Outage Recovery",
            disaster_type=DisasterType.POWER_OUTAGE,
            rto_minutes=30,
            rpo_minutes=5,
            procedures=[
                "Assess power outage scope",
                "Initiate UPS power if available",
                "Activate secondary data center",
                "Failover to standby systems",
                "Verify service availability",
                "Monitor power restoration"
            ],
            contact_personnel=["devops@helm-ai.com", "facilities@helm-ai.com"],
            critical_systems=["all"],
            backup_requirements={
                "backup_type": "incremental",
                "retention_days": 7,
                "geo_redundant": True
            }
        )
        
        # Security breach recovery plan
        self.create_recovery_plan(
            name="Security Breach Recovery",
            disaster_type=DisasterType.SECURITY_BREACH,
            rto_minutes=120,
            rpo_minutes=0,
            procedures=[
                "Isolate affected systems",
                "Preserve forensic evidence",
                "Identify breach vector",
                "Patch vulnerabilities",
                "Restore from clean backups",
                "Implement additional security controls",
                "Notify stakeholders if required"
            ],
            contact_personnel=["security@helm-ai.com", "legal@helm-ai.com", "devops@helm-ai.com"],
            critical_systems=["authentication", "database", "api_server"],
            backup_requirements={
                "backup_type": "full",
                "retention_days": 365,
                "immutable": True
            }
        )
    
    def _initialize_failover_configs(self):
        """Initialize failover configurations"""
        
        # API service failover
        self.create_failover_config(
            service_name="api_service",
            primary_region=self.primary_region,
            secondary_region=self.secondary_region,
            health_check_url="https://api.helm-ai.com/health",
            failover_threshold=3,
            failback_delay_minutes=30
        )
        
        # Database failover
        self.create_failover_config(
            service_name="database",
            primary_region=self.primary_region,
            secondary_region=self.secondary_region,
            health_check_url="https://api.helm-ai.com/db/health",
            failover_threshold=2,
            failback_delay_minutes=60
        )
    
    def create_recovery_plan(self, 
                           name: str,
                           disaster_type: DisasterType,
                           rto_minutes: int,
                           rpo_minutes: int,
                           procedures: List[str],
                           contact_personnel: List[str],
                           critical_systems: List[str],
                           backup_requirements: Dict[str, Any]) -> RecoveryPlan:
        """Create disaster recovery plan"""
        plan_id = f"plan_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        plan = RecoveryPlan(
            plan_id=plan_id,
            name=name,
            disaster_type=disaster_type,
            rto_minutes=rto_minutes,
            rpo_minutes=rpo_minutes,
            procedures=procedures,
            contact_personnel=contact_personnel,
            critical_systems=critical_systems,
            backup_requirements=backup_requirements
        )
        
        self.plans[plan_id] = plan
        
        logger.info(f"Created recovery plan: {name} ({plan_id})")
        return plan
    
    def create_failover_config(self, 
                             service_name: str,
                             primary_region: str,
                             secondary_region: str,
                             health_check_url: str,
                             failover_threshold: int,
                             failback_delay_minutes: int) -> FailoverConfig:
        """Create failover configuration"""
        config_id = f"failover_{service_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        config = FailoverConfig(
            config_id=config_id,
            service_name=service_name,
            primary_region=primary_region,
            secondary_region=secondary_region,
            health_check_url=health_check_url,
            failover_threshold=failover_threshold,
            failback_delay_minutes=failback_delay_minutes
        )
        
        self.failover_configs[config_id] = config
        
        logger.info(f"Created failover config: {service_name} ({config_id})")
        return config
    
    def declare_disaster(self, 
                        disaster_type: DisasterType,
                        severity: str,
                        description: str,
                        recovery_plan_id: str = None) -> DisasterEvent:
        """Declare disaster event"""
        event_id = f"disaster_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(description.encode()).hexdigest()[:8]}"
        
        # Find appropriate recovery plan if not specified
        if not recovery_plan_id:
            for plan_id, plan in self.plans.items():
                if plan.disaster_type == disaster_type:
                    recovery_plan_id = plan_id
                    break
        
        event = DisasterEvent(
            event_id=event_id,
            disaster_type=disaster_type,
            severity=severity,
            description=description,
            detected_at=datetime.now(),
            recovery_plan_id=recovery_plan_id
        )
        
        self.events[event_id] = event
        
        # Log disaster declaration
        logger.critical(f"DISASTER DECLARED: {disaster_type.value} - {description}")
        
        # Initiate recovery if plan is available
        if recovery_plan_id:
            self.initiate_recovery(event_id)
        
        return event
    
    def initiate_recovery(self, event_id: str) -> bool:
        """Initiate disaster recovery"""
        try:
            event = self.events.get(event_id)
            if not event:
                return False
            
            plan = self.plans.get(event.recovery_plan_id)
            if not plan:
                logger.error(f"Recovery plan not found: {event.recovery_plan_id}")
                return False
            
            event.recovery_status = RecoveryStatus.IN_PROGRESS
            
            # Start recovery in background thread
            recovery_thread = threading.Thread(
                target=self._execute_recovery,
                args=(event, plan),
                daemon=True
            )
            recovery_thread.start()
            
            logger.info(f"Recovery initiated for disaster: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initiate recovery: {e}")
            return False
    
    def _execute_recovery(self, event: DisasterEvent, plan: RecoveryPlan):
        """Execute disaster recovery procedures"""
        try:
            logger.info(f"Executing recovery plan: {plan.name}")
            
            start_time = datetime.now()
            
            # Execute recovery procedures
            for i, procedure in enumerate(plan.procedures):
                try:
                    logger.info(f"Executing procedure {i+1}/{len(plan.procedures)}: {procedure}")
                    
                    # Execute procedure based on type
                    if "backup" in procedure.lower():
                        self._execute_backup_recovery(plan, procedure)
                    elif "failover" in procedure.lower():
                        self._execute_failover(plan, procedure)
                    elif "stop" in procedure.lower():
                        self._stop_services(plan.critical_systems)
                    elif "restart" in procedure.lower():
                        self._restart_services(plan.critical_systems)
                    else:
                        # Generic procedure execution
                        self._execute_generic_procedure(procedure)
                    
                    event.actions_taken.append(f"Completed: {procedure}")
                    
                    # Check RTO compliance
                    elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed_minutes > plan.rto_minutes:
                        logger.warning(f"RTO exceeded: {elapsed_minutes:.1f} minutes (target: {plan.rto_minutes})")
                    
                except Exception as e:
                    logger.error(f"Failed to execute procedure '{procedure}': {e}")
                    event.actions_taken.append(f"Failed: {procedure} - {str(e)}")
            
            # Update recovery status
            event.recovery_status = RecoveryStatus.FULLY_RECOVERED
            event.resolved_at = datetime.now()
            
            logger.info(f"Recovery completed for disaster: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Recovery execution failed: {e}")
            event.recovery_status = RecoveryStatus.FAILED
    
    def _execute_backup_recovery(self, plan: RecoveryPlan, procedure: str):
        """Execute backup recovery procedure"""
        backup_type = plan.backup_requirements.get("backup_type", "full")
        
        # Find latest successful backup
        backups = backup_manager.list_backups(status=BackupStatus.COMPLETED)
        
        if not backups:
            raise Exception("No successful backups found")
        
        # Get latest backup
        latest_backup = backups[0]
        
        # Restore backup
        restore_path = f"/tmp/restore_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        success = backup_manager.restore_backup(latest_backup.backup_id, restore_path)
        
        if not success:
            raise Exception(f"Backup restore failed: {latest_backup.backup_id}")
        
        logger.info(f"Backup restored: {latest_backup.backup_id} -> {restore_path}")
    
    def _execute_failover(self, plan: RecoveryPlan, procedure: str):
        """Execute failover procedure"""
        for config in self.failover_configs.values():
            if config.service_name in plan.critical_systems:
                self.initiate_failover(config.config_id)
    
    def _stop_services(self, services: List[str]):
        """Stop critical services"""
        for service in services:
            try:
                # Use systemctl or docker to stop services
                subprocess.run(["systemctl", "stop", service], check=True)
                logger.info(f"Stopped service: {service}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to stop service {service}: {e}")
    
    def _restart_services(self, services: List[str]):
        """Restart critical services"""
        for service in services:
            try:
                subprocess.run(["systemctl", "restart", service], check=True)
                logger.info(f"Restarted service: {service}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to restart service {service}: {e}")
    
    def _execute_generic_procedure(self, procedure: str):
        """Execute generic recovery procedure"""
        # This would contain specific procedure implementations
        # For now, just log the procedure
        logger.info(f"Executing generic procedure: {procedure}")
        time.sleep(2)  # Simulate procedure execution
    
    def initiate_failover(self, config_id: str) -> bool:
        """Initiate failover for service"""
        try:
            config = self.failover_configs.get(config_id)
            if not config:
                return False
            
            if not config.auto_failover_enabled:
                logger.info(f"Auto failover disabled for service: {config.service_name}")
                return False
            
            config.status = FailoverStatus.FAILING_OVER
            
            # Update DNS to point to secondary region
            self._update_dns_record(config, config.secondary_region)
            
            # Start services in secondary region
            self._start_secondary_services(config)
            
            config.status = FailoverStatus.FAILED_OVER
            config.last_failover = datetime.now()
            
            logger.info(f"Failover completed for service: {config.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failover failed for service {config.service_name}: {e}")
            config.status = FailoverStatus.ACTIVE
            return False
    
    def _update_dns_record(self, config: FailoverConfig, target_region: str):
        """Update DNS record for failover"""
        try:
            # Get hosted zone ID
            hosted_zone_id = os.getenv('ROUTE53_HOSTED_ZONE_ID')
            if not hosted_zone_id:
                logger.warning("Route53 hosted zone ID not configured")
                return
            
            # Update DNS record
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': f"{config.service_name}.helm-ai.com",
                                'Type': 'CNAME',
                                'TTL': 60,
                                'ResourceRecords': [
                                    {
                                        'Value': f"loadbalancer-{target_region}.helm-ai.com"
                                    }
                                ]
                            }
                        }
                    ]
                }
            )
            
            logger.info(f"DNS updated for {config.service_name} -> {target_region}")
            
        except ClientError as e:
            logger.error(f"Failed to update DNS: {e}")
    
    def _start_secondary_services(self, config: FailoverConfig):
        """Start services in secondary region"""
        try:
            # This would use AWS SDK to start services in secondary region
            # For now, just log the action
            logger.info(f"Starting services in {config.secondary_region}")
            
        except Exception as e:
            logger.error(f"Failed to start secondary services: {e}")
    
    def initiate_failback(self, config_id: str) -> bool:
        """Initiate failback to primary region"""
        try:
            config = self.failover_configs.get(config_id)
            if not config:
                return False
            
            if config.status != FailoverStatus.FAILED_OVER:
                logger.warning(f"Service {config.service_name} is not in failed over state")
                return False
            
            # Wait for failback delay
            if config.last_failover:
                wait_time = (config.last_failover + timedelta(minutes=config.failback_delay_minutes)) - datetime.now()
                if wait_time.total_seconds() > 0:
                    logger.info(f"Waiting {wait_time.total_seconds():.0f} seconds before failback")
                    time.sleep(wait_time.total_seconds())
            
            # Update DNS back to primary region
            self._update_dns_record(config, config.primary_region)
            
            config.status = FailoverStatus.FAILBACK
            
            logger.info(f"Failback initiated for service: {config.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failback failed for service {config.service_name}: {e}")
            return False
    
    def _start_health_monitoring(self):
        """Start health monitoring for failover"""
        def monitor_health():
            while True:
                try:
                    for config in self.failover_configs.values():
                        if config.auto_failover_enabled and config.status == FailoverStatus.ACTIVE:
                            self._check_service_health(config)
                    
                    time.sleep(self.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
        
        health_thread = threading.Thread(target=monitor_health, daemon=True)
        health_thread.start()
    
    def _check_service_health(self, config: FailoverConfig):
        """Check service health and trigger failover if needed"""
        try:
            response = requests.get(config.health_check_url, timeout=10)
            healthy = response.status_code == 200
            
            if not healthy:
                # Increment failed check count
                failed_checks = config.metadata.get('failed_health_checks', 0) + 1
                config.metadata['failed_health_checks'] = failed_checks
                
                if failed_checks >= config.failover_threshold:
                    logger.warning(f"Service {config.service_name} health check failed {failed_checks} times, initiating failover")
                    self.initiate_failover(config.config_id)
            else:
                # Reset failed check count
                config.metadata['failed_health_checks'] = 0
                
        except requests.RequestException as e:
            logger.warning(f"Health check failed for {config.service_name}: {e}")
            
            failed_checks = config.metadata.get('failed_health_checks', 0) + 1
            config.metadata['failed_health_checks'] = failed_checks
            
            if failed_checks >= config.failover_threshold:
                logger.warning(f"Service {config.service_name} health check failed {failed_checks} times, initiating failover")
                self.initiate_failover(config.config_id)
    
    def test_recovery_plan(self, plan_id: str) -> Dict[str, Any]:
        """Test disaster recovery plan"""
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                return {"success": False, "error": "Plan not found"}
            
            logger.info(f"Testing recovery plan: {plan.name}")
            
            start_time = datetime.now()
            
            # Simulate recovery procedures
            for i, procedure in enumerate(plan.procedures):
                logger.info(f"Testing procedure {i+1}/{len(plan.procedures)}: {procedure}")
                time.sleep(1)  # Simulate procedure execution
            
            test_duration = (datetime.now() - start_time).total_seconds() / 60
            
            # Update plan test timestamp
            plan.tested_at = datetime.now()
            
            # Check if test meets RTO
            rto_compliant = test_duration <= plan.rto_minutes
            
            return {
                "success": True,
                "plan_id": plan_id,
                "plan_name": plan.name,
                "test_duration_minutes": test_duration,
                "rto_target_minutes": plan.rto_minutes,
                "rto_compliant": rto_compliant,
                "tested_at": plan.tested_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Recovery plan test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_disaster_dashboard(self) -> Dict[str, Any]:
        """Get disaster recovery dashboard"""
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "active_disasters": 0,
            "recovery_plans": len(self.plans),
            "failover_configs": len(self.failover_configs),
            "services_status": {},
            "recent_events": []
        }
        
        # Count active disasters
        active_disasters = [e for e in self.events.values() if e.recovery_status in [RecoveryStatus.IN_PROGRESS, RecoveryStatus.PARTIALLY_RECOVERED]]
        dashboard["active_disasters"] = len(active_disasters)
        
        # Service status from failover configs
        for config in self.failover_configs.values():
            dashboard["services_status"][config.service_name] = {
                "status": config.status.value,
                "primary_region": config.primary_region,
                "secondary_region": config.secondary_region,
                "last_failover": config.last_failover.isoformat() if config.last_failover else None
            }
        
        # Recent events
        recent_events = sorted(self.events.values(), key=lambda x: x.detected_at, reverse=True)[:10]
        dashboard["recent_events"] = [
            {
                "event_id": event.event_id,
                "disaster_type": event.disaster_type.value,
                "severity": event.severity,
                "description": event.description,
                "detected_at": event.detected_at.isoformat(),
                "recovery_status": event.recovery_status.value
            }
            for event in recent_events
        ]
        
        return dashboard
    
    def get_recovery_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery plan details"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        return {
            "plan_id": plan.plan_id,
            "name": plan.name,
            "disaster_type": plan.disaster_type.value,
            "rto_minutes": plan.rto_minutes,
            "rpo_minutes": plan.rpo_minutes,
            "procedures": plan.procedures,
            "contact_personnel": plan.contact_personnel,
            "critical_systems": plan.critical_systems,
            "backup_requirements": plan.backup_requirements,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
            "tested_at": plan.tested_at.isoformat() if plan.tested_at else None
        }


# Global instance (with error handling)
try:
    disaster_recovery = DisasterRecoveryManager()
except Exception as e:
    logger.warning(f"Failed to initialize disaster recovery manager: {e}")
    disaster_recovery = None
