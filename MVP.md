# TRADE SCAN PRO - MVP SPECIFICATION

**Document Version:** 2.1 (AI-Enhanced)  
**Date:** December 2024  
**Last Updated:** December 1, 2024  
**Status:** In Progress

---

# COMPLETION STATUS OVERVIEW

| Phase | Name | Status | Completion |
|-------|------|--------|------------|
| 1 | Core Infrastructure | ✅ COMPLETE | 100% |
| 2 | Valuation Engine | ✅ COMPLETE | 100% |
| 3 | Advanced Charting | ✅ COMPLETE | 100% |
| 4 | AI Backtesting System | 🔄 IN PROGRESS | 60% |
| 5 | Value Hunter Portfolio | 🔄 IN PROGRESS | 70% |
| 6 | Strategy Ranking System | ⏳ PENDING | 0% |
| 7 | Educational Platform | ⏳ PENDING | 0% |
| 8 | Social & Viral Features | 🔄 IN PROGRESS | 40% |
| 9 | Retention Features | 🔄 IN PROGRESS | 30% |
| 10 | UI/UX & Rebrand | ⏳ PENDING | 0% |

---

# AI INTEGRATION (NEW)

## Groq AI Integration for Backtesting

The backtesting system uses **Groq AI** (llama-3.3-70b-versatile) to:
1. Parse natural language strategy descriptions
2. Generate Python trading logic code
3. Validate strategy parameters
4. Optimize entry/exit conditions

### Environment Configuration
```
```

### AI Service Architecture
```
User Strategy Text → Groq AI → Python Code → Backtest Engine → Results
```

---

# PHASE 1: CORE INFRASTRUCTURE ✅ COMPLETE

## 1.1 Completed Items
- [x] Trading Mode Context (`TradingModeContext.jsx`)
- [x] Trading Mode Toggle Component (`TradingModeToggle.jsx`)
- [x] Day Trade / Long-Term mode configurations
- [x] Dynamic navigation per mode
- [x] User Profile model with subscription info
- [x] News system commented out (ready for removal)

## 1.2 Files Implemented
- `/app/frontend/src/context/TradingModeContext.jsx`
- `/app/frontend/src/components/TradingModeToggle.jsx`
- `/app/backend/stocks/models.py` (UserProfile, Stock, etc.)

---

# PHASE 2: VALUATION ENGINE ✅ COMPLETE (100%)

## 2.1 Completed Items
- [x] StockFundamentals model (50+ dedicated fields)
- [x] ValuationService class with all models
- [x] DCF (Discounted Cash Flow) valuation
- [x] EPV (Earnings Power Value) calculation
- [x] Graham Number calculation
- [x] PEG Fair Value model
- [x] Relative Value scoring vs sector
- [x] Composite valuation score (0-100)
- [x] Valuation status classification
- [x] Strength score calculation (0-100)
- [x] Comprehensive valuation API endpoints
- [x] Undervalued stocks screener endpoint
- [x] Daily update service for fundamentals
- [x] Management command for scheduled updates
- [x] Dividend analysis
- [x] Growth metrics (revenue CAGR, EPS)
- [x] Profitability margins
- [x] Balance sheet health
- [x] Cash flow analysis

## 2.3 Technical Specification

### StockFundamentals Model Fields
```python
# Price & Valuation
pe_ratio, forward_pe, peg_ratio, price_to_sales, price_to_book, 
ev_to_revenue, ev_to_ebitda, enterprise_value

# Profitability
gross_margin, operating_margin, profit_margin, roe, roa, roic

# Growth
revenue_growth_yoy, revenue_growth_3y, revenue_growth_5y,
earnings_growth_yoy, earnings_growth_5y, fcf_growth_yoy

# Financial Health
current_ratio, quick_ratio, debt_to_equity, debt_to_assets,
interest_coverage, altman_z_score, piotroski_f_score

# Cash Flow
operating_cash_flow, free_cash_flow, fcf_per_share, fcf_yield

# Dividends
dividend_yield, dividend_payout_ratio, years_dividend_growth

# Calculated Valuations
dcf_value, epv_value, graham_number, peg_fair_value,
relative_value_score, valuation_score, strength_score
```

### Valuation Score Formula
- DCF Weight: 30%
- EPV Weight: 20%
- Graham Number Weight: 15%
- PEG Fair Value Weight: 10%
- Relative Value Weight: 25%

### Status Classification
- 70+ = Significantly Undervalued (STRONG BUY)
- 55-69 = Undervalued (BUY)
- 45-54 = Fair Value (HOLD)
- 30-44 = Overvalued (SELL)
- <30 = Significantly Overvalued (STRONG SELL)

---

