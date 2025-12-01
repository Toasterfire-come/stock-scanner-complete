# Page Fix Checklist (6 items per page)

This document defines six concrete fix items per page via category baselines and maps every route to a baseline. Where a page needs extra nuances, an addendum is included.

## Baselines

- [MKT] Marketing pages (public/marketing)
  1) SEO: Add/verify title, meta description, canonical.
  2) Accessibility: Enforce semantic heading order; descriptive link text; skip-to-content.
  3) Media: All images have meaningful alt, width/height, and `loading="lazy"` where offscreen.
  4) Performance: Preload LCP media; control CLS; defer non-critical scripts; code-split heavy sections.
  5) Analytics: Track primary CTAs and key interactions to backend metrics API.
  6) Link hygiene: External links use `rel="noopener noreferrer"`; internal links use `Link` (no hard reloads).

- [AUTH] Authentication pages (auth flow)
  1) SEO: `robots: noindex,follow`.
  2) Forms: Label/describe inputs; summarize errors; move focus to first error; keyboard-only flow.
  3) Security: CSRF ensured for POST; rate-limit and lockout handling surfaced; sanitize messages.
  4) UX: Password reveal toggles; strength meter; confirm password validation.
  5) Analytics: Track submit success/failure, OAuth callbacks; avoid logging PII.
  6) Link hygiene: Legal links accessible; no `_blank` unless necessary with proper `rel`.

- [APP] Application pages (protected app UI)
  1) SEO: `robots: noindex,follow`; page title reflects context.
  2) Loading: Skeletons/spinners with reduced layout shift; empty/error states.
  3) Data: Cancel in-flight requests on unmount; debounce filters; handle 401/429 gracefully.
  4) Accessibility: Tables/grids keyboard nav; focus states; ARIA for controls.
  5) Performance: Virtualize long lists; paginate; memoize; avoid unnecessary re-renders.
  6) Analytics: Track page views and key interactions to backend; add contextual tags.

- [DEV] Developer tools pages
  1) SEO: `robots: noindex,follow`.
  2) Security: Mask keys/secrets; avoid logging sensitive data; RBAC enforcement.
  3) UX: Copy-to-clipboard with aria-live; confirm destructive actions.
  4) Links: External docs `_blank` with `rel`; internal use `Link`.
  5) Analytics: Track key actions (create/revoke key, console requests).
  6) Error handling: Show API errors with retry and guidance.

- [DOCS] Documentation pages
  1) SEO: Canonical and descriptive title/description per doc; breadcrumbs.
  2) Accessibility: Table of contents with skip links; keyboard-friendly anchors.
  3) Code: Copy buttons with aria-live; monospace; syntax highlighting.
  4) Security: Sanitize markdown/HTML; safe links.
  5) Navigation: Prev/Next links; category overview context.
  6) Analytics: Track doc views and copy events.

- [ENT] Enterprise/lead forms
  1) SEO: Canonical (or `noindex` if gated); og/twitter tags.
  2) Forms: Field validation with inline messages; focus management; ARIA.
  3) Anti-abuse: Honeypot; basic rate-limiting feedback; backend spam checks.
  4) Analytics: Track submissions and funnel; include attribution tags.
  5) Success flow: Thank-you/confirmation route; email confirmation.
  6) Link hygiene: External links with `rel`; file links show type/size.

- [SYS] System/status pages
  1) SEO: `robots: noindex,follow`.
  2) Accessibility: Table headers `scope` and captions; color not sole indicator.
  3) Polling: Interval with cleanup/backoff; offline handling.
  4) Perf: Minimal layout shift; lazy-load charts.
  5) Links: Link to incidents/RSS.
  6) Analytics: Track incidents view and refresh.

- [SHARE] Public share pages
  1) SEO: `robots: noindex,follow`; no sensitive data in meta.
  2) Validation: Check slug format; handle expired/invalid.
  3) CTA: “Open in app” with deep link; fallback.
  4) Analytics: Track share open and conversion.
  5) Security: Mask sensitive values; avoid leaking user data.
  6) Perf: SSR/cache headers (if applicable); lightweight payload.

