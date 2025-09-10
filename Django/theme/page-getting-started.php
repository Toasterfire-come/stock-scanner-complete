<?php
/**
 * Template Name: Getting Started
 */
get_header(); ?>
<div class="getting-started">
  <div class="container" style="max-width:1000px;margin:40px auto;padding:0 20px;">
    <h1>Getting Started</h1>
    <ol class="card" style="padding:24px;">
      <li>Create your account or sign in</li>
      <li>Explore the free Dashboard and Stock Lookup</li>
      <li>Build a Watchlist to track tickers you care about</li>
      <li>Upgrade to unlock advanced scanning, alerts, and more</li>
    </ol>
    <div class="grid" style="display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));">
      <a class="card btn" href="/stock-lookup/">Stock Lookup</a>
      <a class="card btn" href="/stock-news/">Stock News</a>
      <a class="card btn" href="/market-overview/">Market Overview</a>
      <a class="card btn" href="/premium-plans/">Premium Plans</a>
    </div>
  </div>
</div>
<?php get_footer(); ?>