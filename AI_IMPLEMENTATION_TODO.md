AI Implementation TODO — Retail Trade Scanner (WordPress Theme-Only)

Scope: Create a production-ready, fully responsive WordPress theme implementing the stock scanning site UI/UX. Only modify/add a theme (no core/plugins). Use content-referenced SVGs, consistent spacing/typography, and the finance palette. Provide reusable template parts and complete page templates for every route listed (and analogous pages).

Theme Bootstrap & Structure
- [ ] Create theme folder: retail-trade-scanner/ with: style.css (theme header), functions.php, theme.json, screenshot.png, readme.txt.
- [ ] Directory layout: assets/css, assets/js, assets/icons, assets/fonts, template-parts/, templates/pages/, inc/ (setup files), patterns/ (optional Gutenberg patterns).
- [ ] Text domain: retail-trade-scanner; load_theme_textdomain; translation-ready strings.

Design Tokens & Theming (palette per prompt)
- [ ] Colors: Primary #1E88E5, Secondary #43A047, Accent #E53935; Neutrals #F5F5F5 (bg), #E0E0E0 (dividers), #212121 (text), #757575 (muted).
- [ ] Define CSS variables in a base stylesheet and expose same in theme.json (settings.color.palette, custom properties) for editor parity.
- [ ] Typography: Inter or Roboto; headers bold, body regular, captions smaller/muted; define sizes/line-heights in theme.json and CSS.
- [ ] Spacing scale and radii; shadows for surfaces; maintain responsive scale.
- [ ] Dark mode (optional): prefers-color-scheme media and adjustable variables.

Assets & Icons (reference by content)
- [ ] Integrate an inline SVG sprite (content-based) including: logo, bell/notifications, dashboard, screener, alerts, watchlist, portfolio, news, settings, search, LinkedIn, Twitter, GitHub.
- [ ] Helper: PHP function to render icons by passing raw SVG content or a content hash, not filenames.
- [ ] Accessibility: role="img", aria-label or <title> where needed; focus states.

Global Styling
- [ ] Base: reset/normalize, typography, links, forms, tables using CSS variables.
- [ ] Component styles (SCSS/CSS) colocated under assets/scss and compiled to assets/css/main.css.
- [ ] Fluid grid utilities and breakpoints; container widths; spacing utilities.
- [ ] Enqueue styles/scripts via wp_enqueue_scripts with versioning and dependency management.

Core Theme Templates
- [ ] header.php: left logo (inline SVG), center search (ticker/company input UI), right user menu (avatar dropdown for settings/logout), notifications bell with badge.
- [ ] sidebar.php: collapsible; icons + labels; collapsed shows icons with tooltips; active item has glowing left border + darker background; keyboard accessible.
- [ ] footer.php: Terms, Privacy, Contact links; social icons (LinkedIn, Twitter, GitHub); copyright.
- [ ] index.php, page.php, singular templates; 404.php; front-page.php.

Template Parts (reusable)
- [ ] template-parts/components/button.php (variants), badge.php, card.php (metrics), table.php (data table shell), chart-shell.php (container with tooltip/legend hooks), tabs.php.
- [ ] template-parts/layout/main-shell.php providing sticky header/sidebar layout wrappers.

Page Templates (create for ALL pages, not just those mentioned)
- [ ] templates/pages/page-dashboard.php — grid for top movers, indices, sentiment, heatmaps.
- [ ] templates/pages/page-screener.php — advanced filter panel (left), results table (right), sorting/pagination/export shell.
- [ ] templates/pages/page-alerts.php — manage/add/edit price/volume/PE alerts.
- [ ] templates/pages/page-portfolio.php — performance charts, allocation, gains/losses, daily P/L.
- [ ] templates/pages/page-news.php — infinite scroll feed with sentiment tags/grades.
- [ ] templates/pages/page-settings.php — tabs: Profile, Notifications, API Integrations, Security.
- [ ] templates/pages/page-search.php — symbol input, autocomplete, quote card, historical table.
- [ ] templates/pages/page-popular.php — trending, most active, gainers, losers.
- [ ] templates/pages/page-email.php — subscribe form, list manager, history table.
- [ ] templates/pages/page-finder.php — sector grid, factor tiles, screen results.
- [ ] templates/pages/page-filters.php — presets, custom builder, save preset.
- [ ] templates/pages/page-plans.php — tiers, FAQ, CTA.
- [ ] templates/pages/page-contact.php — contact form with validation, help links.
- [ ] 404.php — message and search link; searchform.php for consistent UI.
- [ ] Provide a base page wrapper layout used by all page templates.

WordPress Integration (theme-only)
- [ ] functions.php: add_theme_support (title-tag, post-thumbnails, html5, editor-styles), register_nav_menus (primary, footer), register_sidebar (widgets if needed).
- [ ] Editor styles: add_editor_style for consistent typography/colors.
- [ ] Create WP menus for header and footer; map to sidebar items where applicable.

JavaScript Behavior
- [ ] Toggle sidebar collapse with persistence (localStorage) and tooltips on hover.
- [ ] Header search interactions; notifications popover; user avatar dropdown.
- [ ] Responsive tables transform to cards on small screens.
- [ ] Respect reduced motion; subtle hover/entrance animations.

Responsiveness & Accessibility
- [ ] Breakpoints and container queries; mobile: sidebar → hamburger/top sheet.
- [ ] Keyboard navigation for menus, dropdowns, dialogs; visible focus rings.
- [ ] Color contrast checks for all states; aria attributes for dynamic components.

Performance & Production Readiness
- [ ] Minify and version CSS/JS; defer/non-critical scripts; preload critical fonts.
- [ ] Inline critical CSS for above-the-fold; optimize SVGs (remove metadata).
- [ ] Lighthouse performance/accessibility targets.

Quality & Testing
- [ ] PHPCS (WordPress Coding Standards) for PHP; stylelint for CSS; eslint for JS if applicable.
- [ ] Template smoke tests: header/sidebar/footer render; page templates load without errors.
- [ ] Visual checks across breakpoints.

Docs & Packaging
- [ ] README with theme setup, menu/widget assignment, page template usage.
- [ ] Theming guide for tokens and icon usage by content.
- [ ] Package theme as zip for deployment; note that only theme files change.

Deliverables Checklist
- [ ] Theme scaffolding (style.css header, functions.php, theme.json, header.php, footer.php, sidebar.php).
- [ ] Global styling and theme variables file(s) integrated; component-specific CSS/SCSS.
- [ ] SVG icon sprite integrated and rendered by content.
- [ ] Reusable template parts for header, sidebar, footer, cards, charts, tables.
- [ ] Page templates for: dashboard, screener, alerts, portfolio, news, settings, and ALL other pages listed above.
