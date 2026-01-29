"""
Helm AI Billing System
Complete billing and payment processing system with Stripe integration
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timezone, timedelta
import uuid
import stripe
from enum import Enum

from database import get_db, User
from auth import get_current_active_user, get_current_superuser
from user_management import check_permission

# Stripe Configuration (use environment variables in production)
STRIPE_API_KEY = "sk_test_..."  # Replace with actual key
STRIPE_PUBLISHABLE_KEY = "pk_test_..."  # Replace with actual key
STRIPE_WEBHOOK_SECRET = "whsec_..."  # Replace with actual key

stripe.api_key = STRIPE_API_KEY

# Enums
class SubscriptionPlan(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"

# Pydantic Models
class CustomerCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[Dict[str, str]] = None

class PaymentMethodCreate(BaseModel):
    type: str  # "card" or "bank_account"
    card_token: Optional[str] = None
    bank_account_token: Optional[str] = None
    is_default: bool = False

class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan
    payment_method_id: Optional[str] = None
    trial_period_days: Optional[int] = None
    coupon_id: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    plan: Optional[SubscriptionPlan] = None
    payment_method_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None
    coupon_id: Optional[str] = None

class InvoiceCreate(BaseModel):
    customer_id: str
    amount: int
    currency: str = "usd"
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None

class PaymentIntentCreate(BaseModel):
    amount: int
    currency: str = "usd"
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class RefundCreate(BaseModel):
    payment_intent_id: str
    amount: Optional[int] = None
    reason: Optional[str] = None

# Database Models (extend existing database.py)
class Customer(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str]
    company: Optional[str]
    address: Optional[Dict[str, str]]
    stripe_customer_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentMethod(BaseModel):
    id: str
    customer_id: str
    type: str
    last4: str
    brand: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Subscription(BaseModel):
    id: str
    customer_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Invoice(BaseModel):
    id: str
    customer_id: str
    subscription_id: Optional[str]
    status: InvoiceStatus
    amount: int
    currency: str
    description: Optional[str]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentIntent(BaseModel):
    id: str
    customer_id: Optional[str]
    amount: int
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Plan Configuration
PLANS = {
    SubscriptionPlan.STARTER: {
        "name": "Starter Plan",
        "price": 25000,  # $250.00 in cents
        "currency": "usd",
        "interval": "month",
        "features": [
            "Basic AI detection",
            "Up to 1,000 requests/month",
            "Email support",
            "Standard reporting"
        ],
        "stripe_price_id": "price_starter_monthly"  # Replace with actual Stripe price ID
    },
    SubscriptionPlan.PROFESSIONAL: {
        "name": "Professional Plan",
        "price": 100000,  # $1,000.00 in cents
        "currency": "usd",
        "interval": "month",
        "features": [
            "Advanced AI detection",
            "Up to 10,000 requests/month",
            "Priority support",
            "Advanced analytics",
            "Custom integrations"
        ],
        "stripe_price_id": "price_professional_monthly"  # Replace with actual Stripe price ID
    },
    SubscriptionPlan.ENTERPRISE: {
        "name": "Enterprise Plan",
        "price": 500000,  # $5,000.00 in cents
        "currency": "usd",
        "interval": "month",
        "features": [
            "Unlimited AI detection",
            "Unlimited requests",
            "24/7 dedicated support",
            "Enterprise analytics",
            "Custom AI models",
            "On-premise deployment",
            "SLA guarantee"
        ],
        "stripe_price_id": "price_enterprise_monthly"  # Replace with actual Stripe price ID
    }
}

# Customer Management Functions
async def create_customer(db: Session, customer_data: CustomerCreate, user_id: int) -> Customer:
    """Create a new Stripe customer"""
    
    try:
        # Create Stripe customer
        stripe_customer = stripe.Customer.create(
            email=customer_data.email,
            name=customer_data.name,
            phone=customer_data.phone,
            address=customer_data.address,
            metadata={"user_id": str(user_id)}
        )
        
        # Create customer record (in real implementation, save to database)
        customer = Customer(
            id=stripe_customer.id,
            email=customer_data.email,
            name=customer_data.name,
            phone=customer_data.phone,
            company=customer_data.company,
            address=customer_data.address,
            stripe_customer_id=stripe_customer.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return customer
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

async def get_customer(db: Session, customer_id: str) -> Optional[Customer]:
    """Get customer by ID"""
    
    try:
        stripe_customer = stripe.Customer.retrieve(customer_id)
        
        return Customer(
            id=stripe_customer.id,
            email=stripe_customer.email,
            name=stripe_customer.name,
            phone=stripe_customer.phone,
            company=stripe_customer.metadata.get("company"),
            address=stripe_customer.address,
            stripe_customer_id=stripe_customer.id,
            created_at=datetime.fromtimestamp(stripe_customer.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer not found: {str(e)}"
        )

# Payment Method Functions
async def create_payment_method(db: Session, customer_id: str, payment_data: PaymentMethodCreate) -> PaymentMethod:
    """Create a new payment method"""
    
    try:
        if payment_data.type == "card" and payment_data.card_token:
            # Create card payment method
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={"token": payment_data.card_token},
                customer=customer_id
            )
        elif payment_data.type == "bank_account" and payment_data.bank_account_token:
            # Create bank account payment method
            payment_method = stripe.PaymentMethod.create(
                type="bank_account",
                bank_account={"token": payment_data.bank_account_token},
                customer=customer_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method data"
            )
        
        # Set as default if requested
        if payment_data.is_default:
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method.id}
            )
        
        return PaymentMethod(
            id=payment_method.id,
            customer_id=customer_id,
            type=payment_method.type,
            last4=payment_method.card.last4 if payment_method.type == "card" else None,
            brand=payment_method.card.brand if payment_method.type == "card" else None,
            exp_month=payment_method.card.exp_month if payment_method.type == "card" else None,
            exp_year=payment_method.card.exp_year if payment_method.type == "card" else None,
            is_default=payment_data.is_default,
            created_at=datetime.fromtimestamp(payment_method.created, timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

async def get_payment_methods(db: Session, customer_id: str) -> List[PaymentMethod]:
    """Get customer's payment methods"""
    
    try:
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )
        
        result = []
        for pm in payment_methods.data:
            result.append(PaymentMethod(
                id=pm.id,
                customer_id=customer_id,
                type=pm.type,
                last4=pm.card.last4 if pm.type == "card" else None,
                brand=pm.card.brand if pm.type == "card" else None,
                exp_month=pm.card.exp_month if pm.type == "card" else None,
                exp_year=pm.card.exp_year if pm.type == "card" else None,
                is_default=False,  # Would need to check customer's default payment method
                created_at=datetime.fromtimestamp(pm.created, timezone.utc)
            ))
        
        return result
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

