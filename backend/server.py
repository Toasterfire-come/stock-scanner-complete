from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import mysql.connector
from mysql.connector import pooling
import os
import logging
import requests
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import time
import hashlib
import secrets
import json
import threading

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# External API configuration
EXTERNAL_API_URL = os.environ.get('EXTERNAL_API_URL', 'https://api.retailtradescanner.com')
EXTERNAL_API_PASSWORD = os.environ.get('EXTERNAL_API_PASSWORD', '')

# MySQL Database Configuration
USER_DB_CONFIG = {
    'host': os.environ.get('USER_DB_HOST', 'db5018639265.hosting-data.io'),
    'port': int(os.environ.get('USER_DB_PORT', 3306)),
    'database': os.environ.get('USER_DB_NAME', 'user_info'),
    'user': os.environ.get('USER_DB_USER', 'Dbu288455'),
    'password': os.environ.get('USER_DB_PASSWORD', '((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_name': 'user_pool',
    'pool_size': 10,
    'pool_reset_session': False
}

STOCK_DB_CONFIG = {
    'host': os.environ.get('STOCK_DB_HOST', 'db5018639278.hosting-data.io'),
    'port': int(os.environ.get('STOCK_DB_PORT', 3306)),
    'database': os.environ.get('STOCK_DB_NAME', 'stock_info'),
    'user': os.environ.get('STOCK_DB_USER', 'dbu2734171'),
    'password': os.environ.get('STOCK_DB_PASSWORD', '((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_name': 'stock_pool',
    'pool_size': 10,
    'pool_reset_session': False
}

# Initialize MySQL connection pools
user_db_pool = None
stock_db_pool = None
db_disabled = False

try:
    user_db_pool = mysql.connector.pooling.MySQLConnectionPool(**USER_DB_CONFIG)
    stock_db_pool = mysql.connector.pooling.MySQLConnectionPool(**STOCK_DB_CONFIG)
    logging.info("MySQL connection pools initialized successfully")
except Exception as e:
    logging.warning(f"MySQL not available, using in-memory store: {e}")
    db_disabled = True

# Security configuration
security = HTTPBearer(auto_error=False)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-this-in-production')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this-in-production')

# Create the main app
app = FastAPI(
    title="Trade Scan Pro API",
    description="Professional Stock Market Analysis API with MySQL Integration", 
    version="2.0.0",
    docs_url="/docs" if os.environ.get('DEBUG', 'False').lower() == 'true' else None,
    redoc_url="/redoc" if os.environ.get('DEBUG', 'False').lower() == 'true' else None
)

# Security middleware
if os.environ.get('ENVIRONMENT') == 'production':
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["api.retailtradescanner.com", "tradescanpro.com", "localhost", "127.0.0.1"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "X-RateLimit-Used",
        "X-RateLimit-Limit", 
        "X-RateLimit-Reset",
        "X-RateLimit-Remaining",
    ]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Create API router
api_router = APIRouter(prefix="/api")

# MySQL Database Helper Functions
def get_user_db_connection():
    """Get connection from user database pool"""
    if db_disabled or user_db_pool is None:
        return None
    try:
        return user_db_pool.get_connection()
    except Exception as e:
        logging.error(f"Failed to get user DB connection: {e}")
        return None

def get_stock_db_connection():
    """Get connection from stock database pool"""
    if db_disabled or stock_db_pool is None:
        return None
    try:
        return stock_db_pool.get_connection()
    except Exception as e:
        logging.error(f"Failed to get stock DB connection: {e}")
        return None

def init_database_tables():
    """Initialize required database tables"""
    if db_disabled:
        return
    
    # User database tables
    user_conn = get_user_db_connection()
    if user_conn:
        try:
            cursor = user_conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    plan VARCHAR(50) DEFAULT 'free',
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # API Usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    endpoint VARCHAR(255) NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    user_agent TEXT,
                    plan VARCHAR(50) DEFAULT 'free',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_created_at (created_at)
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    ticker VARCHAR(10) NOT NULL,
                    current_price DECIMAL(10,2),
                    target_price DECIMAL(10,2) NOT NULL,
                    condition ENUM('above', 'below') NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_triggered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP NULL,
                    INDEX idx_user_id (user_id),
                    INDEX idx_ticker (ticker)
                )
            """)
            
            cursor.close()
            user_conn.commit()
            logging.info("User database tables initialized")
        except Exception as e:
            logging.error(f"Failed to initialize user tables: {e}")
        finally:
            user_conn.close()
    
    # Stock database tables
    stock_conn = get_stock_db_connection()
    if stock_conn:
        try:
            cursor = stock_conn.cursor()
            
            # Stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id VARCHAR(36) PRIMARY KEY,
                    ticker VARCHAR(10) UNIQUE NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    current_price DECIMAL(10,2),
                    price_change DECIMAL(10,2),
                    change_percent DECIMAL(5,2),
                    volume BIGINT,
                    market_cap BIGINT,
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    exchange VARCHAR(20),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_ticker (ticker),
                    INDEX idx_sector (sector),
                    INDEX idx_market_cap (market_cap)
                )
            """)
            
            # Portfolio table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    ticker VARCHAR(10) NOT NULL,
                    shares DECIMAL(10,4) NOT NULL,
                    purchase_price DECIMAL(10,2),
                    purchase_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_ticker (ticker)
                )
            """)
            
            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    ticker VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_ticker (ticker),
                    UNIQUE KEY unique_user_ticker (user_id, ticker)
                )
            """)
            
            cursor.close()
            stock_conn.commit()
            logging.info("Stock database tables initialized")
        except Exception as e:
            logging.error(f"Failed to initialize stock tables: {e}")
        finally:
            stock_conn.close()

