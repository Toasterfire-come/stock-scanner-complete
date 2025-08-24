<?php /* Template Name: Stock Screener */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="section">
  <div class="container">
    <div class="content">
      <h1 style="color:var(--navy);">Stock Screener</h1>
      <p class="muted">Client-side demo powered by mock data. Real data integration can be added later.</p>
    </div>
    <div class="card" style="padding:16px;">
      <div class="toolbar" role="region" aria-label="Screener controls">
        <input id="q" class="input" type="search" placeholder="Search by symbol or name" aria-label="Search stocks" />
        <select id="sector" class="select" aria-label="Filter by sector"></select>
        <button id="sortPrice" class="btn" aria-pressed="false" aria-label="Sort by price">Sort by Price</button>
      </div>
      <div style="overflow:auto;">
        <table class="table" aria-label="Screener table">
          <thead>
            <tr><th>Symbol</th><th>Name</th><th>Sector</th><th>Price</th><th>Change</th><th></th></tr>
          </thead>
          <tbody id="screenerBody"></tbody>
        </table>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <aside id="watchlist" class="card" style="padding:12px;">
      <h3 style="margin:8px 0 4px; color:var(--navy);">Watchlist</h3>
      <p class="muted" style="margin:0 0 8px;">Saves in your browser.</p>
      <ul id="watchlistItems" style="list-style:none; padding:0; margin:0;"></ul>
    </aside>
  </div>
</section>
<?php get_footer(); ?>