from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Dict, Any
import uuid
from datetime import datetime
import asyncio
import math

import httpx
import stripe


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Third-party configs
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
stripe.api_key = os.environ.get('STRIPE_API_KEY')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

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


# -----------------------------
# Health and configuration
# -----------------------------

class HealthResponse(BaseModel):
    status: Literal['ok', 'degraded', 'down']
    mongodb: Literal['ok', 'down']
    time: datetime = Field(default_factory=datetime.utcnow)


@api_router.get('/health', response_model=HealthResponse)
async def health_check():
    mongodb_status: Literal['ok', 'down'] = 'down'
    try:
        # Ping the database to confirm connectivity
        await db.command('ping')
        mongodb_status = 'ok'
    except Exception as exc:
        logger.exception('MongoDB ping failed: %s', exc)

    status: Literal['ok', 'degraded', 'down']
    status = 'ok' if mongodb_status == 'ok' else 'degraded'

    return HealthResponse(status=status, mongodb=mongodb_status)


# -----------------------------
# Market data helpers (Alpha Vantage)
# -----------------------------

ALPHA_VANTAGE_BASE = 'https://www.alphavantage.co/query'


async def fetch_alpha_vantage_daily(symbol: str) -> Dict[str, Any]:
    if not ALPHA_VANTAGE_API_KEY:
        raise HTTPException(status_code=400, detail='ALPHA_VANTAGE_API_KEY not configured')
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'outputsize': 'compact',
        'apikey': ALPHA_VANTAGE_API_KEY,
    }
    async with httpx.AsyncClient(timeout=20) as client_http:
        response = await client_http.get(ALPHA_VANTAGE_BASE, params=params)
        response.raise_for_status()
        data = response.json()
        if 'Error Message' in data or 'Time Series (Daily)' not in data:
            raise HTTPException(status_code=502, detail=f'Alpha Vantage daily data unavailable for {symbol}')
        return data


async def fetch_alpha_vantage_overview(symbol: str) -> Dict[str, Any]:
    if not ALPHA_VANTAGE_API_KEY:
        raise HTTPException(status_code=400, detail='ALPHA_VANTAGE_API_KEY not configured')
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
    }
    async with httpx.AsyncClient(timeout=20) as client_http:
        response = await client_http.get(ALPHA_VANTAGE_BASE, params=params)
        response.raise_for_status()
        data = response.json()
        if not data or 'Symbol' not in data:
            raise HTTPException(status_code=502, detail=f'Alpha Vantage overview unavailable for {symbol}')
        return data


async def get_universe_tickers(universe: Optional[str]) -> List[str]:
    if not universe:
        return []
    uni = (universe or '').lower()
    if uni == 'sp500':
        import pandas as pd  # heavy import on demand

        def _read_sp500() -> List[str]:
            tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = tables[0]
            return df['Symbol'].astype(str).tolist()

        return await asyncio.to_thread(_read_sp500)
    if uni == 'nasdaq100':
        import pandas as pd

        def _read_nasdaq100() -> List[str]:
            tables = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
            # Find the table with tickers
            for table in tables:
                cols = [str(c).lower() for c in table.columns]
                if any('ticker' in c or 'symbol' in c for c in cols):
                    col = table.columns[0]
                    return table[col].astype(str).tolist()
            return []

        return await asyncio.to_thread(_read_nasdaq100)
    if uni == 'dow30':
        import pandas as pd

        def _read_dow30() -> List[str]:
            tables = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
            for table in tables:
                cols = [str(c).lower() for c in table.columns]
                if any('symbol' in c for c in cols):
                    col = [c for c in table.columns if 'Symbol' in str(c)][0]
                    return table[col].astype(str).tolist()
            return []

        return await asyncio.to_thread(_read_dow30)
    return []


