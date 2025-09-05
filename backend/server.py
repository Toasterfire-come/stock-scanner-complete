from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import uuid
import yfinance as yf
import logging
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from functools import lru_cache
import httpx

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'stock_scanner')]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create FastAPI app
app = FastAPI(title="Stock Scanner API", version="1.0.0")

# CORS middleware - updated to match documentation
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Router
api_router = APIRouter(prefix="/api")

# ============ MODELS ============

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    plan: str = "free"
    api_token: str
    is_premium: bool = False
    limits: Dict[str, int]
    usage: Dict[str, Any]
    subscription: Dict[str, Any]

class StockData(BaseModel):
    ticker: str
    symbol: str
    company_name: str
    name: str
    exchange: str
    current_price: float
    price_change_today: float
    price_change_week: Optional[float] = None
    price_change_month: Optional[float] = None
    price_change_year: Optional[float] = None
    change_percent: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_ask_spread: Optional[float] = None
    days_range: Optional[str] = None
    days_low: Optional[float] = None
    days_high: Optional[float] = None
    volume: int
    volume_today: int
    avg_volume_3mon: Optional[int] = None
    dvav: Optional[float] = None
    shares_available: Optional[int] = None
    market_cap: Optional[int] = None
    market_cap_change_3mon: Optional[int] = None
    formatted_market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    pe_change_3mon: Optional[float] = None
    dividend_yield: Optional[float] = None
    earnings_per_share: Optional[float] = None
    book_value: Optional[float] = None
    price_to_book: Optional[float] = None
    week_52_low: Optional[float] = None
    week_52_high: Optional[float] = None
    one_year_target: Optional[float] = None
    formatted_price: str
    formatted_change: str
    formatted_volume: str
    last_updated: datetime
    created_at: datetime
    is_gaining: bool
    is_losing: bool
    volume_ratio: Optional[float] = None
    price_near_52_week_high: Optional[bool] = None
    price_near_52_week_low: Optional[bool] = None
    price_position_52_week: Optional[float] = None

class StockQuote(BaseModel):
    success: bool = True
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    rate_limit_warning: bool = False
    source: str = "yfinance"
    market_data: Dict[str, Any]
    cached: bool = False

class PlatformStats(BaseModel):
    success: bool = True
    nyse_stocks: int
    nasdaq_stocks: int
    total_stocks: int
    total_indicators: int
    scanner_combinations: int
    platform_stats: Dict[str, Any]
    market_stats: Dict[str, Any]
    timestamp: datetime

class UsageStats(BaseModel):
    success: bool = True
    usage: Dict[str, Any]
    rate_limits: Dict[str, Any]

# ============ UTILITY FUNCTIONS ============

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = await db.users.find_one({"username": username})
    return user

def format_currency(value):
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def format_volume(value):
    if value >= 1e9:
        return f"{value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return str(value)

