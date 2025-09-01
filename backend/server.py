from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from .schemas import (
    APIMessage,
    HealthResponse,
    Stock,
    StocksListResponse,
    StockDetailResponse,
    SearchResponse,
    SearchResult,
    AlertsCreateMeta,
    AlertCreateRequest,
    AlertCreateResponse,
    SubscriptionRequest,
    SubscriptionResponse,
    LoginRequest,
    LoginResponse,
    UserProfile,
    ProfileUpdateRequest,
    PasswordChangeRequest,
    BillingHistoryItem,
    BillingHistoryResponse,
    CurrentPlanResponse,
    ChangePlanRequest,
    NotificationSettings,
    NotificationItem,
    NotificationHistoryResponse,
    MarkReadRequest,
    WatchlistItem,
    WatchlistAddRequest,
    PortfolioItem,
    PortfolioAddRequest,
    NewsFeedResponse,
    NewsPrefRequest,
    RevenueValidateRequest,
    RevenueValidateResponse,
    RevenueApplyRequest,
    RevenueApplyResponse,
    RevenueRecordRequest,
    RevenueRecordResponse,
)
from .auth import create_access_token, decode_token, hash_password, verify_password
from .utils import now_iso, get_next_sequence, paginate, normalize_ticker, str_uuid, make_month_year, to_float

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise RuntimeError("MONGO_URL not configured")
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'retail_scanner')]

# Create the main app without a prefix
app = FastAPI(title="Retail Trade Scanner API", version="0.1.0")

# Create a router with the /api prefix
api = APIRouter(prefix="/api")
revenue = APIRouter(prefix="/api/revenue")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------------------
# Helpers & Dependencies
# ----------------------
async def get_user_from_token(authorization: Optional[str] = None) -> Dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    payload = decode_token(parts[1])
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await db.users.find_one({"id": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# -------------
# Data seeding
# -------------
async def seed_data():
    # Create indexes
    await db.stocks.create_index("ticker", unique=True)
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)

    # Seed a demo user if none
    user_count = await db.users.count_documents({})
    if user_count == 0:
        demo = {
            "id": str_uuid(),
            "username": "demo",
            "email": "demo@example.com",
            "password_hash": hash_password("password123"),
            "first_name": "Demo",
            "last_name": "User",
            "phone": "",
            "company": "",
            "is_premium": False,
            "plan": {"plan_type": "free", "billing_cycle": "monthly", "features": {"api_calls_limit": 1000}},
            "last_login": None,
            "date_joined": now_iso(),
        }
        await db.users.insert_one(demo)

    # Seed stocks if empty
    stock_count = await db.stocks.count_documents({})
    if stock_count == 0:
        now = now_iso()
        sample = [
            {
                "ticker": "AAPL", "symbol": "AAPL", "company_name": "Apple Inc.", "exchange": "NASDAQ",
                "current_price": 210.5, "price_change_today": 2.1, "change_percent": 1.01, "volume": 80234123,
                "market_cap": 3300000000000, "last_updated": now, "currency": "USD",
                "price_history": [{"price": 209.0, "timestamp": now}, {"price": 210.5, "timestamp": now}],
                "pe_ratio": 28.5, "dividend_yield": 0.5,
            },
            {
                "ticker": "MSFT", "symbol": "MSFT", "company_name": "Microsoft Corporation", "exchange": "NASDAQ",
                "current_price": 440.3, "price_change_today": -1.2, "change_percent": -0.27, "volume": 42100123,
                "market_cap": 3300000000000, "last_updated": now, "currency": "USD",
                "price_history": [{"price": 441.5, "timestamp": now}, {"price": 440.3, "timestamp": now}],
                "pe_ratio": 35.4, "dividend_yield": 0.7,
            },
            {
                "ticker": "NVDA", "symbol": "NVDA", "company_name": "NVIDIA Corporation", "exchange": "NASDAQ",
                "current_price": 128.2, "price_change_today": 5.6, "change_percent": 4.57, "volume": 120334455,
                "market_cap": 3100000000000, "last_updated": now, "currency": "USD",
                "price_history": [{"price": 122.6, "timestamp": now}, {"price": 128.2, "timestamp": now}],
                "pe_ratio": 52.6, "dividend_yield": 0.04,
            }
        ]
        await db.stocks.insert_many(sample)


@app.on_event("startup")
async def on_startup():
    await seed_data()


# ----------------
# Health & Root
# ----------------
@api.get("/")
async def root():
    return {"status": "ok", "message": "Retail Trade Scanner API"}


@api.get("/health/", response_model=HealthResponse)
async def health():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version="0.1.0",
        timestamp=now_iso(),
        endpoints={
            "stocks": "/api/stocks/",
            "health": "/api/health/",
            "revenue": "/api/revenue/revenue-analytics/",
            "docs": "/docs",
            "trending": "/api/trending/",
            "search": "/api/search/",
        },
        features={"wordpress_integration": False, "real_time_data": False, "alerts": True, "analytics": True},
    )


