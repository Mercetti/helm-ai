// ===================================
// STELLAR LOGIC AI - AUTOMATED UI TESTING
// ===================================

class AutomatedUITester {
    constructor() {
        this.testResults = [];
        this.currentUrl = window.location.href;
        this.testPages = [
            'index.html',
            'dashboard.html',
            'crm.html',
            'ai_assistant.html',
            'study_guide.html'
        ];
    }

    // Run comprehensive tests across all pages
    async runComprehensiveTests() {
        console.log('🚀 Starting comprehensive UI testing...');
        
        const results = {
            timestamp: new Date().toISOString(),
            url: this.currentUrl,
            tests: {},
            summary: {
                total: 0,
                passed: 0,
                failed: 0,
                warnings: 0
            }
        };

        // Test current page
        results.tests[this.getPageName()] = await this.testPage(this.currentUrl);
        
        // Update summary
        Object.values(results.tests).forEach(pageResults => {
            pageResults.forEach(result => {
                results.summary.total++;
                if (result.status === 'pass') {
                    results.summary.passed++;
                } else if (result.status === 'fail') {
                    results.summary.failed++;
                } else {
                    results.summary.warnings++;
                }
            });
        });

        console.log('📊 Test Results:', results);
        this.displayResults(results);
        return results;
    }

    // Get page name from URL
    getPageName(url = this.currentUrl) {
        const path = new URL(url).pathname;
        return path.split('/').pop() || 'index.html';
    }

    // Test individual page
    async testPage(url) {
        const pageResults = [];
        
        // Button Tests
        pageResults.push(...await this.testButtons());
        
        // Link Tests
        pageResults.push(...await this.testLinks());
        
        // Navigation Tests
        pageResults.push(...await this.testNavigation());
        
        // Form Tests
        pageResults.push(...await this.testForms());
        
        // Accessibility Tests
        pageResults.push(...await this.testAccessibility());
        
        // Performance Tests
        pageResults.push(...await this.testPerformance());
        
        // Visual Tests
        pageResults.push(...await this.testVisualElements());
        
        return pageResults;
    }

    // Test all buttons on the page
    async testButtons() {
        const results = [];
        const buttons = document.querySelectorAll('button, [role="button"]');
        
        results.push({
            category: 'Buttons',
            name: 'Button Count',
            status: buttons.length > 0 ? 'pass' : 'warning',
            message: `Found ${buttons.length} buttons`,
            details: { count: buttons.length }
        });

        // Test each button
        buttons.forEach((button, index) => {
            const hasClickHandler = button.onclick || button.addEventListener;
            const hasText = button.textContent.trim() !== '' || button.getAttribute('aria-label');
            const isVisible = this.isVisible(button);
            
            results.push({
                category: 'Buttons',
                name: `Button ${index + 1} Functionality`,
                status: hasClickHandler && hasText && isVisible ? 'pass' : 'fail',
                message: `Button ${index + 1}: ${hasClickHandler ? '✓' : '✗'} handler, ${hasText ? '✓' : '✗'} text, ${isVisible ? '✓' : '✗'} visible`,
                details: {
                    element: button.tagName,
                    text: button.textContent.trim().substring(0, 50),
                    hasHandler: !!hasClickHandler,
                    hasText: !!hasText,
                    isVisible: isVisible
                }
            });
        });

        return results;
    }

