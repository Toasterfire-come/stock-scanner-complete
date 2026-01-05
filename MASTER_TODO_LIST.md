# Trade Scan Pro - Master TODO List
**Created:** January 3, 2026
**Priority Order:** P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low)
**Status Legend:** ⬜ Not Started | 🟨 In Progress | ✅ Complete

---

## ✅ Reality Check (Actual Repo Status)
**Last audited:** January 5, 2026

The repo already contains substantial implementation work that this checklist wasn’t reflecting. Highlights:
- ✅ **Social share buttons + share text + copy + basic event logging** are implemented in `frontend/src/pages/app/Backtesting.jsx`
- 🟨 **PNG image export** is implemented (via `html-to-image`), but size variants + QR-code export still need polish
- ✅ **Advanced metrics (Sortino/Calmar/Omega/VaR/CVaR/etc) + composite score + quality grade** are implemented (backend + UI)
- 🟨 **Achievements system** exists (backend + frontend components) and is returned by the backtest API, but the UI wiring still needs completing
- 🟨 **Public backtest share page** exists (`/share/backtest/:backtest_id`) but needs endpoint alignment + “public/private” model controls

---

## 🔥 PRIORITY 0 - CRITICAL (Launch Blockers)

### Viral Features - Week 1-2 (40 hours)

#### AI Backtester Social Sharing
- [x] **TICKET #1: Social Share Buttons** (8 hours) ✅ *(core implemented; QA polish remains)*
  - [x] Add Twitter/X share button with pre-filled text
  - [x] Add LinkedIn share button
  - [x] Add Reddit share button *(no subreddit selector yet)*
  - [x] Add "Copy Link" button with toast notification
  - [x] Implement `generateShareText()` function
  - [x] Track share events in analytics *(currently `logger.info(...)`; wire to product analytics if desired)*
  - [ ] Test all share buttons on mobile
  - [x] QA: Verify share text populates correctly

#### AI Backtester Image Export
- [ ] **TICKET #2: Image Export Feature** (16 hours) 🟨
  - [x] Install `html-to-image` dependency
  - [x] Install `qrcode.react` dependency *(installed; not yet used in export output)*
  - [x] Create exportable results card component (`resultsCardRef`)
  - [x] Add "Download as Image" button *(labeled “Export PNG”)*
  - [ ] Implement `exportAsImage()` function (1200x628px Twitter) *(currently exports the on-page results DOM; sizing presets still needed)*
  - [ ] Add Instagram variant (1080x1080px)
  - [x] Add Trade Scan Pro watermark to images *(text watermark exists; upgrade to stronger branding if desired)*
  - [ ] Add QR code linking to public results
  - [ ] Test image export on all browsers
  - [x] QA: Verify image quality (2x pixel ratio) *(uses `pixelRatio: 2`)*

#### Advanced Strategy Metrics
- [x] **TICKET #3: Advanced Metrics** (12 hours) ✅ *(implemented; a few planned items remain)*
  - [x] Backend: Add advanced metrics calculations *(implemented inside backtesting metrics pipeline)*
  - [x] Calculate Sortino Ratio
  - [x] Calculate Calmar Ratio
  - [x] Calculate Omega Ratio
  - [x] Calculate Value at Risk (VaR 95%)
  - [x] Calculate Conditional VaR (CVaR)
  - [x] Calculate Recovery Factor
  - [x] Calculate Avg Win/Loss Ratio *(avg win + avg loss + win/loss ratio derived)*
  - [x] Calculate Expectancy per trade
  - [x] Calculate Kelly Criterion %
  - [x] Calculate max win/loss streaks
  - [x] Calculate T-statistic & P-value
  - [ ] Calculate Alpha vs benchmark *(not implemented)*
  - [ ] Calculate Beta (volatility) *(not implemented)*
  - [x] Calculate Quality Score (0-100)
  - [ ] Frontend: Add "Advanced Metrics" tab *(currently rendered as sections in Results; optional to split into a dedicated tab)*
  - [ ] Add metric tooltips ("What does this mean?")
  - [ ] Add benchmark comparison table
  - [x] Add statistical significance indicator *(p-value + interpretation present)*
  - [ ] QA: Test with various strategy types

