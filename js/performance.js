// ===================================
// STELLAR LOGIC AI - PERFORMANCE MONITORING
// ===================================

class PerformanceMonitor {
  constructor() {
    this.metrics = {};
    this.observers = [];
    this.init();
  }

  init() {
    this.trackPageLoad();
    this.trackCoreWebVitals();
    this.trackUserInteractions();
    this.trackResourceTiming();
    this.setupIntersectionObserver();
  }

  // Track Page Load Performance
  trackPageLoad() {
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0];
      
      this.metrics.pageLoad = {
        dns: navigation.domainLookupEnd - navigation.domainLookupStart,
        tcp: navigation.connectEnd - navigation.connectStart,
        ssl: navigation.secureConnectionStart > 0 ? navigation.connectEnd - navigation.secureConnectionStart : 0,
        ttfb: navigation.responseStart - navigation.requestStart,
        download: navigation.responseEnd - navigation.responseStart,
        domParse: navigation.domContentLoadedEventStart - navigation.responseEnd,
        domReady: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        total: navigation.loadEventEnd - navigation.navigationStart
      };

      console.log('Page Load Metrics:', this.metrics.pageLoad);
      this.sendMetrics('page_load', this.metrics.pageLoad);
    });
  }

  // Track Core Web Vitals
  trackCoreWebVitals() {
    // Largest Contentful Paint (LCP)
    this.observeLCP();
    
    // First Input Delay (FID)
    this.observeFID();
    
    // Cumulative Layout Shift (CLS)
    this.observeCLS();
  }

  observeLCP() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      
      this.metrics.lcp = {
        value: lastEntry.startTime,
        element: lastEntry.element?.tagName || 'unknown',
        url: lastEntry.url || ''
      };

      console.log('LCP:', this.metrics.lcp);
      this.sendMetrics('lcp', this.metrics.lcp);
    });

    observer.observe({ entryTypes: ['largest-contentful-paint'] });
    this.observers.push(observer);
  }

  observeFID() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        this.metrics.fid = {
          value: entry.processingStart - entry.startTime,
          inputType: entry.name
        };

        console.log('FID:', this.metrics.fid);
        this.sendMetrics('fid', this.metrics.fid);
      });
    });

    observer.observe({ entryTypes: ['first-input'] });
    this.observers.push(observer);
  }

  observeCLS() {
    let clsValue = 0;
    
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });

      this.metrics.cls = {
        value: clsValue,
        entries: entries.length
      };

      console.log('CLS:', this.metrics.cls);
      this.sendMetrics('cls', this.metrics.cls);
    });

    observer.observe({ entryTypes: ['layout-shift'] });
    this.observers.push(observer);
  }

  // Track User Interactions
  trackUserInteractions() {
    let startTime = performance.now();
    
    document.addEventListener('click', (event) => {
      const clickTime = performance.now();
      const timeOnPage = clickTime - startTime;
      
      this.metrics.userInteraction = {
        type: 'click',
        target: event.target.tagName,
        timeOnPage: timeOnPage,
        timestamp: clickTime
      };

      this.sendMetrics('user_interaction', this.metrics.userInteraction);
    });

    // Track form submissions
    document.addEventListener('submit', (event) => {
      const submitTime = performance.now();
      
      this.metrics.formSubmission = {
        form: event.target.tagName,
        timeToSubmit: submitTime - startTime,
        timestamp: submitTime
      };

      this.sendMetrics('form_submission', this.metrics.formSubmission);
    });
  }

  // Track Resource Loading
  trackResourceTiming() {
    window.addEventListener('load', () => {
      const resources = performance.getEntriesByType('resource');
      
      this.metrics.resources = {
        total: resources.length,
        images: resources.filter(r => r.initiatorType === 'img').length,
        scripts: resources.filter(r => r.initiatorType === 'script').length,
        styles: resources.filter(r => r.initiatorType === 'link').length,
        totalSize: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
        slowResources: resources.filter(r => r.duration > 1000).map(r => ({
          name: r.name,
          duration: r.duration,
          size: r.transferSize
        }))
      };

      console.log('Resource Metrics:', this.metrics.resources);
      this.sendMetrics('resources', this.metrics.resources);
    });
  }

  // Setup Intersection Observer for Lazy Loading
  setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.classList.add('loaded');
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.1
    });

    // Observe all lazy images
    document.querySelectorAll('img[data-src]').forEach(img => {
      observer.observe(img);
    });

    this.observers.push(observer);
  }

  // Send Metrics to Analytics
  sendMetrics(type, data) {
    // Send to Google Analytics if available
    if (typeof gtag !== 'undefined') {
      gtag('event', type, {
        custom_parameter: JSON.stringify(data),
        value: typeof data.value === 'number' ? Math.round(data.value) : undefined
      });
    }

    // Send to custom analytics endpoint
    if (typeof fetch !== 'undefined') {
      fetch('/api/analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          data,
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: Date.now()
        })
      }).catch(error => {
        console.warn('Failed to send analytics:', error);
      });
    }
  }

  // Get Performance Report
  getReport() {
    return {
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      metrics: this.metrics,
      memory: performance.memory ? {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      } : null,
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : null
    };
  }

  // Cleanup Observers
  cleanup() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// ===================================
