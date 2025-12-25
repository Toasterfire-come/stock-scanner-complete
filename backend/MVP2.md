---

## SUBSCRIPTION TIERS (FRONTEND-HANDLED SIGNUP)
=======
**Note:** See [MVP2_STATUS_ANALYSIS.md](MVP2_STATUS_ANALYSIS.md) for detailed evidence of completion.

---

## 🚀 WHAT'S NEXT (PRIORITY ORDER)

### Priority 1: Frontend UI Implementation (IN PROGRESS)
- ✅ Paper Trading UI components created
- ✅ SMS Alerts UI components created
- ✅ Two-Factor Authentication UI components created
- ⏳ Backend API integration and testing
- ⏳ Real-time updates and advanced features

### Priority 2: Options Analytics (intraday chains, Greeks, IV surfaces) ✅ COMPLETED
- ✅ Database models created (OptionsChain, OptionContract, VolatilitySurface, OptionsAnalytics)
- ✅ Management command for intraday options data fetching with Greeks calculation
- ✅ Support for delta, gamma, theta, vega, rho, implied volatility
- ✅ Options chain statistics and analytics (put-call ratio, max pain, skew analysis)

### Priority 3: News & Sentiment System (real-time ingestion, NLP analysis) ✅ COMPLETED
- ✅ Comprehensive news models (NewsArticle, NewsSource, NewsRealtimeFeed, NLP analysis models)
- ✅ Real-time ingestion from WebSocket, RSS, API, and web scraping feeds
- ✅ NLP processing with sentiment analysis (VADER), topic classification, entity extraction
- ✅ Keyword analysis, ticker extraction, and relevance scoring
- ✅ Management command for automated news processing and analysis

### Priority 4: Exotic Chart Types (Renko, Kagi, P&F, Heikin-Ashi)

### Priority 5: Strategy Ranking & Leaderboards (Phase 6)

### Priority 6: Trading Journal (Phase 9)

### Priority 7: Social Features (Phase 8)

---

## SUBSCRIPTION TIERS (FRONTEND-HANDLED SIGNUP)
---

## SUBSCRIPTION TIERS (FRONTEND-HANDLED SIGNUP)

| Tier | Price | Intended User |
|---|---|---|
| **Basic** | $9.99 / month | Analysis, learning, manual trading |
| **Pro** | $24.99 / month | Strategy builders, active traders |


---

## DATA ORIGIN & FLOW (STRICT RULES)

### Charting
- **Source:** Stooq  
- **Method:** Pulled directly from the **user’s browser**
- **Charts:** All Stooq charts, **HTML-modified**, no server relay

### Analytics / Storage
- **Source:** yfinance
- **Method:** Server-side ingestion → database
- **Frequencies:**
  - 1-minute hybrid updater
  - Daily updater
- **Used for:**
  - Screeners
  - Valuation models
  - Backtests
  - Strategy scoring
  - Options analytics
  - Journals & performance reviews

---

## ALERTING (FINAL)

- ❌ No email alerts anywhere
- ✅ SMS only (Self-Hosted Multi Attempt TextBelt)
- ✅ SMS via **free API requiring no signup**
- ✅ Webhooks supported
- ✅ Single & multi-condition alerts

---

## CORE FEATURE INVENTORY (CONFIRMED INCLUDED)

### Charting & Technical Analysis
- Exotic chart types:
  - Renko
  - Kagi
  - Point & Figure
  - Heikin-Ashi
- Volume Profile (support & resistance via volume)
- Automated technical summaries:
  - SMA
  - RSI
  - MACD
  - Clear bullish / neutral / bearish implications
- Customizable chart layouts:
  - Save / load indicators
  - Drawings
  - Settings

### Market Intelligence
- Real-time news ingestion
- NLP sentiment analysis
- News filtering:
  - By ticker
  - By sentiment
  - By category
- Economic calendar:
  - Earnings
  - Fed decisions
  - Macro releases
  - Events displayed directly on charts

### Fundamentals & Options
- Standardized financial statements
- Intraday options chains
- Greeks
- Implied volatility surfaces

### UX / UI
- Modular dashboard (drag & drop widgets)
- Responsive design (desktop, tablet, mobile)
- Full mobile charting
- Clean data tables (high-performance rendering)
- Clean charts with readable data points
- Contextual help:
  - Tooltips
  - Guided tours
- Extensive knowledge base & FAQs
- Clear CTAs
- Intuitive navigation
- Streamlined UI elements