def compute_breakout_from_daily_series(series: Dict[str, Dict[str, str]], lookback_days: int = 20) -> Optional[Dict[str, Any]]:
    # series: mapping date_str -> OHLCV dicts as strings
    # Convert to chronological list (oldest to newest)
    try:
        ordered_dates = sorted(series.keys())
        closes = []
        highs = []
        volumes = []
        for d in ordered_dates:
            day = series[d]
            closes.append(float(day['4. close']))
            highs.append(float(day['2. high']))
            volumes.append(float(day['6. volume']))
        if len(closes) < lookback_days + 2:
            return None
        # Exclude latest day when computing prior high and avg volume
        prior_high = max(highs[-(lookback_days + 1):-1])
        prior_avg_vol = sum(volumes[-(lookback_days + 1):-1]) / lookback_days
        last_close = closes[-1]
        last_volume = volumes[-1]
        is_breakout = last_close > prior_high and last_volume >= 1.5 * prior_avg_vol
        if not is_breakout:
            return None
        pct_above = (last_close / prior_high - 1.0) * 100.0
        vol_ratio = last_volume / prior_avg_vol if prior_avg_vol > 0 else math.nan
        return {
            'prior_high': prior_high,
            'last_close': last_close,
            'pct_above_prior_high': pct_above,
            'volume_ratio_vs_20d': vol_ratio,
        }
    except Exception as exc:
        logger.exception('Failed to compute breakout: %s', exc)
        return None