#### Analytics Setup
- [ ] **Analytics Tracking** (4 hours) 🟨
  - [ ] Install Mixpanel or Amplitude *(optional; repo already has Matomo proxy + structured logging + Sentry)*
  - [x] Track 'Backtest Shared' event *(currently logged via `logger.info(...)`)*
  - [x] Track 'Backtest Image Exported' event *(currently logged via `logger.info(...)`)*
  - [ ] Track 'Viral Signup' event (from shared links)
  - [ ] Set up conversion funnels
  - [ ] Create analytics dashboard
  - [ ] QA: Verify events fire correctly

---

## 🚀 PRIORITY 1 - HIGH (30-Day Launch Goals)

### Public Sharing & SEO - Week 3-4 (32 hours)

#### Public Backtest Pages
- [ ] **TICKET #4: Public Results Pages** (12 hours) 🟨
  - [ ] Backend: Add `is_public`, `share_slug` fields to Backtest model *(not present yet; current public page uses backtest id)*
  - [ ] Backend: Create `share_backtest()` endpoint
  - [x] Backend: Create public endpoint (no auth required) *(exists: `backtesting/public/<id>/`)*
  - [ ] Fix public share page API path alignment *(currently `PublicBacktestShare.jsx` fetches `/api/backtest/public/...` but backend exposes `/api/backtesting/public/...`)*
  - [ ] Backend: Add view count tracking
  - [x] Frontend: Create share route *(exists: `/share/backtest/:backtest_id`)*
  - [x] Frontend: Build public page *(exists: `frontend/src/pages/PublicBacktestShare.jsx`)*
  - [ ] Add "Make Public" toggle in Results tab
  - [ ] Add creator attribution (@username)
  - [ ] Add "Fork This Strategy" button
  - [x] Add CTA for non-logged-in users *(present on share page)*
  - [x] Add SEO meta tags (Open Graph, Twitter Card) *(present on share page)*
  - [ ] QA: Test public/private access controls *(needs model + enforcement)*

#### Achievement System
- [ ] **TICKET #5: Gamification - Badges** (12 hours) 🟨 *(system exists; UI wiring still needed)*
  - [x] Define 10 achievement types (First Steps, In the Green, etc.)
  - [x] Backend: Persist unlocked achievements *(Achievement model + migration present)*
  - [x] Backend: Create achievement check logic *(runs after backtest completion)*
  - [x] Frontend: Create achievement unlock notification *(component exists)*
  - [ ] Frontend: Add achievements display to profile *(component exists; not routed/embedded yet)*
  - [x] Add "Share Achievement" to Twitter/X *(supported in components + API)*
  - [ ] Create badge icons/graphics *(currently emoji-based; optional upgrade)*
  - [ ] QA: Test achievement unlock conditions + end-to-end UI flow

#### Leaderboards
- [ ] **TICKET #6: Strategy Leaderboards** (8 hours) 🟨 *(backend + page exist; routing + backtester integration still needed)*
  - [x] Backend: Create leaderboard query (top by return, Sharpe, etc.) *(exists: Strategy Ranking endpoints)*
  - [ ] Frontend: Add "Leaderboard" tab to Backtesting page
  - [ ] Add route/link to leaderboard page *(StrategyLeaderboard exists but is not currently routed in `App.js`)*
  - [x] Show Top strategies by timeframe *(backend supports timeframes; UI supports 1m/3m/6m/1y)*
  - [x] Add category filters *(UI supports Day/Swing/Long-Term)*
  - [x] Show fork/clone count per strategy *(backend exposes clone_count; UI shows popularity)*
  - [x] Add "Fork/Clone Strategy" action *(clone endpoint exists; UI includes clone action)*
  - [ ] QA: Verify leaderboard refresh + caching logic works as expected

### Content Marketing Start - Week 3-4 (20 hours)

#### Blog Content
- [ ] **Blog Setup** (4 hours)
  - [ ] Set up blog infrastructure (/blog route)
  - [ ] Create blog post template
  - [ ] Set up CMS (if needed) or Markdown files
  - [ ] Configure SEO for blog posts

- [ ] **Write 4 Blog Posts** (16 hours)
  - [ ] Post 1: "Top 10 Trading Strategies Backtested (AI Results)"
  - [ ] Post 2: "How to Beat the S&P 500: Data-Driven Analysis"
  - [ ] Post 3: "Day Trading vs Swing Trading: Which is More Profitable?"
  - [ ] Post 4: "Understanding Sharpe Ratio: A Beginner's Guide"
  - [ ] Publish all posts
  - [ ] Share on social media