# --------------
# Stocks & Search
# --------------
@api.get("/stocks/", response_model=StocksListResponse)
async def get_stocks(
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[int] = None,
    min_market_cap: Optional[int] = None,
    max_market_cap: Optional[int] = None,
    min_pe: Optional[float] = None,
    max_pe: Optional[float] = None,
    exchange: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
):
    q: Dict[str, Any] = {}
    if search:
        regex = {"$regex": search, "$options": "i"}
        q["$or"] = [{"ticker": regex}, {"company_name": regex}]
    if min_price is not None:
        q["current_price"] = q.get("current_price", {})
        q["current_price"].update({"$gte": float(min_price)})
    if max_price is not None:
        q["current_price"] = q.get("current_price", {})
        q["current_price"].update({"$lte": float(max_price)})
    if min_volume is not None:
        q["volume"] = {"$gte": int(min_volume)}
    if min_market_cap is not None:
        q["market_cap"] = q.get("market_cap", {})
        q["market_cap"].update({"$gte": int(min_market_cap)})
    if max_market_cap is not None:
        q["market_cap"] = q.get("market_cap", {})
        q["market_cap"].update({"$lte": int(max_market_cap)})
    if min_pe is not None:
        q["pe_ratio"] = q.get("pe_ratio", {})
        q["pe_ratio"].update({"$gte": float(min_pe)})
    if max_pe is not None:
        q["pe_ratio"] = q.get("pe_ratio", {})
        q["pe_ratio"].update({"$lte": float(max_pe)})
    if exchange and exchange.lower() != "all":
        q["exchange"] = exchange

    sort = None
    if sort_by:
        direction = -1 if (sort_order or "desc").lower() == "desc" else 1
        sort = [(sort_by, direction)]

    cursor = db.stocks.find(q)
    if sort:
        cursor = cursor.sort(sort)
    docs = await cursor.limit(limit).to_list(length=limit)

    data: List[Stock] = [Stock(**{**d, "_id": None}) for d in docs]
    return StocksListResponse(success=True, data=data, count=len(data), total_available=len(data), filters_applied={"query": q}, timestamp=now_iso())


@api.get("/stock/{ticker}/", response_model=StockDetailResponse)
@api.get("/stocks/{ticker}/", response_model=StockDetailResponse)
async def get_stock_detail(ticker: str):
    ticker = normalize_ticker(ticker)
    doc = await db.stocks.find_one({"ticker": ticker})
    if not doc:
        return StockDetailResponse(success=False, data=None, timestamp=now_iso(), error="Not found")
    return StockDetailResponse(success=True, data=Stock(**{**doc, "_id": None}), timestamp=now_iso())


@api.get("/search/", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1)):
    regex = {"$regex": q, "$options": "i"}
    docs = await db.stocks.find({"$or": [{"ticker": regex}, {"company_name": regex}]}).limit(20).to_list(20)
    results: List[SearchResult] = [
        SearchResult(
            ticker=d["ticker"],
            company_name=d.get("company_name", d["ticker"]),
            current_price=d.get("current_price"),
            change_percent=d.get("change_percent"),
            market_cap=d.get("market_cap"),
            exchange=d.get("exchange"),
            match_type=("ticker" if d["ticker"].lower() == q.lower() else "company"),
            url=f"/app/stocks/{d['ticker']}"
        )
        for d in docs
    ]
    return SearchResponse(success=True, query=q, count=len(results), results=results, timestamp=now_iso())