# Subscription Functions
async def create_subscription(db: Session, customer_id: str, subscription_data: SubscriptionCreate) -> Subscription:
    """Create a new subscription"""
    
    try:
        plan_config = PLANS.get(subscription_data.plan)
        if not plan_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )
        
        # Create subscription
        subscription_params = {
            "customer": customer_id,
            "items": [{"price": plan_config["stripe_price_id"]}],
            "payment_behavior": "default_incomplete",
            "expand": ["latest_invoice.payment_intent"]
        }
        
        if subscription_data.trial_period_days:
            subscription_params["trial_period_days"] = subscription_data.trial_period_days
        
        if subscription_data.coupon_id:
            subscription_params["coupon"] = subscription_data.coupon_id
        
        if subscription_data.payment_method_id:
            subscription_params["default_payment_method"] = subscription_data.payment_method_id
        
        stripe_subscription = stripe.Subscription.create(**subscription_params)
        
        return Subscription(
            id=stripe_subscription.id,
            customer_id=customer_id,
            plan=subscription_data.plan,
            status=SubscriptionStatus(stripe_subscription.status),
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start, timezone.utc),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end, timezone.utc),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            trial_start=datetime.fromtimestamp(stripe_subscription.trial_start, timezone.utc) if stripe_subscription.trial_start else None,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end, timezone.utc) if stripe_subscription.trial_end else None,
            created_at=datetime.fromtimestamp(stripe_subscription.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

async def get_subscription(db: Session, subscription_id: str) -> Optional[Subscription]:
    """Get subscription by ID"""
    
    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Find the plan from the subscription items
        plan = SubscriptionPlan.STARTER  # Default
        for item in stripe_subscription.items.data:
            for plan_key, plan_config in PLANS.items():
                if item.price.id == plan_config["stripe_price_id"]:
                    plan = plan_key
                    break
        
        return Subscription(
            id=stripe_subscription.id,
            customer_id=stripe_subscription.customer,
            plan=plan,
            status=SubscriptionStatus(stripe_subscription.status),
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start, timezone.utc),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end, timezone.utc),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            trial_start=datetime.fromtimestamp(stripe_subscription.trial_start, timezone.utc) if stripe_subscription.trial_start else None,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end, timezone.utc) if stripe_subscription.trial_end else None,
            created_at=datetime.fromtimestamp(stripe_subscription.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription not found: {str(e)}"
        )

