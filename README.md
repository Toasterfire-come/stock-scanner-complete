Retail Trade Scanner Theme
=========================

Requirements
------------
- WordPress 6.4+
- PHP 8.0+

Development
-----------
1. Install Node 18+ and Yarn or npm.
2. Install deps:
   - `yarn install` or `npm install`
3. Start dev build:
   - `yarn dev` (watches Tailwind)

Production build
----------------
- `yarn build` generates `assets/css/theme.css` (minified).
- Enqueued assets use filemtime-based cache-busting.

Internationalization
--------------------
- Text domain: `rts`
- Load path: `languages/`
- Use `__()`, `esc_html__()`, `esc_attr__()` for translatable strings.