@api.get("/trending/")
async def trending():
    # high_volume: sort by volume desc
    hv_docs = await db.stocks.find({}).sort([("volume", -1)]).limit(5).to_list(5)
    gainers_docs = await db.stocks.find({}).sort([("change_percent", -1)]).limit(5).to_list(5)
    most_active_docs = await db.stocks.find({}).sort([("price_change_today", -1)]).limit(5).to_list(5)

    def map_item(d):
        return {
            "ticker": d.get("ticker"),
            "name": d.get("company_name", d.get("ticker")),
            "current_price": d.get("current_price"),
            "price_change_today": d.get("price_change_today", 0.0),
            "change_percent": d.get("change_percent", 0.0),
            "volume": d.get("volume", 0),
            "market_cap": d.get("market_cap", 0),
        }

    return {
        "high_volume": [map_item(d) for d in hv_docs],
        "top_gainers": [map_item(d) for d in gainers_docs],
        "most_active": [map_item(d) for d in most_active_docs],
        "last_updated": now_iso()
    }


@api.get("/market-stats/")
async def market_stats():
    total = await db.stocks.count_documents({})
    gainers = await db.stocks.count_documents({"change_percent": {"$gt": 0}})
    losers = await db.stocks.count_documents({"change_percent": {"$lt": 0}})
    unchanged = total - gainers - losers
    top_gainers = await db.stocks.find({}).sort([("change_percent", -1)]).limit(3).to_list(3)
    top_losers = await db.stocks.find({}).sort([("change_percent", 1)]).limit(3).to_list(3)
    most_active = await db.stocks.find({}).sort([("volume", -1)]).limit(3).to_list(3)

    def tg_map(d):
        return {"ticker": d["ticker"], "name": d.get("company_name", d["ticker"]), "current_price": d.get("current_price"), "price_change_today": d.get("price_change_today", 0.0), "change_percent": d.get("change_percent", 0.0)}

    def ma_map(d):
        return {"ticker": d["ticker"], "name": d.get("company_name", d["ticker"]), "current_price": d.get("current_price"), "volume": d.get("volume", 0)}

    return {
        "market_overview": {"total_stocks": total, "nyse_stocks": 0, "gainers": gainers, "losers": losers, "unchanged": unchanged},
        "top_gainers": [tg_map(d) for d in top_gainers],
        "top_losers": [tg_map(d) for d in top_losers],
        "most_active": [ma_map(d) for d in most_active],
        "last_updated": now_iso()
    }


# ------
# Alerts
# ------
@api.get("/alerts/create/", response_model=AlertsCreateMeta)
async def alerts_meta():
    return AlertsCreateMeta(
        endpoint="/api/alerts/create/",
        method="POST",
        description="Create a price alert for a stock.",
        required_fields={"ticker": "string", "target_price": "number", "alert_type": "above|below", "email": "string (optional)"},
        example_request={"ticker": "AAPL", "target_price": 200.0, "condition": "above", "email": "you@example.com"},
        usage="POST the JSON to endpoint to create the alert"
    )


@api.post("/alerts/create/", response_model=AlertCreateResponse)
async def create_alert(payload: AlertCreateRequest):
    alert_id = await get_next_sequence(db, "alert_id")
    doc = {
        "id": alert_id,
        "ticker": normalize_ticker(payload.ticker),
        "target_value": float(payload.target_price),
        "alert_type": payload.condition,
        "email": payload.email,
        "created_at": now_iso(),
        "is_active": True,
        "is_triggered": False,
    }
    await db.alerts.insert_one(doc)
    return AlertCreateResponse(alert_id=alert_id, message="Alert created", details={"ticker": doc["ticker"], "target_value": doc["target_value"], "alert_type": doc["alert_type"], "created_at": doc["created_at"]})


# --------------
# Subscriptions
# --------------
@api.post("/subscription/", response_model=SubscriptionResponse)
@api.post("/wordpress/subscribe/", response_model=SubscriptionResponse)
async def subscribe(payload: SubscriptionRequest):
    doc = {"email": payload.email, "category": payload.category, "is_active": True, "created_at": now_iso()}
    await db.subscriptions.insert_one(doc)
    return SubscriptionResponse(success=True, message="Subscribed", data={"email": payload.email, "category": payload.category, "is_active": True})