- [LEGAL] Legal pages
  1) SEO: Canonical, title, meta description.
  2) Structure: Anchored headings; table of contents; hierarchical headings.
  3) Print: Print stylesheet; accessible contrast.
  4) Updates: Last updated/versioning block.
  5) Accessibility: Long content navigation; link focus; skip links.
  6) Analytics: Track terms/privacy views.

- [REF] Referral apply pages
  1) Cookie: Set `REF_*` cookie; validate code format.
  2) Metrics: Log `referral_click` to backend with tags.
  3) Redirect: Forward to `/pricing?ref=CODE` with `state.discount_code`.
  4) Header: Ensure `X-Referral-Code` present on API calls.
  5) UX: Show applying state; fallback if invalid code.
  6) Tests: Add e2e navigation check for each shortlink.

## Per-route mapping (each page: apply the six items of its baseline)

Marketing [MKT]: `/`, `/features`, `/about`, `/contact`, `/pricing`, `/pricing-old`, `/stock-filter`, `/market-scan`, `/demo-scanner`, `/resources`, `/press`, `/widgets`, `/badges`, `/partners`, `/product`, `/data`, `/use-cases`, `/changelog`.

Auth [AUTH]: `/auth/sign-in`, `/auth/sign-up`, `/auth/plan-selection`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email`, `/auth/oauth-callback`.

Onboarding [APP]: `/onboarding`.

Billing [APP + ENT specifics for success/failure UX]: `/checkout`, `/checkout/success`, `/checkout/failure`.

App protected [APP]: `/app/dashboard`, `/app/markets`, `/app/stocks`, `/app/stocks/:symbol`, `/app/portfolio`.

Screeners [APP]: `/app/screeners`, `/app/screeners/:id`, `/app/screeners/new`, `/app/screeners/:id/edit`, `/app/screeners/:id/results`, `/app/templates`.

Market overview [APP]: `/app/market-heatmap`, `/app/sectors`, `/app/top-movers`, `/app/pre-after-market`, `/app/economic-calendar`.

News [APP]: `/app/news`, `/app/news/preferences`, `/app/news/subscribe`.

Alerts & Watchlists [APP]: `/app/alerts`, `/app/alerts/history`, `/app/watchlists`, `/app/watchlists/:id`.

Developer tools [DEV]: `/app/developer`, `/app/developer/api-keys`, `/app/developer/usage-statistics`, `/app/developer/api-documentation`, `/app/developer/console`.

Data export [APP]: `/app/exports`, `/app/exports/custom-report`, `/app/exports/scheduled`, `/app/exports/history`.

Account [APP]: `/account/profile`, `/account/password`, `/account/notifications`, `/account/billing`, `/account/plan`, `/account/settings`.

System [SYS]: `/endpoint-status`.

Docs [DOCS]: `/docs`, `/docs/getting-started/create-account`, `/docs/getting-started/dashboard`, `/docs/getting-started/first-screener`, `/docs/:category`, `/docs/:category/:slug`.

Legal [LEGAL]: `/legal/terms`, `/legal/privacy`.

Share [SHARE]: `/w/:slug`, `/p/:slug`.

Referral [REF]: `/adam50`, `/ref/:code`.

## Addenda (page-specific nuances)
- `/pricing-old` [MKT]: Add `noindex` and a banner redirecting to `/pricing`.
- `/product`, `/data`, `/use-cases`, `/changelog` [MKT]: Temporary `noindex` until content lands; add basic content or redirect.
- `/app/screeners/:id/edit` [APP]: Confirm-on-navigate for unsaved changes; autosave throttle.
- `/app/exports/*` [APP]: Progress + cancel; file size/type shown; expiry notices for downloads.
- `/app/developer/api-keys` [DEV]: Rotate keys; copy masked preview; confirm revoke with typed phrase.
- `/docs/:category/:slug` [DOCS]: Sanitize HTML; canonical per slug; author/date.
- `/endpoint-status` [SYS]: Backoff on failures; link to incident feed.
