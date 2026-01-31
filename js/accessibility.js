// ===================================
// STELLAR LOGIC AI - ACCESSIBILITY ENHANCEMENTS
// ===================================

class AccessibilityManager {
  constructor() {
    this.announcer = null;
    this.focusTrap = null;
    this.keyboardNav = false;
    this.init();
  }

  init() {
    this.setupAnnouncer();
    this.setupKeyboardNavigation();
    this.setupFocusManagement();
    this.setupAriaLiveRegions();
    this.setupSkipLinks();
    this.setupScreenReaderSupport();
  }

  // Setup Screen Reader Announcer
  setupAnnouncer() {
    this.announcer = document.createElement('div');
    this.announcer.setAttribute('aria-live', 'polite');
    this.announcer.setAttribute('aria-atomic', 'true');
    this.announcer.className = 'sr-only';
    this.announcer.id = 'accessibility-announcer';
    document.body.appendChild(this.announcer);
  }

  // Announce messages to screen readers
  announce(message, priority = 'polite') {
    if (this.announcer) {
      this.announcer.setAttribute('aria-live', priority);
      this.announcer.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        this.announcer.textContent = '';
      }, 1000);
    }
  }

  // Setup Keyboard Navigation
  setupKeyboardNavigation() {
    // Detect keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        this.keyboardNav = true;
        document.body.classList.add('keyboard-nav');
      }
    });

    document.addEventListener('mousedown', () => {
      this.keyboardNav = false;
      document.body.classList.remove('keyboard-nav');
    });

    // Handle escape key for modals
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeCurrentModal();
      }
    });
  }

  // Setup Focus Management
  setupFocusManagement() {
    // Add focus indicators
    document.addEventListener('focusin', (e) => {
      e.target.classList.add('focus-visible');
    });

    document.addEventListener('focusout', (e) => {
      e.target.classList.remove('focus-visible');
    });

    // Trap focus in modals
    this.setupFocusTrap();
  }

  // Setup Focus Trap for Modals
  setupFocusTrap() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
      modal.addEventListener('open', () => {
        this.trapFocus(modal);
      });
      
      modal.addEventListener('close', () => {
        this.removeFocusTrap(modal);
      });
    });
  }

  trapFocus(element) {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;

    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    this.focusTrap = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
          }
        }
      }
    };

    element.addEventListener('keydown', this.focusTrap);
    firstFocusable.focus();
  }

  removeFocusTrap(element) {
    if (this.focusTrap) {
      element.removeEventListener('keydown', this.focusTrap);
      this.focusTrap = null;
    }
  }

  // Setup ARIA Live Regions
  setupAriaLiveRegions() {
    // Create live regions for dynamic content
    const liveRegions = [
      { id: 'status-live', politeness: 'polite' },
      { id: 'alert-live', politeness: 'assertive' },
      { id: 'progress-live', politeness: 'polite' }
    ];

    liveRegions.forEach(region => {
      const liveRegion = document.createElement('div');
      liveRegion.id = region.id;
      liveRegion.setAttribute('aria-live', region.politeness);
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      document.body.appendChild(liveRegion);
    });
  }

  // Setup Skip Links
  setupSkipLinks() {
    const skipLinks = [
      { href: '#main', text: 'Skip to main content' },
      { href: '#navigation', text: 'Skip to navigation' },
      { href: '#footer', text: 'Skip to footer' }
    ];

    const skipLinksContainer = document.createElement('div');
    skipLinksContainer.className = 'skip-links';

    skipLinks.forEach(link => {
      const skipLink = document.createElement('a');
      skipLink.href = link.href;
      skipLink.textContent = link.text;
      skipLink.className = 'skip-link';
      skipLinksContainer.appendChild(skipLink);
    });

    document.body.insertBefore(skipLinksContainer, document.body.firstChild);
  }

  // Setup Screen Reader Support
  setupScreenReaderSupport() {
    // Add landmarks
    this.addLandmarks();
    
    // Setup form validation
    this.setupFormValidation();
    
    // Setup table accessibility
    this.setupTableAccessibility();
    
    // Setup carousel accessibility
    this.setupCarouselAccessibility();
  }

  // Add Semantic Landmarks
  addLandmarks() {
    const main = document.querySelector('main') || document.querySelector('[role="main"]');
    if (main && !main.hasAttribute('aria-label')) {
      main.setAttribute('aria-label', 'Main content');
    }

    const nav = document.querySelector('nav') || document.querySelector('[role="navigation"]');
    if (nav && !nav.hasAttribute('aria-label')) {
      nav.setAttribute('aria-label', 'Main navigation');
    }

    const header = document.querySelector('header') || document.querySelector('[role="banner"]');
    if (header && !header.hasAttribute('aria-label')) {
      header.setAttribute('aria-label', 'Site header');
    }

    const footer = document.querySelector('footer') || document.querySelector('[role="contentinfo"]');
    if (footer && !footer.hasAttribute('aria-label')) {
      footer.setAttribute('aria-label', 'Site footer');
    }
  }

  // Setup Form Validation
  setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
          this.announce('Please correct the errors in the form', 'assertive');
        }
      });

      // Real-time validation
      const inputs = form.querySelectorAll('input, select, textarea');
      inputs.forEach(input => {
        input.addEventListener('blur', () => {
          this.validateField(input);
        });
      });
    });
  }

  validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });

    return isValid;
  }

  validateField(field) {
    const isValid = field.checkValidity();
    const errorMessage = field.parentElement.querySelector('.error-message');
    
    if (!isValid) {
      field.classList.add('error-input');
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', field.id + '-error');
      
      if (errorMessage) {
        errorMessage.textContent = field.validationMessage;
        errorMessage.style.display = 'block';
      }
    } else {
      field.classList.remove('error-input');
      field.setAttribute('aria-invalid', 'false');
      
      if (errorMessage) {
        errorMessage.style.display = 'none';
      }
    }

    return isValid;
  }

  // Setup Table Accessibility
  setupTableAccessibility() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
      // Add caption if missing
      if (!table.querySelector('caption')) {
        const caption = document.createElement('caption');
        caption.textContent = 'Data table';
        table.insertBefore(caption, table.firstChild);
      }

      // Add headers
      const headers = table.querySelectorAll('th');
      headers.forEach((header, index) => {
        if (!header.id) {
          header.id = `header-${index}`;
        }
        header.setAttribute('scope', 'col');
      });

      // Link cells to headers
      const cells = table.querySelectorAll('td');
      cells.forEach((cell, rowIndex) => {
        const headerId = `header-${cell.cellIndex}`;
        cell.setAttribute('headers', headerId);
      });
    });
  }

  // Setup Carousel Accessibility
  setupCarouselAccessibility() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
      const slides = carousel.querySelectorAll('.carousel-slide');
      const controls = carousel.querySelectorAll('.carousel-control');
      
      // Add labels to slides
      slides.forEach((slide, index) => {
        slide.setAttribute('aria-label', `Slide ${index + 1} of ${slides.length}`);
        slide.setAttribute('role', 'group');
        slide.setAttribute('aria-roledescription', 'slide');
      });

      // Add labels to controls
      controls.forEach((control, index) => {
        if (control.classList.contains('prev')) {
          control.setAttribute('aria-label', 'Previous slide');
        } else if (control.classList.contains('next')) {
          control.setAttribute('aria-label', 'Next slide');
        }
      });

      // Announce slide changes
      let currentSlide = 0;
      const observer = new MutationObserver(() => {
        const newSlide = Array.from(slides).findIndex(slide => 
          slide.style.transform === 'translateX(0px)'
        );
        
        if (newSlide !== currentSlide && newSlide !== -1) {
          currentSlide = newSlide;
          this.announce(`Slide ${newSlide + 1} of ${slides.length}`);
        }
      });

      observer.observe(carousel.querySelector('.carousel-track'), {
        attributes: true,
        attributeFilter: ['style']
      });
    });
  }

  // Modal Management
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      
      // Focus management
      this.trapFocus(modal);
      
      // Announce to screen readers
      this.announce('Modal opened');
      
      // Emit custom event
      modal.dispatchEvent(new CustomEvent('open'));
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      
      // Remove focus trap
      this.removeFocusTrap(modal);
      
      // Return focus to trigger
      const trigger = document.querySelector(`[data-modal-target="${modalId}"]`);
      if (trigger) {
        trigger.focus();
      }
      
      // Announce to screen readers
      this.announce('Modal closed');
      
      // Emit custom event
      modal.dispatchEvent(new CustomEvent('close'));
    }
  }

  closeCurrentModal() {
    const openModal = document.querySelector('.modal.open');
    if (openModal) {
      this.closeModal(openModal.id);
    }
  }

  // Tab Management
  activateTab(tabId, panelId) {
    // Deactivate all tabs and panels
    document.querySelectorAll('.tab-button').forEach(tab => {
      tab.setAttribute('aria-selected', 'false');
      tab.setAttribute('tabindex', '-1');
    });
    
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.setAttribute('aria-hidden', 'true');
    });
    
    // Activate selected tab and panel
    const selectedTab = document.getElementById(tabId);
    const selectedPanel = document.getElementById(panelId);
    
    if (selectedTab && selectedPanel) {
      selectedTab.setAttribute('aria-selected', 'true');
      selectedTab.setAttribute('tabindex', '0');
      selectedPanel.setAttribute('aria-hidden', 'false');
      
      // Announce to screen readers
      this.announce(`Tab ${selectedTab.textContent} activated`);
      
      // Focus the tab
      selectedTab.focus();
    }
  }

  // Accordion Management
  toggleAccordion(buttonId) {
    const button = document.getElementById(buttonId);
    const panel = document.getElementById(button.getAttribute('aria-controls'));
    
    if (button && panel) {
      const isExpanded = button.getAttribute('aria-expanded') === 'true';
      
      button.setAttribute('aria-expanded', !isExpanded);
      panel.setAttribute('aria-hidden', isExpanded);
      
      // Announce to screen readers
      const state = isExpanded ? 'collapsed' : 'expanded';
      this.announce(`Accordion ${button.textContent} ${state}`);
    }
  }

  // Progress Bar Updates
  updateProgress(progressId, value, max = 100) {
    const progressBar = document.getElementById(progressId);
    const progressFill = progressBar?.querySelector('.progress-fill');
    const progressLabel = progressBar?.querySelector('.progress-label');
    
    if (progressBar && progressFill) {
      const percentage = Math.round((value / max) * 100);
      progressFill.style.width = `${percentage}%`;
      progressBar.setAttribute('aria-valuenow', value);
      progressBar.setAttribute('aria-valuemin', 0);
      progressBar.setAttribute('aria-valuemax', max);
      
      // Update label if exists
      if (progressLabel) {
        progressLabel.textContent = `${percentage}% complete`;
      }
      
      // Announce to screen readers
      this.announce(`Progress: ${percentage}% complete`);
    }
  }

  // Get Accessibility Report
  getAccessibilityReport() {
    const report = {
      timestamp: Date.now(),
      url: window.location.href,
      checks: {
        images: this.checkImageAltText(),
        forms: this.checkFormLabels(),
        headings: this.checkHeadingStructure(),
        links: this.checkLinkText(),
        colorContrast: this.checkColorContrast(),
        focusable: this.checkFocusableElements(),
        landmarks: this.checkLandmarks()
      }
    };
    
    return report;
  }

  checkImageAltText() {
    const images = document.querySelectorAll('img');
    const issues = [];
    
    images.forEach((img, index) => {
      if (!img.alt && img.alt !== '') {
        issues.push({
          element: 'img',
          index: index,
          issue: 'Missing alt text',
          src: img.src
        });
      }
    });
    
    return { total: images.length, issues };
  }

  checkFormLabels() {
    const inputs = document.querySelectorAll('input, select, textarea');
    const issues = [];
    
    inputs.forEach((input, index) => {
      const hasLabel = document.querySelector(`label[for="${input.id}"]`) || 
                      input.closest('label') ||
                      input.getAttribute('aria-label') ||
                      input.getAttribute('aria-labelledby');
      
      if (!hasLabel) {
        issues.push({
          element: input.tagName,
          index: index,
          issue: 'Missing label',
          type: input.type,
          name: input.name
        });
      }
    });
    
    return { total: inputs.length, issues };
  }

  checkHeadingStructure() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const issues = [];
    let previousLevel = 0;
    
    headings.forEach((heading, index) => {
      const currentLevel = parseInt(heading.tagName.substring(1));
      
      if (currentLevel > previousLevel + 1) {
        issues.push({
          element: heading.tagName,
          index: index,
          issue: `Heading level skipped from ${previousLevel} to ${currentLevel}`,
          text: heading.textContent.substring(0, 50)
        });
      }
      
      previousLevel = currentLevel;
    });
    
    return { total: headings.length, issues };
  }

  checkLinkText() {
    const links = document.querySelectorAll('a[href]');
    const issues = [];
    
    links.forEach((link, index) => {
      const text = link.textContent.trim();
      
      if (text === '' || text === 'click here' || text === 'read more') {
        issues.push({
          element: 'a',
          index: index,
          issue: 'Poor link text',
          text: text,
          href: link.href
        });
      }
    });
    
    return { total: links.length, issues };
  }

  checkColorContrast() {
    // This would require a color contrast library
    // For now, return placeholder
    return { 
      total: 0, 
      issues: [],
      note: 'Color contrast checking requires additional library'
    };
  }

  checkFocusableElements() {
    const focusableElements = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    return { 
      total: focusableElements.length,
      issues: []
    };
  }

  checkLandmarks() {
    const landmarks = {
      'main': document.querySelector('main, [role="main"]'),
      'nav': document.querySelector('nav, [role="navigation"]'),
      'header': document.querySelector('header, [role="banner"]'),
      'footer': document.querySelector('footer, [role="contentinfo"]')
    };
    
    const missing = Object.keys(landmarks).filter(key => !landmarks[key]);
    
    return {
      found: Object.keys(landmarks).length - missing.length,
      missing: missing,
      issues: missing.map(landmark => ({
        element: landmark,
        issue: `Missing ${landmark} landmark`
      }))
    };
  }
}

// Initialize Accessibility Manager
let accessibilityManager;

document.addEventListener('DOMContentLoaded', () => {
  accessibilityManager = new AccessibilityManager();
  console.log('Accessibility enhancements initialized');
});

// Export for global access
window.StellarLogicAI = window.StellarLogicAI || {};
window.StellarLogicAI.AccessibilityManager = AccessibilityManager;
window.StellarLogicAI.accessibility = accessibilityManager;
