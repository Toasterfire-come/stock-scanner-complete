Retail Trade Scanner — Theme Notes and TODO

Scope
- This theme powers the WordPress marketing + dashboard shell for the Retail Trade Scanner platform.
- Pages under /templates/pages provide polished, assignable templates for key sections.

Existing Page Templates
- Dashboard: templates/pages/page-dashboard.php
- Scanner: templates/pages/page-scanner.php
- Watchlists: templates/pages/page-watchlists.php
- Portfolio: templates/pages/page-portfolio.php
- Alerts: templates/pages/page-alerts.php
- News: templates/pages/page-news.php
- Search: templates/pages/page-search.php
- Popular: templates/pages/page-popular.php
- Finder: templates/pages/page-finder.php
- Filters: templates/pages/page-filters.php
- Settings: templates/pages/page-settings.php
- Email: templates/pages/page-email.php
- Contact: templates/pages/page-contact.php
- Plans/Pricing: templates/pages/page-plans.php
- About: templates/pages/page-about.php

How to assign a template in WP
1) Create a new Page (Pages → Add New) and set the title & slug (e.g., “Watchlists” with slug watchlists).
2) From the Page Attributes → Template dropdown, pick the matching template (e.g., “Watchlists”).
3) Publish.

Navigation wiring (check these slugs)
- /dashboard/ (Dashboard)
- /scanner/ (Scanner)
- /watchlists/ (Watchlists)
- /portfolio/ (Portfolio)
- /alerts/ (Alerts)
- /news/ (News)

Detected links that imply additional pages
- Footer → /api-docs/ (API Docs) → TODO template or use default Page
- Footer → /help/ (Help Center) → TODO template or use default Page
- Footer → /tutorials/ (Tutorials index) → TODO template or use default Page
- Footer → /blog/ (Blog) → use default Posts index with a custom archive template later
- Legal → /privacy-policy/, /terms-of-service/, /disclaimer/ → simple Page templates are acceptable initially
- About page CTA → /careers/ → TODO template or use default Page

Theme TODO (next passes)
- Create minimal, polished templates for:
  • API Docs (page-api-docs.php)
  • Help Center (page-help.php)
  • Tutorials (page-tutorials.php)
  • Careers (page-careers.php)
  • Privacy Policy (page-privacy-policy.php)
  • Terms of Service (page-terms-of-service.php)
  • Disclaimer (page-disclaimer.php)
- Add 404.php with theme-consistent empty state
- Add archive.php and search.php variants styled with glassmorphism (optional; WP default works meanwhile)
- Verify assets/icons/sprite.svg exists or provide fallback icons
- Consider adding a closing counterpart for template-parts/layout/main-shell.php if desired (currently opens layout wrapper only)

Notes
- All templates avoid hardcoding external URLs and rely on WordPress helpers.
- Accessibility and semantics: buttons have labels, headings follow hierarchy, forms are labeled.
- Data in templates is placeholder-only and safe to replace with real integrations later.