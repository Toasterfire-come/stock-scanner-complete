Trade Scan Pro — User Experience & Feature Overview (Internal Sponsorship Brief)

Date: 2025-10-07
Audience: Internal; sponsors and partners evaluating user experience, plans, onboarding, and monetization.

### 1) Product overview
- Trade Scan Pro is a professional trading platform for screening stocks, real-time alerts, portfolio analytics, and market research.
- Core value: Fast discovery of trade ideas with configurable screeners, alerting, and analytics; clear upgrade path from a free tier to paid plans.

### 2) Plans and core capabilities
- Free: 15 monthly stock queries; basic filters; 1 portfolio; no alerts/watchlists.
- Bronze ($24.99/mo): 1,500 monthly API calls; advanced screening; 50 alerts; 2 watchlists.
- Silver ($49.99/mo): 5,000 monthly API calls; advanced tools; 100 alerts; 10 watchlists; 1 portfolio.
- Gold ($89.99/mo): Unlimited API calls; all features; developer tools; white-label options (for enterprise use cases).
- Annual billing offers ~15% savings; 7‑day $1 trial via code TRIAL across paid plans.

Plan limits (client guard; server is source of truth): Free 30 calls/mo; Bronze 1,500; Silver 5,000; Gold unlimited.

### 3) End-to-end user journey
This section maps the actual UI components and backend endpoints used in our codebase.

3.1 Entry and discovery
- Key routes: `/features`, `/pricing`, marketing pages, and docs (`/docs`). Primary CTA: Try Now for Free → `/auth/sign-up`.

3.2 Account creation (Sign Up)
- Route: `/auth/sign-up` (`frontend/src/pages/auth/SignUp.jsx`).
- Fields: firstName (required), lastName (optional), username (optional/auto‑derived from email), email, password/confirm, Terms acceptance.
- Social sign-in: Google (button) and Google One‑Tap; back end paths: `/auth/google/login`, `/auth/google/onetap`.
- Referral capture: from URL path `/auth/sign-up/ref-<CODE>` and from `?ref=<CODE>` (and robust parsing of other query keys via `REACT_APP_REFERRAL_QUERY_KEYS`).
- API: POST `/api/auth/register/` (client helper `registerUser`). On success, auto‑login attempt then redirect to Plan Selection.

3.3 Email verification
- Route: `/auth/verify-email` (`VerifyEmail.jsx`). Accepts `?token=...` and simulates verification + resend. Successful verification redirects to sign‑in. Users can also proceed on Free.

3.4 Sign-in
- Route: `/auth/sign-in` (`SignIn.jsx`). Username/email + password; on success, redirect to `/app/dashboard` (or requested `redirect`).

3.5 Two-Factor Authentication (2FA)
- Route: `/auth/2fa` (`TwoFactorAuth.jsx`). 6‑digit code input. Endpoints: `/auth/verify-2fa/`, `/auth/resend-2fa/`.

3.6 Plan selection (post‑signup)
- Route: `/auth/plan-selection` (`PlanSelection.jsx`).
- Shows Bronze/Silver/Gold and Free with monthly vs annual toggle. Detects referral and surfaces a TRIAL banner.
- Free → `/app/dashboard`. Paid → `/checkout` with plan, cycle, and referral/discount passed as state.

3.7 Checkout (PayPal)
- Route: `/checkout` (`Checkout.jsx`). Works for unauthenticated visitors to allow price/PayPal init.
- Loads pricing meta from `/api/billing/plans-meta/` (fallback local meta when unavailable).
- Promo/referral codes: input with sanitation; apply via POST `/api/billing/apply-discount/`.
- Payment: `PayPalCheckout` (env or meta plan IDs). On success → `/checkout/success`; on error → `/checkout/failure`.
- Env for PayPal plans (fallback/local):
  - `REACT_APP_PAYPAL_PLAN_BRONZE_MONTHLY`, `REACT_APP_PAYPAL_PLAN_BRONZE_ANNUAL`
  - `REACT_APP_PAYPAL_PLAN_SILVER_MONTHLY`, `REACT_APP_PAYPAL_PLAN_SILVER_ANNUAL`
  - `REACT_APP_PAYPAL_PLAN_GOLD_MONTHLY`, `REACT_APP_PAYPAL_PLAN_GOLD_ANNUAL`

3.8 Post‑purchase confirmation
- Route: `/checkout/success` (`CheckoutSuccess.jsx`). Updates client user plan, tracks purchase, links to docs and account billing.
- Failure handling: `/checkout/failure` (`CheckoutFailure.jsx`) with common issues and quick actions.

3.9 Onboarding
- Route: `/onboarding` (`OnboardingWizard.jsx`). Multi‑step profile/preferences collection for personalization (currently client‑side; not persisted by default).

