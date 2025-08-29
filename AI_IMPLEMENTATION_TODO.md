Theme bootstrap & repo basics
[✓] Create theme folder retail-trade-scanner/ with required theme header in style.css, functions.php, theme.json, screenshot.png, readme.txt
[✓] Add .gitignore (node_modules, build artifacts, .DS_Store, vendor, .env, .zip) and a LICENSE (suggest MIT or other desired license)
[✓] Add package.json or build tool config if using a toolchain (optional)
[✓] Ensure text domain retail-trade-scanner and call load_theme_textdomain() in functions.php for translations
[✓] Provide a CHANGELOG.md and CONTRIBUTING.md (optional but recommended)

Directory layout (standardized)
[ ] assets/css/ (compiled /minified CSS) and assets/scss/ (source)
[ ] assets/js/ and assets/js/vendor/ (polyfills/builds)
[ ] assets/icons/ (svg sprite / raw svgs) and assets/fonts/ (webfont files + license)
[ ] template-parts/ (components: header, footer, card, table, chart-shell, etc.)
[ ] templates/pages/ (page templates listed below)
[ ] inc/ for PHP helper files (setup, enqueue, icon helper, template helpers)
[ ] patterns/ for Gutenberg block patterns (optional)
[ ] build/ or dist/ if using a compile step (ignored by Git)

Design tokens & theming parity
[ ] Define CSS variables in a base stylesheet (:root) for colors, spacing, radii, shadows, type scale, easing – expose same palette and font settings in theme.json (editor parity)
[ ] Colors: Primary #1E88E5, Secondary #43A047, Accent #E53935; Neutrals #F5F5F5, #E0E0E0, #212121, #757575 (and tints/shades & semantic success/warning/danger)
[ ] Typography: Inter/Roboto font stacks; define sizes, weights, line-heights in theme.json and CSS; preload fonts and use font-display: swap
[ ] Spacing scale and radii tokens; surface shadows; responsive scale variables
[ ] Dark mode support via prefers-color-scheme and optional [data-theme="dark"] overrides
[ ] Expose editor styles with add_editor_style() and theme.json editor settings

Assets & icons (content-referenced)
[ ] Create an inline SVG sprite (placed near top of <body> or output via PHP helper) containing: logo, bell/notifications, dashboard, screener, alerts, watchlist, portfolio, news, settings, search, LinkedIn, Twitter, GitHub, top-movers, volume, watchlist, alerts, charts placeholders, etc.
[ ] Implement a PHP helper (e.g., rts_get_icon($content_hash_or_svg, $attrs = [])) that outputs accessible SVG by content or hash (not filename) and sets <title>/role="img"/aria-hidden appropriately
[ ] Optimize SVGs (strip metadata, combine common defs, ensure viewBox and stroke/fill consistency)
[ ] Include fallback PNGs for email or legacy clients if required

Global styling & componentized CSS
[ ] Base: reset/normalize, base typography, anchors, lists, forms, tables using CSS variables
[ ] Component styles colocated under assets/scss/components/ (buttons, badges, cards, table, chart-shell, toast, modal, tabs) and compiled to assets/css/main.css
[ ] Utility classes (spacing, grid helpers, text utilities) and responsive breakpoints
[ ] Fluid grid utilities, container widths, and masonry/bento helpers if used
[ ] Use CSS cascade layers (@layer base, components, utilities) if possible for predictable CSS ordering
[ ] Provide skeleton loading and accessible loading states for data-heavy components

Enqueue & build process
[ ] Enqueue styles/scripts via wp_enqueue_scripts with proper dependencies and versioning (use filemtime or build hash)
[ ] Enqueue editor styles and block styles for Gutenberg parity
[ ] Ensure scripts are deferred/async where safe; critical CSS inlined for above-the-fold
[ ] Add a build pipeline (npm + webpack/rollup/parcel or sass + postcss) to produce minified assets; provide npm run build, npm run dev commands

