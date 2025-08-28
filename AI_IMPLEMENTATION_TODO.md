AI Implementation TODO — Retail Trade Scanner

Scope: Build a production-ready, fully responsive stock scanning website with clean, minimal UI/UX. Use content-referenced SVGs, consistent spacing/typography, and finance-oriented color palette. Produce reusable components and complete page templates for every route (not just the ones listed in the prompt).

Decisions & Planning
- [ ] Choose frontend stack (React or Vue) and router. Prefer TS for scalability.
- [ ] Establish folder/module architecture (components, pages, styles, icons, utils, api, hooks).
- [ ] Define accessibility standards (WCAG 2.1 AA), keyboard navigation, focus order.

Design Tokens & Theming
- [ ] Align tokens with finance palette (prompt overrides):
      Primary #1E88E5, Secondary #43A047, Accent #E53935, Neutrals #F5F5F5/#E0E0E0/#212121/#757575.
- [ ] Update global CSS variables to match palette, spacing scale, radii, shadows.
- [ ] Typography: Inter/Roboto, bold headers, regular body, muted captions; set sizes/line-heights.
- [ ] Support light/dark/auto modes and surface elevations (glassmorphic optional).
- [ ] Document token usage (colors, spacing, typography) with examples.

Icons & Assets (reference by content)
- [ ] Provide a content-addressed SVG sprite/registry including: logo, bell/notifications, dashboard, screener, alerts, watchlist, portfolio, news, settings, search, social (LinkedIn, Twitter, GitHub).
- [ ] Implement helper to inject icons by inner SVG content/signature rather than filename.
- [ ] Ensure accessible icons: role="img", titles/aria-labels where needed.

Global Styling
- [ ] Create global base styles: CSS reset/normalize, typography, links, forms, tables.
- [ ] Component-specific styles (SCSS/CSS modules) with BEM or CSS-in-JS (if selected).
- [ ] Fluid grid system and spacing utilities; responsive breakpoints.
- [ ] Theming utilities (CSS variables), prefers-color-scheme support.

Core Layout Components
- [ ] Header: left logo (SVG content), center search (tickers/companies), right user menu (avatar dropdown: settings/logout), notifications bell with alert badge.
- [ ] Sidebar (collapsible):
      - Icons + labels; collapsed: icons-only with tooltips.
      - Active state: glowing left border + darker background.
      - Keyboard and screen-reader accessible; remembers collapse state.
- [ ] Footer: Terms, Privacy, Contact links; social icons (LinkedIn, Twitter, GitHub); copyright.
- [ ] Main content shell with slots for page templates; sticky header/sidebar behavior.

Reusable UI Components
- [ ] Buttons (primary, secondary, accent, outline, ghost), loading/disabled states.
- [ ] Cards (surface/elevated/glass), headers, actions, metrics.
- [ ] Tabs and segmented controls (for Settings/Portfolio sub-views).
- [ ] Data table: sorting, pagination, sticky header, row hover, responsive card mode, CSV/Excel export.
- [ ] Chart shell components with responsive container, tooltip, legend, grid (lib-agnostic wrappers).
- [ ] Badges, toasts, modals, dropdowns, tooltips.
- [ ] Form inputs with validation states, helper text, and accessible errors.

Page Templates (create for ALL pages, not just those mentioned)
- [ ] Dashboard: grid layout for top movers, major indices, market sentiment, volume heatmaps.
- [ ] Screener: advanced filter panel (left), results table (right), sorting, pagination, export.
- [ ] Alerts: CRUD for price, volume, P/E alerts; list, create/edit forms.
- [ ] Portfolio: performance charts, allocation breakdown, gains/losses, daily P/L.
- [ ] News: infinite scroll feed, sentiment tags/grades, reading pane.
- [ ] Settings: tabbed sections (Profile, Notifications, API Integrations, Security).
- [ ] Search: symbol input, autocomplete, quote card, historical table.
- [ ] Popular: trending, most active, gainers, losers.
- [ ] Email Lists: subscribe form, list manager, history table.
- [ ] Finder: sector grid, factor tiles, screen results.
- [ ] Filters: presets, custom builder, save preset.
- [ ] Plans & Pricing: tiers, FAQ, CTA.
- [ ] Contact: contact form with validation, help links.
- [ ] Portfolio (aux link) — already covered above; ensure route parity.
- [ ] Auth: sign-in, sign-up, forgot password.
- [ ] Not Found (404): message and search link.
- [ ] Base page wrapper layout shared by all pages.

Routing & Navigation
- [ ] Configure routes for all templates; active link states synced to sidebar.
- [ ] Breadcrumbs where appropriate; document titles/meta tags per route.

Responsiveness & UX
- [ ] Define breakpoints and container queries; ensure mobile/desktop parity.
- [ ] Mobile: sidebar becomes hamburger/top sheet; tables collapse to cards; charts resize.
- [ ] Motion: subtle hover scale, entrance fade-up, skeleton loaders; respects reduced motion.
- [ ] Focus/hover states visible and color-contrast compliant.

Data & Integration (scaffold-only)
- [ ] API layer abstraction; mock services for quotes, movers, screener results, news.
- [ ] Real-time updates placeholder (websocket/SSE) for price/alerts.
- [ ] Persist user preferences (theme, sidebar state) in storage.

Performance & Production Readiness
- [ ] Bundle optimization, code-splitting, tree-shaking, prefetch/preload critical assets.
- [ ] Minify CSS/JS, extract critical CSS; image/SVG optimization.
- [ ] Lighthouse performance/accessibility checks with thresholds.

Quality & Testing
- [ ] Linting/formatting (ESLint, Prettier) and stylelint.
- [ ] Unit tests for components; integration tests for pages; E2E smoke flow (login → dashboard → screener).
- [ ] Visual regression tests for key templates/components.

Docs & Ops
- [ ] Developer README with setup, scripts, environment, build/deploy.
- [ ] Theming guide (how to use tokens; referencing SVGs by content).
- [ ] CI/CD pipeline for build, tests, preview deploys; production deploy workflow.

Deliverables Checklist
- [ ] Global styling and theme variables file(s).
- [ ] Component-specific SCSS/CSS.
- [ ] SVG icon set for navigation/actions/social (content-referenced).
- [ ] Reusable React/Vue components: header, sidebar, footer, cards, charts, tables.
- [ ] Page templates for: dashboard, screener, alerts, portfolio, news, settings, and ALL other pages listed above.
