# MVP2 Version 3.4 - Comprehensive Analysis & Roadmap

**Analysis Date:** December 23, 2025
**Document Version:** 3.4 (Updated specification)
**Current Status:** Phases 1-5 Complete, Phases 6-11 Pending

---

## Executive Summary

The MVP2 specification has been **significantly updated** from a simple 10-phase plan to a **comprehensive, production-grade blueprint** with:
- Updated subscription tiers ($9.99 Basic / $24.99 Pro)
- **Strict data flow rules** (Stooq browser-side, yfinance server-side)
- **Paper trading system** (new critical feature)
- **SMS-only alerts** (TextBelt self-hosted, no email)
- **11 phases** instead of 10 (added Phase 11: Proper Setup)
- TradingView × Apple design inspiration
- Extensive feature inventory

---

## Major Changes from Previous Version

| Aspect | Old MVP2 | New MVP2 v3.4 |
|--------|----------|---------------|
| **Pricing** | $15 Basic / $25 Premium | $9.99 Basic / $24.99 Pro |
| **Charting Source** | Unspecified | **Stooq (browser-side only)** |
| **Data Source** | yfinance | **yfinance (server-side only)** |
| **Alerts** | Email mentioned | **SMS only (TextBelt)** |
| **Paper Trading** | Not mentioned | **Required first-class feature** |
| **Options** | Basic mention | **Intraday chains, Greeks, IV surfaces** |
| **News** | Basic | **NLP sentiment, filtering, calendar** |
| **Exotic Charts** | Not specified | **Renko, Kagi, P&F, Heikin-Ashi** |
| **Phase Count** | 10 | **11 (added Proper Setup)** |
| **Design Standard** | Generic | **TradingView × Apple inspired** |

---

## Critical Architecture Rules

### 1. Data Flow (STRICT - Cannot Be Violated)

**Charting:**
```
User Browser → Stooq API → HTML Modification → Display
NO server relay, NO database storage of chart data
```

**Analytics/Storage:**
```
Server → yfinance → Database → API → Frontend
Used for: Screeners, Valuations, Backtests, Journals
```

**Why This Matters:**
- Avoids data provider license violations
- Reduces server load (charts = client-side)
- Separates concerns (charts vs analytics)
- Legal compliance

### 2. Alert System (SMS Only)

**Requirements:**
- ❌ NO email alerts anywhere
- ✅ SMS via TextBelt (self-hosted, free, no signup)
- ✅ Webhook support
- ✅ Single & multi-condition alerts

**Implementation:**
- Basic tier: Single-condition SMS
- Pro tier: Multi-condition SMS
- TextBelt API integration (open source)

### 3. Paper Trading (NEW - Critical Feature)

**Architecture:**
```
Separate ledger (never mixed with real data)
├── Visual: Stooq browser charts
├── Execution: yfinance database prices
├── Deterministic fills (slippage, spread, latency simulation)
└── Performance tracking (P&L, drawdowns, win rate)
```

**Order Types:**
- Basic: Market, Limit, Stop
- Pro: Bracket, OCO, Trailing stop-loss

**Why Critical:**
- Reduces user fear
- Encourages experimentation
- Retention anchor (performance history)
- Validates strategies before real money

---

## Current State Analysis

### ✅ Phases 1-5 Complete (50%)

**Phase 1: Core Infrastructure**
- ✅ Trading mode toggle
- ✅ User profiles
- ✅ Subscription system

**Phase 2: Valuation Engine**
- ✅ StockFundamentals model
- ✅ ValuationService (DCF, EPV, Graham, PEG)
- ✅ Composite scoring
- ✅ Undervalued screener

**Phase 3: Advanced Charting**
- ✅ Stooq HTML5 charts
- ✅ Multiple chart types
- ✅ Technical indicators
- ✅ Drawing tools

**Phase 4: AI Backtesting**
- ✅ BacktestRun model
- ✅ Groq AI integration
- ✅ Natural language → Python code
- ✅ Performance metrics

