"""
Helm AI Security Hardening Module
Provides additional security measures, audits, and vulnerability assessments
"""

import os
import sys
import json
import hashlib
import secrets
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from database.database_manager import get_database_manager

@dataclass
class SecurityAudit:
    """Security audit record"""
    audit_id: str
    timestamp: datetime
    audit_type: str
    severity: str  # low, medium, high, critical
    category: str
    description: str
    affected_resources: List[str]
    recommendations: List[str]
    status: str = "open"  # open, in_progress, resolved, false_positive
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'audit_id': self.audit_id,
            'timestamp': self.timestamp.isoformat(),
            'audit_type': self.audit_type,
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'affected_resources': self.affected_resources,
            'recommendations': self.recommendations,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }

@dataclass
class Vulnerability:
    """Security vulnerability record"""
    vuln_id: str
    cve_id: Optional[str]
    severity: str
    cvss_score: Optional[float]
    title: str
    description: str
    affected_components: List[str]
    discovered_at: datetime
    patched_at: Optional[datetime] = None
    patch_version: Optional[str] = None
    status: str = "open"  # open, in_progress, patched, ignored
    remediation_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'vuln_id': self.vuln_id,
            'cve_id': self.cve_id,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'title': self.title,
            'description': self.description,
            'affected_components': self.affected_components,
            'discovered_at': self.discovered_at.isoformat(),
            'patched_at': self.patched_at.isoformat() if self.patched_at else None,
            'patch_version': self.patch_version,
            'status': self.status,
            'remediation_steps': self.remediation_steps
        }