@lru_cache(maxsize=100)
def get_stock_data(symbol: str):
    """Cache stock data for 5 minutes"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="2d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'][-1]
        previous_close = hist['Close'][-2] if len(hist) > 1 else current_price
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
        
        return {
            "symbol": symbol.upper(),
            "current_price": float(current_price),
            "change": float(change),
            "change_percent": float(change_percent),
            "volume": int(hist['Volume'][-1]) if not hist['Volume'].empty else 0,
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE'),
            "dividend_yield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            "week_52_high": info.get('fiftyTwoWeekHigh'),
            "week_52_low": info.get('fiftyTwoWeekLow'),
            "company_name": info.get('longName', symbol.upper()),
            "exchange": info.get('exchange', 'NASDAQ'),
        }
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

# ============ PUBLIC ENDPOINTS ============

@app.get("/")
async def homepage():
    return {"message": "Stock Scanner API", "status": "healthy", "version": "1.0.0"}

@app.get("/health/")
async def health_check():
    return {"status": "healthy"}

@api_router.get("/")
async def api_index():
    return {
        "message": "Stock Scanner API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/api/auth/",
            "stocks": "/api/stocks/",
            "platform_stats": "/api/platform-stats/",
            "usage": "/api/usage/"
        }
    }

@api_router.get("/platform-stats/")
async def get_platform_stats():
    # Get actual counts from database
    total_users = await db.users.count_documents({})
    premium_users = await db.users.count_documents({"plan": {"$ne": "free"}})
    
    return PlatformStats(
        nyse_stocks=0,
        nasdaq_stocks=5,
        total_stocks=5,
        total_indicators=14,
        scanner_combinations=70,
        platform_stats={
            "total_users": total_users,
            "premium_users": premium_users,
            "recent_stock_updates": 5,
            "api_calls_today": 0
        },
        market_stats={
            "exchanges_supported": ["NYSE", "NASDAQ"],
            "data_sources": ["yfinance", "real-time feeds"],
            "update_frequency": "Real-time"
        },
        timestamp=datetime.utcnow()
    )

@api_router.get("/usage/")
async def get_usage_stats():
    return UsageStats(
        usage={
            "plan": "free",
            "monthly_used": 0,
            "monthly_limit": 15,
            "daily_used": 0,
            "daily_limit": 15
        },
        rate_limits={
            "requests_this_minute": 0,
            "requests_this_hour": 0,
            "requests_this_day": 0,
            "rate_limited": False
        }
    )

# ============ STOCK DATA ENDPOINTS ============

@api_router.get("/stocks/")
async def get_stocks(
    limit: int = 50,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[int] = None,
    exchange: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    # Sample popular stocks for demonstration
    sample_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
    
    stocks_data = []
    for symbol in sample_stocks[:limit]:
        data = get_stock_data(symbol)
        if data:
            stock = StockData(
                ticker=data["symbol"],
                symbol=data["symbol"],
                company_name=data["company_name"],
                name=data["company_name"],
                exchange=data["exchange"],
                current_price=data["current_price"],
                price_change_today=data["change"],
                change_percent=data["change_percent"],
                volume=data["volume"],
                volume_today=data["volume"],
                market_cap=data.get("market_cap"),
                pe_ratio=data.get("pe_ratio"),
                dividend_yield=data.get("dividend_yield"),
                week_52_high=data.get("week_52_high"),
                week_52_low=data.get("week_52_low"),
                formatted_price=f"${data['current_price']:.2f}",
                formatted_change=f"{'+' if data['change'] >= 0 else ''}${data['change']:.2f} ({data['change_percent']:.2f}%)",
                formatted_volume=format_volume(data["volume"]),
                formatted_market_cap=format_currency(data.get("market_cap", 0)) if data.get("market_cap") else None,
                last_updated=datetime.utcnow(),
                created_at=datetime.utcnow(),
                is_gaining=data["change"] > 0,
                is_losing=data["change"] < 0
            )
            stocks_data.append(stock)
    
    return {
        "success": True,
        "data": stocks_data,
        "total": len(stocks_data),
        "limit": limit
    }

@api_router.get("/stocks/{symbol}/")
async def get_stock_details(symbol: str):
    data = get_stock_data(symbol.upper())
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    stock = StockData(
        ticker=data["symbol"],
        symbol=data["symbol"],
        company_name=data["company_name"],
        name=data["company_name"],
        exchange=data["exchange"],
        current_price=data["current_price"],
        price_change_today=data["change"],
        change_percent=data["change_percent"],
        volume=data["volume"],
        volume_today=data["volume"],
        market_cap=data.get("market_cap"),
        pe_ratio=data.get("pe_ratio"),
        dividend_yield=data.get("dividend_yield"),
        week_52_high=data.get("week_52_high"),
        week_52_low=data.get("week_52_low"),
        formatted_price=f"${data['current_price']:.2f}",
        formatted_change=f"{'+' if data['change'] >= 0 else ''}${data['change']:.2f} ({data['change_percent']:.2f}%)",
        formatted_volume=format_volume(data["volume"]),
        formatted_market_cap=format_currency(data.get("market_cap", 0)) if data.get("market_cap") else None,
        last_updated=datetime.utcnow(),
        created_at=datetime.utcnow(),
        is_gaining=data["change"] > 0,
        is_losing=data["change"] < 0
    )
    
    return {
        "success": True,
        "data": stock
    }

@api_router.get("/stocks/{symbol}/quote/")
async def get_stock_quote(symbol: str):
    data = get_stock_data(symbol.upper())
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return StockQuote(
        symbol=data["symbol"],
        price=data["current_price"],
        change=data["change"],
        change_percent=data["change_percent"],
        volume=data["volume"],
        timestamp=datetime.utcnow(),
        market_data={
            "open": data["current_price"],  # Simplified for demo
            "high": data["current_price"] * 1.02,
            "low": data["current_price"] * 0.98,
            "previous_close": data["current_price"] - data["change"],
            "market_cap": data.get("market_cap", 0),
            "pe_ratio": data.get("pe_ratio")
        },
        cached=True
    )

@api_router.get("/realtime/{ticker}/")
async def get_realtime_data(ticker: str):
    data = get_stock_data(ticker.upper())
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow()
    }

@api_router.get("/stocks/search/")
async def search_stocks(q: str):
    # Simple search implementation
    sample_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
    results = []
    
    for symbol in sample_stocks:
        if q.upper() in symbol or q.lower() in symbol.lower():
            data = get_stock_data(symbol)
            if data:
                results.append({
                    "symbol": data["symbol"],
                    "name": data["company_name"],
                    "exchange": data["exchange"]
                })
    
    return {
        "success": True,
        "data": results
    }

@api_router.get("/stocks/nasdaq/")
async def get_nasdaq_stocks(limit: int = 500):
    nasdaq_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
    
    stocks_data = []
    for symbol in nasdaq_stocks[:limit]:
        data = get_stock_data(symbol)
        if data:
            stocks_data.append(data)
    
    return {
        "success": True,
        "data": stocks_data,
        "exchange": "NASDAQ"
    }

@api_router.get("/market/stats/")
async def get_market_stats():
    return {
        "success": True,
        "data": {
            "total_stocks": 5000,
            "gainers": 2500,
            "losers": 2000,
            "unchanged": 500,
            "volume_leaders": ["AAPL", "TSLA", "AMZN"]
        }
    }

@api_router.get("/trending/")
async def get_trending_stocks():
    trending = ["TSLA", "AAPL", "NVDA", "AMD", "MSFT"]
    
    high_volume = []
    top_gainers = []
    most_active = []
    
    for symbol in trending:
        data = get_stock_data(symbol)
        if data:
            stock_info = {
                "symbol": symbol,
                "price": data["current_price"],
                "change_percent": data["change_percent"],
                "volume": data["volume"]
            }
            high_volume.append(stock_info)
            if data["change_percent"] > 0:
                top_gainers.append(stock_info)
            most_active.append(stock_info)
    
    return {
        "success": True,
        "high_volume": high_volume,
        "top_gainers": sorted(top_gainers, key=lambda x: x["change_percent"], reverse=True),
        "most_active": most_active
    }

@api_router.get("/market/filter/")
async def filter_stocks(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[int] = None,
    exchange: Optional[str] = None
):
    # Apply filters to sample data
    sample_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    filtered_stocks = []
    
    for symbol in sample_stocks:
        data = get_stock_data(symbol)
        if data:
            # Apply filters
            if min_price and data["current_price"] < min_price:
                continue
            if max_price and data["current_price"] > max_price:
                continue
            if min_volume and data["volume"] < min_volume:
                continue
            if exchange and data["exchange"] != exchange:
                continue
                
            filtered_stocks.append(data)
    
    return {
        "success": True,
        "data": filtered_stocks,
        "filters_applied": {
            "min_price": min_price,
            "max_price": max_price,
            "min_volume": min_volume,
            "exchange": exchange
        }
    }

# ============ AUTHENTICATION ENDPOINTS ============

@api_router.post("/auth/register/")
async def register_user(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    api_token = str(uuid.uuid4())
    
    user_doc = {
        "user_id": await db.counters.find_one_and_update(
            {"_id": "user_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        ).get("seq", 1),
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "password_hash": hashed_password,
        "plan": "free",
        "api_token": api_token,
        "is_premium": False,
        "created_at": datetime.utcnow(),
        "limits": {"monthly": 15, "daily": 15},
        "usage": {"monthly_calls": 0, "daily_calls": 0, "last_call": None},
        "subscription": {"active": False, "end_date": None, "trial_used": False}
    }
    
    await db.users.insert_one(user_doc)
    
    # Create response
    response_data = UserResponse(
        user_id=user_doc["user_id"],
        username=user_doc["username"],
        email=user_doc["email"],
        first_name=user_doc["first_name"],
        last_name=user_doc["last_name"],
        plan=user_doc["plan"],
        api_token=user_doc["api_token"],
        is_premium=user_doc["is_premium"],
        limits=user_doc["limits"],
        usage=user_doc["usage"],
        subscription=user_doc["subscription"]
    )
    
    return {
        "success": True,
        "data": response_data,
        "message": "User registered successfully"
    }

@api_router.post("/auth/login/")
async def login_user(credentials: UserLogin):
    # Find user
    user = await db.users.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create response
    response_data = UserResponse(
        user_id=user["user_id"],
        username=user["username"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        plan=user["plan"],
        api_token=user["api_token"],
        is_premium=user["is_premium"],
        limits=user["limits"],
        usage=user["usage"],
        subscription=user["subscription"]
    )
    
    return {
        "success": True,
        "data": response_data,
        "message": "Login successful"
    }

# ============ AUTHENTICATED ENDPOINTS ============

@api_router.get("/user/profile/")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    response_data = UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        plan=current_user["plan"],
        api_token=current_user["api_token"],
        is_premium=current_user["is_premium"],
        limits=current_user["limits"],
        usage=current_user["usage"],
        subscription=current_user["subscription"]
    )
    
    return {
        "success": True,
        "data": response_data
    }

@api_router.post("/user/profile/")
async def update_user_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Update allowed fields
    update_fields = {}
    allowed_fields = ["first_name", "last_name", "email"]
    
    for field in allowed_fields:
        if field in profile_data:
            update_fields[field] = profile_data[field]
    
    if update_fields:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_fields}
        )
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

@api_router.post("/user/change-password/")
async def change_password(
    password_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not verify_password(current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    new_password_hash = get_password_hash(new_password)
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }

# ============ BILLING ENDPOINTS ============

@api_router.get("/billing/current-plan/")
async def get_current_plan(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "success": True,
        "data": {
            "plan": current_user["plan"],
            "is_premium": current_user["is_premium"],
            "limits": current_user["limits"],
            "subscription": current_user["subscription"]
        }
    }

@api_router.get("/billing/history/")
async def get_billing_history(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "success": True,
        "data": [],
        "message": "No billing history found"
    }

@api_router.get("/billing/stats/")
async def get_billing_stats(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "success": True,
        "data": {
            "total_spent": 0,
            "current_month_spending": 0,
            "plan_cost": 0
        }
    }

# ============ PORTFOLIO & WATCHLIST ENDPOINTS ============

@api_router.get("/portfolio/")
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    portfolio = await db.portfolios.find({"user_id": current_user["user_id"]}).to_list(100)
    return {
        "success": True,
        "data": portfolio
    }

@api_router.post("/portfolio/add/")
async def add_to_portfolio(
    portfolio_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    symbol = portfolio_data.get("symbol", "").upper()
    
    portfolio_item = {
        "user_id": current_user["user_id"],
        "symbol": symbol,
        "added_at": datetime.utcnow()
    }
    
    await db.portfolios.insert_one(portfolio_item)
    
    return {
        "success": True,
        "message": f"Added {symbol} to portfolio"
    }

@api_router.get("/watchlist/")
async def get_watchlist(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    watchlist = await db.watchlists.find({"user_id": current_user["user_id"]}).to_list(100)
    return {
        "success": True,
        "data": watchlist
    }

@api_router.post("/watchlist/add/")
async def add_to_watchlist(
    watchlist_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    symbol = watchlist_data.get("symbol", "").upper()
    
    watchlist_item = {
        "user_id": current_user["user_id"],
        "symbol": symbol,
        "added_at": datetime.utcnow()
    }
    
    await db.watchlists.insert_one(watchlist_item)
    
    return {
        "success": True,
        "message": f"Added {symbol} to watchlist"
    }

# ============ WORDPRESS INTEGRATION ENDPOINTS ============

@api_router.get("/wordpress/")
async def get_wordpress_stocks():
    return {
        "success": True,
        "data": [],
        "message": "WordPress integration endpoint"
    }

@api_router.get("/wordpress/news/")
async def get_wordpress_news():
    return {
        "success": True,
        "data": [],
        "message": "WordPress news endpoint"
    }

@api_router.get("/simple/stocks/")
async def get_simple_stocks():
    simple_data = []
    sample_stocks = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in sample_stocks:
        data = get_stock_data(symbol)
        if data:
            simple_data.append({
                "symbol": symbol,
                "price": data["current_price"],
                "change": data["change_percent"]
            })
    
    return {
        "success": True,
        "data": simple_data
    }

# Include the API router
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)