    // Test all links on the page
    async testLinks() {
        const results = [];
        const links = document.querySelectorAll('a[href]');
        
        results.push({
            category: 'Links',
            name: 'Link Count',
            status: links.length > 0 ? 'pass' : 'warning',
            message: `Found ${links.length} links`,
            details: { count: links.length }
        });

        // Test each link
        links.forEach((link, index) => {
            const href = link.getAttribute('href');
            const hasText = link.textContent.trim() !== '';
            const isExternal = href.startsWith('http');
            const hasTargetBlank = isExternal && link.getAttribute('target') === '_blank';
            const isVisible = this.isVisible(link);
            
            let status = 'pass';
            if (!hasText && !link.getAttribute('aria-label')) {
                status = 'fail';
            } else if (isExternal && !hasTargetBlank) {
                status = 'warning';
            } else if (!isVisible) {
                status = 'warning';
            }
            
            results.push({
                category: 'Links',
                name: `Link ${index + 1} Validation`,
                status: status,
                message: `Link ${index + 1}: ${hasText ? '✓' : '✗'} text, ${isVisible ? '✓' : '✗'} visible, ${isExternal ? (hasTargetBlank ? '✓' : '✗') : '—'} external handling`,
                details: {
                    href: href,
                    text: link.textContent.trim().substring(0, 50),
                    isExternal: isExternal,
                    hasTargetBlank: hasTargetBlank,
                    isVisible: isVisible
                }
            });
        });

        return results;
    }

    // Test navigation elements
    async testNavigation() {
        const results = [];
        
        // Test main navigation
        const nav = document.querySelector('nav, [role="navigation"]');
        results.push({
            category: 'Navigation',
            name: 'Main Navigation Present',
            status: nav ? 'pass' : 'warning',
            message: nav ? 'Main navigation found' : 'No main navigation found',
            details: { hasNav: !!nav }
        });

        if (nav) {
            const navLinks = nav.querySelectorAll('a');
            results.push({
                category: 'Navigation',
                name: 'Navigation Links',
                status: navLinks.length > 0 ? 'pass' : 'fail',
                message: `Navigation has ${navLinks.length} links`,
                details: { linkCount: navLinks.length }
            });
        }

        // Test mobile navigation
        const mobileMenu = document.querySelector('.mobile-menu, [data-mobile-menu]');
        const mobileToggle = document.querySelector('[data-toggle-mobile], .mobile-menu-toggle');
        
        results.push({
            category: 'Navigation',
            name: 'Mobile Navigation',
            status: (mobileMenu && mobileToggle) || (!mobileMenu && !mobileToggle) ? 'pass' : 'fail',
            message: mobileMenu ? 'Mobile navigation present' : 'No mobile navigation required',
            details: { hasMobileMenu: !!mobileMenu, hasToggle: !!mobileToggle }
        });

        // Test breadcrumbs
        const breadcrumbs = document.querySelector('.breadcrumb, [role="navigation"][aria-label*="breadcrumb"]');
        results.push({
            category: 'Navigation',
            name: 'Breadcrumb Navigation',
            status: breadcrumbs ? 'pass' : 'pass', // Breadcrumbs are optional
            message: breadcrumbs ? 'Breadcrumbs found' : 'No breadcrumbs (optional)',
            details: { hasBreadcrumbs: !!breadcrumbs }
        });

        return results;
    }

    // Test form elements
    async testForms() {
        const results = [];
        const forms = document.querySelectorAll('form');
        
        results.push({
            category: 'Forms',
            name: 'Form Count',
            status: 'pass', // Forms are optional
            message: `Found ${forms.length} forms`,
            details: { count: forms.length }
        });

        forms.forEach((form, formIndex) => {
            const inputs = form.querySelectorAll('input, select, textarea');
            const requiredInputs = form.querySelectorAll('[required]');
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            const hasLabels = this.checkFormLabels(form);
            
            results.push({
                category: 'Forms',
                name: `Form ${formIndex + 1} Structure`,
                status: (inputs.length > 0 && hasLabels && submitButton) ? 'pass' : 'warning',
                message: `Form ${formIndex + 1}: ${inputs.length} inputs, ${requiredInputs.length} required, ${hasLabels ? '✓' : '✗'} labels, ${submitButton ? '✓' : '✗'} submit`,
                details: {
                    inputCount: inputs.length,
                    requiredCount: requiredInputs.length,
                    hasLabels: hasLabels,
                    hasSubmit: !!submitButton
                }
            });
        });

        return results;
    }