#### Error Monitoring
- [ ] **Sentry/Rollbar Setup** (4 hours)
  - [ ] Install Sentry or Rollbar
  - [ ] Configure error tracking
  - [ ] Set up alerts for critical errors
  - [ ] Test error reporting
  - [ ] Create error dashboard

---

## 📊 PRIORITY 2 - MEDIUM (60-90 Day Goals)

### Network Effects - Month 2 (40 hours)

#### Strategy Forking
- [ ] **TICKET #7: Fork/Remix Strategies** (8 hours)
  - [ ] Backend: Add `forked_from` field to Backtest model
  - [ ] Backend: Create `fork_backtest()` endpoint
  - [ ] Frontend: Add "Fork Strategy" button
  - [ ] Pre-fill Create tab with forked strategy
  - [ ] Show attribution ("Inspired by @username")
  - [ ] Track fork count
  - [ ] QA: Test fork chain (fork of fork)

#### Comparison Mode
- [ ] **TICKET #8: Strategy Comparison** (12 hours)
  - [ ] Add "Select to Compare" checkboxes in History tab
  - [ ] Create comparison modal/page
  - [ ] Show side-by-side metrics
  - [ ] Overlay equity curves on same chart
  - [ ] Highlight winner for each metric
  - [ ] Add "vs Buy & Hold" comparison
  - [ ] Add "vs S&P 500" comparison
  - [ ] QA: Test with 2-4 strategies

#### Trading Journal Viral Features
- [ ] **Trading Journal Sharing** (8 hours)
  - [ ] Add "Share Monthly Performance" button
  - [ ] Generate shareable performance card
  - [ ] Export journal as PDF
  - [ ] Add achievement badges (100 trades, profitable month)
  - [ ] Add journal leaderboard (optional)

#### Portfolio Viral Features
- [ ] **Public Portfolio Pages** (8 hours)
  - [ ] Add "Make Public" toggle to portfolios
  - [ ] Create public portfolio page
  - [ ] Add performance badges
  - [ ] Show historical performance chart
  - [ ] Add "Clone Portfolio" button

#### Value Hunter Viral Features
- [ ] **Value Hunter Sharing** (4 hours)
  - [ ] Add "Share This Week's Picks" button
  - [ ] Create shareable image for weekly picks
  - [ ] Add historical track record display
  - [ ] Email digest for new weekly picks

### Additional Features - Month 2-3 (30 hours)

#### PDF Export
- [ ] **TICKET #9: PDF Report Generator** (12 hours)
  - [ ] Install jsPDF and html2canvas
  - [ ] Create PDF template
  - [ ] Add executive summary page
  - [ ] Add equity curve chart page
  - [ ] Add trade history table
  - [ ] Add disclaimer footer
  - [ ] Add "Download PDF" button
  - [ ] QA: Test PDF generation across browsers

#### Embed Widgets
- [ ] **TICKET #10: Embeddable Results** (8 hours)
  - [ ] Create embed endpoint (`/embed/backtest/:slug`)
  - [ ] Build mini results widget
  - [ ] Generate iframe embed code
  - [ ] Add "Embed" button with modal
  - [ ] Test iframe on external site
  - [ ] Add responsive sizing options

#### Challenge Mode
- [ ] **TICKET #11: Weekly Challenges** (10 hours)
  - [ ] Backend: Create Challenge model
  - [ ] Backend: Create challenge endpoints
  - [ ] Frontend: Add challenge card to Dashboard
  - [ ] Show current week's challenge
  - [ ] Show leaderboard for challenge
  - [ ] Add "Enter Challenge" flow
  - [ ] Award badges to winners

#### Viral Headlines
- [ ] **TICKET #12: Auto-Generated Headlines** (4 hours)
  - [ ] Create `generateViralHeadline()` function
  - [ ] Add suggested headline card in Results
  - [ ] Add "Copy Headline" button
  - [ ] Test headline variations
  - [ ] A/B test headline templates

---

## 🎨 PRIORITY 3 - LOW (Nice-to-Have)

### UX Improvements (20 hours)

#### Onboarding
- [ ] **Interactive Product Tour** (8 hours)
  - [ ] Install Intro.js or similar
  - [ ] Create step-by-step tour
  - [ ] Add tooltips for key features
  - [ ] Show on first login
  - [ ] Add "Skip Tour" option

