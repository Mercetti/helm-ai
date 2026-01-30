"""
Helm AI Advanced Subscription Management System
Provides comprehensive subscription billing, management, and analytics
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import stripe
from sqlalchemy import text

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from monitoring.distributed_tracing import distributed_tracer
from database.database_manager import get_database_manager

class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    PAUSED = "paused"

class SubscriptionTier(Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

class PaymentMethod(Enum):
    """Payment method enumeration"""
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    PAYPAL = "paypal"
    CRYPTO = "crypto"
    INVOICE = "invoice"
    WIRE_TRANSFER = "wire_transfer"

@dataclass
class SubscriptionPlan:
    """Subscription plan configuration"""
    plan_id: str
    name: str
    tier: SubscriptionTier
    price: float
    currency: str = "USD"
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    features: List[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    trial_days: int = 0
    setup_fee: float = 0.0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'tier': self.tier.value,
            'price': self.price,
            'currency': self.currency,
            'billing_cycle': self.billing_cycle.value,
            'features': self.features,
            'limits': self.limits,
            'trial_days': self.trial_days,
            'setup_fee': self.setup_fee,
            'is_active': self.is_active,
            'metadata': self.metadata
        }

@dataclass
class Subscription:
    """User subscription"""
    subscription_id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status.value,
            'current_period_start': self.current_period_start.isoformat(),
            'current_period_end': self.current_period_end.isoformat(),
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'canceled_at': self.canceled_at.isoformat() if self.canceled_at else None,
            'paused_at': self.paused_at.isoformat() if self.paused_at else None,
            'payment_method_id': self.payment_method_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Invoice:
    """Subscription invoice"""
    invoice_id: str
    subscription_id: str
    user_id: str
    amount: float
    currency: str
    status: str  # draft, open, paid, void, uncollectible
    due_date: datetime
    paid_at: Optional[datetime] = None
    stripe_invoice_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'invoice_id': self.invoice_id,
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'due_date': self.due_date.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'stripe_invoice_id': self.stripe_invoice_id,
            'payment_method_id': self.payment_method_id,
            'line_items': self.line_items,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class UsageMetric:
    """Usage metric for billing"""
    metric_id: str
    subscription_id: str
    metric_name: str
    quantity: float
    unit: str
    period_start: datetime
    period_end: datetime
    recorded_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'subscription_id': self.subscription_id,
            'metric_name': self.metric_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'recorded_at': self.recorded_at.isoformat(),
            'metadata': self.metadata
        }

class SubscriptionManager:
    """Advanced subscription management system"""
    
    def __init__(self):
        self.plans = {}
        self.subscriptions = {}
        self.invoices = {}
        self.usage_metrics = deque(maxlen=10000)
        self.billing_events = deque(maxlen=5000)
        self.lock = threading.RLock()
        
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Configuration
        self.config = {
            'default_currency': 'USD',
            'trial_period_days': 14,
            'grace_period_days': 7,
            'dunning_enabled': True,
            'auto_renewal_enabled': True,
            'usage_tracking_enabled': True,
            'invoice_generation_days_before': 7,
            'late_fee_percentage': 0.05,
            'currency_conversion_enabled': True
        }
        
        # Setup default plans
        self._setup_default_plans()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_default_plans(self):
        """Setup default subscription plans"""
        # Free plan
        free_plan = SubscriptionPlan(
            plan_id="free",
            name="Free Tier",
            tier=SubscriptionTier.FREE,
            price=0.0,
            billing_cycle=BillingCycle.MONTHLY,
            features=[
                "Basic AI features",
                "1,000 API calls/month",
                "Community support",
                "Basic analytics"
            ],
            limits={
                "api_calls": 1000,
                "storage_gb": 1,
                "team_members": 1,
                "projects": 3
            },
            trial_days=0
        )
        
        # Basic plan
        basic_plan = SubscriptionPlan(
            plan_id="basic",
            name="Basic Plan",
            tier=SubscriptionTier.BASIC,
            price=29.99,
            billing_cycle=BillingCycle.MONTHLY,
            features=[
                "Advanced AI features",
                "10,000 API calls/month",
                "Email support",
                "Advanced analytics",
                "Custom integrations"
            ],
            limits={
                "api_calls": 10000,
                "storage_gb": 10,
                "team_members": 5,
                "projects": 20
            },
            trial_days=14
        )
        
        # Professional plan
        professional_plan = SubscriptionPlan(
            plan_id="professional",
            name="Professional Plan",
            tier=SubscriptionTier.PROFESSIONAL,
            price=99.99,
            billing_cycle=BillingCycle.MONTHLY,
            features=[
                "Premium AI features",
                "100,000 API calls/month",
                "Priority support",
                "Real-time analytics",
                "Advanced integrations",
                "Custom models",
                "White-labeling"
            ],
            limits={
                "api_calls": 100000,
                "storage_gb": 100,
                "team_members": 20,
                "projects": 100
            },
            trial_days=14
        )
        
        # Enterprise plan
        enterprise_plan = SubscriptionPlan(
            plan_id="enterprise",
            name="Enterprise Plan",
            tier=SubscriptionTier.ENTERPRISE,
            price=499.99,
            billing_cycle=BillingCycle.MONTHLY,
            features=[
                "Unlimited AI features",
                "Unlimited API calls",
                "24/7 dedicated support",
                "Enterprise analytics",
                "Custom integrations",
                "Custom models",
                "White-labeling",
                "SLA guarantee",
                "On-premise deployment"
            ],
            limits={
                "api_calls": float('inf'),
                "storage_gb": float('inf'),
                "team_members": float('inf'),
                "projects": float('inf')
            },
            trial_days=30
        )
        
        # Register plans
        for plan in [free_plan, basic_plan, professional_plan, enterprise_plan]:
            self.plans[plan.plan_id] = plan
    
    def _start_background_tasks(self):
        """Start background billing tasks"""
        # Invoice generation
        invoice_thread = threading.Thread(
            target=self._invoice_generation_loop,
            daemon=True,
            name="subscription-invoice-generation"
        )
        invoice_thread.start()
        
        # Subscription renewal
        renewal_thread = threading.Thread(
            target=self._subscription_renewal_loop,
            daemon=True,
            name="subscription-renewal"
        )
        renewal_thread.start()
        
        # Usage tracking
        usage_thread = threading.Thread(
            target=self._usage_tracking_loop,
            daemon=True,
            name="usage-tracking"
        )
        usage_thread.start()
    
    def create_subscription(self, user_id: str, plan_id: str, payment_method_id: str,
                          trial_days: Optional[int] = None) -> Optional[Subscription]:
        """Create new subscription"""
        try:
            with distributed_tracer.trace_span("create_subscription", "subscription-manager"):
                logger.info(f"Creating subscription for user {user_id} with plan {plan_id}")
                
                # Validate plan
                plan = self.plans.get(plan_id)
                if not plan or not plan.is_active:
                    raise ValueError(f"Invalid or inactive plan: {plan_id}")
                
                # Check existing subscription
                existing_subscription = self._get_user_subscription(user_id)
                if existing_subscription and existing_subscription.status == SubscriptionStatus.ACTIVE:
                    raise ValueError("User already has an active subscription")
                
                # Create subscription in Stripe
                stripe_subscription = self._create_stripe_subscription(
                    user_id, plan, payment_method_id, trial_days
                )
                
                # Calculate period dates
                now = datetime.now()
                trial_end = None
                if trial_days or plan.trial_days:
                    trial_days = trial_days or plan.trial_days
                    trial_end = now + timedelta(days=trial_days)
                    period_start = trial_end
                else:
                    period_start = now
                
                # Calculate period end based on billing cycle
                if plan.billing_cycle == BillingCycle.MONTHLY:
                    period_end = period_start + timedelta(days=30)
                elif plan.billing_cycle == BillingCycle.QUARTERLY:
                    period_end = period_start + timedelta(days=90)
                elif plan.billing_cycle == BillingCycle.ANNUAL:
                    period_end = period_start + timedelta(days=365)
                else:
                    period_end = period_start + timedelta(days=30)
                
                # Create subscription
                subscription = Subscription(
                    subscription_id=str(uuid.uuid4()),
                    user_id=user_id,
                    plan_id=plan_id,
                    status=SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE,
                    current_period_start=period_start,
                    current_period_end=period_end,
                    trial_end=trial_end,
                    payment_method_id=payment_method_id,
                    stripe_subscription_id=stripe_subscription.id if stripe_subscription else None
                )
                
                # Store subscription
                with self.lock:
                    self.subscriptions[subscription.subscription_id] = subscription
                
                # Store in database
                self._store_subscription(subscription)
                
                # Log billing event
                self._log_billing_event('subscription_created', subscription)
                
                logger.info(f"Created subscription {subscription.subscription_id} for user {user_id}")
                return subscription
                
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    def _create_stripe_subscription(self, user_id: str, plan: SubscriptionPlan,
                                  payment_method_id: str, trial_days: Optional[int]) -> Optional[Any]:
        """Create subscription in Stripe"""
        try:
            # Get or create Stripe customer
            customer = self._get_or_create_stripe_customer(user_id)
            
            # Create subscription
            subscription_data = {
                'customer': customer.id,
                'items': [{
                    'price_data': {
                        'currency': plan.currency,
                        'product_data': {
                            'name': plan.name,
                            'description': f'{plan.tier.value.title()} subscription'
                        },
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                        'recurring': {
                            'interval': plan.billing_cycle.value.replace('ly', '')
                        }
                    }
                }],
                'default_payment_method': payment_method_id,
                'expand': ['latest_invoice.payment_intent']
            }
            
            # Add trial period if specified
            if trial_days or plan.trial_days:
                trial_days = trial_days or plan.trial_days
                subscription_data['trial_period_days'] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_data)
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            return None
    
    def _get_or_create_stripe_customer(self, user_id: str) -> Any:
        """Get or create Stripe customer"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check if customer already exists
                result = session.execute(text("""
                    SELECT stripe_customer_id FROM users WHERE user_id = :user_id
                """), {'user_id': user_id})
                
                customer_id = result.fetchone()
                
                if customer_id and customer_id[0]:
                    # Retrieve existing customer
                    return stripe.Customer.retrieve(customer_id[0])
                else:
                    # Create new customer
                    user_result = session.execute(text("""
                        SELECT email, first_name, last_name FROM users WHERE user_id = :user_id
                    """), {'user_id': user_id})
                    
                    user_data = user_result.fetchone()
                    if not user_data:
                        raise ValueError(f"User not found: {user_id}")
                    
                    email, first_name, last_name = user_data
                    
                    customer = stripe.Customer.create(
                        email=email,
                        name=f"{first_name} {last_name}",
                        metadata={'user_id': user_id}
                    )
                    
                    # Update user with customer ID
                    session.execute(text("""
                        UPDATE users SET stripe_customer_id = :customer_id WHERE user_id = :user_id
                    """), {
                        'customer_id': customer.id,
                        'user_id': user_id
                    })
                    
                    session.commit()
                    return customer
                    
        except Exception as e:
            logger.error(f"Error getting/creating Stripe customer: {e}")
            raise
    
    def _get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's active subscription"""
        with self.lock:
            for subscription in self.subscriptions.values():
                if subscription.user_id == user_id and subscription.status in [
                    SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING
                ]:
                    return subscription
        return None
    
    def upgrade_subscription(self, user_id: str, new_plan_id: str) -> bool:
        """Upgrade user subscription"""
        try:
            with distributed_tracer.trace_span("upgrade_subscription", "subscription-manager"):
                current_subscription = self._get_user_subscription(user_id)
                if not current_subscription:
                    raise ValueError("No active subscription found")
                
                new_plan = self.plans.get(new_plan_id)
                if not new_plan:
                    raise ValueError(f"Invalid plan: {new_plan_id}")
                
                # Check if it's actually an upgrade
                current_plan = self.plans.get(current_subscription.plan_id)
                if new_plan.price <= current_plan.price:
                    raise ValueError("New plan must be more expensive for upgrade")
                
                # Update Stripe subscription
                if current_subscription.stripe_subscription_id:
                    self._update_stripe_subscription(current_subscription.stripe_subscription_id, new_plan)
                
                # Update local subscription
                current_subscription.plan_id = new_plan_id
                current_subscription.updated_at = datetime.now()
                
                # Store in database
                self._update_subscription(current_subscription)
                
                # Log billing event
                self._log_billing_event('subscription_upgraded', current_subscription)
                
                logger.info(f"Upgraded subscription for user {user_id} to plan {new_plan_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error upgrading subscription: {e}")
            return False
    
    def downgrade_subscription(self, user_id: str, new_plan_id: str) -> bool:
        """Downgrade user subscription (takes effect next billing cycle)"""
        try:
            with distributed_tracer.trace_span("downgrade_subscription", "subscription-manager"):
                current_subscription = self._get_user_subscription(user_id)
                if not current_subscription:
                    raise ValueError("No active subscription found")
                
                new_plan = self.plans.get(new_plan_id)
                if not new_plan:
                    raise ValueError(f"Invalid plan: {new_plan_id}")
                
                # Schedule downgrade for next billing cycle
                current_subscription.metadata['scheduled_downgrade'] = new_plan_id
                current_subscription.updated_at = datetime.now()
                
                # Store in database
                self._update_subscription(current_subscription)
                
                # Log billing event
                self._log_billing_event('subscription_downgrade_scheduled', current_subscription)
                
                logger.info(f"Scheduled downgrade for user {user_id} to plan {new_plan_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error downgrading subscription: {e}")
            return False
    
    def cancel_subscription(self, user_id: str, cancel_at_period_end: bool = True) -> bool:
        """Cancel user subscription"""
        try:
            with distributed_tracer.trace_span("cancel_subscription", "subscription-manager"):
                current_subscription = self._get_user_subscription(user_id)
                if not current_subscription:
                    raise ValueError("No active subscription found")
                
                # Cancel in Stripe
                if current_subscription.stripe_subscription_id:
                    stripe.Subscription.modify(
                        current_subscription.stripe_subscription_id,
                        cancel_at_period_end=cancel_at_period_end
                    )
                
                # Update local subscription
                if cancel_at_period_end:
                    current_subscription.metadata['cancellation_scheduled'] = True
                else:
                    current_subscription.status = SubscriptionStatus.CANCELED
                    current_subscription.canceled_at = datetime.now()
                
                current_subscription.updated_at = datetime.now()
                
                # Store in database
                self._update_subscription(current_subscription)
                
                # Log billing event
                self._log_billing_event('subscription_canceled', current_subscription)
                
                logger.info(f"Canceled subscription for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            return False
    
    def pause_subscription(self, user_id: str) -> bool:
        """Pause user subscription"""
        try:
            with distributed_tracer.trace_span("pause_subscription", "subscription-manager"):
                current_subscription = self._get_user_subscription(user_id)
                if not current_subscription:
                    raise ValueError("No active subscription found")
                
                # Pause in Stripe
                if current_subscription.stripe_subscription_id:
                    stripe.Subscription.modify(
                        current_subscription.stripe_subscription_id,
                        pause_collection={'behavior': 'keep_as_draft'}
                    )
                
                # Update local subscription
                current_subscription.status = SubscriptionStatus.PAUSED
                current_subscription.paused_at = datetime.now()
                current_subscription.updated_at = datetime.now()
                
                # Store in database
                self._update_subscription(current_subscription)
                
                # Log billing event
                self._log_billing_event('subscription_paused', current_subscription)
                
                logger.info(f"Paused subscription for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error pausing subscription: {e}")
            return False
    
    def resume_subscription(self, user_id: str) -> bool:
        """Resume paused subscription"""
        try:
            with distributed_tracer.trace_span("resume_subscription", "subscription-manager"):
                current_subscription = self._get_user_subscription(user_id)
                if not current_subscription or current_subscription.status != SubscriptionStatus.PAUSED:
                    raise ValueError("No paused subscription found")
                
                # Resume in Stripe
                if current_subscription.stripe_subscription_id:
                    stripe.Subscription.modify(
                        current_subscription.stripe_subscription_id,
                        pause_collection=''
                    )
                
                # Update local subscription
                current_subscription.status = SubscriptionStatus.ACTIVE
                current_subscription.paused_at = None
                current_subscription.updated_at = datetime.now()
                
                # Store in database
                self._update_subscription(current_subscription)
                
                # Log billing event
                self._log_billing_event('subscription_resumed', current_subscription)
                
                logger.info(f"Resumed subscription for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error resuming subscription: {e}")
            return False
    
    def record_usage(self, user_id: str, metric_name: str, quantity: float,
                     unit: str, metadata: Dict[str, Any] = None) -> bool:
        """Record usage metric for billing"""
        try:
            subscription = self._get_user_subscription(user_id)
            if not subscription:
                return False
            
            # Create usage metric
            usage_metric = UsageMetric(
                metric_id=str(uuid.uuid4()),
                subscription_id=subscription.subscription_id,
                metric_name=metric_name,
                quantity=quantity,
                unit=unit,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                metadata=metadata or {}
            )
            
            # Store usage metric
            with self.lock:
                self.usage_metrics.append(usage_metric)
            
            # Store in database
            self._store_usage_metric(usage_metric)
            
            logger.info(f"Recorded usage: {metric_name} = {quantity} {unit} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            return False
    
    def get_subscription_usage(self, user_id: str, period_start: datetime = None,
                             period_end: datetime = None) -> Dict[str, Any]:
        """Get subscription usage summary"""
        try:
            subscription = self._get_user_subscription(user_id)
            if not subscription:
                return {}
            
            # Default to current period
            if not period_start:
                period_start = subscription.current_period_start
            if not period_end:
                period_end = subscription.current_period_end
            
            # Get usage metrics for period
            with self.lock:
                usage_metrics = [
                    metric for metric in self.usage_metrics
                    if (metric.subscription_id == subscription.subscription_id and
                        metric.period_start >= period_start and
                        metric.period_end <= period_end)
                ]
            
            # Aggregate by metric name
            usage_summary = defaultdict(lambda: {'quantity': 0, 'unit': '', 'count': 0})
            
            for metric in usage_metrics:
                usage_summary[metric.metric_name]['quantity'] += metric.quantity
                usage_summary[metric.metric_name]['unit'] = metric.unit
                usage_summary[metric.metric_name]['count'] += 1
            
            # Get plan limits
            plan = self.plans.get(subscription.plan_id)
            limits = plan.limits if plan else {}
            
            return {
                'subscription_id': subscription.subscription_id,
                'plan_id': subscription.plan_id,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'usage': dict(usage_summary),
                'limits': limits,
                'utilization': {
                    metric: {
                        'used': usage_summary[metric]['quantity'],
                        'limit': limits.get(metric, float('inf')),
                        'percentage': (usage_summary[metric]['quantity'] / limits.get(metric, float('inf')) * 100) if limits.get(metric) != float('inf') else 0
                    }
                    for metric in usage_summary
                    if metric in limits
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription usage: {e}")
            return {}
    
    def get_billing_summary(self, user_id: str) -> Dict[str, Any]:
        """Get billing summary for user"""
        try:
            subscription = self._get_user_subscription(user_id)
            if not subscription:
                return {}
            
            plan = self.plans.get(subscription.plan_id)
            if not plan:
                return {}
            
            # Get recent invoices
            with self.lock:
                recent_invoices = [
                    invoice for invoice in self.invoices.values()
                    if invoice.user_id == user_id
                ][:10]  # Last 10 invoices
            
            # Calculate totals
            total_paid = sum(invoice.amount for invoice in recent_invoices if invoice.status == 'paid')
            total_outstanding = sum(invoice.amount for invoice in recent_invoices if invoice.status == 'open')
            
            return {
                'subscription': subscription.to_dict(),
                'plan': plan.to_dict(),
                'next_billing_date': subscription.current_period_end.isoformat(),
                'amount_due': plan.price,
                'currency': plan.currency,
                'total_paid': total_paid,
                'total_outstanding': total_outstanding,
                'recent_invoices': [invoice.to_dict() for invoice in recent_invoices],
                'payment_method_id': subscription.payment_method_id
            }
            
        except Exception as e:
            logger.error(f"Error getting billing summary: {e}")
            return {}
    
    def _store_subscription(self, subscription: Subscription):
        """Store subscription in database"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                session.execute(text("""
                    INSERT INTO subscriptions (
                        subscription_id, user_id, plan_id, status,
                        current_period_start, current_period_end, trial_end,
                        canceled_at, paused_at, payment_method_id,
                        stripe_subscription_id, metadata, created_at, updated_at
                    ) VALUES (
                        :subscription_id, :user_id, :plan_id, :status,
                        :current_period_start, :current_period_end, :trial_end,
                        :canceled_at, :paused_at, :payment_method_id,
                        :stripe_subscription_id, :metadata, :created_at, :updated_at
                    )
                """), {
                    'subscription_id': subscription.subscription_id,
                    'user_id': subscription.user_id,
                    'plan_id': subscription.plan_id,
                    'status': subscription.status.value,
                    'current_period_start': subscription.current_period_start,
                    'current_period_end': subscription.current_period_end,
                    'trial_end': subscription.trial_end,
                    'canceled_at': subscription.canceled_at,
                    'paused_at': subscription.paused_at,
                    'payment_method_id': subscription.payment_method_id,
                    'stripe_subscription_id': subscription.stripe_subscription_id,
                    'metadata': json.dumps(subscription.metadata),
                    'created_at': subscription.created_at,
                    'updated_at': subscription.updated_at
                })
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error storing subscription in database: {e}")
    
    def _update_subscription(self, subscription: Subscription):
        """Update subscription in database"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                session.execute(text("""
                    UPDATE subscriptions SET
                        plan_id = :plan_id, status = :status,
                        current_period_start = :current_period_start,
                        current_period_end = :current_period_end, trial_end = :trial_end,
                        canceled_at = :canceled_at, paused_at = :paused_at,
                        payment_method_id = :payment_method_id,
                        stripe_subscription_id = :stripe_subscription_id,
                        metadata = :metadata, updated_at = :updated_at
                    WHERE subscription_id = :subscription_id
                """), {
                    'subscription_id': subscription.subscription_id,
                    'plan_id': subscription.plan_id,
                    'status': subscription.status.value,
                    'current_period_start': subscription.current_period_start,
                    'current_period_end': subscription.current_period_end,
                    'trial_end': subscription.trial_end,
                    'canceled_at': subscription.canceled_at,
                    'paused_at': subscription.paused_at,
                    'payment_method_id': subscription.payment_method_id,
                    'stripe_subscription_id': subscription.stripe_subscription_id,
                    'metadata': json.dumps(subscription.metadata),
                    'updated_at': subscription.updated_at
                })
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error updating subscription in database: {e}")
    
    def _store_usage_metric(self, usage_metric: UsageMetric):
        """Store usage metric in database"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                session.execute(text("""
                    INSERT INTO usage_metrics (
                        metric_id, subscription_id, metric_name, quantity,
                        unit, period_start, period_end, recorded_at, metadata
                    ) VALUES (
                        :metric_id, :subscription_id, :metric_name, :quantity,
                        :unit, :period_start, :period_end, :recorded_at, :metadata
                    )
                """), {
                    'metric_id': usage_metric.metric_id,
                    'subscription_id': usage_metric.subscription_id,
                    'metric_name': usage_metric.metric_name,
                    'quantity': usage_metric.quantity,
                    'unit': usage_metric.unit,
                    'period_start': usage_metric.period_start,
                    'period_end': usage_metric.period_end,
                    'recorded_at': usage_metric.recorded_at,
                    'metadata': json.dumps(usage_metric.metadata)
                })
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error storing usage metric in database: {e}")
    
    def _log_billing_event(self, event_type: str, subscription: Subscription):
        """Log billing event"""
        try:
            event = {
                'event_id': str(uuid.uuid4()),
                'timestamp': datetime.now(),
                'event_type': event_type,
                'subscription_id': subscription.subscription_id,
                'user_id': subscription.user_id,
                'plan_id': subscription.plan_id,
                'status': subscription.status.value
            }
            
            with self.lock:
                self.billing_events.append(event)
            
            # Store in database
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                session.execute(text("""
                    INSERT INTO billing_events (
                        event_id, timestamp, event_type, subscription_id,
                        user_id, plan_id, status, metadata
                    ) VALUES (
                        :event_id, :timestamp, :event_type, :subscription_id,
                        :user_id, :plan_id, :status, :metadata
                    )
                """), {
                    'event_id': event['event_id'],
                    'timestamp': event['timestamp'],
                    'event_type': event['event_type'],
                    'subscription_id': event['subscription_id'],
                    'user_id': event['user_id'],
                    'plan_id': event['plan_id'],
                    'status': event['status'],
                    'metadata': json.dumps({k: v for k, v in event.items() if k not in [
                        'event_id', 'timestamp', 'event_type', 'subscription_id',
                        'user_id', 'plan_id', 'status'
                    ]})
                })
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Error logging billing event: {e}")
    
    def _invoice_generation_loop(self):
        """Background loop for invoice generation"""
        while True:
            try:
                # Generate invoices for upcoming billing periods
                self._generate_upcoming_invoices()
                
                # Sleep for 6 hours
                time.sleep(21600)
                
            except Exception as e:
                logger.error(f"Error in invoice generation loop: {e}")
                time.sleep(3600)
    
    def _subscription_renewal_loop(self):
        """Background loop for subscription renewal"""
        while True:
            try:
                # Process renewals and expirations
                self._process_subscription_renewals()
                
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in subscription renewal loop: {e}")
                time.sleep(1800)
    
    def _usage_tracking_loop(self):
        """Background loop for usage tracking"""
        while True:
            try:
                # Process usage metrics and billing
                self._process_usage_billing()
                
                # Sleep for 24 hours
                time.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error in usage tracking loop: {e}")
                time.sleep(3600)
    
    def _generate_upcoming_invoices(self):
        """Generate invoices for upcoming billing periods"""
        # Implementation would generate invoices for subscriptions nearing renewal
        pass
    
    def _process_subscription_renewals(self):
        """Process subscription renewals and expirations"""
        # Implementation would handle automatic renewals and expirations
        pass
    
    def _process_usage_billing(self):
        """Process usage-based billing"""
        # Implementation would calculate and bill for usage-based metrics
        pass
    
    def get_subscription_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get subscription metrics and analytics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.lock:
                # Get recent subscriptions
                recent_subscriptions = [
                    sub for sub in self.subscriptions.values()
                    if sub.created_at >= cutoff_date
                ]
                
                # Get billing events
                recent_events = [
                    event for event in self.billing_events
                    if datetime.fromisoformat(event['timestamp']) >= cutoff_date
                ]
                
                # Calculate metrics
                total_subscriptions = len(self.subscriptions)
                active_subscriptions = len([
                    sub for sub in self.subscriptions.values()
                    if sub.status == SubscriptionStatus.ACTIVE
                ])
                
                new_subscriptions = len(recent_subscriptions)
                churned_subscriptions = len([
                    event for event in recent_events
                    if event['event_type'] == 'subscription_canceled'
                ])
                
                # Revenue metrics
                monthly_recurring_revenue = sum(
                    self.plans[sub.plan_id].price
                    for sub in self.subscriptions.values()
                    if sub.status == SubscriptionStatus.ACTIVE and
                    self.plans.get(sub.plan_id)
                )
                
                # Plan distribution
                plan_distribution = defaultdict(int)
                for sub in self.subscriptions.values():
                    if sub.status == SubscriptionStatus.ACTIVE:
                        plan_distribution[sub.plan_id] += 1
            
            return {
                'period_days': days,
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions,
                'new_subscriptions': new_subscriptions,
                'churned_subscriptions': churned_subscriptions,
                'churn_rate': (churned_subscriptions / max(active_subscriptions + churned_subscriptions, 1)) * 100,
                'monthly_recurring_revenue': monthly_recurring_revenue,
                'plan_distribution': dict(plan_distribution),
                'average_revenue_per_user': monthly_recurring_revenue / max(active_subscriptions, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription metrics: {e}")
            return {}

# Global subscription manager instance
subscription_manager = SubscriptionManager()

def create_subscription(user_id: str, plan_id: str, payment_method_id: str,
                      trial_days: int = None) -> Optional[Subscription]:
    """Create new subscription"""
    return subscription_manager.create_subscription(user_id, plan_id, payment_method_id, trial_days)

def upgrade_subscription(user_id: str, new_plan_id: str) -> bool:
    """Upgrade user subscription"""
    return subscription_manager.upgrade_subscription(user_id, new_plan_id)

def cancel_subscription(user_id: str, cancel_at_period_end: bool = True) -> bool:
    """Cancel user subscription"""
    return subscription_manager.cancel_subscription(user_id, cancel_at_period_end)

def record_usage(user_id: str, metric_name: str, quantity: float,
                 unit: str, metadata: Dict[str, Any] = None) -> bool:
    """Record usage metric"""
    return subscription_manager.record_usage(user_id, metric_name, quantity, unit, metadata)

def get_billing_summary(user_id: str) -> Dict[str, Any]:
    """Get billing summary for user"""
    return subscription_manager.get_billing_summary(user_id)

def get_subscription_metrics(days: int = 30) -> Dict[str, Any]:
    """Get subscription metrics"""
    return subscription_manager.get_subscription_metrics(days)