// LAZY LOADING IMPLEMENTATION
// ===================================

class LazyLoader {
  constructor() {
    this.observer = null;
    this.init();
  }

  init() {
    this.setupImageLazyLoading();
    this.setupComponentLazyLoading();
  }

  setupImageLazyLoading() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          
          if (element.dataset.src) {
            // Load image
            element.src = element.dataset.src;
            element.classList.add('loaded');
            
            // Load srcset if available
            if (element.dataset.srcset) {
              element.srcset = element.dataset.srcset;
            }
            
            // Remove from observation
            this.observer.unobserve(element);
          }
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.1
    });

    // Observe all images with data-src
    document.querySelectorAll('img[data-src]').forEach(img => {
      this.observer.observe(img);
    });
  }

  setupComponentLazyLoading() {
    const componentObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const component = entry.target;
          
          // Load component content
          this.loadComponent(component);
          componentObserver.unobserve(component);
        }
      });
    }, {
      rootMargin: '100px 0px',
      threshold: 0.1
    });

    // Observe components with data-component
    document.querySelectorAll('[data-component]').forEach(component => {
      componentObserver.observe(component);
    });
  }

  async loadComponent(element) {
    const componentName = element.dataset.component;
    
    try {
      const response = await fetch(`/components/${componentName}.html`);
      const html = await response.text();
      
      element.innerHTML = html;
      element.classList.add('loaded');
      
      // Dispatch custom event
      element.dispatchEvent(new CustomEvent('componentLoaded', {
        detail: { componentName }
      }));
      
    } catch (error) {
      console.error(`Failed to load component ${componentName}:`, error);
      element.innerHTML = `<p>Failed to load ${componentName}</p>`;
    }
  }
}

// ===================================
// PERFORMANCE OPTIMIZATION UTILITIES
// ===================================

class PerformanceUtils {
  // Debounce function for performance
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Throttle function for performance
  static throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // Optimize images
  static optimizeImages() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      // Add loading="lazy" attribute
      if (!img.hasAttribute('loading')) {
        img.setAttribute('loading', 'lazy');
      }
      
      // Add error handling
      img.onerror = function() {
        this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0yNSA1MEg3NVY3NUgyNVY1MFoiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTM3LjUgMzcuNUw1MCA1MEw2Mi41IDM3LjVWNjIuNUgzNy41VjM3LjVaIiBmaWxsPSIjRDFENUQCIi8+Cjwvc3ZnPgo=';
      };
    });
  }

  // Preload critical resources
  static preloadResources(resources) {
    resources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource.url;
      link.as = resource.type;
      
      if (resource.type === 'font') {
        link.type = 'font/woff2';
        link.crossOrigin = 'anonymous';
      }
      
      document.head.appendChild(link);
    });
  }

  // Setup service worker
  static setupServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then(registration => {
            console.log('SW registered:', registration);
          })
          .catch(error => {
            console.log('SW registration failed:', error);
          });
      });
    }
  }
}

// ===================================
// INITIALIZATION
// ===================================

// Initialize performance monitoring
let performanceMonitor;
let lazyLoader;

document.addEventListener('DOMContentLoaded', () => {
  performanceMonitor = new PerformanceMonitor();
  lazyLoader = new LazyLoader();
  
  // Optimize images
  PerformanceUtils.optimizeImages();
  
  // Setup service worker
  PerformanceUtils.setupServiceWorker();
  
  // Preload critical resources
  PerformanceUtils.preloadResources([
    { url: '/styles/unified-framework.css', type: 'style' },
    { url: '/Stellar_Logic_AI_Logo.png', type: 'image' }
  ]);
  
  console.log('Performance optimizations initialized');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (performanceMonitor) {
    performanceMonitor.cleanup();
  }
});

// Export for global access
window.StellarLogicAI = {
  PerformanceMonitor,
  LazyLoader,
  PerformanceUtils
};