#### Welcome Email Series
- [ ] **Email Onboarding** (6 hours)
  - [ ] Set up email service (SendGrid/Mailchimp)
  - [ ] Write 5-email welcome series
  - [ ] Day 1: Welcome + Quick Start
  - [ ] Day 3: Feature Deep Dive
  - [ ] Day 7: Success Stories
  - [ ] Day 14: Pro Plan Benefits
  - [ ] Day 30: Renewal Reminder

#### Mobile Optimizations
- [ ] **Mobile UX Polish** (6 hours)
  - [ ] Add bottom navigation for mobile
  - [ ] Optimize chart sizes for small screens
  - [ ] Add swipe gestures for charts
  - [ ] Test touch targets (min 44x44px)
  - [ ] Test on iOS Safari
  - [ ] Test on Android Chrome

### Testing & QA (30 hours)

#### Automated Testing
- [ ] **Unit Tests** (12 hours)
  - [ ] Set up Jest + React Testing Library
  - [ ] Write tests for Backtesting component
  - [ ] Write tests for share functions
  - [ ] Write tests for metric calculations
  - [ ] Aim for 60%+ code coverage

#### E2E Testing
- [ ] **End-to-End Tests** (10 hours)
  - [ ] Set up Playwright or Cypress
  - [ ] Write test: Complete backtest flow
  - [ ] Write test: Share to social media
  - [ ] Write test: Fork strategy
  - [ ] Write test: Public page access

#### Load Testing
- [ ] **Performance Testing** (8 hours)
  - [ ] Set up k6 or Artillery
  - [ ] Test 100 concurrent users
  - [ ] Test database under load
  - [ ] Optimize slow queries
  - [ ] Add caching layer if needed

### Infrastructure (20 hours)

#### Monitoring & Alerts
- [ ] **Uptime Monitoring** (4 hours)
  - [ ] Set up Pingdom or StatusPage
  - [ ] Monitor API endpoints
  - [ ] Monitor frontend uptime
  - [ ] Set up SMS/email alerts

#### Backup & Recovery
- [ ] **Disaster Recovery** (8 hours)
  - [ ] Set up automated database backups
  - [ ] Test backup restoration
  - [ ] Document recovery procedures
  - [ ] Set up point-in-time recovery

#### Performance Optimization
- [ ] **Speed Improvements** (8 hours)
  - [ ] Add Redis caching layer
  - [ ] Optimize database indices
  - [ ] Enable CDN for static assets
  - [ ] Implement code splitting
  - [ ] Lazy load heavy components

---

## 📱 FUTURE ROADMAP (6-12 Months)

### Mobile App Development (3-4 months, $30-50K)
- [ ] **React Native App**
  - [ ] iOS app development
  - [ ] Android app development
  - [ ] Push notifications
  - [ ] App store optimization
  - [ ] Beta testing
  - [ ] Launch on App Store & Google Play

### Marketplace (2-3 months, 80 hours)
- [ ] **Strategy Marketplace**
  - [ ] Backend: Create marketplace infrastructure
  - [ ] Frontend: Build marketplace UI
  - [ ] Payment processing (20% platform fee)
  - [ ] Seller verification
  - [ ] Rating/review system
  - [ ] Launch with 50+ strategies

### Enterprise Features (2-3 months, 60 hours)
- [ ] **White Label Platform**
  - [ ] Custom branding options
  - [ ] Subdomain configuration
  - [ ] Dedicated support tier
  - [ ] API rate limit increases
  - [ ] SLA guarantees

---

## 📊 SUCCESS METRICS TO TRACK

### Growth Metrics
- [ ] Weekly signups
- [ ] Free-to-paid conversion rate (target: 10-15%)
- [ ] Monthly recurring revenue (MRR)
- [ ] Customer acquisition cost (CAC)
- [ ] Lifetime value (LTV)
- [ ] LTV/CAC ratio (target: >3:1)

### Engagement Metrics
- [ ] Daily active users (DAU)
- [ ] Monthly active users (MAU)
- [ ] DAU/MAU ratio (target: >20%)
- [ ] Backtests run per user
- [ ] Feature adoption rates
- [ ] Session duration

### Viral Metrics
- [ ] Share rate (target: >15%)
- [ ] Viral coefficient (target: >0.3)
- [ ] Referral signups
- [ ] Public page views
- [ ] Social media mentions
- [ ] Content engagement

