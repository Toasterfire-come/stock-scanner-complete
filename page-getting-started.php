<?php
/**
 * Template Name: Getting Started (v3)
 */
get_header(); ?>
<section class="glass-section">
  <div class="container" style="max-width:1000px;margin:0 auto;">
    <header class="section-intro">
      <h1 class="section-title text-gradient"><?php the_title(); ?></h1>
    </header>
    <div class="card glass-card">
      <div class="card-body">
        <ol style="display:grid;gap:.5rem;">
          <li><?php _e('Create your account or sign in', 'stock-scanner'); ?></li>
          <li><?php _e('Explore the free Dashboard and Stock Lookup', 'stock-scanner'); ?></li>
          <li><?php _e('Build a Watchlist to track tickers you care about', 'stock-scanner'); ?></li>
          <li><?php _e('Upgrade to unlock advanced scanning, alerts, and more', 'stock-scanner'); ?></li>
        </ol>
      </div>
    </div>
    <div class="features-grid" style="margin-top:1rem;">
      <a class="card glass-card btn" href="/stock-lookup/"><?php _e('Stock Lookup', 'stock-scanner'); ?></a>
      <a class="card glass-card btn" href="/stock-news/"><?php _e('Stock News', 'stock-scanner'); ?></a>
      <a class="card glass-card btn" href="/market-overview/"><?php _e('Market Overview', 'stock-scanner'); ?></a>
      <a class="card glass-card btn" href="/premium-plans/"><?php _e('Premium Plans', 'stock-scanner'); ?></a>
    </div>
  </div>
</section>
<?php get_footer(); ?>