# PHASE 3: ADVANCED CHARTING ✅ COMPLETE (100%)

## 3.1 Chart Types
- [x] Candlestick (default)
- [x] Line chart
- [x] Area chart
- [x] Heikin-Ashi (Premium)

## 3.2 Timeframes
- [x] 1m (Premium)
- [x] 5m (Premium)
- [x] 15m
- [x] 30m
- [x] 1H
- [x] 4H (Premium)
- [x] 1D
- [x] 1W
- [x] 1M

## 3.3 Technical Indicators (API Complete)
- [x] SMA (Simple Moving Average) - configurable periods
- [x] EMA (Exponential Moving Average) - configurable periods
- [x] RSI (Relative Strength Index)
- [x] MACD (Moving Average Convergence Divergence)
- [x] Bollinger Bands
- [x] VWAP (Volume Weighted Average Price)
- [x] Stochastic Oscillator
- [x] ATR (Average True Range)

## 3.4 Chart API Endpoints
- [x] GET /api/chart/{ticker}/ - Historical OHLCV data
- [x] GET /api/chart/{ticker}/indicators/ - Technical indicators
- [x] GET /api/chart/timeframes/ - Available timeframes
- [x] Support for multiple chart types and timeframes
- [x] Premium timeframe gating (1m, 5m, 4h)
- [x] Caching for performance

## 3.5 Features Implemented
- [x] Chart data aggregation (4H timeframe)
- [x] Heikin-Ashi conversion
- [x] Volume data included
- [x] Timestamp normalization
- [x] Error handling and validation

## 3.6 Frontend Integration Ready
- Charts are pulled via frontend using APIs
- All table data is served by backend
- Technical indicators calculated server-side
- Real-time price updates handled separately

---

# DATA UPDATE STRATEGY

## Daily Backend Updates (Once per day at market close)

### Fundamental Data
- All 50+ valuation metrics (PE, PEG, margins, ratios, etc.)
- DCF, EPV, Graham Number, PEG Fair Value calculations
- Composite valuation scores and recommendations
- Strength scores and grades
- Market cap, 52-week ranges, average volume
- Dividend data, growth metrics, cash flow metrics

### Technical Data (Daily Timeframe)
- Daily moving averages (SMA, EMA)
- Daily RSI, MACD, Bollinger Bands
- Other daily technical indicators

### Update Methods
```bash
# Manual update
python manage.py update_daily_data

# Cron job (recommended)
0 17 * * * cd /app/backend && python manage.py update_daily_data

# Scheduler daemon
python daily_data_scheduler.py
```

## Real-time Frontend Updates (via browser)

### Price Data
- Current price and price changes
- Bid/Ask prices
- Day's range (high/low)
- Current volume

### Chart Data
- Intraday charts (1m, 5m, 15m, 30m, 1H)
- Real-time technical indicators (intraday timeframes)
- Chart drawing tools and overlays

### API Endpoints
- `/api/chart/{ticker}/` - Chart data (OHLCV)
- `/api/chart/{ticker}/indicators/` - Technical indicators
- `/api/valuation/{ticker}/` - Valuation data (cached from daily updates)

**See `DAILY_DATA_UPDATE_README.md` for full documentation.**

---

# PHASE 4: AI BACKTESTING SYSTEM 🔄 IN PROGRESS (60%)

## 4.1 AI Strategy Generation (Groq Integration)

### How It Works
1. User describes strategy in natural language
2. Groq AI (llama-3.3-70b-versatile) parses and generates Python code
3. Code is validated and sandboxed
4. Backtest engine executes strategy against historical data
5. Results are displayed with metrics

### Environment Configuration
```
GROQ_API_KEY=your_groq_api_key_here
```

### AI Service Architecture
```
User Strategy Text → Groq AI → Python Code → Backtest Engine → Results
```

## 4.2 Backend Implementation Status

### ✅ Completed (Backend)
- [x] `BacktestRun` model with all fields (models.py)
- [x] `BaselineStrategy` model for preset strategies
- [x] `BacktestingService` class with Groq AI integration
- [x] Strategy code generation via AI
- [x] Backtest execution engine
- [x] Performance metrics calculation (Sharpe, drawdown, win rate, etc.)
- [x] API endpoints registered:
  - POST `/api/backtesting/create/` - Create new backtest
  - POST `/api/backtesting/{id}/run/` - Execute backtest
  - GET `/api/backtesting/{id}/` - Get backtest results
  - GET `/api/backtesting/list/` - List all backtests
  - GET `/api/backtesting/baseline-strategies/` - List preset strategies

