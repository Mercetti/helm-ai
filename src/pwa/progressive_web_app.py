"""
Progressive Web App (PWA) Capabilities for Helm AI
===============================================

This module provides comprehensive PWA capabilities:
- Service Worker implementation
- Offline functionality and caching
- Web App Manifest
- Push notifications
- Background sync
- App installation prompts
- Responsive design optimization
- Performance optimization
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("pwa")


class CacheStrategy(str, Enum):
    """Cache strategies for PWA"""
    CACHE_FIRST = "cache_first"
    NETWORK_FIRST = "network_first"
    CACHE_ONLY = "cache_only"
    NETWORK_ONLY = "network_only"
    STALE_WHILE_REVALIDATE = "stale_while_revalidate"


class NotificationPermission(str, Enum):
    """Notification permission states"""
    DEFAULT = "default"
    GRANTED = "granted"
    DENIED = "denied"


@dataclass
class PWAManifest:
    """PWA Web App Manifest configuration"""
    id: str
    name: str
    short_name: str
    description: str
    start_url: str
    display: str = "standalone"
    background_color: str = "#ffffff"
    theme_color: str = "#1976d2"
    orientation: str = "portrait-primary"
    icons: List[Dict[str, str]] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CacheRule:
    """Cache rule for service worker"""
    id: str
    name: str
    url_pattern: str
    strategy: CacheStrategy
    cache_name: str
    max_age: int = 86400  # 24 hours
    max_entries: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PushSubscription:
    """Push notification subscription"""
    id: str
    endpoint: str
    keys: Dict[str, str]
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class PWAGenerator:
    """Progressive Web App Generator and Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.manifests: Dict[str, PWAManifest] = {}
        self.cache_rules: Dict[str, CacheRule] = {}
        self.subscriptions: Dict[str, PushSubscription] = {}
        
        logger.info("PWA Generator initialized")
    
    def create_service_worker(self, app_name: str, output_path: str) -> bool:
        """Create service worker file"""
        try:
            sw_content = self._generate_service_worker_content(app_name)
            
            sw_path = Path(output_path) / "sw.js"
            sw_path.write_text(sw_content)
            
            logger.info(f"Service worker created at {sw_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create service worker: {e}")
            return False
    
    def _generate_service_worker_content(self, app_name: str) -> str:
        """Generate service worker JavaScript content"""
        return f'''
const CACHE_NAME = '{app_name}-v1';
const STATIC_CACHE_NAME = '{app_name}-static-v1';
const DYNAMIC_CACHE_NAME = '{app_name}-dynamic-v1';

// Files to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/assets/css/main.css',
  '/assets/js/main.js',
  '/assets/icons/icon-192x192.png',
  '/assets/icons/icon-512x512.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {{
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {{
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }))
      .then(() => {{
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      }})
  );
}});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {{
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {{
        return Promise.all(
          cacheNames.map((cacheName) => {{
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME) {{
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }}
          }})
        );
      }})
      .then(() => {{
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      }})
  );
}});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {{
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {{
    return;
  }}
  
  // Handle different request types
  if (STATIC_ASSETS.includes(url.pathname)) {{
    // Cache first for static assets
    event.respondWith(cacheFirst(request));
  }} else if (url.pathname.startsWith('/api/')) {{
    // Network first for API calls
    event.respondWith(networkFirst(request));
  }} else {{
    // Stale while revalidate for other requests
    event.respondWith(staleWhileRevalidate(request));
  }}
}});

// Cache first strategy
async function cacheFirst(request) {{
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {{
    return cachedResponse;
  }}
  
  try {{
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {{
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }}
    
    return networkResponse;
  }} catch (error) {{
    console.error('Cache first failed:', error);
    return new Response('Offline', {{ status: 503, statusText: 'Service Unavailable' }});
  }}
}}

// Network first strategy
async function networkFirst(request) {{
  try {{
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {{
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }}
    
    return networkResponse;
  }} catch (error) {{
    console.error('Network first failed, trying cache:', error);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {{
      return cachedResponse;
    }}
    
    return new Response('Offline', {{ status: 503, statusText: 'Service Unavailable' }});
  }}
}}

// Stale while revalidate strategy
async function staleWhileRevalidate(request) {{
  const cachedResponse = await caches.match(request);
  const fetchPromise = fetch(request).then((networkResponse) => {{
    if (networkResponse.ok) {{
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }}
    return networkResponse;
  }}).catch((error) => {{
    console.error('Stale while revalidate failed:', error);
    return cachedResponse || new Response('Offline', {{ status: 503 }});
  }});
  
  return cachedResponse || fetchPromise;
}}

// Background sync
self.addEventListener('sync', (event) => {{
  if (event.tag === 'background-sync') {{
    event.waitUntil(doBackgroundSync());
  }}
}});

async function doBackgroundSync() {{
  try {{
    // Perform background sync operations
    console.log('Background sync completed');
  }} catch (error) {{
    console.error('Background sync failed:', error);
  }}
}}

// Push notifications
self.addEventListener('push', (event) => {{
  const options = {{
    body: event.data ? event.data.text() : 'New notification',
    icon: '/assets/icons/icon-192x192.png',
    badge: '/assets/icons/badge.png',
    vibrate: [100, 50, 100],
    data: {{
      dateOfArrival: Date.now(),
      primaryKey: 1
    }},
    actions: [
      {{
        action: 'explore',
        title: 'Explore',
        icon: '/assets/icons/check.png'
      }},
      {{
        action: 'close',
        title: 'Close',
        icon: '/assets/icons/x.png'
      }}
    ]
  }};
  
  event.waitUntil(
    self.registration.showNotification('Helm AI', options)
  );
}});

// Notification click handling
self.addEventListener('notificationclick', (event) => {{
  event.notification.close();
  
  if (event.action === 'explore') {{
    event.waitUntil(
      clients.openWindow('/')
    );
  }}
}});
'''
    
    def create_web_app_manifest(self, manifest: PWAManifest, output_path: str) -> bool:
        """Create web app manifest file"""
        try:
            manifest_data = {
                "name": manifest.name,
                "short_name": manifest.short_name,
                "description": manifest.description,
                "start_url": manifest.start_url,
                "display": manifest.display,
                "background_color": manifest.background_color,
                "theme_color": manifest.theme_color,
                "orientation": manifest.orientation,
                "icons": manifest.icons,
                "categories": manifest.categories,
                "scope": "/",
                "lang": "en",
                "dir": "ltr"
            }
            
            manifest_path = Path(output_path) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest_data, indent=2))
            
            # Store manifest
            self.manifests[manifest.id] = manifest
            
            logger.info(f"Web app manifest created at {manifest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create web app manifest: {e}")
            return False
    
    def create_offline_page(self, output_path: str) -> bool:
        """Create offline fallback page"""
        try:
            offline_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Helm AI</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            max-width: 400px;
        }
        .icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
            font-weight: 300;
        }
        p {
            font-size: 1.1rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .btn {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-block;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📱</div>
        <h1>You're Offline</h1>
        <p>It looks like you've lost your internet connection. Don't worry, you can still access some features of Helm AI when you're back online.</p>
        <button class="btn" onclick="window.location.reload()">Try Again</button>
    </div>
</body>
</html>
'''
            
            offline_path = Path(output_path) / "offline.html"
            offline_path.write_text(offline_html)
            
            logger.info(f"Offline page created at {offline_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create offline page: {e}")
            return False
    
    def create_pwa_client_script(self, output_path: str) -> bool:
        """Create PWA client-side JavaScript"""
        try:
            pwa_js = '''
// PWA Client Script
class PWAManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.swRegistration = null;
    this.deferredPrompt = null;
    
    this.init();
  }
  
  async init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      try {
        this.swRegistration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', this.swRegistration);
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
    
    // Listen for online/offline events
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
    
    // Listen for beforeinstallprompt
    window.addEventListener('beforeinstallprompt', this.handleBeforeInstallPrompt.bind(this));
    
    // Listen for appinstalled
    window.addEventListener('appinstalled', this.handleAppInstalled.bind(this));
    
    // Check if app is installed
    this.checkIfInstalled();
  }
  
  handleOnline() {
    this.isOnline = true;
    console.log('App is online');
    this.showOnlineStatus();
  }
  
  handleOffline() {
    this.isOnline = false;
    console.log('App is offline');
    this.showOfflineStatus();
  }
  
  showOnlineStatus() {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
      statusElement.textContent = 'Online';
      statusElement.className = 'online';
    }
  }
  
  showOfflineStatus() {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
      statusElement.textContent = 'Offline';
      statusElement.className = 'offline';
    }
  }
  
  handleBeforeInstallPrompt(event) {
    console.log('beforeinstallprompt fired');
    event.preventDefault();
    this.deferredPrompt = event;
    this.showInstallButton();
  }
  
  handleAppInstalled() {
    console.log('App was installed');
    this.deferredPrompt = null;
    this.hideInstallButton();
  }
  
  showInstallButton() {
    const installButton = document.getElementById('install-button');
    if (installButton) {
      installButton.style.display = 'block';
    }
  }
  
  hideInstallButton() {
    const installButton = document.getElementById('install-button');
    if (installButton) {
      installButton.style.display = 'none';
    }
  }
  
  async installApp() {
    if (!this.deferredPrompt) {
      console.log('No deferred prompt available');
      return;
    }
    
    this.deferredPrompt.prompt();
    
    const {{ result }} = await this.deferredPrompt.userChoice;
    
    if (result.outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }
    
    this.deferredPrompt = null;
    this.hideInstallButton();
  }
  
  checkIfInstalled() {
    // Check if app is running in standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('App is installed and running in standalone mode');
      return true;
    }
    
    // Check if app is running from home screen
    if (window.navigator.standalone) {
      console.log('App is installed and running from home screen');
      return true;
    }
    
    return false;
  }
  
  async requestNotificationPermission() {
    if ('Notification' in navigator) {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
      return permission;
    }
    
    return 'denied';
  }
  
  async subscribeToPushNotifications() {
    if (!this.swRegistration) {
      console.error('Service Worker not registered');
      return null;
    }
    
    try {
      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
      });
      
      console.log('Push subscription:', subscription);
      return subscription;
    } catch (error) {
      console.error('Push subscription failed:', error);
      return null;
    }
  }
  
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }
  
  async syncData() {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      try {
        await this.swRegistration.sync.register('background-sync');
        console.log('Background sync registered');
      } catch (error) {
        console.error('Background sync registration failed:', error);
      }
    }
  }
}

