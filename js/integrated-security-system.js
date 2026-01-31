// ===================================
// STELLOR LOGIC AI - INTEGRATED SECURITY SYSTEM
// ===================================
// Bridges new AI safety guardrails with existing Helm AI security infrastructure

class IntegratedSecuritySystem {
    constructor() {
        this.helmSecurity = null;
        this.aiSafetyGuardrails = null;
        this.isInitialized = false;
        
        this.initialize();
    }
    
    async initialize() {
        console.log('🔒 Initializing Integrated Security System...');
        
        // Initialize AI safety guardrails
        if (window.StellarLogicAI?.safetyGuardrails) {
            this.aiSafetyGuardrails = window.StellarLogicAI.safetyGuardrails;
            console.log('✅ AI Safety Guardrails loaded');
        }
        
        // Connect to existing Helm AI security
        await this.connectToHelmSecurity();
        
        this.isInitialized = true;
        console.log('✅ Integrated Security System initialized');
    }
    
    // Connect to existing Helm AI security infrastructure
    async connectToHelmSecurity() {
        try {
            // Check if we can access existing security reports
            const response = await fetch('/api/security/status');
            
            if (response.ok) {
                const securityData = await response.json();
                this.helmSecurity = {
                    banditReport: securityData.banditReport || null,
                    safetyReport: securityData.safetyReport || null,
                    lastSecurityScan: securityData.lastScan || null,
                    complianceStatus: securityData.compliance || 'unknown'
                };
                
                console.log('✅ Connected to existing Helm AI security system');
                this.enhanceWithAIGuardrails();
            } else {
                console.log('⚠️ Helm AI security system not accessible - using standalone mode');
            }
        } catch (error) {
            console.log('⚠️ Could not connect to Helm AI security:', error.message);
        }
    }
    
    // Enhance existing security with AI guardrails
    enhanceWithAIGuardrails() {
        if (!this.aiSafetyGuardrails) return;
        
        // Add existing security files to protection list
        const existingSecurityFiles = [
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
            'tests/run_tests.sh',
            'tests/reports/bandit-report.json',
            'tests/reports/safety-report.json'
        ];
        
        existingSecurityFiles.forEach(file => {
            this.aiSafetyGuardrails.addProtectedFile(file);
        });
        
        console.log(`✅ Protected ${existingSecurityFiles.length} existing Helm AI security files`);
    }
    
    // Run comprehensive security scan
    async runComprehensiveSecurityScan() {
        console.log('🔒 Running comprehensive security scan...');
        
        const results = {
            helmSecurity: {},
            aiSafety: {},
            integrated: {},
            timestamp: new Date().toISOString(),
            overallStatus: 'unknown'
        };
        
        // Run existing Helm AI security tests
        if (this.helmSecurity) {
            results.helmSecurity = await this.runHelmSecurityTests();
        }
        
        // Run AI safety guardrails checks
        if (this.aiSafetyGuardrails) {
            results.aiSafety = await this.runAISafetyChecks();
        }
        
        // Run integrated security tests
        results.integrated = await this.runIntegratedSecurityTests();
        
        // Calculate overall status
        results.overallStatus = this.calculateOverallStatus(results);
        
        console.log('✅ Comprehensive security scan completed');
        return results;
    }
    
    // Run existing Helm AI security tests
    async runHelmSecurityTests() {
        const results = {
            banditAnalysis: 'not_available',
            safetyCheck: 'not_available',
            complianceStatus: 'not_available'
        };
        
        try {
            // Check if Bandit report exists
            const banditResponse = await fetch('/api/security/bandit-report');
            if (banditResponse.ok) {
                const banditData = await banditResponse.json();
                results.banditAnalysis = {
                    status: banditData.results ? 'completed' : 'failed',
                    issues: banditData.results ? Object.keys(banditData.results).length : 0,
                    highSeverity: banditData.results ? 
                        Object.values(banditData.results).filter(r => r.issue_severity === 'HIGH').length : 0
                };
            }
            
            // Check if Safety report exists
            const safetyResponse = await fetch('/api/security/safety-report');
            if (safetyResponse.ok) {
                const safetyData = await safetyResponse.json();
                results.safetyCheck = {
                    status: safetyData.vulnerabilities ? 'completed' : 'failed',
                    vulnerabilities: safetyData.vulnerabilities ? safetyData.vulnerabilities.length : 0,
                    highSeverity: safetyData.vulnerabilities ? 
                        safetyData.vulnerabilities.filter(v => v.severity === 'HIGH').length : 0
                };
            }
            
            results.complianceStatus = this.helmSecurity.complianceStatus;
            
        } catch (error) {
            console.log('⚠️ Could not run Helm AI security tests:', error.message);
        }
        
        return results;
    }
    
    // Run AI safety guardrails checks
    async runAISafetyChecks() {
        if (!this.aiSafetyGuardrails) {
            return { status: 'not_available' };
        }
        
        const complianceReport = this.aiSafetyGuardrails.generateComplianceSummary();
        
        return {
            status: 'completed',
            complianceRate: complianceReport.summary.complianceRate,
            sessionStats: complianceReport.sessionStats,
            protectedFiles: complianceReport.protectedFiles.length,
            recommendations: complianceReport.recommendations
        };
    }
    
    // Run integrated security tests
    async runIntegratedSecurityTests() {
        const results = {
            crossValidation: 'not_available',
            threatDetection: 'not_available',
            incidentResponse: 'not_available'
        };
        
        try {
            // Cross-validate between Helm AI and AI safety systems
            results.crossValidation = await this.crossValidateSecuritySystems();
            
            // Test threat detection integration
            results.threatDetection = await this.testThreatDetectionIntegration();
            
            // Test incident response integration
            results.incidentResponse = await this.testIncidentResponseIntegration();
            
        } catch (error) {
            console.log('⚠️ Integrated security tests error:', error.message);
        }
        
        return results;
    }
    
