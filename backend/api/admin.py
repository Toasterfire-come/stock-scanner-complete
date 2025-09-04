"""
Admin API endpoints for user and system management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..database.connection import get_db_session
from ..database.models import User, Membership, Payment, AuditLog
from ..security.auth import TokenManager, RateLimiter
from ..services.monitoring import Analytics, PerformanceMonitor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(token: str) -> Dict[str, Any]:
    """
    Verify admin access
    """
    payload = TokenManager.verify_token(token)
    if not payload or not payload.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

# User Management Endpoints

@router.get("/users")
@RateLimiter.rate_limit_decorator(max_attempts=100, window_seconds=60)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    List all users with filtering and pagination
    """
    query = db.query(User).join(Membership)
    
    # Apply filters
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    if plan:
        query = query.filter(Membership.plan == plan)
    
    if status:
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)
        elif status == 'verified':
            query = query.filter(User.email_verified == True)
        elif status == 'unverified':
            query = query.filter(User.email_verified == False)
    
    # Pagination
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}",
            'plan': user.membership.plan.value if user.membership else 'free',
            'is_active': user.is_active,
            'email_verified': user.email_verified,
            'created_at': user.created_at,
            'last_login': user.last_login
        } for user in users],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Get detailed user information
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's payments
    payments = db.query(Payment).filter(
        Payment.user_id == user_id
    ).order_by(Payment.created_at.desc()).limit(10).all()
    
    # Get user's audit logs
    audit_logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.created_at.desc()).limit(20).all()
    
    return {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'email_verified': user.email_verified,
            'two_factor_enabled': user.two_factor_enabled,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'last_login': user.last_login,
            'registration_ip': user.registration_ip,
            'last_login_ip': user.last_login_ip
        },
        'membership': {
            'plan': user.membership.plan.value if user.membership else 'free',
            'is_active': user.membership.is_active if user.membership else False,
            'current_period_end': user.membership.current_period_end if user.membership else None,
            'stripe_customer_id': user.membership.stripe_customer_id if user.membership else None
        } if user.membership else None,
        'payments': [{
            'id': payment.id,
            'amount': payment.amount,
            'currency': payment.currency,
            'status': payment.status.value,
            'plan': payment.plan.value,
            'created_at': payment.created_at
        } for payment in payments],
        'audit_logs': [{
            'action': log.action,
            'resource': log.resource,
            'ip_address': log.ip_address,
            'created_at': log.created_at
        } for log in audit_logs]
    }

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    reason: str,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Suspend a user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    # Log action
    audit_log = AuditLog(
        user_id=admin['user_id'],
        action='suspend_user',
        resource='user',
        resource_id=user_id,
        metadata={'reason': reason}
    )
    db.add(audit_log)
    db.commit()
    
    return {'message': 'User suspended successfully'}

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Activate a suspended user account
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    # Log action
    audit_log = AuditLog(
        user_id=admin['user_id'],
        action='activate_user',
        resource='user',
        resource_id=user_id
    )
    db.add(audit_log)
    db.commit()
    
    return {'message': 'User activated successfully'}

@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Force password reset for a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate password reset token
    from ..security.auth import PasswordManager
    reset_token = PasswordManager.generate_secure_token()
    
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send password reset email
    from ..services.email_service import EmailService
    email_service = EmailService()
    await email_service.send_password_reset_email(
        user.email,
        f"{user.first_name} {user.last_name}",
        reset_token
    )
    
    return {'message': 'Password reset email sent'}

# System Management Endpoints

@router.get("/dashboard")
async def admin_dashboard(
    admin = Depends(verify_admin),
    db: Session = Depends(get_db_session)
):
    """
    Get admin dashboard statistics
    """
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.email_verified == True).count()
    
    # Subscription statistics
    memberships = db.query(Membership).all()
    subscription_stats = {
        'free': 0,
        'basic': 0,
        'pro': 0,
        'enterprise': 0
    }
    for membership in memberships:
        subscription_stats[membership.plan.value] += 1
    
    # Revenue statistics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_payments = db.query(Payment).filter(
        Payment.created_at >= thirty_days_ago,
        Payment.status == 'completed'
    ).all()
    
    total_revenue = sum(payment.amount for payment in recent_payments)
    
    # System metrics
    system_metrics = PerformanceMonitor.get_system_metrics()
    
    return {
        'users': {
            'total': total_users,
            'active': active_users,
            'verified': verified_users,
            'unverified': total_users - verified_users
        },
        'subscriptions': subscription_stats,
        'revenue': {
            'last_30_days': total_revenue,
            'transaction_count': len(recent_payments),
            'average_transaction': total_revenue / len(recent_payments) if recent_payments else 0
        },
        'system': system_metrics
    }

@router.get("/analytics")
async def get_analytics(
    period: str = Query('30d', regex='^(7d|30d|90d|1y)$'),
    admin = Depends(verify_admin)
):
    """
    Get detailed analytics
    """
    # Calculate date range
    end_date = datetime.utcnow()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    else:  # 1y
        start_date = end_date - timedelta(days=365)
    
    user_analytics = await Analytics.get_user_analytics(start_date, end_date)
    revenue_analytics = await Analytics.get_revenue_analytics(start_date, end_date)
    api_analytics = await Analytics.get_api_usage_analytics(start_date, end_date)
    
    return {
        'period': {
            'start': start_date,
            'end': end_date
        },
        'users': user_analytics,
        'revenue': revenue_analytics,
        'api': api_analytics
    }

@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Get audit logs with filtering
    """
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Pagination
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return {
        'logs': [{
            'id': log.id,
            'user_id': log.user_id,
            'action': log.action,
            'resource': log.resource,
            'resource_id': log.resource_id,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'status_code': log.status_code,
            'created_at': log.created_at
        } for log in logs],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }

@router.post("/broadcast")
async def send_broadcast(
    subject: str,
    message: str,
    target: str = Query('all', regex='^(all|free|paid)$'),
    db: Session = Depends(get_db_session),
    admin = Depends(verify_admin)
):
    """
    Send broadcast email to users
    """
    query = db.query(User).filter(User.is_active == True)
    
    # Filter by target
    if target == 'free':
        query = query.join(Membership).filter(Membership.plan == 'free')
    elif target == 'paid':
        query = query.join(Membership).filter(Membership.plan != 'free')
    
    users = query.all()
    
    # Queue emails
    from ..services.email_service import EmailQueue
    email_queue = EmailQueue()
    
    for user in users:
        email_queue.enqueue({
            'to_email': user.email,
            'subject': subject,
            'html_content': message,
            'text_content': message
        })
    
    return {
        'message': f'Broadcast queued for {len(users)} users'
    }

@router.post("/maintenance-mode")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    admin = Depends(verify_admin)
):
    """
    Toggle maintenance mode
    """
    import redis
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379))
    )
    
    if enabled:
        r.set('maintenance_mode', 'true')
        if message:
            r.set('maintenance_message', message)
    else:
        r.delete('maintenance_mode')
        r.delete('maintenance_message')
    
    return {
        'maintenance_mode': enabled,
        'message': message if enabled else None
    }