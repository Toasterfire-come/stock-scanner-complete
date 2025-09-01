# Backend-Frontend Integration Contracts (Retail Trade Scanner)

Purpose: Minimal but production-friendly API contracts to power v1 without frontend mocks. All routes are mounted under /api to satisfy ingress rules.

Base URLs
- Backend base: {REACT_APP_BACKEND_URL}
- API prefix: /api
- Revenue prefix: /api/revenue

Auth
- Scheme: Bearer JWT in Authorization header: Bearer &lt;token&gt;
- Login: POST /api/auth/login/
  - body: { username: string, password: string }
  - resp: { success, data: { user_id, username, email, first_name, last_name, is_premium, last_login }, message, token }
- Logout: POST /api/auth/logout/
- Me (profile): GET /api/user/profile/ (auth)
- Update profile: POST /api/user/profile/ (auth)
- Change password: POST /api/user/change-password/ (auth)

Health & Meta
- GET /api/ -> { status: "ok", message }
- GET /api/health/ -> { status, database, version, timestamp, endpoints, features }

Stocks
- GET /api/stocks/ (filters: limit, search, category, min_price, max_price, min_volume, min_market_cap, max_market_cap, min_pe, max_pe, exchange, sort_by, sort_order)
- GET /api/stock/{ticker}/ (alias: /api/stocks/{ticker}/)
- GET /api/search/?q=string
- GET /api/trending/ -> { high_volume, top_gainers, most_active, last_updated }
- GET /api/market-stats/

Alerts
- GET /api/alerts/create/ -> meta describing POST contract
- POST /api/alerts/create/ -> creates alert, returns { alert_id, message, details }

Subscriptions
- POST /api/subscription/ and /api/wordpress/subscribe/

Billing
- GET /api/user/billing-history/ (auth, pagination)
- GET /api/billing/current-plan/ (auth)
- POST /api/billing/change-plan/ (auth)
- GET /api/billing/stats/ (auth)

Notifications
- GET/POST /api/user/notification-settings/ (auth)
- GET /api/notifications/history/ (auth)
- POST /api/notifications/mark-read/ (auth)

Watchlist
- GET /api/watchlist/ (auth)
- POST /api/watchlist/add/ (auth)
- DELETE /api/watchlist/{item_id}/ (auth)

Portfolio
- GET /api/portfolio/ (auth)
- POST /api/portfolio/add/ (auth)
- DELETE /api/portfolio/{holding_id}/ (auth)

News (App)
- GET /api/news/feed/ (auth)
- POST /api/news/mark-read/ (auth)
- POST /api/news/mark-clicked/ (auth)
- POST /api/news/preferences/ (auth)
- POST /api/news/sync-portfolio/ (auth)

Revenue (mounted at /api/revenue/...)
- POST /api/revenue/validate-discount/
- POST /api/revenue/apply-discount/
- POST /api/revenue/record-payment/
- GET /api/revenue/revenue-analytics/ (and /{month_year}/)
- POST /api/revenue/initialize-codes/
- GET /api/revenue/monthly-summary/{month_year}/ (auth scope: staff_only - simulated)

Data Model (MongoDB)
- users { id, username, email, password_hash, first_name, last_name, phone, company, is_premium, plan: { plan_type, billing_cycle, features }, last_login, date_joined }
- stocks { ticker, symbol, company_name, exchange, current_price, price_change_today, change_percent, volume, market_cap, last_updated, currency, price_history[], pe_ratio, dividend_yield }
- alerts { id (seq), user_id? (optional), ticker, target_price, condition, email, created_at }
- subscriptions { email, category, is_active, created_at }
- watchlist { id, user_id, symbol, company_name, current_price, price_change, price_change_percent, volume, market_cap, watchlist_name, notes, alert_price, added_date }
- portfolio { id, user_id, symbol, shares, avg_cost, current_price, total_value, gain_loss, gain_loss_percent, portfolio_name, added_date }
- notifications_settings { user_id, trading{}, portfolio{}, news{}, security{} }
- notifications { id, user_id, title, message, type, is_read, created_at, read_at, metadata }
- billing_history { id, user_id, date, description, amount, status, method, download_url }
- revenue_codes { code, discount_percentage, description, active }
- revenue_records { id, user_id, amount, discount_code, original_amount, discount_amount, final_amount, commission_amount, revenue_type, payment_date, month_year }
- counters { name, seq }

Frontend Integration Notes
- Use process.env.REACT_APP_BACKEND_URL + "/api" for all calls (already configured). No hardcoding URLs or ports.
- Include Authorization header with Bearer token for auth routes.
- File uploads not in v1.

Mocking
- None on frontend. Backend seeds example stocks on startup if empty to ensure UI has data. This is not a mock layer; it persists in MongoDB.