"""
Authentication and security utilities for production
"""
import os
import secrets
import hashlib
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pyotp
import qrcode
from io import BytesIO
import base64
from email_validator import validate_email, EmailNotValidError
import re
from functools import wraps
import redis
import json

# Security configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_EXPIRE_HOURS = 1
EMAIL_VERIFICATION_EXPIRE_DAYS = 7

# Redis for rate limiting and session management
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

class PasswordPolicy:
    """
    Password strength validation
    """
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """
        Validate password against policy
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if cls.REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARS)}]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if password.lower() in weak_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, "Password is valid"

class TokenManager:
    """
    JWT token management with refresh tokens
    """
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Create JWT access token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            'exp': expire,
            'type': 'access',
            'iat': datetime.utcnow()
        })
        return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            'exp': expire,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)  # Unique token ID
        })
        token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Store in Redis for revocation capability
        redis_client.setex(
            f"refresh_token:{to_encode['jti']}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            json.dumps(data)
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            if payload.get('type') != token_type:
                return None
            
            # Check if refresh token is revoked
            if token_type == 'refresh':
                jti = payload.get('jti')
                if not redis_client.exists(f"refresh_token:{jti}"):
                    return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    @staticmethod
    def revoke_refresh_token(jti: str):
        """
        Revoke a refresh token
        """
        redis_client.delete(f"refresh_token:{jti}")

class PasswordManager:
    """
    Secure password hashing and verification
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a secure random token
        """
        return secrets.token_urlsafe(length)

class TwoFactorAuth:
    """
    Two-factor authentication using TOTP
    """
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new 2FA secret
        """
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(email: str, secret: str) -> str:
        """
        Generate QR code for 2FA setup
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name='Stock Scanner'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify 2FA token
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

class RateLimiter:
    """
    Rate limiting for API endpoints and login attempts
    """
    
    @staticmethod
    def check_rate_limit(
        key: str,
        max_attempts: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns (is_allowed, remaining_attempts)
        """
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window_seconds, 1)
            return True, max_attempts - 1
        
        current = int(current)
        if current >= max_attempts:
            ttl = redis_client.ttl(key)
            return False, ttl
        
        redis_client.incr(key)
        return True, max_attempts - current - 1
    
    @staticmethod
    def rate_limit_decorator(max_attempts: int = 10, window_seconds: int = 60):
        """
        Decorator for rate limiting endpoints
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract request from args (FastAPI passes it as first arg)
                request = args[0] if args else None
                if not request:
                    return await func(*args, **kwargs)
                
                # Get client IP
                client_ip = request.client.host
                key = f"rate_limit:{func.__name__}:{client_ip}"
                
                allowed, remaining = RateLimiter.check_rate_limit(
                    key, max_attempts, window_seconds
                )
                
                if not allowed:
                    from fastapi import HTTPException
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Try again in {remaining} seconds"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

class SessionManager:
    """
    User session management
    """
    
    @staticmethod
    def create_session(user_id: int, ip_address: str, user_agent: str) -> Dict[str, str]:
        """
        Create a new user session
        """
        session_id = secrets.token_urlsafe(32)
        
        # Create tokens
        access_token = TokenManager.create_access_token({
            'user_id': user_id,
            'session_id': session_id
        })
        
        refresh_token = TokenManager.create_refresh_token({
            'user_id': user_id,
            'session_id': session_id
        })
        
        # Store session in Redis
        session_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        }
        
        redis_client.setex(
            f"session:{session_id}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            json.dumps(session_data)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id
        }
    
    @staticmethod
    def validate_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate and get session data
        """
        session_data = redis_client.get(f"session:{session_id}")
        if not session_data:
            return None
        
        data = json.loads(session_data)
        
        # Update last activity
        data['last_activity'] = datetime.utcnow().isoformat()
        redis_client.setex(
            f"session:{session_id}",
            REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            json.dumps(data)
        )
        
        return data
    
    @staticmethod
    def revoke_session(session_id: str):
        """
        Revoke a user session
        """
        redis_client.delete(f"session:{session_id}")
    
    @staticmethod
    def revoke_all_user_sessions(user_id: int):
        """
        Revoke all sessions for a user
        """
        # Get all session keys
        pattern = "session:*"
        for key in redis_client.scan_iter(match=pattern):
            session_data = redis_client.get(key)
            if session_data:
                data = json.loads(session_data)
                if data.get('user_id') == user_id:
                    redis_client.delete(key)

class EmailValidator:
    """
    Email validation and verification
    """
    
    @staticmethod
    def validate(email: str) -> tuple[bool, str]:
        """
        Validate email format and domain
        """
        try:
            # Validate format
            validation = validate_email(email, check_deliverability=False)
            email = validation.email
            
            # Check for disposable email domains
            disposable_domains = [
                'tempmail.com', 'throwaway.email', '10minutemail.com',
                'guerrillamail.com', 'mailinator.com'
            ]
            
            domain = email.split('@')[1].lower()
            if domain in disposable_domains:
                return False, "Disposable email addresses are not allowed"
            
            return True, email
        except EmailNotValidError as e:
            return False, str(e)

class IPGeolocation:
    """
    IP-based geolocation and security checks
    """
    
    @staticmethod
    def get_location(ip_address: str) -> Dict[str, Any]:
        """
        Get geolocation data for IP address
        """
        # In production, use a service like MaxMind or IPGeolocation API
        # This is a placeholder implementation
        return {
            'ip': ip_address,
            'country': 'Unknown',
            'city': 'Unknown',
            'is_vpn': False,
            'is_tor': False,
            'risk_score': 0
        }
    
    @staticmethod
    def check_suspicious_activity(ip_address: str) -> bool:
        """
        Check if IP shows suspicious activity
        """
        # Check recent failed login attempts
        key = f"failed_login:{ip_address}"
        attempts = redis_client.get(key)
        
        if attempts and int(attempts) > 5:
            return True
        
        # Check IP reputation (placeholder)
        # In production, use threat intelligence feeds
        
        return False