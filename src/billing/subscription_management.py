"""
Helm AI Advanced Subscription Management System
Provides comprehensive subscription management with billing, plans, and customer lifecycle
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
from decimal import Decimal, ROUND_HALF_UP

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PENDING = "pending"

class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class PlanType(Enum):
    """Plan type enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class PaymentMethod(Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    INVOICE = "invoice"
    CRYPTOCURRENCY = "cryptocurrency"

class InvoiceStatus(Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    plan_id: str
    name: str
    description: str
    plan_type: PlanType
    price: Decimal
    currency: str
    billing_cycle: BillingCycle
    features: Dict[str, Any]
    limits: Dict[str, Any]
    trial_days: int
    setup_fee: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'plan_type': self.plan_type.value,
            'price': float(self.price),
            'currency': self.currency,
            'billing_cycle': self.billing_cycle.value,
            'features': self.features,
            'limits': self.limits,
            'trial_days': self.trial_days,
            'setup_fee': float(self.setup_fee),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class CustomerSubscription:
    """Customer subscription record"""
    subscription_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    started_at: datetime
    ends_at: Optional[datetime]
    trial_ends_at: Optional[datetime]
    billing_cycle: BillingCycle
    price: Decimal
    currency: str
    auto_renew: bool
    payment_method_id: str
    usage_metrics: Dict[str, Any]
    features_used: Set[str]
    limits_reached: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary"""
        return {
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'billing_cycle': self.billing_cycle.value,
            'price': float(self.price),
            'currency': self.currency,
            'auto_renew': self.auto_renew,
            'payment_method_id': self.payment_method_id,
            'usage_metrics': self.usage_metrics,
            'features_used': list(self.features_used),
            'limits_reached': self.limits_reached,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class PaymentMethod:
    """Payment method record"""
    payment_method_id: str
    customer_id: str
    method_type: PaymentMethod
    provider: str
    provider_payment_method_id: str
    is_default: bool
    card_last4: Optional[str]
    card_brand: Optional[str]
    card_exp_month: Optional[int]
    card_exp_year: Optional[int]
    billing_address: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment method to dictionary"""
        return {
            'payment_method_id': self.payment_method_id,
            'customer_id': self.customer_id,
            'method_type': self.method_type.value,
            'provider': self.provider,
            'provider_payment_method_id': self.provider_payment_method_id,
            'is_default': self.is_default,
            'card_last4': self.card_last4,
            'card_brand': self.card_brand,
            'card_exp_month': self.card_exp_month,
            'card_exp_year': self.card_exp_year,
            'billing_address': self.billing_address,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Invoice:
    """Invoice record"""
    invoice_id: str
    subscription_id: str
    customer_id: str
    invoice_number: str
    status: InvoiceStatus
    amount: Decimal
    currency: str
    due_date: datetime
    paid_date: Optional[datetime]
    line_items: List[Dict[str, Any]]
    taxes: List[Dict[str, Any]]
    discounts: List[Dict[str, Any]]
    total_tax: Decimal
    total_discount: Decimal
    payment_method_id: str
    notes: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary"""
        return {
            'invoice_id': self.invoice_id,
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'invoice_number': self.invoice_number,
            'status': self.status.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'due_date': self.due_date.isoformat(),
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'line_items': self.line_items,
            'taxes': self.taxes,
            'discounts': self.discounts,
            'total_tax': float(self.total_tax),
            'total_discount': float(self.total_discount),
            'payment_method_id': self.payment_method_id,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class UsageMetric:
    """Usage metric record"""
    metric_id: str
    subscription_id: str
    metric_name: str
    metric_value: Union[int, float, Decimal]
    metric_unit: str
    recorded_at: datetime
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert usage metric to dictionary"""
        return {
            'metric_id': self.metric_id,
            'subscription_id': self.subscription_id,
            'metric_name': self.metric_name,
            'metric_value': float(self.metric_value) if isinstance(self.metric_value, Decimal) else self.metric_value,
            'metric_unit': self.metric_unit,
            'recorded_at': self.recorded_at.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'metadata': self.metadata
        }

class SubscriptionManager:
    """Subscription management system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.subscriptions: Dict[str, CustomerSubscription] = {}
        self.payment_methods: Dict[str, PaymentMethod] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.usage_metrics: Dict[str, UsageMetric] = {}
        self.customer_data: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # Configuration
        self.default_currency = os.getenv('DEFAULT_CURRENCY', 'USD')
        self.trial_conversion_rate = float(os.getenv('TRIAL_CONVERSION_RATE', '0.25'))
        self.late_fee_rate = float(os.getenv('LATE_FEE_RATE', '0.02'))
        self.invoice_due_days = int(os.getenv('INVOICE_DUE_DAYS', '30'))
        
        # Initialize default plans
        self._initialize_default_plans()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_plans(self) -> None:
        """Initialize default subscription plans"""
        # Free Plan
        free_plan = SubscriptionPlan(
            plan_id="free",
            name="Free Plan",
            description="Basic features for individuals and small teams",
            plan_type=PlanType.FREE,
            price=Decimal('0.00'),
            currency=self.default_currency,
            billing_cycle=BillingCycle.MONTHLY,
            features={
                'api_access': True,
                'basic_analytics': True,
                'email_support': True,
                '1_user': True,
                '1gb_storage': True
            },
            limits={
                'users': 1,
                'storage_gb': 1,
                'api_calls_per_day': 1000,
                'reports_per_month': 10
            },
            trial_days=0,
            setup_fee=Decimal('0.00'),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Basic Plan
        basic_plan = SubscriptionPlan(
            plan_id="basic",
            name="Basic Plan",
            description="Professional features for growing teams",
            plan_type=PlanType.BASIC,
            price=Decimal('29.00'),
            currency=self.default_currency,
            billing_cycle=BillingCycle.MONTHLY,
            features={
                'api_access': True,
                'advanced_analytics': True,
                'email_support': True,
                '5_users': True,
                '10gb_storage': True,
                'priority_support': True
            },
            limits={
                'users': 5,
                'storage_gb': 10,
                'api_calls_per_day': 10000,
                'reports_per_month': 100
            },
            trial_days=14,
            setup_fee=Decimal('0.00'),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Professional Plan
        professional_plan = SubscriptionPlan(
            plan_id="professional",
            name="Professional Plan",
            description="Advanced features for professional teams",
            plan_type=PlanType.PROFESSIONAL,
            price=Decimal('99.00'),
            currency=self.default_currency,
            billing_cycle=BillingCycle.MONTHLY,
            features={
                'api_access': True,
                'advanced_analytics': True,
                'phone_support': True,
                'unlimited_users': True,
                '100gb_storage': True,
                'priority_support': True,
                'custom_integrations': True,
                'advanced_security': True
            },
            limits={
                'users': 999999,  # Unlimited
                'storage_gb': 100,
                'api_calls_per_day': 100000,
                'reports_per_month': 1000
            },
            trial_days=14,
            setup_fee=Decimal('0.00'),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Enterprise Plan
        enterprise_plan = SubscriptionPlan(
            plan_id="enterprise",
            name="Enterprise Plan",
            description="Complete solution for large organizations",
            plan_type=PlanType.ENTERPRISE,
            price=Decimal('499.00'),
            currency=self.default_currency,
            billing_cycle=BillingCycle.MONTHLY,
            features={
                'api_access': True,
                'advanced_analytics': True,
                '24_7_support': True,
                'unlimited_users': True,
                'unlimited_storage': True,
                'dedicated_account_manager': True,
                'custom_integrations': True,
                'advanced_security': True,
                'sla_guarantee': True,
                'custom_training': True,
                'white_labeling': True
            },
            limits={
                'users': 999999,  # Unlimited
                'storage_gb': 999999,  # Unlimited
                'api_calls_per_day': 999999,  # Unlimited
                'reports_per_month': 999999  # Unlimited
            },
            trial_days=30,
            setup_fee=Decimal('1000.00'),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add plans to registry
        self.plans[free_plan.plan_id] = free_plan
        self.plans[basic_plan.plan_id] = basic_plan
        self.plans[professional_plan.plan_id] = professional_plan
        self.plans[enterprise_plan.plan_id] = enterprise_plan
        
        logger.info(f"Initialized {len(self.plans)} default subscription plans")
    
    def create_subscription(self, customer_id: str, plan_id: str, payment_method_id: str, 
                          trial: bool = False, metadata: Optional[Dict[str, Any]] = None) -> CustomerSubscription:
        """Create a new subscription"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        
        if not plan.is_active:
            raise ValueError(f"Plan {plan_id} is not active")
        
        subscription_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate dates
        started_at = now
        trial_ends_at = now + timedelta(days=plan.trial_days) if trial and plan.trial_days > 0 else None
        ends_at = self._calculate_subscription_end_date(started_at, plan.billing_cycle)
        
        # Create subscription
        subscription = CustomerSubscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.TRIAL if trial_ends_at else SubscriptionStatus.ACTIVE,
            started_at=started_at,
            ends_at=ends_at,
            trial_ends_at=trial_ends_at,
            billing_cycle=plan.billing_cycle,
            price=plan.price,
            currency=plan.currency,
            auto_renew=True,
            payment_method_id=payment_method_id,
            usage_metrics={},
            features_used=set(),
            limits_reached=[],
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        )
        
        with self.lock:
            self.subscriptions[subscription_id] = subscription
        
        # Create initial invoice if not trial
        if not trial_ends_at:
            self._create_subscription_invoice(subscription)
        
        logger.info(f"Created subscription {subscription_id} for customer {customer_id}")
        
        return subscription
    
    def _calculate_subscription_end_date(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate subscription end date based on billing cycle"""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.YEARLY:
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)  # Default to monthly
    
    def _create_subscription_invoice(self, subscription: CustomerSubscription) -> Invoice:
        """Create invoice for subscription"""
        plan = self.plans[subscription.plan_id]
        invoice_id = str(uuid.uuid4())
        invoice_number = self._generate_invoice_number()
        
        # Calculate line items
        line_items = [
            {
                'description': f"{plan.name} - {plan.billing_cycle.value}",
                'quantity': 1,
                'unit_price': float(plan.price),
                'amount': float(plan.price)
            }
        ]
        
        # Add setup fee if applicable
        total_amount = plan.price
        if plan.setup_fee > 0:
            line_items.append({
                'description': 'Setup Fee',
                'quantity': 1,
                'unit_price': float(plan.setup_fee),
                'amount': float(plan.setup_fee)
            })
            total_amount += plan.setup_fee
        
        # Calculate taxes (simplified)
        tax_rate = Decimal('0.08')  # 8% tax rate
        total_tax = total_amount * tax_rate
        
        # Calculate due date
        due_date = datetime.utcnow() + timedelta(days=self.invoice_due_days)
        
        invoice = Invoice(
            invoice_id=invoice_id,
            subscription_id=subscription.subscription_id,
            customer_id=subscription.customer_id,
            invoice_number=invoice_number,
            status=InvoiceStatus.DRAFT,
            amount=total_amount + total_tax,
            currency=subscription.currency,
            due_date=due_date,
            paid_date=None,
            line_items=line_items,
            taxes=[{'rate': float(tax_rate), 'amount': float(total_tax)}],
            discounts=[],
            total_tax=total_tax,
            total_discount=Decimal('0.00'),
            payment_method_id=subscription.payment_method_id,
            notes="",
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with self.lock:
            self.invoices[invoice_id] = invoice
        
        return invoice
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().hex[:8]).upper()
        return f"INV-{timestamp}-{random_suffix}"
    
    def upgrade_subscription(self, subscription_id: str, new_plan_id: str, 
                           immediate: bool = True) -> CustomerSubscription:
        """Upgrade subscription to new plan"""
        with self.lock:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            if new_plan_id not in self.plans:
                raise ValueError(f"Plan {new_plan_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            old_plan = self.plans[subscription.plan_id]
            new_plan = self.plans[new_plan_id]
            
            # Check if it's actually an upgrade
            if new_plan.price <= old_plan.price:
                raise ValueError("New plan must be more expensive than current plan")
            
            # Create new subscription
            new_subscription_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Calculate proration if immediate
            if immediate:
                # Calculate remaining value of current subscription
                remaining_days = (subscription.ends_at - now).days
                if remaining_days > 0:
                    daily_rate = subscription.price / 30  # Simplified daily rate
                    credit_amount = daily_rate * remaining_days
                    
                    # Apply credit to new subscription
                    new_price = new_plan.price - credit_amount
                else:
                    new_price = new_plan.price
            else:
                new_price = new_plan.price
            
            new_subscription = CustomerSubscription(
                subscription_id=new_subscription_id,
                customer_id=subscription.customer_id,
                plan_id=new_plan_id,
                status=SubscriptionStatus.ACTIVE,
                started_at=now,
                ends_at=self._calculate_subscription_end_date(now, new_plan.billing_cycle),
                trial_ends_at=None,
                billing_cycle=new_plan.billing_cycle,
                price=new_price,
                currency=new_plan.currency,
                auto_renew=subscription.auto_renew,
                payment_method_id=subscription.payment_method_id,
                usage_metrics=subscription.usage_metrics,
                features_used=subscription.features_used,
                limits_reached=[],
                metadata=subscription.metadata,
                created_at=now,
                updated_at=now
            )
            
            # Cancel old subscription
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.ends_at = now
            
            # Add new subscription
            self.subscriptions[new_subscription_id] = new_subscription
            
            # Create invoice for upgrade
            if immediate:
                self._create_upgrade_invoice(new_subscription, credit_amount if 'credit_amount' in locals() else Decimal('0.00'))
            
            logger.info(f"Upgraded subscription {subscription_id} to {new_plan_id}")
            
            return new_subscription
    
    def _create_upgrade_invoice(self, subscription: CustomerSubscription, credit_amount: Decimal) -> Invoice:
        """Create invoice for subscription upgrade"""
        plan = self.plans[subscription.plan_id]
        invoice_id = str(uuid.uuid4())
        invoice_number = self._generate_invoice_number()
        
        # Calculate line items
        line_items = [
            {
                'description': f"Upgrade to {plan.name} - {plan.billing_cycle.value}",
                'quantity': 1,
                'unit_price': float(subscription.price),
                'amount': float(subscription.price)
            }
        ]
        
        # Add credit if applicable
        discounts = []
        if credit_amount > 0:
            discounts.append({
                'description': 'Proration Credit',
                'amount': float(credit_amount)
            })
        
        total_amount = subscription.price - credit_amount
        
        # Calculate taxes
        tax_rate = Decimal('0.08')
        total_tax = total_amount * tax_rate
        
        invoice = Invoice(
            invoice_id=invoice_id,
            subscription_id=subscription.subscription_id,
            customer_id=subscription.customer_id,
            invoice_number=invoice_number,
            status=InvoiceStatus.DRAFT,
            amount=total_amount + total_tax,
            currency=subscription.currency,
            due_date=datetime.utcnow() + timedelta(days=self.invoice_due_days),
            paid_date=None,
            line_items=line_items,
            taxes=[{'rate': float(tax_rate), 'amount': float(total_tax)}],
            discounts=discounts,
            total_tax=total_tax,
            total_discount=credit_amount,
            payment_method_id=subscription.payment_method_id,
            notes="Upgrade invoice with proration credit",
            metadata={'upgrade': True},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with self.lock:
            self.invoices[invoice_id] = invoice
        
        return invoice
    
    def cancel_subscription(self, subscription_id: str, reason: str = "") -> bool:
        """Cancel subscription"""
        with self.lock:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.ends_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            
            # Add cancellation reason to metadata
            if reason:
                subscription.metadata['cancellation_reason'] = reason
            
            logger.info(f"Cancelled subscription {subscription_id}")
            
            return True
    
    def renew_subscription(self, subscription_id: str) -> bool:
        """Renew subscription"""
        with self.lock:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            if subscription.status != SubscriptionStatus.ACTIVE:
                return False
            
            # Calculate new end date
            new_end_date = self._calculate_subscription_end_date(subscription.ends_at, subscription.billing_cycle)
            
            # Update subscription
            subscription.ends_at = new_end_date
            subscription.updated_at = datetime.utcnow()
            
            # Create new invoice
            self._create_subscription_invoice(subscription)
            
            logger.info(f"Renewed subscription {subscription_id}")
            
            return True
    
    def record_usage(self, subscription_id: str, metric_name: str, metric_value: Union[int, float, Decimal], 
                    metric_unit: str = "count", metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record usage metric"""
        with self.lock:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # Create usage metric
            metric_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            usage_metric = UsageMetric(
                metric_id=metric_id,
                subscription_id=subscription_id,
                metric_name=metric_name,
                metric_value=Decimal(str(metric_value)) if isinstance(metric_value, (int, float, Decimal)) else metric_value,
                metric_unit=metric_unit,
                recorded_at=now,
                period_start=now.replace(day=1),  # Start of month
                period_end=now.replace(day=28),  # End of month (simplified)
                metadata=metadata or {}
            )
            
            self.usage_metrics[metric_id] = usage_metric
            
            # Update subscription usage metrics
            subscription.usage_metrics[metric_name] = float(metric_value)
            subscription.updated_at = now
            
            # Check limits
            self._check_subscription_limits(subscription)
            
            return True
    
    def _check_subscription_limits(self, subscription: CustomerSubscription) -> None:
        """Check if subscription limits are reached"""
        plan = self.plans[subscription.plan_id]
        
        # Check each limit
        for limit_name, limit_value in plan.limits.items():
            current_usage = subscription.usage_metrics.get(limit_name, 0)
            
            if current_usage >= limit_value:
                if limit_name not in subscription.limits_reached:
                    subscription.limits_reached.append(limit_name)
                    logger.warning(f"Limit reached for subscription {subscription.subscription_id}: {limit_name}")
            else:
                if limit_name in subscription.limits_reached:
                    subscription.limits_reached.remove(limit_name)
    
    def get_subscription_usage(self, subscription_id: str, period_start: Optional[datetime] = None, 
                            period_end: Optional[datetime] = None) -> Dict[str, Any]:
        """Get subscription usage for a period"""
        with self.lock:
            if subscription_id not in self.subscriptions:
                return {}
            
            subscription = self.subscriptions[subscription_id]
            
            # Filter usage metrics by period
            usage_metrics = []
            for metric in self.usage_metrics.values():
                if metric.subscription_id == subscription_id:
                    if period_start and period_end:
                        if period_start <= metric.recorded_at <= period_end:
                            usage_metrics.append(metric)
                    else:
                        usage_metrics.append(metric)
            
            # Aggregate metrics
            aggregated_usage = {}
            for metric in usage_metrics:
                if metric.metric_name not in aggregated_usage:
                    aggregated_usage[metric.metric_name] = {
                        'total': 0,
                        'unit': metric.metric_unit,
                        'count': 0
                    }
                
                aggregated_usage[metric.metric_name]['total'] += float(metric.metric_value)
                aggregated_usage[metric.metric_name]['count'] += 1
            
            return {
                'subscription_id': subscription_id,
                'period_start': period_start.isoformat() if period_start else None,
                'period_end': period_end.isoformat() if period_end else None,
                'usage_metrics': aggregated_usage,
                'limits_reached': subscription.limits_reached,
                'plan_limits': self.plans[subscription.plan_id].limits
            }
    
    def add_payment_method(self, customer_id: str, method_type: PaymentMethod, provider: str,
                          provider_payment_method_id: str, billing_address: Dict[str, Any],
                          card_details: Optional[Dict[str, Any]] = None,
                          is_default: bool = False) -> PaymentMethod:
        """Add payment method for customer"""
        payment_method_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # If setting as default, unset other defaults
        if is_default:
            for pm in self.payment_methods.values():
                if pm.customer_id == customer_id and pm.is_default:
                    pm.is_default = False
                    pm.updated_at = now
        
        payment_method = PaymentMethod(
            payment_method_id=payment_method_id,
            customer_id=customer_id,
            method_type=method_type,
            provider=provider,
            provider_payment_method_id=provider_payment_method_id,
            is_default=is_default,
            card_last4=card_details.get('last4') if card_details else None,
            card_brand=card_details.get('brand') if card_details else None,
            card_exp_month=card_details.get('exp_month') if card_details else None,
            card_exp_year=card_details.get('exp_year') if card_details else None,
            billing_address=billing_address,
            metadata={},
            created_at=now,
            updated_at=now
        )
        
        with self.lock:
            self.payment_methods[payment_method_id] = payment_method
        
        logger.info(f"Added payment method {payment_method_id} for customer {customer_id}")
        
        return payment_method
    
    def get_customer_subscriptions(self, customer_id: str) -> List[CustomerSubscription]:
        """Get all subscriptions for a customer"""
        with self.lock:
            return [sub for sub in self.subscriptions.values() if sub.customer_id == customer_id]
    
    def get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription management metrics"""
        with self.lock:
            total_subscriptions = len(self.subscriptions)
            active_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
            trial_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.TRIAL])
            
            # Revenue metrics
            monthly_revenue = sum(s.price for s in self.subscriptions.values() if s.billing_cycle == BillingCycle.MONTHLY and s.status == SubscriptionStatus.ACTIVE)
            yearly_revenue = sum(s.price for s in self.subscriptions.values() if s.billing_cycle == BillingCycle.YEARLY and s.status == SubscriptionStatus.ACTIVE)
            
            # Plan distribution
            plan_distribution = defaultdict(int)
            for subscription in self.subscriptions.values():
                plan_distribution[subscription.plan_id] += 1
            
            # Churn rate (simplified)
            cancelled_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.CANCELLED])
            churn_rate = (cancelled_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
            
            return {
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions,
                'trial_subscriptions': trial_subscriptions,
                'cancelled_subscriptions': cancelled_subscriptions,
                'churn_rate': round(churn_rate, 2),
                'monthly_revenue': float(monthly_revenue),
                'yearly_revenue': float(yearly_revenue),
                'plan_distribution': dict(plan_distribution),
                'total_payment_methods': len(self.payment_methods),
                'total_invoices': len(self.invoices),
                'paid_invoices': len([i for i in self.invoices.values() if i.status == InvoiceStatus.PAID]),
                'overdue_invoices': len([i for i in self.invoices.values() if i.status == InvoiceStatus.OVERDUE])
            }
    
    def _start_background_tasks(self) -> None:
        """Start background subscription tasks"""
        # Start subscription renewal thread
        renewal_thread = threading.Thread(target=self._process_renewals, daemon=True)
        renewal_thread.start()
        
        # Start trial expiration thread
        trial_thread = threading.Thread(target=self._process_trial_expirations, daemon=True)
        trial_thread.start()
        
        # Start invoice processing thread
        invoice_thread = threading.Thread(target=self._process_invoices, daemon=True)
        invoice_thread.start()
    
    def _process_renewals(self) -> None:
        """Process subscription renewals"""
        while True:
            try:
                # Check every hour
                time.sleep(3600)
                
                now = datetime.utcnow()
                renewals_processed = 0
                
                with self.lock:
                    for subscription in self.subscriptions.values():
                        if (subscription.status == SubscriptionStatus.ACTIVE and
                            subscription.auto_renew and
                            subscription.ends_at <= now):
                            
                            if self.renew_subscription(subscription.subscription_id):
                                renewals_processed += 1
                
                if renewals_processed > 0:
                    logger.info(f"Processed {renewals_processed} subscription renewals")
                
            except Exception as e:
                logger.error(f"Renewal processing failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _process_trial_expirations(self) -> None:
        """Process trial expirations"""
        while True:
            try:
                # Check every hour
                time.sleep(3600)
                
                now = datetime.utcnow()
                trials_expired = 0
                
                with self.lock:
                    for subscription in self.subscriptions.values():
                        if (subscription.status == SubscriptionStatus.TRIAL and
                            subscription.trial_ends_at and
                            subscription.trial_ends_at <= now):
                            
                            # Convert to paid subscription or cancel
                            if subscription.auto_renew:
                                subscription.status = SubscriptionStatus.ACTIVE
                                subscription.trial_ends_at = None
                                subscription.updated_at = now
                                
                                # Create first invoice
                                self._create_subscription_invoice(subscription)
                                trials_expired += 1
                            else:
                                subscription.status = SubscriptionStatus.EXPIRED
                                subscription.trial_ends_at = None
                                subscription.updated_at = now
                                trials_expired += 1
                
                if trials_expired > 0:
                    logger.info(f"Processed {trials_expired} trial expirations")
                
            except Exception as e:
                logger.error(f"Trial expiration processing failed: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _process_invoices(self) -> None:
        """Process invoice status updates"""
        while True:
            try:
                # Check every 6 hours
                time.sleep(21600)
                
                now = datetime.utcnow()
                invoices_processed = 0
                
                with self.lock:
                    for invoice in self.invoices.values():
                        if invoice.status == InvoiceStatus.SENT and invoice.due_date <= now:
                            # Mark as overdue
                            invoice.status = InvoiceStatus.OVERDUE
                            invoice.updated_at = now
                            invoices_processed += 1
                
                if invoices_processed > 0:
                    logger.info(f"Processed {invoices_processed} overdue invoices")
                
            except Exception as e:
                logger.error(f"Invoice processing failed: {e}")
                time.sleep(1800)  # Wait 30 minutes before retrying

# Global subscription manager instance
subscription_manager = SubscriptionManager()

# Export main components
__all__ = [
    'SubscriptionManager',
    'SubscriptionPlan',
    'CustomerSubscription',
    'PaymentMethod',
    'Invoice',
    'UsageMetric',
    'SubscriptionStatus',
    'BillingCycle',
    'PlanType',
    'PaymentMethod',
    'InvoiceStatus',
    'subscription_manager'
]