class SecurityAuditor:
    """Comprehensive security auditing system"""
    
    def __init__(self):
        self.audits = deque(maxlen=1000)
        self.vulnerabilities = deque(maxlen=500)
        self.security_policies = self._setup_security_policies()
        self.lock = threading.RLock()
        
    def _setup_security_policies(self) -> Dict[str, Any]:
        """Setup security policies and thresholds"""
        return {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'history_count': 5
            },
            'session_policy': {
                'max_duration_hours': 8,
                'idle_timeout_minutes': 30,
                'max_concurrent_sessions': 3
            },
            'api_key_policy': {
                'max_age_days': 365,
                'require_rotation': True,
                'min_key_length': 32
            },
            'access_policy': {
                'max_failed_attempts': 5,
                'lockout_duration_minutes': 15,
                'require_mfa': True
            }
        }
    
    def run_security_audit(self, audit_type: str = "comprehensive") -> List[SecurityAudit]:
        """Run security audit"""
        logger.info(f"Starting security audit: {audit_type}")
        
        audits = []
        
        if audit_type in ["comprehensive", "authentication"]:
            audits.extend(self._audit_authentication())
        
        if audit_type in ["comprehensive", "authorization"]:
            audits.extend(self._audit_authorization())
        
        if audit_type in ["comprehensive", "data_protection"]:
            audits.extend(self._audit_data_protection())
        
        if audit_type in ["comprehensive", "infrastructure"]:
            audits.extend(self._audit_infrastructure())
        
        if audit_type in ["comprehensive", "compliance"]:
            audits.extend(self._audit_compliance())
        
        # Store audits
        with self.lock:
            self.audits.extend(audits)
        
        logger.info(f"Security audit completed: {len(audits)} findings")
        
        return audits
    
    def _audit_authentication(self) -> List[SecurityAudit]:
        """Audit authentication security"""
        audits = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for weak passwords
                result = session.execute(text("""
                    SELECT id, email, password_hash, created_at, updated_at
                    FROM users
                    WHERE password_hash IS NOT NULL
                """))
                
                users = result.fetchall()
                
                for user in users:
                    user_id, email, password_hash, created_at, updated_at = user
                    
                    # Check password age
                    if updated_at:
                        password_age = (datetime.now() - updated_at).days
                        if password_age > self.security_policies['password_policy']['max_age_days']:
                            audits.append(SecurityAudit(
                                audit_id=secrets.token_hex(8),
                                timestamp=datetime.now(),
                                audit_type="authentication",
                                severity="medium",
                                category="password_policy",
                                description=f"User {email} has password older than {password_age} days",
                                affected_resources=[f"user:{user_id}"],
                                recommendations=["Force password change", "Implement password expiration policy"]
                            ))
                
                # Check for inactive accounts
                result = session.execute(text("""
                    SELECT id, email, last_login_at
                    FROM users
                    WHERE last_login_at < NOW() - INTERVAL '90 days'
                """))
                
                inactive_users = result.fetchall()
                
                if inactive_users:
                    audits.append(SecurityAudit(
                        audit_id=secrets.token_hex(8),
                        timestamp=datetime.now(),
                        audit_type="authentication",
                        severity="low",
                        category="account_management",
                        description=f"Found {len(inactive_users)} inactive accounts",
                        affected_resources=[f"user:{user[0]}" for user in inactive_users],
                        recommendations=["Review inactive accounts", "Consider account suspension"]
                    ))
                
        except Exception as e:
            logger.error(f"Authentication audit failed: {e}")
        
        return audits
    
    def _audit_authorization(self) -> List[SecurityAudit]:
        """Audit authorization and access control"""
        audits = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for users with excessive privileges
                result = session.execute(text("""
                    SELECT u.id, u.email, u.role, COUNT(ak.id) as api_key_count
                    FROM users u
                    LEFT JOIN api_keys ak ON u.id = ak.user_id
                    WHERE u.role = 'ADMIN'
                    GROUP BY u.id, u.email, u.role
                """))
                
                admin_users = result.fetchall()
                
                for admin in admin_users:
                    user_id, email, role, api_key_count = admin
                    
                    if api_key_count > 10:
                        audits.append(SecurityAudit(
                            audit_id=secrets.token_hex(8),
                            timestamp=datetime.now(),
                            audit_type="authorization",
                            severity="medium",
                            category="privilege_escalation",
                            description=f"Admin user {email} has {api_key_count} API keys",
                            affected_resources=[f"user:{user_id}"],
                            recommendations=["Review API key usage", "Implement principle of least privilege"]
                        ))
                
                # Check for orphaned API keys
                result = session.execute(text("""
                    SELECT ak.id, ak.name, ak.user_id, ak.created_at
                    FROM api_keys ak
                    LEFT JOIN users u ON ak.user_id = u.id
                    WHERE u.id IS NULL
                """))
                
                orphaned_keys = result.fetchall()
                
                if orphaned_keys:
                    audits.append(SecurityAudit(
                        audit_id=secrets.token_hex(8),
                        timestamp=datetime.now(),
                        audit_type="authorization",
                        severity="high",
                        category="access_control",
                        description=f"Found {len(orphaned_keys)} orphaned API keys",
                        affected_resources=[f"api_key:{key[0]}" for key in orphaned_keys],
                        recommendations=["Remove orphaned API keys", "Implement key cleanup procedures"]
                    ))
                
        except Exception as e:
            logger.error(f"Authorization audit failed: {e}")
        
        return audits
    
    def _audit_data_protection(self) -> List[SecurityAudit]:
        """Audit data protection and encryption"""
        audits = []
        
        try:
            # Check for sensitive data in logs
            log_files = ['app.log', 'security.log', 'audit.log']
            
            sensitive_patterns = [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card numbers
                r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # SSN pattern
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        content = f.read()
                        
                        for pattern in sensitive_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                audits.append(SecurityAudit(
                                    audit_id=secrets.token_hex(8),
                                    timestamp=datetime.now(),
                                    audit_type="data_protection",
                                    severity="high",
                                    category="data_exposure",
                                    description=f"Sensitive data found in {log_file}",
                                    affected_resources=[log_file],
                                    recommendations=["Remove sensitive data from logs", "Implement log sanitization"]
                                ))
                                break
            
            # Check for unencrypted sensitive data
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for plain text passwords (should never happen)
                result = session.execute(text("""
                    SELECT COUNT(*) FROM users 
                    WHERE password_hash NOT LIKE '$2$%' 
                    AND password_hash NOT LIKE '$6$%'
                    AND password_hash NOT LIKE '$pbkdf2$%'
                """))
                
                plain_text_passwords = result.scalar()
                
                if plain_text_passwords > 0:
                    audits.append(SecurityAudit(
                        audit_id=secrets.token_hex(8),
                        timestamp=datetime.now(),
                        audit_type="data_protection",
                        severity="critical",
                        category="encryption",
                        description=f"Found {plain_text_passwords} accounts with unencrypted passwords",
                        affected_resources=["users table"],
                        recommendations=["Immediately encrypt all passwords", "Audit password storage procedures"]
                    ))
                
        except Exception as e:
            logger.error(f"Data protection audit failed: {e}")
        
        return audits
    
    def _audit_infrastructure(self) -> List[SecurityAudit]:
        """Audit infrastructure security"""
        audits = []
        
        try:
            # Check for default credentials
            default_credentials = [
                ('admin', 'admin'),
                ('root', 'root'),
                ('admin', 'password'),
                ('admin', '123456')
            ]
            
            # Check environment variables for sensitive data
            sensitive_env_vars = [
                'DATABASE_PASSWORD',
                'API_SECRET_KEY',
                'JWT_SECRET',
                'REDIS_PASSWORD'
            ]
            
            for env_var in sensitive_env_vars:
                if env_var in os.environ:
                    value = os.environ[env_var]
                    if len(value) < 32:  # Weak secret
                        audits.append(SecurityAudit(
                            audit_id=secrets.token_hex(8),
                            timestamp=datetime.now(),
                            audit_type="infrastructure",
                            severity="high",
                            category="credential_management",
                            description=f"Weak secret detected in {env_var}",
                            affected_resources=[f"env:{env_var}"],
                            recommendations=["Use strong secrets", "Rotate secrets regularly"]
                        ))
            
            # Check for SSL/TLS configuration
            if not os.getenv('SSL_CERT_PATH'):
                audits.append(SecurityAudit(
                    audit_id=secrets.token_hex(8),
                    timestamp=datetime.now(),
                    audit_type="infrastructure",
                    severity="medium",
                    category="encryption",
                    description="SSL/TLS not configured",
                    affected_resources=["web_server"],
                    recommendations=["Configure SSL/TLS", "Use HTTPS for all communications"]
                ))
            
        except Exception as e:
            logger.error(f"Infrastructure audit failed: {e}")
        
        return audits
    
    def _audit_compliance(self) -> List[SecurityAudit]:
        """Audit compliance requirements"""
        audits = []
        
        try:
            # Check for audit logging
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check if audit logs are being recorded
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """))
                
                recent_logs = result.scalar()
                
                if recent_logs == 0:
                    audits.append(SecurityAudit(
                        audit_id=secrets.token_hex(8),
                        timestamp=datetime.now(),
                        audit_type="compliance",
                        severity="medium",
                        category="audit_trail",
                        description="No audit logs recorded in last 24 hours",
                        affected_resources=["audit_logs"],
                        recommendations=["Enable audit logging", "Verify log configuration"]
                    ))
                
                # Check for data retention policies
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs 
                    WHERE created_at < NOW() - INTERVAL '365 days'
                """))
                
                old_logs = result.scalar()
                
                if old_logs > 10000:
                    audits.append(SecurityAudit(
                        audit_id=secrets.token_hex(8),
                        timestamp=datetime.now(),
                        audit_type="compliance",
                        severity="low",
                        category="data_retention",
                        description=f"Found {old_logs} audit logs older than 1 year",
                        affected_resources=["audit_logs"],
                        recommendations=["Implement data retention policy", "Archive old logs"]
                    ))
                
        except Exception as e:
            logger.error(f"Compliance audit failed: {e}")
        
        return audits
    
    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get audit summary for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            recent_audits = [a for a in self.audits if a.timestamp >= cutoff_date]
        
        if not recent_audits:
            return {
                'period_days': days,
                'total_audits': 0,
                'by_severity': {},
                'by_category': {},
                'by_status': {}
            }
        
        # Group by severity
        by_severity = defaultdict(int)
        for audit in recent_audits:
            by_severity[audit.severity] += 1
        
        # Group by category
        by_category = defaultdict(int)
        for audit in recent_audits:
            by_category[audit.category] += 1
        
        # Group by status
        by_status = defaultdict(int)
        for audit in recent_audits:
            by_status[audit.status] += 1
        
        return {
            'period_days': days,
            'total_audits': len(recent_audits),
            'by_severity': dict(by_severity),
            'by_category': dict(by_category),
            'by_status': dict(by_status),
            'critical_issues': len([a for a in recent_audits if a.severity == 'critical']),
            'high_issues': len([a for a in recent_audits if a.severity == 'high']),
            'resolution_rate': (len([a for a in recent_audits if a.status == 'resolved']) / len(recent_audits)) * 100
        }