# ----
# Auth
# ----
@api.post("/auth/login/", response_model=LoginResponse)
async def login(payload: LoginRequest):
    user = await db.users.find_one({"$or": [{"username": payload.username}, {"email": payload.username}]})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user["id"]})
    await db.users.update_one({"id": user["id"]}, {"$set": {"last_login": now_iso()}})
    profile = UserProfile(user_id=user["id"], username=user["username"], email=user["email"], first_name=user.get("first_name", ""), last_name=user.get("last_name", ""), phone=user.get("phone", ""), company=user.get("company", ""), date_joined=user.get("date_joined", now_iso()), last_login=user.get("last_login"), is_premium=user.get("is_premium", False))
    return LoginResponse(success=True, data=profile, message="Logged in", token=token)


@api.post("/auth/logout/")
async def logout():
    return {"success": True, "message": "Logged out"}


@api.get("/user/profile/", response_model=Dict[str, Any])
async def get_profile(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    profile = {
        "success": True,
        "data": {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "phone": user.get("phone", ""),
            "company": user.get("company", ""),
            "date_joined": user.get("date_joined", now_iso()),
            "last_login": user.get("last_login"),
            "is_premium": user.get("is_premium", False),
        },
    }
    return profile


@api.post("/user/profile/")
async def update_profile(payload: ProfileUpdateRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        return {"success": True, "message": "No changes", "data": {"user_id": user["id"], "username": user["username"], "email": user["email"]}}
    await db.users.update_one({"id": user["id"]}, {"$set": update})
    user.update(update)
    return {"success": True, "message": "Profile updated", "data": {"user_id": user["id"], "username": user["username"], "email": user["email"], "first_name": user.get("first_name", ""), "last_name": user.get("last_name", ""), "phone": user.get("phone", ""), "company": user.get("company", "")}}


@api.post("/user/change-password/")
async def change_password(payload: PasswordChangeRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if not verify_password(payload.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Current password invalid")
    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": hash_password(payload.new_password)}})
    return {"success": True, "message": "Password changed"}


# -------
# Billing
# -------
@api.get("/user/billing-history/", response_model=BillingHistoryResponse)
@api.get("/billing/history/", response_model=BillingHistoryResponse)
async def billing_history(page: int = 1, limit: int = 10, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    docs = await db.billing_history.find({"user_id": user["id"]}).sort([("date", -1)]).to_list(1000)
    data = [BillingHistoryItem(**d) for d in docs]
    page_items, pagination = paginate([i.model_dump() for i in data], page, limit)
    return BillingHistoryResponse(success=True, data=[BillingHistoryItem(**i) for i in page_items], pagination=pagination)


@api.get("/billing/current-plan/", response_model=CurrentPlanResponse)
async def current_plan(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    plan = user.get("plan", {"plan_type": "free", "plan_name": "Free", "is_premium": user.get("is_premium", False), "billing_cycle": "monthly", "features": {"scanners": 3}})
    return CurrentPlanResponse(success=True, data=plan)


@api.post("/billing/change-plan/")
async def change_plan(payload: ChangePlanRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    is_premium = payload.plan_type in ["basic", "pro", "enterprise"]
    await db.users.update_one({"id": user["id"]}, {"$set": {"plan": payload.model_dump(), "is_premium": is_premium}})
    return {"success": True, "message": "Plan updated", "data": {"plan_type": payload.plan_type, "billing_cycle": payload.billing_cycle, "is_premium": is_premium, "api_calls_limit": 10000 if is_premium else 1000}}


@api.get("/billing/stats/")
async def billing_stats(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    docs = await db.billing_history.find({"user_id": user["id"]}).to_list(1000)
    total_spent = sum([to_float(d.get("amount", 0.0)) for d in docs])
    return {"success": True, "data": {"total_spent": total_spent, "recent_payments": min(5, len(docs)), "account_status": "active", "next_billing_date": now_iso()}}


# --------------
# Notifications
# --------------
@api.get("/user/notification-settings/")
@api.get("/notifications/settings/")
async def get_notification_settings(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    doc = await db.notifications_settings.find_one({"user_id": user["id"]})
    default = {
        "trading": {"price_alerts": True, "volume_alerts": False, "market_hours": True},
        "portfolio": {"daily_summary": True, "weekly_report": True, "milestone_alerts": True},
        "news": {"breaking_news": True, "earnings_alerts": True, "analyst_ratings": False},
        "security": {"login_alerts": True, "billing_updates": True, "plan_updates": True},
    }
    return {"success": True, "data": doc.get("settings", default) if doc else default}


@api.post("/user/notification-settings/")
@api.post("/notifications/settings/")
async def update_notification_settings(payload: NotificationSettings, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    await db.notifications_settings.update_one({"user_id": user["id"]}, {"$set": {"settings": payload.model_dump()}}, upsert=True)
    return {"success": True, "message": "Settings updated"}


@api.get("/notifications/history/", response_model=NotificationHistoryResponse)
async def notifications_history(page: int = 1, limit: int = 20, type: Optional[str] = None, is_read: Optional[bool] = None, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    q: Dict[str, Any] = {"user_id": user["id"]}
    if type:
        q["type"] = type
    if is_read is not None:
        q["is_read"] = bool(is_read)
    docs = await db.notifications.find(q).sort([("created_at", -1)]).to_list(1000)
    items = [NotificationItem(**d).model_dump() for d in docs]
    page_items, pagination = paginate(items, page, limit)
    unread = await db.notifications.count_documents({"user_id": user["id"], "is_read": False})
    return NotificationHistoryResponse(success=True, data=[NotificationItem(**i) for i in page_items], pagination=pagination, summary={"total_unread": unread})


@api.post("/notifications/mark-read/")
async def mark_read(payload: MarkReadRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    if payload.mark_all:
        res = await db.notifications.update_many({"user_id": user["id"], "is_read": False}, {"$set": {"is_read": True, "read_at": now_iso()}})
        updated = res.modified_count
    else:
        ids = payload.notification_ids or []
        updated = 0
        for nid in ids:
            r = await db.notifications.update_one({"user_id": user["id"], "id": nid}, {"$set": {"is_read": True, "read_at": now_iso()}})
            updated += r.modified_count
    remaining_unread = await db.notifications.count_documents({"user_id": user["id"], "is_read": False})
    return {"success": True, "message": "Updated", "data": {"updated_count": updated, "remaining_unread": remaining_unread}}


# ----------
# Watchlists
# ----------
@api.get("/watchlist/")
async def get_watchlist(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    docs = await db.watchlist.find({"user_id": user["id"]}).to_list(1000)
    return {"success": True, "data": docs, "summary": {"total_items": len(docs), "gainers": 0, "losers": 0, "unchanged": len(docs)}}


@api.post("/watchlist/add/")
async def add_watchlist(payload: WatchlistAddRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    symbol = normalize_ticker(payload.symbol)
    stock = await db.stocks.find_one({"ticker": symbol})
    doc = {
        "id": str_uuid(),
        "user_id": user["id"],
        "symbol": symbol,
        "company_name": stock.get("company_name", symbol) if stock else symbol,
        "current_price": stock.get("current_price", 0.0) if stock else 0.0,
        "price_change": stock.get("price_change_today", 0.0) if stock else 0.0,
        "price_change_percent": stock.get("change_percent", 0.0) if stock else 0.0,
        "volume": stock.get("volume", 0) if stock else 0,
        "market_cap": stock.get("market_cap", 0) if stock else 0,
        "watchlist_name": payload.watchlist_name or "My Watchlist",
        "notes": payload.notes or "",
        "alert_price": payload.alert_price,
        "added_date": now_iso(),
    }
    await db.watchlist.insert_one(doc)
    return {"success": True, "message": "Added", "data": doc}


@api.delete("/watchlist/{item_id}/")
async def delete_watchlist(item_id: str, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    res = await db.watchlist.delete_one({"user_id": user["id"], "id": item_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "message": "Deleted", "data": {"id": item_id}}


# ----------
# Portfolio
# ----------
@api.get("/portfolio/")
async def get_portfolio(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    docs = await db.portfolio.find({"user_id": user["id"]}).to_list(1000)
    total_value = sum([d.get("total_value", 0.0) for d in docs])
    total_gain_loss = sum([d.get("gain_loss", 0.0) for d in docs])
    summary = {
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_percent": (total_gain_loss / total_value * 100.0) if total_value else 0.0,
        "total_holdings": len(docs),
    }
    return {"success": True, "data": docs, "summary": summary}


@api.post("/portfolio/add/")
async def add_portfolio(payload: PortfolioAddRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    stock = await db.stocks.find_one({"ticker": normalize_ticker(payload.symbol)})
    current_price = stock.get("current_price", payload.avg_cost) if stock else payload.avg_cost
    total_value = current_price * float(payload.shares)
    cost = float(payload.avg_cost) * float(payload.shares)
    gain_loss = total_value - cost
    doc = {
        "id": str_uuid(),
        "user_id": user["id"],
        "symbol": normalize_ticker(payload.symbol),
        "shares": float(payload.shares),
        "avg_cost": float(payload.avg_cost),
        "current_price": float(current_price),
        "total_value": float(total_value),
        "gain_loss": float(gain_loss),
        "gain_loss_percent": float((gain_loss / cost * 100.0) if cost else 0.0),
        "portfolio_name": payload.portfolio_name or "My Portfolio",
        "added_date": now_iso(),
    }
    await db.portfolio.update_one({"user_id": user["id"], "symbol": doc["symbol"], "portfolio_name": doc["portfolio_name"]}, {"$set": doc}, upsert=True)
    return {"success": True, "message": "Holding upserted", "data": {k: doc[k] for k in ["id", "symbol", "shares", "avg_cost", "portfolio_name"], "action": "added"}}


@api.delete("/portfolio/{holding_id}/")
async def delete_portfolio(holding_id: str, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    res = await db.portfolio.delete_one({"user_id": user["id"], "id": holding_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "message": "Deleted", "data": {"id": holding_id}}


# ----
# News
# ----
@api.get("/news/feed/", response_model=NewsFeedResponse)
async def news_feed(limit: int = 20, category: Optional[str] = None, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    docs = await db.news.find({}).sort([("published_at", -1)]).limit(limit).to_list(limit)
    return NewsFeedResponse(success=True, data={"news_items": docs, "count": len(docs)}, message="OK")


@api.post("/news/mark-read/")
async def news_mark_read(body: Dict[str, Any], authorization: Optional[str] = None):
    _ = await get_user_from_token(authorization)
    news_id = body.get("news_id")
    if not news_id or int(news_id) < 1:
        raise HTTPException(status_code=400, detail="Invalid news_id")
    await db.news_reads.update_one({"news_id": int(news_id)}, {"$set": {"read": True, "read_at": now_iso()}}, upsert=True)
    return {"success": True, "message": "Read"}


@api.post("/news/mark-clicked/")
async def news_mark_clicked(body: Dict[str, Any], authorization: Optional[str] = None):
    _ = await get_user_from_token(authorization)
    news_id = body.get("news_id")
    if not news_id or int(news_id) < 1:
        raise HTTPException(status_code=400, detail="Invalid news_id")
    await db.news_reads.update_one({"news_id": int(news_id)}, {"$set": {"clicked": True, "clicked_at": now_iso()}}, upsert=True)
    return {"success": True, "message": "Clicked"}


@api.post("/news/preferences/")
async def news_preferences(payload: NewsPrefRequest, authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    await db.news_prefs.update_one({"user_id": user["id"]}, {"$set": payload.model_dump()}, upsert=True)
    return {"success": True, "data": payload.model_dump(), "message": "Updated"}


@api.post("/news/sync-portfolio/")
async def news_sync_portfolio(authorization: Optional[str] = None):
    user = await get_user_from_token(authorization)
    # For MVP we just confirm sync
    return {"success": True, "message": "Portfolio synced for news preferences"}


# --------
# Revenue
# --------
@revenue.post("/initialize-codes/")
async def revenue_init():
    # Seed two default codes if not present
    for c, pct, desc in [("ref50", 50.0, "Referral 50% off"), ("trial", 100.0, "Free trial")]:
        await db.revenue_codes.update_one({"code": c}, {"$setOnInsert": {"code": c, "discount_percentage": pct, "description": desc, "active": True}}, upsert=True)
    return {"success": True, "data": {"ref50": {"discount_percentage": 50.0}, "trial": {"discount_percentage": 100.0}, "message": "Initialized"}, "timestamp": now_iso(), "endpoint": "/api/revenue/initialize-codes/", "method": "POST"}


@revenue.post("/validate-discount/", response_model=RevenueValidateResponse)
async def validate_discount(payload: RevenueValidateRequest, authorization: Optional[str] = None):
    code = (payload.code or "").lower()
    doc = await db.revenue_codes.find_one({"code": code, "active": True})
    if not doc:
        return RevenueValidateResponse(valid=False, message="Invalid code", applies_discount=False)
    return RevenueValidateResponse(valid=True, message="Valid", applies_discount=True, code=code, discount_percentage=float(doc.get("discount_percentage", 0.0)), description=doc.get("description", ""))


@revenue.post("/apply-discount/", response_model=RevenueApplyResponse)
async def apply_discount(payload: RevenueApplyRequest, authorization: Optional[str] = None):
    code = (payload.code or "").lower()
    doc = await db.revenue_codes.find_one({"code": code, "active": True})
    pct = float(doc.get("discount_percentage", 0.0)) if doc else 0.0
    discount_amount = round(float(payload.amount) * pct / 100.0, 2)
    final_amount = round(float(payload.amount) - discount_amount, 2)
    return RevenueApplyResponse(success=True, code=code, applies_discount=bool(doc), original_amount=float(payload.amount), discount_amount=discount_amount, final_amount=final_amount, savings_percentage=pct, message="Applied" if doc else "No discount")


@revenue.post("/record-payment/", response_model=RevenueRecordResponse)
async def record_payment(payload: RevenueRecordRequest):
    code_doc = await db.revenue_codes.find_one({"code": (payload.discount_code or "").lower(), "active": True}) if payload.discount_code else None
    pct = float(code_doc.get("discount_percentage", 0.0)) if code_doc else 0.0
    discount_amount = round(float(payload.amount) * pct / 100.0, 2)
    final_amount = round(float(payload.amount) - discount_amount, 2)
    commission_amount = round(final_amount * 0.1, 2)
    month_year = make_month_year(datetime.fromisoformat(payload.payment_date.replace("Z", ""))) if payload.payment_date else make_month_year()
    rid = await get_next_sequence(db, "revenue_id")
    doc = {
        "id": rid,
        "user_id": payload.user_id,
        "original_amount": float(payload.amount),
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "commission_amount": commission_amount,
        "revenue_type": "subscription",
        "payment_date": payload.payment_date or now_iso(),
        "discount_code": (payload.discount_code or "").lower() or None,
        "month_year": month_year,
    }
    await db.revenue_records.insert_one(doc)
    return RevenueRecordResponse(success=True, revenue_id=rid, original_amount=doc["original_amount"], discount_amount=discount_amount, final_amount=final_amount, commission_amount=commission_amount, revenue_type="subscription", month_year=month_year)


@revenue.get("/revenue-analytics/")
@revenue.get("/revenue-analytics/{month_year}/")
async def revenue_analytics(month_year: Optional[str] = None, format: Optional[str] = "json"):
    q = {"month_year": month_year} if month_year else {}
    docs = await db.revenue_records.find(q).to_list(1000)
    total = sum([d.get("final_amount", 0.0) for d in docs])
    return {"success": True, "data": {"total_revenue": total, "records": docs}, "timestamp": now_iso(), "endpoint": "/api/revenue/revenue-analytics/", "method": "GET"}


@revenue.get("/monthly-summary/{month_year}/")
async def monthly_summary(month_year: str, authorization: Optional[str] = None):
    # Simulate staff-only by requiring any valid token for MVP
    _ = await get_user_from_token(authorization)
    docs = await db.revenue_records.find({"month_year": month_year}).to_list(1000)
    total = sum([d.get("final_amount", 0.0) for d in docs])
    discount_total = sum([d.get("discount_amount", 0.0) for d in docs])
    commission_total = sum([d.get("commission_amount", 0.0) for d in docs])
    return {"success": True, "summary": {"month_year": month_year, "total_revenue": total, "regular_revenue": total - discount_total, "discount_generated_revenue": total, "total_discount_savings": discount_total, "total_commission_owed": commission_total, "total_paying_users": len(docs), "new_discount_users": 0, "existing_discount_users": 0, "last_updated": now_iso()}}


# Include routers
app.include_router(api)
app.include_router(revenue)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()