Core theme templates & structure
[ ] header.php — left inline SVG logo, center search input (ticker/company), right user menu (avatar dropdown), notifications bell with badge, nav for desktop (ARIA, keyboard accessible)
[ ] sidebar.php — collapsible, keyboard accessible, shows icons + labels; collapsed shows icons with tooltips; active link visual (glowing left border + darker bg)
[ ] footer.php — terms/privacy/contact links, social icons, copyright, small sitemap
[ ] index.php, page.php, single.php, archive.php, 404.php, front-page.php (front page template for landing/ui)
[ ] searchform.php — consistent search UI used site-wide
[ ] functions.php — theme setup, register nav menus (primary, footer), register sidebars/widgets (if used), add_theme_support (title-tag, post-thumbnails, html5, editor-styles), enqueue assets, register block styles/patterns
[ ] theme.json — define color palette, font sizes, custom properties for editor parity and block styling

Template parts (reusable components)
[ ] template-parts/components/button.php — button variants (primary, secondary, outline, gradient, magnetic) with ARIA and focus styles
[ ] template-parts/components/badge.php — positive/negative/neutral badges (semantic)
[ ] template-parts/components/card.php — metric KPI card (title, value, delta badge, small sparkline)
[ ] template-parts/components/table.php — data table shell with sortable headers, sticky head, responsive behavior
[ ] template-parts/components/chart-shell.php — accessible chart container with legend + tooltip hooks; loadable client-side chart later
[ ] template-parts/components/tabs.php — keyboard-accessible tabs with ARIA
[ ] template-parts/layout/main-shell.php — main page wrapper providing sticky header/sidebar layout and content container
[ ] template-parts/components/modal.php and toast.php — accessible modal and toast patterns (trap focus, ESC close)

Page templates (create for every page and analogous pages)
[ ] templates/pages/page-dashboard.php — overview grid: kpis, top movers, indices, market sentiment, heatmap (bento/masonry)
[ ] templates/pages/page-screener.php — left filter panel, results table, client-side filters UI, sort/pagination/export (CSV) hooks
[ ] templates/pages/page-alerts.php — list/manage/add/edit price/volume/PE alerts with form validation and confirmation flows
[ ] templates/pages/page-portfolio.php — portfolio positions, performance time series, allocation pie, gains/losses, daily P/L KPI cards
[ ] templates/pages/page-news.php — infinite scroll feed, source filters, sentiment tags and grades, reading pane layout
[ ] templates/pages/page-settings.php — tabs: Profile, Notifications, API Integrations (API key management UI), Security (2FA hint)
[ ] templates/pages/page-search.php — symbol input, autocomplete, quote card, fundamentals, historical table shell
[ ] templates/pages/page-popular.php — trending / most active / gainers / losers list and cards
[ ] templates/pages/page-email.php — subscribe form, list manager, history table (email delivery statuses)
[ ] templates/pages/page-finder.php — sector grid, factor tiles, screen results export hooks
[ ] templates/pages/page-filters.php — presets list, custom builder UI, save preset modal
[ ] templates/pages/page-plans.php — pricing tiers, features, CTA, membership badge treatments
[ ] templates/pages/page-contact.php — contact form with server-side validation hints and help links
[ ] 404.php — friendly 404, search link, suggested pages; consistent shell wrapper for all templates
[ ] Provide a base page wrapper layout used by all page templates, and a consistent way to include page-level scripts/styles

WordPress-only integration & editor parity
[ ] functions.php add_theme_support required features; register nav menus (primary, footer) and sidebars/widgets if desired
[ ] Provide block-templates or block-patterns (optional) for landing sections and dashboard cards so site admins can assemble pages via Gutenberg
[ ] Register REST endpoints if theme needs dynamic data fetching (theme-only caution: avoid plugin-level features)
[ ] Provide sample menu assignment instructions and recommended widget areas in readme.txt

JS behavior & interactivity (theme-only)
[ ] Sidebar collapse/expand with localStorage persistence, animated transitions, keyboard shortcuts, aria-expanded toggles
[ ] Header search interactions: debounce, live autocomplete (client-side UI only; actual search backend must be provided separately)
[ ] Notifications popover with aria roles and real-time badge hook (theme displays; data source plugin/backend)
[ ] User avatar dropdown (profile/settings/logout links), keyboard accessible, closes on ESC or click outside
[ ] Tables responsive: small screens show card view with same data (transform), support swipe/scroll for wide tables
[ ] Respect prefers-reduced-motion in all animations; controlled micro-interactions (hover ripple/magnetic)
[ ] Minimal JS bundling, deferred where safe; provide non-JS fallbacks for critical interactions