class VulnerabilityScanner:
    """Vulnerability scanning and assessment"""
    
    def __init__(self):
        self.vulnerabilities = deque(maxlen=500)
        self.scan_results = {}
        self.lock = threading.RLock()
        
    def scan_dependencies(self) -> List[Vulnerability]:
        """Scan dependencies for known vulnerabilities"""
        logger.info("Starting dependency vulnerability scan")
        
        vulnerabilities = []
        
        try:
            # Check for common vulnerable dependencies
            vulnerable_packages = {
                'requests': '<2.25.0',
                'urllib3': '<1.26.0',
                'flask': '<1.0',
                'sqlalchemy': '<1.4.0',
                'redis': '<3.5.0',
                'psycopg2': '<2.8.0'
            }
            
            for package, vulnerable_version in vulnerable_packages.items():
                try:
                    # Try to import and check version
                    module = __import__(package)
                    version = getattr(module, '__version__', 'unknown')
                    
                    # This is a simplified check - in practice, you'd use proper version comparison
                    if version != 'unknown' and 'dev' not in version:
                        vulnerabilities.append(Vulnerability(
                            vuln_id=secrets.token_hex(8),
                            cve_id=None,
                            severity="medium",
                            cvss_score=5.5,
                            title=f"Potentially vulnerable {package} version",
                            description=f"Package {package} version {version} may have known vulnerabilities",
                            affected_components=[f"package:{package}"],
                            discovered_at=datetime.now(),
                            remediation_steps=[f"Upgrade {package} to latest stable version"]
                        ))
                        
                except ImportError:
                    continue
            
            # Store vulnerabilities
            with self.lock:
                self.vulnerabilities.extend(vulnerabilities)
            
            logger.info(f"Dependency scan completed: {len(vulnerabilities)} vulnerabilities found")
            
        except Exception as e:
            logger.error(f"Dependency scan failed: {e}")
        
        return vulnerabilities
    
    def scan_configuration(self) -> List[Vulnerability]:
        """Scan configuration for security issues"""
        logger.info("Starting configuration vulnerability scan")
        
        vulnerabilities = []
        
        try:
            # Check for insecure configurations
            insecure_configs = {
                'DEBUG': 'True',
                'ALLOWED_HOSTS': ['*'],
                'CORS_ALLOW_ALL_ORIGINS': 'True',
                'SECURE_SSL_REDIRECT': 'False',
                'SESSION_COOKIE_SECURE': 'False'
            }
            
            for config_key, insecure_value in insecure_configs.items():
                current_value = os.getenv(config_key)
                
                if current_value == insecure_value:
                    vulnerabilities.append(Vulnerability(
                        vuln_id=secrets.token_hex(8),
                        cve_id=None,
                        severity="medium",
                        cvss_score=4.5,
                        title=f"Insecure configuration: {config_key}",
                        description=f"Configuration {config_key} is set to insecure value",
                        affected_components=[f"config:{config_key}"],
                        discovered_at=datetime.now(),
                        remediation_steps=[f"Update {config_key} to secure value"]
                    ))
            
            # Store vulnerabilities
            with self.lock:
                self.vulnerabilities.extend(vulnerabilities)
            
            logger.info(f"Configuration scan completed: {len(vulnerabilities)} vulnerabilities found")
            
        except Exception as e:
            logger.error(f"Configuration scan failed: {e}")
        
        return vulnerabilities
    
    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """Get vulnerability summary"""
        with self.lock:
            vulns = list(self.vulnerabilities)
        
        if not vulns:
            return {
                'total_vulnerabilities': 0,
                'by_severity': {},
                'by_status': {},
                'critical_count': 0,
                'high_count': 0
            }
        
        # Group by severity
        by_severity = defaultdict(int)
        for vuln in vulns:
            by_severity[vuln.severity] += 1
        
        # Group by status
        by_status = defaultdict(int)
        for vuln in vulns:
            by_status[vuln.status] += 1
        
        return {
            'total_vulnerabilities': len(vulns),
            'by_severity': dict(by_severity),
            'by_status': dict(by_status),
            'critical_count': len([v for v in vulns if v.severity == 'critical']),
            'high_count': len([v for v in vulns if v.severity == 'high']),
            'patched_count': len([v for v in vulns if v.status == 'patched']),
            'open_count': len([v for v in vulns if v.status == 'open'])
        }

# Global security instances
security_auditor = SecurityAuditor()
vulnerability_scanner = VulnerabilityScanner()

def run_security_audit(audit_type: str = "comprehensive") -> List[SecurityAudit]:
    """Run security audit"""
    return security_auditor.run_security_audit(audit_type)

def scan_vulnerabilities() -> List[Vulnerability]:
    """Scan for vulnerabilities"""
    vulnerabilities = []
    vulnerabilities.extend(vulnerability_scanner.scan_dependencies())
    vulnerabilities.extend(vulnerability_scanner.scan_configuration())
    return vulnerabilities

def get_security_report() -> Dict[str, Any]:
    """Get comprehensive security report"""
    return {
        'timestamp': datetime.now().isoformat(),
        'audit_summary': security_auditor.get_audit_summary(),
        'vulnerability_summary': vulnerability_scanner.get_vulnerability_summary(),
        'security_policies': security_auditor.security_policies
    }