### ❌ Pending (Frontend)
- [ ] Backtesting UI page
- [ ] Strategy input form (natural language)
- [ ] Results visualization (equity curve, metrics)
- [ ] Baseline strategies selector
- [ ] Backtest history view

## 4.3 Backtest Models
```python
class BacktestRun:
    user: ForeignKey(User)
    name: CharField
    strategy_text: TextField  # User's natural language
    generated_code: TextField  # AI-generated Python
    category: CharField  # day_trading, swing_trading, long_term
    symbols: JSONField
    initial_capital: DecimalField
    status: CharField  # pending, processing, completed, failed
    
    # Results
    total_return: DecimalField
    annualized_return: DecimalField
    sharpe_ratio: DecimalField
    max_drawdown: DecimalField
    win_rate: DecimalField
    profit_factor: DecimalField
    total_trades: IntegerField
    composite_score: DecimalField
    trades_data: JSONField
    equity_curve: JSONField
```

## 4.4 20 Baseline Strategies

### Day Trading (7)
1. Opening Range Breakout (ORB)
2. VWAP Bounce
3. Gap and Go
4. Red to Green Move
5. 9 EMA Scalping
6. High of Day Breakout
7. Support/Resistance Reversal

### Swing Trading (7)
1. 20/50 EMA Crossover
2. RSI Oversold Bounce
3. Cup and Handle Pattern
4. Bollinger Band Squeeze
5. MACD Histogram Reversal
6. Weekly Breakout
7. Mean Reversion to 50 SMA

### Long-Term (6)
1. Graham Value Investing
2. Dividend Growth Strategy
3. Growth at Reasonable Price (GARP)
4. Dogs of the Dow
5. Momentum Factor Strategy
6. Small Cap Value

## 4.4 Plan Limits
- Basic ($15): No backtesting
- Premium ($25): 5 backtests/month

---

# PHASE 5: VALUE HUNTER PORTFOLIO ⏳ PENDING

## 5.1 Concept
Automated weekly portfolio that:
- Buys Monday at 9:35 AM ET
- Sells Friday at 3:55 PM ET
- Selects top 10 undervalued stocks by valuation score

## 5.2 Models
```python
class ValueHunterWeek:
    week_start: DateField
    week_end: DateField
    starting_capital: DecimalField
    ending_capital: DecimalField
    weekly_return: DecimalField
    benchmark_return: DecimalField
    alpha: DecimalField
    cumulative_return: DecimalField

class ValueHunterPosition:
    week: ForeignKey(ValueHunterWeek)
    symbol: CharField
    shares: DecimalField
    entry_price: DecimalField
    exit_price: DecimalField
    return_percent: DecimalField
```

---

# PHASES 6-10: SUMMARY

## Phase 6: Strategy Ranking System
- Composite scoring algorithm
- Leaderboard by category
- Clone strategy feature

## Phase 7: Educational Platform
- 5 course categories
- Interactive tooltips
- Trading glossary (200+ terms)

## Phase 8: Social & Viral Features
- Shareable charts/backtests
- Referral program
- Public profiles

## Phase 9: Retention Features
- Custom indicator builder
- Trading journal
- Tax reporting

## Phase 10: UI/UX & Rebrand
- New color palette
- Animation system
- Mobile optimization

---

# PRICING MODEL

| Feature | Basic ($15/mo) | Premium ($25/mo) |
|---------|----------------|------------------|
| Screeners | 5 saved | Unlimited |
| Alerts | 10 active | Unlimited |
| Watchlists | 3 | Unlimited |
| Chart Timeframes | 15m, 30m, 1H, 1D | All (1m-1D) |
| Drawing Tools | 5/chart | Unlimited |
| Indicators | 3/chart | 10/chart |
| Fundamentals | 10 metrics | 50+ metrics |
| Valuation Score | View only | Full breakdown |
| AI Backtesting | ❌ | 5/month |
| Value Hunter | Summary | Real-time |

---

# TECHNICAL STACK

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 + Tailwind CSS
- **Database:** SQLite (dev) / MySQL (prod)
- **AI:** Groq API (llama-3.3-70b-versatile)
- **Stock Data:** yfinance
- **Charts:** Lightweight Charts (TradingView)

---

# IMPLEMENTATION TIMELINE

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1-2 | Phase 1 | ✅ COMPLETE |
| 3-4 | Phase 2 | 🔄 Valuation Engine |
| 5-6 | Phase 3 | Advanced Charting |
| 7-8 | Phase 4 | AI Backtesting |
| 9-10 | Phase 5 | Value Hunter |
| 11-12 | Phase 6 | Strategy Ranking |
| 13-14 | Phase 7-8 | Education + Social |
| 15-16 | Phase 9-10 | Retention + Polish |

---

*Last Updated: December 2024*
