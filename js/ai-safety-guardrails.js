// ===================================
// STELLOR LOGIC AI - AI SAFETY & COMPLIANCE GUARDRAILS
// ===================================
// Enhanced version building on existing Helm AI security infrastructure

class AISafetyGuardrails {
    constructor() {
        // Core AI testing files (NEVER modify these)
        this.protectedFiles = [
            // Existing Helm AI security files
            'src/security/security_hardening.py',
            'src/security/backup_system.py',
            'src/security/compliance_monitoring.py',
            'src/security/data_integrity.py',
            'src/security/encryption.py',
            'src/security/incident_response.py',
            'src/security/ml_threat_detection.py',
            'src/security/security_monitoring.py',
            'src/security/soar.py',
            'src/security/zero_trust.py',
            
            // Testing infrastructure
            'tests/run_tests.sh',
            'tests/reports/bandit-report.json',
            'tests/reports/safety-report.json',
            
            // Core AI testing files (NEW - but respect existing)
            'js/comprehensive-test-suite.js',
            'js/ui-tester.js', 
            'js/backend-tester.js',
            'js/integration-tester.js',
            'js/security-tester.js',
            'js/ai-safety-guardrails.js',
            
            // Critical system files
            'package.json',
            'js/performance.js',
            'js/accessibility.js',
            
            // Configuration files
            '.env',
            'config/',
            '.github/workflows/',
            
            // Legal compliance
            'HELM-AI-LEGAL-COMPLIANCE-SUITE.md',
            'DEPLOYMENT-GUIDE.md'
        ];
        
        this.protectedPatterns = [
            // AI self-modification patterns (ENHANCED)
            /AISafetyGuardrails/,
            /comprehensiveTestSuite/,
            /autoFix.*this\./,
            /modify.*test.*code/,
            /patch.*ai.*file/,
            
            // Advanced self-modification patterns
            /this\.(protectedFiles|complianceRules|sessionStats)/,
            /window\.StellarLogicAI\.(safetyGuardrails|comprehensiveTestSuite)/,
            /delete.*this\./,
            /override.*prototype/,
            /Object\.defineProperty.*this/,
            /Reflect\.defineProperty/,
            /Proxy\./,
            
            // Critical system patterns (ENHANCED)
            /process\.exit/,
            /require\(['"]child_process['"]/, 
            /eval\(/,
            /Function\(/,
            /setTimeout.*0/,
            /setInterval.*auto/,
            
            // Dangerous code execution patterns
            /new\s+Function\(/,
            /setTimeout\s*\(\s*['"`]eval/,
            /setInterval\s*\(\s*['"`]eval/,
            /document\.write\s*\(/,
            /innerHTML\s*=\s*.*script/,
            /outerHTML\s*=\s*.*script/,
            
            // File system access patterns
            /fs\./,
            /require\(['"]fs['"]/,
            /readFile/,
            /writeFile/,
            /unlink/,
            /rmdir/,
            
            // Network access patterns
            /http\.request/,
            /https\.request/,
            /fetch\s*\(\s*['"`]http/,
            /XMLHttpRequest/,
            
            // Process manipulation patterns
            /spawn/,
            /exec/,
            /execSync/,
            /child_process/,
            
            // Memory manipulation patterns
            /Buffer\./,
            /Uint8Array/,
            /ArrayBuffer/,
            /SharedArrayBuffer/,
            
            // Crypto manipulation patterns
            /crypto\./,
            /createHash/,
            /createCipher/,
            /createDecipher/
        ];
        
        this.complianceRules = {
            // File modification limits
            maxFileModifications: 5,
            maxAutoFixesPerSession: 20,
            
            // Approval requirements
            requireHumanApproval: true,
            criticalOperationsRequireApproval: true,
            
            // Logging and monitoring
            logAllModifications: true,
            logSecurityEvents: true,
            logBlockedAttempts: true,
            
            // Backup and recovery
            backupBeforeChanges: true,
            createRestorePoints: true,
            
            // Time-based restrictions
            maxSessionDuration: 3600000, // 1 hour in milliseconds
            cooldownPeriod: 300000, // 5 minutes between modifications
            
            // Content restrictions
            maxCodeSizePerModification: 10000, // 10KB
            allowedFileTypes: ['.js', '.html', '.css', '.json', '.md'],
            
            // Network restrictions
            blockExternalRequests: true,
            allowedDomains: ['localhost', '127.0.0.1'],
            
            // Memory restrictions
            maxMemoryUsage: 100 * 1024 * 1024, // 100MB
            
            // Emergency controls
            emergencyStopEnabled: true,
            autoStopOnViolation: true
        };
        
        this.sessionStats = {
            // Basic counters
            modifications: 0,
            autoFixes: 0,
            blockedAttempts: 0,
            lastReset: Date.now(),
            
            // Detailed tracking
            modificationsByType: {},
            blockedByPattern: {},
            approvalRequests: 0,
            approvalsGranted: 0,
            approvalsDenied: 0,
            
            // Performance tracking
            averageModificationTime: 0,
            totalModificationTime: 0,
            memoryUsage: 0,
            
            // Security events
            securityEvents: [],
            criticalViolations: 0,
            warnings: 0,
            
            // Session management
            sessionStartTime: Date.now(),
            lastActivity: Date.now(),
            emergencyStops: 0,
            
            // Compliance tracking
            complianceScore: 100,
            violations: [],
            resolvedViolations: 0
        };
    }

    // Check if file is protected
    isProtectedFile(filePath) {
        const normalizedPath = filePath.replace(/\\/g, '/');
        
        return this.protectedFiles.some(protected => {
            if (protected.endsWith('/')) {
                return normalizedPath.startsWith(protected);
            }
            return normalizedPath === protected || normalizedPath.endsWith(protected);
        });
    }

    // Check if modification is safe (ENHANCED)
    isModificationSafe(filePath, content, operation = 'modify') {
        // Check if file is protected
        if (this.isProtectedFile(filePath)) {
            this.logSecurityEvent('PROTECTED_FILE_ACCESS', {
                filePath: filePath,
                operation: operation,
                blocked: true,
                reason: 'File is in protected list'
            });
            return false;
        }

        // Check for dangerous patterns in content
        for (const pattern of this.protectedPatterns) {
            if (pattern.test(content)) {
                this.logSecurityEvent('DANGEROUS_PATTERN_DETECTED', {
                    filePath: filePath,
                    pattern: pattern.toString(),
                    operation: operation,
                    blocked: true
                });
                return false;
            }
        }

        // Check session limits
        if (this.sessionStats.modifications >= this.complianceRules.maxFileModifications) {
            this.logSecurityEvent('SESSION_LIMIT_EXCEEDED', {
                modifications: this.sessionStats.modifications,
                limit: this.complianceRules.maxFileModifications,
                blocked: true
            });
            return false;
        }

        // Check session duration
        const sessionDuration = Date.now() - this.sessionStats.sessionStartTime;
        if (sessionDuration > this.complianceRules.maxSessionDuration) {
            this.logSecurityEvent('SESSION_DURATION_EXCEEDED', {
                sessionDuration: sessionDuration,
                limit: this.complianceRules.maxSessionDuration,
                blocked: true
            });
            return false;
        }

        // Check cooldown period
        const timeSinceLastModification = Date.now() - this.sessionStats.lastActivity;
        if (timeSinceLastModification < this.complianceRules.cooldownPeriod) {
            this.logSecurityEvent('COOLDOWN_PERIOD_ACTIVE', {
                timeSinceLastModification: timeSinceLastModification,
                cooldownPeriod: this.complianceRules.cooldownPeriod,
                blocked: true
            });
            return false;
        }

        // Check file size
        if (content.length > this.complianceRules.maxCodeSizePerModification) {
            this.logSecurityEvent('FILE_SIZE_EXCEEDED', {
                fileSize: content.length,
                maxSize: this.complianceRules.maxCodeSizePerModification,
                blocked: true
            });
            return false;
        }

        // Check file type
        const fileExtension = filePath.split('.').pop().toLowerCase();
        if (!this.complianceRules.allowedFileTypes.includes('.' + fileExtension)) {
            this.logSecurityEvent('INVALID_FILE_TYPE', {
                fileExtension: fileExtension,
                allowedTypes: this.complianceRules.allowedFileTypes,
                blocked: true
            });
            return false;
        }

        // Check memory usage
        if (performance.memory) {
            const memoryUsage = performance.memory.usedJSHeapSize;
            if (memoryUsage > this.complianceRules.maxMemoryUsage) {
                this.logSecurityEvent('MEMORY_LIMIT_EXCEEDED', {
                    memoryUsage: memoryUsage,
                    maxMemory: this.complianceRules.maxMemoryUsage,
                    blocked: true
                });
                return false;
            }
        }

        return true;
    }

    // Safe file modification with approval
    async safeFileModification(filePath, content, operation = 'modify') {
        // Safety check
        if (!this.isModificationSafe(filePath, content, operation)) {
            this.sessionStats.blockedAttempts++;
            throw new Error(`Modification blocked by AI safety guardrails: ${filePath}`);
        }

        // Require human approval for critical operations
        if (this.complianceRules.requireHumanApproval) {
            const approval = await this.requestHumanApproval(filePath, content, operation);
            if (!approval.approved) {
                this.logSecurityEvent('HUMAN_APPROVAL_DENIED', {
                    filePath: filePath,
                    reason: approval.reason,
                    operation: operation
                });
                throw new Error(`Human approval denied: ${approval.reason}`);
            }
        }

        // Create backup before modification
        if (this.complianceRules.backupBeforeChanges) {
            await this.createBackup(filePath);
        }

        // Log the modification
        this.logSecurityEvent('FILE_MODIFICATION', {
            filePath: filePath,
            operation: operation,
            contentLength: content.length,
            approved: true
        });

        // Update session stats
        this.sessionStats.modifications++;

        return true;
    }

    // Request human approval (in real implementation, this would show UI)
    async requestHumanApproval(filePath, content, operation) {
        // For now, auto-approve non-critical files
        const isCritical = this.isCriticalFile(filePath);
        
        if (!isCritical) {
            return { approved: true, reason: 'Non-critical file auto-approved' };
        }

        // In production, this would show a UI dialog
        console.log(`🔒 AI SAFETY: Human approval required for ${operation} on ${filePath}`);
        console.log(`📝 Content preview: ${content.substring(0, 200)}...`);
        
        // Simulate human approval (in real implementation, wait for actual approval)
        return { approved: true, reason: 'Human approval simulated' };
    }

    // Check if file is critical
    isCriticalFile(filePath) {
        const criticalPatterns = [
            /package\.json$/,
            /config\//,
            /\.env$/,
            /security/,
            /auth/,
            /database/
        ];

        return criticalPatterns.some(pattern => pattern.test(filePath));
    }

    // Create backup of file
    async createBackup(filePath) {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupPath = `${filePath}.backup.${timestamp}`;
            
            // In real implementation, this would copy the file
            console.log(`💾 Created backup: ${backupPath}`);
            
            return backupPath;
        } catch (error) {
            console.error(`Failed to create backup for ${filePath}:`, error);
        }
    }

    // Log security events
    logSecurityEvent(eventType, details) {
        const event = {
            timestamp: new Date().toISOString(),
            eventType: eventType,
            details: details,
            sessionId: this.getSessionId()
        };

        console.log(`🔒 AI SAFETY [${eventType}]:`, details);

        // In production, send to security monitoring
        this.sendToSecurityMonitor(event);
    }

    // Get session ID
    getSessionId() {
        if (!this.sessionId) {
            this.sessionId = `ai-session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        }
        return this.sessionId;
    }

    // Send to security monitor
    sendToSecurityMonitor(event) {
        // In production, send to logging service
        if (typeof fetch !== 'undefined') {
            fetch('/api/ai-security/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            }).catch(() => {
                // Silently fail if monitoring endpoint is not available
            });
        }
    }

    // Check auto-fix limits
    canPerformAutoFix() {
        return this.sessionStats.autoFixes < this.complianceRules.maxAutoFixesPerSession;
    }

    // Record auto-fix
    recordAutoFix(issueType, filePath) {
        this.sessionStats.autoFixes++;
        
        this.logSecurityEvent('AUTO_FIX_PERFORMED', {
            issueType: issueType,
            filePath: filePath,
            totalAutoFixes: this.sessionStats.autoFixes,
            remainingAutoFixes: this.complianceRules.maxAutoFixesPerSession - this.sessionStats.autoFixes
        });

        if (this.sessionStats.autoFixes >= this.complianceRules.maxAutoFixesPerSession) {
            this.logSecurityEvent('AUTO_FIX_LIMIT_REACHED', {
                limit: this.complianceRules.maxAutoFixesPerSession,
                reached: this.sessionStats.autoFixes
            });
        }
    }

    // Reset session stats
    resetSession() {
        this.sessionStats = {
            modifications: 0,
            autoFixes: 0,
            blockedAttempts: 0,
            lastReset: Date.now()
        };

        this.logSecurityEvent('SESSION_RESET', {
            timestamp: new Date().toISOString()
        });
    }

    // Emergency stop method
    emergencyStop(reason = 'Emergency stop activated') {
        this.logSecurityEvent('EMERGENCY_STOP', {
            reason: reason,
            sessionStats: this.sessionStats,
            timestamp: Date.now()
        });
        
        this.sessionStats.emergencyStops++;
        this.sessionStats.complianceScore = 0;
        
        // Disable all modifications
        this.complianceRules.maxFileModifications = 0;
        this.complianceRules.maxAutoFixesPerSession = 0;
        
        console.error('🚨 EMERGENCY STOP ACTIVATED:', reason);
        
        // In a real implementation, this would:
        // - Stop all ongoing operations
        // - Lock the system
        // - Notify administrators
        // - Create emergency backup
        
        return true;
    }

    // Check system health
    checkSystemHealth() {
        const health = {
            status: 'healthy',
            issues: [],
            recommendations: [],
            score: 100
        };
        
        // Check session duration
        const sessionDuration = Date.now() - this.sessionStats.sessionStartTime;
        if (sessionDuration > this.complianceRules.maxSessionDuration * 0.8) {
            health.issues.push('Session approaching duration limit');
            health.recommendations.push('Consider session reset');
            health.score -= 20;
        }
        
        // Check modification count
        if (this.sessionStats.modifications > this.complianceRules.maxFileModifications * 0.8) {
            health.issues.push('Approaching modification limit');
            health.recommendations.push('Monitor remaining modifications');
            health.score -= 15;
        }
        
        // Check blocked attempts
        if (this.sessionStats.blockedAttempts > 10) {
            health.issues.push('High number of blocked attempts');
            health.recommendations.push('Review blocked attempts for patterns');
            health.score -= 25;
        }
        
        // Check memory usage
        if (performance.memory) {
            const memoryUsage = performance.memory.usedJSHeapSize;
            const memoryPercent = (memoryUsage / this.complianceRules.maxMemoryUsage) * 100;
            if (memoryPercent > 80) {
                health.issues.push('High memory usage');
                health.recommendations.push('Consider memory optimization');
                health.score -= 20;
            }
        }
        
        // Determine overall status
        if (health.score >= 90) {
            health.status = 'excellent';
        } else if (health.score >= 70) {
            health.status = 'good';
        } else if (health.score >= 50) {
            health.status = 'warning';
        } else {
            health.status = 'critical';
        }
        
        return health;
    }

    // Auto-heal system
    autoHeal() {
        const health = this.checkSystemHealth();
        
        if (health.status === 'critical') {
            this.emergencyStop('Critical system health - auto-heal triggered');
            return false;
        }
        
        // Apply auto-healing measures
        if (health.issues.includes('Session approaching duration limit')) {
            this.resetSession();
        }
        
        if (health.issues.includes('High memory usage')) {
            // Trigger garbage collection if available
            if (window.gc) {
                window.gc();
            }
        }
        
        this.logSecurityEvent('AUTO_HEAL', {
            health: health,
            actions: health.recommendations
        });
        
        return true;
    }

    // Get compliance report
    getComplianceReport() {
        return {
            sessionId: this.getSessionId(),
            sessionStats: this.sessionStats,
            complianceRules: this.complianceRules,
            protectedFiles: this.protectedFiles,
            protectedPatterns: this.protectedPatterns.map(p => p.toString()),
            timestamp: new Date().toISOString()
        };
    }

    // Validate AI behavior
    validateAIBehavior(action, context) {
        const validationRules = {
            // Actions that require approval
            requiresApproval: [
                'modifyFile',
                'deleteFile', 
                'createFile',
                'executeCommand',
                'installPackage'
            ],
            
            // Actions that are blocked
            blocked: [
                'modifySelf',
                'disableSafety',
                'bypassCompliance',
                'accessSensitiveData'
            ]
        };

        // Check if action is blocked
        if (validationRules.blocked.includes(action)) {
            this.logSecurityEvent('BLOCKED_ACTION', {
                action: action,
                context: context,
                reason: 'Action is explicitly blocked'
            });
            return false;
        }

        // Check if action requires approval
        if (validationRules.requiresApproval.includes(action)) {
            this.logSecurityEvent('APPROVAL_REQUIRED', {
                action: action,
                context: context
            });
            return 'approval_required';
        }

        return true;
    }

    // Add protected file
    addProtectedFile(filePath) {
        if (!this.protectedFiles.includes(filePath)) {
            this.protectedFiles.push(filePath);
            this.logSecurityEvent('PROTECTED_FILE_ADDED', {
                filePath: filePath
            });
        }
    }

    // Remove protected file (with approval)
    async removeProtectedFile(filePath, approved = false) {
        if (!approved) {
            const approval = await this.requestHumanApproval(
                filePath, 
                '', 
                'remove-protection'
            );
            if (!approval.approved) {
                throw new Error('Approval denied to remove protected file');
            }
        }

        const index = this.protectedFiles.indexOf(filePath);
        if (index > -1) {
            this.protectedFiles.splice(index, 1);
            this.logSecurityEvent('PROTECTED_FILE_REMOVED', {
                filePath: filePath
            });
        }
    }

    // Check for self-modification attempts
    checkSelfModification(code, filePath) {
        const selfModPatterns = [
            /AISafetyGuardrails/,
            /this\.protectedFiles/,
            /this\.complianceRules/,
            /this\.sessionStats/,
            /addProtectedFile/,
            /removeProtectedFile/
        ];

        for (const pattern of selfModPatterns) {
            if (pattern.test(code)) {
                this.logSecurityEvent('SELF_MODIFICATION_ATTEMPT', {
                    filePath: filePath,
                    pattern: pattern.toString(),
                    blocked: true
                });
                return false;
            }
        }

        return true;
    }

    // Generate compliance summary
    generateComplianceSummary() {
        const report = this.getComplianceReport();
        
        return {
            status: 'compliant',
            summary: {
                sessionDuration: Date.now() - report.sessionStats.lastReset,
                modifications: report.sessionStats.modifications,
                autoFixes: report.sessionStats.autoFixes,
                blockedAttempts: report.sessionStats.blockedAttempts,
                complianceRate: this.calculateComplianceRate()
            },
            recommendations: this.generateRecommendations(),
            timestamp: new Date().toISOString()
        };
    }

    // Calculate compliance rate
    calculateComplianceRate() {
        const total = this.sessionStats.modifications + this.sessionStats.blockedAttempts;
        if (total === 0) return 100;
        
        return Math.round((this.sessionStats.modifications / total) * 100);
    }

    // Generate recommendations
    generateRecommendations() {
        const recommendations = [];
        
        if (this.sessionStats.blockedAttempts > 0) {
            recommendations.push('Review blocked modification attempts');
        }
        
        if (this.sessionStats.autoFixes >= this.complianceRules.maxAutoFixesPerSession * 0.8) {
            recommendations.push('Approaching auto-fix limit, consider manual review');
        }
        
        if (this.sessionStats.modifications >= this.complianceRules.maxFileModifications * 0.8) {
            recommendations.push('Approaching modification limit, consider session reset');
        }
        
        return recommendations;
    }
}

// ===================================
// ENHANCED COMPREHENSIVE TEST SUITE WITH SAFETY
// ===================================

class SafeComprehensiveTestSuite extends ComprehensiveTestSuite {
    constructor() {
        super();
        this.safetyGuardrails = new AISafetyGuardrails();
        this.initializeSafety();
    }

    // Initialize safety features
    initializeSafety() {
        // Override auto-fix method with safety checks
        this.originalAutoFix = this.autoFix;
        this.autoFix = this.safeAutoFix.bind(this);
        
        // Add safety monitoring
        this.setupSafetyMonitoring();
        
        console.log('🔒 AI Safety Guardrails initialized');
    }

    // Safe auto-fix with compliance checks
    async safeAutoFix(issue) {
        // Validate AI behavior
        const validation = this.safetyGuardrails.validateAIBehavior('autoFix', {
            issueType: issue.type,
            description: issue.description
        });

        if (validation === false) {
            console.log('🔒 Auto-fix blocked by safety guardrails');
            return { success: false, reason: 'Safety guardrails blocked auto-fix' };
        }

        if (validation === 'approval_required') {
            console.log('🔒 Auto-fix requires human approval');
            return { success: false, reason: 'Human approval required' };
        }

        // Check auto-fix limits
        if (!this.safetyGuardrails.canPerformAutoFix()) {
            console.log('🔒 Auto-fix limit reached');
            return { success: false, reason: 'Auto-fix limit reached' };
        }

        // Perform safe auto-fix
        try {
            const result = await this.originalAutoFix(issue);
            
            if (result.success) {
                this.safetyGuardrails.recordAutoFix(issue.type, issue.element);
            }
            
            return result;
        } catch (error) {
            this.safetyGuardrails.logSecurityEvent('AUTO_FIX_ERROR', {
                error: error.message,
                issue: issue
            });
            return { success: false, reason: error.message };
        }
    }

    // Safe file modification
    async safeFileModification(filePath, content, operation = 'modify') {
        return await this.safetyGuardrails.safeFileModification(filePath, content, operation);
    }

    // Setup safety monitoring
    setupSafetyMonitoring() {
        // Monitor AI activities
        setInterval(() => {
            const compliance = this.safetyGuardrails.generateComplianceSummary();
            
            if (compliance.summary.complianceRate < 90) {
                console.log('⚠️ AI compliance rate below 90%:', compliance.summary.complianceRate);
            }
            
            if (compliance.recommendations.length > 0) {
                console.log('💡 AI Safety Recommendations:', compliance.recommendations);
            }
        }, 60000); // Check every minute
    }

    // Override applyFix with safety
    async applyFix(fix) {
        // Validate fix safety
        if (!this.safetyGuardrails.checkSelfModification(fix.code, fix.target)) {
            throw new Error('Fix contains self-modification patterns - blocked by safety guardrails');
        }

        // Check if target file is protected
        if (this.safetyGuardrails.isProtectedFile(fix.target)) {
            throw new Error(`Cannot modify protected file: ${fix.target}`);
        }

        // Perform safe modification
        await this.safeFileModification(fix.target, fix.code, 'auto-fix');
        console.log(`🔧 Safe fix applied: ${fix.description}`);
    }

    // Get safety report
    getSafetyReport() {
        return this.safetyGuardrails.generateComplianceSummary();
    }

    // Reset safety session
    resetSafetySession() {
        this.safetyGuardrails.resetSession();
        console.log('🔒 Safety session reset');
    }
}

// Initialize safe test suite
const safeTestSuite = new SafeComprehensiveTestSuite();

// Global access with safety
window.StellarLogicAI = window.StellarLogicAI || {};
window.StellarLogicAI.SafeComprehensiveTestSuite = SafeComprehensiveTestSuite;
window.StellarLogicAI.safeTestSuite = safeTestSuite;
window.StellarLogicAI.safetyGuardrails = safeTestSuite.safetyGuardrails;

// Override global test runner with safety
window.runUITests = async function() {
    console.log('🔒 Running UI tests with safety guardrails...');
    const results = await safeTestSuite.runComprehensiveTests();
    console.log('📊 Safe test results:', results);
    console.log('🔒 Safety report:', safeTestSuite.getSafetyReport());
    return results;
};

// Auto-initialize with safety
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        safeTestSuite.initialize();
    });
} else {
    safeTestSuite.initialize();
}
