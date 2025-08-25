<?php /* Template Name: Front Page */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="hero section">
  <div class="container hero-grid">
    <div>
      <h1>Research faster. Trade smarter.</h1>
      <p>Lightning-fast stock screener, real-time watchlists, and clean portfolio tracking. Secure. Accessible. Beautiful.</p>
      <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
        <a class="btn btn-primary" href="#screener">Launch Screener</a>
        <a class="btn btn-ghost" href="#how">How it works</a>
        <span id="healthBadge" class="badge" aria-live="polite">Checking API…</span>
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
      <p class="muted" style="margin:0 0 20px;">Search, filter by sector, sort by price. Hydrates with external API if configured.</p>
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
      <p class="muted" style="margin:0 0 20px;">If the external API is set, this will fetch live items.</p>
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
        <a class="btn btn-ghost" href="<?php echo esc_url(home_url('/checkout')); ?>">Start free</a>
      </div>
      <div class="card" style="padding:20px; border:2px solid #d7e3ff; box-shadow: 0 10px 24px rgba(27,110,243,0.15);">
        <h3>Pro</h3>
        <p class="muted">Advanced filtering and export</p>
        <ul>
          <li>All Free features</li>
          <li>Advanced screeners</li>
          <li>Unlimited portfolios</li>
        </ul>
        <a class="btn btn-primary" href="<?php echo esc_url(home_url('/checkout')); ?>">Upgrade</a>
      </div>
      <div class="card" style="padding:20px;">
        <h3>Enterprise</h3>
        <p class="muted">Teams, SSO, priority support</p>
        <ul>
          <li>Team workspaces</li>
          <li>Audit logs</li>
          <li>Dedicated support</li>
        </ul>
        <a class="btn" href="<?php echo esc_url(home_url('/contact')); ?>">Contact sales</a>
      </div>
    </div>
  </div>
</section>
<script defer src="<?php echo esc_url( get_template_directory_uri() . '/assets/js/ui.js' ); ?>"></script>
<script defer>
(function(){
  document.addEventListener('DOMContentLoaded', async function(){
    // Health badge
    const badge = document.getElementById('healthBadge');
    try{
      const h = await (window.finmApi ? window.finmApi.health() : Promise.reject('no api'));
      const status = (h.status||'').toLowerCase();
      if(status==='healthy'){ badge.textContent='API: Healthy'; badge.classList.add('badge-green'); }
      else { badge.textContent='API: Degraded'; badge.classList.add('badge-red'); }
    }catch(e){ badge.textContent='API: Offline'; badge.classList.add('badge-red'); }
  });
})();
</script>
<?php get_footer(); ?>