def compute_undervalued_from_overview(overview: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        pe = float(overview.get('PERatio') or 'nan')
        pb = float(overview.get('PriceToBookRatio') or 'nan')
        eps = float(overview.get('EPS') or 'nan')
        dividend_yield = float(overview.get('DividendYield') or 'nan') if overview.get('DividendYield') not in (None, 'None') else math.nan
        # Simple heuristic: low P/E and low P/B, positive earnings
        if (not math.isnan(pe) and pe <= 15.0) and (not math.isnan(pb) and pb <= 1.5) and (not math.isnan(eps) and eps > 0):
            score = (15.0 / pe) + (1.5 / pb) + (1.0 if dividend_yield and not math.isnan(dividend_yield) and dividend_yield > 0 else 0)
            return {
                'pe_ratio': pe,
                'price_to_book': pb,
                'eps': eps,
                'dividend_yield': dividend_yield if not math.isnan(dividend_yield) else None,
                'undervalued_score': score,
            }
        return None
    except Exception as exc:
        logger.exception('Failed to compute undervalued: %s', exc)
        return None


class ScanRequest(BaseModel):
    tickers: Optional[List[str]] = None
    universe: Optional[Literal['sp500', 'nasdaq100', 'dow30']] = None
    limit: Optional[int] = Field(default=20, ge=1, le=500)


@api_router.get('/scans/breakouts')
async def scan_breakouts(tickers: Optional[str] = Query(default=None, description='Comma-separated symbols'),
                         universe: Optional[str] = Query(default=None, description='sp500|nasdaq100|dow30'),
                         limit: int = Query(default=20, ge=1, le=200)):
    symbols: List[str] = []
    if tickers:
        symbols = [s.strip().upper() for s in tickers.split(',') if s.strip()]
    if not symbols:
        symbols = await get_universe_tickers(universe)
    if not symbols:
        raise HTTPException(status_code=400, detail='Provide tickers or universe')
    # Rate limiting: Alpha Vantage allows 5 req/min free; limit symbols accordingly
    symbols = symbols[:limit]

    results: List[Dict[str, Any]] = []
    for sym in symbols:
        try:
            data = await fetch_alpha_vantage_daily(sym)
            series = data.get('Time Series (Daily)', {})
            breakout = compute_breakout_from_daily_series(series)
            if breakout:
                item = {
                    'symbol': sym,
                    'signal': 'breakout',
                    **breakout,
                    'slogan': 'Catch breakouts early',
                }
                results.append(item)
        except HTTPException as he:
            logger.warning('Data unavailable for %s: %s', sym, he.detail)
        except Exception as exc:
            logger.exception('Failed to scan %s: %s', sym, exc)

    return {
        'count': len(results),
        'results': sorted(results, key=lambda r: r.get('pct_above_prior_high', 0), reverse=True),
        'message': 'Catch breakouts early',
    }


@api_router.get('/scans/undervalued')
async def scan_undervalued(tickers: Optional[str] = Query(default=None, description='Comma-separated symbols'),
                           universe: Optional[str] = Query(default=None, description='sp500|nasdaq100|dow30'),
                           limit: int = Query(default=20, ge=1, le=200)):
    symbols: List[str] = []
    if tickers:
        symbols = [s.strip().upper() for s in tickers.split(',') if s.strip()]
    if not symbols:
        symbols = await get_universe_tickers(universe)
    if not symbols:
        raise HTTPException(status_code=400, detail='Provide tickers or universe')
    symbols = symbols[:limit]

    results: List[Dict[str, Any]] = []
    for sym in symbols:
        try:
            overview = await fetch_alpha_vantage_overview(sym)
            undervalued = compute_undervalued_from_overview(overview)
            if undervalued:
                results.append({
                    'symbol': sym,
                    'signal': 'undervalued',
                    **undervalued,
                    'slogan': 'Find undervalued stocks in 1 click',
                })
        except HTTPException as he:
            logger.warning('Overview unavailable for %s: %s', sym, he.detail)
        except Exception as exc:
            logger.exception('Failed to evaluate %s: %s', sym, exc)

    return {
        'count': len(results),
        'results': sorted(results, key=lambda r: r.get('undervalued_score', 0), reverse=True),
        'message': 'Find undervalued stocks in 1 click',
    }


# -----------------------------
# Referrals
# -----------------------------


def generate_referral_code() -> str:
    return uuid.uuid4().hex[:8]


class ReferralInviteRequest(BaseModel):
    inviter_id: str
    invitee_email: EmailStr


class ReferralLinkResponse(BaseModel):
    referral_code: str
    referral_link: str


class ReferralSummaryResponse(BaseModel):
    inviter_id: str
    total_invited: int
    total_paid: int
    rewards_months_earned: int
    rewards_months_granted: int
    pending_rewards_months: int


async def get_or_create_user(inviter_id: str) -> Dict[str, Any]:
    user = await db.users.find_one({'inviter_id': inviter_id})
    if user:
        return user
    referral_code = generate_referral_code()
    doc = {
        'inviter_id': inviter_id,
        'referral_code': referral_code,
        'rewards_months_granted': 0,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    await db.users.insert_one(doc)
    return doc


@api_router.get('/referrals/link', response_model=ReferralLinkResponse)
async def get_referral_link(user_id: str = Query(..., description='Current authenticated user id')):
    user = await get_or_create_user(user_id)
    referral_code = user.get('referral_code') or generate_referral_code()
    if not user.get('referral_code'):
        await db.users.update_one({'inviter_id': user_id}, {'$set': {'referral_code': referral_code, 'updated_at': datetime.utcnow()}})
    base_site = os.environ.get('APP_BASE_URL', 'https://retailtradescanner.com')
    link = f"{base_site}/?ref={referral_code}"
    return ReferralLinkResponse(referral_code=referral_code, referral_link=link)


@api_router.post('/referrals/invite')
async def create_referral_invite(payload: ReferralInviteRequest):
    user = await get_or_create_user(payload.inviter_id)
    referral_code = user.get('referral_code')
    invite = await db.referrals.find_one({'invitee_email': str(payload.invitee_email)})
    if invite:
        return {'status': 'exists', 'message': 'Invite already exists for this email'}
    doc = {
        'inviter_id': payload.inviter_id,
        'invitee_email': str(payload.invitee_email).lower(),
        'referral_code': referral_code,
        'status': 'invited',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    await db.referrals.insert_one(doc)
    # Optional: send email via SES if configured
    if os.environ.get('SES_SENDER_EMAIL') and os.environ.get('AWS_REGION'):
        try:
            import boto3

            ses = boto3.client('ses', region_name=os.environ['AWS_REGION'])
            base_site = os.environ.get('APP_BASE_URL', 'https://retailtradescanner.com')
            link = f"{base_site}/?ref={referral_code}"
            ses.send_email(
                Source=os.environ['SES_SENDER_EMAIL'],
                Destination={'ToAddresses': [str(payload.invitee_email)]},
                Message={
                    'Subject': {'Data': 'Join RetailTradeScanner'},
                    'Body': {
                        'Text': {'Data': f"You've been invited to RetailTradeScanner. Sign up here: {link}"}
                    },
                },
            )
        except Exception as exc:
            logger.warning('SES send failed: %s', exc)
    return {'status': 'ok'}


@api_router.get('/referrals/summary', response_model=ReferralSummaryResponse)
async def referral_summary(user_id: str = Query(...)):
    user = await get_or_create_user(user_id)
    total_invited = await db.referrals.count_documents({'inviter_id': user_id})
    total_paid = await db.referrals.count_documents({'inviter_id': user_id, 'status': 'paid'})
    rewards_months_earned = total_paid // 3
    rewards_months_granted = int(user.get('rewards_months_granted', 0))
    pending_rewards_months = max(0, rewards_months_earned - rewards_months_granted)
    return ReferralSummaryResponse(
        inviter_id=user_id,
        total_invited=total_invited,
        total_paid=total_paid,
        rewards_months_earned=rewards_months_earned,
        rewards_months_granted=rewards_months_granted,
        pending_rewards_months=pending_rewards_months,
    )


@api_router.post('/referrals/webhook/stripe')
async def stripe_webhook(request: Request):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail='STRIPE_WEBHOOK_SECRET not configured')
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as exc:
        logger.warning('Stripe signature verification failed: %s', exc)
        raise HTTPException(status_code=400, detail='Invalid signature')

    event_type = event.get('type')
    data_object = event.get('data', {}).get('object', {})
    customer_email = (data_object.get('customer_details', {}) or {}).get('email') or data_object.get('customer_email')
    referral_code = (data_object.get('metadata') or {}).get('referral_code')

    # Only process successful checkout or subscription events
    relevant_types = {
        'checkout.session.completed',
        'invoice.payment_succeeded',
        'customer.subscription.created',
        'customer.subscription.updated',
        'payment_intent.succeeded',
    }
    if event_type not in relevant_types:
        return {'received': True}

    if not referral_code and not customer_email:
        return {'received': True}

    try:
        query = {}
        if referral_code:
            query['referral_code'] = referral_code
        if customer_email:
            query['invitee_email'] = str(customer_email).lower()

        invite = await db.referrals.find_one(query)
        if not invite:
            logger.info('No matching referral found for code=%s email=%s', referral_code, customer_email)
            return {'received': True}

        await db.referrals.update_one({'_id': invite['_id']}, {'$set': {'status': 'paid', 'paid_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}})

        inviter_id = invite['inviter_id']
        user = await get_or_create_user(inviter_id)
        total_paid = await db.referrals.count_documents({'inviter_id': inviter_id, 'status': 'paid'})
        earned_months = total_paid // 3
        already_granted = int(user.get('rewards_months_granted', 0))
        if earned_months > already_granted:
            await db.users.update_one({'inviter_id': inviter_id}, {'$set': {'rewards_months_granted': earned_months, 'updated_at': datetime.utcnow()}})
        return {'received': True}
    except Exception as exc:
        logger.exception('Failed to process Stripe webhook: %s', exc)
        raise HTTPException(status_code=500, detail='Webhook processing failed')


# -----------------------------
# Quality-of-life endpoints
# -----------------------------


@api_router.get('/scans/help')
async def scans_help():
    return {
        'endpoints': {
            'GET /api/scans/breakouts': {
                'query': ['tickers=TSLA,AAPL,MSFT (optional)', 'universe=sp500|nasdaq100|dow30 (optional)', 'limit=20 (optional)'],
                'message': 'Catch breakouts early',
            },
            'GET /api/scans/undervalued': {
                'query': ['tickers=TSLA,AAPL,MSFT (optional)', 'universe=sp500|nasdaq100|dow30 (optional)', 'limit=20 (optional)'],
                'message': 'Find undervalued stocks in 1 click',
            },
        },
        'value': 'Save hours of charting',
    }