    // Cross-validate security systems
    async crossValidateSecuritySystems() {
        if (!this.helmSecurity || !this.aiSafetyGuardrails) {
            return { status: 'incomplete' };
        }
        
        const validation = {
            status: 'passed',
            findings: []
        };
        
        // Check if AI safety guardrails protect Helm AI security files
        const helmSecurityFiles = [
            'src/security/security_hardening.py',
            'src/security/backup_system.py',
            'tests/run_tests.sh'
        ];
        
        for (const file of helmSecurityFiles) {
            const isProtected = this.aiSafetyGuardrails.isProtectedFile(file);
            if (!isProtected) {
                validation.findings.push({
                    file: file,
                    issue: 'not_protected_by_ai_safety',
                    severity: 'medium'
                });
                validation.status = 'warning';
            }
        }
        
        return validation;
    }
    
    // Test threat detection integration
    async testThreatDetectionIntegration() {
        try {
            // Test if AI threat detection can work with existing ML threat detection
            const response = await fetch('/api/security/threat-detection/test');
            
            if (response.ok) {
                const testData = await response.json();
                return {
                    status: 'passed',
                    integrationWorking: testData.integrationWorking || false,
                    testResults: testData
                };
            }
            
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }
    
    // Test incident response integration
    async testIncidentResponseIntegration() {
        try {
            // Test if AI safety can work with existing incident response
            const response = await fetch('/api/security/incident-response/test');
            
            if (response.ok) {
                const testData = await response.json();
                return {
                    status: 'passed',
                    integrationWorking: testData.integrationWorking || false,
                    testResults: testData
                };
            }
            
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }
    
    // Calculate overall security status
    calculateOverallStatus(results) {
        const statuses = [];
        
        if (results.helmSecurity.banditAnalysis !== 'not_available') {
            statuses.push(results.helmSecurity.banditAnalysis.status);
        }
        
        if (results.helmSecurity.safetyCheck !== 'not_available') {
            statuses.push(results.helmSecurity.safetyCheck.status);
        }
        
        if (results.aiSafety.status !== 'not_available') {
            statuses.push(results.aiSafety.status);
        }
        
        if (results.integrated.crossValidation !== 'not_available') {
            statuses.push(results.integrated.crossValidation.status);
        }
        
        // Determine overall status
        const passedCount = statuses.filter(s => s === 'passed' || s === 'completed').length;
        const totalCount = statuses.length;
        
        if (passedCount === totalCount) {
            return 'excellent';
        } else if (passedCount >= totalCount * 0.8) {
            return 'good';
        } else if (passedCount >= totalCount * 0.6) {
            return 'warning';
        } else {
            return 'critical';
        }
    }
    
    // Generate integrated security report
    generateIntegratedReport() {
        return {
            timestamp: new Date().toISOString(),
            system: 'Stellar Logic AI (Enhanced Helm AI)',
            components: {
                helmSecurity: this.helmSecurity ? 'connected' : 'standalone',
                aiSafety: this.aiSafetyGuardrails ? 'active' : 'inactive',
                integration: this.isInitialized ? 'initialized' : 'not_initialized'
            },
            recommendations: this.generateIntegratedRecommendations(),
            nextSteps: this.getNextSecuritySteps()
        };
    }
    
    // Generate integrated recommendations
    generateIntegratedRecommendations() {
        const recommendations = [];
        
        if (!this.helmSecurity) {
            recommendations.push('Connect to existing Helm AI security system');
        }
        
        if (!this.aiSafetyGuardrails) {
            recommendations.push('Initialize AI safety guardrails');
        }
        
        if (this.helmSecurity && this.aiSafetyGuardrails) {
            recommendations.push('Run comprehensive security scan');
            recommendations.push('Monitor integrated security dashboard');
        }
        
        return recommendations;
    }
    
    // Get next security steps
    getNextSecuritySteps() {
        const steps = [];
        
        if (!this.isInitialized) {
            steps.push('Initialize integrated security system');
        }
        
        if (this.isInitialized) {
            steps.push('Run comprehensive security scan');
            steps.push('Review integrated security report');
            steps.push('Address any security findings');
        }
        
        return steps;
    }
    
    // Get security dashboard data
    getSecurityDashboardData() {
        return {
            isInitialized: this.isInitialized,
            helmSecurityStatus: this.helmSecurity ? 'connected' : 'standalone',
            aiSafetyStatus: this.aiSafetyGuardrails ? 'active' : 'inactive',
            lastScan: this.lastSecurityScan || null,
            recommendations: this.generateIntegratedRecommendations()
        };
    }
    
    // Run security scan and update last scan time
    async runSecurityScan() {
        const results = await this.runComprehensiveSecurityScan();
        this.lastSecurityScan = new Date().toISOString();
        return results;
    }
}

// Initialize integrated security system
const integratedSecurity = new IntegratedSecuritySystem();

// Global access
window.StellarLogicAI = window.StellarLogicAI || {};
window.StellarLogicAI.IntegratedSecuritySystem = IntegratedSecuritySystem;
window.StellarLogicAI.integratedSecurity = integratedSecurity;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        integratedSecurity.initialize();
    });
} else {
    integratedSecurity.initialize();
}

// Global function for integrated security testing
window.runIntegratedSecurityTests = async function() {
    console.log('🔒 Running integrated security tests...');
    const results = await integratedSecurity.runComprehensiveSecurityScan();
    console.log('📊 Integrated security results:', results);
    return results;
};