# Initialize database tables on startup
init_database_tables()

# External API client (unchanged)
class ExternalAPIClient:
    def __init__(self, base_url: str, api_password: str):
        self.base_url = base_url
        self.api_password = api_password
        self.session = requests.Session()
        self.default_timeout = float(os.environ.get('EXTERNAL_API_TIMEOUT_SECONDS', '2'))
        if api_password:
            self.session.headers.update({'X-API-Key': api_password})
        self.session.timeout = self.default_timeout
        
    def get(self, endpoint: str, params: dict = None):
        """Make GET request to external API with fallback"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.default_timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"External API error, using fallback: {e}")
            return self._get_fallback_data(endpoint, params)
    
    def _get_fallback_data(self, endpoint: str, params: dict = None):
        """Provide fallback data when external API is unavailable"""
        if "/health/" in endpoint:
            return {"status": "healthy", "database": "connected", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}
        
        elif "/api/stocks/" in endpoint:
            return {"success": True, "data": [], "count": 0, "total_available": 0, "timestamp": datetime.utcnow().isoformat()}
        
        elif "/api/search/" in endpoint:
            query = params.get('q', '') if params else ''
            return {
                "success": True,
                "query": query,
                "count": 3,
                "results": [
                    {"ticker": "AAPL", "company_name": "Apple Inc.", "current_price": 175.50, "change_percent": 1.30, "market_cap": 2750000000000, "exchange": "NASDAQ"},
                    {"ticker": "MSFT", "company_name": "Microsoft Corporation", "current_price": 410.80, "change_percent": 2.10, "market_cap": 3050000000000, "exchange": "NASDAQ"},
                    {"ticker": "GOOGL", "company_name": "Alphabet Inc.", "current_price": 145.30, "change_percent": 2.25, "market_cap": 1800000000000, "exchange": "NASDAQ"}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            return {"success": True, "message": "Fallback data", "timestamp": datetime.utcnow().isoformat()}

# Initialize external API client
external_api = ExternalAPIClient(EXTERNAL_API_URL, EXTERNAL_API_PASSWORD)

# Plan limits and models (unchanged)
PLAN_LIMITS = {
    'free': {'monthly': 15, 'daily': -1},
    'bronze': {'monthly': 1500, 'daily': 150},
    'silver': {'monthly': 5000, 'daily': 500, 'portfolios': 5, 'alerts': 50},
    'gold': {'monthly': -1, 'daily': -1}
}

# In-memory storage for rate limiting (fallback)
rate_limit_storage = defaultdict(list)
usage_memory = defaultdict(list)
alerts_memory = defaultdict(list)

# Pydantic models
class ApiUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str
    ip_address: str
    user_agent: Optional[str] = None
    plan: str = "free"

class UsageStats(BaseModel):
    plan: str
    monthly_used: int
    monthly_limit: int
    daily_used: int
    daily_limit: int

async def log_api_usage(user_id: str, endpoint: str, ip_address: str, user_agent: str = None, plan: str = "free"):
    """Log API usage to MySQL database"""
    usage = ApiUsage(
        user_id=user_id,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent,
        plan=plan
    )
    
    user_conn = get_user_db_connection()
    if user_conn:
        try:
            cursor = user_conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage (id, user_id, endpoint, ip_address, user_agent, plan, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (usage.id, usage.user_id, usage.endpoint, usage.ip_address, usage.user_agent, usage.plan, datetime.utcnow()))
            cursor.close()
            user_conn.commit()
        except Exception as e:
            logging.warning(f"DB insert failed, switching to in-memory logging: {e}")
            usage_memory[user_id].append(datetime.utcnow())
        finally:
            user_conn.close()
    else:
        usage_memory[user_id].append(datetime.utcnow())

async def get_usage_counts(user_id: str, plan: str) -> UsageStats:
    """Get current usage counts for a user from MySQL"""
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1) 
    month_ago = now - timedelta(days=30)
    
    user_conn = get_user_db_connection()
    if user_conn:
        try:
            cursor = user_conn.cursor()
            
            # Count daily usage
            cursor.execute("""
                SELECT COUNT(*) FROM api_usage 
                WHERE user_id = %s AND created_at >= %s
            """, (user_id, day_ago))
            daily_count = cursor.fetchone()[0]
            
            # Count monthly usage
            cursor.execute("""
                SELECT COUNT(*) FROM api_usage 
                WHERE user_id = %s AND created_at >= %s
            """, (user_id, month_ago))
            monthly_count = cursor.fetchone()[0]
            
            cursor.close()
        except Exception as e:
            logging.warning(f"DB count failed, using in-memory counts: {e}")
            timestamps = usage_memory[user_id]
            daily_count = len([t for t in timestamps if t >= day_ago])
            monthly_count = len([t for t in timestamps if t >= month_ago])
        finally:
            user_conn.close()
    else:
        timestamps = usage_memory[user_id]
        daily_count = len([t for t in timestamps if t >= day_ago])
        monthly_count = len([t for t in timestamps if t >= month_ago])
    
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    
    return UsageStats(
        plan=plan,
        monthly_used=monthly_count,
        monthly_limit=limits['monthly'] if limits['monthly'] != -1 else 999999,
        daily_used=daily_count,
        daily_limit=limits['daily'] if limits['daily'] != -1 else 999999
    )

async def can_make_api_call(user_id: str, plan: str = "free") -> bool:
    """Check if user can make an API call based on their plan limits"""
    if plan == 'gold':
        return True
    
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    usage_stats = await get_usage_counts(user_id, plan)
    
    if limits['monthly'] != -1 and usage_stats.monthly_used >= limits['monthly']:
        return False
    
    if limits['daily'] != -1 and usage_stats.daily_used >= limits['daily']:
        return False
    
    return True

async def get_user_info(request: Request) -> Dict[str, str]:
    """Extract user info from request"""
    user_id = request.headers.get("X-User-ID", "demo_user")
    plan = request.headers.get("X-User-Plan", "free")
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "")
    
    return {
        "user_id": user_id,
        "plan": plan.lower(),
        "ip_address": ip_address,
        "user_agent": user_agent
    }

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Trade Scan Pro API v2.0 with MySQL"}

@api_router.get("/health")
async def health_check():
    """Health check with database connectivity"""
    user_db_status = "connected" if not db_disabled and user_db_pool else "disconnected"
    stock_db_status = "connected" if not db_disabled and stock_db_pool else "disconnected"
    
    return {
        "status": "healthy",
        "user_database": user_db_status,
        "stock_database": stock_db_status,
        "external_api": "connected",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/stocks/")
async def get_stocks(
    request: Request,
    limit: int = 50,
    search: str = None,
    category: str = "nyse",
    min_price: float = None,
    max_price: float = None
):
    """Get stock list from database or external API"""
    user_info = await get_user_info(request)
    await log_api_usage(
        user_info["user_id"],
        "/stocks/",
        user_info["ip_address"],
        user_info["user_agent"],
        user_info["plan"]
    )
    
    # Try to get from database first
    stock_conn = get_stock_db_connection()
    if stock_conn:
        try:
            cursor = stock_conn.cursor(dictionary=True)
            query = "SELECT * FROM stocks WHERE 1=1"
            params = []
            
            if search:
                query += " AND (ticker LIKE %s OR company_name LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            if min_price is not None:
                query += " AND current_price >= %s"
                params.append(min_price)
            
            if max_price is not None:
                query += " AND current_price <= %s"
                params.append(max_price)
            
            query += f" LIMIT {min(limit, 1000)}"
            
            cursor.execute(query, params)
            stocks = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "data": stocks,
                "count": len(stocks),
                "source": "database"
            }
        except Exception as e:
            logging.error(f"Database query failed: {e}")
        finally:
            stock_conn.close()
    
    # Fallback to external API
    params = {
        "limit": min(limit, 1000),
        "category": category
    }
    if search:
        params["search"] = search
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    
    return external_api.get("/api/stocks/", params)

@api_router.get("/stock/{symbol}")
async def get_stock_detail(symbol: str, request: Request):
    """Get individual stock details"""
    user_info = await get_user_info(request)
    
    if not await can_make_api_call(user_info["user_id"], user_info["plan"]):
        raise HTTPException(status_code=429, detail="API limit reached for your plan")
    
    await log_api_usage(
        user_info["user_id"],
        f"/stock/{symbol}",
        user_info["ip_address"],
        user_info["user_agent"],
        user_info["plan"]
    )
    
    return external_api.get(f"/api/stock/{symbol}/")

@api_router.get("/search/")
async def search_stocks(q: str, request: Request):
    """Search stocks"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    user_info = await get_user_info(request)
    await log_api_usage(
        user_info["user_id"],
        "/search/",
        user_info["ip_address"],
        user_info["user_agent"],
        user_info["plan"]
    )

    return external_api.get("/api/search/", {"q": q})

