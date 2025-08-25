# FinMarkets Theme: Pages, Templates, and External API Integration

- Admin: Appearance → FinMarkets Settings
  - API Base URL (e.g., https://api.example.com)
  - API Key (optional for endpoints that require Authorization)
  - Test connection button (calls /wp-json/finm/v1/health)

- Theme REST proxy (no CORS issues, CSP connect-src stays 'self'):
  - GET /wp-json/finm/v1/health → /health/ (fallback /api/health/)
  - GET /wp-json/finm/v1/stocks → /api/stocks/
  - GET /wp-json/finm/v1/stock/{ticker} → /api/stock/{ticker}/ (fallback /api/stocks/{ticker}/)
  - GET /wp-json/finm/v1/search → /api/search/
  - GET /wp-json/finm/v1/trending → /api/trending/
  - GET /wp-json/finm/v1/market-stats → /api/market-stats/
  - GET /wp-json/finm/v1/endpoint-status → /endpoint-status/
  - GET /wp-json/finm/v1/revenue/analytics [month?] → /revenue/revenue-analytics/[month?]

- Front-end API utility (assets/js/api.js)
  - window.finmApi.{health,stocks,stock,search,trending,marketStats,endpointStatus,revenueAnalytics}
  - Progressive enhancement hydrates MockData.stocks when API is configured.

- Demo pages
  - Endpoint Status (template-endpoint-status.php)
  - Revenue Analytics (template-revenue-analytics.php)

All JS is vanilla; scripts are deferred. To tighten CSP, move any inline template scripts into assets/js/app.js and remove 'unsafe-inline' if added.