    // Test accessibility features
    async testAccessibility() {
        const results = [];
        
        // Test image alt text
        const images = document.querySelectorAll('img');
        const imagesWithAlt = Array.from(images).filter(img => img.alt !== undefined);
        const imagesMissingAlt = images.length - imagesWithAlt.length;
        
        results.push({
            category: 'Accessibility',
            name: 'Image Alt Text',
            status: imagesMissingAlt === 0 ? 'pass' : (imagesMissingAlt <= 2 ? 'warning' : 'fail'),
            message: `${imagesWithAlt.length}/${images.length} images have alt text`,
            details: { 
                total: images.length, 
                withAlt: imagesWithAlt.length, 
                missingAlt: imagesMissingAlt 
            }
        });

        // Test heading structure
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const hasH1 = document.querySelector('h1');
        let properStructure = true;
        let previousLevel = 0;
        
        headings.forEach(heading => {
            const level = parseInt(heading.tagName.substring(1));
            if (previousLevel > 0 && level > previousLevel + 1) {
                properStructure = false;
            }
            previousLevel = level;
        });
        
        results.push({
            category: 'Accessibility',
            name: 'Heading Structure',
            status: hasH1 && properStructure ? 'pass' : 'warning',
            message: `${hasH1 ? '✓' : '✗'} H1 present, ${properStructure ? '✓' : '✗'} proper hierarchy`,
            details: { 
                hasH1: !!hasH1, 
                properStructure: properStructure, 
                totalHeadings: headings.length 
            }
        });

        // Test focus management
        const focusableElements = document.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        results.push({
            category: 'Accessibility',
            name: 'Focus Management',
            status: focusableElements.length > 0 ? 'pass' : 'warning',
            message: `${focusableElements.length} focusable elements found`,
            details: { focusableCount: focusableElements.length }
        });

        // Test ARIA labels
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
        const elementsWithAria = Array.from(interactiveElements).filter(el => 
            el.getAttribute('aria-label') || 
            el.getAttribute('aria-labelledby') || 
            el.textContent.trim() !== ''
        );
        
        results.push({
            category: 'Accessibility',
            name: 'ARIA Labels',
            status: elementsWithAria.length === interactiveElements.length ? 'pass' : 'warning',
            message: `${elementsWithAria.length}/${interactiveElements.length} interactive elements have labels`,
            details: { 
                total: interactiveElements.length, 
                withLabels: elementsWithAria.length 
            }
        });

        return results;
    }

    // Test performance aspects
    async testPerformance() {
        const results = [];
        
        // Test page load time
        const loadTime = performance.now();
        const acceptableLoadTime = 3000; // 3 seconds
        
        results.push({
            category: 'Performance',
            name: 'Page Load Time',
            status: loadTime < acceptableLoadTime ? 'pass' : 'warning',
            message: `Page loaded in ${Math.round(loadTime)}ms`,
            details: { loadTime: Math.round(loadTime), threshold: acceptableLoadTime }
        });

        // Test image optimization
        const images = document.querySelectorAll('img');
        const optimizedImages = Array.from(images).filter(img => 
            img.loading === 'lazy' || 
            img.src.startsWith('data:image') ||
            img.src.includes('.webp')
        );
        
        results.push({
            category: 'Performance',
            name: 'Image Optimization',
            status: optimizedImages.length > 0 ? 'pass' : 'warning',
            message: `${optimizedImages.length}/${images.length} images are optimized`,
            details: { 
                total: images.length, 
                optimized: optimizedImages.length 
            }
        });

        // Test resource loading
        const resources = performance.getEntriesByType('resource');
        const slowResources = resources.filter(r => r.duration > 1000);
        
        results.push({
            category: 'Performance',
            name: 'Resource Loading',
            status: slowResources.length < 3 ? 'pass' : 'warning',
            message: `${slowResources.length} resources loaded slowly (>1s)`,
            details: { 
                totalResources: resources.length, 
                slowResources: slowResources.length 
            }
        });

        return results;
    }