async def update_subscription(db: Session, subscription_id: str, subscription_data: SubscriptionUpdate) -> Subscription:
    """Update subscription"""
    
    try:
        update_params = {}
        
        if subscription_data.plan:
            plan_config = PLANS.get(subscription_data.plan)
            if not plan_config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid plan"
                )
            
            # Get current subscription to preserve other items
            current_sub = stripe.Subscription.retrieve(subscription_id)
            
            update_params = {
                "items": [{"id": current_sub.items.data[0].id, "price": plan_config["stripe_price_id"]}]
            }
        
        if subscription_data.cancel_at_period_end is not None:
            update_params["cancel_at_period_end"] = subscription_data.cancel_at_period_end
        
        if subscription_data.coupon_id:
            update_params["coupon"] = subscription_data.coupon_id
        
        if subscription_data.payment_method_id:
            update_params["default_payment_method"] = subscription_data.payment_method_id
        
        stripe_subscription = stripe.Subscription.modify(subscription_id, **update_params)
        
        # Find the plan from the subscription items
        plan = subscription_data.plan if subscription_data.plan else SubscriptionPlan.STARTER
        for item in stripe_subscription.items.data:
            for plan_key, plan_config in PLANS.items():
                if item.price.id == plan_config["stripe_price_id"]:
                    plan = plan_key
                    break
        
        return Subscription(
            id=stripe_subscription.id,
            customer_id=stripe_subscription.customer,
            plan=plan,
            status=SubscriptionStatus(stripe_subscription.status),
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start, timezone.utc),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end, timezone.utc),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            trial_start=datetime.fromtimestamp(stripe_subscription.trial_start, timezone.utc) if stripe_subscription.trial_start else None,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end, timezone.utc) if stripe_subscription.trial_end else None,
            created_at=datetime.fromtimestamp(stripe_subscription.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

async def cancel_subscription(db: Session, subscription_id: str, at_period_end: bool = True) -> Subscription:
    """Cancel subscription"""
    
    try:
        stripe_subscription = stripe.Subscription.delete(
            subscription_id,
            at_period_end=at_period_end
        )
        
        # Find the plan from the subscription items
        plan = SubscriptionPlan.STARTER  # Default
        for item in stripe_subscription.items.data:
            for plan_key, plan_config in PLANS.items():
                if item.price.id == plan_config["stripe_price_id"]:
                    plan = plan_key
                    break
        
        return Subscription(
            id=stripe_subscription.id,
            customer_id=stripe_subscription.customer,
            plan=plan,
            status=SubscriptionStatus(stripe_subscription.status),
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start, timezone.utc),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end, timezone.utc),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            trial_start=datetime.fromtimestamp(stripe_subscription.trial_start, timezone.utc) if stripe_subscription.trial_start else None,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end, timezone.utc) if stripe_subscription.trial_end else None,
            created_at=datetime.fromtimestamp(stripe_subscription.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

# Invoice Functions
async def create_invoice(db: Session, invoice_data: InvoiceCreate) -> Invoice:
    """Create a new invoice"""
    
    try:
        invoice_params = {
            "customer": invoice_data.customer_id,
            "currency": invoice_data.currency,
            "description": invoice_data.description,
            "metadata": invoice_data.metadata or {}
        }
        
        if invoice_data.due_date:
            invoice_params["due_date"] = int(invoice_data.due_date.timestamp())
        
        # Create invoice item
        stripe.InvoiceItem.create(
            customer=invoice_data.customer_id,
            amount=invoice_data.amount,
            currency=invoice_data.currency,
            description=invoice_data.description
        )
        
        # Create and finalize invoice
        stripe_invoice = stripe.Invoice.create(**invoice_params)
        stripe_invoice = stripe.Invoice.finalize_invoice(stripe_invoice.id)
        
        return Invoice(
            id=stripe_invoice.id,
            customer_id=invoice_data.customer_id,
            subscription_id=None,
            status=InvoiceStatus(stripe_invoice.status),
            amount=invoice_data.amount,
            currency=invoice_data.currency,
            description=invoice_data.description,
            due_date=invoice_data.due_date,
            paid_at=datetime.fromtimestamp(stripe_invoice.status_transitions.paid_at, timezone.utc) if stripe_invoice.status_transitions.paid_at else None,
            created_at=datetime.fromtimestamp(stripe_invoice.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

# Payment Intent Functions
async def create_payment_intent(db: Session, payment_data: PaymentIntentCreate) -> PaymentIntent:
    """Create a new payment intent"""
    
    try:
        intent_params = {
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "description": payment_data.description,
            "metadata": payment_data.metadata or {}
        }
        
        if payment_data.customer_id:
            intent_params["customer"] = payment_data.customer_id
        
        if payment_data.payment_method_id:
            intent_params["payment_method"] = payment_data.payment_method_id
            intent_params["confirm"] = True
        
        stripe_intent = stripe.PaymentIntent.create(**intent_params)
        
        return PaymentIntent(
            id=stripe_intent.id,
            customer_id=payment_data.customer_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status=stripe_intent.status,
            description=payment_data.description,
            created_at=datetime.fromtimestamp(stripe_intent.created, timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

# Refund Functions
async def create_refund(db: Session, refund_data: RefundCreate) -> Dict[str, Any]:
    """Create a refund"""
    
    try:
        refund_params = {
            "payment_intent": refund_data.payment_intent_id,
            "reason": refund_data.reason or "requested_by_customer"
        }
        
        if refund_data.amount:
            refund_params["amount"] = refund_data.amount
        
        stripe_refund = stripe.Refund.create(**refund_params)
        
        return {
            "id": stripe_refund.id,
            "amount": stripe_refund.amount,
            "currency": stripe_refund.currency,
            "status": stripe_refund.status,
            "reason": stripe_refund.reason,
            "created": datetime.fromtimestamp(stripe_refund.created, timezone.utc)
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )

# API Routes
def setup_billing_routes(app: FastAPI):
    """Setup billing routes"""
    
    @app.get("/billing/plans")
    async def get_plans():
        """Get available subscription plans"""
        return PLANS
    
    @app.post("/billing/customers", response_model=Customer)
    async def create_new_customer(
        customer_data: CustomerCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new customer"""
        
        customer = await create_customer(db, customer_data, current_user.id)
        return customer
    
    @app.get("/billing/customers/{customer_id}", response_model=Customer)
    async def get_customer_info(
        customer_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get customer information"""
        
        customer = await get_customer(db, customer_id)
        return customer
    
    @app.post("/billing/payment-methods", response_model=PaymentMethod)
    async def create_new_payment_method(
        customer_id: str,
        payment_data: PaymentMethodCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new payment method"""
        
        payment_method = await create_payment_method(db, customer_id, payment_data)
        return payment_method
    
    @app.get("/billing/payment-methods/{customer_id}", response_model=List[PaymentMethod])
    async def get_customer_payment_methods(
        customer_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get customer's payment methods"""
        
        payment_methods = await get_payment_methods(db, customer_id)
        return payment_methods
    
    @app.post("/billing/subscriptions", response_model=Subscription)
    async def create_new_subscription(
        customer_id: str,
        subscription_data: SubscriptionCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new subscription"""
        
        subscription = await create_subscription(db, customer_id, subscription_data)
        return subscription
    
    @app.get("/billing/subscriptions/{subscription_id}", response_model=Subscription)
    async def get_subscription_info(
        subscription_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Get subscription information"""
        
        subscription = await get_subscription(db, subscription_id)
        return subscription
    
    @app.put("/billing/subscriptions/{subscription_id}", response_model=Subscription)
    async def update_subscription_info(
        subscription_id: str,
        subscription_data: SubscriptionUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Update subscription"""
        
        subscription = await update_subscription(db, subscription_id, subscription_data)
        return subscription
    
    @app.post("/billing/subscriptions/{subscription_id}/cancel", response_model=Subscription)
    async def cancel_subscription_endpoint(
        subscription_id: str,
        at_period_end: bool = True,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Cancel subscription"""
        
        subscription = await cancel_subscription(db, subscription_id, at_period_end)
        return subscription
    
    @app.post("/billing/invoices", response_model=Invoice)
    async def create_new_invoice(
        invoice_data: InvoiceCreate,
        current_user: User = Depends(check_permission("billing", "create")),
        db: Session = Depends(get_db)
    ):
        """Create a new invoice"""
        
        invoice = await create_invoice(db, invoice_data)
        return invoice
    
    @app.post("/billing/payment-intents", response_model=PaymentIntent)
    async def create_new_payment_intent(
        payment_data: PaymentIntentCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Create a new payment intent"""
        
        payment_intent = await create_payment_intent(db, payment_data)
        return payment_intent
    
    @app.post("/billing/refunds")
    async def create_new_refund(
        refund_data: RefundCreate,
        current_user: User = Depends(check_permission("billing", "create")),
        db: Session = Depends(get_db)
    ):
        """Create a refund"""
        
        refund = await create_refund(db, refund_data)
        return refund

# Export functions
__all__ = [
    "setup_billing_routes",
    "create_customer",
    "get_customer",
    "create_payment_method",
    "get_payment_methods",
    "create_subscription",
    "get_subscription",
    "update_subscription",
    "cancel_subscription",
    "create_invoice",
    "create_payment_intent",
    "create_refund",
    "PLANS",
    "CustomerCreate",
    "PaymentMethodCreate",
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "InvoiceCreate",
    "PaymentIntentCreate",
    "RefundCreate",
    "Customer",
    "PaymentMethod",
    "Subscription",
    "Invoice",
    "PaymentIntent"
]
