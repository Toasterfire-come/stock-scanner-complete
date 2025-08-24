<?php
/**
 * Fallback template + Demo Homepage (frontend-only, mocked)
 * This file renders a teaser experience using window.MockData (from assets/js/mock.js)
 */
if (!defined('ABSPATH')) { exit; }
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src https://fonts.gstatic.com 'self' data:; script-src 'self'; connect-src 'self';" />
  <?php wp_head(); ?>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
</head>
<body <?php body_class(); ?>>
  <a class="screen-reader-text" href="#main">Skip to content</a>
  <header class="header">
    <div class="container header-inner" role="navigation" aria-label="Primary">
      <a class="brand" href="<?php echo esc_url(home_url('/')); ?>">
        <span class="brand-badge" aria-hidden="true"></span>
        <span>FinMarkets</span>
      </a>
      <nav class="nav" aria-label="Main menu">
        <a href="#screener">Screener</a>
        <a href="#watchlist">Watchlist</a>
        <a href="#news">News</a>
        <a href="#pricing">Pricing</a>
      </nav>
      <div>
        <button class="btn" id="loginBtn" aria-haspopup="dialog">Sign in</button>
        <a class="btn btn-primary" href="#pricing">Get Pro</a>
      </div>
    </div>
  </header>

  <main id="main">
    <section class="hero section">
      <div class="container hero-grid">
        <div>
          <h1>Research faster. Trade smarter.</h1>
          <p>Lightning-fast stock screener, real-time watchlists, and clean portfolio tracking. Secure. Accessible. Beautiful.</p>
          <div style="display:flex; gap:12px;">
            <a class="btn btn-primary" href="#screener">Launch Screener</a>
            <a class="btn btn-ghost" href="#how">How it works</a>
          </div>
          <div class="stat" style="margin-top:24px;">
            <div class="stat-item"><span class="muted">Coverage</span><strong>8,000+ stocks</strong></div>
            <div class="stat-item"><span class="muted">Speed</span><strong>&lt;50ms filters</strong></div>
            <div class="stat-item"><span class="muted">Uptime</span><strong>99.9%</strong></div>
          </div>
        </div>
        <div class="card" style="padding:16px;">
          <div class="muted" style="margin-bottom:8px;">Preview</div>
          <table class="table" aria-describedby="Screener preview">
            <thead><tr><th>Symbol</th><th>Name</th><th>Price</th><th>Δ</th></tr></thead>
            <tbody id="previewBody"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="screener" class="section">
      <div class="container">
        <div class="content">
          <h2 style="margin:0 0 12px; color:var(--navy);">Stock Screener</h2>
          <p class="muted" style="margin:0 0 20px;">Client-side demo with mock data. Search, filter by sector, sort by price.</p>
        </div>
        <div class="card" style="padding:16px;">
          <div class="toolbar" role="region" aria-label="Screener controls">
            <input id="q" class="input" type="search" placeholder="Search by symbol or name" aria-label="Search stocks" />
            <select id="sector" class="select" aria-label="Filter by sector"></select>
            <button id="sortPrice" class="btn" aria-pressed="false" aria-label="Sort by price">Sort by Price</button>
          </div>
          <div class="grid cols-2">
            <div style="overflow:auto;">
              <table class="table" aria-label="Screener table">
                <thead>
                  <tr><th>Symbol</th><th>Name</th><th>Sector</th><th>Price</th><th>Change</th><th></th></tr>
                </thead>
                <tbody id="screenerBody"></tbody>
              </table>
            </div>
            <aside id="watchlist" class="card" style="padding:12px;">
              <h3 style="margin:8px 0 4px; color:var(--navy);">Watchlist</h3>
              <p class="muted" style="margin:0 0 8px;">Saves in your browser.</p>
              <ul id="watchlistItems" style="list-style:none; padding:0; margin:0;"></ul>
            </aside>
          </div>
        </div>
      </div>
    </section>

    <section id="news" class="section">
      <div class="container">
        <div class="content">
          <h2 style="margin:0 0 12px; color:var(--navy);">Market News</h2>
          <p class="muted" style="margin:0 0 20px;">Mock headlines for layout and motion.</p>
        </div>
        <div class="grid cols-3">
          <div id="newsGrid" class="grid cols-3" style="grid-template-columns: repeat(3, minmax(0, 1fr));"></div>
        </div>
      </div>
    </section>

    <section id="pricing" class="section" aria-label="Pricing plans">
      <div class="container">
        <div class="grid cols-3">
          <div class="card" style="padding:20px;">
            <h3>Free</h3>
            <p class="muted">Basics for casual browsing</p>
            <ul>
              <li>Real-time watchlist</li>
              <li>Community screens</li>
              <li>News summaries</li>
            </ul>
            <button class="btn btn-ghost">Start free</button>
          </div>
          <div class="card" style="padding:20px; border:2px solid #d7e3ff; box-shadow: 0 10px 24px rgba(27,110,243,0.15);">
            <h3>Pro</h3>
            <p class="muted">Advanced filtering and export</p>
            <ul>
              <li>All Free features</li>
              <li>Advanced screeners</li>
              <li>Unlimited portfolios</li>
            </ul>
            <button class="btn btn-primary">Upgrade</button>
          </div>
          <div class="card" style="padding:20px;">
            <h3>Enterprise</h3>
            <p class="muted">Teams, SSO, priority support</p>
            <ul>
              <li>Team workspaces</li>
              <li>Audit logs</li>
              <li>Dedicated support</li>
            </ul>
            <button class="btn">Contact sales</button>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="container" style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
      <div>
        <div class="brand" style="margin-bottom:8px;"><span class="brand-badge"></span>FinMarkets</div>
        <div class="muted">&copy; <?php echo date('Y'); ?> FinMarkets. All rights reserved.</div>
      </div>
      <nav aria-label="Footer">
        <a href="#">Privacy</a> · <a href="#">Terms</a> · <a href="#">Security</a>
      </nav>
    </div>
  </footer>

  <?php wp_footer(); ?>
</body>
</html>