    // Test visual elements
    async testVisualElements() {
        const results = [];
        
        // Test responsive design
        const hasViewportMeta = document.querySelector('meta[name="viewport"]');
        results.push({
            category: 'Visual',
            name: 'Responsive Design',
            status: hasViewportMeta ? 'pass' : 'fail',
            message: hasViewportMeta ? 'Viewport meta tag present' : 'Missing viewport meta tag',
            details: { hasViewportMeta: !!hasViewportMeta }
        });

        // Test CSS consistency
        const buttons = document.querySelectorAll('button');
        const consistentButtons = buttons.length <= 1 || this.checkButtonConsistency(buttons);
        
        results.push({
            category: 'Visual',
            name: 'Button Consistency',
            status: consistentButtons ? 'pass' : 'warning',
            message: `Buttons are ${consistentButtons ? 'consistent' : 'inconsistent'} in styling`,
            details: { 
                buttonCount: buttons.length, 
                consistent: consistentButtons 
            }
        });

        // Test color contrast (basic check)
        const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
        const hasGoodContrast = this.checkColorContrast(textElements);
        
        results.push({
            category: 'Visual',
            name: 'Color Contrast',
            status: hasGoodContrast ? 'pass' : 'warning',
            message: `Color contrast appears ${hasGoodContrast ? 'adequate' : 'potentially low'}`,
            details: { 
                elementsChecked: textElements.length, 
                adequateContrast: hasGoodContrast 
            }
        });

        return results;
    }

    // Helper methods
    isVisible(element) {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0' &&
               element.offsetWidth > 0 && 
               element.offsetHeight > 0;
    }

    checkFormLabels(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let allHaveLabels = true;
        
        inputs.forEach(input => {
            const hasLabel = document.querySelector(`label[for="${input.id}"]`) ||
                           input.closest('label') ||
                           input.getAttribute('aria-label') ||
                           input.getAttribute('aria-labelledby');
            if (!hasLabel) {
                allHaveLabels = false;
            }
        });
        
        return allHaveLabels;
    }

    checkButtonConsistency(buttons) {
        if (buttons.length <= 1) return true;
        
        const firstButtonStyle = window.getComputedStyle(buttons[0]);
        const consistentButtons = Array.from(buttons).every(button => {
            const style = window.getComputedStyle(button);
            return style.padding === firstButtonStyle.padding &&
                   style.borderRadius === firstButtonStyle.borderRadius &&
                   style.fontFamily === firstButtonStyle.fontFamily;
        });
        
        return consistentButtons;
    }

    checkColorContrast(elements) {
        // Basic contrast check - this is simplified
        // In production, you'd use a proper contrast calculation library
        let goodContrastCount = 0;
        
        elements.slice(0, 10).forEach(element => { // Check first 10 elements for performance
            const style = window.getComputedStyle(element);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            // Simple heuristic: if both are defined and not too similar
            if (color && backgroundColor && 
                color !== 'rgb(0, 0, 0)' && 
                backgroundColor !== 'rgb(255, 255, 255)' &&
                color !== backgroundColor) {
                goodContrastCount++;
            }
        });
        
        return goodContrastCount > Math.min(elements.length, 10) * 0.7;
    }

    // Display results in a formatted way
    displayResults(results) {
        console.log('='.repeat(60));
        console.log('🧪 STELLAR LOGIC AI - UI TEST RESULTS');
        console.log('='.repeat(60));
        console.log(`📅 Timestamp: ${results.timestamp}`);
        console.log(`🌐 URL: ${results.url}`);
        console.log(`📊 Summary: ${results.summary.passed} passed, ${results.summary.failed} failed, ${results.summary.warnings} warnings`);
        console.log(`✅ Success Rate: ${Math.round((results.summary.passed / results.summary.total) * 100)}%`);
        console.log('='.repeat(60));

        Object.entries(results.tests).forEach(([pageName, pageResults]) => {
            console.log(`\n📄 Page: ${pageName}`);
            console.log('-'.repeat(40));
            
            const categories = {};
            pageResults.forEach(result => {
                if (!categories[result.category]) {
                    categories[result.category] = [];
                }
                categories[result.category].push(result);
            });

            Object.entries(categories).forEach(([category, tests]) => {
                console.log(`\n🔍 ${category}:`);
                tests.forEach(test => {
                    const icon = test.status === 'pass' ? '✅' : test.status === 'fail' ? '❌' : '⚠️';
                    console.log(`  ${icon} ${test.name}: ${test.message}`);
                });
            });
        });

        console.log('\n' + '='.repeat(60));
        console.log('🎉 Test completed!');
        console.log('='.repeat(60));
    }