### Performance & Security
- Optimized API endpoints
- Aggressive caching
- Load testing for concurrency
- CDN for static assets
- MFA
- Encryption at rest & in transit

---

## PAPER TRADING SYSTEM (NEW — REQUIRED)

### Purpose
Allow users to practice, test strategies, and validate setups without capital risk, directly tied into analytics and retention loops.

### Architecture
- Separate **paper trading ledger** (never mixed with live data)
- Uses:
  - Stooq browser charts (visual reference)
  - yfinance database prices (execution simulation)
- Deterministic fills:
  - Configurable slippage
  - Spread simulation
  - Latency simulation (Pro)

### Features
- Virtual starting balance (configurable)
- Supports:
  - Market orders
  - Limit orders
  - Stop orders
  - **Advanced order types**:
    - Bracket orders
    - OCO
    - Trailing stop-loss
- Strategy-based paper trades
- Manual paper trades
- Performance tracking:
  - P&L
  - Drawdowns
  - Win rate
  - Risk metrics

### Tier Access
- **Basic:** Manual paper trading only
- **Pro:** Strategy-driven paper trading + analytics

### Retention Impact
- Reduces fear of usage
- Encourages experimentation
- Anchors users via performance history

---

## SUBSCRIPTION FEATURE MAPPING

### BASIC — $9.99

Included:
- Stooq charting (standard + volume profile view)
- Core indicators
- Automated technical summaries
- Financial statements
- News + sentiment
- Economic calendar
- Manual paper trading
- Single-condition SMS alerts
- Mobile chart viewing
- Education & help
- Security features

Excluded:
- Exotic charts
- Saved layouts
- Strategy backtesting
- Strategy cloning
- Options analytics
- Advanced orders
- Multi-condition alerts
- Copy trading

---

### PRO — $24.99

Everything in Basic **plus**:
- All exotic chart types
- Saved chart layouts
- Modular dashboards
- AI backtesting
- Composite strategy scoring
- Leaderboards
- Strategy cloning
- Full paper trading (strategy + advanced orders)
- Intraday options analytics
- Multi-condition SMS alerts
- Follow & copy traders
- Trading journal
- Performance reviews
- Custom themes

---

# PHASE EXECUTION PLAN (6–10)

---

## PHASE 6 — STRATEGY RANKING & SCORING

**Includes**
- Composite scoring engine
- Normalized metrics
- Category leaderboards
- Anti-overfitting controls
- Strategy cloning

**Why**
- Monetization leverage
- Competitive engagement
- Trustworthy rankings

---

## PHASE 7 — EDUCATION & CONTEXT

**Includes**
- Structured learning paths
- Indicator explanations
- Inline tooltips
- Feature walkthroughs
- Knowledge base

**Why**
- Lowers onboarding friction
- Increases feature adoption

---

## PHASE 8 — SOCIAL & COPY TRADING

**Includes**
- Public profiles (opt-in)
- Strategy sharing
- Copy trading (paper & live-ready)
- Referral tracking

**Why**
- Network effects
- Organic growth

---

## PHASE 9 — RETENTION & HABITS

**Includes**
- Trading journal
- Monthly performance reviews
- Emotional tagging
- Custom indicators
- Exports & tax prep

**Why**
- Deep user attachment
- Churn reduction

---

## PHASE 10 — POLISH, SCALE & TRUST

**Includes**
- Modular dashboards
- Advanced chart UX
- Mobile parity
- Performance tuning
- Security hardening
- CTA clarity
- Navigation simplification

**Why**
- Professional credibility
- Scalability
- Conversion optimization

## Phase 11 - Proper Setup

**Includes**
- Proper Docker Container Setup for Lunix
- Clean Repo Remove Clutter
- Proper Load Balancer with plug and play for multiple instances around the world
- Clean path to start including all nessesary tems, like a data base setp script, tunnel setup script, and test scripts that help trubbleshoot
- 10-30 min setup after clone

---

## FINAL NOTES

- All listed features above are **explicitly included**
- All charts originate from **Stooq via browser**
- All analytics originate from **database-stored yfinance**
- Repo remains clean and clutter free
- No email alerts under any circumstance
- Paper trading is a first-class system
- Design remains color-agnostic and professional

Ensure proper dherince to this file and QA-Frontend.md. Test backend and do visual/static testing of the frontend to ensure quality and production readyness. Identify issues as a non-Biased 3rd party for both the frontend and backend. Ensure proper connection between them. Verify both backend and frontend ready for production and have been fully updated in claims, visuals, and in processes to 
---

**This document is the authoritative execution blueprint for MVP2.**
