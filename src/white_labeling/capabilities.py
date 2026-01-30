"""
White-Labeling Capabilities for Helm AI
=======================================

This module provides comprehensive white-labeling capabilities:
- Custom branding and theming
- Domain and subdomain management
- Custom CSS and JavaScript injection
- Logo and asset management
- Email template customization
- Mobile app branding
- API white-labeling
- Reseller management
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("white_labeling")


class BrandingStatus(str, Enum):
    """Branding status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class AssetType(str, Enum):
    """Asset types"""
    LOGO = "logo"
    FAVICON = "favicon"
    BANNER = "banner"
    BACKGROUND = "background"
    ICON = "icon"
    FONT = "font"
    CSS = "css"
    JAVASCRIPT = "javascript"


class ThemeType(str, Enum):
    """Theme types"""
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


@dataclass
class BrandingAsset:
    """Branding asset definition"""
    id: str
    tenant_id: str
    asset_type: AssetType
    name: str
    file_path: str
    file_size: int
    mime_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ColorScheme:
    """Color scheme definition"""
    id: str
    tenant_id: str
    name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    border_color: str
    success_color: str
    warning_color: str
    error_color: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Typography:
    """Typography settings"""
    id: str
    tenant_id: str
    font_family: str
    font_size_base: str
    font_size_small: str
    font_size_large: str
    font_size_xlarge: str
    font_weight_normal: str
    font_weight_bold: str
    line_height_base: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CustomCSS:
    """Custom CSS definition"""
    id: str
    tenant_id: str
    name: str
    css_content: str
    minified: bool = False
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CustomJavaScript:
    """Custom JavaScript definition"""
    id: str
    tenant_id: str
    name: str
    js_content: str
    minified: bool = False
    version: str = "1.0"
    load_order: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmailTemplate:
    """Email template definition"""
    id: str
    tenant_id: str
    template_type: str
    name: str
    subject: str
    html_content: str
    text_content: str
    variables: List[str] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DomainConfiguration:
    """Domain configuration"""
    id: str
    tenant_id: str
    domain: str
    subdomain: str
    ssl_enabled: bool = True
    custom_ssl_cert: bool = False
    dns_verified: bool = False
    active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WhiteLabelConfiguration:
    """White-label configuration"""
    id: str
    tenant_id: str
    company_name: str
    product_name: str
    tagline: str
    description: str
    contact_email: str
    support_email: str
    website_url: str
    privacy_policy_url: str
    terms_of_service_url: str
    status: BrandingStatus = BrandingStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class WhiteLabelingManager:
    """White-Labeling Capabilities Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.branding_assets: Dict[str, BrandingAsset] = {}
        self.color_schemes: Dict[str, ColorScheme] = {}
        self.typographies: Dict[str, Typography] = {}
        self.custom_css: Dict[str, CustomCSS] = {}
        self.custom_js: Dict[str, CustomJavaScript] = {}
        self.email_templates: Dict[str, EmailTemplate] = {}
        self.domain_configs: Dict[str, DomainConfiguration] = {}
        self.white_label_configs: Dict[str, WhiteLabelConfiguration] = {}
        
        # Initialize default templates and themes
        self._initialize_default_themes()
        self._initialize_default_email_templates()
        
        logger.info("White-Labeling Manager initialized")
    
    def _initialize_default_themes(self):
        """Initialize default color schemes and typography"""
        # Default light theme
        light_theme = ColorScheme(
            id=str(uuid.uuid4()),
            tenant_id="default",
            name="Light Theme",
            primary_color="#1976d2",
            secondary_color="#424242",
            accent_color="#ff4081",
            background_color="#ffffff",
            text_color="#212121",
            border_color="#e0e0e0",
            success_color="#4caf50",
            warning_color="#ff9800",
            error_color="#f44336"
        )
        self.color_schemes[light_theme.id] = light_theme
        
        # Default dark theme
        dark_theme = ColorScheme(
            id=str(uuid.uuid4()),
            tenant_id="default",
            name="Dark Theme",
            primary_color="#90caf9",
            secondary_color="#bdbdbd",
            accent_color="#f48fb1",
            background_color="#121212",
            text_color="#ffffff",
            border_color="#333333",
            success_color="#81c784",
            warning_color="#ffb74d",
            error_color="#e57373"
        )
        self.color_schemes[dark_theme.id] = dark_theme
        
        # Default typography
        default_typography = Typography(
            id=str(uuid.uuid4()),
            tenant_id="default",
            font_family="Inter, system-ui, sans-serif",
            font_size_base="16px",
            font_size_small="14px",
            font_size_large="18px",
            font_size_xlarge="24px",
            font_weight_normal="400",
            font_weight_bold="700",
            line_height_base="1.5"
        )
        self.typographies[default_typography.id] = default_typography
    
    def _initialize_default_email_templates(self):
        """Initialize default email templates"""
        default_templates = [
            {
                "template_type": "welcome",
                "name": "Welcome Email",
                "subject": "Welcome to {{company_name}}!",
                "html_content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                        .header { background-color: {{primary_color}}; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .footer { background-color: #f5f5f5; padding: 20px; text-align: center; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{{company_name}}</h1>
                        <p>{{tagline}}</p>
                    </div>
                    <div class="content">
                        <h2>Welcome {{user_name}}!</h2>
                        <p>Thank you for joining {{company_name}}. We're excited to have you on board!</p>
                        <p>Get started by <a href="{{login_url}}">logging in to your account</a>.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 {{company_name}}. All rights reserved.</p>
                        <p><a href="{{privacy_policy_url}}">Privacy Policy</a> | <a href="{{terms_of_service_url}}">Terms of Service</a></p>
                    </div>
                </body>
                </html>
                """,
                "text_content": """
                Welcome to {{company_name}}!
                
                Hi {{user_name}},
                
                Thank you for joining {{company_name}}. We're excited to have you on board!
                
                Get started by logging in to your account: {{login_url}}
                
                Best regards,
                The {{company_name}} Team
                """
            },
            {
                "template_type": "password_reset",
                "name": "Password Reset",
                "subject": "Reset your {{company_name}} password",
                "html_content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                        .header { background-color: {{primary_color}}; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .button { background-color: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
                        .footer { background-color: #f5f5f5; padding: 20px; text-align: center; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{{company_name}}</h1>
                    </div>
                    <div class="content">
                        <h2>Password Reset Request</h2>
                        <p>Hi {{user_name}},</p>
                        <p>We received a request to reset your password for your {{company_name}} account.</p>
                        <p>Click the button below to reset your password:</p>
                        <p><a href="{{reset_url}}" class="button">Reset Password</a></p>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you didn't request this password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 {{company_name}}. All rights reserved.</p>
                    </div>
                </body>
                </html>
                """,
                "text_content": """
                Password Reset Request
                
                Hi {{user_name}},
                
                We received a request to reset your password for your {{company_name}} account.
                
                Click the link below to reset your password:
                {{reset_url}}
                
                This link will expire in 24 hours.
                
                If you didn't request this password reset, please ignore this email.
                
                Best regards,
                The {{company_name}} Team
                """
            },
            {
                "template_type": "invoice",
                "name": "Invoice Notification",
                "subject": "Invoice #{{invoice_number}} from {{company_name}}",
                "html_content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                        .header { background-color: {{primary_color}}; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .invoice-details { background-color: #f9f9f9; padding: 15px; margin: 20px 0; }
                        .footer { background-color: #f5f5f5; padding: 20px; text-align: center; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{{company_name}}</h1>
                        <p>{{tagline}}</p>
                    </div>
                    <div class="content">
                        <h2>Invoice #{{invoice_number}}</h2>
                        <p>Hi {{user_name}},</p>
                        <p>Your invoice for {{billing_period}} is ready.</p>
                        <div class="invoice-details">
                            <h3>Invoice Details</h3>
                            <p><strong>Amount:</strong> ${{amount}}</p>
                            <p><strong>Due Date:</strong> {{due_date}}</p>
                            <p><strong>Invoice Number:</strong> {{invoice_number}}</p>
                        </div>
                        <p><a href="{{invoice_url}}">View and Pay Invoice</a></p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 {{company_name}}. All rights reserved.</p>
                    </div>
                </body>
                </html>
                """,
                "text_content": """
                Invoice #{{invoice_number}} from {{company_name}}
                
                Hi {{user_name}},
                
                Your invoice for {{billing_period}} is ready.
                
                Amount: ${{amount}}
                Due Date: {{due_date}}
                Invoice Number: {{invoice_number}}
                
                View and pay your invoice: {{invoice_url}}
                
                Best regards,
                The {{company_name}} Team
                """
            }
        ]
        
        for template_data in default_templates:
            template = EmailTemplate(
                id=str(uuid.uuid4()),
                tenant_id="default",
                template_type=template_data["template_type"],
                name=template_data["name"],
                subject=template_data["subject"],
                html_content=template_data["html_content"],
                text_content=template_data["text_content"],
                variables=["company_name", "tagline", "user_name", "login_url", "reset_url", "invoice_url", "invoice_number", "amount", "due_date", "billing_period", "privacy_policy_url", "terms_of_service_url"]
            )
            self.email_templates[template.id] = template
    
    def create_white_label_config(self, tenant_id: str, config_data: Dict[str, Any]) -> WhiteLabelConfiguration:
        """Create white-label configuration for tenant"""
        try:
            config = WhiteLabelConfiguration(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                company_name=config_data.get("company_name", ""),
                product_name=config_data.get("product_name", ""),
                tagline=config_data.get("tagline", ""),
                description=config_data.get("description", ""),
                contact_email=config_data.get("contact_email", ""),
                support_email=config_data.get("support_email", ""),
                website_url=config_data.get("website_url", ""),
                privacy_policy_url=config_data.get("privacy_policy_url", ""),
                terms_of_service_url=config_data.get("terms_of_service_url", ""),
                status=BrandingStatus.PENDING
            )
            
            self.white_label_configs[config.id] = config
            
            # Copy default themes and templates for tenant
            self._copy_default_themes_for_tenant(tenant_id)
            self._copy_default_templates_for_tenant(tenant_id)
            
            logger.info(f"White-label configuration created for tenant {tenant_id}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to create white-label configuration: {e}")
            raise
    
    def _copy_default_themes_for_tenant(self, tenant_id: str):
        """Copy default themes for tenant"""
        try:
            # Copy color schemes
            for scheme in self.color_schemes.values():
                if scheme.tenant_id == "default":
                    new_scheme = ColorScheme(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        name=scheme.name,
                        primary_color=scheme.primary_color,
                        secondary_color=scheme.secondary_color,
                        accent_color=scheme.accent_color,
                        background_color=scheme.background_color,
                        text_color=scheme.text_color,
                        border_color=scheme.border_color,
                        success_color=scheme.success_color,
                        warning_color=scheme.warning_color,
                        error_color=scheme.error_color
                    )
                    self.color_schemes[new_scheme.id] = new_scheme
            
            # Copy typography
            for typo in self.typographies.values():
                if typo.tenant_id == "default":
                    new_typo = Typography(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        font_family=typo.font_family,
                        font_size_base=typo.font_size_base,
                        font_size_small=typo.font_size_small,
                        font_size_large=typo.font_size_large,
                        font_size_xlarge=typo.font_size_xlarge,
                        font_weight_normal=typo.font_weight_normal,
                        font_weight_bold=typo.font_weight_bold,
                        line_height_base=typo.line_height_base
                    )
                    self.typographies[new_typo.id] = new_typo
            
            logger.info(f"Default themes copied for tenant {tenant_id}")
            
        except Exception as e:
            logger.error(f"Failed to copy default themes for tenant {tenant_id}: {e}")
            raise
    
    def _copy_default_templates_for_tenant(self, tenant_id: str):
        """Copy default email templates for tenant"""
        try:
            for template in self.email_templates.values():
                if template.tenant_id == "default":
                    new_template = EmailTemplate(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        template_type=template.template_type,
                        name=template.name,
                        subject=template.subject,
                        html_content=template.html_content,
                        text_content=template.text_content,
                        variables=template.variables.copy(),
                        active=template.active
                    )
                    self.email_templates[new_template.id] = new_template
            
            logger.info(f"Default email templates copied for tenant {tenant_id}")
            
        except Exception as e:
            logger.error(f"Failed to copy default templates for tenant {tenant_id}: {e}")
            raise
    
    def upload_branding_asset(self, tenant_id: str, asset_type: AssetType, 
                            file_path: str, name: str, file_size: int, 
                            mime_type: str, metadata: Dict[str, Any] = None) -> BrandingAsset:
        """Upload branding asset"""
        try:
            asset = BrandingAsset(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                asset_type=asset_type,
                name=name,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                metadata=metadata or {}
            )
            
            self.branding_assets[asset.id] = asset
            
            logger.info(f"Branding asset uploaded: {asset.id} for tenant {tenant_id}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to upload branding asset: {e}")
            raise
    
    def update_color_scheme(self, tenant_id: str, scheme_id: str, 
                          colors: Dict[str, str]) -> bool:
        """Update color scheme"""
        try:
            if scheme_id not in self.color_schemes:
                return False
            
            scheme = self.color_schemes[scheme_id]
            if scheme.tenant_id != tenant_id:
                return False
            
            # Update colors
            if "primary_color" in colors:
                scheme.primary_color = colors["primary_color"]
            if "secondary_color" in colors:
                scheme.secondary_color = colors["secondary_color"]
            if "accent_color" in colors:
                scheme.accent_color = colors["accent_color"]
            if "background_color" in colors:
                scheme.background_color = colors["background_color"]
            if "text_color" in colors:
                scheme.text_color = colors["text_color"]
            if "border_color" in colors:
                scheme.border_color = colors["border_color"]
            if "success_color" in colors:
                scheme.success_color = colors["success_color"]
            if "warning_color" in colors:
                scheme.warning_color = colors["warning_color"]
            if "error_color" in colors:
                scheme.error_color = colors["error_color"]
            
            scheme.updated_at = datetime.utcnow()
            
            logger.info(f"Color scheme updated: {scheme_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update color scheme: {e}")
            return False
    
    def update_typography(self, tenant_id: str, typo_id: str, 
                        typography_data: Dict[str, str]) -> bool:
        """Update typography settings"""
        try:
            if typo_id not in self.typographies:
                return False
            
            typo = self.typographies[typo_id]
            if typo.tenant_id != tenant_id:
                return False
            
            # Update typography
            if "font_family" in typography_data:
                typo.font_family = typography_data["font_family"]
            if "font_size_base" in typography_data:
                typo.font_size_base = typography_data["font_size_base"]
            if "font_size_small" in typography_data:
                typo.font_size_small = typography_data["font_size_small"]
            if "font_size_large" in typography_data:
                typo.font_size_large = typography_data["font_size_large"]
            if "font_size_xlarge" in typography_data:
                typo.font_size_xlarge = typography_data["font_size_xlarge"]
            if "font_weight_normal" in typography_data:
                typo.font_weight_normal = typography_data["font_weight_normal"]
            if "font_weight_bold" in typography_data:
                typo.font_weight_bold = typography_data["font_weight_bold"]
            if "line_height_base" in typography_data:
                typo.line_height_base = typography_data["line_height_base"]
            
            typo.updated_at = datetime.utcnow()
            
            logger.info(f"Typography updated: {typo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update typography: {e}")
            return False
    
    def add_custom_css(self, tenant_id: str, name: str, css_content: str, 
                      minified: bool = False) -> CustomCSS:
        """Add custom CSS"""
        try:
            css = CustomCSS(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=name,
                css_content=css_content,
                minified=minified
            )
            
            self.custom_css[css.id] = css
            
            logger.info(f"Custom CSS added: {css.id} for tenant {tenant_id}")
            return css
            
        except Exception as e:
            logger.error(f"Failed to add custom CSS: {e}")
            raise
    
    def add_custom_javascript(self, tenant_id: str, name: str, js_content: str, 
                            minified: bool = False, load_order: int = 0) -> CustomJavaScript:
        """Add custom JavaScript"""
        try:
            js = CustomJavaScript(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=name,
                js_content=js_content,
                minified=minified,
                load_order=load_order
            )
            
            self.custom_js[js.id] = js
            
            logger.info(f"Custom JavaScript added: {js.id} for tenant {tenant_id}")
            return js
            
        except Exception as e:
            logger.error(f"Failed to add custom JavaScript: {e}")
            raise
    
    def update_email_template(self, tenant_id: str, template_id: str, 
                            template_data: Dict[str, Any]) -> bool:
        """Update email template"""
        try:
            if template_id not in self.email_templates:
                return False
            
            template = self.email_templates[template_id]
            if template.tenant_id != tenant_id:
                return False
            
            # Update template
            if "name" in template_data:
                template.name = template_data["name"]
            if "subject" in template_data:
                template.subject = template_data["subject"]
            if "html_content" in template_data:
                template.html_content = template_data["html_content"]
            if "text_content" in template_data:
                template.text_content = template_data["text_content"]
            if "variables" in template_data:
                template.variables = template_data["variables"]
            if "active" in template_data:
                template.active = template_data["active"]
            
            template.updated_at = datetime.utcnow()
            
            logger.info(f"Email template updated: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update email template: {e}")
            return False
    
    def configure_domain(self, tenant_id: str, domain: str, subdomain: str, 
                        ssl_enabled: bool = True) -> DomainConfiguration:
        """Configure custom domain"""
        try:
            domain_config = DomainConfiguration(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                domain=domain,
                subdomain=subdomain,
                ssl_enabled=ssl_enabled
            )
            
            self.domain_configs[domain_config.id] = domain_config
            
            # In real implementation, this would set up DNS and SSL
            logger.info(f"Domain configuration created: {domain_config.id}")
            return domain_config
            
        except Exception as e:
            logger.error(f"Failed to configure domain: {e}")
            raise
    
    def generate_branding_package(self, tenant_id: str) -> Dict[str, Any]:
        """Generate complete branding package for tenant"""
        try:
            # Get tenant branding data
            config = next((c for c in self.white_label_configs.values() 
                         if c.tenant_id == tenant_id), None)
            
            if not config:
                return {"error": "White-label configuration not found"}
            
            # Get color schemes
            color_schemes = [s for s in self.color_schemes.values() if s.tenant_id == tenant_id]
            
            # Get typography
            typographies = [t for t in self.typographies.values() if t.tenant_id == tenant_id]
            
            # Get assets
            assets = [a for a in self.branding_assets.values() if a.tenant_id == tenant_id]
            
            # Get custom CSS
            custom_css = [css for css in self.custom_css.values() if css.tenant_id == tenant_id]
            
            # Get custom JavaScript
            custom_js = [js for js in self.custom_js.values() if js.tenant_id == tenant_id]
            
            # Get email templates
            email_templates = [t for t in self.email_templates.values() if t.tenant_id == tenant_id]
            
            # Get domain configurations
            domain_configs = [d for d in self.domain_configs.values() if d.tenant_id == tenant_id]
            
            # Generate CSS variables
            css_variables = self._generate_css_variables(color_schemes[0] if color_schemes else None,
                                                       typographies[0] if typographies else None)
            
            # Generate branding package
            branding_package = {
                "configuration": {
                    "company_name": config.company_name,
                    "product_name": config.product_name,
                    "tagline": config.tagline,
                    "description": config.description,
                    "contact_email": config.contact_email,
                    "support_email": config.support_email,
                    "website_url": config.website_url,
                    "privacy_policy_url": config.privacy_policy_url,
                    "terms_of_service_url": config.terms_of_service_url
                },
                "css_variables": css_variables,
                "color_schemes": [
                    {
                        "id": scheme.id,
                        "name": scheme.name,
                        "colors": {
                            "primary": scheme.primary_color,
                            "secondary": scheme.secondary_color,
                            "accent": scheme.accent_color,
                            "background": scheme.background_color,
                            "text": scheme.text_color,
                            "border": scheme.border_color,
                            "success": scheme.success_color,
                            "warning": scheme.warning_color,
                            "error": scheme.error_color
                        }
                    }
                    for scheme in color_schemes
                ],
                "typography": [
                    {
                        "id": typo.id,
                        "font_family": typo.font_family,
                        "font_sizes": {
                            "base": typo.font_size_base,
                            "small": typo.font_size_small,
                            "large": typo.font_size_large,
                            "xlarge": typo.font_size_xlarge
                        },
                        "font_weights": {
                            "normal": typo.font_weight_normal,
                            "bold": typo.font_weight_bold
                        },
                        "line_height": typo.line_height_base
                    }
                    for typo in typographies
                ],
                "assets": [
                    {
                        "id": asset.id,
                        "type": asset.asset_type.value,
                        "name": asset.name,
                        "file_path": asset.file_path,
                        "mime_type": asset.mime_type
                    }
                    for asset in assets
                ],
                "custom_css": [
                    {
                        "id": css.id,
                        "name": css.name,
                        "content": css.css_content,
                        "minified": css.minified
                    }
                    for css in custom_css
                ],
                "custom_javascript": [
                    {
                        "id": js.id,
                        "name": js.name,
                        "content": js.js_content,
                        "minified": js.minified,
                        "load_order": js.load_order
                    }
                    for js in custom_js
                ],
                "email_templates": [
                    {
                        "id": template.id,
                        "type": template.template_type,
                        "name": template.name,
                        "subject": template.subject,
                        "html_content": template.html_content,
                        "text_content": template.text_content,
                        "variables": template.variables
                    }
                    for template in email_templates
                ],
                "domain_configurations": [
                    {
                        "id": domain.id,
                        "domain": domain.domain,
                        "subdomain": domain.subdomain,
                        "ssl_enabled": domain.ssl_enabled,
                        "active": domain.active
                    }
                    for domain in domain_configs
                ]
            }
            
            return branding_package
            
        except Exception as e:
            logger.error(f"Failed to generate branding package: {e}")
            return {"error": str(e)}
    
    def _generate_css_variables(self, color_scheme: Optional[ColorScheme], 
                               typography: Optional[Typography]) -> str:
        """Generate CSS variables from color scheme and typography"""
        try:
            css_vars = []
            
            if color_scheme:
                css_vars.extend([
                    f"--primary-color: {color_scheme.primary_color};",
                    f"--secondary-color: {color_scheme.secondary_color};",
                    f"--accent-color: {color_scheme.accent_color};",
                    f"--background-color: {color_scheme.background_color};",
                    f"--text-color: {color_scheme.text_color};",
                    f"--border-color: {color_scheme.border_color};",
                    f"--success-color: {color_scheme.success_color};",
                    f"--warning-color: {color_scheme.warning_color};",
                    f"--error-color: {color_scheme.error_color};"
                ])
            
            if typography:
                css_vars.extend([
                    f"--font-family: {typography.font_family};",
                    f"--font-size-base: {typography.font_size_base};",
                    f"--font-size-small: {typography.font_size_small};",
                    f"--font-size-large: {typography.font_size_large};",
                    f"--font-size-xlarge: {typography.font_size_xlarge};",
                    f"--font-weight-normal: {typography.font_weight_normal};",
                    f"--font-weight-bold: {typography.font_weight_bold};",
                    f"--line-height-base: {typography.line_height_base};"
                ])
            
            return "\n".join(css_vars)
            
        except Exception as e:
            logger.error(f"Failed to generate CSS variables: {e}")
            return ""
    
    def get_branding_dashboard(self, tenant_id: str) -> Dict[str, Any]:
        """Get branding dashboard for tenant"""
        try:
            dashboard = {
                "branding_status": {},
                "assets_summary": {},
                "templates_summary": {},
                "domain_status": {},
                "recent_changes": []
            }
            
            # Get branding configuration
            config = next((c for c in self.white_label_configs.values() 
                         if c.tenant_id == tenant_id), None)
            
            if config:
                dashboard["branding_status"] = {
                    "company_name": config.company_name,
                    "product_name": config.product_name,
                    "status": config.status.value,
                    "last_updated": config.updated_at.isoformat()
                }
            
            # Assets summary
            assets = [a for a in self.branding_assets.values() if a.tenant_id == tenant_id]
            assets_by_type = defaultdict(int)
            for asset in assets:
                assets_by_type[asset.asset_type.value] += 1
            
            dashboard["assets_summary"] = {
                "total_assets": len(assets),
                "by_type": dict(assets_by_type)
            }
            
            # Templates summary
            templates = [t for t in self.email_templates.values() if t.tenant_id == tenant_id]
            active_templates = sum(1 for t in templates if t.active)
            
            dashboard["templates_summary"] = {
                "total_templates": len(templates),
                "active_templates": active_templates
            }
            
            # Domain status
            domains = [d for d in self.domain_configs.values() if d.tenant_id == tenant_id]
            active_domains = sum(1 for d in domains if d.active)
            
            dashboard["domain_status"] = {
                "total_domains": len(domains),
                "active_domains": active_domains
            }
            
            # Recent changes (simulate recent updates)
            recent_items = []
            
            # Add recent asset uploads
            recent_assets = sorted(assets, key=lambda a: a.updated_at, reverse=True)[:3]
            for asset in recent_assets:
                recent_items.append({
                    "type": "asset",
                    "name": asset.name,
                    "action": "uploaded",
                    "timestamp": asset.updated_at.isoformat()
                })
            
            # Add recent template updates
            recent_templates = sorted(templates, key=lambda t: t.updated_at, reverse=True)[:3]
            for template in recent_templates:
                recent_items.append({
                    "type": "template",
                    "name": template.name,
                    "action": "updated",
                    "timestamp": template.updated_at.isoformat()
                })
            
            # Sort by timestamp
            dashboard["recent_changes"] = sorted(recent_items, 
                                               key=lambda x: x["timestamp"], 
                                               reverse=True)[:5]
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get branding dashboard: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_branding_assets": len(self.branding_assets),
            "total_color_schemes": len(self.color_schemes),
            "total_typographies": len(self.typographies),
            "total_custom_css": len(self.custom_css),
            "total_custom_js": len(self.custom_js),
            "total_email_templates": len(self.email_templates),
            "total_domain_configs": len(self.domain_configs),
            "total_white_label_configs": len(self.white_label_configs),
            "supported_asset_types": [t.value for t in AssetType],
            "theme_types": [t.value for t in ThemeType],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
WHITE_LABELING_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "storage": {
        "asset_storage_path": "/var/lib/helm-ai/assets",
        "max_file_size": 10485760,  # 10MB
        "allowed_mime_types": ["image/jpeg", "image/png", "image/svg+xml", "text/css", "application/javascript"]
    },
    "branding": {
        "default_theme": "light",
        "custom_css_enabled": True,
        "custom_js_enabled": True,
        "email_template_variables": ["company_name", "product_name", "user_name", "login_url"]
    }
}


# Initialize white-labeling manager
white_labeling_manager = WhiteLabelingManager(WHITE_LABELING_CONFIG)

# Export main components
__all__ = [
    'WhiteLabelingManager',
    'BrandingAsset',
    'ColorScheme',
    'Typography',
    'CustomCSS',
    'CustomJavaScript',
    'EmailTemplate',
    'DomainConfiguration',
    'WhiteLabelConfiguration',
    'BrandStatus',
    'AssetType',
    'ThemeType',
    'white_labeling_manager'
]
