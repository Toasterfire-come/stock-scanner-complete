from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
import uuid


class APIMessage(BaseModel):
    status: str = "ok"
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
    timestamp: str
    endpoints: Dict[str, str]
    features: Dict[str, bool]


class PricePoint(BaseModel):
    price: float
    timestamp: str


class Stock(BaseModel):
    ticker: str
    symbol: str
    company_name: str
    exchange: str
    current_price: Optional[float] = None
    price_change_today: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[int] = None
    last_updated: Optional[str] = None
    currency: Optional[str] = "USD"
    price_history: List[PricePoint] = []
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None


class StocksListResponse(BaseModel):
    success: bool
    data: List[Stock]
    count: Optional[int] = None
    total_available: Optional[int] = None
    filters_applied: Optional[Dict[str, Any]] = None
    timestamp: str


class StockDetailResponse(BaseModel):
    success: bool
    data: Optional[Stock] = None
    timestamp: str
    error: Optional[str] = None


class SearchResult(BaseModel):
    ticker: str
    company_name: str
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    market_cap: Optional[int] = None
    exchange: Optional[str] = None
    match_type: str = "ticker"
    url: str


class SearchResponse(BaseModel):
    success: bool
    query: str
    count: int
    results: List[SearchResult]
    timestamp: str


class AlertsCreateMeta(BaseModel):
    endpoint: str
    method: str
    description: str
    required_fields: Dict[str, str]
    example_request: Dict[str, Any]
    usage: str


class AlertCreateRequest(BaseModel):
    ticker: str
    target_price: float
    condition: str  # above|below
    email: EmailStr


class AlertCreateResponse(BaseModel):
    alert_id: int
    message: str
    details: Dict[str, Any]


class SubscriptionRequest(BaseModel):
    email: EmailStr
    category: Optional[str] = None


class SubscriptionResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone: Optional[str] = ""
    company: Optional[str] = ""
    date_joined: str
    last_login: Optional[str] = None
    is_premium: bool = False


class LoginResponse(BaseModel):
    success: bool
    data: UserProfile
    message: str
    token: str


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class BillingHistoryItem(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    status: str
    method: str
    download_url: str


class BillingHistoryResponse(BaseModel):
    success: bool
    data: List[BillingHistoryItem]
    pagination: Dict[str, Any]


class CurrentPlanResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


class ChangePlanRequest(BaseModel):
    plan_type: str
    billing_cycle: str


class NotificationSettings(BaseModel):
    trading: Dict[str, bool]
    portfolio: Dict[str, bool]
    news: Dict[str, bool]
    security: Dict[str, bool]


class NotificationItem(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str
    read_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationHistoryResponse(BaseModel):
    success: bool
    data: List[NotificationItem]
    pagination: Dict[str, Any]
    summary: Dict[str, int]


class MarkReadRequest(BaseModel):
    notification_ids: Optional[List[int]] = None
    mark_all: Optional[bool] = False


class WatchlistItem(BaseModel):
    id: str
    symbol: str
    company_name: Optional[str] = ""
    current_price: Optional[float] = 0.0
    price_change: Optional[float] = 0.0
    price_change_percent: Optional[float] = 0.0
    volume: Optional[int] = 0
    market_cap: Optional[int] = 0
    watchlist_name: str
    notes: Optional[str] = ""
    alert_price: Optional[float] = None
    added_date: str


class WatchlistAddRequest(BaseModel):
    symbol: str
    watchlist_name: Optional[str] = "My Watchlist"
    notes: Optional[str] = None
    alert_price: Optional[float] = None


class PortfolioItem(BaseModel):
    id: str
    symbol: str
    shares: float
    avg_cost: float
    current_price: float
    total_value: float
    gain_loss: float
    gain_loss_percent: float
    portfolio_name: str
    added_date: str


class PortfolioAddRequest(BaseModel):
    symbol: str
    shares: float
    avg_cost: float
    portfolio_name: Optional[str] = "My Portfolio"


class NewsFeedResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None


class NewsPrefRequest(BaseModel):
    followed_stocks: List[str]
    followed_sectors: List[str]
    preferred_categories: List[str]
    news_frequency: str


class RevenueValidateRequest(BaseModel):
    code: str


class RevenueValidateResponse(BaseModel):
    valid: bool
    message: str
    applies_discount: bool
    code: Optional[str] = None
    discount_percentage: Optional[float] = None
    description: Optional[str] = None


class RevenueApplyRequest(BaseModel):
    code: str
    amount: float


class RevenueApplyResponse(BaseModel):
    success: bool
    code: str
    applies_discount: bool
    original_amount: float
    discount_amount: float
    final_amount: float
    savings_percentage: float
    message: str


class RevenueRecordRequest(BaseModel):
    user_id: int
    amount: float
    discount_code: Optional[str] = None
    payment_date: Optional[str] = None


class RevenueRecordResponse(BaseModel):
    success: bool
    revenue_id: int
    original_amount: float
    discount_amount: float
    final_amount: float
    commission_amount: float
    revenue_type: str
    month_year: str