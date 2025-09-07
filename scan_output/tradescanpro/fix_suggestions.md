# Fix suggestions for tradescanpro

## Errors detected

Broken pages or assets (HTTP >= 400):

- asset -> https://fonts.googleapis.com (code: 404)
- asset -> https://fonts.gstatic.com (code: 404)
- asset -> https://www.paypalobjects.com (code: 403)
- page -> https://tradescanpro.com/alerts/create/ (code: 500)
- page -> https://tradescanpro.com/api (code: 404)
- page -> https://tradescanpro.com/api/event (code: 404)
- page -> https://tradescanpro.com/api/logs/security/ (code: 404)
- page -> https://tradescanpro.com/app/ (code: 500)
- page -> https://tradescanpro.com/app/dashboard (code: 500)
- page -> https://tradescanpro.com/apply-discount/ (code: 500)
- page -> https://tradescanpro.com/app/market-heatmap (code: 500)
- page -> https://tradescanpro.com/app/markets (code: 500)
- page -> https://tradescanpro.com/app/news (code: 500)
- page -> https://tradescanpro.com/app/top-movers (code: 500)
- page -> https://tradescanpro.com/auth (code: 500)
- page -> https://tradescanpro.com/auth/login (code: 500)
- page -> https://tradescanpro.com/auth/login/ (code: 500)
- page -> https://tradescanpro.com/auth/logout/ (code: 500)
- page -> https://tradescanpro.com/auth/register (code: 500)
- page -> https://tradescanpro.com/auth/register/ (code: 500)
- page -> https://tradescanpro.com/auth/sign-in (code: 500)
- page -> https://tradescanpro.com/billing/change-plan/ (code: 500)
- page -> https://tradescanpro.com/billing/current-plan/ (code: 500)
- page -> https://tradescanpro.com/billing/download/ (code: 500)
- page -> https://tradescanpro.com/billing/history/ (code: 500)
- page -> https://tradescanpro.com/billing/stats/ (code: 500)
- page -> https://tradescanpro.com/docs (code: 500)
- page -> https://tradescanpro.com/endpoint-status/ (code: 500)
- page -> https://tradescanpro.com/health/ (code: 500)
- page -> https://tradescanpro.com/initialize-codes/ (code: 500)
- page -> https://tradescanpro.com/legal/privacy (code: 500)
- page -> https://tradescanpro.com/legal/terms (code: 500)
- page -> https://tradescanpro.com/logs/client/ (code: 403)
- page -> https://tradescanpro.com/market-stats/ (code: 500)
- page -> https://tradescanpro.com/news/feed/ (code: 500)
- page -> https://tradescanpro.com/news/mark-clicked/ (code: 500)
- page -> https://tradescanpro.com/news/mark-read/ (code: 500)
- page -> https://tradescanpro.com/portfolio/add/ (code: 500)
- page -> https://tradescanpro.com/portfolio/ (code: 500)
- page -> https://tradescanpro.com/pricing (code: 500)
- page -> https://tradescanpro.com/realtime/ (code: 500)
- page -> https://tradescanpro.com/record-payment/ (code: 500)
- page -> https://tradescanpro.com/revenue-analytics/ (code: 404)
- page -> https://tradescanpro.com/revenue (code: 404)
- page -> https://tradescanpro.com/_root.data (code: 500)
- page -> https://tradescanpro.com/search/ (code: 500)
- page -> https://tradescanpro.com/statistics/ (code: 500)
- page -> https://tradescanpro.com/stock/ (code: 500)
- page -> https://tradescanpro.com/stocks/ (code: 500)
- page -> https://tradescanpro.com/trending/ (code: 500)
- page -> https://tradescanpro.com/user/change-password/ (code: 500)
- page -> https://tradescanpro.com/user/notification-settings/ (code: 500)
- page -> https://tradescanpro.com/validate-discount/ (code: 500)
- page -> https://tradescanpro.com/watchlist/add/ (code: 500)
- page -> https://tradescanpro.com/watchlist/ (code: 500)

## Redirected URLs

Update references from old URL to final URL to avoid runtime redirects:

- https://o.sentry.io -> https://o.sentry.io/auth/login/o/
- https://www.paypal.com -> https://www.paypal.com/us/home

## Mixed content candidates (http assets on https pages)

- None found

## Suggestions

- Replace references to redirected URLs with their final destinations.
- Switch http asset links to https if the resource is available over https.
- Fix or remove links to resources returning 404/410. Verify paths and filenames.
- Ensure the server returns proper 200/301 for canonical routes; avoid redirect chains (>1 hop).

## Replacement map (auto-fixable)

The following pairs can be safely replaced in source code (left -> right):

- https://o.sentry.io -> https://o.sentry.io/auth/login/o/
- https://www.paypal.com -> https://www.paypal.com/us/home

For http->https upgrades, validate availability first.