**Phase 5: Value Hunter**
- ✅ Automated weekly portfolio
- ✅ Monday buy / Friday sell
- ✅ Top 10 selection
- ✅ Benchmark tracking

### ⏳ Phases 6-11 Pending (50%)

**What's Missing:**
- Phase 6: Strategy ranking & leaderboards
- Phase 7: Education & tooltips
- Phase 8: Social & copy trading
- Phase 9: Trading journal & retention
- Phase 10: UI/UX polish & mobile
- Phase 11: Docker, cleanup, deployment

---

## New Features Required (Not Yet Implemented)

### 1. Paper Trading System ⚠️ CRITICAL

**Status:** NOT IMPLEMENTED
**Priority:** HIGHEST
**Complexity:** HIGH

**Required Components:**
```python
# Models needed
class PaperTradingAccount(models.Model):
    user = ForeignKey(User)
    starting_balance = DecimalField
    current_balance = DecimalField
    created_at = DateTimeField

class PaperTrade(models.Model):
    account = ForeignKey(PaperTradingAccount)
    symbol = CharField
    order_type = CharField  # market, limit, stop, bracket, oco, trailing
    side = CharField  # buy, sell
    quantity = DecimalField
    entry_price = DecimalField
    exit_price = DecimalField
    slippage = DecimalField
    status = CharField  # pending, filled, cancelled
    pnl = DecimalField

class PaperTradePerformance(models.Model):
    account = ForeignKey(PaperTradingAccount)
    total_pnl = DecimalField
    win_rate = DecimalField
    max_drawdown = DecimalField
    sharpe_ratio = DecimalField
```

**Files to Create:**
- `stocks/models.py` - Add paper trading models
- `stocks/services/paper_trading_service.py` - Execution engine
- `stocks/paper_trading_api.py` - REST endpoints
- Frontend: Paper trading dashboard

**Estimated Effort:** 2-3 weeks

### 2. SMS Alert System (TextBelt)

**Status:** NOT IMPLEMENTED
**Priority:** HIGH
**Complexity:** MEDIUM

**Requirements:**
- Self-hosted TextBelt instance
- Alert condition builder
- SMS queue management
- Rate limiting per user

**Implementation:**
```python
# Models
class Alert(models.Model):
    user = ForeignKey(User)
    symbol = CharField
    condition_type = CharField  # price_above, price_below, volume_spike, etc.
    threshold = DecimalField
    phone_number = CharField
    enabled = BooleanField

class AlertHistory(models.Model):
    alert = ForeignKey(Alert)
    triggered_at = DateTimeField
    message = TextField
    sms_status = CharField  # sent, failed, pending
```

**Files to Create:**
- `stocks/models.py` - Alert models
- `stocks/services/alert_service.py` - Condition checking
- `stocks/services/sms_service.py` - TextBelt integration
- Celery task for alert monitoring

**Estimated Effort:** 1-2 weeks

### 3. Options Analytics

**Status:** PARTIALLY IMPLEMENTED
**Priority:** MEDIUM
**Complexity:** HIGH

**Requirements:**
- Intraday options chains
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Implied volatility surfaces
- Options screener

**What Exists:**
- Basic options data structure (possibly in valuation_json)

**What's Needed:**
- Real-time options chain fetching
- Greeks calculation service
- IV surface visualization
- Options-specific API endpoints

**Estimated Effort:** 3-4 weeks

### 4. News & Sentiment

**Status:** NOT IMPLEMENTED
**Priority:** MEDIUM
**Complexity:** MEDIUM

**Requirements:**
- Real-time news ingestion (API: Finnhub, Alpha Vantage, or NewsAPI)
- NLP sentiment analysis
- News filtering (ticker, sentiment, category)
- Economic calendar integration

