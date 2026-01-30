"""
Helm AI White-Labeling Capabilities
Provides comprehensive white-labeling support with custom branding, themes, and configurations
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
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class BrandStatus(Enum):
    """Brand status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class ThemeType(Enum):
    """Theme type enumeration"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"

class ComponentType(Enum):
    """Component type enumeration"""
    LOGO = "logo"
    FAVICON = "favicon"
    BANNER = "banner"
    FOOTER = "footer"
    EMAIL_TEMPLATE = "email_template"
    LOGIN_PAGE = "login_page"
    DASHBOARD = "dashboard"
    MOBILE_APP = "mobile_app"

@dataclass
class BrandConfiguration:
    """Brand configuration definition"""
    brand_id: str
    tenant_id: str
    brand_name: str
    company_name: str
    domain: str
    status: BrandStatus
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    theme: Dict[str, Any]
    assets: Dict[str, Any]
    custom_css: str
    custom_js: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brand configuration to dictionary"""
        return {
            'brand_id': self.brand_id,
            'tenant_id': self.tenant_id,
            'brand_name': self.brand_name,
            'company_name': self.company_name,
            'domain': self.domain,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings': self.settings,
            'theme': self.theme,
            'assets': self.assets,
            'custom_css': self.custom_css,
            'custom_js': self.custom_js,
            'metadata': self.metadata
        }