Responsiveness, container queries & accessibility
[ ] Breakpoints and container queries for card scaling and component behavior; mobile-first approach
[ ] Mobile: sidebar collapses to hamburger menu that opens an accessible off-canvas sheet; search becomes full-width at top
[ ] Keyboard navigation for all menus, dropdowns, dialogs with visible focus rings and focus-visible support
[ ] ARIA attributes for interactive elements; add aria-live regions for dynamic notifications and toast messages
[ ] Color contrast verification for text, buttons, badges in all states (WCAG AA) and high-contrast media queries

Performance & production readiness
[ ] Minify and version CSS/JS; use hashed filenames in production for cache busting
[ ] Inline critical CSS for above-the-fold (header + hero + nav) and defer non-critical CSS
[ ] Preload critical fonts and use font-display: swap and font-variation-settings where applicable
[ ] Optimize SVGs, remove metadata, combine defs, avoid large inline SVG bloat; provide aria-hidden for decorative svgs
[ ] Lazy-load below-the-fold images, charts, and widgets; use loading="lazy" for images
[ ] Set appropriate HTTP caching headers at deploy/infrastructure layer (not theme but document in README)
[ ] Lighthouse targets: aim for 90+ accessibility/performance where possible (theme responsibilities documented)

Security & privacy considerations (theme-only)
[ ] No direct external requests in theme code except fonts/icons via known CDN or bundled assets; document privacy implications
[ ] Escape all output with esc_html, esc_attr, wp_kses_post as appropriate; use nonce checks on any form submissions included in the theme
[ ] Secure contact forms (if implemented in theme) with nonce verification; advise that server-side processing should be plugin-handled

Quality & testing
[ ] PHPCS WordPress coding standards for PHP files; stylelint for CSS/SCSS; eslint for JS; include basic config files
[ ] Automated unit/integration tests optional (theme-only scope may limit what’s tested), but add smoke tests: header/sidebar/footer render without fatal errors
[ ] Visual regression checklist: snapshot key pages (dashboard, screener, news, portfolio) across breakpoints
[ ] Cross-browser QA: Chrome, Edge, Safari, Firefox (desktop/mobile) and iOS/Android device checks
[ ] Accessibility testing: axe, manual keyboard-only walkthrough, color-contrast checks

Docs, packaging & delivery
[ ] README.md with theme setup, menu/widget assignment, page templates mapping, token usage, icon usage by content instructions, recommended plugins (if any), and deployment notes
[ ] Theming guide: tokens list, examples of how to render icons by content, SCSS partial structure, and instructions for editor color palette sync
[ ] screenshot.png showing the primary theme layout (desktop hero) and a mobile screenshot optionally included in /screenshot/ for WordPress theme installer
[ ] Package theme as zip for distribution with instructions for installing via WP admin theme uploader
[ ] Add a small “release checklist” in README: minify assets, update version, tag commit, produce zip

Deliverables checklist (final verification)
[ ] Theme scaffolding: style.css header, functions.php, theme.json, header.php, footer.php, sidebar.php, readme, screenshot
[ ] Global styling and theme variables file(s) integrated and exposed to editor
[ ] SCSS sources and compiled/minified CSS in assets/css
[ ] JS sources and compiled/minified JS in assets/js with proper enqueueing
[ ] SVG icon sprite integrated and helper to render icons by content/hash (with accessibility)
[ ] Template parts for header, sidebar, footer, cards, charts, tables, and utilities
[ ] Page templates for dashboard, screener, alerts, portfolio, news, settings, search, popular, email, finder, filters, plans, contact, and 404
[ ] Theme-only README and theming guide; packaged theme zip ready for upload
[ ] QA sign-off: smoke tests passed, visual checks, accessibility checks, and performance notes documented