**Implementation:**
```python
# Models
class NewsArticle(models.Model):
    ticker = ForeignKey(Stock)
    headline = CharField
    summary = TextField
    source = CharField
    published_at = DateTimeField
    sentiment_score = DecimalField  # -1 to 1
    category = CharField

class EconomicEvent(models.Model):
    event_type = CharField  # earnings, fed_decision, macro_release
    date = DateTimeField
    impact = CharField  # high, medium, low
    actual = DecimalField
    forecast = DecimalField
```

**Files to Create:**
- `stocks/models.py` - News models
- `stocks/services/news_service.py` - Ingestion & sentiment
- `stocks/news_api.py` - REST endpoints
- Celery task for news fetching

**Estimated Effort:** 2-3 weeks

### 5. Exotic Chart Types

**Status:** PARTIALLY IMPLEMENTED (Stooq has these)
**Priority:** LOW (Stooq may already support)
**Complexity:** LOW

**Required Charts:**
- Renko
- Kagi
- Point & Figure
- Heikin-Ashi

**Action:**
- Verify Stooq supports these
- If not, add via TradingView Lightweight Charts library

**Estimated Effort:** 1 week (if needed)

---

## Phases 6-11 Breakdown

### Phase 6: Strategy Ranking & Scoring ⏳

**Complexity:** MEDIUM
**Estimated Time:** 2-3 weeks

**Components:**
1. Composite scoring engine
   - Normalize metrics across strategies
   - Weight calculation (Sharpe, win rate, drawdown, etc.)
   - Category-specific scoring

2. Leaderboards
   - Day trading leaderboard
   - Swing trading leaderboard
   - Long-term leaderboard
   - Overall leaderboard

3. Anti-overfitting controls
   - Minimum trade count requirements
   - Out-of-sample testing
   - Walk-forward validation scores

4. Strategy cloning
   - Copy strategy parameters
   - Attribution to original author
   - Version tracking

**Models:**
```python
class StrategyRanking(models.Model):
    strategy = ForeignKey(BacktestRun)
    category = CharField
    composite_score = DecimalField
    rank = IntegerField
    percentile = DecimalField
    updated_at = DateTimeField
```

**Files:**
- `stocks/services/ranking_service.py`
- `stocks/ranking_api.py`
- Frontend: Leaderboard pages

---

### Phase 7: Education & Context ⏳

**Complexity:** LOW-MEDIUM
**Estimated Time:** 2 weeks

**Components:**
1. Structured learning paths
   - Beginner → Intermediate → Advanced
   - Topics: Technical analysis, Fundamentals, Options, Strategy building

2. Indicator explanations
   - What is RSI?
   - What is MACD?
   - How to use Bollinger Bands?

3. Inline tooltips
   - Hover over any metric → explanation
   - Context-aware help

4. Feature walkthroughs
   - First-time user onboarding
   - Interactive tours (e.g., Intro.js)

5. Knowledge base
   - FAQ section
   - Video tutorials
   - Written guides

**Models:**
```python
class LearningPath(models.Model):
    name = CharField
    difficulty = CharField  # beginner, intermediate, advanced
    order = IntegerField

class LearningModule(models.Model):
    path = ForeignKey(LearningPath)
    title = CharField
    content = TextField
    video_url = URLField
    order = IntegerField

class UserProgress(models.Model):
    user = ForeignKey(User)
    module = ForeignKey(LearningModule)
    completed = BooleanField
    completed_at = DateTimeField
```

**Files:**
- `education/` app (new Django app)
- Frontend: Education portal

---

### Phase 8: Social & Copy Trading ⏳

**Complexity:** HIGH
**Estimated Time:** 3-4 weeks

**Components:**
1. Public profiles (opt-in)
   - User bio, avatar
   - Trading stats (win rate, total return, Sharpe)
   - Public strategies

2. Strategy sharing
   - Publish strategy to community
   - Visibility controls (public, followers-only, private)