    // Generate HTML report
    generateHTMLReport(results) {
        const html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>UI Test Report - Stellar Logic AI</title>
            <style>
                body { font-family: 'Inter', sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; }
                .header { text-align: center; margin-bottom: 30px; }
                .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
                .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
                .summary-card h3 { margin: 0 0 10px 0; color: #6c757d; }
                .summary-card .number { font-size: 2rem; font-weight: bold; }
                .pass { color: #28a745; }
                .fail { color: #dc3545; }
                .warning { color: #ffc107; }
                .test-section { margin-bottom: 30px; }
                .test-section h2 { color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
                .test-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; margin: 5px 0; border-radius: 6px; }
                .test-item.pass { background: #d4edda; border-left: 4px solid #28a745; }
                .test-item.fail { background: #f8d7da; border-left: 4px solid #dc3545; }
                .test-item.warning { background: #fff3cd; border-left: 4px solid #ffc107; }
                .status { padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; font-weight: bold; }
                .status.pass { background: #28a745; }
                .status.fail { background: #dc3545; }
                .status.warning { background: #ffc107; color: #212529; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 UI Test Report</h1>
                    <p>Stellar Logic AI - Automated Testing Results</p>
                    <p><strong>Date:</strong> ${new Date(results.timestamp).toLocaleString()}</p>
                    <p><strong>URL:</strong> ${results.url}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>Total Tests</h3>
                        <div class="number">${results.summary.total}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Passed</h3>
                        <div class="number pass">${results.summary.passed}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Failed</h3>
                        <div class="number fail">${results.summary.failed}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Success Rate</h3>
                        <div class="number">${Math.round((results.summary.passed / results.summary.total) * 100)}%</div>
                    </div>
                </div>
                
                ${Object.entries(results.tests).map(([pageName, pageResults]) => {
                    const categories = {};
                    pageResults.forEach(result => {
                        if (!categories[result.category]) {
                            categories[result.category] = [];
                        }
                        categories[result.category].push(result);
                    });
                    
                    return `
                    <div class="test-section">
                        <h2>📄 ${pageName}</h2>
                        ${Object.entries(categories).map(([category, tests]) => `
                            <h3>🔍 ${category}</h3>
                            ${tests.map(test => `
                                <div class="test-item ${test.status}">
                                    <div>
                                        <strong>${test.name}</strong>
                                        <div style="font-size: 14px; color: #6c757d;">${test.message}</div>
                                    </div>
                                    <span class="status ${test.status}">${test.status.toUpperCase()}</span>
                                </div>
                            `).join('')}
                        `).join('')}
                    </div>
                    `;
                }).join('')}
            </div>
        </body>
        </html>`;
        
        return html;
    }
}

// Initialize and run tests
const uiTester = new AutomatedUITester();

// Global function to run tests
window.runUITests = async function() {
    console.log('🚀 Starting UI Tests...');
    const results = await uiTester.runComprehensiveTests();
    
    // Generate HTML report
    const htmlReport = uiTester.generateHTMLReport(results);
    const blob = new Blob([htmlReport], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    // Open report in new window
    window.open(url, '_blank');
    
    return results;
};

// Auto-run tests if on test page
if (window.location.pathname.includes('test')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            runUITests();
        }, 1000);
    });
}

// Export for use in other scripts
window.StellarLogicAI = window.StellarLogicAI || {};
window.StellarLogicAI.UITester = AutomatedUITester;
window.StellarLogicAI.uiTester = uiTester;