// Initialize PWA Manager
const pwaManager = new PWAManager();

// Global functions for HTML elements
window.installApp = () => pwaManager.installApp();
window.requestNotificationPermission = () => pwaManager.requestNotificationPermission();
window.subscribeToPushNotifications = () => pwaManager.subscribeToPushNotifications();
window.syncData = () => pwaManager.syncData();
'''
            
            pwa_path = Path(output_path) / "pwa.js"
            pwa_path.write_text(pwa_js)
            
            logger.info(f"PWA client script created at {pwa_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PWA client script: {e}")
            return False
    
    def add_cache_rule(self, rule: CacheRule) -> bool:
        """Add a cache rule"""
        try:
            self.cache_rules[rule.id] = rule
            logger.info(f"Cache rule added: {rule.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add cache rule: {e}")
            return False
    
    def create_push_subscription(self, subscription: PushSubscription) -> bool:
        """Create push notification subscription"""
        try:
            self.subscriptions[subscription.id] = subscription
            logger.info(f"Push subscription created: {subscription.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create push subscription: {e}")
            return False
    
    def generate_pwa_html_template(self, app_name: str) -> str:
        """Generate PWA HTML template"""
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    
    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#1976d2">
    <meta name="description" content="Advanced AI-powered analytics platform">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="{app_name}">
    <meta name="format-detection" content="telephone=no">
    
    <!-- Web App Manifest -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- Icons -->
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/icons/favicon-16x16.png">
    <link rel="mask-icon" href="/assets/icons/safari-pinned-tab.svg" color="#1976d2">
    
    <!-- Styles -->
    <link rel="stylesheet" href="/assets/css/main.css">
    
    <!-- PWA Script -->
    <script src="/pwa.js" defer></script>
</head>
<body>
    <!-- Connection Status Indicator -->
    <div id="connection-status" class="connection-status">
        <span class="status-text">Online</span>
    </div>
    
    <!-- Install Button -->
    <button id="install-button" class="install-button" style="display: none;">
        Install App
    </button>
    
    <!-- Main App Content -->
    <div id="app">
        <header class="app-header">
            <h1>{app_name}</h1>
            <nav class="app-nav">
                <button class="nav-btn" onclick="showDashboard()">Dashboard</button>
                <button class="nav-btn" onclick="showAnalytics()">Analytics</button>
                <button class="nav-btn" onclick="showSettings()">Settings</button>
            </nav>
        </header>
        
        <main class="app-main">
            <div id="dashboard" class="page active">
                <h2>Dashboard</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total Revenue</h3>
                        <p class="metric-value">$125,430</p>
                        <span class="metric-change positive">+12.5%</span>
                    </div>
                    <div class="metric-card">
                        <h3>Active Users</h3>
                        <p class="metric-value">8,234</p>
                        <span class="metric-change positive">+5.2%</span>
                    </div>
                    <div class="metric-card">
                        <h3>Conversion Rate</h3>
                        <p class="metric-value">3.4%</p>
                        <span class="metric-change negative">-0.8%</span>
                    </div>
                    <div class="metric-card">
                        <h3>Avg. Session</h3>
                        <p class="metric-value">4m 32s</p>
                        <span class="metric-change positive">+18.3%</span>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>Revenue Trend</h3>
                    <canvas id="revenue-chart"></canvas>
                </div>
            </div>
            
            <div id="analytics" class="page">
                <h2>Analytics</h2>
                <div class="analytics-content">
                    <p>Detailed analytics and insights...</p>
                </div>
            </div>
            
            <div id="settings" class="page">
                <h2>Settings</h2>
                <div class="settings-content">
                    <div class="setting-group">
                        <h3>Notifications</h3>
                        <button onclick="requestNotificationPermission()">
                            Enable Notifications
                        </button>
                        <button onclick="subscribeToPushNotifications()">
                            Subscribe to Push Updates
                        </button>
                    </div>
                    
                    <div class="setting-group">
                        <h3>Data Sync</h3>
                        <button onclick="syncData()">
                            Sync Data Now
                        </button>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script src="/assets/js/main.js"></script>
</body>
</html>
'''
    
    def get_pwa_metrics(self) -> Dict[str, Any]:
        """Get PWA metrics"""
        return {
            "total_manifests": len(self.manifests),
            "total_cache_rules": len(self.cache_rules),
            "total_subscriptions": len(self.subscriptions),
            "supported_features": [
                "service_worker",
                "offline_support",
                "push_notifications",
                "background_sync",
                "app_installation"
            ],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
PWA_CONFIG = {
    "output_path": "./pwa",
    "cache_strategies": {
        "static": "cache_first",
        "api": "network_first",
        "dynamic": "stale_while_revalidate"
    },
    "manifest": {
        "name": "Helm AI",
        "short_name": "HelmAI",
        "theme_color": "#1976d2",
        "background_color": "#ffffff"
    }
}


# Initialize PWA generator
pwa_generator = PWAGenerator(PWA_CONFIG)

# Export main components
__all__ = [
    'PWAGenerator',
    'PWAManifest',
    'CacheRule',
    'PushSubscription',
    'CacheStrategy',
    'NotificationPermission',
    'pwa_generator'
]
