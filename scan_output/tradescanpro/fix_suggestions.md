# Fix suggestions for tradescanpro

## Errors detected

Broken pages or assets (HTTP >= 400):

- asset -> https://fonts.googleapis.com (code: 404)
- asset -> https://fonts.gstatic.com (code: 404)
- asset -> https://www.paypalobjects.com (code: 403)
- page -> https://tradescanpro.com/app/dashboard (code: 500)
- page -> https://tradescanpro.com/app/market-heatmap (code: 500)
- page -> https://tradescanpro.com/app/markets (code: 500)
- page -> https://tradescanpro.com/app/news (code: 500)
- page -> https://tradescanpro.com/app/top-movers (code: 500)
- page -> https://tradescanpro.com/docs (code: 500)
- page -> https://tradescanpro.com/legal/privacy (code: 500)
- page -> https://tradescanpro.com/legal/terms (code: 500)
- page -> https://tradescanpro.com/pricing (code: 500)

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
