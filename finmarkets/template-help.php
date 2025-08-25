<?php /* Template Name: Help Center */ if (!defined('ABSPATH')) { exit; } get_header(); ?>
<section class="glass-section">
  <div class="container">
    <header class="section-intro">
      <h1>Help Center</h1>
      <p class="section-subtitle">Guides and documentation for FinMarkets</p>
    </header>

    <div class="grid cols-3">
      <div class="card glass-card p-6">
        <h3>Getting Started</h3>
        <ul>
          <li><a href="/getting-started/">Account Setup</a></li>
          <li><a href="/screener/">First Stock Screen</a></li>
          <li><a href="/dashboard/">Dashboard Overview</a></li>
        </ul>
      </div>
      <div class="card glass-card p-6">
        <h3>Features</h3>
        <ul>
          <li><a href="/screener/">Advanced Screener</a></li>
          <li><a href="/watchlist/">Watchlists</a></li>
          <li><a href="/portfolio/">Portfolio Tracking</a></li>
        </ul>
      </div>
      <div class="card glass-card p-6">
        <h3>Billing & Account</h3>
        <ul>
          <li><a href="/account/">Account Settings</a></li>
          <li><a href="/billing-history/">Billing History</a></li>
          <li><a href="/premium-plans/">Plans & Pricing</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>
<?php get_footer(); ?>