3. Copy trading
   - Paper trading copying (follow another user's paper trades)
   - Live-ready architecture (for future real money)
   - Delayed copying (e.g., 15-minute delay for free)

4. Referral tracking
   - Unique referral links
   - Referral rewards (free Pro months, etc.)

**Models:**
```python
class UserProfile(models.Model):  # Extend existing
    bio = TextField
    avatar = ImageField
    public_profile = BooleanField
    follower_count = IntegerField
    following_count = IntegerField

class Follow(models.Model):
    follower = ForeignKey(User)
    following = ForeignKey(User)
    created_at = DateTimeField

class CopyTrading(models.Model):
    copier = ForeignKey(User)
    trader = ForeignKey(User)
    paper_account = ForeignKey(PaperTradingAccount)
    auto_copy = BooleanField
    delay_minutes = IntegerField

class Referral(models.Model):
    referrer = ForeignKey(User)
    referred = ForeignKey(User)
    code = CharField(unique=True)
    reward_granted = BooleanField
```

**Files:**
- `social/` app (new Django app)
- Frontend: Profile pages, follow system, copy trading UI

---

### Phase 9: Retention & Habits ⏳

**Complexity:** MEDIUM
**Estimated Time:** 2-3 weeks

**Components:**
1. Trading journal
   - Entry/exit notes
   - Emotional state tracking
   - Screenshot uploads
   - Tags & categories

2. Monthly performance reviews
   - Automated reports
   - Best/worst trades
   - Monthly trends
   - Improvement suggestions

3. Emotional tagging
   - Tag trades: Fear, Greed, FOMO, Disciplined, etc.
   - Emotion-based analytics

4. Custom indicators
   - User-created technical indicators
   - Formula builder
   - Backtesting with custom indicators

5. Exports & tax prep
   - CSV export
   - Tax-ready formats
   - P&L summaries

**Models:**
```python
class JournalEntry(models.Model):
    user = ForeignKey(User)
    trade = ForeignKey(PaperTrade)  # or real trade
    notes = TextField
    emotional_state = CharField
    screenshot = ImageField
    tags = JSONField
    created_at = DateTimeField

class CustomIndicator(models.Model):
    user = ForeignKey(User)
    name = CharField
    formula = TextField
    parameters = JSONField
    created_at = DateTimeField
```

**Files:**
- `journal/` app (new Django app)
- `stocks/services/custom_indicator_service.py`
- Frontend: Journal UI, custom indicator builder

---

### Phase 10: Polish, Scale & Trust ⏳

**Complexity:** MEDIUM-HIGH
**Estimated Time:** 3-4 weeks

**Components:**
1. Modular dashboards
   - Drag & drop widgets
   - Save layouts
   - Widget library (charts, watchlists, news, P&L, etc.)

2. Advanced chart UX
   - Keyboard shortcuts
   - Multi-chart layouts
   - Synchronized charts

3. Mobile parity
   - Full mobile charting (touch-optimized)
   - Responsive tables
   - Mobile-specific UI

4. Performance tuning
   - Database query optimization
   - Redis caching
   - CDN setup
   - Load testing (100+ concurrent users)

5. Security hardening
   - MFA (2FA)
   - Session management
   - Rate limiting
   - Encryption at rest & in transit

6. CTA clarity
   - Clear upgrade paths
   - Feature gating UI
   - Conversion optimization

7. Navigation simplification
   - Sidebar cleanup
   - Breadcrumbs
   - Search functionality

**Files:**
- Frontend: Complete redesign/refactor
- Backend: Performance optimization
- Infrastructure: CDN, load balancer

---

### Phase 11: Proper Setup (NEW) ⏳

**Complexity:** HIGH
**Estimated Time:** 2-3 weeks

**Components:**
1. Docker container setup
   - Dockerfile for backend
   - Dockerfile for frontend
   - docker-compose.yml
   - Environment variable management

2. Clean repo (remove clutter)
   - Delete unused files
   - Organize documentation
   - Clean up test files

3. Load balancer
   - Nginx configuration
   - Multi-instance support
   - Global deployment ready

4. Setup scripts
   - Database setup script (migrations, seed data)
   - Tunnel setup script (Cloudflare)
   - Test scripts (health checks, troubleshooting)

5. 10-30 minute setup goal
   - Single command: `docker-compose up`
   - Automated migrations
   - Sample data loading

**Files to Create:**
- `Dockerfile` (backend)
- `frontend/Dockerfile`
- `docker-compose.yml`
- `scripts/setup_database.sh`
- `scripts/setup_tunnel.sh`
- `scripts/health_check.sh`
- `.env.example`
- `SETUP_GUIDE.md`

---

## Priority Roadmap

### Immediate (Next 2-4 Weeks)

1. **Paper Trading System** ⚠️ CRITICAL
   - Models, service, API
   - Basic order types (market, limit, stop)
   - Performance tracking
   - Frontend UI

2. **SMS Alerts (TextBelt)**
   - Alert models
   - Condition builder
   - TextBelt integration
   - Frontend alert management

### Short-Term (1-2 Months)

3. **Options Analytics**
   - Options chain fetching
   - Greeks calculation
   - Basic screener

4. **News & Sentiment**
   - News ingestion
   - Sentiment analysis
   - Economic calendar

### Medium-Term (2-3 Months)

5. **Phase 6: Strategy Ranking**
6. **Phase 7: Education**
7. **Phase 9: Trading Journal**

### Long-Term (3-6 Months)

8. **Phase 8: Social & Copy Trading**
9. **Phase 10: Polish & Mobile**
10. **Phase 11: Proper Setup**

---

## Subscription Tier Implementation

### What Needs Feature Gating

**Basic ($9.99) Restrictions:**
- ❌ Exotic charts (Renko, Kagi, P&F, Heikin-Ashi)
- ❌ Saved chart layouts
- ❌ Strategy backtesting
- ❌ Options analytics
- ❌ Advanced paper trading orders (bracket, OCO, trailing)
- ❌ Multi-condition alerts
- ❌ Copy trading

**Pro ($24.99) Full Access:**
- ✅ Everything in Basic
- ✅ All exotic chart types
- ✅ Unlimited saved layouts
- ✅ AI backtesting
- ✅ Full options analytics
- ✅ Advanced paper trading
- ✅ Multi-condition alerts
- ✅ Copy trading
- ✅ Trading journal
- ✅ Custom themes

**Implementation:**
```python
# Decorator for feature gating
def requires_pro(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.subscription_tier == 'pro':
            return Response({'error': 'Pro subscription required'}, status=403)
        return func(request, *args, **kwargs)
    return wrapper

# Usage
@requires_pro
def create_backtest(request):
    # Backtest creation logic
    pass
```

---

## Design Standards

**Inspiration:** TradingView × Apple

**Principles:**
1. **Minimalist** - Remove unnecessary elements
2. **High-density** - Maximum information, minimum space
3. **Color-agnostic** - Works in any color scheme
4. **Professional** - Serious, trustworthy, not gamified
5. **Clean data presentation** - Tables, charts, numbers

**Typography:**
- System fonts (San Francisco, Segoe UI, Roboto)
- Clear hierarchy
- Readable at all sizes

**Layout:**
- Grid-based
- Consistent spacing
- Logical grouping

---

## Next Steps

1. **Commit scanner file reorganization**
2. **Create paper trading models & service** (highest priority)
3. **Set up TextBelt for SMS alerts**
4. **Begin Phase 6 implementation** (strategy ranking)
5. **Frontend: Update subscription tiers to $9.99/$24.99**
6. **Frontend: Implement feature gating**
7. **Documentation: Update all docs to reflect v3.4 spec**

---

## Files Moved (Completed)

✅ Scanner files organized into `stock_retrieval/`:
- `scanner_1min_hybrid.py` → `stock_retrieval/scanner_1min_hybrid.py`
- `realtime_daily_with_proxies.py` → `stock_retrieval/realtime_daily_with_proxies.py`
- `http_proxies.txt` → `stock_retrieval/http_proxies.txt`

---

*Analysis completed: December 23, 2025*
*Next update: After Phase 6 implementation begins*
