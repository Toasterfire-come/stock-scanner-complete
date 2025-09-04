"""
Database models for production-ready user system
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class PlanType(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Security fields
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    email_verified_at = Column(DateTime)
    
    # Password reset
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # IP tracking for security
    registration_ip = Column(String(45))
    last_login_ip = Column(String(45))
    
    # Relationships
    membership = relationship("Membership", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Membership(Base):
    __tablename__ = 'memberships'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    plan = Column(Enum(PlanType), default=PlanType.FREE)
    
    # Subscription details
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    
    # Plan status
    is_active = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Usage limits
    api_calls_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer)
    storage_used_mb = Column(Float, default=0)
    storage_limit_mb = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="membership")

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_token = Column(String(255), unique=True, index=True)
    refresh_token = Column(String(255), unique=True, index=True)
    
    # Session details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(Text)
    
    # Expiry
    access_token_expires = Column(DateTime)
    refresh_token_expires = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Payment details
    stripe_payment_intent_id = Column(String(255))
    stripe_invoice_id = Column(String(255))
    amount = Column(Float)
    currency = Column(String(3), default='USD')
    status = Column(Enum(PaymentStatus))
    
    # Plan details
    plan = Column(Enum(PlanType))
    billing_period = Column(String(20))  # monthly, yearly
    
    # Metadata
    description = Column(Text)
    metadata = Column(Text)  # JSON field for additional data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
    failed_at = Column(DateTime)
    refunded_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")

class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Key details
    key_hash = Column(String(255), unique=True, index=True)
    key_prefix = Column(String(10))  # First few chars for identification
    name = Column(String(100))
    
    # Permissions
    scopes = Column(Text)  # JSON array of allowed scopes
    
    # Rate limiting
    rate_limit = Column(Integer)
    calls_made = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Action details
    action = Column(String(100))  # login, logout, password_change, etc.
    resource = Column(String(100))  # user, payment, api_key, etc.
    resource_id = Column(Integer)
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_method = Column(String(10))
    request_path = Column(String(255))
    
    # Response
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    
    # Additional data
    metadata = Column(Text)  # JSON field
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Notification details
    type = Column(String(50))  # email, sms, push, in_app
    channel = Column(String(50))  # billing, security, marketing, system
    subject = Column(String(255))
    content = Column(Text)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Priority
    priority = Column(String(20), default='normal')  # low, normal, high, critical
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    subject = Column(String(255))
    html_content = Column(Text)
    text_content = Column(Text)
    
    # Metadata
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)