3.10 First‑run application
- Key app routes: `/app/markets`, `/app/alerts`, `/app/watchlists`, `/app/portfolio`, `/app/screeners`, `/app/news`.
- Data endpoints include: `/api/trending/`, `/api/market-stats/`, `/api/stocks/…`, `/api/filter/` (see `frontend/src/api/client.js`).

### 4) Account, billing, and notifications
- Current plan: `/account/plan` (`CurrentPlan.jsx`), API `/api/billing/current-plan/`, change via `/api/billing/change-plan/`, usage via `/api/usage/`.
- Billing history: `/account/billing` (`BillingHistory.jsx`), APIs: `/api/billing/history/`, `/api/billing/stats/`, invoices `/api/billing/download/{id}/`.
- Payment method update: `/api/user/update-payment/` (UI shows placeholder card details; integrate with billing portal in production).
- Profile: `/account/profile` (`Profile.jsx`), reads `/api/user/profile/`; update not supported yet (client returns not supported).
- Notification settings: `/account/notifications` (`NotificationSettings.jsx`) using `/api/user/notification-settings/`.

### 5) Feature set (user‑facing)
- Screening and filters: real‑time market data, advanced filtering, screener templates, exports (CSV).
- Alerts: price/volume/indicator triggers; alert history; notifications via email.
- Watchlists: create, add/remove stocks; sharing and public links supported via `/api/share/*` endpoints.
- Portfolio analytics: performance, sector allocation, dividend tracking.
- News feed: personalized news, preferences, read/click analytics.
- Developer tools (Gold): API keys, usage stats, documentation endpoints.

### 6) Enterprise & white‑label
- Quote Request: `/enterprise/quote-request` with options including SSO Integration, white‑label, real‑time data, custom integrations; submits to `/api/enterprise/quote-request/`.
- White‑Label configuration (Gold): `/enterprise/white-label` (`WhiteLabelConfig.jsx`), load `/api/white-label/configurations/`, save `/api/white-label/configurations/create/`. Supports custom branding, domain (CNAME → `platform.retailtradescanner.com`), CSS/JS.
- SSO: Exposed as an enterprise feature option; implementation delivered through enterprise engagement.

### 7) Payments, discounts, and referrals
- TRIAL code: 7‑day trial for $1 on paid plans.
- Referral codes: auto‑detected from `?ref=` or configured query keys (`REACT_APP_REFERRAL_QUERY_KEYS`) and `utm_source` patterns; applied at Plan Selection and Checkout.
- PayPal checkout via backend endpoints: create/capture order; backend docs also include webhook handling (signature verification) for reliability.

### 8) Security, auth, and privacy
- Authentication: Bearer token attached by Axios interceptor from `localStorage` (`rts_token`).
- CSRF: `csrftoken` cookie supported; `X‑CSRFToken` header injected for mutating requests.
- SSO (enterprise) available via custom integration.
- Client observability: Sentry initialized when `REACT_APP_SENTRY_DSN` is set; request headers and cookies redacted; user PII minimized. Increased sampling for `login` and `checkout` transactions.
- Rate limits (client guard): free 30/mo; bronze 1,500; silver 5,000; gold unlimited. Server‑side enforcement authoritative.

### 9) Analytics and instrumentation
- Client metric logging: POST `/api/logs/metrics/` (e.g., `checkout_success`/`checkout_error`).
- Client error logging: POST `/api/logs/client/` with timestamp and path.
- Purchase tracking on success page with `trackEvent('purchase', …)` for analytics systems.

### 10) Quick index (routes and endpoints)
- User auth routes: `/auth/sign-up`, `/auth/sign-in`, `/auth/verify-email`, `/auth/2fa`, `/auth/plan-selection`, `/checkout`, `/checkout/success`, `/checkout/failure`.
- Account routes: `/account/plan`, `/account/billing`, `/account/profile`, `/account/notifications`.
- Enterprise routes: `/enterprise/quote-request`, `/enterprise/white-label`.
- Selected APIs used (prefixed with `/api`):
  - Auth: `/auth/register/`, `/auth/login/`, `/auth/logout/`, `/auth/csrf/`, `/auth/verify-2fa/`, `/auth/resend-2fa/`
  - Billing: `/billing/plans-meta/`, `/billing/apply-discount/`, `/billing/create-paypal-order/`, `/billing/capture-paypal-order/`, `/billing/history/`, `/billing/current-plan/`, `/billing/change-plan/`, `/billing/stats/`, `/billing/download/{id}/`
  - White‑Label: `/white-label/configurations/`, `/white-label/configurations/create/`
  - Enterprise: `/enterprise/quote-request/`
  - Usage/Status: `/usage/`, `/status/`, `/health/`
  - Market data: `/trending/`, `/market-stats/`, `/stocks/…`, `/filter/`

— End of document —