### Retention Metrics
- [ ] Monthly churn rate (target: <5%)
- [ ] 30/60/90-day retention
- [ ] Feature stickiness
- [ ] Reactivation rate

---

## 🎯 90-DAY MILESTONES

### Month 1 Goals
- ⬜ Complete Priority 0 features (viral basics)
- ⬜ Launch analytics tracking
- ⬜ Publish 4 blog posts
- ⬜ Achieve 500 signups
- ⬜ Achieve 50 paid users
- ⬜ Reach $1,250 MRR
- ⬜ 15% share rate on backtests

### Month 2 Goals
- ⬜ Complete Priority 1 features (public pages, gamification)
- ⬜ Launch leaderboards
- ⬜ Launch achievement system
- ⬜ Create 4 more blog posts
- ⬜ Record 2 YouTube videos
- ⬜ Achieve 750 signups
- ⬜ Achieve 90 paid users
- ⬜ Reach $2,475 MRR

### Month 3 Goals
- ⬜ Complete Priority 2 features (network effects)
- ⬜ Launch strategy forking
- ⬜ Launch comparison mode
- ⬜ Launch weekly challenges
- ⬜ Achieve 1,125 signups
- ⬜ Achieve 146 paid users
- ⬜ Reach $4,220 MRR
- ⬜ Viral coefficient >0.3

---

## 📝 NOTES & DEPENDENCIES

### Technical Dependencies
- **Frontend:**
  - html-to-image (for image export)
  - qrcode.react (for QR codes)
  - jspdf + html2canvas (for PDF export)
  - Mixpanel or Amplitude (for analytics)
  - Sentry or Rollbar (for error tracking)
  - Intro.js (for product tour)

- **Backend:**
  - Redis (for caching - optional)
  - Celery (for async tasks - if needed)
  - SendGrid or Mailchimp (for emails)

### Resource Requirements
- **Development:**
  - 2 full-stack engineers
  - 1 designer (part-time)
  - 1 content writer (part-time)

- **Timeline:**
  - Priority 0: 1-2 weeks (40 hours)
  - Priority 1: 3-4 weeks (52 hours)
  - Priority 2: 6-8 weeks (70 hours)
  - Total: ~12 weeks to complete all P0-P2

### Budget Estimate
- Development (162 hours @ $100/hr): $16,200
- Design work (20 hours @ $80/hr): $1,600
- Content creation (40 hours @ $50/hr): $2,000
- Infrastructure/tools: $500/month
- **Total:** ~$20K one-time + $500/month ongoing

### ROI Calculation
- Investment: $20K
- Month 1 return: +$849 MRR = $10,188 ARR
- Month 12 return: +$15-25K MRR = $180-300K ARR
- **Payback period:** 2-3 months
- **12-month ROI:** 900-1,500%

---

## ✅ COMPLETION TRACKING

**Overall Progress:**
- Priority 0: ✅✅🟨🟨 50% (2/4 core tickets complete; 2 in progress)
- Priority 1: 🟨⬜⬜⬜⬜⬜⬜ 14% (1/7 started; several partially implemented)
- Priority 2: ⬜⬜⬜⬜⬜⬜⬜⬜ 0% (0/8 tasks)
- Priority 3: ⬜⬜⬜⬜ 0% (0/4 tasks)

**Last Updated:** January 5, 2026
**Next Review:** Weekly sprint planning
**Owner:** Development Team Lead
**Status:** 🟨 In progress (P0 underway)

---

## 🚀 QUICK START GUIDE

**To begin implementation:**

1. **Week 1 Sprint:** Focus on TICKET #1 (Social Sharing)
   - Assign to frontend developer
   - 8-hour estimate
   - High impact, quick win

2. **Week 1-2 Sprint:** Simultaneously work on TICKET #3 (Advanced Metrics)
   - Assign to backend + frontend developers
   - 12-hour estimate
   - User requested feature

3. **Week 2 Sprint:** Complete TICKET #2 (Image Export)
   - Assign to frontend developer
   - 16-hour estimate
   - Highest viral potential

4. **Review & Iterate:** After Priority 0 completion
   - Analyze share rate data
   - Gather user feedback
   - Adjust Priority 1 based on learnings

**Sprint Velocity Target:** 40 hours/week (2 developers @ 20 hours each)
**Estimated Timeline:** Priority 0 complete in 2 weeks

---

**END OF MASTER TODO LIST**
