<?php
/**
 * Template Name: Home (Marketing)
 * Description: Marketing-focused homepage to convert visitors into customers
 */

get_header(); ?>

<div class="home-page">
  <div class="container">
    <div class="page-header">
      <h1>Retail Trade Scanner</h1>
      <p class="page-description">Find, track, and analyze stocks with professional-grade tools built for traders and investors</p>
    </div>

    <!-- Hero CTA -->
    <div class="panel card" style="padding: 24px; display: grid; gap: 16px;">
      <div style="display: grid; gap: 8px;">
        <h2 style="margin:0;">Powerful Stock Screening and Insights</h2>
        <p class="muted" style="margin:0;">High-contrast, fast, and accurate. Start free and upgrade anytime.</p>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <a class="btn btn-primary" href="/stock-screener/">Start Screening</a>
        <a class="btn btn-secondary" href="/signup/">Create Free Account</a>
        <a class="btn btn-outline" href="/premium-plans/">View Plans</a>
      </div>
    </div>

    <!-- Feature Grid -->
    <div class="features-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 24px;">
      <div class="card" style="padding:20px;">
        <h3>Advanced Screener</h3>
        <p class="muted">Filter by market cap, price, volume, performance, and technicals to quickly find opportunities.</p>
        <a class="btn btn-outline" href="/stock-screener/">Explore Screener</a>
      </div>
      <div class="card" style="padding:20px;">
        <h3>My Watchlist</h3>
        <p class="muted">Build a personalized watchlist and get quick suggestions to start, with alerts and notes.</p>
        <a class="btn btn-outline" href="/watchlist/">Open Watchlist</a>
      </div>
      <div class="card" style="padding:20px;">
        <h3>Portfolio Tracking</h3>
        <p class="muted">Track holdings and ROI with real-time performance summaries and CSV import.</p>
        <a class="btn btn-outline" href="/portfolio/">Go to Portfolios</a>
      </div>
      <div class="card" style="padding:20px;">
        <h3>Personalized News</h3>
        <p class="muted">See tailored news for your holdings and interests with smart filtering and analytics.</p>
        <a class="btn btn-outline" href="/personalized-news/">See News</a>
      </div>
    </div>

    <!-- Social Proof / Stats -->
    <div class="card" style="padding:20px; margin-top: 24px;">
      <h3>Why Traders Choose Retail Trade Scanner</h3>
      <ul style="margin:12px 0 0 18px; color: var(--color-text-muted);">
        <li>High-contrast, accessible UI for long trading sessions</li>
        <li>Fast screening with professional filters</li>
        <li>Unified dashboard with usage stats and limits</li>
        <li>Easy watchlists and portfolio import</li>
      </ul>
    </div>

    <!-- Secondary CTA -->
    <div class="panel card" style="padding: 20px; display:flex; flex-wrap:wrap; gap:12px; margin-top: 24px; align-items:center; justify-content:space-between;">
      <div>
        <h3 style="margin:0;">Get started for free</h3>
        <p class="muted" style="margin:0;">Upgrade anytime for more features and higher limits</p>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <a class="btn btn-primary" href="/signup/">Create Account</a>
        <a class="btn btn-outline" href="/premium-plans/">Compare Plans</a>
      </div>
    </div>
  </div>
</div>

<?php get_footer(); ?>