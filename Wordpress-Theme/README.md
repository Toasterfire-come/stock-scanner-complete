# FinMarkets WordPress Theme (Teaser Build)

What you have now
- A new theme folder at Wordpress-Theme/finmarkets with:
  - style.css (theme header + design system, Inter, color palette, responsive)
  - functions.php (enqueue Inter + style.css, mock.js with defer, basic security headers)
  - index.php (demo homepage with hero, screener, watchlist, news, pricing)
  - assets/js/mock.js (mock datasets for stocks and news)

Notes
- 100% vanilla JS. No jQuery. All interactions run in the browser and save to localStorage.
- This is MOCKED data only. No payment processing, no live quotes yet.

How to install
1) Zip the finmarkets directory and upload in WordPress: Appearance ➜ Themes ➜ Add New ➜ Upload.
2) Activate the theme and visit your site homepage.

Next steps (on request)
- Generate all required templates: custom pages (Screener, Market Overview, Portfolio, Lookup, News, Watchlist, User Settings, Payments), informational pages (About, Help, FAQ, Contact, Glossary, How It Works, Getting Started, Roadmap), account pages (Login, Dashboard, Account, Billing History), business pages (Premium Plans, Compare Plans), utility pages (Privacy, Terms, Security, Accessibility, Status, Sitemap, Market Hours), plus core templates (front-page, header, footer, page, single, archive, search, 404, etc.).
- Wire up real data sources and optional payments (Stripe) after your confirmation and API keys.