@dataclass
class BrandAsset:
    """Brand asset definition"""
    asset_id: str
    brand_id: str
    component_type: ComponentType
    asset_type: str  # image, css, js, font, etc.
    file_path: str
    url: str
    file_size: int
    mime_type: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert brand asset to dictionary"""
        return {
            'asset_id': self.asset_id,
            'brand_id': self.brand_id,
            'component_type': component_type.value,
            'asset_type': self.asset_type,
            'file_path': self.file_path,
            'url': self.url,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class ThemeTemplate:
    """Theme template definition"""
    template_id: str
    name: str
    description: str
    theme_type: ThemeType
    is_default: bool
    is_premium: bool
    colors: Dict[str, str]
    typography: Dict[str, Any]
    spacing: Dict[str, Any]
    components: Dict[str, Any]
    custom_properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme template to dictionary"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'theme_type': self.theme_type.value,
            'is_default': self.is_default,
            'is_premium': self.is_premium,
            'colors': self.colors,
            'typography': self.typography,
            'spacing': self.spacing,
            'components': self.components,
            'custom_properties': self.custom_properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BrandManager:
    """White-labeling brand management system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.brands: Dict[str, BrandConfiguration] = {}
        self.brand_assets: Dict[str, BrandAsset] = {}
        self.theme_templates: Dict[str, ThemeTemplate] = {}
        self.domain_brand_mappings: Dict[str, str] = {}  # domain -> brand_id
        self.lock = threading.Lock()
        
        # Configuration
        self.assets_base_path = os.getenv('BRAND_ASSETS_PATH', 'assets/brands')
        self.max_brand_assets = int(os.getenv('MAX_BRAND_ASSETS', '100'))
        self.allowed_mime_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
            'text/css', 'application/javascript', 'font/woff', 'font/woff2'
        }
        
        # Ensure assets directory exists
        os.makedirs(self.assets_base_path, exist_ok=True)
        
        # Initialize default theme templates
        self._initialize_default_themes()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_themes(self) -> None:
        """Initialize default theme templates"""
        # Light Theme
        light_theme = ThemeTemplate(
            template_id="light_default",
            name="Light Theme",
            description="Clean and modern light theme",
            theme_type=ThemeType.LIGHT,
            is_default=True,
            is_premium=False,
            colors={
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'background': '#ffffff',
                'surface': '#f8f9fa',
                'text_primary': '#212529',
                'text_secondary': '#6c757d',
                'border': '#dee2e6',
                'shadow': 'rgba(0, 0, 0, 0.1)'
            },
            typography={
                'font_family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font_size_base': '16px',
                'font_weight_normal': '400',
                'font_weight_bold': '600',
                'line_height': '1.5',
                'letter_spacing': '0.01em'
            },
            spacing={
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
                'xxl': '48px'
            },
            components={
                'button': {
                    'border_radius': '6px',
                    'padding': '12px 24px',
                    'font_weight': '600'
                },
                'card': {
                    'border_radius': '8px',
                    'shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '24px'
                },
                'input': {
                    'border_radius': '4px',
                    'border_width': '1px',
                    'padding': '12px 16px'
                }
            },
            custom_properties={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Dark Theme
        dark_theme = ThemeTemplate(
            template_id="dark_default",
            name="Dark Theme",
            description="Modern dark theme for low-light environments",
            theme_type=ThemeType.DARK,
            is_default=True,
            is_premium=False,
            colors={
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'success': '#198754',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#0dcaf0',
                'light': '#f8f9fa',
                'dark': '#212529',
                'background': '#1a1a1a',
                'surface': '#2d2d2d',
                'text_primary': '#ffffff',
                'text_secondary': '#adb5bd',
                'border': '#495057',
                'shadow': 'rgba(0, 0, 0, 0.3)'
            },
            typography={
                'font_family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font_size_base': '16px',
                'font_weight_normal': '400',
                'font_weight_bold': '600',
                'line_height': '1.5',
                'letter_spacing': '0.01em'
            },
            spacing={
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
                'xxl': '48px'
            },
            components={
                'button': {
                    'border_radius': '6px',
                    'padding': '12px 24px',
                    'font_weight': '600'
                },
                'card': {
                    'border_radius': '8px',
                    'shadow': '0 2px 8px rgba(0, 0, 0, 0.3)',
                    'padding': '24px'
                },
                'input': {
                    'border_radius': '4px',
                    'border_width': '1px',
                    'padding': '12px 16px'
                }
            },
            custom_properties={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Corporate Theme (Premium)
        corporate_theme = ThemeTemplate(
            template_id="corporate_premium",
            name="Corporate Theme",
            description="Professional corporate theme with premium features",
            theme_type=ThemeType.CUSTOM,
            is_default=False,
            is_premium=True,
            colors={
                'primary': '#1e3a8a',
                'secondary': '#64748b',
                'success': '#059669',
                'danger': '#dc2626',
                'warning': '#d97706',
                'info': '#0891b2',
                'light': '#f8fafc',
                'dark': '#1e293b',
                'background': '#ffffff',
                'surface': '#f1f5f9',
                'text_primary': '#0f172a',
                'text_secondary': '#475569',
                'border': '#e2e8f0',
                'shadow': 'rgba(0, 0, 0, 0.05)'
            },
            typography={
                'font_family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'font_size_base': '16px',
                'font_weight_normal': '400',
                'font_weight_bold': '700',
                'line_height': '1.6',
                'letter_spacing': '0.005em'
            },
            spacing={
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
                'xxl': '48px'
            },
            components={
                'button': {
                    'border_radius': '4px',
                    'padding': '14px 28px',
                    'font_weight': '700',
                    'text_transform': 'uppercase'
                },
                'card': {
                    'border_radius': '12px',
                    'shadow': '0 4px 6px rgba(0, 0, 0, 0.05)',
                    'padding': '32px'
                },
                'input': {
                    'border_radius': '6px',
                    'border_width': '2px',
                    'padding': '14px 18px'
                }
            },
            custom_properties={
                'premium_gradients': True,
                'advanced_animations': True,
                'custom_icons': True
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add themes to registry
        self.theme_templates[light_theme.template_id] = light_theme
        self.theme_templates[dark_theme.template_id] = dark_theme
        self.theme_templates[corporate_theme.template_id] = corporate_theme
        
        logger.info(f"Initialized {len(self.theme_templates)} default theme templates")
    
    def create_brand(self, tenant_id: str, brand_name: str, company_name: str, domain: str,
                     theme_template_id: Optional[str] = None, custom_settings: Optional[Dict[str, Any]] = None) -> BrandConfiguration:
        """Create a new brand configuration"""
        brand_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Validate domain uniqueness
        if domain in self.domain_brand_mappings:
            raise ValueError(f"Domain {domain} is already branded")
        
        # Get theme template
        if theme_template_id and theme_template_id in self.theme_templates:
            theme_template = self.theme_templates[theme_template_id]
            theme = {
                'template_id': theme_template_id,
                'colors': theme_template.colors.copy(),
                'typography': theme_template.typography.copy(),
                'spacing': theme_template.spacing.copy(),
                'components': theme_template.components.copy(),
                'custom_properties': theme_template.custom_properties.copy()
            }
        else:
            # Use default light theme
            default_theme = self.theme_templates['light_default']
            theme = {
                'template_id': 'light_default',
                'colors': default_theme.colors.copy(),
                'typography': default_theme.typography.copy(),
                'spacing': default_theme.spacing.copy(),
                'components': default_theme.components.copy(),
                'custom_properties': {}
            }
        
        # Create brand configuration
        brand = BrandConfiguration(
            brand_id=brand_id,
            tenant_id=tenant_id,
            brand_name=brand_name,
            company_name=company_name,
            domain=domain,
            status=BrandStatus.PENDING,
            created_at=now,
            updated_at=now,
            settings=custom_settings or {},
            theme=theme,
            assets={},
            custom_css="",
            custom_js="",
            metadata={}
        )
        
        with self.lock:
            self.brands[brand_id] = brand
            self.domain_brand_mappings[domain] = brand_id
        
        # Create brand directory
        brand_path = os.path.join(self.assets_base_path, brand_id)
        os.makedirs(brand_path, exist_ok=True)
        
        # Create default CSS file
        self._generate_brand_css(brand)
        
        # Activate brand
        brand.status = BrandStatus.ACTIVE
        brand.updated_at = now
        
        logger.info(f"Created brand {brand_id} ({brand_name}) for tenant {tenant_id}")
        
        return brand
    
    def _generate_brand_css(self, brand: BrandConfiguration) -> None:
        """Generate CSS file for brand"""
        css_content = f"""
/* {brand.brand_name} - Generated CSS */
:root {{
    /* Colors */
    --brand-primary: {brand.theme['colors']['primary']};
    --brand-secondary: {brand.theme['colors']['secondary']};
    --brand-success: {brand.theme['colors']['success']};
    --brand-danger: {brand.theme['colors']['danger']};
    --brand-warning: {brand.theme['colors']['warning']};
    --brand-info: {brand.theme['colors']['info']};
    --brand-light: {brand.theme['colors']['light']};
    --brand-dark: {brand.theme['colors']['dark']};
    --brand-background: {brand.theme['colors']['background']};
    --brand-surface: {brand.theme['colors']['surface']};
    --brand-text-primary: {brand.theme['colors']['text_primary']};
    --brand-text-secondary: {brand.theme['colors']['text_secondary']};
    --brand-border: {brand.theme['colors']['border']};
    --brand-shadow: {brand.theme['colors']['shadow']};
    
    /* Typography */
    --brand-font-family: {brand.theme['typography']['font_family']};
    --brand-font-size-base: {brand.theme['typography']['font_size_base']};
    --brand-font-weight-normal: {brand.theme['typography']['font_weight_normal']};
    --brand-font-weight-bold: {brand.theme['typography']['font_weight_bold']};
    --brand-line-height: {brand.theme['typography']['line_height']};
    --brand-letter-spacing: {brand.theme['typography']['letter_spacing']};
    
    /* Spacing */
    --brand-spacing-xs: {brand.theme['spacing']['xs']};
    --brand-spacing-sm: {brand.theme['spacing']['sm']};
    --brand-spacing-md: {brand.theme['spacing']['md']};
    --brand-spacing-lg: {brand.theme['spacing']['lg']};
    --brand-spacing-xl: {brand.theme['spacing']['xl']};
    --brand-spacing-xxl: {brand.theme['spacing']['xxl']};
}}

/* Base styles */
body {{
    font-family: var(--brand-font-family);
    font-size: var(--brand-font-size-base);
    line-height: var(--brand-line-height);
    letter-spacing: var(--brand-letter-spacing);
    color: var(--brand-text-primary);
    background-color: var(--brand-background);
}}

/* Component styles */
.btn-primary {{
    background-color: var(--brand-primary);
    border-color: var(--brand-primary);
    color: white;
    border-radius: {brand.theme['components']['button']['border_radius']};
    padding: {brand.theme['components']['button']['padding']};
    font-weight: {brand.theme['components']['button']['font_weight']};
}}

.card {{
    border-radius: {brand.theme['components']['card']['border_radius']};
    box-shadow: {brand.theme['components']['card']['shadow']};
    padding: {brand.theme['components']['card']['padding']};
    background-color: var(--brand-surface);
    border: 1px solid var(--brand-border);
}}

.form-control {{
    border-radius: {brand.theme['components']['input']['border_radius']};
    border-width: {brand.theme['components']['input']['border_width']};
    padding: {brand.theme['components']['input']['padding']};
    border-color: var(--brand-border);
    background-color: var(--brand-background);
    color: var(--brand-text-primary);
}}

/* Custom CSS */
{brand.custom_css}
"""
        
        # Write CSS file
        css_path = os.path.join(self.assets_base_path, brand.brand_id, 'brand.css')
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        logger.info(f"Generated CSS for brand {brand.brand_id}")
    
    def upload_brand_asset(self, brand_id: str, component_type: ComponentType, file_path: str,
                          description: str = "") -> BrandAsset:
        """Upload brand asset"""
        if brand_id not in self.brands:
            raise ValueError(f"Brand {brand_id} not found")
        
        brand = self.brands[brand_id]
        
        # Check asset limit
        current_assets = len([a for a in self.brand_assets.values() if a.brand_id == brand_id])
        if current_assets >= self.max_brand_assets:
            raise ValueError(f"Brand {brand_id} has reached maximum asset limit")
        
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = self._get_mime_type(file_path)
        
        if mime_type not in self.allowed_mime_types:
            raise ValueError(f"File type {mime_type} not allowed")
        
        # Copy file to brand assets directory
        asset_id = str(uuid.uuid4())
        asset_filename = f"{asset_id}_{os.path.basename(file_path)}"
        brand_asset_path = os.path.join(self.assets_base_path, brand_id, asset_filename)
        
        import shutil
        shutil.copy2(file_path, brand_asset_path)
        
        # Generate URL
        asset_url = f"/assets/brands/{brand_id}/{asset_filename}"
        
        # Create asset record
        asset = BrandAsset(
            asset_id=asset_id,
            brand_id=brand_id,
            component_type=component_type,
            asset_type=self._get_asset_type(mime_type),
            file_path=brand_asset_path,
            url=asset_url,
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        with self.lock:
            self.brand_assets[asset_id] = asset
        
        # Update brand assets
        if component_type.value not in brand.assets:
            brand.assets[component_type.value] = []
        
        brand.assets[component_type.value].append(asset.to_dict())
        brand.updated_at = datetime.utcnow()
        
        logger.info(f"Uploaded asset {asset_id} for brand {brand_id}")
        
        return asset
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""
        import mimetypes
        
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    def _get_asset_type(self, mime_type: str) -> str:
        """Get asset type from MIME type"""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type == 'text/css':
            return 'css'
        elif mime_type == 'application/javascript':
            return 'js'
        elif mime_type.startswith('font/'):
            return 'font'
        else:
            return 'other'
    
    def update_brand_theme(self, brand_id: str, theme_updates: Dict[str, Any]) -> bool:
        """Update brand theme"""
        with self.lock:
            if brand_id not in self.brands:
                return False
            
            brand = self.brands[brand_id]
            
            # Update theme
            for section, updates in theme_updates.items():
                if section in brand.theme:
                    brand.theme[section].update(updates)
            
            brand.updated_at = datetime.utcnow()
            
            # Regenerate CSS
            self._generate_brand_css(brand)
            
            logger.info(f"Updated theme for brand {brand_id}")
            
            return True
    
    def update_brand_settings(self, brand_id: str, settings: Dict[str, Any]) -> bool:
        """Update brand settings"""
        with self.lock:
            if brand_id not in self.brands:
                return False
            
            brand = self.brands[brand_id]
            brand.settings.update(settings)
            brand.updated_at = datetime.utcnow()
            
            logger.info(f"Updated settings for brand {brand_id}")
            
            return True
    
    def get_brand_by_domain(self, domain: str) -> Optional[BrandConfiguration]:
        """Get brand by domain"""
        with self.lock:
            brand_id = self.domain_brand_mappings.get(domain)
            if brand_id:
                return self.brands.get(brand_id)
            return None
    
    def get_brand_assets(self, brand_id: str, component_type: Optional[ComponentType] = None) -> List[BrandAsset]:
        """Get brand assets"""
        with self.lock:
            assets = [a for a in self.brand_assets.values() if a.brand_id == brand_id and a.is_active]
            
            if component_type:
                assets = [a for a in assets if a.component_type == component_type]
            
            return assets
    
    def get_brand_css(self, brand_id: str) -> str:
        """Get brand CSS content"""
        css_path = os.path.join(self.assets_base_path, brand_id, 'brand.css')
        
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                return f.read()
        
        return ""
    
    def generate_brand_variables(self, brand_id: str) -> Dict[str, Any]:
        """Generate CSS variables for brand"""
        with self.lock:
            if brand_id not in self.brands:
                return {}
            
            brand = self.brands[brand_id]
            
            variables = {
                'brand_id': brand.brand_id,
                'brand_name': brand.brand_name,
                'company_name': brand.company_name,
                'domain': brand.domain,
                'colors': brand.theme['colors'],
                'typography': brand.theme['typography'],
                'spacing': brand.theme['spacing'],
                'components': brand.theme['components'],
                'assets': brand.assets,
                'custom_css': brand.custom_css,
                'custom_js': brand.custom_js
            }
            
            return variables
    
    def create_theme_template(self, name: str, description: str, theme_type: ThemeType,
                             colors: Dict[str, str], typography: Dict[str, Any],
                             spacing: Dict[str, Any], components: Dict[str, Any],
                             is_premium: bool = False) -> ThemeTemplate:
        """Create custom theme template"""
        template_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        template = ThemeTemplate(
            template_id=template_id,
            name=name,
            description=description,
            theme_type=theme_type,
            is_default=False,
            is_premium=is_premium,
            colors=colors,
            typography=typography,
            spacing=spacing,
            components=components,
            custom_properties={},
            created_at=now,
            updated_at=now
        )
        
        with self.lock:
            self.theme_templates[template_id] = template
        
        logger.info(f"Created theme template {template_id} ({name})")
        
        return template
    
    def apply_theme_template(self, brand_id: str, template_id: str) -> bool:
        """Apply theme template to brand"""
        with self.lock:
            if brand_id not in self.brands:
                return False
            
            if template_id not in self.theme_templates:
                return False
            
            brand = self.brands[brand_id]
            template = self.theme_templates[template_id]
            
            # Apply template theme
            brand.theme = {
                'template_id': template_id,
                'colors': template.colors.copy(),
                'typography': template.typography.copy(),
                'spacing': template.spacing.copy(),
                'components': template.components.copy(),
                'custom_properties': template.custom_properties.copy()
            }
            
            brand.updated_at = datetime.utcnow()
            
            # Regenerate CSS
            self._generate_brand_css(brand)
            
            logger.info(f"Applied theme template {template_id} to brand {brand_id}")
            
            return True
    
    def get_brand_metrics(self) -> Dict[str, Any]:
        """Get brand management metrics"""
        with self.lock:
            total_brands = len(self.brands)
            active_brands = len([b for b in self.brands.values() if b.status == BrandStatus.ACTIVE])
            pending_brands = len([b for b in self.brands.values() if b.status == BrandStatus.PENDING])
            
            # Theme distribution
            theme_distribution = defaultdict(int)
            for brand in self.brands.values():
                template_id = brand.theme.get('template_id', 'unknown')
                theme_distribution[template_id] += 1
            
            # Asset statistics
            total_assets = len(self.brand_assets)
            active_assets = len([a for a in self.brand_assets.values() if a.is_active])
            
            # Component type distribution
            component_distribution = defaultdict(int)
            for asset in self.brand_assets.values():
                if asset.is_active:
                    component_distribution[asset.component_type.value] += 1
            
            return {
                'total_brands': total_brands,
                'active_brands': active_brands,
                'pending_brands': pending_brands,
                'theme_distribution': dict(theme_distribution),
                'total_assets': total_assets,
                'active_assets': active_assets,
                'component_distribution': dict(component_distribution),
                'total_theme_templates': len(self.theme_templates),
                'premium_templates': len([t for t in self.theme_templates.values() if t.is_premium])
            }
    
    def _start_background_tasks(self) -> None:
        """Start background brand management tasks"""
        # Start asset cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_assets, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_assets(self) -> None:
        """Cleanup inactive brand assets"""
        while True:
            try:
                # Run cleanup daily
                time.sleep(86400)  # 24 hours
                
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                with self.lock:
                    # Find inactive assets
                    inactive_assets = [
                        asset for asset in self.brand_assets.values()
                        if not asset.is_active and asset.updated_at < cutoff_date
                    ]
                    
                    for asset in inactive_assets:
                        # Remove file
                        if os.path.exists(asset.file_path):
                            os.remove(asset.file_path)
                        
                        # Remove asset record
                        del self.brand_assets[asset.asset_id]
                    
                    if inactive_assets:
                        logger.info(f"Cleaned up {len(inactive_assets)} inactive brand assets")
                
            except Exception as e:
                logger.error(f"Asset cleanup failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying

# Global brand manager instance
brand_manager = BrandManager()

# Export main components
__all__ = [
    'BrandManager',
    'BrandConfiguration',
    'BrandAsset',
    'ThemeTemplate',
    'BrandStatus',
    'ThemeType',
    'ComponentType',
    'brand_manager'
]