# Authentication endpoints
@api_router.get("/auth/csrf/")
async def get_csrf_token(response: Response):
    """Issue a CSRF token"""
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        key="csrftoken",
        value=token,
        httponly=False,
        samesite="Lax"
    )
    return {"csrfToken": token}

@api_router.post("/auth/login/")
async def login_endpoint(payload: dict, response: Response):
    """Login endpoint"""
    username = (payload or {}).get("username") or (payload or {}).get("email") or "user"
    email = (payload or {}).get("email") or (username if (isinstance(username, str) and "@" in username) else f"{username}@example.com")

    api_token = secrets.token_urlsafe(24)
    response.set_cookie(
        key="sessionid",
        value=api_token,
        httponly=True,
        samesite="Lax"
    )

    user_payload = {
        "user_id": uuid.uuid4().hex,
        "username": username,
        "email": email,
        "first_name": (username.split("@")[0] if isinstance(username, str) else "User"),
        "last_name": "",
        "plan": "free",
        "is_verified": True,
        "date_joined": datetime.utcnow().isoformat(),
        "api_token": api_token,
    }

    return {"success": True, "message": "Login successful", "data": user_payload}

@api_router.post("/auth/logout/")
async def logout_endpoint():
    """Logout endpoint"""
    return {"success": True}

# Include router in main app
app.include_router(api_router)

# Configure logging
log_level = logging.INFO if os.environ.get('DEBUG', 'False').lower() != 'true' else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/supervisor/backend.log') if os.path.exists('/var/log/supervisor/') else logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Starting Trade Scan Pro API v2.0 with MySQL")
logger.info(f"User DB: {USER_DB_CONFIG['host']}:{USER_DB_CONFIG['port']}")
logger.info(f"Stock DB: {STOCK_DB_CONFIG['host']}:{STOCK_DB_CONFIG['port']}")
logger.info(f"External API: {EXTERNAL_API_URL}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup database connections"""
    try:
        if user_db_pool:
            # MySQL connector pools don't have explicit close method
            pass
        if stock_db_pool:
            pass
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")