from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import time


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Plan limits based on PHP configuration
PLAN_LIMITS = {
    'free': {'monthly': 15, 'daily': 5, 'hourly': 2},
    'bronze': {'monthly': 1500, 'daily': 50, 'hourly': 10},
    'silver': {'monthly': 5000, 'daily': 200, 'hourly': 25},
    'gold': {'monthly': -1, 'daily': -1, 'hourly': -1}  # -1 means unlimited
}

# Rate limiting thresholds (advisory)
RATE_LIMITS = {
    'requests_per_minute': 10,
    'requests_per_hour': 300,
    'requests_per_day': 1000
}

# In-memory storage for rate limiting (in production, use Redis)
rate_limit_storage = defaultdict(list)
usage_cache = defaultdict(lambda: defaultdict(int))


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ApiUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    user_agent: Optional[str] = None
    plan: str = "free"

class UsageStats(BaseModel):
    plan: str
    monthly_used: int
    monthly_limit: int
    daily_used: int
    daily_limit: int
    hourly_used: int
    hourly_limit: int

class RateLimitInfo(BaseModel):
    requests_this_minute: int
    requests_this_hour: int
    requests_this_day: int
    rate_limited: bool
    advisory_only: bool = True


async def log_api_usage(user_id: str, endpoint: str, ip_address: str, user_agent: str = None, plan: str = "free"):
    """Log API usage to database"""
    usage = ApiUsage(
        user_id=user_id,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent,
        plan=plan
    )
    await db.api_usage.insert_one(usage.dict())

async def get_usage_counts(user_id: str, plan: str) -> UsageStats:
    """Get current usage counts for a user"""
    now = datetime.utcnow()
    
    # Calculate time boundaries
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)
    month_ago = now - timedelta(days=30)
    
    # Count usage in different time periods
    hourly_count = await db.api_usage.count_documents({
        "user_id": user_id,
        "timestamp": {"$gte": hour_ago}
    })
    
    daily_count = await db.api_usage.count_documents({
        "user_id": user_id,
        "timestamp": {"$gte": day_ago}
    })
    
    monthly_count = await db.api_usage.count_documents({
        "user_id": user_id,
        "timestamp": {"$gte": month_ago}
    })
    
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    
    return UsageStats(
        plan=plan,
        monthly_used=monthly_count,
        monthly_limit=limits['monthly'] if limits['monthly'] != -1 else 999999,
        daily_used=daily_count,
        daily_limit=limits['daily'] if limits['daily'] != -1 else 999999,
        hourly_used=hourly_count,
        hourly_limit=limits['hourly'] if limits['hourly'] != -1 else 999999
    )

async def can_make_api_call(user_id: str, plan: str = "free") -> bool:
    """Check if user can make an API call based on their plan limits"""
    if plan == 'gold':
        return True  # Unlimited for gold plan
    
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    usage_stats = await get_usage_counts(user_id, plan)
    
    # Check monthly limit
    if limits['monthly'] != -1 and usage_stats.monthly_used >= limits['monthly']:
        return False
    
    # Check daily limit
    if limits['daily'] != -1 and usage_stats.daily_used >= limits['daily']:
        return False
    
    # Check hourly limit
    if limits['hourly'] != -1 and usage_stats.hourly_used >= limits['hourly']:
        return False
    
    return True

def calculate_request_rates(ip_address: str) -> Dict[str, int]:
    """Calculate request rates for IP address"""
    now = time.time()
    requests = rate_limit_storage[ip_address]
    
    # Clean old requests
    minute_ago = now - 60
    hour_ago = now - 3600
    day_ago = now - 86400
    
    # Filter requests within time windows
    requests_minute = len([r for r in requests if r > minute_ago])
    requests_hour = len([r for r in requests if r > hour_ago])
    requests_day = len([r for r in requests if r > day_ago])
    
    return {
        'minute': requests_minute,
        'hour': requests_hour,
        'day': requests_day
    }

async def check_rate_limits(ip_address: str) -> RateLimitInfo:
    """Check rate limits for IP address (advisory only)"""
    now = time.time()
    
    # Add current request timestamp
    rate_limit_storage[ip_address].append(now)
    
    # Clean old timestamps (keep only last day)
    rate_limit_storage[ip_address] = [
        r for r in rate_limit_storage[ip_address] 
        if r > now - 86400
    ]
    
    rates = calculate_request_rates(ip_address)
    
    # Check if any limits exceeded (advisory only)
    rate_limited = (
        rates['minute'] > RATE_LIMITS['requests_per_minute'] or
        rates['hour'] > RATE_LIMITS['requests_per_hour'] or
        rates['day'] > RATE_LIMITS['requests_per_day']
    )
    
    if rate_limited:
        logging.warning(f"Rate limits exceeded (advisory) for IP {ip_address}: {rates['minute']}/min, {rates['hour']}/hr, {rates['day']}/day")
    
    return RateLimitInfo(
        requests_this_minute=rates['minute'],
        requests_this_hour=rates['hour'],
        requests_this_day=rates['day'],
        rate_limited=rate_limited,
        advisory_only=True
    )

async def get_user_info(request: Request) -> Dict[str, str]:
    """Extract user info from request (simplified for demo)"""
    # In production, this would extract from JWT token or session
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

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Trade Scan Pro API v1.0"}

@api_router.get("/usage")
async def get_user_usage(request: Request):
    """Get current usage statistics for the user"""
    user_info = await get_user_info(request)
    
    usage_stats = await get_usage_counts(user_info["user_id"], user_info["plan"])
    rate_info = await check_rate_limits(user_info["ip_address"])
    
    return {
        "usage": usage_stats.dict(),
        "rate_limits": rate_info.dict()
    }

@api_router.get("/stocks/{symbol}/quote")
async def get_stock_quote(symbol: str, request: Request):
    """Get stock quote - with usage tracking and limits"""
    user_info = await get_user_info(request)
    
    # Check if user can make API call
    if not await can_make_api_call(user_info["user_id"], user_info["plan"]):
        raise HTTPException(status_code=429, detail="API limit reached for your plan")
    
    # Check rate limits (advisory)
    rate_info = await check_rate_limits(user_info["ip_address"])
    
    # Log the API usage
    await log_api_usage(
        user_info["user_id"],
        f"/stocks/{symbol}/quote",
        user_info["ip_address"],
        user_info["user_agent"],
        user_info["plan"]
    )
    
    # Mock stock data (in production, fetch from real API)
    mock_data = {
        "symbol": symbol.upper(),
        "price": 150.25,
        "change": 2.35,
        "change_percent": 1.59,
        "volume": 1234567,
        "timestamp": datetime.utcnow().isoformat(),
        "rate_limit_warning": rate_info.rate_limited
    }
    
    return mock_data

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
